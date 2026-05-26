# triage-bench Findings

## Results

| Run | Prompt | Accuracy | Question F1 |
|-----|--------|----------|-------------|
| run_001 | baseline_v1 (zero-shot) | 70.4% | 0.396 |
| run_002 | baseline_v2 (definitions + few-shots) | 75.0% | 0.671 |
| run_003 | baseline_v3 (MIPROv2 optimized) | 71.0% | 0.485 |

Model: `claude-haiku-4-5-20251001`. Test set: 200 stratified NLBSE examples.

## Key finding 

The handwritten v2 prompt outperformed both the zero-shot baseline and MIPROv2's optimized v3. The harness caught the v3 drop — without it, v3 would have looked like a reasonable next step (longer, more structured, optimizer-generated) and shipped silently. The value of this project is the measurement layer, not the v2 prompt.

## What worked

**The bug/question boundary was the whole game.** v1 defaulted to `bug` under uncertainty - 40 of 66 questions were mislabeled as bugs. v2 fixed this with an explicit rule (technical content ≠ bug) plus two hard few-shot examples (bug-shaped titles labeled `question`). Question recall jumped from 0.28 to 0.73, driving the entire +4.6pp overall gain.

**Few-shots are load-bearing, not decorative.** When MIPROv2 dropped them in v3, question recall collapsed back to 0.38. A more elaborate instruction couldn't substitute for concrete examples on the hard boundary.

**`feature` was stable across all three runs** (F1 0.83 - 0.86). The entire precision-recall tradeoff lives between `bug` and `question`.

## What didn't work

**APO instruction elaboration.** MIPROv2's 250-word structured instruction explicitly listed "error messages or stack traces" as a positive `bug` signal - re-introducing the exact bias v2 was designed to suppress. More words ≠ better signal.

**MIPROv2's zero-demo choice.** Dropping few-shots was the single most consequential decision in v3, and it hurt. This may partly reflect optimization noise: ~10 rate-limit errors during DSPy's eval loop and a train distribution (34/33/33) that didn't match the test set (67/67/66).

## What APO did surface

One non-obvious meta-rule worth keeping: *"the patterns of these categories are consistent across frameworks and domains"* — a hint that the model should ignore domain vocabulary and focus on linguistic structure. v2 implied this; v3 made it explicit. The rule is useful; the configuration that produced it wasn't.

## Next

1. **Hybrid v4:** v2's prompt + APO's domain-agnostic meta-rule
2. **Fairer APO run:** open question whether v3 measured MIPROv2's ceiling or its defaults — re-run with rate-limit noise eliminated and `max_labeled_demos=4`
3. **Routing as a second label:** the harness is reusable