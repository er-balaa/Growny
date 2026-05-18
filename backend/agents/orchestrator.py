import json
from config import groq_client
from agents.financial_agent import process_finance_message
from agents.task_agent import process_task_message
from agents.tools.web_tools import get_current_datetime
from agents.tools.db_tools import get_wealth_summary, get_all_tasks


def _build_user_context(user_id: str) -> str:
    """Fetch real user data from Supabase and format it as a context string."""
    try:
        wealth = get_wealth_summary(user_id)
        currency = wealth.get("currency", "INR")
        total_income = wealth.get("total_income", 0)
        total_expense = wealth.get("total_expense", 0)
        net_balance = wealth.get("net_balance", 0)
        tx_count = wealth.get("transaction_count", 0)
        breakdown = wealth.get("category_breakdown", {})
        recent_txns = wealth.get("recent_transactions", [])

        finance_lines = [
            f"💰 FINANCIAL SUMMARY ({currency}):",
            f"  • Total Income : {currency} {total_income:,.2f}",
            f"  • Total Expense: {currency} {total_expense:,.2f}",
            f"  • Net Balance  : {currency} {net_balance:,.2f}",
            f"  • Transactions : {tx_count} total",
        ]
        if breakdown:
            finance_lines.append("  • Spending by Category:")
            for cat, amt in sorted(breakdown.items(), key=lambda x: -x[1])[:8]:
                finance_lines.append(f"      - {cat}: {currency} {amt:,.2f}")
        if recent_txns:
            finance_lines.append("  • Recent Transactions:")
            for t in recent_txns[:5]:
                sign = "+" if t.get("type") == "INCOME" else "-"
                finance_lines.append(
                    f"      - {t.get('date', '?')}: {sign}{currency} {t.get('amount', 0):,.2f} ({t.get('description', 'N/A')})"
                )

        # Tasks
        all_tasks = get_all_tasks(user_id, limit=50)
        pending = [t for t in all_tasks if not t.get("completed")]
        done = [t for t in all_tasks if t.get("completed")]

        task_lines = [
            f"\n📋 TASK SUMMARY:",
            f"  • Total Tasks  : {len(all_tasks)}",
            f"  • Pending      : {len(pending)}",
            f"  • Completed    : {len(done)}",
        ]
        if pending:
            task_lines.append("  • Pending Tasks:")
            for t in pending[:10]:
                due = f" (due: {t['due_date']})" if t.get("due_date") else ""
                task_lines.append(
                    f"      - [{t.get('priority','?')}] [{t.get('category','?')}] {t.get('content','')}{due}"
                )

        return "\n".join(finance_lines + task_lines)

    except Exception as e:
        print(f"[Context] Error building user context: {e}")
        return "No personal data available yet."


def _groq_answer_with_context(text: str, history: list, user_id: str) -> str:
    """Answer the user's question with full access to their real DB data."""
    if not groq_client:
        return "AI service unavailable."

    user_context = _build_user_context(user_id)

    system_prompt = (
        "You are Growny, a smart personal finance and task assistant. "
        "You have FULL access to the user's real financial and task data shown below. "
        "Always use this data to answer accurately. "
        "If they ask 'how much do I have?', compute and answer from the net balance. "
        "If they ask about tasks, list them clearly. "
        "Never say you don't have access to their data — you do.\n\n"
        f"Today: {get_current_datetime()}\n\n"
        f"=== USER'S PERSONAL DATA ===\n{user_context}\n"
        "=== END OF DATA ===\n\n"
        "Respond in a friendly, concise manner. Use emojis where appropriate."
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in (history or [])[-8:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": text})

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.4,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"I ran into an issue: {str(e)}"


def classify_intent(text: str, history: list) -> str:
    """
    Classify whether the user wants to:
    - LOG_FINANCE  : save a new income/expense transaction
    - SAVE_TASK    : save a new task/note/reminder
    - QUERY        : ask a question about their data or anything else
    """
    if not groq_client:
        return "QUERY"

    history_str = ""
    if history:
        history_str = "Recent context:\n" + "\n".join(
            [f"{m['role']}: {m['content']}" for m in history[-6:]]
        ) + "\n\n"

    prompt = (
        history_str +
        'Classify the user\'s message into exactly ONE category:\n'
        '- "LOG_FINANCE": User is explicitly recording/logging a new financial transaction (income or expense). '
        'Examples: "I spent 500 on groceries", "got salary 50000", "paid 200 for coffee".\n'
        '- "SAVE_TASK": User is explicitly creating a new task, reminder, or note to be saved. '
        'Examples: "remind me to call doctor", "add task: buy milk", "note: project deadline friday".\n'
        '- "QUERY": Everything else — questions about their balance, spending, tasks, general advice, greetings, calculations. '
        'Examples: "how much do I have?", "what are my tasks?", "show my expenses", "how much did I spend?", "what is my balance?".\n\n'
        'IMPORTANT: Questions are always "QUERY", even if they mention money or tasks.\n\n'
        'Return JSON only: {"intent": "LOG_FINANCE" | "SAVE_TASK" | "QUERY"}\n'
        f'Message: "{text}"'
    )

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.0,
        )
        data = json.loads(response.choices[0].message.content)
        intent = data.get("intent", "QUERY")
        if intent not in ("LOG_FINANCE", "SAVE_TASK", "QUERY"):
            intent = "QUERY"
        print(f"[Intent] '{text[:60]}' => {intent}")
        return intent
    except Exception as e:
        print(f"[Intent] Classification error: {e}")
        return "QUERY"


def route_message(text: str, user_id: str, history: list = None, user_email: str = "", user_name: str = "") -> dict:
    intent = classify_intent(text, history)

    if intent == "LOG_FINANCE":
        reply = process_finance_message(text, user_id, user_email=user_email, user_name=user_name)
        # If it couldn't parse a transaction, answer the question instead
        if "couldn't quite understand" in reply.lower() or "error" in reply.lower():
            reply = _groq_answer_with_context(text, history, user_id)
            return {"reply": reply, "action_type": "GENERAL", "data": None}
        return {"reply": reply, "action_type": "FINANCE", "data": None}

    if intent == "SAVE_TASK":
        reply = process_task_message(text, user_id)
        if "error" in reply.lower():
            reply = _groq_answer_with_context(text, history, user_id)
            return {"reply": reply, "action_type": "GENERAL", "data": None}
        return {"reply": reply, "action_type": "TASK", "data": None}

    # QUERY — answer with full user context from DB
    reply = _groq_answer_with_context(text, history, user_id)
    return {"reply": reply, "action_type": "GENERAL", "data": None}
