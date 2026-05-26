# Triage-Bench Run Report

| Field | Value |
|-------|-------|
| Run file | `runs/run_003.json` |
| Model | `claude-haiku-4-5-20251001` |
| Prompt | `baseline_v3_apo` |
| Timestamp | 2026-05-26T15:43:38.255982+00:00 |
| Examples | 200 (0 errors excluded from metrics) |

## Overall Accuracy

**142/200 = 71.0%**

## Per-Class Metrics

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| bug | 0.615 | 0.955 | 0.749 | 67 |
| feature | 0.898 | 0.791 | 0.841 | 67 |
| question | 0.676 | 0.379 | 0.485 | 66 |

## Confusion Matrix

Rows = actual, Columns = predicted.

| actual \ predicted | bug | feature | question |
|---|---|---|---|
| bug | 64 | 0 | 3 |
| feature | 5 | 53 | 9 |
| question | 35 | 6 | 25 |

## Cost & Latency

| Metric | Value |
|--------|-------|
| Input tokens | 123,369 |
| Output tokens | 800 |
| Estimated cost | $0.1274 |
| Pricing basis | $1.00 / $5.00 per 1M input/output tokens (Haiku 4.5) |
| Latency p50 | 1.857s |
| Latency p95 | 3.419s |
| Errors | 0 |
