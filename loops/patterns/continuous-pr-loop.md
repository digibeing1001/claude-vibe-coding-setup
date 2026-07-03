# Continuous PR Loop

用于 PR/CI/部署自动化。仅当 CI 和仓库权限就绪时使用。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 分钟-小时 |
| 风险 | Medium |
| 默认就绪度 | L2 |
| 时间尺度 | 分钟-小时 |
| 触发 | 需要自动创建/修复 PR / CI 失败自动修 |

## 循环

```
Context: 加载 PR 状态 + CI 日志 + 预算
Decide:  判断是否值得修复（vs 升级人工）
Act:     在隔离 branch/worktree 实现一个 PR 大小的迭代
Evaluate: 本地质量门通过 + push + CI 通过
```

## 步骤

1. **Isolate**——创建隔离 branch/worktree
2. **Implement**——实现一个 PR 大小的迭代
3. **Local gates**——跑本地质量门（build/type/lint/test）
4. **Push**——push 并等 CI
5. **Repair**——把失败 CI 日志喂给一次修复尝试
6. **Stop**——超过重试预算就停

## 预算

| 维度 | 默认 |
| --- | --- |
| Max iterations | 1（单 PR 单次迭代） |
| Max retries/cause | 2（CI 失败重试） |
| Max tokens | 500,000 |
| Max sub-agent spawns | 5 |
| Max stagnant cycles | 3 |

## 停止条件

- 本地门 + CI 全绿 → `complete`（PR 就绪，等人类 merge）
- 同 CI 失败重试 2 次仍失败 → `wait_human`
- CI 失败根因在 denylist 路径 → `wait_human`
- 超过 token 预算 → `budget_exhausted`

## Maker/Checker

- Maker：实现 + 本地验证
- Checker：在隔离 worktree 跑 6 阶段验证 + 跑 CI 模拟
- CI 是最终的 Checker（独立环境）

## Auto-merge 策略

默认**不 auto-merge**。即使 CI 全绿，也等人类 merge。

如果开启 auto-merge：
- 仅限 allowlist 内的非行为变更（见 [safety-guardrails.md](../safety-guardrails.md)）
- 行为变更禁止 auto-merge
- auto-merge 前必须 Checker APPROVE

## CI 修复策略

```text
CI 失败 → 读 CI 日志 → 判断根因:
  - 测试失败 → localize-repair-validate 一次
  - 类型错误 → 修类型一次
  - lint → 修 lint 一次
  - 依赖问题 → wait_human（不在 PR loop 范围）
  - 环境问题 → wait_human
修复后 push → 等 CI → 重复（最多 2 次）
```

## STATE.md

```markdown
## Goal
PR #<n> 通过 CI

## Acceptance Criteria
- [ ] 本地 build 通过
- [ ] 本地测试通过
- [ ] CI 全绿

## Current Evidence
<CI 日志摘要>

## Failed Attempts
- 修测试失败: 测试本身有问题 → 改测试 → CI 绿

## Next Smallest Step
等人类 merge
```

## 与 ci-sweeper 的区别

| 维度 | continuous-pr-loop | ci-sweeper |
| --- | --- | --- |
| 触发 | 用户请求创建 PR | 定期扫描 CI 失败 |
| 范围 | 单 PR 全流程 | 多 PR 的 CI 失败修复 |
| 节奏 | 单次 | 5-15 分钟 |
| 就绪度 | L2 | L2 |
