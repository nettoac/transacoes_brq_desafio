import asyncio
import uuid
import aiohttp
import time


async def test_transaction_flow():
    async with aiohttp.ClientSession() as session:
        # Criando uma transação
        transaction_data = {
            "accountID": str(uuid.uuid4()),
            "amount": 100.50,
            "type": "credit"
        }
        
        print("\n1. Creating transaction...")
        async with session.post('http://localhost:8000/api/v1/transactions', json=transaction_data) as response:
            result = await response.json()
            transaction_id = result['transactionID']
            print(f"Transaction created with ID: {transaction_id}")
            print(f"Initial status: {result['status']}")
        
        print("\n2. Waiting for processing...")
        await asyncio.sleep(1)
        
        # Pegando status da metrica
        print("\n3. Checking final status...")
        async with session.get(f'http://localhost:8000/api/v1/transactions/{transaction_id}') as response:
            result = await response.json()
            print(f"Final status: {result['status']}")

async def load_test(num_requests=100, concurrent=10):
    async with aiohttp.ClientSession() as session:
        tasks = []
        start_time = time.time()
        
        async def make_request():
            transaction_data = {
                "accountID": str(uuid.uuid4()),
                "amount": 100.50,
                "type": "credit"
            }
            async with session.post('http://localhost:8000/api/v1/transactions', json=transaction_data) as response:
                return await response.json()
        
        for _ in range(num_requests):
            tasks.append(make_request())
            if len(tasks) >= concurrent:
                await asyncio.gather(*tasks)
                tasks = []
        
        if tasks:
            await asyncio.gather(*tasks)
        
        total_time = time.time() - start_time
        print(f"\nLoad test completed:")
        print(f"Total requests: {num_requests}")
        print(f"Time taken: {total_time:.2f} seconds")
        print(f"Average TPS: {num_requests/total_time:.2f}")

async def main():
    # Teste de fluxo de transação única
    print("\n=== Testing Single Transaction Flow ===")
    await test_transaction_flow()
    
    # Carregando testes
    print("\n=== Running Load Test ===")
    await load_test(num_requests=100, concurrent=10)
    
    # Pegando métricas da API
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:8000/api/v1/metrics') as response:
            metrics = await response.json()
            print("\n=== API Metrics ===")
            print(f"TPS: {metrics['tps']}")
            print(f"P99 Latency: {metrics['p99_latency']}ms")
            print(f"Total Requests: {metrics['total_requests']}")

if __name__ == "__main__":
    asyncio.run(main())