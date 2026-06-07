"""Corpus preparation pass — three fixes before the full scan.

Fix 1: Re-derive framework_tag from actual imports in each repo.
Fix 2: Replace 0-2-star langchain-agents repos that have <5 Python files.
Fix 3: Run agentic-guard agent detection on each repo; record agent_count.

Run from the project root (must have cloned or will clone here):
    python eval/prep_corpus.py

Writes:
  eval/corpus.json          — updated in place
  eval/prep_report.json     — full per-repo detail for audit
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

CORPUS_PATH = Path("eval/corpus.json")
REPOS_DIR   = Path("eval/repos")
REPORT_PATH = Path("eval/prep_report.json")

EXCLUDED_REPOS: set[str] = {
    "openai/openai-agents-python",
    "langchain-ai/langgraph",
    "crewAIInc/crewAI",
    "NirDiamant/GenAI_Agents",
    "langchain-ai/langchain-academy",
    "assafelovic/gpt-researcher",
    "neural-maze/agents-towards-production",
    "openai/openai-cookbook",
    "langchain-ai/langchain",
}

FRAMEWORK_CAPS = {
    "langgraph":        30,
    "openai-agents":    30,
    "crewai":           25,
    "autogen":          25,
    "llama-index":      20,
    "langchain-agents": 20,
}

# ─── GitHub API ──────────────────────────────────────────────────────────────

def _gh_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        try:
            r = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True)
            token = r.stdout.strip()
        except Exception:
            pass
    return token


def _api_get(url: str, token: str) -> Any:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code in (403, 429):
            return None  # rate-limited
        return None
    except Exception:
        return None


def get_head_sha(full_name: str, branch: str, token: str) -> str | None:
    url = f"https://api.github.com/repos/{full_name}/git/refs/heads/{branch}"
    data = _api_get(url, token)
    if data is None:
        return None
    if isinstance(data, list):
        for ref in data:
            if ref.get("ref") == f"refs/heads/{branch}":
                return ref["object"]["sha"]
        return None
    if isinstance(data, dict) and "object" in data:
        return data["object"]["sha"]
    return None


def search_repos(query: str, token: str, per_page: int = 50) -> list[dict]:
    encoded = urllib.parse.quote(query)
    url = (f"https://api.github.com/search/repositories"
           f"?q={encoded}&sort=stars&order=desc&per_page={per_page}")
    data = _api_get(url, token)
    if not data:
        return []
    return data.get("items", [])


# ─── Clone helpers ────────────────────────────────────────────────────────────

def _run(cmd: list[str], cwd: Path | None = None) -> tuple[int, str]:
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return r.returncode, (r.stdout + r.stderr).strip()


def shallow_clone(full_name: str, clone_url: str, branch: str, sha: str) -> Path | None:
    dest = REPOS_DIR / full_name
    if dest.exists():
        # Verify HEAD
        rc, head = _run(["git", "rev-parse", "HEAD"], cwd=dest)
        if rc == 0 and head.strip() == sha:
            return dest
        # Present but wrong — try checkout
        _run(["git", "checkout", sha], cwd=dest)
        rc2, head2 = _run(["git", "rev-parse", "HEAD"], cwd=dest)
        if rc2 == 0 and head2.strip() == sha:
            return dest

    dest.parent.mkdir(parents=True, exist_ok=True)
    rc, _ = _run(["git", "clone", "--depth", "1", "--branch", branch,
                   clone_url, str(dest)])
    if rc != 0:
        return None

    _, head = _run(["git", "rev-parse", "HEAD"], cwd=dest)
    if head.strip() == sha:
        return dest

    # SHA differs from branch tip — unshallow and checkout
    _run(["git", "fetch", "--unshallow"], cwd=dest)
    rc2, _ = _run(["git", "checkout", sha], cwd=dest)
    if rc2 != 0:
        return None

    return dest


# ─── Fix 1: import-based framework detection ─────────────────────────────────

# Each detector returns True if the repo matches the framework.
# Priority order: langgraph > crewai > autogen > openai-agents > llama-index > langchain-agents

def _grep(pattern: str, path: Path, recursive: bool = True) -> bool:
    """Return True if pattern found in any .py file under path."""
    flags = ["-rl", "--include=*.py", "-m", "1"]
    if not recursive:
        flags = ["-l", "--include=*.py", "-m", "1"]
    r = subprocess.run(["grep"] + flags + [pattern, str(path)],
                       capture_output=True, text=True)
    return r.returncode == 0


def detect_framework(repo_path: Path) -> str:
    """Detect primary agent framework from imports. Priority: langgraph first."""
    # langgraph wins over plain langchain
    if _grep(r"from langgraph\|import langgraph", repo_path):
        return "langgraph"
    # crewai
    if _grep(r"from crewai\|import crewai", repo_path):
        return "crewai"
    # autogen / ag2
    if _grep(r"from autogen\|import autogen\|from ag2\|import ag2\|from autogen_agentchat\|import autogen_agentchat", repo_path):
        return "autogen"
    # OpenAI Agents SDK — imported as `agents` package; look for Agent/Runner from it
    if _grep(r"from agents import\|from openai_agents\|import openai_agents", repo_path):
        return "openai-agents"
    # llama-index agents (not just RAG — must have agent-specific class usage)
    if _grep(r"from llama_index\|import llama_index", repo_path):
        agent_patterns = r"AgentRunner\|FunctionCallingAgent\|OpenAIAgent\|ReActAgent\|StructuredPlannerAgent\|AgentWorker\|llama_index\.agent"
        if _grep(agent_patterns, repo_path):
            return "llama-index"
    # langchain agents (AgentExecutor / React / tool-calling, NOT langgraph)
    if _grep(r"from langchain\|import langchain", repo_path):
        agent_patterns = r"AgentExecutor\|create_react_agent\|create_tool_calling_agent\|create_openai_tools_agent\|ZeroShotAgent\|initialize_agent"
        if _grep(agent_patterns, repo_path):
            return "langchain-agents"
    return "unknown"


def count_python_files(repo_path: Path) -> int:
    result = subprocess.run(
        ["find", str(repo_path), "-name", "*.py", "-not", "-path", "*/.git/*"],
        capture_output=True, text=True
    )
    return len([l for l in result.stdout.splitlines() if l.strip()])


# ─── Fix 3: agent count via agentic-guard parser ─────────────────────────────

def count_agents(repo_path: Path) -> int:
    """Return the number of agent definitions found by the agentic-guard parser.

    Uses the Python API (Scanner.scan) directly so that agent_count is
    independent of whether any rules fire — a clean repo with agents still
    reports the right count.
    """
    try:
        # Import here to avoid polluting the top-level namespace and to allow
        # the function to fail gracefully if the package isn't installed.
        from agentic_guard.engine import Scanner  # noqa: PLC0415
        result = Scanner().scan(repo_path)
        return result.agents_seen
    except Exception:
        return -1  # -1 = scan error, distinguishable from 0 (scanned, no agents)


# ─── Fix 2: find replacement langchain-agents repos ──────────────────────────

REPLACEMENT_QUERIES = [
    "langchain AgentExecutor tools language:python stars:>10",
    "langchain create_react_agent tools language:python stars:>10",
    "langchain agent tools executor language:python stars:>20",
    "langchain openai tools agent language:python stars:>15",
    "langchain tool calling agent language:python stars:>10",
]


def find_replacement_lca(
    n: int,
    exclude: set[str],
    token: str,
) -> list[dict]:
    """Search GitHub for n substantive langchain-agent repos not in exclude."""
    found: list[dict] = []
    seen: set[str] = set(exclude)

    for query in REPLACEMENT_QUERIES:
        if len(found) >= n:
            break
        items = search_repos(query, token, per_page=50)
        time.sleep(1)
        for item in items:
            if len(found) >= n:
                break
            fn = item["full_name"]
            if fn in seen:
                continue
            if item.get("fork") or item.get("archived"):
                continue
            lang = (item.get("language") or "").lower()
            size_kb = item.get("size", 0)
            if lang != "python" or size_kb < 50:
                continue
            sha = get_head_sha(fn, item.get("default_branch", "main"), token)
            if sha is None:
                continue
            seen.add(fn)
            found.append({
                "full_name": fn,
                "clone_url": item["clone_url"],
                "default_branch": item.get("default_branch", "main"),
                "sha": sha,
                "framework_tag": "langchain-agents",
                "stars": item.get("stargazers_count", 0),
                "collected_at": datetime.now(timezone.utc).isoformat(),
            })
            print(f"    replacement: {fn} stars={item.get('stargazers_count',0)}")

    return found


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    token = _gh_token()
    corpus: list[dict] = json.loads(CORPUS_PATH.read_text())
    all_full_names: set[str] = {e["full_name"] for e in corpus}
    report: list[dict] = []

    # ── Step A: shallow-clone all 150 repos ──────────────────────────────────
    print(f"=== Cloning {len(corpus)} repos (shallow) ===")

    def _clone_entry(entry: dict) -> tuple[dict, Path | None]:
        dest = shallow_clone(
            entry["full_name"], entry["clone_url"],
            entry["default_branch"], entry["sha"]
        )
        return entry, dest

    cloned: dict[str, Path | None] = {}
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_clone_entry, e): e["full_name"] for e in corpus}
        for i, fut in enumerate(as_completed(futures), 1):
            entry, dest = fut.result()
            cloned[entry["full_name"]] = dest
            status = "ok" if dest else "FAIL"
            print(f"  [{i:3d}/{len(corpus)}] {status}  {entry['full_name']}", flush=True)

    # ── Step B: Fix 1 — re-tag by imports ────────────────────────────────────
    print("\n=== Fix 1: re-tagging by imports ===")
    retag_log: list[dict] = []
    py_counts: dict[str, int] = {}

    for entry in corpus:
        fn = entry["full_name"]
        dest = cloned.get(fn)
        if dest is None:
            report.append({"full_name": fn, "error": "clone_failed"})
            continue

        py_count = count_python_files(dest)
        py_counts[fn] = py_count
        detected = detect_framework(dest)
        old_tag = entry["framework_tag"]

        if detected != old_tag:
            print(f"  RETAG {fn}: {old_tag} → {detected}")
            retag_log.append({"full_name": fn, "old_tag": old_tag, "new_tag": detected})
            entry["framework_tag"] = detected

    # ── Step C: Fix 2 — replace weak langchain-agents repos ──────────────────
    print("\n=== Fix 2: replacing low-quality langchain-agents repos ===")

    lca_weak = [
        e for e in corpus
        if e["framework_tag"] == "langchain-agents"
        and e["stars"] <= 2
        and py_counts.get(e["full_name"], 999) < 5
    ]
    print(f"  Repos to remove: {len(lca_weak)}")
    for e in lca_weak:
        print(f"    - {e['full_name']} (stars={e['stars']}, py_files={py_counts.get(e['full_name'], '?')})")

    removed_names = {e["full_name"] for e in lca_weak}
    corpus_keep = [e for e in corpus if e["full_name"] not in removed_names]

    # Find replacements
    all_known = all_full_names | EXCLUDED_REPOS
    replacements = find_replacement_lca(len(lca_weak), all_known, token)
    print(f"  Replacements found: {len(replacements)}")

    # Shallow-clone replacements
    for rep in replacements:
        dest = shallow_clone(
            rep["full_name"], rep["clone_url"],
            rep["default_branch"], rep["sha"]
        )
        cloned[rep["full_name"]] = dest
        rep_tag = detect_framework(dest) if dest else "langchain-agents"
        rep["framework_tag"] = rep_tag
        py_counts[rep["full_name"]] = count_python_files(dest) if dest else 0
        all_full_names.add(rep["full_name"])
        print(f"    cloned replacement: {rep['full_name']} detected={rep_tag}")

    corpus_final = corpus_keep + replacements

    # Enforce cap — trim if any framework is over
    from collections import Counter
    fw_counts: Counter = Counter(e["framework_tag"] for e in corpus_final)
    trimmed: list[dict] = []
    fw_seen: Counter = Counter()
    for entry in corpus_final:
        cap = FRAMEWORK_CAPS.get(entry["framework_tag"], 9999)
        if fw_seen[entry["framework_tag"]] < cap:
            trimmed.append(entry)
            fw_seen[entry["framework_tag"]] += 1

    corpus_final = trimmed

    # ── Step D: Fix 3 — agent count ──────────────────────────────────────────
    print(f"\n=== Fix 3: counting agents in {len(corpus_final)} repos ===")

    def _count(entry: dict) -> tuple[str, int]:
        dest = cloned.get(entry["full_name"])
        if dest is None:
            return entry["full_name"], -1
        n = count_agents(dest)
        return entry["full_name"], n

    agent_counts: dict[str, int] = {}
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures2 = {pool.submit(_count, e): e["full_name"] for e in corpus_final}
        for i, fut in enumerate(as_completed(futures2), 1):
            fn, n = fut.result()
            agent_counts[fn] = n
            print(f"  [{i:3d}/{len(corpus_final)}] agents={n:3d}  {fn}", flush=True)

    for entry in corpus_final:
        entry["agent_count"] = agent_counts.get(entry["full_name"], -1)
        entry["py_file_count"] = py_counts.get(entry["full_name"], -1)

    # ── Write outputs ─────────────────────────────────────────────────────────
    CORPUS_PATH.write_text(json.dumps(corpus_final, indent=2))

    fw_dist = Counter(e["framework_tag"] for e in corpus_final)
    zero_agent = [e["full_name"] for e in corpus_final if e.get("agent_count", -1) == 0]

    prep_report = {
        "total": len(corpus_final),
        "framework_distribution": dict(fw_dist),
        "retagged": retag_log,
        "removed": [{"full_name": e["full_name"], "stars": e["stars"],
                     "py_files": py_counts.get(e["full_name"], "?"),
                     "reason": "0-2 stars and <5 Python files"}
                    for e in lca_weak],
        "added_replacements": [{"full_name": r["full_name"], "stars": r["stars"],
                                 "framework_tag": r["framework_tag"]}
                                for r in replacements],
        "zero_agent_repos": zero_agent,
        "zero_agent_count": len(zero_agent),
    }
    REPORT_PATH.write_text(json.dumps(prep_report, indent=2))

    # ── Console summary ───────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print(f"Total repos: {len(corpus_final)}")
    print("\nFramework distribution (post-fix):")
    for fw, cnt in sorted(fw_dist.items()):
        print(f"  {fw}: {cnt}")
    print(f"\nRetagged: {len(retag_log)}")
    for r in retag_log:
        print(f"  {r['full_name']}: {r['old_tag']} → {r['new_tag']}")
    print(f"\nRemoved (weak langchain-agents): {len(lca_weak)}")
    print(f"Replacements added: {len(replacements)}")
    print(f"\nRepos with agent_count == 0: {len(zero_agent)}")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()
