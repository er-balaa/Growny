"""
Email Service — Sends beautiful HTML emails via Gmail SMTP.

Triggers:
- Daily Overview digest (wealth + tasks summary)
- Important alerts (overdue tasks, high expense warnings)
- Missed information reminders
"""
import smtplib
import os
import pathlib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Always load .env from the backend directory — works on every restart
_env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=_env_path, override=False)

GMAIL_SENDER = os.getenv("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")


def _send_email(to_email: str, subject: str, html_body: str) -> dict:
    """Core function to send an HTML email via Gmail SMTP."""
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        return {"success": False, "error": "Gmail credentials not configured."}
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"Growny Assistant <{GMAIL_SENDER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, to_email, msg.as_string())

        print(f"[Email] Sent '{subject}' to {to_email}")
        return {"success": True}
    except Exception as e:
        print(f"[Email] Error: {e}")
        return {"success": False, "error": str(e)}


def _base_template(title: str, preview: str, content_html: str) -> str:
    """Wrap content in a beautiful responsive HTML email shell."""
    today = datetime.now().strftime("%B %d, %Y")
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#0f0f1a;font-family:'Segoe UI',Arial,sans-serif;">
  <!-- Preheader -->
  <div style="display:none;max-height:0;overflow:hidden;color:#0f0f1a;">{preview}</div>

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0f1a;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#6c3fff 0%,#a855f7 50%,#ec4899 100%);
                        border-radius:20px 20px 0 0;padding:36px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:800;letter-spacing:-0.5px;">Growny</h1>
              <p style="margin:6px 0 0;color:rgba(255,255,255,0.8);font-size:14px;">Your Personal Finance &amp; Task Assistant</p>
              <p style="margin:4px 0 0;color:rgba(255,255,255,0.6);font-size:13px;">{today}</p>
            </td>
          </tr>

          <!-- Title Bar -->
          <tr>
            <td style="background:#1a1a2e;padding:20px 40px 0;border-left:1px solid #2a2a4a;border-right:1px solid #2a2a4a;">
              <h2 style="margin:0;color:#e2e8f0;font-size:22px;font-weight:700;">{title}</h2>
              <div style="height:3px;background:linear-gradient(90deg,#6c3fff,#ec4899);border-radius:2px;margin-top:10px;"></div>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="background:#1a1a2e;padding:28px 40px;border-left:1px solid #2a2a4a;border-right:1px solid #2a2a4a;">
              {content_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#111126;border-radius:0 0 20px 20px;padding:24px 40px;text-align:center;
                        border:1px solid #2a2a4a;border-top:none;">
              <p style="margin:0;color:#6b7280;font-size:13px;">
                Sent by <strong style="color:#a855f7;">Growny Assistant</strong> · 
                <a href="#" style="color:#6c3fff;text-decoration:none;">Manage Notifications</a>
              </p>
                You're receiving this because you're a Growny user.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _card(title: str, value: str, color: str = "#6c3fff") -> str:
    return f"""
    <td width="33%" style="text-align:center;padding:4px;">
      <div style="background:#242442;border-radius:12px;padding:16px 12px;border-top:3px solid {color};">
        <div style="color:#a0aec0;font-size:11px;margin:4px 0 2px;text-transform:uppercase;letter-spacing:0.5px;">{title}</div>
        <div style="color:#e2e8f0;font-size:16px;font-weight:700;">{value}</div>
      </div>
    </td>"""


def _alert_badge(level: str) -> str:
    colors = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}
    c = colors.get(level, "#6b7280")
    return f'<span style="background:{c}22;color:{c};font-size:11px;font-weight:700;padding:2px 8px;border-radius:20px;border:1px solid {c}55;">{level}</span>'


# ─────────────────────────────────────────────
# Public Email Functions
# ─────────────────────────────────────────────

def send_daily_digest(to_email: str, user_name: str, wealth: dict, tasks: list, ai_insight: str) -> dict:
    """Send the daily overview digest email."""
    currency = wealth.get("currency", "INR")
    income = wealth.get("total_income", 0)
    expense = wealth.get("total_expense", 0)
    balance = wealth.get("net_balance", 0)
    balance_color = "#10b981" if balance >= 0 else "#ef4444"
    balance_sign = "+" if balance >= 0 else ""

    # Finance cards
    cards_html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        {_card("Total Income", f"{currency} {income:,.0f}", "#10b981")}
        {_card("Total Expense", f"{currency} {expense:,.0f}", "#ef4444")}
        {_card("Net Balance", f"{balance_sign}{currency} {abs(balance):,.0f}", balance_color)}
      </tr>
    </table>"""

    # Category breakdown
    breakdown = wealth.get("category_breakdown", {})
    breakdown_html = ""
    if breakdown:
        breakdown_html = '<p style="color:#a0aec0;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin:20px 0 10px;">Spending by Category</p>'
        for cat, amt in sorted(breakdown.items(), key=lambda x: -x[1])[:6]:
            pct = (amt / expense * 100) if expense > 0 else 0
            breakdown_html += f"""
            <div style="margin-bottom:10px;">
              <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                <span style="color:#e2e8f0;font-size:13px;">{cat}</span>
                <span style="color:#a0aec0;font-size:13px;">{currency} {amt:,.0f} ({pct:.0f}%)</span>
              </div>
              <div style="background:#2a2a4a;border-radius:4px;height:6px;">
                <div style="background:linear-gradient(90deg,#6c3fff,#a855f7);border-radius:4px;height:6px;width:{min(pct,100):.0f}%;"></div>
              </div>
            </div>"""

    # Tasks section
    tasks_html = ""
    if tasks:
        tasks_html = f'<p style="color:#a0aec0;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin:20px 0 10px;">Tasks Due Today ({len(tasks)})</p>'
        for t in tasks[:6]:
            tasks_html += f"""
            <div style="background:#242442;border-radius:10px;padding:12px 16px;margin-bottom:8px;
                         border-left:3px solid #6c3fff;display:flex;align-items:center;gap:10px;">
              <span>{_alert_badge(t.get("priority","MEDIUM"))}</span>
              <span style="color:#e2e8f0;font-size:14px;">{t.get("content","")}</span>
            </div>"""
    else:
        tasks_html = """<div style="background:#242442;border-radius:10px;padding:16px;text-align:center;margin-top:16px;">
            <p style="color:#6b7280;margin:6px 0 0;font-size:14px;">No tasks due today. Great day to get ahead!</p>
          </div>"""

    # AI insight
    insight_html = f"""
    <div style="background:linear-gradient(135deg,#1e1b4b,#2d1b69);border-radius:14px;
                padding:20px;margin-top:20px;border:1px solid #6c3fff44;">
      <p style="margin:0 0 8px;color:#a855f7;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.5px;">
        AI Insight
      </p>
      <p style="margin:0;color:#e2e8f0;font-size:15px;line-height:1.6;">{ai_insight}</p>
    </div>"""

    content = f"""
    <p style="margin:0 0 20px;color:#a0aec0;font-size:15px;line-height:1.6;">
      Hey <strong style="color:#e2e8f0;">{user_name}</strong>! Here's your financial and task overview for today.
    </p>
    {cards_html}
    {breakdown_html}
    {tasks_html}
    {insight_html}"""

    html = _base_template(
        title="Your Daily Overview",
        preview=f"Balance: {currency} {balance:,.0f} · {len(tasks)} tasks due today",
        content_html=content
    )
    return _send_email(to_email, f"Growny Daily Digest — {datetime.now().strftime('%b %d, %Y')}", html)


def send_important_alert(to_email: str, user_name: str, alert_type: str, details: dict) -> dict:
    """Send an urgent/important alert email."""
    alert_configs = {
        "HIGH_EXPENSE": {
            "color": "#ef4444", "title": "High Spending Alert",
            "headline": "You've had unusually high expenses today!"
        },
        "OVERDUE_TASK": {
            "color": "#f59e0b", "title": "Overdue Task Alert",
            "headline": "You have overdue tasks that need attention!"
        },
        "NEGATIVE_BALANCE": {
            "color": "#ef4444", "title": "Balance Warning",
            "headline": "Your expenses are exceeding your income!"
        },
        "BUDGET_MILESTONE": {
            "color": "#10b981", "title": "Milestone Achieved",
            "headline": "Great news — you've hit a savings milestone!"
        },
    }

    cfg = alert_configs.get(alert_type, {"color": "#6c3fff", "title": "Important Update", "headline": "Something needs your attention."})
    message = details.get("message", "Please review your Growny dashboard for details.")
    data_points = details.get("data_points", [])

    data_html = ""
    if data_points:
        data_html = '<ul style="margin:16px 0;padding:0;list-style:none;">'
        for point in data_points:
            data_html += f'<li style="color:#e2e8f0;font-size:14px;padding:6px 0;border-bottom:1px solid #2a2a4a;">• {point}</li>'
        data_html += "</ul>"

    content = f"""
    <div style="background:linear-gradient(135deg,{cfg["color"]}22,{cfg["color"]}11);
                border-radius:14px;padding:24px;border:1px solid {cfg["color"]}44;margin-bottom:20px;">
      <h3 style="margin:0 0 8px;color:{cfg["color"]};text-align:center;font-size:18px;">{cfg["headline"]}</h3>
      <p style="margin:0;color:#a0aec0;text-align:center;font-size:14px;line-height:1.6;">{message}</p>
    </div>

    Hey <strong style="color:#e2e8f0;">{user_name}</strong>,
    {data_html}

    <div style="text-align:center;margin-top:24px;">
      <a href="http://localhost:3000" 
         style="background:linear-gradient(135deg,#6c3fff,#a855f7);color:#fff;text-decoration:none;
                padding:14px 32px;border-radius:10px;font-weight:700;font-size:15px;display:inline-block;">
        Open Growny Dashboard →
      </a>
    </div>"""

    html = _base_template(
        title=f"{cfg['title']}",
        preview=cfg["headline"],
        content_html=content
    )
    return _send_email(to_email, f"Growny Alert: {cfg['title']}", html)


def send_missed_info_reminder(to_email: str, user_name: str, missing_items: list) -> dict:
    """Send an email when the user hasn't logged data in a while."""
    items_html = ""
    for item in missing_items:
        items_html += f"""
        <div style="background:#242442;border-radius:10px;padding:14px 18px;margin-bottom:10px;
                     border-left:3px solid #f59e0b;">
          <p style="margin:0;color:#fbbf24;font-size:13px;font-weight:600;">{item.get("title","")}</p>
          <p style="margin:4px 0 0;color:#a0aec0;font-size:13px;">{item.get("description","")}</p>
        </div>"""

    content = f"""
    <p style="margin:0 0 20px;color:#a0aec0;font-size:15px;line-height:1.6;">
      Hey <strong style="color:#e2e8f0;">{user_name}</strong>! We noticed some information might be missing from your Growny profile. 
      Keeping your data up-to-date helps us give you better insights.
    </p>
    <p style="color:#a0aec0;font-size:13px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;margin:0 0 12px;">
      What's Missing
    </p>
    {items_html}

    <div style="background:linear-gradient(135deg,#1e1b4b,#2d1b69);border-radius:14px;
                padding:18px;margin-top:20px;border:1px solid #6c3fff44;text-align:center;">
      <p style="margin:0 0 12px;color:#e2e8f0;font-size:14px;">Update your information now to get the most out of Growny!</p>
      <a href="http://localhost:3000"
         style="background:linear-gradient(135deg,#6c3fff,#a855f7);color:#fff;text-decoration:none;
                padding:12px 28px;border-radius:10px;font-weight:700;font-size:14px;display:inline-block;">
        Update Now →
      </a>
    </div>"""

    html = _base_template(
        title="Don't Forget to Log Your Data",
        preview="Some information seems to be missing from your Growny profile.",
        content_html=content
    )
    return _send_email(to_email, "Growny Reminder: Your data needs updating", html)
