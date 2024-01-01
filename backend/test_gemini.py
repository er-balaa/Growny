import google.generativeai as genai
import json
import re
from datetime import datetime

# Configure Gemini
genai.configure(api_key='AIzaSyCA3IYmYDOcoNsGNiDcLeg0EzH4UDjX55s')
model = genai.GenerativeModel('gemini-2.0-flash')

def analyze_todo(text: str) -> dict:
    """
    Uses LLM to clean and categorize information
    Called: Once per task creation only
    Model: gemini-2.0-flash (fastest, cheapest)
    """
    prompt = f"""
    Current Date: {datetime.now().strftime('%Y-%m-%d')}
    Input: "{text}"

    Extract into JSON:
    - category: "TASK", "REMINDER", or "NOTE"
    - priority: "HIGH", "MEDIUM", or "LOW"
    - summary: "Professional one-sentence summary (must not be empty)"
    - due_date: "YYYY-MM-DD" or null
    """
    try:
        print(f"Sending prompt to Gemini: {prompt}")
        response = model.generate_content(prompt)
        print(f"Raw Gemini response: {response.text}")
        
        match = re.search(r'\{.*\}', response.text, re.DOTALL)
        if match:
            data = json.loads(match.group())
            # Fallback if summary is missing
            if not data.get('summary'):
               data['summary'] = text
            return data
        return {"category": "NOTE", "priority": "MEDIUM", "summary": text, "due_date": None}
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {"category": "NOTE", "priority": "MEDIUM", "summary": text, "due_date": None}

if __name__ == "__main__":
    test_text = "buy milk"
    result = analyze_todo(test_text)
    print(f"Result: {result}")
