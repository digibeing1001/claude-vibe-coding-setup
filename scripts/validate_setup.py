#!/usr/bin/env python3
"""Validate the portable Vibe Coding skill bundle.

The script intentionally avoids third-party dependencies so it can run inside
Claude Code, Codex, Hermes, OpenClaw, CI, or a fresh user machine.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


NAME_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def exact_child(directory: Path, name: str) -> Path | None:
    try:
        for child in directory.iterdir():
            if child.name == name:
                return child
    except FileNotFoundError:
        return None
    return None


def run_git(args: list[str], cwd: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", *args],
            cwd=str(cwd),
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return ""


def gitlink_paths(root: Path) -> set[str]:
    output = run_git(["ls-files", "--stage", "skills"], root)
    paths: set[str] = set()
    for line in output.splitlines():
        parts = line.split()
        if len(parts) >= 4 and parts[0] == "160000":
            paths.add(parts[3].replace("\\", "/"))
    return paths


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues: list[str] = []
    if not lines or lines[0].strip() != "---":
        return {}, ["missing_yaml_frontmatter"]
    end = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end = index
            break
    if end is None:
        return {}, ["unterminated_yaml_frontmatter"]

    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith(" ") or line.startswith("\t"):
            continue
        if ":" not in line:
            issues.append(f"unparsed_frontmatter_line:{line[:40]}")
            continue
        key, value = line.split(":", 1)
        value = value.strip().strip('"').strip("'")
        data[key.strip()] = value
    return data, issues


def validate_skill(skill_dir: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": skill_dir.name,
        "path": str(skill_dir),
        "status": "ok",
        "errors": [],
        "warnings": [],
        "notices": [],
    }
    skill_file = exact_child(skill_dir, "SKILL.md")
    if skill_file is None:
        variants = [
            child.name
            for child in skill_dir.iterdir()
            if child.is_file() and child.name.lower() == "skill.md"
        ]
        if variants:
            result["errors"].append(f"non_standard_skill_filename:{','.join(variants)}")
        else:
            result["errors"].append("missing_SKILL.md")
        result["status"] = "error"
        return result

    try:
        data, issues = parse_frontmatter(skill_file)
    except UnicodeDecodeError:
        result["errors"].append("not_utf8")
        result["status"] = "error"
        return result

    result["warnings"].extend(issues)
    skill_name = data.get("name", "")
    description = data.get("description", "")

    if not skill_name:
        result["errors"].append("missing_frontmatter_name")
    elif not NAME_RE.match(skill_name):
        result["errors"].append(f"invalid_frontmatter_name:{skill_name}")
    elif skill_name != skill_dir.name:
        result["warnings"].append(f"name_differs_from_directory:{skill_name}")

    if not description:
        result["errors"].append("missing_frontmatter_description")
    elif len(description.split()) > 120:
        result["warnings"].append("long_frontmatter_description")

    extras = sorted(set(data) - {"name", "description"})
    if extras:
        result["notices"].append("ignored_extra_frontmatter_keys:" + ",".join(extras))

    if result["errors"]:
        result["status"] = "error"
    elif result["warnings"]:
        result["status"] = "warning"
    return result


def validate(root: Path) -> dict[str, Any]:
    skills_dir = root / "skills"
    gitlinks = gitlink_paths(root)
    results = []
    for child in sorted(skills_dir.iterdir(), key=lambda p: p.name.lower()):
        if not child.is_dir():
            continue
        rel = child.relative_to(root).as_posix()
        if rel in gitlinks:
            results.append(
                {
                    "name": child.name,
                    "path": str(child),
                    "status": "error",
                    "errors": ["gitlink_skill_directory"],
                    "warnings": [],
                    "notices": [],
                }
            )
            continue
        results.append(validate_skill(child))

    errors = [item for item in results if item["status"] == "error"]
    warnings = [item for item in results if item["status"] == "warning"]
    notices = [item for item in results if item["notices"]]
    return {
        "root": str(root),
        "skill_count": len(results),
        "ok_count": len([item for item in results if item["status"] == "ok"]),
        "warning_count": len(warnings),
        "error_count": len(errors),
        "notice_count": len(notices),
        "skills": results,
    }


def print_text(report: dict[str, Any]) -> None:
    print("Vibe Coding setup validation")
    print("=" * 30)
    print(f"Root: {report['root']}")
    print(f"Skills: {report['skill_count']}")
    print(f"OK: {report['ok_count']}")
    print(f"Warnings: {report['warning_count']}")
    print(f"Errors: {report['error_count']}")
    print(f"Notices: {report['notice_count']}")
    print()
    for item in report["skills"]:
        if item["status"] == "ok":
            continue
        print(f"[{item['status'].upper()}] {item['name']}")
        for err in item["errors"]:
            print(f"  error: {err}")
        for warning in item["warnings"]:
            print(f"  warning: {warning}")
        for notice in item["notices"]:
            print(f"  notice: {notice}")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=repo_root())
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    parser.add_argument("--output", type=Path, help="Write JSON report to a file.")
    parser.add_argument("--warnings-fail", action="store_true")
    args = parser.parse_args(argv)

    report = validate(args.root.resolve())
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_text(report)

    if report["error_count"] > 0:
        return 1
    if args.warnings_fail and report["warning_count"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
