package com.brq.payment;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

public class StressTest {
    // URL base da API de pagamentos
    private static final String BASE_URL = "http://localhost:8080/api/v1";
    
    // Configuração do cliente HTTP com timeout de 10 segundos
    private static final HttpClient client = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    public static void main(String[] args) throws Exception {
        System.out.println("Iniciando teste de stress da API de Pagamentos");
        System.out.println("============================================");
        
        // Configurações dos testes com diferentes cargas
        int[][] testConfigs = {
            {100, 10},  // Teste de aquecimento
            {500, 20},  // Carga moderada
            {1000, 30}  // Carga alta
        };

        for (int i = 0; i < testConfigs.length; i++) {
            runStressTest(testConfigs[i][0], testConfigs[i][1]);
            
            // Adiciona pausa somente se não for o último teste
            if (i < testConfigs.length - 1) {
                System.out.println("\nAguardando 10 segundos antes do próximo teste...");
                Thread.sleep(10000);
            }
        }
    }

    private static void runStressTest(int totalTransactions, int concurrentRequests) throws Exception {
        System.out.printf("\nIniciando teste com %d transações e %d requisições concorrentes\n", 
            totalTransactions, concurrentRequests);
        System.out.println("----------------------------------------------------");

        // Verificar disponibilidade do servidor
        if (!checkServerAvailability()) {
            System.out.println("\n⚠️ ERRO: Servidor não está disponível em " + BASE_URL);
            System.out.println("Por favor, verifique se o servidor está em execução.");
            System.out.println("Comando para iniciar o servidor: mvn spring-boot:run");
            return;
        }

        System.out.println("✅ Servidor disponível, iniciando testes...\n");

        ExecutorService executor = Executors.newFixedThreadPool(concurrentRequests);
        List<CompletableFuture<Boolean>> futures = new ArrayList<>();
        long startTime = System.currentTimeMillis();
        List<Long> responseTimes = new ArrayList<>();
        int successfulRequests = 0;
        int failedRequests = 0;

        // Processamento em lotes para melhor controle
        int batchSize = Math.min(500, totalTransactions);
        for (int i = 0; i < totalTransactions; i += batchSize) {
            int currentBatchSize = Math.min(batchSize, totalTransactions - i);
            System.out.printf("Processando lote %d (%d transações)\n", (i/batchSize + 1), currentBatchSize);

            for (int j = 0; j < currentBatchSize; j++) {
                CompletableFuture<Boolean> future = CompletableFuture.supplyAsync(() -> {
                    try {
                        long requestStart = System.currentTimeMillis();
                        boolean success = sendTransaction();
                        responseTimes.add(System.currentTimeMillis() - requestStart);
                        return success;
                    } catch (Exception e) {
                        System.out.println("Erro na requisição: " + e.getMessage());
                        return false;
                    }
                }, executor);
                futures.add(future);
            }

            // Aguarda conclusão do lote
            CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();
            
            // Contabiliza resultados
            for (CompletableFuture<Boolean> future : futures) {
                if (future.get()) successfulRequests++;
                else failedRequests++;
            }
            futures.clear();
            
            System.out.println("Lote processado. Pausa de 500ms para controle de carga...");
            Thread.sleep(500);
        }

        executor.shutdown();
        executor.awaitTermination(1, TimeUnit.MINUTES);

        // Cálculo das métricas
        long totalTime = System.currentTimeMillis() - startTime;
        double tps = successfulRequests / (totalTime / 1000.0);
        responseTimes.sort(null);
        double p99Latency = responseTimes.get((int)(responseTimes.size() * 0.99));

        // Impressão dos resultados
        System.out.println("\n=== Resultados do Teste de Stress ===");
        System.out.printf("Tempo total: %.2f segundos\n", totalTime/1000.0);
        System.out.printf("Requisições bem-sucedidas: %d\n", successfulRequests);
        System.out.printf("Requisições com falha: %d\n", failedRequests);
        System.out.printf("Transações por segundo (TPS): %.2f\n", tps);
        System.out.printf("Latência P99: %.2f ms\n", p99Latency);

        // Obtém métricas da API
        printApiMetrics();
    }

    private static boolean sendTransaction() throws Exception {
        String json = String.format("""
            {"accountID":"%s","amount":100.50,"type":"credit"}
            """, UUID.randomUUID());

        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(BASE_URL + "/transactions"))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString(json))
            .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.statusCode() == 200;
    }

    private static boolean checkServerAvailability() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/metrics"))
                .GET()
                .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            return response.statusCode() == 200;
        } catch (Exception e) {
            System.out.println("Erro ao verificar disponibilidade: " + e.getMessage());
            return false;
        }
    }

    private static void printApiMetrics() {
        try {
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/metrics"))
                .GET()
                .build();

            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            System.out.println("\n=== Métricas da API ===");
            System.out.println(response.body());
        } catch (Exception e) {
            System.out.println("Falha ao obter métricas da API: " + e.getMessage());
        }
    }
}