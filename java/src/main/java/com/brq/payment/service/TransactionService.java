package com.brq.payment.service;

import com.brq.payment.model.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CompletableFuture;
import java.util.ArrayList;
import java.util.List;
import java.time.Instant;

@Slf4j
@Service
public class TransactionService {
    private final Map<String, Transaction> transactionsTable = new ConcurrentHashMap<>();
    private final Map<String, Map<String, Object>> transactionsStatusTable = new ConcurrentHashMap<>();
    private final List<String> sqsQueue = new ArrayList<>();
    private final Metrics metrics = new Metrics();

    public Transaction createTransaction(String accountId, Double amount, String type) {
        long startTime = System.currentTimeMillis();

        Transaction transaction = Transaction.builder()
                .transactionID(UUID.randomUUID().toString())
                .accountID(accountId)
                .amount(amount)
                .type(TransactionType.valueOf(type.toUpperCase()))
                .status(TransactionStatus.IN_PROCESSING)
                .build();

        transactionsTable.put(transaction.getTransactionID(), transaction);
        sendToSqs(transaction);
        processTransaction(transaction.getTransactionID());

        metrics.addLatency(System.currentTimeMillis() - startTime);
        metrics.incrementRequests();

        return transaction;
    }

    @Async
    public CompletableFuture<Void> sendToSqs(Transaction transaction) {
        log.info("[SQS] Sending transaction {} to queue", transaction.getTransactionID());
        sqsQueue.add(transaction.getTransactionID());
        try {
            Thread.sleep(5);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        log.info("[SQS] Transaction {} queued successfully", transaction.getTransactionID());
        return CompletableFuture.completedFuture(null);
    }

    @Async
    public void processTransaction(String transactionId) {
        log.info("[Lambda] Processing transaction {}", transactionId);
        try {
            Thread.sleep(10);
            if (transactionsTable.containsKey(transactionId)) {
                Map<String, Object> status = new ConcurrentHashMap<>();
                status.put("transactionID", transactionId);
                status.put("status", TransactionStatus.PROCESSED);
                status.put("processed_at", Instant.now().toEpochMilli());
                transactionsStatusTable.put(transactionId, status);
                log.info("[Lambda] Transaction {} processed successfully", transactionId);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public Map<String, Object> getTransaction(String transactionId) {
        long startTime = System.currentTimeMillis();
        
        Map<String, Object> result = transactionsStatusTable.get(transactionId);
        if (result == null && transactionsTable.containsKey(transactionId)) {
            Transaction transaction = transactionsTable.get(transactionId);
            result = Map.of(
                "transactionID", transaction.getTransactionID(),
                "status", transaction.getStatus()
            );
        }

        metrics.addLatency(System.currentTimeMillis() - startTime);
        return result;
    }

    public Map<String, Object> getMetrics() {
        return metrics.getMetrics();
    }
}