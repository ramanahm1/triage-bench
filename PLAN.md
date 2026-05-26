# triage-bench — Planning Context

This file is the planning context for the project. Do not re-debate framing decisions already made below.

## Problem

In any company that runs on tickets (Jira, GitHub Issues, ServiceNow, Zendesk), new tickets arrive as free-text and must be triaged before work starts: classified (bug/feature/question), routed (which team), and prioritized (P0/P1/P2). Historically this is done by submitters picking dropdowns (often wrong), human triagers (expensive), or keyword rules engines (brittle).

LLMs are an obvious fit, and teams have started dropping Claude/GPT into the triage step. But most deployments are vibes-based: someone wrote a prompt, it looked good on 5 examples, they shipped it. Nobody measures real accuracy, nobody catches regressions when prompts are tweaked.

That's the gap. This project builds the missing measurement layer: a lightweight eval harness for LLM ticket triage, with automated prompt optimization (APO) as a follow-on once measurement exists.

## What we're building

A small repo that answers one question repeatedly: "How good is this prompt at classifying tickets?"

Four pieces:
1. A labeled dataset (NLBSE issue classification, or k8s GitHub issues as fallback)
2. A baseline prompt (deliberately crude — this is the floor)
3. An async runner that calls Claude Haiku on each example and logs predictions
4. A scorer producing a markdown report: accuracy, per-class precision/recall/F1, confusion matrix, total cost, p50/p95 latency

Then: one prompt iteration (few-shot v2), a delta tracker (run-over-run score deltas, per-category), and one DSPy MIPROv2 optimization run.

## 5-Block plan

- **Block 1:** Repo setup, deps (uv), dataset download (NLBSE or k8s issues), `prompts/baseline_v1.txt` written.
- **Block 2:** Async runner hitting Claude Haiku on 200 examples, saves `runs/run_001.json` with predictions + ground truth + tokens + latency + prompt version + model + timestamp.
- **Block 3:** Scorer reads run file, emits markdown report to `runs/run_001_report.md`. **This is the "if I stop here I have a real artifact" checkpoint — commit everything.**
- **Block 4:** Write `baseline_v2.txt` (one improvement, recommend few-shot examples). Run it. Build `compare_runs.py` that diffs two run files and flags any category that moved by more than ±3%.
- **Block 5:** DSPy MIPROv2 wired to the eval, one optimization run. Write `FINDINGS.md` with: baseline number, final number, top 3 things that moved the score, top 3 that didn't.

If we fall behind at Block 3, cut APO. The baseline + iteration is the core artifact; APO is a good-to-have add-on.

## Constraints / guardrails

- Keep scripts minimal (50-line scripts), not frameworks. Resist over-engineering the runner.
- Use `uv` for dependency management.
- Commit after each hour.
- Folder structure: `data/`, `prompts/`, `runs/`, `src/`.
- Model: Claude Haiku (cheap, fast) for the runner.
- Start with 200 test examples, not the full set - keep iteration fast.
- Async/batched calls so 200 examples take ~1 minute, and not 15.

## Dataset decision

Primary: NLBSE issue classification dataset (SDLC-native, pre-split, has published benchmark numbers to compare against).
Fallback if NLBSE has access friction: scrape ~1,000 labeled issues from `kubernetes/kubernetes` via the GitHub API, classify by `kind/bug` vs `kind/feature` vs `kind/support`.
Do not spend more than 15 minutes on dataset acquisition. If NLBSE blocks for any reason, switch to k8s immediately (always check with user while attempting to, prioritize their opinion).

## Out of scope for v1

- Multi-label classification (start single-label)
- Routing and priority (start with classification only; add later)
- Fine-tuning (this is a prompting harness, not a training harness)
- Fancy logging/retry frameworks