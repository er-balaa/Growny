import json
import threading
from datetime import datetime
from config import groq_client, supabase


def _get_balance(user_id: str) -> tuple:
    """Return (total_income, total_expense, net_balance) for the user."""
    if not supabase:
        return 0, 0, 0
    try:
        result = supabase.table("transactions").select("type,amount").eq("user_id", user_id).execute()
        txns = result.data or []
        income  = sum(t["amount"] for t in txns if t.get("type") == "INCOME")
        expense = sum(t["amount"] for t in txns if t.get("type") == "EXPENSE")
        return round(income, 2), round(expense, 2), round(income - expense, 2)
    except Exception as e:
        print(f"[Balance] Error: {e}")
        return 0, 0, 0


def _send_negative_balance_alert(user_email: str, user_name: str,
                                  income: float, expense: float, balance: float, currency: str):
    """Fire-and-forget: send the negative balance alert in a background thread."""
    def _send():
        try:
            from services.email_service import send_important_alert
            send_important_alert(
                to_email=user_email,
                user_name=user_name,
                alert_type="NEGATIVE_BALANCE",
                details={
                    "message": (
                        f"Your expenses ({currency} {expense:,.2f}) are now exceeding "
                        f"your income ({currency} {income:,.2f}). Your balance is negative!"
                    ),
                    "data_points": [
                        f"Total Income : {currency} {income:,.2f}",
                        f"Total Expense: {currency} {expense:,.2f}",
                        f"Net Balance  : {currency} {balance:,.2f}  ⚠️ NEGATIVE",
                        "Tip: Review your largest expense categories and reduce discretionary spending.",
                    ]
                }
            )
            print(f"[Alert] Negative balance email sent to {user_email}")
        except Exception as e:
            print(f"[Alert] Failed to send negative balance email: {e}")

    thread = threading.Thread(target=_send, daemon=True)
    thread.start()


def analyze_transaction(text: str) -> dict:
    if not groq_client:
        return None

    prompt_template = """
    Current Date: """ + datetime.now().strftime('%Y-%m-%d') + """

    Extract financial transaction details from the text.
    Return a JSON object with exactly these fields:
    - "type": strictly "INCOME" or "EXPENSE"
    - "amount": numeric value (e.g., 50.0)
    - "currency": e.g., "USD", "INR" (default to INR if unknown)
    - "category": e.g., "Groceries", "Salary", "Transport", "Rent", "Dining"
    - "description": brief summary of what the transaction was for
    - "date": "YYYY-MM-DD" (use current date if not specified)

    If the text is NOT a transaction, return {"is_transaction": false}
    """

    prompt = prompt_template + '\nInput text: "' + text + '"'

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(response.choices[0].message.content)
        return data
    except Exception as e:
        print(f"Financial Agent Error: {e}")
        return None


def process_finance_message(text: str, user_id: str, user_email: str = "", user_name: str = "") -> str:
    data = analyze_transaction(text)

    if not data or data.get("is_transaction") is False or "amount" not in data:
        return "I couldn't quite understand the transaction details. Could you specify the amount and what it was for?"

    if not supabase:
        return "Database connection error. Could not save transaction."

    try:
        currency = data.get("currency", "INR")
        payload = {
            "user_id": user_id,
            "type": data.get("type", "EXPENSE"),
            "amount": data.get("amount", 0.0),
            "currency": currency,
            "category": data.get("category", "General"),
            "description": data.get("description", text),
            "raw_text": text,
            "source": "chat",
            "date": data.get("date", datetime.now().strftime('%Y-%m-%d'))
        }

        result = supabase.table("transactions").insert(payload).execute()

        if result.data:
            saved = result.data[0]
            amount   = saved['amount']
            type_str = "Income" if saved['type'] == 'INCOME' else "Expense"
            reply    = f"Logged {type_str}: {currency} {amount} for {saved['description']}."

            # ── Auto-check balance after every transaction ──────────
            income, expense, balance = _get_balance(user_id)
            if balance < 0 and user_email:
                _send_negative_balance_alert(user_email, user_name, income, expense, balance, currency)

            return reply

        return "Failed to log transaction."
    except Exception as e:
        print(f"Finance DB Error: {e}")
        return f"Error saving transaction: {str(e)}"
