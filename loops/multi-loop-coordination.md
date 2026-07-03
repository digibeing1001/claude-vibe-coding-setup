# 多 Loop 协调

多个 loop 同时运行时，必须有优先级、碰撞检测、共享 inbox，否则会互相覆盖、抢占资源、通知淹没人类。

## 优先级表

当多个 loop 同时可行动时，按优先级决定谁先跑：

| 优先级 | Loop | 理由 |
| --- | --- | --- |
| P0 | ci-sweeper | CI 失败阻塞所有人，最高优先 |
| P1 | pr-babysitter | PR 卡住影响交付节奏 |
| P2 | dependency-sweeper | 依赖漏洞有安全风险 |
| P3 | post-merge-cleanup | 合并后清理，off-peak 跑 |
| P4 | daily-triage | 报告类，不紧急 |
| P5 | issue-triage | 提案类，不紧急 |
| P6 | changelog-drafter | 文档类，最低优先 |

### 优先级规则

- 高优先级 loop 可抢占低优先级的子 agent（不是抢占主调度）
- 同优先级按 FIFO（先触发的先跑）
- 所有 loop 都受各自预算约束，优先级不绕过预算
- 人类可手动提升任一 loop 的优先级（写入 STATE.md 的 override 字段）

## 碰撞检测

多个 action loop 可能操作同一 branch/PR，必须检测碰撞。

### acting_on 字段

每个 action loop 在 STATE.md 写入 `acting_on` 字段：

```markdown
## Current Action
acting_on: branch/fix-ci-failure-123
acting_since: 2026-07-03T14:30:00+08:00
```

### spawn 前检查

任何 action loop 在 spawn 子 agent 前必须：

1. 读所有其他 loop 的 STATE.md
2. 提取各自的 `acting_on` 字段
3. 如果目标 branch/PR 与任一正在行动的 loop 冲突：
   - skip 本轮
   - log "collision with <other_loop> on <branch>"
   - 下一轮再试

### 碰撞日志

碰撞记录在 loop-run-log.md：

```markdown
## Run <run_id>
- Time: ...
- Pattern: ci-sweeper
- Outcome: skipped
- Reason: collision with pr-babysitter on branch/fix-ci-failure-123
- Retry: next cycle
```

## 共享 Human Inbox

所有 loop 的升级通知进入共享 inbox，避免人类被多个 loop 分别通知淹没。

### 共享 STATE.md 的 High Priority 区

```markdown
# Loop State

## High Priority (waiting on human)
- [ci-sweeper] branch/fix-ci-failure-123 — waiting since 2026-07-03 14:30 — CI 失败根因不明
- [pr-babysitter] PR #456 — waiting since 2026-07-03 15:00 — merge conflict 需人工解决
- [dependency-sweeper] CVE-2026-1234 — waiting since 2026-07-03 16:00 — 需升级 major 版本
```

### 通知去重

同一 branch/PR/issue 的多个 loop 升级合并为一条通知：

```text
[Loop Escalation] branch/fix-ci-failure-123
- ci-sweeper: CI 失败根因不明
- pr-babysitter: 同一 PR 的 merge conflict
Action needed: <链接>
```

### >24h 告警

High Priority 区任一项 waiting >24h，触发告警：

```text
[Loop Overdue] <项> has been waiting for <hours>h
Loop: <pattern>
Branch/PR: <acting_on>
Reason: <原因>
```

## 共享 loop-run-log.md

所有 loop 共享一个 loop-run-log.md，追加式记录：

```markdown
# Loop Run Log

## Run a1b2c3
- Time: 2026-07-03 14:00-14:05
- Pattern: ci-sweeper
- Branch: fix-ci-failure-123
- Outcome: complete
- Tokens: 12,000

## Run d4e5f6
- Time: 2026-07-03 14:10-14:15
- Pattern: pr-babysitter
- PR: #456
- Outcome: skipped (collision)
- Tokens: 500

## Run g7h8i9
- Time: 2026-07-03 14:20-14:30
- Pattern: daily-triage
- Outcome: complete
- Tokens: 8,000
```

这个文件用于跨 loop 分析趋势，不是用来重放历史。

## 多 loop 状态布局

每个 loop 模式独立 state 文件，共享 run log：

```
.agent/
├── state/
│   ├── STATE.md                    # 主状态文件（共享 High Priority 区）
│   ├── loop-run-log.md             # 共享运行历史
│   ├── daily-triage.state.md       # 各模式独立 state
│   ├── ci-sweeper.state.md
│   ├── pr-babysitter.state.md
│   ├── issue-triage.state.md
│   └── ...
├── runs/
│   └── <run_id>/
│       └── ...
```

## 资源隔离

多 loop 共享资源时需隔离：

### Worktree 隔离

每个 action loop 在独立 worktree 跑：

```bash
git worktree add ../loop-ci-sweeper-<run_id> <branch>
git worktree add ../loop-pr-babysitter-<run_id> <branch>
```

避免互相污染工作目录。

### 预算隔离

每个 loop 有独立预算，不共享：

```markdown
| Loop | Max tokens/day |
| --- | --- |
| ci-sweeper | 200,000 |
| pr-babysitter | 150,000 |
```

ci-sweeper 耗尽预算不影响 pr-babysitter。

### 通知隔离

每个 loop 的通知带 `[<pattern>]` 前缀，人类可快速识别来源：

```text
[ci-sweeper] CI 失败 on branch/fix-ci-failure-123
[pr-babysitter] PR #456 merge conflict
```

## 协调失败模式

| 失败 | 症状 | 修复 |
| --- | --- | --- |
| 优先级失效 | 低优先级抢占了高优先级资源 | 检查优先级表，spawn 前读其他 state |
| 碰撞未检测 | 两个 loop 改同一文件 | acting_on 字段必须配置，spawn 前必读 |
| 通知风暴 | 人类被多个 loop 轮番通知 | 共享 inbox + 去重 + >24h 告警 |
| 预算互相影响 | 一个 loop 耗尽预算影响其他 | 预算隔离，每 loop 独立预算 |
| worktree 冲突 | 两 loop 在同一 worktree 跑 | 强制每 action loop 独立 worktree |
