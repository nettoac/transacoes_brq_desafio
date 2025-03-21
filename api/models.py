from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional
from datetime import datetime
from uuid import uuid4

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionStatus(str, Enum):
    IN_PROCESSING = "in_processing"
    PROCESSED = "processed"
    FAILED = "failed"

class TransactionRequest(BaseModel):
    accountID: str = Field(..., description="Account ID")
    amount: float = Field(..., description="Transaction amount")
    type: TransactionType = Field(..., description="Transaction type")

class Transaction(BaseModel):
    transactionID: str = Field(default_factory=lambda: str(uuid4()))
    accountID: str
    amount: float
    type: TransactionType
    status: TransactionStatus = TransactionStatus.IN_PROCESSING
    
class TransactionResponse(BaseModel):
    transactionID: str
    status: TransactionStatus