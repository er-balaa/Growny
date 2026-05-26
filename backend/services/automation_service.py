import asyncio
import json
import os
from datetime import datetime, timedelta
from config import supabase
from services.email_service import send_task_reminder_email, send_missed_task_email

SENT_EMAILS_FILE = "sent_emails.json"
USER_EMAILS_FILE = "user_emails.json"

def _load_json(filepath, default):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def _save_json(filepath, data):
    try:
        with open(filepath, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"[Automation] Failed to save {filepath}: {e}")

async def poll_tasks_and_send_emails():
    """Background loop to check for upcoming and overdue tasks."""
    print("[Automation] Starting task polling service...")
    
    while True:
        try:
            if not supabase:
                await asyncio.sleep(300)
                continue
                
            # Load states
            sent_emails = _load_json(SENT_EMAILS_FILE, {"reminders": [], "missed": []})
            user_emails = _load_json(USER_EMAILS_FILE, {})
            
            # Fetch all pending tasks with a due date
            result = supabase.table("tasks").select("*").not_.is_("due_date", "null").execute()
            tasks = result.data or []
            
            now = datetime.now()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            tomorrow = today + timedelta(days=1)
            
            reminders_sent = False
            
            for task in tasks:
                task_id = str(task.get("id"))
                due_date_str = task.get("due_date")
                user_id = task.get("user_id")
                content = task.get("content", "A task")
                priority = task.get("priority", "MEDIUM")
                
                if not due_date_str or not user_id:
                    continue
                
                try:
                    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
                except ValueError:
                    continue # Invalid date format
                
                user_info = user_emails.get(user_id)
                if not user_info:
                    continue # We don't have this user's email cached
                    
                email = user_info.get("email")
                name = user_info.get("name", "User").split(' ')[0]
                
                # Check Overdue
                if due_date < today:
                    if task_id not in sent_emails["missed"]:
                        print(f"[Automation] Sending Missed Task email to {email}")
                        send_missed_task_email(email, name, content, due_date_str)
                        sent_emails["missed"].append(task_id)
                        reminders_sent = True
                        
                # Check Due Soon (Today or Tomorrow)
                elif due_date == today or due_date == tomorrow:
                    if task_id not in sent_emails["reminders"]:
                        print(f"[Automation] Sending Reminder email to {email}")
                        send_task_reminder_email(email, name, content, due_date_str, priority)
                        sent_emails["reminders"].append(task_id)
                        reminders_sent = True
                        
            # Check 8 PM Daily Digest
            if now.hour == 20:
                from routers.email import _groq_insight
                from services.email_service import send_daily_digest
                from agents.tools.db_tools import get_wealth_summary, get_tasks_entered_today
                
                today_str = today.strftime("%Y-%m-%d")
                
                if "digests" not in sent_emails:
                    sent_emails["digests"] = {}
                
                for user_id, user_info in user_emails.items():
                    if user_id not in sent_emails["digests"] or sent_emails["digests"][user_id] != today_str:
                        print(f"[Automation] Sending 8 PM Daily Digest to {user_info.get('email')}")
                        try:
                            wealth = get_wealth_summary(user_id)
                            tasks_entered_today = get_tasks_entered_today(user_id)
                            
                            currency = wealth.get("currency", "INR")
                            today_expense = wealth.get("today_expense", 0)
                            balance = wealth.get("net_balance", 0)
                            breakdown = wealth.get("category_breakdown", {})
                            
                            breakdown_str = "\\n".join([f"  - {cat}: {currency} {amt:,.2f}" for cat, amt in breakdown.items()]) or "  No spending recorded yet."
                            task_list_str = "\\n".join([f"  - [{t.get('priority','?')}] {t.get('content','')}" for t in tasks_entered_today]) or "  No tasks entered today."
                            
                            insight_prompt = (
                                f"User's daily summary:\\n"
                                f"- Today's Expense: {currency} {today_expense:,.2f}\\n"
                                f"- Net Balance: {currency} {balance:,.2f}\\n"
                                f"Tasks entered today:\\n{task_list_str}\\n\\n"
                                "Write a short (2-3 sentences) friendly and motivating daily insight. "
                                "Comment on their activity today and give one actionable tip."
                            )
                            ai_insight = _groq_insight(insight_prompt)
                            
                            send_daily_digest(
                                to_email=user_info["email"],
                                user_name=user_info.get("name", "User").split(' ')[0],
                                wealth=wealth,
                                tasks=tasks_entered_today,
                                ai_insight=ai_insight
                            )
                            sent_emails["digests"][user_id] = today_str
                            reminders_sent = True
                        except Exception as e:
                            print(f"[Automation] Failed to send daily digest to {user_id}: {e}")
                            
            if reminders_sent:
                _save_json(SENT_EMAILS_FILE, sent_emails)
                
        except Exception as e:
            print(f"[Automation] Error in polling loop: {e}")
            
        # Poll every 5 minutes
        await asyncio.sleep(300)
