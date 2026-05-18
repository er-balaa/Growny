"""
Insights Router — Proactive AI-generated summaries.

GET /api/insights/daily       — AI spending summary for today
GET /api/insights/tasks-due   — Today's tasks with AI prioritization notes
"""
from fastapi import APIRouter, Depends
from auth import verify_firebase_token
from agents.tools.db_tools import get_recent_transactions, get_tasks_due_today
from agents.tools.finance_tools import calculate_totals, spending_by_category
from config import groq_client
from datetime import datetime

router = APIRouter()


def _groq_summary(prompt: str) -> str:
    if not groq_client:
        return "AI service unavailable."
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Could not generate insight: {str(e)}"


@router.get("/insights/daily")
async def daily_spending_insight(user_data: dict = Depends(verify_firebase_token)):
    """Return an AI-generated daily spending summary."""
    user_id = user_data["uid"]
    transactions = get_recent_transactions(user_id, limit=30)
    today = datetime.now().strftime('%Y-%m-%d')

    today_txns = [t for t in transactions if t.get("date") == today]
    totals = calculate_totals(today_txns)
    breakdown = spending_by_category(today_txns)

    breakdown_str = "\n".join([f"  - {cat}: ₹{amt:,.2f}" for cat, amt in breakdown.items()]) or "  No expenses yet."

    prompt = (
        f"Today is {today}. Here is the user's spending summary for today:\n"
        f"- Total Income: ₹{totals['total_income']:,.2f}\n"
        f"- Total Expense: ₹{totals['total_expense']:,.2f}\n"
        f"- Net Balance: ₹{totals['net_balance']:,.2f}\n"
        f"Breakdown by category:\n{breakdown_str}\n\n"
        "Write a short (2-3 sentence) friendly insight about today's spending. "
        "Mention any notable patterns and give one actionable tip."
    )

    insight = _groq_summary(prompt)

    return {
        "date": today,
        "totals": totals,
        "breakdown": breakdown,
        "insight": insight,
        "transaction_count": len(today_txns),
    }


@router.get("/insights/tasks-due")
async def tasks_due_today(user_data: dict = Depends(verify_firebase_token)):
    """Return today's due tasks with AI-generated prioritization notes."""
    user_id = user_data["uid"]
    tasks = get_tasks_due_today(user_id)

    if not tasks:
        return {
            "date": datetime.now().strftime('%Y-%m-%d'),
            "tasks": [],
            "insight": "You have no tasks due today. A great day to get ahead! 🎯",
        }

    task_list_str = "\n".join(
        [f"  - [{t.get('priority','MEDIUM')}] {t.get('content','')}" for t in tasks]
    )

    prompt = (
        f"The user has {len(tasks)} task(s) due today:\n{task_list_str}\n\n"
        "Write a short (2-3 sentence) motivating message about their day. "
        "Suggest which task to tackle first based on priority and give one productivity tip."
    )

    insight = _groq_summary(prompt)

    return {
        "date": datetime.now().strftime('%Y-%m-%d'),
        "tasks": tasks,
        "task_count": len(tasks),
        "insight": insight,
    }
