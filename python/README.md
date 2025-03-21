# API de Pagamentos - Versão Python

API REST para processamento de transações financeiras com simulação de serviços AWS (SQS, Lambda e DynamoDB).

## 🚀 Tecnologias

- Python 3.8+
- FastAPI
- Uvicorn
- aiohttp

## 📋 Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Ambiente virtual (recomendado)

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/nettoac/desafio_brq.git
cd desafio_brq
```

2. Crie e ative o ambiente virtual:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## ⚡ Executando a API

1. Inicie o servidor:
```bash
python main.py
```

2. A API estará disponível em: `http://localhost:8000`

## 📌 Endpoints

### 1. Criar Transação
- **Endpoint:** POST `/api/v1/transactions`
- **Payload:**
```json
{
    "accountID": "uuid-da-conta",
    "amount": 100.50,
    "type": "credit"
}
```

#### Exemplo com cURL:
```bash
curl -X POST http://localhost:8000/api/v1/transactions ^
-H "Content-Type: application/json" ^
-d "{\"accountID\":\"550e8400-e29b-41d4-a716-446655440000\",\"amount\":100.50,\"type\":\"credit\"}"
```

#### Exemplo com Insomnia:
1. Crie uma nova requisição POST
2. URL: `http://localhost:8000/api/v1/transactions`
3. Body: JSON
4. Cole o payload acima

### 2. Consultar Transação
- **Endpoint:** GET `/api/v1/transactions/{transaction_id}`

#### Exemplo com cURL:
```bash
curl http://localhost:8000/api/v1/transactions/550e8400-e29b-41d4-a716-446655440000
```

#### Exemplo com Insomnia:
1. Crie uma nova requisição GET
2. URL: `http://localhost:8000/api/v1/transactions/550e8400-e29b-41d4-a716-446655440000`

### 3. Métricas da API
- **Endpoint:** GET `/api/v1/metrics`

#### Exemplo com cURL:
```bash
curl http://localhost:8000/api/v1/metrics
```

#### Exemplo com Insomnia:
1. Crie uma nova requisição GET
2. URL: `http://localhost:8000/api/v1/metrics`

## 🔬 Testes de Stress

O projeto inclui um script de teste de stress para avaliar o desempenho da API:

```bash
python stress_test.py
```

### Configurações de Teste:
- Teste de aquecimento: 100 transações com 10 requisições concorrentes
- Carga moderada: 500 transações com 20 requisições concorrentes
- Carga alta: 1000 transações com 30 requisições concorrentes

### Métricas Avaliadas:
- Tempo total de execução
- Requisições bem-sucedidas
- Requisições com falha
- Transações por segundo (TPS)
- Latência P99

## ✅ Resultados Esperados

### 1. Criação de Transação
```json
{
    "transactionID": "uuid-da-transacao",
    "status": "IN_PROCESSING"
}
```

### 2. Consulta de Transação
```json
{
    "transactionID": "uuid-da-transacao",
    "status": "PROCESSED"
}
```

### 3. Métricas
```json
{
    "tps": 150.25,
    "p99_latency": 45.5,
    "total_requests": 1000
}
```

## 📊 Monitoramento

- A API simula o processamento assíncrono usando filas (SQS)
- Transações são processadas por um Lambda simulado
- Os dados são persistidos em um DynamoDB simulado
- Métricas de performance são coletadas em tempo real

## 🚨 Tratamento de Erros

- 404: Transação não encontrada
- 500: Erro interno do servidor
- Timeout: 30 segundos para requisições
- Retry automático em caso de falhas

## 🔍 Observações

- A API utiliza armazenamento em arquivo para simular persistência
- O processamento assíncrono é simulado com delays controlados
- Recomenda-se usar um worker único em desenvolvimento
```