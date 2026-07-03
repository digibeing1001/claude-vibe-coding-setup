# Parallel Generation Loop

用于原型、设计替代方案、研究候选。每个 agent 走不同方向，比较后选一个推进。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 分钟-小时 |
| 风险 | Medium |
| 默认就绪度 | L2 |
| 时间尺度 | 分钟-小时 |
| 触发 | 需要多个创意变体 / 设计探索 / 研究候选 |

## 循环

```
Context: 加载设计目标 + 约束
Decide:  分配每个 agent 一个独特方向 + 输出路径
Act:     每个 agent 在独立 worktree 走自己的方向
Evaluate: 用 rubric 比较输出，选一个推进到 sequential-quality-loop
```

## 步骤

1. **Assign**——每个 agent 一个独特方向和输出路径
2. **Make uniqueness explicit**——不要求 agent 自我区分，人类显式指定
3. **Generate**——每个 agent 在独立 worktree 生成
4. **Compare**——用 rubric 比较输出
5. **Promote**——选一个路径推进到 sequential-quality-loop
6. **Archive**——其他路径归档到 `prototypes/`

## 唯一性显式化

不要这样：

```text
"生成 3 个不同的设计方案"
```

要这样：

```text
Agent 1: 走"最小化"方向，输出到 prototypes/minimal/
Agent 2: 走"功能完整"方向，输出到 prototypes/full/
Agent 3: 走"实验性"方向，输出到 prototypes/experimental/
```

每个 agent 知道自己的方向，不浪费算力自我区分。

## Rubric

比较维度：

| 维度 | 权重 |
| --- | --- |
| 满足核心目标 | 0.4 |
| 实现复杂度 | 0.2 |
| 可维护性 | 0.2 |
| 性能 | 0.1 |
| 创新性 | 0.1 |

## 预算

| 维度 | 默认 |
| --- | --- |
| Max iterations | 1（生成一轮，比较后推进） |
| Max sub-agent spawns | 3-5（并行方向） |
| Max tokens | 500,000 |
| Max stagnant cycles | 不适用 |

## 停止条件

- 所有 agent 完成 + rubric 评分完成 → `complete`（选一个推进）
- 多数 agent 超时 → `wait_human`
- rubric 平分（差距 <0.1）→ `wait_human`（人类决策）

## Maker/Checker

- Maker：每个方向一个 Maker
- Checker：跑 rubric 评分（可由 AI 或人类担任）
- 选定路径后，进入 sequential-quality-loop 才跑 6 阶段验证

## STATE.md

```markdown
## Goal
生成 <N> 个 <方向> 的原型

## Rubric
| 方向 | 核心目标 | 复杂度 | 可维护 | 性能 | 创新 | 总分 |
| --- | --- | --- | --- | --- | --- | --- |
| minimal | 0.9 | 0.9 | 0.8 | 0.7 | 0.5 | 0.84 |
| full | 0.95 | 0.5 | 0.7 | 0.8 | 0.7 | 0.79 |
| experimental | 0.7 | 0.4 | 0.5 | 0.6 | 0.9 | 0.63 |

## Decision
推进 minimal 方向到 sequential-quality-loop

## Next Smallest Step
把 prototypes/minimal/ 移入主分支，跑 6 阶段验证
```
