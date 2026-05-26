# Triage-Bench Run Report

| Field | Value |
|-------|-------|
| Run file | `runs/run_001.json` |
| Model | `claude-haiku-4-5-20251001` |
| Prompt | `baseline_v1` |
| Timestamp | 2026-05-26T11:11:55.461164+00:00 |
| Examples | 200 (1 errors excluded from metrics) |

## Overall Accuracy

**140/199 = 70.4%**

## Per-Class Metrics

| Class | Precision | Recall | F1 | Support |
|-------|-----------|--------|----|---------|
| bug | 0.600 | 0.985 | 0.746 | 67 |
| feature | 0.889 | 0.836 | 0.862 | 67 |
| question | 0.692 | 0.277 | 0.396 | 65 |

## Confusion Matrix

Rows = actual, Columns = predicted.

| actual \ predicted | bug | feature | question |
|---|---|---|---|
| bug | 66 | 0 | 1 |
| feature | 4 | 56 | 7 |
| question | 40 | 7 | 18 |

## Cost & Latency

| Metric | Value |
|--------|-------|
| Input tokens | 62,062 |
| Output tokens | 796 |
| Estimated cost | $0.0660 |
| Pricing basis | $1.00 / $5.00 per 1M input/output tokens (Haiku 4.5) |
| Latency p50 | 0.844s |
| Latency p95 | 3.370s |
| Errors | 1 |
