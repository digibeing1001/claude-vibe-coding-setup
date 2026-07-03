# Post-Merge Cleanup

合并后清理：删死代码、清缓存、更新文档、归档分支。Low 风险，off-peak 跑。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 1天-6小时 |
| 风险 | Low |
| 默认就绪度 | L1 |
| 时间尺度 | 小时 |
| 触发 | cron / merge webhook |

## 循环

```
Context: 加载近期合并的 PR + 代码库状态
Decide:  判断哪些清理可自动做
Act:     执行安全清理（Maker）→ 验证（Checker）
Evaluate: 清理后 build/test 仍通过
```

## 步骤

1. **Scan**——扫描近期合并的 PR
2. **Identify**——识别可清理项（死代码、过期注释、未用 import、缓存）
3. **Decide**——可自动清理 vs 需人工
4. **Clean**——spawn Maker 清理 → Checker 验证 build/test
5. **Document**——更新文档（如 API 变更影响文档）
6. **Archive**——归档已合并的 branch
7. **Critique**——写 Post-Run Critique

## 可自动清理项

| 类型 | 自动 | 备注 |
| --- | --- | --- |
| 未用 import | 是 | |
| 未用变量 | 是 | |
| 过期 TODO 注释 | 是 | 标记为过期 |
| 死代码（无引用） | 是 | 需 Checker 验证 |
| 缓存清理 | 是 | |
| 文档 typo | 是 | |
| 文档内容更新 | 否 | 需人类确认 |
| API 文档重写 | 否 | 需人类确认 |

## 预算

| 维度 | 默认 |
| --- | --- |
| Max runs/day | 1-4 |
| Max tokens/day | 100,000 |
| Max sub-agent spawns/run | 2 |
| Max retries/cause | 1 |

## 停止条件

- 清理完成 + build/test 通过 → `complete`
- 清理导致 build/test 失败 → 回滚 + `wait_human`
- 无可清理项 → `complete`（早退）

## Watchlist 空→早退

```text
IF 无近期合并 PR 且无可清理项:
    早退，本轮 <5k token
ELSE:
    按优先级清理
```

## Maker/Checker

- Maker：执行清理
- Checker：跑 build + test 确认未破坏
- 清理后必须全量 build + test（不只是 scoped）

## Off-peak 调度

默认 off-peak 跑（夜间或低活跃时段），避免与开发者活动冲突：

```yaml
schedule:
  cron: "0 22 * * *"  # 每晚 22:00
  timezone: "Asia/Shanghai"
```

## STATE.md

```markdown
## Goal
清理近期合并的代码

## Watch List
- PR #456 合并后: 清理了 3 个未用 import — done
- PR #457 合并后: 待清理死代码 — pending

## Current Evidence
<build + test 输出>

## Failed Attempts
- 清理 PR #456 死代码: 导致测试失败 → 回滚 → wait_human

## Post-Run Critique
- High noise: 0
- False positives: 1（误删了"看起来死"但有反射调用的代码）
- One improvement: 加反射调用检测
```
