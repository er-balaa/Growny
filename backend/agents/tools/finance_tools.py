"""
Finance Tools — Calculation and budget analysis helpers for the Financial Crew.
"""
from typing import List, Dict


def calculate_totals(transactions: List[Dict]) -> Dict:
    """
    Given a list of transaction records, compute total income, total expense,
    and net balance.
    """
    total_income = sum(t.get("amount", 0) for t in transactions if t.get("type") == "INCOME")
    total_expense = sum(t.get("amount", 0) for t in transactions if t.get("type") == "EXPENSE")
    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "net_balance": round(total_income - total_expense, 2),
    }


def spending_by_category(transactions: List[Dict]) -> Dict[str, float]:
    """
    Aggregate expense amounts by category.
    Returns a dict: {category: total_amount}
    """
    breakdown: Dict[str, float] = {}
    for t in transactions:
        if t.get("type") == "EXPENSE":
            cat = t.get("category", "General")
            breakdown[cat] = round(breakdown.get(cat, 0) + t.get("amount", 0), 2)
    return dict(sorted(breakdown.items(), key=lambda x: x[1], reverse=True))


def budget_checker(transactions: List[Dict], monthly_budget: float = 20000.0) -> Dict:
    """
    Check if current month spending is within a monthly budget limit.
    Returns spend so far, budget remaining, and a warning flag.
    """
    totals = calculate_totals(transactions)
    spent = totals["total_expense"]
    remaining = round(monthly_budget - spent, 2)
    over_budget = remaining < 0
    return {
        "monthly_budget": monthly_budget,
        "spent_so_far": spent,
        "remaining": remaining,
        "over_budget": over_budget,
        "warning": f"You've exceeded your monthly budget by ₹{abs(remaining):,.2f}!" if over_budget
                   else f"₹{remaining:,.2f} remaining in your monthly budget."
    }
