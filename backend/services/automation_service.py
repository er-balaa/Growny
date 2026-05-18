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
                        
            if reminders_sent:
                _save_json(SENT_EMAILS_FILE, sent_emails)
                
        except Exception as e:
            print(f"[Automation] Error in polling loop: {e}")
            
        # Poll every 5 minutes
        await asyncio.sleep(300)
