package com.brq.payment.controller;

import com.brq.payment.model.Transaction;
import com.brq.payment.service.TransactionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1")
@RequiredArgsConstructor
public class TransactionController {
    private final TransactionService transactionService;

    @PostMapping("/transactions")
    public Transaction createTransaction(@RequestBody Map<String, Object> request) {
        return transactionService.createTransaction(
            (String) request.get("accountID"),
            ((Number) request.get("amount")).doubleValue(),
            (String) request.get("type")
        );
    }

    @GetMapping("/transactions/{transactionId}")
    public ResponseEntity<Map<String, Object>> getTransaction(@PathVariable String transactionId) {
        Map<String, Object> transaction = transactionService.getTransaction(transactionId);
        if (transaction == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(transaction);
    }

    @GetMapping("/metrics")
    public Map<String, Object> getMetrics() {
        return transactionService.getMetrics();
    }
}