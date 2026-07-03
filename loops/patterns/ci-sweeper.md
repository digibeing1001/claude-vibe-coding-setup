# CI Sweeper

定期扫描 CI 失败，自动修复明显问题。L2 默认——能改代码但不 auto-merge。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 5-15分钟 |
| 风险 | Medium |
| 默认就绪度 | L2 |
| 时间尺度 | 分钟 |
| 触发 | cron / CI webhook |

## 循环

```
Context: 加载 CI 状态 + 失败日志 + STATE.md
Decide:  判断哪些失败可自动修复
Act:     spawn 子 agent 修复（Maker）→ 验证（Checker）
Evaluate: 修复通过 + CI 重新跑绿
```

## 步骤

1. **Scan**——扫描所有 PR/branch 的 CI 状态
2. **Filter**——忽略 flaky test、已知问题、denylist 路径
3. **Classify**——判断根因（测试失败/类型错误/lint/依赖/环境）
4. **Decide**——可自动修复 vs 需人工
5. **Repair**——spawn Maker 修复 → Checker 验证
6. **Push**——push 修复到 PR branch
7. **Wait CI**——等 CI 重跑
8. **Critique**——写 Post-Run Critique

## 可自动修复的根因

| 根因 | 自动修复 | 备注 |
| --- | --- | --- |
| 测试断言失败 | 是（1次） | 测试文件 hash 不变 |
| 类型错误 | 是（1次） | |
| lint 错误 | 是（1次） | |
| import 排序 | 是（1次） | |
| 缺失依赖 | 是（1次） | 仅 patch 版本 |
| major 依赖升级 | 否 | wait_human |
| 环境问题 | 否 | wait_human |
| CI 配置问题 | 否 | wait_human（denylist） |
| 生产代码逻辑 bug | 是（1次） | 需 Checker 验证 |

## 预算

| 维度 | 默认 |
| --- | --- |
| Max runs/day | 96（15分钟一次） |
| Max tokens/day | 200,000 |
| Max sub-agent spawns/run | 3 |
| Max retries/cause | 2 |
| Max cost (microunits)/day | 1,000,000 |

## 停止条件

- CI 全绿 → `complete`
- 同 PR 修复 2 次仍失败 → `wait_human`
- 根因在 denylist → `wait_human`
- 超过预算 → `budget_exhausted`

## Watchlist 空→早退

```text
IF 所有 PR 的 CI 都是 green:
    早退，本轮 <5k token
    不 spawn 任何子 agent
ELSE:
    按优先级处理失败项
```

## Maker/Checker

- Maker：定位 + 修复
- Checker：在独立 worktree 跑失败命令 + 邻近测试
- CI 是最终 Checker（独立环境）

## 碰撞检测

```text
spawn 前:
  读所有其他 loop 的 STATE.md
  IF 任何 loop 的 acting_on == <当前 PR branch>:
    skip 本轮
    log "collision with <other_loop>"
    下一轮再试
```

## STATE.md

```markdown
## Goal
修复 CI 失败

## High Priority (waiting on human)
- PR #456 — major 依赖升级 — waiting since 14:00

## Watch List
- PR #123 — test failure — last action: 修复中 — acting_on: branch/fix-test

## Failed Attempts
- PR #123 attempt 1: 测试断言不对 → 修了断言 → 仍失败
- PR #123 attempt 2: 根因是 race condition → wait_human

## Post-Run Critique
- High noise: flaky test alert 5 次 → 加 flaky 检测
- False positives: 1（环境问题误判为代码问题）
- One improvement: 加环境问题识别规则
```
