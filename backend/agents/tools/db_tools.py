"""
DB Tools — Reusable Supabase read/write functions for agentic use.
"""
from datetime import datetime
from config import supabase


def save_transaction(user_id: str, type_: str, amount: float, currency: str,
                     category: str, description: str, date: str = None, raw_text: str = "") -> dict:
    """Save a financial transaction to Supabase."""
    if not supabase:
        return {"success": False, "error": "Database not configured"}
    try:
        payload = {
            "user_id": user_id,
            "type": type_.upper(),
            "amount": float(amount),
            "currency": currency or "INR",
            "category": category or "General",
            "description": description,
            "raw_text": raw_text,
            "source": "agent",
            "date": date or datetime.now().strftime('%Y-%m-%d')
        }
        result = supabase.table("transactions").insert(payload).execute()
        if result.data:
            return {"success": True, "record": result.data[0]}
        return {"success": False, "error": "Insert returned no data"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def save_task(user_id: str, content: str, category: str, priority: str,
              due_date: str = None, raw_text: str = "", embedding=None) -> dict:
    """Save a task/reminder/note to Supabase."""
    if not supabase:
        return {"success": False, "error": "Database not configured"}
    try:
        payload = {
            "user_id": user_id,
            "content": content,
            "raw_text": raw_text,
            "category": category.upper() if category else "NOTE",
            "priority": priority.upper() if priority else "MEDIUM",
            "due_date": due_date,
            "embedding": embedding,
        }
        result = supabase.table("tasks").insert(payload).execute()
        if result.data:
            return {"success": True, "record": result.data[0]}
        return {"success": False, "error": "Insert returned no data"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_recent_transactions(user_id: str, limit: int = 10) -> list:
    """Fetch the most recent transactions for a user."""
    if not supabase:
        return []
    try:
        result = (
            supabase.table("transactions")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[DB] get_recent_transactions error: {e}")
        return []


def get_tasks_due_today(user_id: str) -> list:
    """Fetch tasks with a due date of today."""
    if not supabase:
        return []
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .eq("due_date", today)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[DB] get_tasks_due_today error: {e}")
        return []


def get_wealth_summary(user_id: str) -> dict:
    """Compute total income, total expense, and net balance from ALL transactions."""
    if not supabase:
        return {"total_income": 0, "total_expense": 0, "net_balance": 0, "today_expense": 0, "currency": "INR", "recent_transactions": []}
    try:
        result = (
            supabase.table("transactions")
            .select("*")
            .eq("user_id", user_id)
            .order("date", desc=True)
            .execute()
        )
        txns = result.data or []
        today_str = datetime.now().strftime('%Y-%m-%d')
        
        total_income = sum(t["amount"] for t in txns if t.get("type") == "INCOME")
        total_expense = sum(t["amount"] for t in txns if t.get("type") == "EXPENSE")
        today_expense = sum(t["amount"] for t in txns if t.get("type") == "EXPENSE" and t.get("date") == today_str)
        
        net_balance = total_income - total_expense
        category_breakdown = {}
        for t in txns:
            cat = t.get("category", "General")
            category_breakdown[cat] = category_breakdown.get(cat, 0) + t.get("amount", 0)
        return {
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "today_expense": round(today_expense, 2),
            "net_balance": round(net_balance, 2),
            "currency": txns[0].get("currency", "INR") if txns else "INR",
            "transaction_count": len(txns),
            "category_breakdown": category_breakdown,
            "recent_transactions": txns[:10]
        }
    except Exception as e:
        print(f"[DB] get_wealth_summary error: {e}")
        return {"total_income": 0, "total_expense": 0, "net_balance": 0, "today_expense": 0, "currency": "INR", "recent_transactions": []}


def get_all_tasks(user_id: str, limit: int = 50) -> list:
    """Fetch all tasks/reminders/notes for a user."""
    if not supabase:
        return []
    try:
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[DB] get_all_tasks error: {e}")
        return []

def get_tasks_entered_today(user_id: str) -> list:
    """Fetch tasks created today."""
    if not supabase:
        return []
    try:
        today_start = datetime.now().strftime('%Y-%m-%dT00:00:00')
        result = (
            supabase.table("tasks")
            .select("*")
            .eq("user_id", user_id)
            .gte("created_at", today_start)
            .execute()
        )
        return result.data or []
    except Exception as e:
        print(f"[DB] get_tasks_entered_today error: {e}")
        return []
