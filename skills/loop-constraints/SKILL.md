---
name: loop-constraints
description: Loop safety guardrails enforced every run. Loads and checks Path Denylist (forbidden read/write/execute paths), auto-merge policy (default off, requires allowlist), MCP minimal permissions, and risk scoring (>=0.65 escalates to human). Use at every Context node to prevent over-reach, secret leakage, and production damage.
---

# Loop Constraints

Safety guardrails make "what loops cannot touch" an executable checklist, not advisory text. The faster loops run, the more they need hard constraints to prevent AI from touching high-sensitivity paths.

## When to Use

- Every loop's Context node (mandatory)
- Before any file read/write
- Before any command execution
- Before any PR merge
- Before any MCP connector call

## Three Guardrails

| Guardrail | Purpose | Enforcement |
| --- | --- | --- |
| Path Denylist | Forbid loop from reading/writing specific paths | Hard, violation stops loop |
| Auto-merge policy | Limit which changes can auto-merge | Default off; needs allowlist |
| MCP minimal permissions | Limit connector permissions | Enforced at config time |

## Path Denylist

Every loop must load and enforce the denylist at Context node. Hit → `wait_human`, no Act executes.

### Default Denylist

```yaml
# config/loop-denylist.yaml
denylist:
  read:
    - "**/.env"
    - "**/.env.*"
    - "**/secrets/**"
    - "**/credentials/**"
    - "**/*_key.*"
    - "**/*_secret.*"
    - "**/auth/**"
    - "**/.aws/credentials"
    - "**/.ssh/id_*"
  write:
    - "**/.env"
    - "**/.env.*"
    - "**/secrets/**"
    - "**/credentials/**"
    - "**/*_key.*"
    - "**/*_secret.*"
    - "**/auth/**"
    - "**/payments/**"
    - "**/billing/**"
    - "**/migrations/**"
    - "**/k8s/production/**"
    - "**/terraform/prod/**"
    - "**/.github/workflows/**"
  execute:
    - "rm -rf /"
    - "git push --force"
    - "git push --force-with-lease"
    - "DROP TABLE"
    - "DROP DATABASE"
    - "kubectl delete"
    - "terraform destroy"
    - "npm publish"
    - "docker push"
```

### Project-Level Extension

Projects may append in `.agent/loop-denylist.yaml`:

```yaml
denylist:
  write:
    - "src/core/payment/**"
    - "config/production/**"
```

### Loading Rules

- Default denylist from `config/loop-denylist.yaml`
- Project denylist from `.agent/loop-denylist.yaml`, merged with default
- Project can only append, cannot weaken default
- Merged denylist loaded at Context node, hash recorded in STATE.md

### Hit Handling

```text
IF AI's requested path/command hits denylist:
    transition to wait_human
    do not execute
    log: which rule, which path, which run
    notify human
```

## Auto-merge Policy

Auto-merge defaults to **off**. Enabling requires explicit allowlist, only for low-risk change types.

### Default: Off

```yaml
# config/loop-auto-merge.yaml
auto_merge:
  enabled: false
```

### Enable with Allowlist

```yaml
auto_merge:
  enabled: true
  allowlist:
    - "**/*.md"
    - "**/comments/**"
    - "**/lint/**"
    - "**/test/**"
    - "**/*.test.*"
    - "**/*.spec.*"
    - "**/import-order/**"
  denylist:
    - "**/package.json"
    - "**/package-lock.json"
    - "**/yarn.lock"
    - "**/Cargo.lock"
    - "**/go.mod"
    - "**/go.sum"
    - "**/.github/workflows/**"
    - "**/migrations/**"
    - "config/loop-denylist.yaml"
    - "config/loop-auto-merge.yaml"
```

### Behavior Changes Forbidden

Allowlist covers **non-behavior changes only**. Any runtime behavior change (even if path is in allowlist) forbids auto-merge.

Judgment rules:
- Edited `.test.ts` but only formatting → can auto-merge
- Edited `.test.ts` but changed assertion logic → cannot auto-merge (behavior change)
- Edited `.md` but only typo → can auto-merge
- Edited `.md` but changed API doc parameters → cannot auto-merge (may mislead callers)

## MCP Minimal Permissions

MCP connectors must be configured with minimal permissions; loops cannot get more than they need.

### GitHub connector

```yaml
github:
  permissions:
    contents: read
    pull_requests: write
    issues: write
    actions: read
    # forbidden: administration, delete_repo, security_events
  auto_merge: false
  allowed_repos:
    - "org/repo-1"
    - "org/repo-2"
```

### Slack connector

```yaml
slack:
  permissions:
    post_messages: true
  allowed_channels:
    - "#loop-escalations"
  # forbidden: read_messages, delete_messages, invite_users
```

### Database connector

```yaml
database:
  production:
    enabled: false
  staging:
    permissions:
      read: true
      write: false
      ddl: false
```

## Risk Scoring

High-risk actions require human confirmation. Risk scoring by:

| Risk class | Threshold | Examples |
| --- | --- | --- |
| Irreversible | 0.8+ | Deletions, production deploys, DB migrations |
| High-impact | 0.65+ | Core transaction logic, auth flows, payment flows |
| Cross-service | 0.6+ | API contracts, shared libraries, DB schema |
| Reversible but broad | 0.5+ | CI config, dependency versions, build config |
| Reversible and local | <0.5 | Business code, tests, docs |

Risk score >= 0.65 → `wait_human`.

### Calculation

```text
risk_score = max(
  irreversibility,
  blast_radius,
  cross_service ? 0.6 : 0
)
```

## Every-Run Checklist

`loop-constraints` enforces at every Context node:

1. Load merged denylist
2. Verify denylist hash unchanged
3. Load auto-merge config
4. Load MCP permission config
5. Check all paths/commands for this round against denylist
6. Risk-score all actions for this round
7. Hit denylist or risk >= 0.65 → transition to `wait_human`

AI cannot skip `loop-constraints` checks.

## Integration with Controller

```text
Context node:
  1. Run loop-constraints checks
  2. IF any check fails:
       transition to wait_human
       do not proceed to Act
  3. ELSE:
       proceed to Decide/Act
```

Full spec: [`loops/safety-guardrails.md`](../../loops/safety-guardrails.md)
