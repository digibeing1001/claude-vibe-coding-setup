#!/usr/bin/env python3
"""Install the Vibe Coding bundle into common coding-agent hosts."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class HostProfile:
    name: str
    base_dir: Path
    skills_dir: Path
    rules_file: Path | None
    hooks_dir: Path | None


def home() -> Path:
    return Path.home()


def profiles() -> dict[str, HostProfile]:
    h = home()
    return {
        "codex": HostProfile(
            "codex",
            h / ".codex",
            h / ".codex" / "skills",
            h / ".codex" / "vibe-coding" / "CLAUDE.md",
            None,
        ),
        "claude": HostProfile(
            "claude",
            h / ".claude",
            h / ".claude" / "skills",
            h / ".claude" / "CLAUDE.md",
            h / ".claude" / "hooks",
        ),
        "hermes": HostProfile(
            "hermes",
            h / ".hermes",
            h / ".hermes" / "skills",
            h / ".hermes" / "vibe-coding" / "CLAUDE.md",
            h / ".hermes" / "hooks",
        ),
        "openclaw": HostProfile(
            "openclaw",
            h / ".openclaw",
            h / ".openclaw" / "skills",
            h / ".openclaw" / "vibe-coding" / "CLAUDE.md",
            h / ".openclaw" / "hooks",
        ),
    }


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


def iter_skill_dirs(source: Path) -> Iterable[Path]:
    skills_dir = source / "skills"
    for child in sorted(skills_dir.iterdir(), key=lambda p: p.name.lower()):
        if child.is_dir() and exact_child(child, "SKILL.md"):
            yield child


def safe_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def copy_dir(source: Path, target: Path, backup_dir: Path, mode: str, dry_run: bool) -> str:
    if target.exists():
        if mode == "preserve":
            return "skipped"
        if mode != "overwrite":
            raise ValueError(f"Unsupported mode: {mode}")
        if not safe_under(target, target.parent):
            raise RuntimeError(f"Refusing to overwrite unsafe target: {target}")
        backup_target = backup_dir / "skills" / target.name
        if not dry_run:
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            if backup_target.exists():
                if backup_target.is_dir():
                    shutil.rmtree(backup_target)
                else:
                    backup_target.unlink()
            if target.is_dir():
                shutil.copytree(target, backup_target)
                shutil.rmtree(target)
            else:
                shutil.copy2(target, backup_target)
                target.unlink()
            shutil.copytree(source, target)
        return "overwritten"

    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target)
    return "installed"


def copy_file(source: Path, target: Path, backup_dir: Path, mode: str, dry_run: bool) -> str:
    if target.exists():
        if mode == "preserve":
            return "skipped"
        backup_target = backup_dir / "files" / target.name
        if not dry_run:
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_target)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        return "overwritten"

    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return "installed"


def install_host(
    source: Path,
    profile: HostProfile,
    mode: str,
    install_rules: bool,
    install_hooks: bool,
    dry_run: bool,
) -> dict[str, object]:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = profile.base_dir / "backups" / f"vibe-coding-setup-{stamp}"
    counts = {"installed": 0, "skipped": 0, "overwritten": 0}
    details: list[dict[str, str]] = []

    for skill_dir in iter_skill_dirs(source):
        target = profile.skills_dir / skill_dir.name
        status = copy_dir(skill_dir, target, backup_dir, mode, dry_run)
        counts[status] += 1
        details.append({"kind": "skill", "name": skill_dir.name, "status": status})

    files: list[tuple[str, Path, Path | None]] = []
    if install_rules and profile.rules_file:
        files.append(("rules", source / "CLAUDE.md", profile.rules_file))

    if install_hooks and profile.hooks_dir:
        hooks_source = source / "hooks"
        for hook in sorted(hooks_source.glob("*")):
            if hook.is_file():
                files.append(("hook", hook, profile.hooks_dir / hook.name))

    file_details = []
    for kind, src, target in files:
        if target is None or not src.exists():
            continue
        status = copy_file(src, target, backup_dir, mode, dry_run)
        file_details.append({"kind": kind, "name": target.name, "status": status})

    return {
        "host": profile.name,
        "base_dir": str(profile.base_dir),
        "skills_dir": str(profile.skills_dir),
        "mode": mode,
        "dry_run": dry_run,
        "backup_dir": str(backup_dir),
        "skill_counts": counts,
        "skills": details,
        "files": file_details,
    }


def main(argv: list[str]) -> int:
    profile_map = profiles()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=repo_root())
    parser.add_argument(
        "--host",
        action="append",
        choices=[*profile_map.keys(), "all"],
        default=None,
        help="Target host. Repeatable. Defaults to codex.",
    )
    parser.add_argument("--mode", choices=["preserve", "overwrite"], default="preserve")
    parser.add_argument("--install-rules", action="store_true")
    parser.add_argument("--install-hooks", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    requested = args.host or ["codex"]
    hosts: list[str] = []
    for item in requested:
        if item == "all":
            hosts.extend(profile_map)
        else:
            hosts.append(item)
    hosts = list(dict.fromkeys(hosts))

    reports = [
        install_host(
            args.source.resolve(),
            profile_map[name],
            args.mode,
            args.install_rules,
            args.install_hooks,
            args.dry_run,
        )
        for name in hosts
    ]

    if args.json:
        print(json.dumps({"hosts": reports}, indent=2))
    else:
        print("Vibe Coding universal installer")
        print("=" * 31)
        for report in reports:
            counts = report["skill_counts"]
            print(f"Host: {report['host']}")
            print(f"  skills: {report['skills_dir']}")
            print(
                "  installed={installed} skipped={skipped} overwritten={overwritten}".format(
                    **counts
                )
            )
            if report["files"]:
                file_summary = ", ".join(
                    f"{item['kind']}:{item['status']}" for item in report["files"]
                )
                print(f"  files: {file_summary}")
            print(f"  backup: {report['backup_dir']}")
        print()
        print("Use --mode overwrite only after reviewing the backup path above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
