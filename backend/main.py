from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
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

# Mount static files for frontend (mount before other routes)
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS Configuration - Fixed to include all necessary origins
origins = [
    "http://localhost:5173",
    "http://localhost:3000", 
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "*"  # Allow all origins for production deployment
]

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
        print("[OK] Firebase Admin initialized")
    else:
        print(f"Warning: Firebase admin SDK file not found at {firebase_creds_path}. Auth endpoints will be limited.")
except Exception as e:
    print(f"Warning: Firebase initialization error: {e}")

# Initialize Supabase and Gemini
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
    print("[OK] Supabase initialized")
except Exception as e:
    print(f"[ERROR] Supabase initialization error: {e}")
    supabase = None

try:
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel('gemini-2.0-flash')
    print("[OK] Gemini initialized")
except Exception as e:
    print(f"[ERROR] Gemini initialization error: {e}")
    model = None

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

def get_vector(text: str) -> Optional[List[float]]:
    """Generates 768-dim vector using Gemini embedding"""
    if not model:
        print("[ERROR] Gemini model not available")
        return None
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
    """Uses LLM to clean and categorize information"""
    if not model:
        print("[ERROR] Gemini model not available, using fallback")
        return {"category": "NOTE", "priority": "MEDIUM", "summary": text, "due_date": None}
    
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
    """Verify Firebase ID token"""
    try:
        token = credentials.credentials
        print(f"[AUTH] Received token (first 50 chars): {token[:50] if token else 'None'}...")
        
        if not token or token == "test":
            print("[AUTH] Token is empty or 'test'")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if Firebase Admin is initialized
        if not firebase_admin._apps:
            print("[AUTH] ERROR: Firebase Admin SDK not initialized!")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Firebase Admin SDK not initialized",
            )
        
        decoded_token = auth.verify_id_token(token)
        print(f"[AUTH] Token verified successfully for user: {decoded_token.get('uid', 'unknown')}")
        return decoded_token
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH] Token verification failed: {type(e).__name__}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# API Endpoints
@app.get("/")
async def root():
    """Health check"""
    return {"message": "Growny-AI Backend API", "version": "1.0.0"}

@app.get("/app")
async def serve_frontend():
    """Serve the frontend SPA"""
    index_path = "static/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r") as f:
            content = f.read()
        return content
    return {"message": "Frontend not built yet"}

@app.post("/api/tasks", response_model=dict)
async def create_task(task: TaskRequest, user_data: dict = Depends(verify_firebase_token)):
    """Create a new task with AI analysis"""
    print(f"=== CREATE TASK DEBUG ===")
    print(f"Request task text: '{task.text}'")
    print(f"User data: {user_data}")
    
    if not task.text or not task.text.strip():
        print("ERROR: Empty task text")
        raise HTTPException(status_code=400, detail="Task text cannot be empty")

    if not supabase:
        print("ERROR: Supabase not available")
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        print(f"Creating task for user: {user_data['uid']}")
        
        # Step 1: Analyze the task
        print("Calling Gemini for analysis...")
        data = analyze_todo(task.text)
        print(f"Analysis complete: {data}")
        
        # Ensure summary is not empty
        summary_text = data.get('summary')
        if not summary_text:
            summary_text = task.text
            print(f"Using fallback summary: {summary_text}")

        # Step 2: Generate embedding
        print(f"Generating embedding for: {summary_text[:50]}...")
        vector = get_vector(summary_text)
        
        if not vector:
            print("ERROR: Vector generation returned None")
            # Continue without vector instead of failing
            vector = []
        
        # Step 3: Save to Supabase
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
        
        print(f"[OK] Task saved successfully: {result.data[0]['id']}")
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
    """Search tasks using vector similarity"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")

    try:
        print(f"Searching for: {search.query}")
        
        # Generate embedding for search query
        vector = get_vector(search.query)
        if not vector:
            # Fallback to text search if vector generation fails
            result = supabase.table("tasks").select("*").eq("user_id", user_data['uid']).ilike("content", f"%{search.query}%").execute()
        else:
            # Use vector search
            try:
                result = supabase.rpc("match_tasks", {
                    "query_embedding": vector,
                    "match_threshold": 0.7,
                    "match_count": 10,
                    "filter_user_id": user_data['uid']
                }).execute()
            except:
                # Fallback to text search if vector search fails
                result = supabase.table("tasks").select("*").eq("user_id", user_data['uid']).ilike("content", f"%{search.query}%").execute()
        
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
    """Get all tasks for the authenticated user"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
        
    try:
        print(f"Fetching tasks for user: {user_data['uid']}")
        result = supabase.table("tasks").select("*").eq("user_id", user_data['uid']).order("created_at", desc=True).execute()
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
    """Delete a specific task"""
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
        
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
