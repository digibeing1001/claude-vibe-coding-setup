# RFC DAG Loop

用于可分解的规格说明。把大 spec 拆成有真实依赖边的工作单元，按依赖顺序执行。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 小时-天 |
| 风险 | Medium |
| 默认就绪度 | L2 |
| 时间尺度 | 小时-天 |
| 触发 | 大规格 / 多工作单元 / 需并行 |

## 循环

```
Context: 加载 spec + 依赖图 + 当前单元
Decide:  选下一个可执行单元（依赖已满足）
Act:     在独立 worktree 实现单元 + 单元测试
Evaluate: 单元测试通过 + 依赖边未破
```

## 步骤

1. **Decompose**——分解成有真实依赖边的工作单元
2. **Co-locate tests**——测试与实现单元放一起
3. **Isolate**——独立 worktree 或 host-native task space 跑各单元
4. **Land low-overlap first**——先合并重叠低的单元
5. **Rebase + re-test**——合并每个单元前 rebase + 重测
6. **Evict**——冲突或失败的单元用精确失败上下文驱逐

## 依赖图

```text
Unit A (基础工具)
  ├─> Unit B (使用 A 的功能)
  ├─> Unit C (使用 A 的另一功能)
  └─> Unit D (使用 B + C)

执行顺序: A → (B || C) → D
```

## 预算

| 维度 | 默认 |
| --- | --- |
| Max iterations | 5 |
| Max retries/cause | 2 |
| Max tokens | 500,000 |
| Max sub-agent spawns | 4（并行单元） |
| Max stagnant cycles | 3 |

## 停止条件

- 所有单元合并 + 全量测试通过 → `complete`
- 单元驱逐 2 次仍冲突 → `wait_human`
- 依赖边检测到环 → `fail`（spec 有问题）

## Maker/Checker

- Maker：每个单元一个 Maker（可并行）
- Checker：每个单元独立 Checker + 合并后总 Checker
- 单元间合并需跑集成测试

## 多 worktree 协调

```bash
git worktree add ../rfc-unit-a <branch-a>
git worktree add ../rfc-unit-b <branch-b>
git worktree add ../rfc-unit-c <branch-c>
```

每个单元在独立 worktree 跑，合并到主分支前在隔离环境跑集成测试。

## STATE.md

```markdown
## Goal
实现 <spec 标题>

## Dependency Graph
- Unit A: complete
- Unit B: in_progress (worktree: ../rfc-unit-b)
- Unit C: blocked (depends on A, A done, ready)
- Unit D: blocked (depends on B + C)

## Current Evidence
<单元测试 + 集成测试输出>

## Failed Attempts
- Unit B 第一次: 与 A 接口不匹配 — 已修

## Next Smallest Step
合并 Unit B → 启动 Unit C
```
