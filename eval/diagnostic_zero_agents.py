"""Diagnostic script: why do 88/127 repos have agent_count == 0?

Samples 15 repos from the zero-agent set (seed=42) and prints
the exact reproducible sample list used for manual inspection.

Run from the project root:
    python eval/diagnostic_zero_agents.py

Output: prints the 15 repos with their framework tag.
Does NOT scan, does NOT modify corpus.json.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

CORPUS_PATH = Path("eval/corpus.json")
SEED = 42


def main() -> None:
    corpus = json.loads(CORPUS_PATH.read_text())
    zero = [e for e in corpus if e.get("agent_count", -1) == 0]

    fw: dict[str, list] = defaultdict(list)
    for e in zero:
        fw[e["framework_tag"]].append(e)

    print(f"Zero-agent repos: {len(zero)}")
    print("Framework distribution in zero set:")
    for k, v in sorted(fw.items()):
        print(f"  {k}: {len(v)}")

    rng = random.Random(SEED)
    sample: list[dict] = []
    for k in sorted(fw.keys()):
        pool = fw[k][:]
        rng.shuffle(pool)
        sample.extend(pool[:2])

    picked = {e["full_name"] for e in sample}
    remaining = [e for e in zero if e["full_name"] not in picked]
    rng.shuffle(remaining)
    sample.extend(remaining[: 15 - len(sample)])
    sample = sample[:15]

    print(f"\nSample of {len(sample)} (seed={SEED}):")
    for i, e in enumerate(sample, 1):
        print(f"  {i:2d}. {e['full_name']} [{e['framework_tag']}]")


if __name__ == "__main__":
    main()
