"""Step 3 — Scan all cloned corpus repos with the frozen analyzer.

Verifies the current analyzer matches the SHA in eval/FROZEN_VERSION before
running any scans. Refuses to proceed if the SHA doesn't match.

Run from the project root:
    python eval/run_scan.py [--repos-dir eval/repos] [--workers N]

Output:
  eval/findings.csv     — one row per finding, with empty label/notes columns
  eval/scan_summary.json — aggregate counts
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

FROZEN_VERSION_PATH = Path(__file__).parent / "FROZEN_VERSION"
CORPUS_PATH = Path(__file__).parent / "corpus.json"
FINDINGS_CSV = Path(__file__).parent / "findings.csv"
SUMMARY_JSON = Path(__file__).parent / "scan_summary.json"

FINDINGS_COLUMNS = [
    "repo_full_name",
    "repo_sha",
    "file_path",
    "line",
    "rule_id",
    "severity",
    "agent_name",
    "source_tool",
    "sink_tool",
    "prompt_expr",
    "raw_message",
    "label",   # empty — filled during manual labeling
    "notes",   # empty — filled during manual labeling
]


# ---------------------------------------------------------------------------
# Freeze check
# ---------------------------------------------------------------------------

def _current_sha() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True
    )
    return result.stdout.strip()


def _check_freeze() -> str:
    if not FROZEN_VERSION_PATH.exists():
        print(f"ERROR: {FROZEN_VERSION_PATH} not found.")
        sys.exit(1)

    lines = FROZEN_VERSION_PATH.read_text().strip().splitlines()
    frozen_sha = lines[0].strip()
    current = _current_sha()

    if current != frozen_sha:
        print(
            f"ERROR: Analyzer is not at the frozen SHA.\n"
            f"  Frozen:  {frozen_sha}\n"
            f"  Current: {current}\n"
            f"Check out the frozen commit before running scans:\n"
            f"  git checkout {frozen_sha}"
        )
        sys.exit(1)

    print(f"Freeze check passed: analyzer at {frozen_sha[:12]}")
    return frozen_sha


# ---------------------------------------------------------------------------
# Scan a single repo
# ---------------------------------------------------------------------------

def scan_repo(repo_path: Path, full_name: str, repo_sha: str) -> tuple[list[dict], str | None]:
    """Run agentic-guard on a repo. Returns (findings, error_msg)."""
    import re as _re  # noqa: PLC0415
    try:
        from agentic_guard.engine import Scanner  # noqa: PLC0415
        result = Scanner().scan(repo_path)
    except TimeoutError:
        return [], "scan timed out"
    except Exception as exc:
        return [], f"scan error: {exc}"

    rows: list[dict] = []
    for f in result.findings:
        rule_id = f.rule_id
        loc = f.location

        source_tool = ""
        sink_tool = ""
        agent_name = getattr(f, "agent_name", "") or ""
        prompt_expr = ""

        if rule_id == "IG001":
            msg = f.message
            src_m = _re.search(r"untrusted source `([^`]+)`", msg)
            snk_m = _re.search(r"privileged sink `([^`]+)`", msg)
            source_tool = src_m.group(1) if src_m else ""
            sink_tool = snk_m.group(1) if snk_m else ""
        elif rule_id == "IG002":
            prompt_expr = ", ".join(getattr(f, "taint_sources", []) or [])

        rows.append({
            "repo_full_name": full_name,
            "repo_sha": repo_sha,
            "file_path": str(loc.file) if loc else "",
            "line": loc.line if loc else "",
            "rule_id": rule_id,
            "severity": f.severity.value if hasattr(f.severity, "value") else str(f.severity),
            "agent_name": agent_name,
            "source_tool": source_tool,
            "sink_tool": sink_tool,
            "prompt_expr": prompt_expr,
            "raw_message": f.message[:300],
            "label": "",
            "notes": "",
        })

    return rows, None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Scan corpus repos with frozen analyzer")
    parser.add_argument("--repos-dir", type=Path,
                        default=Path(__file__).parent / "repos",
                        help="Directory containing cloned repos")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel scan workers (default: 1; scans are CPU-bound)")
    args = parser.parse_args()

    frozen_sha = _check_freeze()

    if not CORPUS_PATH.exists():
        print(f"ERROR: {CORPUS_PATH} not found.")
        sys.exit(1)

    corpus = json.loads(CORPUS_PATH.read_text())
    repos_dir: Path = args.repos_dir

    all_rows: list[dict] = []
    per_repo: list[dict] = []
    errored: list[dict] = []

    for i, entry in enumerate(corpus, 1):
        full_name = entry["full_name"]
        repo_sha = entry["sha"]
        repo_path = repos_dir / full_name

        if not repo_path.exists():
            print(f"[{i:3d}/{len(corpus)}] MISSING   {full_name} (run clone_corpus.py first)")
            errored.append({"full_name": full_name, "error": "repo not cloned"})
            continue

        findings, error = scan_repo(repo_path, full_name, repo_sha)

        status = "error" if error else "ok"
        count = len(findings)
        print(
            f"[{i:3d}/{len(corpus)}] {status:8s}  {full_name:50s}  {count:3d} findings"
            + (f"  — {error}" if error else ""),
            flush=True,
        )

        if error:
            errored.append({"full_name": full_name, "error": error})
        else:
            all_rows.extend(findings)
            per_repo.append({
                "full_name": full_name,
                "repo_sha": repo_sha,
                "finding_count": count,
                "ig001": sum(1 for r in findings if r["rule_id"] == "IG001"),
                "ig002": sum(1 for r in findings if r["rule_id"] == "IG002"),
            })

    # Write CSV
    FINDINGS_CSV.parent.mkdir(parents=True, exist_ok=True)
    with FINDINGS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FINDINGS_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    # Write summary
    summary = {
        "frozen_sha": frozen_sha,
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "repos_scanned": len(per_repo),
        "repos_errored": len(errored),
        "total_findings": len(all_rows),
        "ig001_findings": sum(r["ig001"] for r in per_repo),
        "ig002_findings": sum(r["ig002"] for r in per_repo),
        "per_repo": per_repo,
        "errors": errored,
    }
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))

    print(f"\n{'='*60}")
    print(f"Scanned:       {len(per_repo)}/{len(corpus)} repos")
    print(f"Errored:       {len(errored)}")
    print(f"Total findings:{len(all_rows):5d}  (IG001: {summary['ig001_findings']}, IG002: {summary['ig002_findings']})")
    print(f"Findings CSV:  {FINDINGS_CSV}")
    print(f"Summary JSON:  {SUMMARY_JSON}")


if __name__ == "__main__":
    main()
