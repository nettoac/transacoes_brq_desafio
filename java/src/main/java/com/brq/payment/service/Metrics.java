package com.brq.payment.service;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.concurrent.atomic.AtomicLong;

public class Metrics {
    private final long startTime;
    private final AtomicLong totalRequests;
    private final List<Long> latencies;

    public Metrics() {
        this.startTime = System.currentTimeMillis();
        this.totalRequests = new AtomicLong(0);
        this.latencies = Collections.synchronizedList(new ArrayList<>());
    }

    public void incrementRequests() {
        totalRequests.incrementAndGet();
    }

    public void addLatency(long latency) {
        latencies.add(latency);
    }

    public Map<String, Object> getMetrics() {
        if (latencies.isEmpty()) {
            return Map.of(
                "tps", 0.0,
                "p99_latency", 0.0,
                "total_requests", 0L
            );
        }

        long totalTime = System.currentTimeMillis() - startTime;
        double tps = totalRequests.get() / (totalTime / 1000.0);

        List<Long> sortedLatencies = new ArrayList<>(latencies);
        Collections.sort(sortedLatencies);
        int p99Index = (int) (sortedLatencies.size() * 0.99);
        double p99Latency = sortedLatencies.get(p99Index);

        return Map.of(
            "tps", Math.round(tps * 100.0) / 100.0,
            "p99_latency", Math.round(p99Latency * 100.0) / 100.0,
            "total_requests", totalRequests.get()
        );
    }
}