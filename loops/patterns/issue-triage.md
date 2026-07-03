# Issue Triage

定期扫描 issue 列表，分类、打标签、提建议。**只提案不动手**——L1 默认。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 2小时-1天 |
| 风险 | Low |
| 默认就绪度 | L1（propose-only） |
| 时间尺度 | 小时-天 |
| 触发 | cron / issue webhook |

## 循环

```
Context: 加载 issue 列表 + 现有标签 + 项目 conventions
Decide:  分类每个 issue（bug/feature/question/duplicate）
Act:     提案标签 + 提案优先级 + 提案处理方式（不改 issue）
Evaluate: 提案完整 + 人类 review 等待
```

## 步骤

1. **Scan**——扫描新 issue 和未分类 issue
2. **Classify**——按 bug/feature/question/duplicate 分类
3. **Prioritize**——按影响范围和紧急程度打优先级
4. **Propose**——提案标签 + 提案处理方式（写报告，不改 issue）
5. **Critique**——写 Post-Run Critique

## L1 → L2 升级

L1 默认只提案。升级到 L2 后：

- 自动打标签（不修改 issue 内容）
- 自动回复 question 类 issue（附"AI 分类，待人类确认"）
- 自动关闭明显 duplicate

升级条件见 [readiness-levels.md](../readiness-levels.md)。

## 预算

| 维度 | 默认 |
| --- | --- |
| Max runs/day | 12（2小时一次）- 1（每天） |
| Max tokens/day | 50,000 |
| Max sub-agent spawns/run | 0（L1）/ 2（L2） |
| Max retries/cause | 1 |

## 停止条件

- 所有新 issue 分类完成 → `complete`
- 无新 issue → `complete`（早退）
- 超过预算 → `budget_exhausted`

## Watchlist 空→早退

```text
IF 无新 issue 且无未分类 issue:
    早退，本轮 <5k token
ELSE:
    按优先级处理
```

## 不自动做的事

- 不自动关闭 bug/feature issue（只关 duplicate）
- 不自动修改 issue 内容
- 不自动 assign 给人
- 不自动创建 PR（这是 continuous-pr-loop 的事）

## STATE.md

```markdown
## Goal
分类新 issue 并提案处理方式

## Watch List
- issue #789 — bug — 提案: 高优，建议修复
- issue #790 — feature — 提案: 中优，建议评估
- issue #791 — question — 提案: 自动回复

## Recent Noise
- issue #788 — duplicate of #789 — 已关闭

## Post-Run Critique
- High noise: 0
- False positives: 1（把 feature 误判为 bug）
- One improvement: 加"是否有复现步骤"判断 bug vs feature
```

## 报告格式

```markdown
# Issue Triage Report <date>

## New Issues
| Issue | 类型 | 优先级 | 提案 |
| --- | --- | --- | --- |
| #789 | bug | 高 | 建议立即修复 |
| #790 | feature | 中 | 建议评估 |

## Pending Human Action
- #789: 确认是否 bug
- #790: 评估优先级

## Trends
- 本周新增: 12 issues
- bug 占比: 40%
- 平均处理时间: 2.5 天
```
