# API de Pagamentos - Versão Java

API REST para processamento de transações financeiras com simulação de serviços AWS (SQS, Lambda e DynamoDB) implementada em Java.

## 🚀 Tecnologias

- Java 17
- Spring Boot 2.7.0
- Maven
- Java HTTP Client
- Lombok

## 📋 Pré-requisitos

### Java Development Kit (JDK)
1. Baixe o JDK 17 em: https://adoptium.net/temurin/releases/?version=17
2. Execute o instalador
3. Configure a variável de ambiente JAVA_HOME:
   - Abra as Variáveis de Ambiente do Sistema
   - Crie nova variável de sistema:
     - Nome: `JAVA_HOME`
     - Valor: `C:\Program Files\Eclipse Adoptium\jdk-17.x.x.x-hotspot` (ajuste o caminho conforme sua instalação)
   - Adicione `%JAVA_HOME%\bin` ao Path do sistema

### Apache Maven
1. Baixe o Maven em: https://maven.apache.org/download.cgi (apache-maven-3.9.x-bin.zip)
2. Extraia para `C:\Program Files\Apache\maven`
3. Configure as variáveis de ambiente:
   - Crie nova variável de sistema:
     - Nome: `M2_HOME`
     - Valor: `C:\Program Files\Apache\maven`
   - Adicione `%M2_HOME%\bin` ao Path do sistema

4. Verifique a instalação:
```bash
mvn -version
```

## 🔧 Instalação

1. Clone o repositório:
```bash
git clone https://github.com/nettoac/desafio_brq.git
cd desafio_brq/java
```

2. Instale as dependências:
```bash
mvn clean install
```

## ⚡ Executando a API

1. Inicie o servidor:
```bash
mvn spring-boot:run
```

2. A API estará disponível em: `http://localhost:8080/api/v1`

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

### 2. Consultar Transação
- **Endpoint:** GET `/api/v1/transactions/{transaction_id}`

### 3. Métricas da API
- **Endpoint:** GET `/api/v1/metrics`

## 🔬 Testes de Stress

O projeto inclui um script de teste de stress para avaliar o desempenho da API:

1. Em um terminal separado (mantenha o servidor rodando), execute:
```bash
mvn compile exec:java -Dexec.mainClass="com.brq.payment.StressTest"
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

## 📊 Monitoramento

- Processamento assíncrono simulado com CompletableFuture
- Métricas de performance coletadas em tempo real
- Controle de concorrência com ExecutorService
- Processamento em lotes para melhor performance

## 🚨 Tratamento de Erros

- 404: Transação não encontrada
- 500: Erro interno do servidor
- Timeout: 10 segundos para requisições
- Retry automático em caso de falhas

## 🔍 Observações

- A API utiliza armazenamento em memória para simular persistência
- O processamento assíncrono é simulado com delays controlados
- Recomenda-se usar um worker único em desenvolvimento
```