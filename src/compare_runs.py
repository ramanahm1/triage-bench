"""Compare two run files and surface accuracy + per-class deltas."""
import argparse, json
from pathlib import Path

LABELS = ["bug", "feature", "question"]
FLAG_THRESHOLD = 0.03  # flag if any class metric moves by more than ±3%


def prf(results, label):
    tp = sum(r["label"] == label and r["prediction"] == label for r in results)
    fp = sum(r["label"] != label and r["prediction"] == label for r in results)
    fn = sum(r["label"] == label and r["prediction"] != label for r in results)
    p  = tp / (tp + fp) if (tp + fp) else 0.0
    r  = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f1


def load(path):
    data    = json.loads(Path(path).read_text())
    results = [r for r in data["results"] if r["prediction"] != "error"]
    acc     = sum(r["label"] == r["prediction"] for r in results) / len(results)
    metrics = {label: prf(results, label) for label in LABELS}
    return data["meta"], acc, metrics


def fmt(delta):
    sign = "+" if delta >= 0 else ""
    return f"{sign}{delta*100:.1f}pp"


def flag(delta):
    return " *** FLAGGED" if abs(delta) > FLAG_THRESHOLD else ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--baseline",  required=True)
    parser.add_argument("--candidate", required=True)
    args = parser.parse_args()

    b_meta, b_acc, b_metrics = load(args.baseline)
    c_meta, c_acc, c_metrics = load(args.candidate)

    print(f"\n{'='*56}")
    print(f"  baseline:  {b_meta['prompt_version']}  ({args.baseline})")
    print(f"  candidate: {c_meta['prompt_version']}  ({args.candidate})")
    print(f"{'='*56}\n")

    acc_delta = c_acc - b_acc
    print(f"Overall accuracy:  {b_acc:.1%} -> {c_acc:.1%}  ({fmt(acc_delta)}){flag(acc_delta)}\n")

    header = f"{'Class':<10}  {'Metric':<10}  {'Baseline':>9}  {'Candidate':>10}  {'Delta':>8}"
    print(header)
    print("-" * len(header))
    for label in LABELS:
        for i, metric in enumerate(["precision", "recall", "F1"]):
            b_val = b_metrics[label][i]
            c_val = c_metrics[label][i]
            delta = c_val - b_val
            print(f"{label:<10}  {metric:<10}  {b_val:>9.3f}  {c_val:>10.3f}  {fmt(delta):>8}{flag(delta)}")
        print()


if __name__ == "__main__":
    main()
