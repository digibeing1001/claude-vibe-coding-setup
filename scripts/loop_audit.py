#!/usr/bin/env python3
"""Loop readiness audit and cost estimator.

Scores a loop pattern against 18 readiness dimensions (100 points total) and
reports which readiness level (L1/L2/L3) it qualifies for. Also estimates
token cost before scheduling.

Intentionally heuristic and dependency-free. Not a replacement for human
review; it is a compact gate that makes the loop designer state what
guardrails exist and where gaps remain.

Usage:
    python scripts/loop_audit.py --pattern daily-triage --suggest --badge
    python scripts/loop_audit.py --estimate-cost --pattern ci-sweeper --items 5
    python scripts/loop_audit.py --list-patterns
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --- 18 readiness dimensions (100 points total) ---------------------------
# Each dimension: (name, max_score, L1_threshold, L2_threshold, L3_threshold)
DIMENSIONS = [
    ("goal_mechanically_verifiable", 8, 4, 6, 7),
    ("stop_conditions", 8, 4, 6, 7),
    ("state_md", 6, 3, 4, 5),
    ("checkpoints", 4, 0, 2, 3),
    ("maker_checker_separation", 8, 0, 6, 7),
    ("six_stage_verification", 6, 0, 4, 5),
    ("denylist", 6, 3, 5, 5),
    ("auto_merge_policy", 4, 0, 2, 4),
    ("mcp_minimal_permissions", 4, 2, 3, 4),
    ("budget_table", 6, 3, 5, 5),
    ("kill_switch", 6, 3, 5, 6),
    ("watchlist_early_exit", 4, 2, 3, 4),
    ("human_gates", 6, 3, 5, 6),
    ("multi_loop_coordination", 4, 0, 2, 4),
    ("post_run_critique", 4, 2, 3, 4),
    ("failure_modes_coverage", 6, 3, 4, 6),
    ("monitoring", 6, 2, 4, 6),
    ("rollback_procedure", 4, 1, 3, 4),
]

L1_THRESHOLD = 38
L2_THRESHOLD = 58
L3_THRESHOLD = 78

# --- Cost estimation baselines ---------------------------------------------
BASELINE_TOKENS = {
    "daily-triage": (2000, 3000),
    "ci-sweeper": (1500, 5000),
    "pr-babysitter": (1000, 4000),
    "issue-triage": (1500, 2000),
    "post-merge-cleanup": (1000, 2000),
    "localize-repair-validate": (3000, 0),
    "sequential-quality-loop": (5000, 0),
    "rfc-dag-loop": (8000, 3000),
    "parallel-generation-loop": (6000, 2000),
    "continuous-pr-loop": (7000, 2000),
}

DEFAULT_MODEL_RATE_PER_K = 0.01  # microunits per token; adjust per model


@dataclass
class DimensionScore:
    name: str
    max_score: int
    score: int
    l1_threshold: int
    l2_threshold: int
    l3_threshold: int

    def meets(self, level: str) -> bool:
        threshold = {"L1": self.l1_threshold, "L2": self.l2_threshold, "L3": self.l3_threshold}[level]
        return self.score >= threshold


@dataclass
class AuditResult:
    pattern: str
    dimensions: list[DimensionScore] = field(default_factory=list)
    total: int = 0

    def level(self) -> str:
        if self.total >= L3_THRESHOLD:
            return "L3 (Unattended)"
        if self.total >= L2_THRESHOLD:
            return "L2 (Assisted)"
        if self.total >= L1_THRESHOLD:
            return "L1 (Report)"
        return "L0 (Draft)"

    def meets(self, level: str) -> bool:
        threshold = {"L1": L1_THRESHOLD, "L2": L2_THRESHOLD, "L3": L3_THRESHOLD}[level]
        return self.total >= threshold

    def weak_dimensions(self, target_level: str) -> list[DimensionScore]:
        return [d for d in self.dimensions if not d.meets(target_level)]


def load_pattern_config(pattern: str, repo_root: Path) -> dict[str, Any]:
    """Load pattern-specific config if it exists."""
    config_path = repo_root / "config" / f"loop-{pattern}.json"
    if config_path.exists():
        try:
            return json.loads(config_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}


def score_dimension(name: str, config: dict[str, Any]) -> int:
    """Score a dimension based on config presence.

    This is heuristic — real scoring requires human review of the actual
    implementation. The script makes the designer state what exists.
    """
    # Map dimension names to config keys
    key_map = {
        "goal_mechanically_verifiable": "goal_verifiable",
        "stop_conditions": "stop_conditions",
        "state_md": "state_md",
        "checkpoints": "checkpoints",
        "maker_checker_separation": "maker_checker",
        "six_stage_verification": "six_stage_verification",
        "denylist": "denylist",
        "auto_merge_policy": "auto_merge_policy",
        "mcp_minimal_permissions": "mcp_permissions",
        "budget_table": "budget_table",
        "kill_switch": "kill_switch",
        "watchlist_early_exit": "watchlist_early_exit",
        "human_gates": "human_gates",
        "multi_loop_coordination": "multi_loop_coordination",
        "post_run_critique": "post_run_critique",
        "failure_modes_coverage": "failure_modes_covered",
        "monitoring": "monitoring",
        "rollback_procedure": "rollback",
    }
    key = key_map.get(name, name)
    value = config.get(key, 0)

    # If config provides an explicit score, use it (clamped to max)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, dict) and "score" in value:
        return int(value["score"])
    return 0


def audit_pattern(pattern: str, repo_root: Path) -> AuditResult:
    config = load_pattern_config(pattern, repo_root)
    result = AuditResult(pattern=pattern)
    for name, max_score, l1, l2, l3 in DIMENSIONS:
        raw = score_dimension(name, config)
        score = min(raw, max_score)
        result.dimensions.append(
            DimensionScore(
                name=name,
                max_score=max_score,
                score=score,
                l1_threshold=l1,
                l2_threshold=l2,
                l3_threshold=l3,
            )
        )
    result.total = sum(d.score for d in result.dimensions)
    return result


def estimate_cost(pattern: str, items: int) -> dict[str, int]:
    base, per_item = BASELINE_TOKENS.get(pattern, (3000, 2000))
    tokens = base + items * per_item
    cost_microunits = int(tokens * DEFAULT_MODEL_RATE_PER_K)
    return {
        "pattern": pattern,
        "items": items,
        "base_tokens": base,
        "per_item_tokens": per_item,
        "estimated_tokens": tokens,
        "estimated_cost_microunits": cost_microunits,
    }


def render_report(result: AuditResult, suggest: bool) -> str:
    lines = []
    lines.append(f"Loop: {result.pattern}")
    lines.append(f"Score: {result.total}/100")
    level = result.level()
    lines.append(f"Level: {level}")
    lines.append(
        f"  meets L1 ({L1_THRESHOLD}): {'yes' if result.meets('L1') else 'no'}  "
        f"L2 ({L2_THRESHOLD}): {'yes' if result.meets('L2') else 'no'}  "
        f"L3 ({L3_THRESHOLD}): {'yes' if result.meets('L3') else 'no'}"
    )
    lines.append("")
    lines.append("Dimensions:")
    for d in result.dimensions:
        marker = " "
        if d.score < d.l1_threshold:
            marker = "!"
        elif d.score < d.l2_threshold:
            marker = "."
        elif d.score < d.l3_threshold:
            marker = "-"
        else:
            marker = " "
        lines.append(f"  {marker} {d.name:<35} {d.score}/{d.max_score}")

    if suggest:
        target = "L3" if result.meets("L2") else ("L2" if result.meets("L1") else "L1")
        weak = result.weak_dimensions(target)
        if weak:
            lines.append("")
            lines.append(f"Weak dimensions (need {target}):")
            for d in weak:
                gap = (d.l3_threshold if target == "L3" else d.l2_threshold if target == "L2" else d.l1_threshold) - d.score
                lines.append(f"  - {d.name}: {d.score}/{d.max_score} (need +{gap} for {target})")
            lines.append("")
            lines.append("Suggested actions:")
            for d in weak:
                lines.append(f"  - Improve {d.name}")
        else:
            lines.append("")
            lines.append(f"All dimensions meet {target}. Consider next level.")
    return "\n".join(lines)


def render_badge(result: AuditResult) -> str:
    level = result.level().split(" ")[0]
    color = {"L0": "lightgrey", "L1": "green", "L2": "yellow", "L3": "orange"}.get(level, "lightgrey")
    return f"![Loop Readiness](https://img.shields.io/badge/loop-{level}-{color})"


def list_patterns(repo_root: Path) -> list[str]:
    patterns_dir = repo_root / "loops" / "patterns"
    if not patterns_dir.exists():
        return []
    return sorted(p.stem for p in patterns_dir.glob("*.md") if p.stem != "README")


def main() -> int:
    parser = argparse.ArgumentParser(description="Loop readiness audit and cost estimator")
    parser.add_argument("--pattern", help="Loop pattern to audit")
    parser.add_argument("--suggest", action="store_true", help="Suggest improvements for weak dimensions")
    parser.add_argument("--badge", action="store_true", help="Output a shields.io badge URL")
    parser.add_argument("--estimate-cost", action="store_true", help="Estimate token cost instead of auditing")
    parser.add_argument("--items", type=int, default=5, help="Number of items for cost estimation")
    parser.add_argument("--list-patterns", action="store_true", help="List available patterns")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()

    if args.list_patterns:
        patterns = list_patterns(repo_root)
        if args.json:
            print(json.dumps({"patterns": patterns}))
        else:
            for p in patterns:
                print(p)
        return 0

    if not args.pattern:
        parser.error("--pattern is required unless --list-patterns")

    if args.estimate_cost:
        cost = estimate_cost(args.pattern, args.items)
        if args.json:
            print(json.dumps(cost, indent=2))
        else:
            print(f"Pattern: {cost['pattern']}")
            print(f"Items: {cost['items']}")
            print(f"Base tokens: {cost['base_tokens']:,}")
            print(f"Per-item tokens: {cost['per_item_tokens']:,}")
            print(f"Estimated tokens: {cost['estimated_tokens']:,}")
            print(f"Estimated cost: {cost['estimated_cost_microunits']:,} microunits")
        return 0

    result = audit_pattern(args.pattern, repo_root)

    if args.badge:
        print(render_badge(result))
        return 0

    if args.json:
        out = {
            "pattern": result.pattern,
            "total": result.total,
            "level": result.level(),
            "meets_l1": result.meets("L1"),
            "meets_l2": result.meets("L2"),
            "meets_l3": result.meets("L3"),
            "dimensions": [
                {
                    "name": d.name,
                    "score": d.score,
                    "max": d.max_score,
                    "l1": d.l1_threshold,
                    "l2": d.l2_threshold,
                    "l3": d.l3_threshold,
                }
                for d in result.dimensions
            ],
        }
        print(json.dumps(out, indent=2))
    else:
        print(render_report(result, args.suggest))
    return 0


if __name__ == "__main__":
    sys.exit(main())
