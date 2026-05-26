# Triage-Bench Run Report

| Field | Value |
|-------|-------|
| Run file | `runs/run_002.json` |
| Model | `claude-haiku-4-5-20251001` |
| Prompt | `baseline_v2` |
| Timestamp | 2026-05-26T12:44:32.413154+00:00 |
| Examples | 200 (0 errors excluded from metrics) |

## Overall Accuracy

**150/200 = 75.0%**

## Per-Class Metrics

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| bug | 0.778 | 0.731 | 0.754 | 67 |
| feature | 0.883 | 0.791 | 0.835 | 67 |
| question | 0.623 | 0.727 | 0.671 | 66 |

## Confusion Matrix

Rows = actual, Columns = predicted.

| actual \ predicted | bug | feature | question |
|---|---|---|---|
| bug | 49 | 1 | 17 |
| feature | 2 | 53 | 12 |
| question | 12 | 6 | 48 |

## Cost & Latency

| Metric | Value |
|--------|-------|
| Input tokens | 191,569 |
| Output tokens | 800 |
| Estimated cost | $0.1956 |
| Pricing basis | $1.00 / $5.00 per 1M input/output tokens (Haiku 4.5) |
| Latency p50 | 0.845s |
| Latency p95 | 3.188s |
| Errors | 0 |
