#!/usr/bin/env python3
"""Find external skill candidates for a capability gap.

The script uses a safe discovery chain:

1. local curated registry
2. GitHub repository search sorted by stars
3. optional findskill-compatible CLIs when installed

It never installs skills. Installation is a separate user-approved step.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_MIN_STARS = 50
STOPWORDS = {
    "a",
    "agent",
    "ai",
    "and",
    "claude",
    "code",
    "coding",
    "for",
    "skill",
    "skills",
    "the",
    "to",
}


def bundle_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_registry(root: Path) -> list[dict[str, Any]]:
    paths = [
        root / "config" / "skill-candidates.json",
        bundle_root() / "config" / "skill-candidates.json",
    ]
    path = next((item for item in paths if item.exists()), None)
    if path is None:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return list(data.get("candidates", []))


def registry_matches(root: Path, capability: str, query: str, limit: int) -> list[dict[str, Any]]:
    capability_l = capability.lower()
    needles = {
        token
        for token in [capability_l, *query.lower().replace("-", " ").split()]
        if token and token not in STOPWORDS and len(token) > 2
    }
    matches = []
    for item in load_registry(root):
        item_cap = str(item.get("capability", "")).lower()
        haystack = " ".join(
            str(item.get(key, "")) for key in ["capability", "repo", "why", "intake"]
        ).lower()
        if item_cap == capability_l or any(needle and needle in haystack for needle in needles):
            matches.append({**item, "source": "local-registry"})
    return matches[:limit]


def github_search(query: str, limit: int, min_stars: int, timeout: int) -> list[dict[str, Any]]:
    terms = query.strip()
    if "skill" not in terms.lower():
        terms = f"{terms} skill"
    q = f"{terms} stars:>={min_stars}"
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": str(limit)}
    )
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "portable-vibe-coding-setup",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8", errors="ignore"))
    except Exception as exc:
        return [
            {
                "source": "github",
                "error": str(exc),
                "search_url": "https://github.com/search?"
                + urllib.parse.urlencode({"q": q, "type": "repositories", "s": "stars", "o": "desc"}),
            }
        ]

    results = []
    for item in payload.get("items", [])[:limit]:
        results.append(
            {
                "source": "github",
                "repo": item.get("full_name"),
                "url": item.get("html_url"),
                "description": item.get("description") or "",
                "stars": item.get("stargazers_count", 0),
                "updated_at": item.get("updated_at"),
                "license": (item.get("license") or {}).get("spdx_id"),
            }
        )
    return results


def run_cli(command: list[str], timeout: int) -> dict[str, Any] | None:
    executable = command[0]
    if shutil.which(executable) is None:
        return None
    try:
        proc = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except Exception as exc:
        return {"source": " ".join(command[:2]), "error": str(exc)}
    return {
        "source": " ".join(command[:2]),
        "returncode": proc.returncode,
        "stdout": proc.stdout[-4000:],
        "stderr": proc.stderr[-1200:],
    }


def cli_searches(query: str, timeout: int) -> list[dict[str, Any]]:
    searches = []
    # Vercel/open Agent Skills CLI. On Windows, direct subprocess works and
    # avoids shell quoting issues.
    searches.append(run_cli(["npx", "--yes", "skills", "find", query], timeout))
    # OpenClaw/ClawHub-style discovery when available.
    searches.append(run_cli(["npx", "--yes", "clawhub", "search", query], timeout))
    # Some environments expose a standalone findskill CLI.
    searches.append(run_cli(["findskill", "search", query], timeout))
    return [item for item in searches if item is not None]


def search_for_capability(
    root: Path,
    capability: str,
    query: str | None = None,
    limit: int = 5,
    min_stars: int = DEFAULT_MIN_STARS,
    timeout: int = 8,
    include_cli: bool = False,
) -> dict[str, Any]:
    search_query = query or f"claude code {capability} agent skill"
    registry = registry_matches(root, capability, search_query, limit)
    github = github_search(search_query, limit, min_stars, timeout)
    cli = cli_searches(search_query, timeout) if include_cli else []
    return {
        "capability": capability,
        "query": search_query,
        "requires_user_approval": True,
        "installs_nothing": True,
        "registry_candidates": registry,
        "github_candidates": github,
        "cli_observations": cli,
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Skill Candidate Search",
        "",
        f"Capability: `{report['capability']}`",
        f"Query: `{report['query']}`",
        "",
        "Policy: discovery only; user approval is required before import or install.",
        "",
        "## Local Registry",
    ]
    for item in report["registry_candidates"] or []:
        lines.append(f"- [{item.get('repo')}]({item.get('url')}): {item.get('why')}")
    if not report["registry_candidates"]:
        lines.append("- No local registry match.")

    lines.extend(["", "## GitHub"])
    for item in report["github_candidates"] or []:
        if "error" in item:
            lines.append(f"- Search error: {item['error']} ({item.get('search_url')})")
            continue
        lines.append(
            f"- [{item.get('repo')}]({item.get('url')}): "
            f"{item.get('stars')} stars, license {item.get('license') or 'unknown'}, "
            f"updated {item.get('updated_at')}. {item.get('description')}"
        )
    if not report["github_candidates"]:
        lines.append("- No GitHub candidates returned.")

    if report["cli_observations"]:
        lines.extend(["", "## findskill-compatible CLI observations"])
        for item in report["cli_observations"]:
            source = item.get("source")
            rc = item.get("returncode", "error")
            snippet = (item.get("stdout") or item.get("stderr") or item.get("error") or "").strip()
            snippet = " ".join(snippet.split())[:800]
            lines.append(f"- `{source}` exit `{rc}`: {snippet}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--capability", required=True)
    parser.add_argument("--query")
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--min-stars", type=int, default=DEFAULT_MIN_STARS)
    parser.add_argument("--timeout", type=int, default=8)
    parser.add_argument("--include-cli", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    args = parser.parse_args(argv)

    report = search_for_capability(
        args.root.resolve(),
        args.capability,
        query=args.query,
        limit=args.limit,
        min_stars=args.min_stars,
        timeout=args.timeout,
        include_cli=args.include_cli,
    )
    if args.json or not args.markdown:
        print(json.dumps(report, indent=2))
    else:
        print(markdown(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
