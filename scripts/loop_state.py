#!/usr/bin/env python3
"""Loop state management CLI.

Reads, writes, prunes, and recovers loop state. Manages STATE.md,
loop-run-log.md, and checkpoints. Intentionally dependency-free.

Usage:
    python scripts/loop_state.py read
    python scripts/loop_state.py write --pattern daily-triage --outcome complete
    python scripts/loop_state.py prune
    python scripts/loop_state.py checkpoint --run-id <uuid>
    python scripts/loop_state.py recover --run-id <uuid>
    python scripts/loop_state.py append-log --pattern ci-sweeper --outcome complete --tokens 12000
    python scripts/loop_state.py init
"""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

STATE_TEMPLATE = """# Loop State

Last run: {timestamp}
Run ID: {run_id}
Pattern: {pattern}
Readiness: L1

## Goal
<mechanically verifiable goal for this loop>

## Acceptance Criteria
- [ ] <criterion 1>

## High Priority (waiting on human)
<!-- items waiting on human, with waiting-since time -->

## Watch List
<!-- items being watched, with last action -->

## Recent Noise (pruned next run)
<!-- noise items, pruned next run -->

## Current Evidence
<command output / observations / test results from this round>

## Decisions
<!-- decision / reason / time -->

## Failed Attempts
<!-- attempt / root cause hypothesis / retryable? -->

## Next Smallest Step
<one smallest next step>

## Post-Run Critique
- High noise items:
- False positives:
- Should downgrade:
- One improvement for next run:
"""

RUN_LOG_HEADER = """# Loop Run Log

Append-only run history across all loops. Each run appends one entry.
"""


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def state_dir() -> Path:
    return repo_root() / ".agent" / "state"


def runs_dir() -> Path:
    return repo_root() / ".agent" / "runs"


def state_file(pattern: str | None = None) -> Path:
    if pattern:
        return state_dir() / f"{pattern}.state.md"
    return state_dir() / "STATE.md"


def run_log_file() -> Path:
    return state_dir() / "loop-run-log.md"


def checkpoints_dir(run_id: str) -> Path:
    return runs_dir() / run_id / "checkpoints"


def ensure_dirs() -> None:
    state_dir().mkdir(parents=True, exist_ok=True)
    runs_dir().mkdir(parents=True, exist_ok=True)


def cmd_init(args: argparse.Namespace) -> int:
    ensure_dirs()
    sf = state_file()
    if not sf.exists():
        run_id = str(uuid.uuid4())[:8]
        sf.write_text(
            STATE_TEMPLATE.format(timestamp=now_iso(), run_id=run_id, pattern="<pattern>"),
            encoding="utf-8",
        )
        print(f"Initialized {sf}")
    else:
        print(f"Already exists: {sf}")
    rl = run_log_file()
    if not rl.exists():
        rl.write_text(RUN_LOG_HEADER, encoding="utf-8")
        print(f"Initialized {rl}")
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    sf = state_file(args.pattern)
    if not sf.exists():
        print(f"State file not found: {sf}", file=sys.stderr)
        return 1
    print(sf.read_text(encoding="utf-8"))
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    ensure_dirs()
    sf = state_file(args.pattern)
    run_id = str(uuid.uuid4())[:8]
    if args.run_id:
        run_id = args.run_id
    content = STATE_TEMPLATE.format(timestamp=now_iso(), run_id=run_id, pattern=args.pattern)
    if args.goal:
        content = content.replace("<mechanically verifiable goal for this loop>", args.goal)
    if args.outcome:
        # Record the exit outcome in the state spine so the next Context node
        # and post-loop hooks can read it without re-parsing the run log.
        outcome_line = f"\n## Last Outcome\n{args.outcome}\n"
        if "## Last Outcome" not in content:
            content = content.rstrip() + "\n" + outcome_line
        else:
            import re
            content = re.sub(
                r"## Last Outcome\n.*?(?=\n## |\Z)",
                f"## Last Outcome\n{args.outcome}\n",
                content,
                flags=re.DOTALL,
            )
    if args.critique_required:
        content = content.rstrip() + "\n\n## Critique Required\ntrue\n"
    sf.write_text(content, encoding="utf-8")
    print(f"Wrote {sf}")
    return 0


def cmd_prune(args: argparse.Namespace) -> int:
    sf = state_file(args.pattern)
    if not sf.exists():
        print(f"State file not found: {sf}", file=sys.stderr)
        return 1
    content = sf.read_text(encoding="utf-8")
    lines = content.splitlines()
    out = []
    in_noise = False
    noise_count = 0
    for line in lines:
        if line.strip().startswith("## Recent Noise"):
            in_noise = True
            out.append(line)
            out.append("<!-- pruned -->")
            continue
        if in_noise and line.strip().startswith("## "):
            in_noise = False
        if in_noise:
            stripped = line.strip()
            if stripped and not stripped.startswith("<!--") and not stripped.startswith("#"):
                noise_count += 1
                continue
        out.append(line)
    sf.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Pruned {noise_count} noise items from {sf}")
    return 0


def cmd_append_log(args: argparse.Namespace) -> int:
    ensure_dirs()
    rl = run_log_file()
    if not rl.exists():
        rl.write_text(RUN_LOG_HEADER, encoding="utf-8")
    run_id = str(uuid.uuid4())[:8]
    entry = f"""
## Run {run_id}
- Time: {now_iso()}
- Pattern: {args.pattern}
- Outcome: {args.outcome}
- Tokens: {args.tokens if args.tokens else "unknown"}
- Duration: {args.duration if args.duration else "unknown"}
- Notes: {args.notes if args.notes else ""}
"""
    with rl.open("a", encoding="utf-8") as f:
        f.write(entry)
    print(f"Appended run {run_id} to {rl}")
    return 0


def cmd_checkpoint(args: argparse.Namespace) -> int:
    ensure_dirs()
    cp_dir = checkpoints_dir(args.run_id)
    cp_dir.mkdir(parents=True, exist_ok=True)
    sf = state_file(args.pattern)
    state_content = sf.read_text(encoding="utf-8") if sf.exists() else ""
    cp = {
        "run_id": args.run_id,
        "timestamp": now_iso(),
        "pattern": args.pattern or "unknown",
        "state_content": state_content,
    }
    cp_path = cp_dir / f"cp-{datetime.now().strftime('%H%M%S')}.json"
    cp_path.write_text(json.dumps(cp, indent=2, ensure_ascii=False), encoding="utf-8")
    current = cp_dir / "current.json"
    current.write_text(json.dumps(cp, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Checkpoint written: {cp_path}")
    return 0


def cmd_recover(args: argparse.Namespace) -> int:
    cp_dir = checkpoints_dir(args.run_id)
    current = cp_dir / "current.json"
    if not current.exists():
        print(f"No checkpoint found for run {args.run_id}", file=sys.stderr)
        return 1
    cp = json.loads(current.read_text(encoding="utf-8"))
    pattern = cp.get("pattern", "unknown")
    sf = state_file(pattern)
    state_content = cp.get("state_content", "")
    if state_content:
        sf.write_text(state_content, encoding="utf-8")
        print(f"Recovered state for pattern '{pattern}' from checkpoint")
    else:
        print("Checkpoint has no state content", file=sys.stderr)
        return 1
    print(f"Next loop round must run Context node to verify state.")
    return 0


def cmd_kill_switch(args: argparse.Namespace) -> int:
    sf = state_file()
    if not sf.exists():
        print("No STATE.md found. Run 'init' first.", file=sys.stderr)
        return 1
    content = sf.read_text(encoding="utf-8")
    if "## Kill Switch" not in content:
        content += "\n## Kill Switch\nstatus: ACTIVE\nreason: \npaused_at: \n"
    lines = content.splitlines()
    out = []
    in_ks = False
    for line in lines:
        if line.strip().startswith("## Kill Switch"):
            in_ks = True
            out.append(line)
            out.append(f"status: {'PAUSED' if args.pause else 'ACTIVE'}")
            if args.pause:
                out.append(f"reason: {args.reason or 'manual pause'}")
                out.append(f"paused_at: {now_iso()}")
            else:
                out.append("reason: ")
                out.append("paused_at: ")
            # skip existing ks lines
            continue
        if in_ks and line.strip().startswith("## "):
            in_ks = False
        if in_ks:
            continue
        out.append(line)
    sf.write_text("\n".join(out) + "\n", encoding="utf-8")
    status = "PAUSED" if args.pause else "ACTIVE"
    print(f"Kill switch set to {status}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop state management CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize state files")
    p_init.set_defaults(func=cmd_init)

    p_read = sub.add_parser("read", help="Read current state")
    p_read.add_argument("--pattern", help="Pattern-specific state file")
    p_read.set_defaults(func=cmd_read)

    p_write = sub.add_parser("write", help="Write state (after run)")
    p_write.add_argument("--pattern", required=True, help="Loop pattern")
    p_write.add_argument("--run-id", help="Run ID (auto-generated if omitted)")
    p_write.add_argument("--goal", help="Goal text")
    p_write.add_argument("--outcome", choices=["complete", "fail", "cancel", "budget_exhausted"], help="Exit outcome to record in STATE.md")
    p_write.add_argument("--critique-required", action="store_true", help="Mark critique_required=true in STATE.md")
    p_write.set_defaults(func=cmd_write)

    p_prune = sub.add_parser("prune", help="Prune resolved/noise items")
    p_prune.add_argument("--pattern", help="Pattern-specific state file")
    p_prune.set_defaults(func=cmd_prune)

    p_log = sub.add_parser("append-log", help="Append to run log")
    p_log.add_argument("--pattern", required=True)
    p_log.add_argument("--outcome", required=True, choices=["complete", "fail", "cancel", "budget_exhausted"])
    p_log.add_argument("--tokens", type=int)
    p_log.add_argument("--duration", help="Run duration (human-readable, e.g. '12m' or '2h30m')")
    p_log.add_argument("--notes")
    p_log.set_defaults(func=cmd_append_log)

    p_cp = sub.add_parser("checkpoint", help="Create checkpoint")
    p_cp.add_argument("--run-id", required=True)
    p_cp.add_argument("--pattern")
    p_cp.set_defaults(func=cmd_checkpoint)

    p_rec = sub.add_parser("recover", help="Recover from checkpoint")
    p_rec.add_argument("--run-id", required=True)
    p_rec.set_defaults(func=cmd_recover)

    p_ks = sub.add_parser("kill-switch", help="Set or clear kill switch")
    p_ks.add_argument("--pause", action="store_true", help="Pause all loops")
    p_ks.add_argument("--resume", action="store_true", help="Resume all loops")
    p_ks.add_argument("--reason", help="Pause reason")
    p_ks.set_defaults(func=cmd_kill_switch)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
