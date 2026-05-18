from pydantic import BaseModel
from typing import List, Optional, Any

class ChatMessage(BaseModel):
    text: str
    history: Optional[List[dict]] = None

class AgentResponse(BaseModel):
    reply: str
    action_type: Optional[str] = None
    data: Optional[Any] = None

class SearchRequest(BaseModel):
    query: str

class SearchResult(BaseModel):
    id: int
    content: str
    category: Optional[str]
    priority: Optional[str]
    due_date: Optional[str]
    similarity: float

class TaskResponse(BaseModel):
    id: int
    content: str
    raw_text: Optional[str]
    category: Optional[str]
    priority: Optional[str]
    due_date: Optional[str]
    created_at: Optional[str]

class TransactionRequest(BaseModel):
    type: str
    amount: float
    currency: str = 'INR'
    category: Optional[str]
    description: str
    date: Optional[str]
    
class TransactionResponse(BaseModel):
    id: int
    type: str
    amount: float
    currency: str
    category: Optional[str]
    description: str
    source: Optional[str]
    date: Optional[str]
    tags: Optional[List[str]]
    created_at: Optional[str]
