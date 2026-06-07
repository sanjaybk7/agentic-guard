"""Step 2 — Clone corpus repos at pinned SHAs.

Reads eval/corpus.json and clones each repo into eval/repos/<owner>/<name>/
at the exact pinned commit SHA. Verifies each checkout HEAD matches the
recorded SHA; reports any mismatches.

Run from the project root:
    python eval/clone_corpus.py [--workers N]

Uses shallow clones (--depth 1) per-repo then checks out the pinned SHA.
If the pinned SHA isn't in the shallow history, falls back to a full clone.

Output:
  eval/clone_report.json — per-repo clone status {full_name, sha, status, error}
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

CORPUS_PATH = Path(__file__).parent / "corpus.json"
REPOS_DIR = Path(__file__).parent / "repos"
REPORT_PATH = Path(__file__).parent / "clone_report.json"


def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=cwd
    )
    return result.returncode, (result.stdout + result.stderr).strip()


def clone_repo(entry: dict) -> dict:
    full_name: str = entry["full_name"]
    clone_url: str = entry["clone_url"]
    branch: str = entry["default_branch"]
    pinned_sha: str = entry["sha"]

    dest = REPOS_DIR / full_name
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists():
        # Already present — verify HEAD matches
        rc, actual_sha = _run(["git", "rev-parse", "HEAD"], cwd=dest)
        actual_sha = actual_sha.strip()
        if rc == 0 and actual_sha == pinned_sha:
            return {"full_name": full_name, "sha": pinned_sha,
                    "status": "already_correct", "error": None}
        # Present but wrong SHA — re-checkout
        rc2, _ = _run(["git", "checkout", pinned_sha], cwd=dest)
        if rc2 == 0:
            return {"full_name": full_name, "sha": pinned_sha,
                    "status": "rechecked", "error": None}
        return {"full_name": full_name, "sha": pinned_sha,
                "status": "error", "error": f"re-checkout failed; head was {actual_sha}"}

    # Shallow clone of the default branch
    rc, out = _run([
        "git", "clone", "--depth", "1",
        "--branch", branch,
        clone_url, str(dest),
    ])
    if rc != 0:
        return {"full_name": full_name, "sha": pinned_sha,
                "status": "error", "error": f"clone failed: {out[:300]}"}

    # Check if pinned SHA is already checked out (shallow clone gets branch tip)
    rc2, actual_sha = _run(["git", "rev-parse", "HEAD"], cwd=dest)
    actual_sha = actual_sha.strip()
    if actual_sha == pinned_sha:
        return {"full_name": full_name, "sha": pinned_sha,
                "status": "ok", "error": None}

    # Pinned SHA differs from branch tip — deepen and checkout
    _run(["git", "fetch", "--unshallow"], cwd=dest)
    rc3, _ = _run(["git", "checkout", pinned_sha], cwd=dest)
    if rc3 != 0:
        return {"full_name": full_name, "sha": pinned_sha,
                "status": "error", "error": f"checkout {pinned_sha[:12]} failed after unshallow"}

    # Final verification
    _, head = _run(["git", "rev-parse", "HEAD"], cwd=dest)
    head = head.strip()
    if head != pinned_sha:
        return {"full_name": full_name, "sha": pinned_sha,
                "status": "sha_mismatch", "error": f"expected {pinned_sha[:12]}, got {head[:12]}"}

    return {"full_name": full_name, "sha": pinned_sha, "status": "ok", "error": None}


def main() -> None:
    parser = argparse.ArgumentParser(description="Clone corpus repos at pinned SHAs")
    parser.add_argument("--workers", type=int, default=4,
                        help="Parallel clone workers (default: 4)")
    args = parser.parse_args()

    if not CORPUS_PATH.exists():
        print(f"ERROR: {CORPUS_PATH} not found. Run collect_corpus.py first.")
        sys.exit(1)

    corpus = json.loads(CORPUS_PATH.read_text())
    REPOS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Cloning {len(corpus)} repos into {REPOS_DIR} using {args.workers} workers")

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(clone_repo, entry): entry["full_name"] for entry in corpus}
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)
            status = result["status"]
            name = result["full_name"]
            err = f" — {result['error']}" if result["error"] else ""
            print(f"  [{i:3d}/{len(corpus)}] {status:18s} {name}{err}", flush=True)

    REPORT_PATH.write_text(json.dumps(results, indent=2))

    ok = sum(1 for r in results if r["status"] in ("ok", "already_correct", "rechecked"))
    errors = [r for r in results if r["status"] not in ("ok", "already_correct", "rechecked")]

    print(f"\nDone: {ok}/{len(corpus)} cloned correctly")
    if errors:
        print(f"Errors ({len(errors)}):")
        for e in errors:
            print(f"  {e['full_name']}: {e['status']} — {e['error']}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
