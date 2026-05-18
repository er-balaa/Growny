from fastapi import APIRouter, Depends, HTTPException
from auth import verify_firebase_token
from models import ChatMessage, AgentResponse
from agents.orchestrator import route_message

router = APIRouter()

@router.post("/chat", response_model=AgentResponse)
async def unified_chat(chat: ChatMessage, user_data: dict = Depends(verify_firebase_token)):
    print(f"=== CHAT DEBUG ===")
    print(f"Message: {chat.text}")
    print(f"User: {user_data['uid']}")
    
    if not chat.text or not chat.text.strip():
        raise HTTPException(status_code=400, detail="Chat text cannot be empty")
        
    try:
        result = route_message(
            text=chat.text,
            user_id=user_data['uid'],
            history=chat.history,
            user_email=user_data.get('email', ''),
            user_name=user_data.get('name') or 'there'
        )
        return AgentResponse(
            reply=result.get("reply", "Done."),
            action_type=result.get("action_type", "GENERAL"),
            data=result.get("data")
        )
    except Exception as e:
        print(f"Chat Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
