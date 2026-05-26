"""DSPy MIPROv2 optimization for ticket triage classifier."""
import csv, json, os, random, sys
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path

import dspy
from dspy.teleprompt import MIPROv2
from dotenv import load_dotenv

load_dotenv()

# IDs already used as few-shot examples in baseline_v2 — exclude from trainset
EXCLUDED_IDS = {
    "microsoft/vscode_2023-09-28 20:31:47",
    "opencv/opencv_2023-03-26 07:31:09",
    "opencv/opencv_2022-02-02 14:39:36",
    "opencv/opencv_2022-05-16 03:05:42",
}


def load_trainset(n_per_class=(34, 33, 33), seed=42):
    csv.field_size_limit(sys.maxsize)
    with open("data/issues_train.csv", "rb") as f:
        raw = f.read().replace(b"\x00", b"")
    rows = list(csv.DictReader(StringIO(raw.decode("utf-8", errors="replace"))))
    rows = [r for r in rows if f"{r['repo']}_{r['created_at']}" not in EXCLUDED_IDS]

    by_label = defaultdict(list)
    for r in rows:
        by_label[r["label"]].append(r)

    random.seed(seed)
    sample = []
    for label, n in zip(["bug", "feature", "question"], n_per_class):
        sample.extend(random.sample(by_label[label], n))
    random.shuffle(sample)

    return [
        dspy.Example(
            title=r["title"].strip(),
            body=r["body"].strip()[:1000],
            label=r["label"],
        ).with_inputs("title", "body")
        for r in sample
    ]


class TicketClassifier(dspy.Signature):
    """Classify a GitHub issue as bug, feature, or question."""

    title: str = dspy.InputField(desc="issue title")
    body: str = dspy.InputField(desc="issue body (may be truncated to 1000 chars)")
    label: str = dspy.OutputField(desc="exactly one of: bug, feature, question")


class Triage(dspy.Module):
    def __init__(self):
        self.classify = dspy.Predict(TicketClassifier)

    def forward(self, title, body):
        return self.classify(title=title, body=body)


def metric(example, pred, trace=None):
    return example.label.lower().strip() == pred.label.lower().strip()


def extract_prompt(optimized: Triage) -> str:
    """Render the optimized DSPy program as a plain-text prompt for runner.py."""
    sig   = optimized.classify.signature
    instr = sig.instructions.strip()
    demos = getattr(optimized.classify, "demos", []) or []

    lines = [instr, ""]
    if demos:
        lines.append("Examples:\n")
        for d in demos:
            lines.append(f"Title: {getattr(d, 'title', '').strip()}")
            lines.append(f"Body: {str(getattr(d, 'body', '')).strip()[:400]}")
            lines.append(f"Label: {getattr(d, 'label', '').strip()}")
            lines.append("")

    lines += [
        "Now classify:\n",
        "Title: {title}",
        "Body: {body}",
        "",
        "Respond with only the single word label (bug, feature, or question). "
        "No punctuation, no explanation.",
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    task_lm   = dspy.LM("anthropic/claude-haiku-4-5-20251001", max_tokens=256)
    prompt_lm = dspy.LM("anthropic/claude-haiku-4-5-20251001", max_tokens=1024)
    dspy.configure(lm=task_lm)

    trainset = load_trainset()
    print(f"Trainset: {len(trainset)} | {Counter(e.label for e in trainset)}\n")

    teleprompter = MIPROv2(
        metric=metric,
        prompt_model=prompt_lm,
        task_model=task_lm,
        auto="light",
        num_threads=3,   # stay under 50 RPM; minibatch_size=35 keeps burst low
        verbose=True,
    )

    optimized = teleprompter.compile(
        Triage(),
        trainset=trainset,
        requires_permission_to_run=False,
    )

    # Persist full program (for reproducibility)
    Path("runs/optimized_program.json").write_text(
        json.dumps(optimized.dump_state(), indent=2)
    )

    # Extract and save human-readable prompt
    prompt_text = extract_prompt(optimized)
    Path("prompts/baseline_v3_apo.txt").write_text(prompt_text)

    print("\n--- Optimized instruction ---")
    print(optimized.classify.signature.instructions)
    print(f"\nDemos selected: {len(getattr(optimized.classify, 'demos', []) or [])}")
    print("Saved: prompts/baseline_v3_apo.txt  runs/optimized_program.json")
