"""Async runner: classifies test.jsonl examples and writes a run JSON file."""
import argparse, asyncio, json, time
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from tqdm.asyncio import tqdm

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"
CONCURRENCY = 3   # limited by 50 RPM org rate limit
RATE_DELAY = 1.5  # seconds between requests per worker (~45 RPM)


async def classify(client: anthropic.AsyncAnthropic, prompt_tpl: str, example: dict) -> dict:
    text = prompt_tpl.replace("{title}", example["title"]).replace("{body}", example["body"])
    t0 = time.monotonic()
    try:
        msg = await client.messages.create(
            model=MODEL,
            max_tokens=10,
            messages=[{"role": "user", "content": text}],
        )
        latency = time.monotonic() - t0
        prediction = msg.content[0].text.strip().lower()
        error = None
        input_tokens = msg.usage.input_tokens
        output_tokens = msg.usage.output_tokens
    except Exception as e:
        latency = time.monotonic() - t0
        prediction = "error"
        error = str(e)
        input_tokens = output_tokens = 0
    return {
        "id": example["id"],
        "label": example["label"],
        "prediction": prediction,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_s": round(latency, 3),
        "error": error,
    }


async def run(prompt_path: Path, data_path: Path, out_path: Path) -> None:
    prompt_tpl = prompt_path.read_text()
    examples = [json.loads(l) for l in data_path.read_text().splitlines() if l.strip()]

    client = anthropic.AsyncAnthropic()
    sem = asyncio.Semaphore(CONCURRENCY)

    async def bounded(ex):
        async with sem:
            await asyncio.sleep(RATE_DELAY)
            return await classify(client, prompt_tpl, ex)

    tasks = [bounded(ex) for ex in examples]
    results = await tqdm.gather(*tasks, desc="Classifying")

    out = {
        "meta": {
            "model": MODEL,
            "prompt_version": prompt_path.stem,
            "prompt_path": str(prompt_path),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "n": len(results),
        },
        "results": results,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {len(results)} results to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", default="prompts/baseline_v1.txt")
    parser.add_argument("--data",   default="data/test.jsonl")
    parser.add_argument("--out",    default="runs/run_001.json")
    args = parser.parse_args()
    asyncio.run(run(Path(args.prompt), Path(args.data), Path(args.out)))
