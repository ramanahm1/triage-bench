"""Scorer: reads a run JSON and writes a markdown report."""
import argparse, json
from collections import Counter, defaultdict
from pathlib import Path

HAIKU_INPUT_COST  = 1.00 / 1_000_000  # $ per token
HAIKU_OUTPUT_COST = 5.00 / 1_000_000
LABELS = ["bug", "feature", "question"]


def prf(results, label):
    tp = sum(r["label"] == label and r["prediction"] == label for r in results)
    fp = sum(r["label"] != label and r["prediction"] == label for r in results)
    fn = sum(r["label"] == label and r["prediction"] != label for r in results)
    p  = tp / (tp + fp) if (tp + fp) else 0.0
    r  = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f1


def render(run_path: Path, out_path: Path) -> None:
    data     = json.loads(run_path.read_text())
    meta     = data["meta"]
    all_res  = data["results"]
    results  = [r for r in all_res if r["prediction"] != "error"]
    errors   = len(all_res) - len(results)
    correct  = sum(r["label"] == r["prediction"] for r in results)
    accuracy = correct / len(results) if results else 0.0

    # confusion matrix: matrix[actual][predicted]
    matrix = defaultdict(Counter)
    for r in results:
        matrix[r["label"]][r["prediction"]] += 1

    # cost + latency
    total_in  = sum(r["input_tokens"] for r in all_res)
    total_out = sum(r["output_tokens"] for r in all_res)
    cost      = total_in * HAIKU_INPUT_COST + total_out * HAIKU_OUTPUT_COST
    lats      = sorted(r["latency_s"] for r in all_res)
    p50, p95  = lats[len(lats) // 2], lats[int(len(lats) * 0.95)]

    lines = [
        "# Triage-Bench Run Report", "",
        "| Field | Value |",
        "|-------|-------|",
        f"| Run file | `{run_path}` |",
        f"| Model | `{meta['model']}` |",
        f"| Prompt | `{meta['prompt_version']}` |",
        f"| Timestamp | {meta['timestamp']} |",
        f"| Examples | {len(all_res)} ({errors} errors excluded from metrics) |",
        "",
        "## Overall Accuracy", "",
        f"**{correct}/{len(results)} = {accuracy:.1%}**",
        "",
        "## Per-Class Metrics", "",
        "| Class | Precision | Recall | F1 | Support |",
        "|-------|-----------|--------|----|---------|",
    ]
    for label in LABELS:
        p, r, f1 = prf(results, label)
        support  = sum(1 for x in results if x["label"] == label)
        lines.append(f"| {label} | {p:.3f} | {r:.3f} | {f1:.3f} | {support} |")

    pred_header = " | ".join(LABELS)
    lines += [
        "",
        "## Confusion Matrix", "",
        "Rows = actual, Columns = predicted.", "",
        f"| actual \\ predicted | {pred_header} |",
        "|---|" + "---|" * len(LABELS),
    ]
    for actual in LABELS:
        cells = " | ".join(str(matrix[actual][pred]) for pred in LABELS)
        lines.append(f"| {actual} | {cells} |")

    lines += [
        "",
        "## Cost & Latency", "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Input tokens | {total_in:,} |",
        f"| Output tokens | {total_out:,} |",
        f"| Estimated cost | ${cost:.4f} |",
        f"| Pricing basis | $1.00 / $5.00 per 1M input/output tokens (Haiku 4.5) |",
        f"| Latency p50 | {p50:.3f}s |",
        f"| Latency p95 | {p95:.3f}s |",
        f"| Errors | {errors} |",
    ]

    out_path.write_text("\n".join(lines) + "\n")
    print(f"Report written to {out_path}")
    print(f"Accuracy: {correct}/{len(results)} = {accuracy:.1%}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run", default="runs/run_001.json")
    parser.add_argument("--out", default=None, help="defaults to <run_stem>_report.md")
    args     = parser.parse_args()
    run_path = Path(args.run)
    out_path = Path(args.out) if args.out else run_path.with_name(run_path.stem + "_report.md")
    render(run_path, out_path)
