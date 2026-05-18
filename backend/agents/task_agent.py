import json
from datetime import datetime
from config import groq_client, supabase
import google.generativeai as genai
import os

def get_vector(text: str):
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return None
        
    try:
        genai.configure(api_key=gemini_key)
        res = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return res['embedding']
    except Exception as e:
        print(f"Vector error: {e}")
        return None

def analyze_todo(text: str) -> dict:
    if not groq_client:
        return {"category": "NOTE", "priority": "MEDIUM", "summary": text, "due_date": None}
    
    prompt_template = """
    Current Date: """ + datetime.now().strftime('%Y-%m-%d') + """

    Analyze the user input and classify it into one of these exact categories:
    1. "TASK" - Actionable items that need to be done.
    2. "REMINDER" - ONLY if the user explicitly uses the word 'remind' or 'reminder'. Otherwise, use 'TASK' or 'NOTE'.
    3. "NOTE" - General information, ideas, or references to save.

    Provide the result as a JSON object containing exactly these fields:
    - "category": strictly "TASK", "REMINDER", or "NOTE".
    - "priority": strictly "HIGH", "MEDIUM", or "LOW".
    - "summary": A neat, actionable restatement. Use an imperative or first-person tone.
    - "due_date": "YYYY-MM-DD" or null.
    """
    
    prompt = prompt_template + '\nInput: "' + text + '"'
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        data = json.loads(response.choices[0].message.content)
        if data.get('category') not in ['TASK', 'REMINDER', 'NOTE']:
             data['category'] = 'NOTE'
        if not data.get('summary'):
           data['summary'] = text
        return data
    except Exception as e:
        print(f"AI Analysis Error: {e}")
        return {"category": "NOTE", "priority": "MEDIUM", "summary": text, "due_date": None}

def process_task_message(text: str, user_id: str) -> str:
    data = analyze_todo(text)
    
    if not supabase:
        return "Database connection error. Could not save task."
        
    try:
        summary_text = data.get('summary', text)
        vector = get_vector(summary_text)
        
        payload = {
            "content": summary_text,
            "raw_text": text,
            "category": data.get('category', 'NOTE'),
            "priority": data.get('priority', 'MEDIUM'),
            "due_date": data.get('due_date'),
            "embedding": vector,
            "user_id": user_id
        }
        
        result = supabase.table("tasks").insert(payload).execute()
        
        if result.data:
            cat = result.data[0]['category'].capitalize()
            return f"{cat} saved: '{summary_text}'"
        return "Failed to save task."
    except Exception as e:
        print(f"Task DB Error: {e}")
        return f"Error saving task: {str(e)}"
