from fastapi import APIRouter, HTTPException
from .models import TransactionRequest, TransactionResponse, TransactionStatus
from .services import create_transaction, get_transaction, get_metrics
from typing import Dict, Any, Optional

router = APIRouter(prefix="/api/v1")

@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction_endpoint(transaction: TransactionRequest):
    """
    Create a new transaction
    """
    result = await create_transaction(
        account_id=transaction.accountID,
        amount=transaction.amount,
        transaction_type=transaction.type
    )
    
    return TransactionResponse(
        transactionID=result.transactionID,
        status=result.status
    )

@router.get("/transactions/{transaction_id}")
async def get_transaction_endpoint(transaction_id: str):
    """
    Get transaction status by ID
    """
    transaction = await get_transaction(transaction_id)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return {
        "transactionID": transaction["transactionID"],
        "status": transaction["status"]
    }

@router.get("/metrics")
async def get_api_metrics():
    """Get API performance metrics"""
    return get_metrics()