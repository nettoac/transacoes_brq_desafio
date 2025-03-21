import asyncio
import aiohttp
import time
import uuid
import os

async def send_transaction(session, transaction_data, timeout=10):
    try:
        async with session.post(
            'http://localhost:8000/api/v1/transactions', 
            json=transaction_data,
            timeout=timeout
        ) as response:
            return await response.json()
    except (aiohttp.ClientConnectorError, asyncio.TimeoutError, 
            aiohttp.ServerDisconnectedError) as e:
        print(f"Erro na requisição: {type(e).__name__}")
        await asyncio.sleep(0.5)
        return None

async def check_server_availability():
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get('http://localhost:8000/api/v1/metrics') as response:
                return response.status == 200
    except Exception as e:
        print(f"Erro ao verificar disponibilidade do servidor: {e}")
        return False

async def run_stress_test(total_transactions=1000, concurrent_requests=50):
    print(f"\nIniciando teste de stress com {total_transactions} transações...")
    print(f"Requisições concorrentes: {concurrent_requests}")
    
    # Verificar se o servidor está disponível
    server_available = await check_server_availability()
    if not server_available:
        print("\n⚠️ ERRO: Servidor não está disponível em http://localhost:8000")
        print("Por favor, verifique se o servidor está rodando com o comando:")
        print("python main.py")
        return
    
    # Configurações otimizadas para o cliente HTTP - com limites mais razoáveis
    conn = aiohttp.TCPConnector(limit=concurrent_requests, ttl_dns_cache=300, force_close=True)
    timeout = aiohttp.ClientTimeout(total=30, connect=10, sock_connect=10, sock_read=10)
    
    successful_requests = 0
    failed_requests = 0
    
    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        start_time = time.time()
        response_times = []

        # Dividir as transações em lotes menores para evitar sobrecarga
        batch_size = min(500, total_transactions)
        
        for batch_start in range(0, total_transactions, batch_size):
            batch_end = min(batch_start + batch_size, total_transactions)
            print(f"Processando lote {batch_start//batch_size + 1} ({batch_end-batch_start} transações)")
            
            # Processar em mini-lotes para melhor controle
            mini_batch_size = min(concurrent_requests, 50)
            
            for mini_batch_start in range(batch_start, batch_end, mini_batch_size):
                mini_batch_end = min(mini_batch_start + mini_batch_size, batch_end)
                
                # Criar tarefas para o mini-lote
                tasks = []
                for _ in range(mini_batch_start, mini_batch_end):
                    transaction_data = {
                        "accountID": str(uuid.uuid4()),
                        "amount": 100.50,
                        "type": "credit"
                    }
                    
                    request_start = time.time()
                    task = asyncio.create_task(send_transaction(session, transaction_data))
                    tasks.append((task, request_start))
                
                # Aguardar todas as tarefas do mini-lote
                for task, req_start in tasks:
                    try:
                        result = await task
                        if result is not None:
                            successful_requests += 1
                            response_times.append(time.time() - req_start)
                        else:
                            failed_requests += 1
                    except Exception as e:
                        failed_requests += 1
                        print(f"Erro ao processar resultado: {e}")
                
                # Pausa entre mini-lotes para evitar sobrecarga
                await asyncio.sleep(0.5)
            
            # Pausa maior entre lotes principais
            print(f"Lote {batch_start//batch_size + 1} concluído. Aguardando...")
            await asyncio.sleep(2)

        total_time = time.time() - start_time
        tps = successful_requests / total_time if total_time > 0 else 0
        
        # Calcula P99 latência
        if response_times:
            sorted_times = sorted(response_times)
            p99_index = int(len(sorted_times) * 0.99)
            p99_latency = sorted_times[p99_index] * 1000 if p99_index < len(sorted_times) else 0
        else:
            p99_latency = 0

        print("\n=== Resultados do Teste de Stress ===")
        print(f"Tempo total: {total_time:.2f} segundos")
        print(f"Requisições bem-sucedidas: {successful_requests}")
        print(f"Requisições com falha: {failed_requests}")
        print(f"Transações por segundo (TPS): {tps:.2f}")
        print(f"Latência P99: {p99_latency:.2f}ms")
        
        # Verificar métricas da API
        try:
            async with session.get('http://localhost:8000/api/v1/metrics') as response:
                api_metrics = await response.json()
                print("\n=== Métricas da API ===")
                print(f"TPS registrado pela API: {api_metrics['tps']}")
                print(f"P99 Latência pela API: {api_metrics['p99_latency']}ms")
                print(f"Total de requisições: {api_metrics['total_requests']}")
        except Exception as e:
            print(f"Erro ao obter métricas: {e}")

if __name__ == "__main__":
    print("Iniciando teste de performance da API de pagamentos")
    
    # Configurações de CPU para melhor desempenho
    cpu_count = os.cpu_count()
    print(f"Número de CPUs disponíveis: {cpu_count}")
    
    # Configurações de teste otimizadas para latência
    test_configs = [
        (100, 10),     # Teste de aquecimento
        (500, 20),     # Teste com carga moderada
        (1000, 30)     # Teste com carga mais alta
        
    ]
    
    for i, (transactions, concurrency) in enumerate(test_configs):
        asyncio.run(run_stress_test(transactions, concurrency))
        if i < len(test_configs) - 1:
            print("\nAguardando 10 segundos antes do próximo teste...")
            time.sleep(10)
