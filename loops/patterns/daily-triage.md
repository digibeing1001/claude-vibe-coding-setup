# Daily Triage

定期扫描 CI 失败、issue、提交、旧 state，把高优项写入 STATE.md，生成报告。**只看不动**——L1 默认。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 1天（可配置 2小时-1天） |
| 风险 | Low |
| 默认就绪度 | L1（report-only） |
| 时间尺度 | 天 |
| 触发 | cron / 定时调度 |

## 循环

```
Context: 加载旧 STATE.md + CI 状态 + issue 列表 + 近期提交
Decide:  triage 分类（高优/观察/噪音）
Act:     写入 STATE.md + 生成报告（不改代码）
Evaluate: 报告完整 + state 已 prune
```

## 步骤

1. **Schedule**——cron 触发
2. **Triage**——摄取 CI 失败、issue、提交、旧 state
3. **Classify**——高优项入 state，噪音项移到 Recent Noise
4. **Report**——生成报告（哪些项需要处理、建议的处理方式）
5. **Prune**——已解决/已合并项移出 state
6. **Critique**——写 Post-Run Critique

## Watchlist 空→早退

```text
IF state 说"无可行动项":
    早退，本轮 <5k token
    不 spawn 任何子 agent
    记录"empty watchlist, early exit"
ELSE:
    生成报告，等待人类 review
```

这是最重要的成本优化——空 watchlist 时燃烧 token 是最大浪费。

## L1 → L2 升级

L1 默认只生成报告。升级到 L2 后：

- spawn 子 agent 做小修复（typo、lint、import 排序）
- 跑 Maker/Checker 流程
- 创建 PR（不 auto-merge）

升级条件见 [readiness-levels.md](../readiness-levels.md)。

## 预算

| 维度 | 默认 |
| --- | --- |
| Max runs/day | 1（默认）- 12（2小时一次） |
| Max tokens/day | 100,000 |
| Max sub-agent spawns/run | 0（L1）/ 3（L2） |
| Max retries/cause | 2 |

## 停止条件

- triage 完成 + state 已更新 + 报告已生成 → `complete`
- 无可行动项 → `complete`（早退）
- 超过 token 预算 → `budget_exhausted`

## STATE.md

```markdown
## Goal
每日 triage 并生成报告

## Watch List
- [CI] main 分支测试失败 — last seen 2h ago — 建议修复
- [issue] #123 bug 报告 — last seen 1d ago — 建议分类
- [commit] 大改动未 review — last seen 3h ago — 建议 review

## Recent Noise (pruned next run)
- [CI] flaky test 已知问题 — 忽略

## Post-Run Critique
- High noise: flaky test alert 重复出现 → 下轮加 flaky 检测
- False positives: 0
- Should downgrade: 0
- One improvement: 加 flaky test 模式过滤
```

## 报告格式

```markdown
# Daily Triage Report <date>

## High Priority
- <项> — <建议动作>

## Watch List
- <项> — <状态>

## Trends
- CI 失败率: <趋势>
- Issue 增长: <趋势>
- 噪音率: <趋势>

## Recommendations
- <建议 1>
- <建议 2>
```
