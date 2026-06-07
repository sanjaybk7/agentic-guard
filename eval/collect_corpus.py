"""Step 1 — Collect 150 agent repositories at pinned SHAs.

Searches GitHub for repositories across six agent frameworks, records the
exact HEAD SHA of each repo's default branch at collection time (without
cloning), and writes eval/corpus.json.

Run from the project root:
    python eval/collect_corpus.py

Requires GITHUB_TOKEN env var OR an active `gh` CLI session (reads the
token via `gh auth token`). Without authentication the API rate limit is
60 req/hr, which is insufficient; the script will stop and report how
many repos were collected before hitting the limit.

Output: eval/corpus.json
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

TARGET = 150
OUT_PATH = Path(__file__).parent / "corpus.json"

# Repos already used in the PR-4/PR-5 corpus — kept independent of eval.
EXCLUDED_REPOS: set[str] = {
    "openai/openai-agents-python",
    "langchain-ai/langgraph",
    "crewAIInc/crewAI",
    "NirDiamant/GenAI_Agents",
    "langchain-ai/langchain-academy",
    "assafelovic/gpt-researcher",          # open_deep_research
    "neural-maze/agents-towards-production",
    "openai/openai-cookbook",
    "langchain-ai/langchain",
}

# Search queries: (framework_tag, github_search_query)
SEARCH_QUERIES: list[tuple[str, str]] = [
    ("langgraph",        "langgraph agent language:python"),
    ("langgraph",        "langgraph workflow agent language:python"),
    ("openai-agents",    "openai-agents-sdk language:python"),
    ("openai-agents",    "openai agents sdk language:python"),
    ("openai-agents",    "openai swarm agent language:python"),
    ("crewai",           "crewai crew language:python"),
    ("crewai",           "crewai agent task language:python"),
    ("crewai",           "crewai flow language:python"),
    ("autogen",          "autogen agent language:python"),
    ("autogen",          "microsoft autogen language:python"),
    ("autogen",          "autogen studio language:python"),
    ("llama-index",      "llama-index agent language:python"),
    ("llama-index",      "llamaindex agents language:python"),
    ("llama-index",      "llama index agentic language:python"),
    ("langchain-agents", "langchain agent executor language:python"),
    ("langchain-agents", "langchain agentexecutor language:python"),
    ("langchain-agents", "langchain react agent language:python"),
]

# Target per-framework minimums to avoid one framework dominating.
FRAMEWORK_TARGETS: dict[str, int] = {
    "langgraph":        30,
    "openai-agents":    30,
    "crewai":           25,
    "autogen":          25,
    "llama-index":      20,
    "langchain-agents": 20,
}

# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

def _gh_token() -> str:
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, check=True
            )
            token = result.stdout.strip()
        except Exception:
            pass
    return token


def _api_get(url: str, token: str) -> dict[str, Any] | None:
    """GET a GitHub API URL. Returns parsed JSON or None on rate-limit / error."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  [rate-limit] {url}", flush=True)
            return None
        if e.code == 404:
            return None
        print(f"  [HTTP {e.code}] {url}", flush=True)
        return None
    except Exception as exc:
        print(f"  [error] {url}: {exc}", flush=True)
        return None


def search_repos(query: str, token: str, per_page: int = 30) -> list[dict[str, Any]]:
    """Search GitHub repos; returns raw item list (up to per_page results)."""
    encoded = urllib.parse.quote(query)
    url = (
        f"https://api.github.com/search/repositories"
        f"?q={encoded}&sort=stars&order=desc&per_page={per_page}"
    )
    data = _api_get(url, token)
    if data is None:
        return []
    return data.get("items", [])


def get_head_sha(full_name: str, branch: str, token: str) -> str | None:
    """Get the HEAD commit SHA of a branch without cloning."""
    url = f"https://api.github.com/repos/{full_name}/git/refs/heads/{branch}"
    data = _api_get(url, token)
    if data is None:
        return None
    # Response is either a single object or a list (if branch name is a prefix)
    if isinstance(data, list):
        for ref in data:
            if ref.get("ref") == f"refs/heads/{branch}":
                return ref["object"]["sha"]
        return None
    if isinstance(data, dict) and "object" in data:
        return data["object"]["sha"]
    return None


def has_enough_python(item: dict) -> bool:
    """Approximate Python-file presence using fields already in the search result.

    Uses repo language + size as a proxy to avoid the heavily rate-limited
    code-search endpoint. A Python repo with size >= 50 KB almost certainly
    has ≥5 Python files.
    """
    lang = (item.get("language") or "").lower()
    size_kb = item.get("size", 0)
    # Must be primarily Python AND have meaningful size
    return lang == "python" and size_kb >= 50


# ---------------------------------------------------------------------------
# Main collection logic
# ---------------------------------------------------------------------------

import urllib.parse  # noqa: E402 (after helpers that use it)


def collect() -> None:
    token = _gh_token()
    if not token:
        print("ERROR: No GitHub token found. Set GITHUB_TOKEN or run `gh auth login`.")
        sys.exit(1)

    collected: list[dict[str, Any]] = []
    seen_full_names: set[str] = set()
    framework_counts: dict[str, int] = {f: 0 for f in FRAMEWORK_TARGETS}
    rate_limited = False
    collected_at = datetime.now(timezone.utc).isoformat()

    print(f"Target: {TARGET} repos | Excluded: {len(EXCLUDED_REPOS)} prior-corpus repos")
    print(f"Exclusions: {sorted(EXCLUDED_REPOS)}\n")

    for framework_tag, query in SEARCH_QUERIES:
        if len(collected) >= TARGET:
            break
        if rate_limited:
            break

        print(f"[{framework_tag}] Searching: {query!r}")
        items = search_repos(query, token, per_page=50)
        if not items:
            print(f"  → 0 results (rate-limited or empty)")
            rate_limited = True
            break

        cap = FRAMEWORK_TARGETS.get(framework_tag, 30)
        if framework_counts.get(framework_tag, 0) >= cap:
            print(f"  → cap reached for {framework_tag} ({cap}), skipping query")
            continue

        for item in items:
            if len(collected) >= TARGET:
                break

            # Enforce per-framework cap
            if framework_counts.get(framework_tag, 0) >= cap:
                break

            full_name: str = item["full_name"]

            # Dedup
            if full_name in seen_full_names:
                continue

            # Exclude prior-corpus repos
            if full_name in EXCLUDED_REPOS:
                print(f"  skip (prior corpus): {full_name}")
                seen_full_names.add(full_name)
                continue

            # Skip forks
            if item.get("fork", False):
                continue

            # Skip archived
            if item.get("archived", False):
                continue

            # Get HEAD SHA
            default_branch: str = item.get("default_branch", "main")
            sha = get_head_sha(full_name, default_branch, token)
            if sha is None:
                print(f"  skip (SHA unavailable): {full_name}")
                continue

            # Check Python content (language + size proxy; avoids code-search rate limit)
            if not has_enough_python(item):
                lang = item.get("language", "?")
                size = item.get("size", 0)
                print(f"  skip (not Python or too small, lang={lang} size={size}KB): {full_name}")
                continue

            entry = {
                "full_name": full_name,
                "clone_url": item["clone_url"],
                "default_branch": default_branch,
                "sha": sha,
                "framework_tag": framework_tag,
                "stars": item.get("stargazers_count", 0),
                "collected_at": collected_at,
            }
            collected.append(entry)
            seen_full_names.add(full_name)
            framework_counts[framework_tag] = framework_counts.get(framework_tag, 0) + 1
            print(f"  + {full_name} [{framework_tag}] sha={sha[:12]} stars={entry['stars']}")

        time.sleep(2)  # inter-query pause

    # Write output
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(collected, indent=2))

    print(f"\n{'='*60}")
    print(f"Collected: {len(collected)} repos (target {TARGET})")
    print(f"Rate-limited during collection: {rate_limited}")
    print("\nFramework distribution:")
    for fw, count in sorted(framework_counts.items()):
        print(f"  {fw}: {count}")
    print(f"\nOutput: {OUT_PATH}")
    if len(collected) < TARGET:
        print(
            f"\nWARNING: Only {len(collected)}/{TARGET} repos collected. "
            "This may be due to API rate limits or insufficient search results. "
            "Do not fabricate entries to reach 150."
        )


if __name__ == "__main__":
    collect()
