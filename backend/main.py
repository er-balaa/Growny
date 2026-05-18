import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers import chat, tasks, transactions, insights, email
from config import supabase, groq_client

app = FastAPI(title="My Wise Backend", version="1.0.0")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "*" 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(transactions.router, prefix="/api", tags=["Transactions"])
app.include_router(insights.router, prefix="/api", tags=["Insights"])
app.include_router(email.router, prefix="/api", tags=["Email"])

@app.get("/api/health")
async def health_check():
    return {
        "message": "My Wise Backend API",
        "version": "2.0.0",
        "status": {
            "supabase": "connected" if supabase else "not configured",
            "groq": "connected" if groq_client else "not configured",
            "auth": "jwt_verification",
            "agent_mode": "fallback_llm"
        }
    }

@app.get("/{full_path:path}")
async def catch_all(full_path: str):
    from fastapi.responses import HTMLResponse, FileResponse
    static_file_path = f"static/{full_path}"
    if os.path.exists(static_file_path) and os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    
    index_path = "static/index.html"
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            content = f.read()
        return HTMLResponse(content=content)
    return {"message": "Frontend not built"}

@app.on_event("startup")
async def startup_event():
    import asyncio
    from services.automation_service import poll_tasks_and_send_emails
    asyncio.create_task(poll_tasks_and_send_emails())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
