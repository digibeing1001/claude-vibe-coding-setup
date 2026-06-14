#!/usr/bin/env python3
"""Score a Vibe Coding run and report missing capability coverage.

This script is intentionally heuristic and dependency-free. It is not a
replacement for tests or human review; it is a compact gate that makes the
agent state what evidence exists and where it needs a stronger skill.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    from find_skill_candidates import search_for_capability
except Exception:  # pragma: no cover - optional helper during partial installs.
    search_for_capability = None


CAPABILITY_SKILLS = {
    "agent-harness": [
        "autonomous-agent-harness",
        "agent-harness-construction",
        "continuous-agent-loop",
        "agent-eval",
    ],
    "accessibility": ["ui-design-review", "design-review", "browser-qa"],
    "browser-qa": ["browser-qa", "e2e-testing", "verification-loop"],
    "deployment": ["deployment-patterns", "canary-watch", "production-audit", "gsd-ship"],
    "design": ["vibe-design-workflow", "design-review", "ui-design-review"],
    "git-safety": ["git-guardrails-claude-code", "setup-pre-commit"],
    "findskill": ["vibe-run-review", "codex-vibe-coding", "vibe-coding"],
    "review": ["review", "requesting-code-review", "plankton-code-quality", "gsd-code-review"],
    "security": ["cso", "security-review", "security-auditor-1.0.0", "security-scan"],
    "testing": [
        "test-driven-development",
        "test-runner-1.0.0",
        "ai-regression-testing",
        "e2e-testing",
        "verification-loop",
    ],
}

CODE_EXTENSIONS = {
    ".c",
    ".cc",
    ".cpp",
    ".cs",
    ".go",
    ".java",
    ".js",
    ".jsx",
    ".kt",
    ".mjs",
    ".py",
    ".rb",
    ".rs",
    ".swift",
    ".ts",
    ".tsx",
}

UI_EXTENSIONS = {".css", ".html", ".jsx", ".tsx", ".vue", ".svelte"}
SECURITY_HINTS = re.compile(r"(auth|login|password|secret|token|payment|stripe|oauth|sql|crypto)", re.I)
PASS_HINTS = re.compile(r"(pass|passed|success|ok|errors:\s*0|exit code:\s*0|green)", re.I)
COMMAND_HINTS = re.compile(
    r"\b(pytest|vitest|jest|npm|pnpm|yarn|tsc|eslint|ruff|mypy|go test|cargo test|"
    r"swift test|xcodebuild|playwright|validate_setup|score_vibe_run|git diff --check)\b",
    re.I,
)
SMELL_HINTS = re.compile(r"\b(FIXME|debugger|console\.log|eval\(|new Function\()", re.I)


@dataclass
class DiffItem:
    path: str
    added: int
    deleted: int


def bundle_root() -> Path:
    return Path(__file__).resolve().parents[1]


def run_git(root: Path, args: list[str]) -> tuple[int, str]:
    try:
        proc = subprocess.run(
            ["git", *args],
            cwd=str(root),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        return proc.returncode, proc.stdout
    except FileNotFoundError:
        return 127, ""


def parse_numstat(output: str) -> list[DiffItem]:
    items: list[DiffItem] = []
    for line in output.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        added_s, deleted_s, path = parts[0], parts[1], parts[-1]
        added = 0 if added_s == "-" else int(added_s)
        deleted = 0 if deleted_s == "-" else int(deleted_s)
        if " => " in path and "{" in path:
            path = path.split(" => ", 1)[-1].strip("{}")
        items.append(DiffItem(path=path.replace("\\", "/"), added=added, deleted=deleted))
    return items


def count_new_file_lines(path: Path) -> int:
    try:
        if path.stat().st_size > 2_000_000:
            return 0
        return len(path.read_text(encoding="utf-8", errors="ignore").splitlines())
    except OSError:
        return 0


def untracked_items(root: Path) -> list[DiffItem]:
    code, out = run_git(root, ["ls-files", "--others", "--exclude-standard"])
    if code != 0:
        return []
    items: list[DiffItem] = []
    for rel in out.splitlines():
        path = root / rel
        if path.is_file():
            items.append(DiffItem(path=rel.replace("\\", "/"), added=count_new_file_lines(path), deleted=0))
    return items


def diff_items(root: Path, base: str | None, head: str | None) -> tuple[str, list[DiffItem]]:
    if base:
        spec = [base, head or "HEAD"] if head else [base]
        code, out = run_git(root, ["diff", "--numstat", *spec])
        return " ".join(["git diff --numstat", *spec]), parse_numstat(out) if code == 0 else []

    code, out = run_git(root, ["diff", "--numstat", "HEAD"])
    items = parse_numstat(out) if code == 0 else []
    items.extend(untracked_items(root))
    if items:
        return "git diff --numstat HEAD + untracked", items

    code, out = run_git(root, ["diff", "--numstat", "HEAD~1", "HEAD"])
    if code == 0:
        return "git diff --numstat HEAD~1 HEAD", parse_numstat(out)
    return "no git diff available", []


def detected_skill_dirs(root: Path, explicit: Path | None) -> list[Path]:
    if explicit:
        return [explicit.expanduser()]
    home = Path.home()
    candidates = [
        root / "skills",
        home / ".codex" / "skills",
        home / ".claude" / "skills",
        home / ".hermes" / "skills",
        home / ".openclaw" / "skills",
        home / ".agents" / "skills",
    ]
    return [path for path in candidates if path.exists()]


def installed_skills(root: Path, explicit: Path | None = None) -> set[str]:
    skills: set[str] = set()
    for skills_dir in detected_skill_dirs(root, explicit):
        skills.update(
            path.name
            for path in skills_dir.iterdir()
            if path.is_dir() and (path / "SKILL.md").exists()
        )
    return skills


def infer_capabilities(items: list[DiffItem]) -> set[str]:
    caps = {"testing", "review"}
    for item in items:
        path = item.path.lower()
        suffix = Path(path).suffix
        if suffix in UI_EXTENSIONS or any(part in path for part in ["frontend", "ui", "app/", "pages/"]):
            caps.update({"browser-qa", "design", "accessibility"})
        if SECURITY_HINTS.search(path):
            caps.add("security")
        if any(part in path for part in ["deploy", "docker", ".github/workflows", "infra", "terraform"]):
            caps.add("deployment")
        if path.startswith("scripts/") or path.startswith("hooks/") or "install" in path:
            caps.add("git-safety")
        if "agent" in path or "loop" in path or "harness" in path:
            caps.add("agent-harness")
    return caps


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def line_count(path: Path) -> int:
    text = read_text(path)
    return len(text.splitlines()) if text else 0


def score_change_containment(items: list[DiffItem]) -> tuple[int, list[str]]:
    if not items:
        return 16, ["No diff detected; score uses neutral containment."]
    files = len(items)
    changed = sum(item.added + item.deleted for item in items)
    code_files = [
        item
        for item in items
        if Path(item.path).suffix.lower() in CODE_EXTENSIONS
    ]
    code_changed = sum(item.added + item.deleted for item in code_files)
    score = 25
    notes: list[str] = [
        f"{files} changed file(s), {changed} changed line(s); "
        f"{len(code_files)} code file(s), {code_changed} code line(s)."
    ]
    if len(code_files) > 12:
        score -= 8
        notes.append("Many code files changed; review for unrelated churn.")
    elif len(code_files) > 6:
        score -= 4
        notes.append("Moderate code file spread.")
    if code_changed > 1200:
        score -= 8
        notes.append("Large code line delta; split or strengthen evidence.")
    elif code_changed > 500:
        score -= 4
        notes.append("Moderate code line delta.")
    if changed > 3000 and code_changed <= 1200:
        score -= 2
        notes.append("Large documentation/instruction delta; strengthen validation evidence.")
    if any(part in item.path for item in items for part in ["node_modules/", "dist/", "build/"]):
        score -= 5
        notes.append("Generated or dependency output appears in the diff.")
    return max(score, 0), notes


def score_verification(evidence_paths: list[Path]) -> tuple[int, list[str]]:
    if not evidence_paths:
        return 8, ["No evidence file supplied; rely on live transcript only."]

    combined = "\n".join(read_text(path) for path in evidence_paths if path.exists())
    missing = [str(path) for path in evidence_paths if not path.exists()]
    commands = len(COMMAND_HINTS.findall(combined))
    passes = len(PASS_HINTS.findall(combined))
    score = 12
    notes = [f"{len(evidence_paths) - len(missing)} evidence file(s), {commands} command hint(s)."]
    if missing:
        score -= 4
        notes.append("Missing evidence path(s): " + ", ".join(missing))
    if commands >= 3 and passes >= 2:
        score = 25
    elif commands >= 2 and passes >= 1:
        score = 21
    elif commands >= 1:
        score = 16
    else:
        notes.append("Evidence lacks recognizable verification commands.")
    return max(score, 0), notes


def score_capabilities(
    root: Path, required: set[str], skills_dir: Path | None
) -> tuple[int, list[str], list[dict[str, Any]]]:
    skills = installed_skills(root, skills_dir)
    missing: list[dict[str, Any]] = []
    notes: list[str] = []
    if not required:
        return 18, ["No explicit or inferred capabilities required."], missing

    for cap in sorted(required):
        expected = CAPABILITY_SKILLS.get(cap, [])
        present = sorted(name for name in expected if name in skills)
        if present:
            notes.append(f"{cap}: covered by {', '.join(present[:3])}.")
        else:
            notes.append(f"{cap}: no mapped local skill found.")
            missing.append({"capability": cap, "expected_skills": expected})

    ratio = (len(required) - len(missing)) / len(required)
    score = round(20 * ratio)
    return score, notes, missing


def score_maintainability(root: Path, items: list[DiffItem]) -> tuple[int, list[str]]:
    score = 20
    notes: list[str] = []
    for item in items:
        path = root / item.path
        suffix = path.suffix.lower()
        if suffix in CODE_EXTENSIONS and path.exists():
            text = read_text(path)
            scanned = "\n".join(
                line for line in text.splitlines() if "SMELL_HINTS" not in line
            )
            smells = SMELL_HINTS.findall(scanned)
            if smells:
                score -= min(6, len(smells) * 2)
                notes.append(f"{item.path}: review debug/TODO/eval-like markers.")
            lines = line_count(path)
            if lines > 650:
                score -= 3
                notes.append(f"{item.path}: {lines} lines; check cohesion.")
    if not notes:
        notes.append("No simple maintainability marker triggered.")
    return max(score, 0), notes


def score_context_surface(items: list[DiffItem]) -> tuple[int, list[str]]:
    if not items:
        return 8, ["No diff detected."]
    docs_or_skills = sum(
        1
        for item in items
        if item.path.startswith("docs/") or item.path.startswith("skills/") or item.path in {"README.md", "CLAUDE.md"}
    )
    score = 10
    notes = [f"{docs_or_skills} docs/skill/rule file(s) changed."]
    if docs_or_skills > 8:
        score -= 4
        notes.append("Large instruction surface changed; validate discovery carefully.")
    elif docs_or_skills > 4:
        score -= 2
        notes.append("Moderate instruction surface changed.")
    return max(score, 0), notes


def load_candidates(root: Path) -> list[dict[str, Any]]:
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


def proposals(
    root: Path,
    missing: list[dict[str, Any]],
    live_skill_search: bool = False,
    include_cli: bool = False,
    search_timeout: int = 8,
    search_limit: int = 5,
) -> list[dict[str, Any]]:
    candidates = load_candidates(root)
    output: list[dict[str, Any]] = []
    for gap in missing:
        cap = gap["capability"]
        matches = [item for item in candidates if item.get("capability") in {cap, "skill-discovery", "skill-library"}]
        search = f"https://github.com/search?q=claude+code+{cap}+skill&type=repositories&s=stars&o=desc"
        proposal = {
            "capability": cap,
            "requires_user_approval": True,
            "github_search": search,
            "candidates": matches[:4],
        }
        if live_skill_search and search_for_capability is not None:
            proposal["live_discovery"] = search_for_capability(
                root,
                cap,
                limit=search_limit,
                timeout=search_timeout,
                include_cli=include_cli,
            )
        output.append(proposal)
    return output


def status_for(total: int) -> str:
    if total >= 85:
        return "pass"
    if total >= 70:
        return "review"
    return "fail"


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    root = args.root.resolve()
    diff_command, items = diff_items(root, args.base, args.head)
    explicit = parse_required(args.required)
    required = explicit or infer_capabilities(items)

    containment, containment_notes = score_change_containment(items)
    verification, verification_notes = score_verification(args.evidence or [])
    capability, capability_notes, missing = score_capabilities(root, required, args.skills_dir)
    maintainability, maintainability_notes = score_maintainability(root, items)
    context, context_notes = score_context_surface(items)

    total = containment + verification + capability + maintainability + context
    return {
        "root": str(root),
        "diff_command": diff_command,
        "changed_files": [item.__dict__ for item in items],
        "required_capabilities": sorted(required),
        "scores": {
            "change_containment": containment,
            "verification_evidence": verification,
            "capability_coverage": capability,
            "maintainability": maintainability,
            "context_surface": context,
            "total": total,
            "status": status_for(total),
        },
        "notes": {
            "change_containment": containment_notes,
            "verification_evidence": verification_notes,
            "capability_coverage": capability_notes,
            "maintainability": maintainability_notes,
            "context_surface": context_notes,
        },
        "capability_gaps": missing,
        "external_skill_policy": {
            "search_github_first": True,
            "requires_user_approval_before_import": True,
            "validate_after_import": True,
        },
        "external_skill_proposals": proposals(
            root,
            missing,
            live_skill_search=args.live_skill_search,
            include_cli=args.include_cli,
            search_timeout=args.search_timeout,
            search_limit=args.search_limit,
        ),
    }


def parse_required(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def markdown(report: dict[str, Any]) -> str:
    scores = report["scores"]
    lines = [
        "# Vibe Run Score",
        "",
        f"Status: **{scores['status']}**",
        f"Total: **{scores['total']}/100**",
        f"Diff: `{report['diff_command']}`",
        "",
        "| Dimension | Score |",
        "| --- | ---: |",
        f"| Change containment | {scores['change_containment']}/25 |",
        f"| Verification evidence | {scores['verification_evidence']}/25 |",
        f"| Capability coverage | {scores['capability_coverage']}/20 |",
        f"| Maintainability | {scores['maintainability']}/20 |",
        f"| Context surface | {scores['context_surface']}/10 |",
        "",
        "## Notes",
    ]
    for key, values in report["notes"].items():
        lines.append(f"- {key}: " + " ".join(values))
    if report["capability_gaps"]:
        lines.extend(["", "## Capability Gaps"])
        for proposal in report["external_skill_proposals"]:
            lines.append(f"- {proposal['capability']}: search {proposal['github_search']}")
            for candidate in proposal["candidates"]:
                lines.append(f"  - {candidate['repo']}: {candidate['why']}")
            live = proposal.get("live_discovery")
            if live:
                for candidate in live.get("github_candidates", [])[:3]:
                    if "error" in candidate:
                        lines.append(f"  - GitHub live search error: {candidate['error']}")
                    else:
                        lines.append(
                            f"  - {candidate.get('repo')}: {candidate.get('stars')} stars, "
                            f"{candidate.get('url')}"
                        )
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project/repository root to score.")
    parser.add_argument(
        "--skills-dir",
        type=Path,
        help="Skill directory to use for capability coverage. Defaults to project and common host skill dirs.",
    )
    parser.add_argument("--base", help="Git diff base, for example origin/master or HEAD~1.")
    parser.add_argument("--head", help="Git diff head when --base is supplied.")
    parser.add_argument("--required", help="Comma-separated required capabilities.")
    parser.add_argument("--evidence", action="append", type=Path, help="Evidence log/report path. Repeatable.")
    parser.add_argument(
        "--live-skill-search",
        action="store_true",
        help="When capability gaps exist, query GitHub for high-star skill candidates.",
    )
    parser.add_argument(
        "--include-cli",
        action="store_true",
        help="Also try findskill-compatible CLIs such as npx skills find and npx clawhub search.",
    )
    parser.add_argument("--search-timeout", type=int, default=8)
    parser.add_argument("--search-limit", type=int, default=5)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    report = build_report(args)
    text = json.dumps(report, indent=2) if args.json or not args.markdown else markdown(report)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text)
    return 0 if report["scores"]["status"] != "fail" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
