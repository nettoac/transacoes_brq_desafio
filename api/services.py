import uuid
import json
import asyncio
import time
from typing import Dict, Optional, Any
from .models import Transaction, TransactionStatus, TransactionType
import threading
import pickle
import os

# Simulação de armazenamento persistente entre workers
STORAGE_FILE = "c:/desenv/desafio_brq/transactions_storage.pkl"
storage_lock = threading.Lock()

def load_storage():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'rb') as f:
            return pickle.load(f)
    return {
        'transactions': {},
        'status': {},
        'metrics': {
            "total_requests": 0,
            "start_time": time.time(),
            "latencies": []
        }
    }

def save_storage(storage_data):
    with storage_lock:
        with open(STORAGE_FILE, 'wb') as f:
            pickle.dump(storage_data, f)

# Iniciando o armazenamento persistente entre workers
storage = load_storage()
transactions_table = storage['transactions']
transactions_status_table = storage['status']
metrics = storage['metrics']

sqs_queue = []  # Simula fila SQS

async def send_to_sqs(transaction: Transaction):
    """Simula o envio de transação para o SQS"""
    print(f"[SQS] Sending transaction {transaction.transactionID} to queue")
    sqs_queue.append(transaction.transactionID)
    await asyncio.sleep(0.005)  
    print(f"[SQS] Transaction {transaction.transactionID} queued successfully")

async def create_transaction(account_id: str, amount: float, transaction_type: str) -> Transaction:
    start_time = time.time()
    
    transaction = Transaction(
        transactionID=str(uuid.uuid4()),
        accountID=account_id,
        amount=amount,
        type=TransactionType(transaction_type),
        status=TransactionStatus.IN_PROCESSING
    )
    
    # Persistindo a transação
    transactions_table[transaction.transactionID] = transaction.model_dump()
    save_storage({
        'transactions': transactions_table,
        'status': transactions_status_table,
        'metrics': metrics
    })
    
    await send_to_sqs(transaction)  # Readicionando a transação para processamento SQS
    asyncio.create_task(process_transaction(transaction.transactionID))
    
    metrics["total_requests"] += 1
    metrics["latencies"].append(time.time() - start_time)
    
    return transaction

async def process_transaction(transaction_id: str):
    print(f"[Lambda] Processing transaction {transaction_id}")
    await asyncio.sleep(0.01)
    
    if transaction_id in transactions_table:
        transactions_status_table[transaction_id] = {
            "transactionID": transaction_id,
            "status": TransactionStatus.PROCESSED,
            "processed_at": time.time()
        }
        # Salvando o status atualizado
        save_storage({
            'transactions': transactions_table,
            'status': transactions_status_table,
            'metrics': metrics
        })
        print(f"[Lambda] Transaction {transaction_id} processed successfully")

async def get_transaction(transaction_id: str) -> Optional[Dict]:
    start_time = time.time()
    
    storage = load_storage()
    transactions_table = storage['transactions']
    transactions_status_table = storage['status']
    
    print(f"[DEBUG] Searching for transaction: {transaction_id}")
    print(f"[DEBUG] Available transactions: {list(transactions_table.keys())}")
    print(f"[DEBUG] Available status: {list(transactions_status_table.keys())}")
    
    result = None
    if transaction_id in transactions_status_table:
        result = transactions_status_table[transaction_id]
    elif transaction_id in transactions_table:
        result = transactions_table[transaction_id]
    
    metrics["latencies"].append(time.time() - start_time)
    return result

def get_metrics():
    """Obtém métricas de desempenho da API"""
    total_time = time.time() - metrics["start_time"]
    total_requests = metrics["total_requests"]
    
    if not metrics["latencies"]:
        return {
            "tps": 0,
            "p99_latency": 0,
            "total_requests": 0
        }
    
    tps = total_requests / total_time if total_time > 0 else 0
    sorted_latencies = sorted(metrics["latencies"])
    p99_index = int(len(sorted_latencies) * 0.99)
    p99_latency = sorted_latencies[p99_index] if p99_index > 0 else sorted_latencies[-1]
    
    return {
        "tps": round(tps, 2),
        "p99_latency": round(p99_latency * 1000, 2),  # Converte para milissegundos
        "total_requests": total_requests
    }