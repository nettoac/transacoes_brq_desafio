package com.brq.payment.model;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class Transaction {
    private String transactionID;
    private String accountID;
    private Double amount;
    private TransactionType type;
    private TransactionStatus status;
}