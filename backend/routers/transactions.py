from fastapi import APIRouter, Depends, HTTPException
from typing import List
from auth import verify_firebase_token
from config import supabase
from models import TransactionResponse

router = APIRouter()

@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(user_data: dict = Depends(verify_firebase_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
        
    try:
        result = supabase.table("transactions").select("*").eq("user_id", user_data['uid']).order("created_at", desc=True).execute()
        
        transactions = []
        for item in result.data:
            transactions.append(TransactionResponse(
                id=int(item.get('id', 0)),
                type=item.get('type', ''),
                amount=float(item.get('amount', 0)),
                currency=item.get('currency', 'INR'),
                category=item.get('category'),
                description=item.get('description', ''),
                source=item.get('source'),
                date=item.get('date'),
                tags=item.get('tags'),
                created_at=str(item.get('created_at', '')) if item.get('created_at') else None
            ))
        return transactions
    except Exception as e:
        print(f"Transactions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/transactions/{tx_id}")
async def delete_transaction(tx_id: str, user_data: dict = Depends(verify_firebase_token)):
    if not supabase:
        raise HTTPException(status_code=500, detail="Database not available")
    try:
        result = supabase.table("transactions").delete().eq("id", tx_id).eq("user_id", user_data['uid']).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return {"success": True, "message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
