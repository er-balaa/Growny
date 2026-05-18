"""
Email Router — Endpoints to trigger email notifications.

POST /api/email/daily-digest        — Send daily overview to user
POST /api/email/test                — Send a test email
GET  /api/email/check-and-notify    — Auto-check for alerts and send if needed
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from auth import verify_firebase_token
from agents.tools.db_tools import get_wealth_summary, get_all_tasks, get_tasks_due_today
from agents.tools.finance_tools import calculate_totals, spending_by_category
from services.email_service import (
    send_daily_digest,
    send_important_alert,
    send_missed_info_reminder,
)
from config import groq_client
from datetime import datetime, date

router = APIRouter()


class EmailRequest(BaseModel):
    to_email: str
    user_name: str = "there"


def _groq_insight(prompt: str) -> str:
    if not groq_client:
        return "Keep tracking your finances for better insights!"
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return "Keep up the great work managing your finances!"


@router.post("/email/daily-digest")
async def trigger_daily_digest(req: EmailRequest, user_data: dict = Depends(verify_firebase_token)):
    """Send the daily financial + task digest email."""
    user_id = user_data["uid"]

    wealth = get_wealth_summary(user_id)
    tasks_today = get_tasks_due_today(user_id)

    currency = wealth.get("currency", "INR")
    income = wealth.get("total_income", 0)
    expense = wealth.get("total_expense", 0)
    balance = wealth.get("net_balance", 0)
    breakdown = wealth.get("category_breakdown", {})

    breakdown_str = "\n".join([f"  - {cat}: {currency} {amt:,.2f}" for cat, amt in breakdown.items()]) or "  No spending recorded yet."
    task_list_str = "\n".join([f"  - [{t.get('priority','?')}] {t.get('content','')}" for t in tasks_today]) or "  No tasks due today."

    insight_prompt = (
        f"User's financial summary:\n"
        f"- Income: {currency} {income:,.2f}\n"
        f"- Expense: {currency} {expense:,.2f}\n"
        f"- Net Balance: {currency} {balance:,.2f}\n"
        f"Category breakdown:\n{breakdown_str}\n\n"
        f"Tasks due today:\n{task_list_str}\n\n"
        "Write a short (2-3 sentences) friendly and motivating daily insight. "
        "Comment on spending patterns and give one actionable tip."
    )
    ai_insight = _groq_insight(insight_prompt)

    result = send_daily_digest(
        to_email=req.to_email,
        user_name=req.user_name,
        wealth=wealth,
        tasks=tasks_today,
        ai_insight=ai_insight,
    )

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to send email"))

    return {"message": f"Daily digest sent to {req.to_email}", "status": "success"}


@router.get("/email/check-and-notify")
async def check_and_notify(to_email: str, user_name: str = "there", user_data: dict = Depends(verify_firebase_token)):
    """
    Auto-checks user data for anomalies and sends alerts if needed:
    - Negative balance
    - High expense day
    - Missing transactions (no data logged in a while)
    - Overdue/high priority tasks
    """
    user_id = user_data["uid"]
    alerts_sent = []

    wealth = get_wealth_summary(user_id)
    all_tasks = get_all_tasks(user_id)
    today = date.today().isoformat()

    income = wealth.get("total_income", 0)
    expense = wealth.get("total_expense", 0)
    balance = wealth.get("net_balance", 0)
    currency = wealth.get("currency", "INR")
    tx_count = wealth.get("transaction_count", 0)

    # 1. Negative balance alert
    if balance < 0:
        result = send_important_alert(
            to_email=to_email, user_name=user_name,
            alert_type="NEGATIVE_BALANCE",
            details={
                "message": f"Your expenses ({currency} {expense:,.2f}) are exceeding your income ({currency} {income:,.2f}).",
                "data_points": [
                    f"Total Income: {currency} {income:,.2f}",
                    f"Total Expense: {currency} {expense:,.2f}",
                    f"Current Balance: {currency} {balance:,.2f} (negative!)",
                    "Tip: Review your largest spending categories and cut back where possible."
                ]
            }
        )
        if result.get("success"):
            alerts_sent.append("negative_balance")

    # 2. No data logged yet (new user or inactive)
    missing = []
    if tx_count == 0:
        missing.append({
            "title": "💰 No Transactions Logged",
            "description": "Start logging your income and expenses so Growny can give you accurate insights."
        })
    if not all_tasks:
        missing.append({
            "title": "📋 No Tasks or Notes Added",
            "description": "Add tasks, reminders, or notes to stay organized and on track."
        })
    if missing:
        result = send_missed_info_reminder(to_email=to_email, user_name=user_name, missing_items=missing)
        if result.get("success"):
            alerts_sent.append("missed_info")

    # 3. Overdue HIGH priority tasks
    overdue_high = [t for t in all_tasks if t.get("priority") == "HIGH" and t.get("due_date") and t.get("due_date") < today]
    if overdue_high:
        result = send_important_alert(
            to_email=to_email, user_name=user_name,
            alert_type="OVERDUE_TASK",
            details={
                "message": f"You have {len(overdue_high)} overdue HIGH priority task(s) that need immediate attention.",
                "data_points": [f"[HIGH] {t.get('content','')} (was due: {t.get('due_date','')})" for t in overdue_high[:5]]
            }
        )
        if result.get("success"):
            alerts_sent.append("overdue_tasks")

    if not alerts_sent:
        return {"message": "Everything looks great! No alerts needed.", "alerts_sent": []}

    return {"message": f"Sent {len(alerts_sent)} alert(s)", "alerts_sent": alerts_sent}


@router.post("/email/test")
async def send_test_email(req: EmailRequest, user_data: dict = Depends(verify_firebase_token)):
    """Send a simple test email to verify Gmail integration."""
    from services.email_service import _send_email, _base_template

    content = """
    <div style="text-align:center;padding:20px 0;">
      <div style="font-size:48px;">🎉</div>
      <h3 style="color:#e2e8f0;margin:16px 0 8px;">Email Integration Working!</h3>
      <p style="color:#a0aec0;font-size:15px;margin:0;">
        Your Growny email notifications are set up correctly.<br/>
        You'll now receive important alerts and daily digests.
      </p>
    </div>
    <div style="background:#242442;border-radius:12px;padding:16px;margin-top:20px;text-align:center;">
      <p style="margin:0;color:#6b7280;font-size:13px;">Sent via Gmail SMTP · Growny Assistant</p>
    </div>"""

    html = _base_template("✅ Test Email", "Your Growny email integration is working!", content)
    result = _send_email(req.to_email, "✅ Growny Email Test — It Works!", html)

    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))

    return {"message": "Test email sent successfully!", "to": req.to_email}
