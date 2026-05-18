from fastapi import APIRouter, Depends, HTTPException
from typing import List
from auth import verify_firebase_token
from config import supabase
from models import TaskResponse

router = APIRouter()

@router.get("/tasks", response_model=List[TaskResponse])
async def get_tasks(user_data: dict = Depends(verify_firebase_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
        
    try:
        result = supabase.table("tasks").select("*").eq("user_id", user_data['uid']).order("created_at", desc=True).execute()
        
        tasks = []
        for item in result.data:
            tasks.append(TaskResponse(
                id=int(item.get('id', 0)),
                content=str(item.get('content', '')),
                raw_text=item.get('raw_text'),
                category=item.get('category'),
                priority=item.get('priority'),
                due_date=item.get('due_date'),
                created_at=str(item.get('created_at', '')) if item.get('created_at') else None
            ))
        return tasks
    except Exception as e:
        print(f"Tasks error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, user_data: dict = Depends(verify_firebase_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        # Fetch task before deleting to get content for email
        task_result = supabase.table("tasks").select("*").eq("id", task_id).eq("user_id", user_data['uid']).execute()
        
        result = supabase.table("tasks").delete().eq("id", task_id).eq("user_id", user_data['uid']).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Task not found")
            
        # Trigger Task Completion Email in background
        if task_result and task_result.data:
            task_content = task_result.data[0].get("content", "A task")
            user_email = user_data.get("email")
            user_name = user_data.get("name") or user_data.get("displayName") or "User"
            if user_email:
                import threading
                from services.email_service import send_task_completion_email
                def _send_completion():
                    try:
                        send_task_completion_email(user_email, user_name.split(' ')[0], task_content)
                    except Exception as e:
                        print(f"Failed to send completion email: {e}")
                threading.Thread(target=_send_completion, daemon=True).start()

        return {"success": True, "message": "Task deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
