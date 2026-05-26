# triage-bench

A lightweight eval harness for measuring LLM performance on GitHub issue triage. Answers a single question run after run: "given this prompt and this model, how accurately are GitHub issues being classified?". Each run produces a comparable accuracy score, so prompt changes can be measured, reducing guess work. 

Includes:
- async runner
- markdown-report scorer
- automated prompt optimization via DSPy MIPROv2

Built to address the measurement gap in LLM triage deployments - where teams ship prompts based on guesses, with no accuracy tracking and no way to detect when a change makes things worse.

## Dataset

[NLBSE 2024 Issue Report Classification](https://github.com/nlbse2024/issue-report-classification) - 1,500 labeled GitHub issues (bug / feature / question), pre-split with published benchmark numbers. We use a stratified 200 example sample from the test split (67 bug / 67 feature / 66 question).

## Folder structure

```
data/       raw dataset + sampled test.jsonl
prompts/    prompt templates (baseline_v1.txt, etc.)
runs/       runner output (JSON) and scorer reports (markdown)
src/        runner, scorer, and comparison scripts
```

## Setup

```bash
uv sync
cp .env.example .env   # include ANTHROPIC_API_KEY
```

## How to run
```
git clone https://github.com/ramanahm1/triage-bench.git
cd triage-bench
uv sync
export ANTHROPIC_API_KEY=sk-ant-...
uv run python src/runner.py --prompt prompts/baseline_v2.txt --data data/test.jsonl --out runs/<user_name>.json
uv run python src/scorer.py --run runs/<user_name>_001.json
uv run python src/compare_runs.py --baseline runs/run_002.json --candidate runs/<user_name>_001.json
```

Requires `ANTHROPIC_API_KEY` in the environment (or `.env` file).