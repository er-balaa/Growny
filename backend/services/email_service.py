"""
Email Service — Sends beautiful HTML emails via Gmail SMTP.

Triggers:
- Daily Overview digest (wealth + tasks summary)
- Important alerts (overdue tasks, high expense warnings)
- Missed information reminders
- Task Completion
- Task Reminders (Due Soon)
- Missed Task (Overdue)
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
    """Wrap content in a beautiful premium Black and Orange HTML email shell."""
    today = datetime.now().strftime("%B %d, %Y")
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{title}</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:'Segoe UI',Arial,sans-serif;">
  <!-- Preheader -->
  <div style="display:none;max-height:0;overflow:hidden;color:#0a0a0a;">{preview}</div>

  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0a;padding:32px 16px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#ff6b2c 0%,#ff8f5c 50%,#ffb088 100%);
                        border-radius:20px 20px 0 0;padding:36px 40px;text-align:center;">
              <h1 style="margin:0;color:#ffffff;font-size:28px;font-weight:800;letter-spacing:-0.5px;">Growny</h1>
              <p style="margin:6px 0 0;color:rgba(255,255,255,0.9);font-size:14px;font-weight:500;">Your Personal Finance &amp; Task Assistant</p>
              <p style="margin:4px 0 0;color:rgba(255,255,255,0.7);font-size:13px;">{today}</p>
            </td>
          </tr>

          <!-- Title Bar -->
          <tr>
            <td style="background:#171717;padding:20px 40px 0;border-left:1px solid #262626;border-right:1px solid #262626;">
              <h2 style="margin:0;color:#ffffff;font-size:22px;font-weight:700;">{title}</h2>
              <div style="height:3px;background:linear-gradient(90deg,#ff6b2c,#ff8f5c);border-radius:2px;margin-top:10px;"></div>
            </td>
          </tr>

          <!-- Content -->
          <tr>
            <td style="background:#171717;padding:28px 40px;border-left:1px solid #262626;border-right:1px solid #262626;">
              {content_html}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background:#111111;border-radius:0 0 20px 20px;padding:24px 40px;text-align:center;
                        border:1px solid #262626;border-top:none;">
              <p style="margin:0;color:#808080;font-size:13px;">
                Sent by <strong style="color:#ff6b2c;">Growny Assistant</strong> · 
                <a href="http://localhost:5173" style="color:#ff8f5c;text-decoration:none;">Manage Notifications</a>
              </p>
              <p style="margin:8px 0 0;color:#4d4d4d;font-size:12px;">
                You're receiving this because you're a Growny user.
              </p>
              <div style="margin-top:16px;padding-top:16px;border-top:1px solid #262626;text-align:left;">
                <p style="margin:0;color:#666666;font-size:11px;line-height:1.5;">
                  <strong>Policy Conditions:</strong> This email is generated automatically based on your active Growny profile. 
                  We respect your privacy. All financial and task data is securely processed to provide you with insights. 
                  Do not reply to this email. For support, please contact your administrator.
                </p>
              </div>
              <p style="margin:16px 0 0;color:#808080;font-size:14px;font-style:italic;">
                Best regards,<br/>The Growny Team
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


def _card(title: str, value: str, color: str = "#ff6b2c") -> str:
    return f"""
    <td width="33%" style="text-align:center;padding:4px;">
      <div style="background:#202020;border-radius:12px;padding:16px 12px;border-top:3px solid {color};">
        <div style="color:#b3b3b3;font-size:11px;margin:4px 0 2px;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;">{title}</div>
        <div style="color:#ffffff;font-size:16px;font-weight:700;">{value}</div>
      </div>
    </td>"""


def _alert_badge(level: str) -> str:
    colors = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}
    c = colors.get(level, "#808080")
    return f'<span style="background:{c}15;color:{c};font-size:11px;font-weight:700;padding:4px 10px;border-radius:12px;border:1px solid {c}44;display:inline-block;">{level}</span>'


# ─────────────────────────────────────────────
# Public Email Functions
# ─────────────────────────────────────────────

def send_daily_digest(to_email: str, user_name: str, wealth: dict, tasks: list, ai_insight: str) -> dict:
    """Send the daily overview digest email."""
    currency = wealth.get("currency", "INR")
    today_expense = wealth.get("today_expense", 0)
    balance = wealth.get("net_balance", 0)
    balance_color = "#10b981" if balance >= 0 else "#ef4444"
    balance_sign = "+" if balance >= 0 else ""

    # Finance cards focusing on Today's Expense and Net Balance
    cards_html = f"""
    <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
      <tr>
        {_card("Today's Expense", f"{currency} {today_expense:,.0f}", "#ef4444")}
        {_card("Net Balance", f"{balance_sign}{currency} {abs(balance):,.0f}", balance_color)}
        {_card("Tasks Added", f"{len(tasks)}", "#f59e0b")}
      </tr>
    </table>"""

    # Tasks section
    tasks_html = ""
    if tasks:
        tasks_html = f'<p style="color:#808080;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:20px 0 10px;">Tasks Entered Today ({len(tasks)})</p>'
        for t in tasks[:6]:
            tasks_html += f"""
            <div style="background:#202020;border-radius:10px;padding:12px 16px;margin-bottom:8px;
                         border-left:3px solid #ff6b2c;display:flex;align-items:center;gap:10px;">
              <span>{_alert_badge(t.get("priority","MEDIUM"))}</span>
              <span style="color:#ffffff;font-size:14px;">{t.get("content","")}</span>
            </div>"""
    else:
        tasks_html = """<div style="background:#202020;border-radius:10px;padding:16px;text-align:center;margin-top:16px;border:1px dashed #333;">
            <p style="color:#808080;margin:0;font-size:14px;">No new tasks added today.</p>
          </div>"""

    # AI insight
    insight_html = f"""
    <div style="background:linear-gradient(135deg,rgba(255,107,44,0.1),rgba(255,143,92,0.05));border-radius:14px;
                padding:20px;margin-top:20px;border:1px solid rgba(255,107,44,0.3);">
      <p style="margin:0 0 8px;color:#ff6b2c;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;">
        AI Insight
      </p>
      <p style="margin:0;color:#ffffff;font-size:15px;line-height:1.6;">{ai_insight}</p>
    </div>"""

    content = f"""
    <p style="margin:0 0 20px;color:#cccccc;font-size:15px;line-height:1.6;">
      Hey <strong style="color:#ffffff;">{user_name}</strong>! Here's your daily roundup at 8 PM.
    </p>
    {cards_html}
    {tasks_html}
    {insight_html}"""

    html = _base_template(
        title="Your Daily Roundup",
        preview=f"Spent Today: {currency} {today_expense:,.0f} · {len(tasks)} tasks added",
        content_html=content
    )
    return _send_email(to_email, f"Growny Daily Roundup — {datetime.now().strftime('%b %d, %Y')}", html)


def send_important_alert(to_email: str, user_name: str, alert_type: str, details: dict) -> dict:
    """Send an urgent/important alert email (e.g. Negative Balance)."""
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

    cfg = alert_configs.get(alert_type, {"color": "#ff6b2c", "title": "Important Update", "headline": "Something needs your attention."})
    message = details.get("message", "Please review your Growny dashboard for details.")
    data_points = details.get("data_points", [])

    data_html = ""
    if data_points:
        data_html = '<ul style="margin:16px 0;padding:0;list-style:none;">'
        for point in data_points:
            data_html += f'<li style="color:#ffffff;font-size:14px;padding:8px 0;border-bottom:1px solid #262626;"><span style="color:{cfg["color"]};margin-right:8px;">•</span>{point}</li>'
        data_html += "</ul>"

    content = f"""
    <div style="background:linear-gradient(135deg,{cfg["color"]}15,{cfg["color"]}05);
                border-radius:14px;padding:24px;border:1px solid {cfg["color"]}44;margin-bottom:24px;">
      <h3 style="margin:0 0 8px;color:{cfg["color"]};text-align:center;font-size:18px;font-weight:700;">{cfg["headline"]}</h3>
      <p style="margin:0;color:#cccccc;text-align:center;font-size:14px;line-height:1.6;">{message}</p>
    </div>

    <p style="margin:0 0 12px;color:#cccccc;font-size:15px;">Hey <strong style="color:#ffffff;">{user_name}</strong>,</p>
    {data_html}

    <div style="text-align:center;margin-top:32px;">
      <a href="http://localhost:5173" 
         style="background:linear-gradient(135deg,#ff6b2c,#ff8f5c);color:#fff;text-decoration:none;
                padding:14px 32px;border-radius:10px;font-weight:700;font-size:15px;display:inline-block;
                box-shadow:0 4px 12px rgba(255,107,44,0.3);">
        Open Growny Dashboard &rarr;
      </a>
    </div>"""

    html = _base_template(
        title=f"{cfg['title']}",
        preview=cfg["headline"],
        content_html=content
    )
    return _send_email(to_email, f"Growny Alert: {cfg['title']}", html)


def send_task_completion_email(to_email: str, user_name: str, task_content: str) -> dict:
    """Send an email when a task is completed."""
    content = f"""
    <div style="text-align:center;margin-bottom:24px;">
      <div style="width:48px;height:48px;background:rgba(16,185,129,0.15);border-radius:50%;
                  display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      <h3 style="margin:0;color:#10b981;font-size:20px;font-weight:700;">Task Completed!</h3>
    </div>
    
    <p style="margin:0 0 16px;color:#cccccc;font-size:15px;line-height:1.6;">
      Great job, <strong style="color:#ffffff;">{user_name}</strong>! You just crushed another task off your list.
    </p>
    
    <div style="background:#202020;border-left:4px solid #10b981;padding:16px;border-radius:8px;margin-bottom:24px;">
      <p style="margin:0;color:#ffffff;font-size:15px;font-weight:500;">{task_content}</p>
    </div>
    
    <p style="margin:0;color:#808080;font-size:14px;text-align:center;">Keep up the great momentum!</p>
    """
    
    html = _base_template(
        title="Task Accomplished",
        preview="You just crushed a task! Keep up the momentum.",
        content_html=content
    )
    return _send_email(to_email, "Growny: Task Completed!", html)


def send_task_reminder_email(to_email: str, user_name: str, task_content: str, due_date: str, priority: str) -> dict:
    """Send an email to remind the user of an upcoming task."""
    content = f"""
    <div style="background:linear-gradient(135deg,rgba(255,107,44,0.15),rgba(255,143,92,0.05));
                border-radius:14px;padding:24px;border:1px solid rgba(255,107,44,0.4);margin-bottom:24px;text-align:center;">
      <h3 style="margin:0 0 8px;color:#ff6b2c;font-size:18px;font-weight:700;">Upcoming Deadline Reminder</h3>
      <p style="margin:0;color:#cccccc;font-size:14px;line-height:1.6;">You have a task due soon that needs your attention.</p>
    </div>

    <p style="margin:0 0 16px;color:#cccccc;font-size:15px;">Hey <strong style="color:#ffffff;">{user_name}</strong>, just a friendly heads-up:</p>

    <div style="background:#202020;border-radius:10px;padding:16px 20px;margin-bottom:24px;border-left:4px solid #ff6b2c;">
      <p style="margin:0 0 8px;color:#ffffff;font-size:16px;font-weight:600;">{task_content}</p>
      <div style="display:flex;gap:12px;margin-top:12px;">
        {_alert_badge(priority)}
        <span style="background:#262626;color:#cccccc;font-size:11px;font-weight:600;padding:4px 10px;border-radius:12px;">Due: {due_date}</span>
      </div>
    </div>
    
    <div style="text-align:center;">
      <a href="http://localhost:5173" 
         style="background:linear-gradient(135deg,#ff6b2c,#ff8f5c);color:#fff;text-decoration:none;
                padding:12px 28px;border-radius:10px;font-weight:700;font-size:14px;display:inline-block;
                box-shadow:0 4px 12px rgba(255,107,44,0.3);">
        View Task &rarr;
      </a>
    </div>
    """
    
    html = _base_template(
        title="Upcoming Task Reminder",
        preview=f"Reminder: {task_content} is due soon.",
        content_html=content
    )
    return _send_email(to_email, "Growny Reminder: Task due soon", html)


def send_missed_task_email(to_email: str, user_name: str, task_content: str, due_date: str) -> dict:
    """Send an email when a task becomes overdue."""
    content = f"""
    <div style="text-align:center;margin-bottom:24px;">
      <div style="width:48px;height:48px;background:rgba(239,68,68,0.15);border-radius:50%;
                  display:inline-flex;align-items:center;justify-content:center;margin-bottom:12px;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
      </div>
      <h3 style="margin:0;color:#ef4444;font-size:20px;font-weight:700;">Task Missed</h3>
    </div>
    
    <p style="margin:0 0 16px;color:#cccccc;font-size:15px;line-height:1.6;">
      Hey <strong style="color:#ffffff;">{user_name}</strong>, looks like a deadline slipped by. It happens to the best of us!
    </p>
    
    <div style="background:#202020;border-left:4px solid #ef4444;padding:16px;border-radius:8px;margin-bottom:24px;">
      <p style="margin:0 0 8px;color:#ffffff;font-size:15px;font-weight:500;">{task_content}</p>
      <span style="color:#ef4444;font-size:12px;font-weight:600;">Was due on: {due_date}</span>
    </div>
    
    <div style="text-align:center;">
      <a href="http://localhost:5173" 
         style="background:linear-gradient(135deg,#ff6b2c,#ff8f5c);color:#fff;text-decoration:none;
                padding:12px 28px;border-radius:10px;font-weight:700;font-size:14px;display:inline-block;
                box-shadow:0 4px 12px rgba(255,107,44,0.3);">
        Reschedule Task &rarr;
      </a>
    </div>
    """
    
    html = _base_template(
        title="Task Overdue",
        preview=f"Missed Deadline: {task_content}",
        content_html=content
    )
    return _send_email(to_email, "Growny Alert: Task is overdue", html)


def send_missed_info_reminder(to_email: str, user_name: str, missing_items: list) -> dict:
    """Send an email when the user hasn't logged data in a while."""
    items_html = ""
    for item in missing_items:
        items_html += f"""
        <div style="background:#202020;border-radius:10px;padding:14px 18px;margin-bottom:10px;
                     border-left:3px solid #ff6b2c;">
          <p style="margin:0;color:#ffffff;font-size:13px;font-weight:600;">{item.get("title","")}</p>
          <p style="margin:4px 0 0;color:#b3b3b3;font-size:13px;">{item.get("description","")}</p>
        </div>"""

    content = f"""
    <p style="margin:0 0 20px;color:#cccccc;font-size:15px;line-height:1.6;">
      Hey <strong style="color:#ffffff;">{user_name}</strong>! We noticed some information might be missing from your Growny profile. 
      Keeping your data up-to-date helps us give you better insights.
    </p>
    <p style="color:#808080;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:1px;margin:0 0 12px;">
      What's Missing
    </p>
    {items_html}

    <div style="background:linear-gradient(135deg,rgba(255,107,44,0.1),rgba(255,143,92,0.05));border-radius:14px;
                padding:18px;margin-top:20px;border:1px solid rgba(255,107,44,0.3);text-align:center;">
      <p style="margin:0 0 12px;color:#ffffff;font-size:14px;">Update your information now to get the most out of Growny!</p>
      <a href="http://localhost:5173"
         style="background:linear-gradient(135deg,#ff6b2c,#ff8f5c);color:#fff;text-decoration:none;
                padding:12px 28px;border-radius:10px;font-weight:700;font-size:14px;display:inline-block;
                box-shadow:0 4px 12px rgba(255,107,44,0.3);">
        Update Now &rarr;
      </a>
    </div>"""

    html = _base_template(
        title="Don't Forget to Log Your Data",
        preview="Some information seems to be missing from your Growny profile.",
        content_html=content
    )
    return _send_email(to_email, "Growny Reminder: Your data needs updating", html)
