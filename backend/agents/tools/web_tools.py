"""
Web Tools — DuckDuckGo search and datetime utilities for agentic use.
Uses duckduckgo-search (no API key required).
"""
from datetime import datetime


def get_current_datetime() -> str:
    """Return the current date and time as a human-readable string."""
    return datetime.now().strftime("%A, %B %d, %Y at %I:%M %p")


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo and return a formatted string of results.
    Falls back gracefully if the package is unavailable.
    """
    try:
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"• {r['title']}: {r['body']}")
        if results:
            return "\n".join(results)
        return "No results found for the given query."
    except ImportError:
        return "Web search is unavailable. Install duckduckgo-search."
    except Exception as e:
        return f"Web search error: {str(e)}"
