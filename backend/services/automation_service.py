import asyncio
import json
import os
import pathlib
from datetime import datetime, timedelta
from config import supabase
from services.email_service import send_task_reminder_email, send_missed_task_email

# ── Persistent path helper ──
# On Render, CWD can vary. Always resolve relative to backend/.
_BACKEND_DIR = pathlib.Path(__file__).parent.parent

# ── In-memory fallback for sent-email dedup ──
# This survives within a single process lifetime on Render.
# JSON file is still used locally as a bonus, but is NOT relied upon.
_memory_sent = {"reminders": set(), "missed": set(), "digests": {}}

SENT_EMAILS_FILE = str(_BACKEND_DIR / "sent_emails.json")
USER_EMAILS_FILE = str(_BACKEND_DIR / "user_emails.json")


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


def _get_user_emails() -> dict:
    """
    Get user email mappings.
    Priority: Supabase users table → local JSON file cache.
    """
    user_emails = {}

    # Try Supabase first — the users info is in auth tokens cached during login
    # Fall back to the local JSON file
    try:
        data = _load_json(USER_EMAILS_FILE, {})
        if data:
            user_emails.update(data)
    except Exception:
        pass

    # Also try fetching from Supabase transactions/tasks to discover user IDs
    # and cross-reference with cached emails
    if supabase and not user_emails:
        try:
            # Try to get distinct user_ids from tasks table
            result = supabase.table("tasks").select("user_id").execute()
            user_ids = set(t.get("user_id") for t in (result.data or []) if t.get("user_id"))
            # We can only send emails to users we know — log a warning
            if user_ids:
                print(f"[Automation] Found {len(user_ids)} users in DB but no email cache. "
                      "Users need to log in once to enable email notifications.")
        except Exception:
            pass

    return user_emails


def _is_already_sent(category: str, task_id: str, sent_emails: dict) -> bool:
    """Check both in-memory and file-based dedup."""
    # Check in-memory first (survives Render restarts within a deploy)
    if task_id in _memory_sent.get(category, set()):
        return True
    # Check file-based
    if task_id in sent_emails.get(category, []):
        return True
    return False


def _mark_sent(category: str, task_id: str, sent_emails: dict):
    """Mark in both in-memory and file-based stores."""
    _memory_sent.setdefault(category, set()).add(task_id)
    if category not in sent_emails:
        sent_emails[category] = []
    if task_id not in sent_emails[category]:
        sent_emails[category].append(task_id)


async def poll_tasks_and_send_emails():
    """Background loop to check for upcoming and overdue tasks."""
    print("[Automation] Starting task polling service...")
    
    while True:
        try:
            if not supabase:
                print("[Automation] Supabase not connected, waiting...")
                await asyncio.sleep(300)
                continue
                
            # Load states
            sent_emails = _load_json(SENT_EMAILS_FILE, {"reminders": [], "missed": []})
            user_emails = _get_user_emails()
            
            if not user_emails:
                print("[Automation] No user emails cached yet. Users need to log in once.")
                await asyncio.sleep(300)
                continue
            
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
                
                if not email:
                    continue
                
                # Check Overdue
                if due_date < today:
                    if not _is_already_sent("missed", task_id, sent_emails):
                        print(f"[Automation] Sending Missed Task email to {email}")
                        result_email = send_missed_task_email(email, name, content, due_date_str)
                        if result_email.get("success"):
                            _mark_sent("missed", task_id, sent_emails)
                            reminders_sent = True
                        else:
                            print(f"[Automation] Failed to send missed email: {result_email.get('error')}")
                        
                # Check Due Soon (Today or Tomorrow)
                elif due_date == today or due_date == tomorrow:
                    if not _is_already_sent("reminders", task_id, sent_emails):
                        print(f"[Automation] Sending Reminder email to {email}")
                        result_email = send_task_reminder_email(email, name, content, due_date_str, priority)
                        if result_email.get("success"):
                            _mark_sent("reminders", task_id, sent_emails)
                            reminders_sent = True
                        else:
                            print(f"[Automation] Failed to send reminder email: {result_email.get('error')}")
                        
            # Check 8 PM Daily Digest
            if now.hour == 20:
                from routers.email import _groq_insight
                from services.email_service import send_daily_digest
                from agents.tools.db_tools import get_wealth_summary, get_tasks_entered_today
                
                today_str = today.strftime("%Y-%m-%d")
                
                if "digests" not in sent_emails:
                    sent_emails["digests"] = {}
                
                for user_id, user_info in user_emails.items():
                    already_sent_digest = (
                        sent_emails.get("digests", {}).get(user_id) == today_str
                        or _memory_sent["digests"].get(user_id) == today_str
                    )
                    
                    if not already_sent_digest:
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
                            
                            result_email = send_daily_digest(
                                to_email=user_info["email"],
                                user_name=user_info.get("name", "User").split(' ')[0],
                                wealth=wealth,
                                tasks=tasks_entered_today,
                                ai_insight=ai_insight
                            )
                            if result_email.get("success"):
                                sent_emails.setdefault("digests", {})[user_id] = today_str
                                _memory_sent["digests"][user_id] = today_str
                                reminders_sent = True
                            else:
                                print(f"[Automation] Failed to send digest: {result_email.get('error')}")
                        except Exception as e:
                            print(f"[Automation] Failed to send daily digest to {user_id}: {e}")
                        
            if reminders_sent:
                _save_json(SENT_EMAILS_FILE, sent_emails)
                
        except Exception as e:
            print(f"[Automation] Error in polling loop: {e}")
            import traceback
            traceback.print_exc()
            
        # Poll every 5 minutes
        await asyncio.sleep(300)


async def poll_tasks_and_send_emails_once():
    """
    Single-run version of the email checker. 
    Called by the /api/cron/check-emails endpoint (triggered by Render cron).
    Returns a summary of what was done.
    """
    summary = {"reminders_sent": 0, "missed_sent": 0, "digests_sent": 0, "errors": []}
    
    try:
        if not supabase:
            summary["errors"].append("Supabase not connected")
            return summary
            
        sent_emails = _load_json(SENT_EMAILS_FILE, {"reminders": [], "missed": []})
        user_emails = _get_user_emails()
        
        if not user_emails:
            summary["errors"].append("No user emails cached. Users need to log in once.")
            return summary
        
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
                continue
            
            user_info = user_emails.get(user_id)
            if not user_info:
                continue
                
            email = user_info.get("email")
            name = user_info.get("name", "User").split(' ')[0]
            
            if not email:
                continue
            
            if due_date < today:
                if not _is_already_sent("missed", task_id, sent_emails):
                    result_email = send_missed_task_email(email, name, content, due_date_str)
                    if result_email.get("success"):
                        _mark_sent("missed", task_id, sent_emails)
                        summary["missed_sent"] += 1
                        reminders_sent = True
                        
            elif due_date == today or due_date == tomorrow:
                if not _is_already_sent("reminders", task_id, sent_emails):
                    result_email = send_task_reminder_email(email, name, content, due_date_str, priority)
                    if result_email.get("success"):
                        _mark_sent("reminders", task_id, sent_emails)
                        summary["reminders_sent"] += 1
                        reminders_sent = True
        
        # Daily digest
        from routers.email import _groq_insight
        from services.email_service import send_daily_digest
        from agents.tools.db_tools import get_wealth_summary, get_tasks_entered_today
        
        today_str = today.strftime("%Y-%m-%d")
        if "digests" not in sent_emails:
            sent_emails["digests"] = {}
        
        for user_id, user_info in user_emails.items():
            already_sent_digest = (
                sent_emails.get("digests", {}).get(user_id) == today_str
                or _memory_sent["digests"].get(user_id) == today_str
            )
            if not already_sent_digest:
                try:
                    wealth = get_wealth_summary(user_id)
                    tasks_entered = get_tasks_entered_today(user_id)
                    
                    currency = wealth.get("currency", "INR")
                    today_expense = wealth.get("today_expense", 0)
                    balance = wealth.get("net_balance", 0)
                    
                    task_list_str = "\\n".join([f"  - [{t.get('priority','?')}] {t.get('content','')}" for t in tasks_entered]) or "  No tasks entered today."
                    insight_prompt = (
                        f"User's daily summary:\\n"
                        f"- Today's Expense: {currency} {today_expense:,.2f}\\n"
                        f"- Net Balance: {currency} {balance:,.2f}\\n"
                        f"Tasks entered today:\\n{task_list_str}\\n\\n"
                        "Write a short (2-3 sentences) friendly and motivating daily insight."
                    )
                    ai_insight = _groq_insight(insight_prompt)
                    
                    result_email = send_daily_digest(
                        to_email=user_info["email"],
                        user_name=user_info.get("name", "User").split(' ')[0],
                        wealth=wealth,
                        tasks=tasks_entered,
                        ai_insight=ai_insight
                    )
                    if result_email.get("success"):
                        sent_emails.setdefault("digests", {})[user_id] = today_str
                        _memory_sent["digests"][user_id] = today_str
                        summary["digests_sent"] += 1
                        reminders_sent = True
                except Exception as e:
                    summary["errors"].append(f"Digest for {user_id}: {str(e)}")
        
        if reminders_sent:
            _save_json(SENT_EMAILS_FILE, sent_emails)
            
    except Exception as e:
        summary["errors"].append(str(e))
    
    return summary
