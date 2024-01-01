from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import os
import json
import re
from datetime import datetime
import google.generativeai as genai
from supabase import create_client
import firebase_admin
from firebase_admin import auth, credentials
from dotenv import load_dotenv
import pathlib

# Load environment variables explicitly from backend directory if not found
env_path = pathlib.Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

print("--- STARTUP DEBUG ---")
print(f"Loading env from: {env_path}")
print(f"GEMINI_API_KEY present: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL')}")
print(f"SUPABASE_KEY present: {bool(os.getenv('SUPABASE_KEY'))}")
print(f"FIREBASE_PATH: {os.getenv('FIREBASE_ADMIN_SDK_PATH')}")
print("---------------------")

app = FastAPI(title="Growny-AI Backend", version="1.0.0")

# CORS Configuration
origins = os.getenv("CORS_ORIGINS", '["http://localhost:5173", "http://localhost:3000"]')
try:
    origins = json.loads(origins)
except:
    origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Firebase
try:
    firebase_creds_path = os.getenv("FIREBASE_ADMIN_SDK_PATH")
    # Resolve relative path
    if firebase_creds_path and firebase_creds_path.startswith("./"):
        firebase_creds_path = str(pathlib.Path(__file__).parent / firebase_creds_path[2:])
        
    if os.path.exists(firebase_creds_path):
        cred = credentials.Certificate(firebase_creds_path)
        # Check if app is already initialized to avoid "App already exists" error
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        print("✅ Firebase Admin initialized")
    else:
        print(f"Warning: Firebase admin SDK file not found at {firebase_creds_path}. Auth endpoints will be limited.")
except Exception as e:
    print(f"Warning: Firebase initialization error: {e}")

# Initialize Supabase and Gemini
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.0-flash')
security = HTTPBearer()

# Pydantic Models
class TaskRequest(BaseModel):
    text: str

class TaskResponse(BaseModel):
    id: int
    content: str
    raw_text: Optional[str]
    category: Optional[str]
    priority: Optional[str]
    due_date: Optional[str]
    created_at: Optional[str]

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    id: int
    content: str
    category: Optional[str]
    priority: Optional[str]
    due_date: Optional[str]
    similarity: float

# ============================================
# GEMINI API CALLS - EFFICIENT IMPLEMENTATION
# ============================================
#
# When Gemini is called:
# 1. CREATE TASK: 2 API calls
#    - analyze_todo(): LLM call to categorize & summarize (gemini-2.0-flash)
#    - get_vector(): Embedding call for semantic search (text-embedding-004)
#
# 2. SEARCH: 1 API call
#    - get_vector(): Embedding call for search query
#
# 3. GET/DELETE TASKS: 0 API calls (database only)
#
# Optimizations implemented:
# - Use gemini-2.0-flash (fastest model)
# - Use text-embedding-004 (768 dimensions, efficient)
# - Embed the SUMMARY not raw text (shorter = faster)
# - No redundant calls on read operations
# ============================================

def get_vector(text: str) -> Optional[List[float]]:
    """
    Generates 768-dim vector using Gemini embedding
    Called: Once per task creation, once per search
    Cost: Very low (embedding model is cheap)
    """
    try:
        res = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_document"
        )
        return res['embedding']
    except Exception as e:
        print(f"Vector Error: {e}")
        return None

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
        response = model.generate_content(prompt)
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

async def verify_firebase_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify Firebase ID token - NO Gemini call"""
    try:
        token = credentials.credentials
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        print(f"Auth Error: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# API Endpoints
@app.get("/")
async def root():
    """Health check - NO Gemini call"""
    return {"message": "Growny-AI Backend API", "version": "1.0.0"}

@app.post("/api/tasks", response_model=dict)
async def create_task(task: TaskRequest, user_data: dict = Depends(verify_firebase_token)):
    """
    Create a new task with AI analysis
    GEMINI CALLS: 2 (analyze + embed)
    """
    print(f"=== CREATE TASK DEBUG ===")
    print(f"Request task text: '{task.text}'")
    print(f"User data: {user_data}")
    
    if not task.text or not task.text.strip():
        print("ERROR: Empty task text")
        raise HTTPException(status_code=400, detail="Task text cannot be empty")

    try:
        print(f"Creating task for user: {user_data['uid']}")
        
        # Step 1: Analyze the task (1 Gemini LLM call)
        print("Calling Gemini for analysis...")
        data = analyze_todo(task.text)
        print(f"Analysis complete: {data}")
        
        # Ensure summary is not empty
        summary_text = data.get('summary')
        if not summary_text:
            summary_text = task.text
            print(f"Using fallback summary: {summary_text}")

        # Step 2: Generate embedding (1 Gemini embedding call)
        print(f"Generating embedding for: {summary_text[:50]}...")
        vector = get_vector(summary_text)  # Use summary (shorter = faster)
        
        if not vector:
            print("ERROR: Vector generation returned None")
            raise HTTPException(status_code=500, detail="Failed to generate vector embedding. Gemini API Key check logs.")
        print(f"✅ Embedding generated, length: {len(vector)}")
        
        # Step 3: Save to Supabase (NO Gemini call)
        payload = {
            "content": summary_text,
            "raw_text": task.text,
            "category": data.get('category', 'NOTE'),
            "priority": data.get('priority', 'MEDIUM'),
            "due_date": data.get('due_date'),
            "embedding": vector,
            "user_id": user_data['uid']
        }
        print(f"Supabase payload prepared: {payload}")
        
        result = supabase.table("tasks").insert(payload).execute()
        
        if not result.data:
            print("ERROR: Supabase insert returned no data")
            raise HTTPException(status_code=500, detail="Failed to save task to Supabase")
        
        print(f"✅ Task saved successfully: {result.data[0]['id']}")
        return {
            "success": True,
            "message": "Task saved successfully",
            "task": result.data[0]
        }
        
    except HTTPException as he:
        print(f"HTTP Exception: {he.detail}")
        raise he
    except Exception as e:
        print(f"ERROR: Exception in create_task: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@app.post("/api/search", response_model=List[SearchResult])
async def search_tasks(search: SearchRequest, user_data: dict = Depends(verify_firebase_token)):
    """
    Search tasks using vector similarity
    GEMINI CALLS: 1 (embed search query)
    """

    try:
        print(f"Searching for: {search.query}")
        
        # Generate embedding for search query (1 Gemini call)
        vector = get_vector(search.query)
        if not vector:
            raise HTTPException(status_code=500, detail="Failed to generate search vector")
        
        # Database query (NO Gemini call)
        result = supabase.rpc("match_tasks", {
            "query_embedding": vector,
            "match_threshold": 0.7,
            "match_count": 10,
            "filter_user_id": user_data['uid']
        }).execute()
        
        if not result.data:
            return []
        
        return [
            SearchResult(
                id=item['id'],
                content=item['content'],
                category=item.get('category'),
                priority=item.get('priority'),
                due_date=item.get('due_date'),
                similarity=item.get('similarity', 0.0)
            )
            for item in result.data
        ]
        
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error searching tasks: {str(e)}")

@app.get("/api/tasks", response_model=List[TaskResponse])
async def get_tasks(user_data: dict = Depends(verify_firebase_token)):
    """
    Get all tasks for the authenticated user
    GEMINI CALLS: 0 (database only)
    """
    try:
        print(f"Fetching tasks for user: {user_data['uid']}")
        result = supabase.table("tasks").select("*").eq("user_id", user_data['uid']).execute()
        print(f"Found {len(result.data)} tasks")
        
        tasks = []
        for item in result.data:
            try:
                tasks.append(TaskResponse(
                    id=int(item.get('id', 0)),
                    content=str(item.get('content', '')),
                    raw_text=item.get('raw_text'),
                    category=item.get('category'),
                    priority=item.get('priority'),
                    due_date=item.get('due_date'),
                    created_at=str(item.get('created_at', '')) if item.get('created_at') else None
                ))
            except Exception as item_error:
                print(f"Error processing task: {item_error}")
                continue
        
        return tasks
        
    except Exception as e:
        print(f"Error fetching tasks: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: str, user_data: dict = Depends(verify_firebase_token)):
    """
    Delete a specific task
    GEMINI CALLS: 0 (database only)
    """
    try:
        result = supabase.table("tasks").delete().eq("id", task_id).eq("user_id", user_data['uid']).execute()
        
        if not result.data:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return {"success": True, "message": "Task deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
