# Loop 模式目录

可直接复用的生产模式。每个模式都有明确的节奏、风险、就绪度建议、停止条件。

## 即时类（L1 默认）

| 模式 | 节奏 | 风险 | 用途 |
| --- | --- | --- | --- |
| [localize-repair-validate](localize-repair-validate.md) | 即时 | Low | 大多数 bug 和回归 |
| [sequential-quality-loop](sequential-quality-loop.md) | 分钟-小时 | Low | 单一聚焦的功能或重构 |

## 长时类（L2 默认）

| 模式 | 节奏 | 风险 | 用途 |
| --- | --- | --- | --- |
| [rfc-dag-loop](rfc-dag-loop.md) | 小时-天 | Medium | 可分解的规格说明 |
| [parallel-generation-loop](parallel-generation-loop.md) | 分钟-小时 | Medium | 原型/设计/研究候选 |
| [continuous-pr-loop](continuous-pr-loop.md) | 分钟-小时 | Medium | CI/PR 自动化 |

## 调度类（L1-L2）

| 模式 | 节奏 | 风险 | 用途 |
| --- | --- | --- | --- |
| [daily-triage](daily-triage.md) | 1天 | Low | 每日 triage 报告 |
| [ci-sweeper](ci-sweeper.md) | 5-15分钟 | Medium | CI 失败自动修复 |
| [issue-triage](issue-triage.md) | 2小时-1天 | Low | issue 分类提案 |
| [post-merge-cleanup](post-merge-cleanup.md) | 1天-6小时 | Low | 合并后清理 |

## 选哪个模式

```text
Bug 或失败测试?
  -> localize-repair-validate

单一聚焦功能?
  -> sequential-quality-loop

大规格可分解?
  -> rfc-dag-loop

需要多个创意变体?
  -> parallel-generation-loop

需要 PR/CI/部署自动化?
  -> continuous-pr-loop

需要定期扫描 CI/issue/提交?
  -> daily-triage (报告)
  -> ci-sweeper (修复)
  -> issue-triage (提案)
```

## 模式通用规则

所有模式都遵循 Loop Engineering 核心机制：

1. **四节点循环**：Context → Decide → Act → Evaluate
2. **8 状态转移**：控制器独占
3. **STATE.md**：每 run 读/写/prune
4. **预算**：声明预算表，超限即停
5. **Maker/Checker**：执行者不验证，验证者不执行
6. **denylist**：每轮强制检查
7. **Post-Run Critique**：每 run 必写
8. **就绪度**：先 L1 跑 1-2 周，再 L2，再 L3
