# 预算管理与 Kill Switch

预算是 Loop Engineering 的硬护栏。没有预算的 loop 会为了"完成感"无限燃烧 token，或在同一个错误上反复尝试。预算不是建议，是控制器强制执行的硬约束——超预算就停。

## 为什么需要预算

AI 的"再多试一次"心态没有自带的成本意识。一个卡住的 loop 可以在 30 分钟内烧掉几十美元，而产出为零。预算把"何时停"从 AI 的判断变成可配置的硬上限。

## 预算表模板

每个 loop 在启动前必须声明预算，写入 `loop-budget.md`：

```markdown
# Loop Budget

| Loop | Max runs/day | Max tokens/day | Max sub-agent spawns/run | Max retries/cause | Max cost (microunits)/day |
| --- | --- | --- | --- | --- | --- |
| daily-triage | 24 | 100,000 | 0 | 2 | 500,000 |
| ci-sweeper | 96 | 200,000 | 3 | 2 | 1,000,000 |
| pr-babysitter | 96 | 150,000 | 2 | 2 | 750,000 |
| continuous-pr-loop | 1 | 500,000 | 5 | 3 | 2,500,000 |
| sequential-quality-loop | 1 | 300,000 | 3 | 3 | 1,500,000 |
| localize-repair-validate | 1 | 100,000 | 0 | 2 | 500,000 |
```

### 预算维度

| 维度 | 含义 | 默认 |
| --- | --- | --- |
| Max runs/day | 每天 loop 触发次数 | 按模式 |
| Max tokens/day | 每天 token 消耗 | 按模式 |
| Max sub-agent spawns/run | 单次 loop 子 agent 派生数 | 3 |
| Max retries/cause | 同一根因重试次数 | 2 |
| Max cost (microunits)/day | 每天费用上限 | 按模式 |
| Max stagnant cycles | 进度停滞轮数 | 3 |
| Max iterations | 单次 loop 最大迭代 | 3 |

## 预算超限流程

当任何维度超限时，控制器执行：

1. **暂停调度器**——停止该 loop 的下一轮触发
2. **追加 run log**——在 `loop-run-log.md` 记录超限事件
3. **开 maintainer issue**——创建人类可见的工单，说明哪个维度超限、超了多少
4. **状态转 `budget_exhausted`**——当前 run 终止

超限不是失败，是正常的成本控制信号。人类决定是提高预算、修复根因（为什么燃烧这么快），还是停掉这个 loop。

## Kill Switch — 一键暂停所有 loop

全局 kill switch 用一个 label 或 flag。所有 loop 在 Context 节点必须先检查 kill switch，命中则立即转 `cancel`。

### 实现方式

选其一：

**方式 1：Git label（推荐用于有仓库的 loop）**

```bash
# 暂停所有 loop
git label loop-pause-all
# 推送到远程
git push origin loop-pause-all

# 恢复
git label -d loop-pause-all
git push origin :loop-pause-all
```

**方式 2：STATE.md flag（推荐用于本地 loop）**

```markdown
# Loop State

## Kill Switch
status: PAUSED  # 改为 ACTIVE 恢复
reason: <暂停原因>
paused_at: <时间>
```

**方式 3：环境变量（推荐用于 CI）**

```bash
export LOOP_PAUSE_ALL=1  # 任何非空值即暂停
```

### Kill switch 规则

- 所有 loop 在 Context 节点第一件事就是检查 kill switch
- 命中 kill switch 时立即转 `cancel`，不跑任何 Act
- Kill switch 只能由人类清除，AI 不能自行清除
- 清除后下一轮 loop 才能恢复，不是立即恢复

## Watchlist 空→早退

这是最重要的成本优化：**watchlist 空 → 早退 <5k token**。

```text
Daily Triage 循环:
1. 调度触发
2. triage skill 摄取（CI 失败/issue/提交/旧 state）
3. 高优项入 state
4. IF state 说"无可行动项":
5.   早退，本轮 <5k token，不 spawn 任何子 agent
6. ELSE:
7.   spawn 子 agent 处理高优项
```

只在 state 说可行动时才 spawn 子 agent。空 watchlist 时燃烧 token 是最大的浪费。

## 成本估算

在调度前估算 token 花费，超预算的 run 不启动。

### 估算公式

```
estimated_tokens = base_tokens(pattern) + items_count * per_item_tokens
estimated_cost = estimated_tokens * model_rate
```

### 基准 token（参考）

| Pattern | Base tokens | Per-item tokens |
| --- | --- | --- |
| daily-triage | 2,000 | 3,000 |
| ci-sweeper | 1,500 | 5,000 |
| pr-babysitter | 1,000 | 4,000 |
| issue-triage | 1,500 | 2,000 |
| post-merge-cleanup | 1,000 | 2,000 |
| localize-repair-validate | 3,000 | 0 |
| sequential-quality-loop | 5,000 | 0 |

### 估算命令

```bash
python scripts/loop_audit.py --estimate-cost --pattern daily-triage --items 5
```

## 预算持久化

每次运行必须持久化以下用量，控制器据此判断是否超限：

```json
{
  "run_id": "<uuid>",
  "loop_pattern": "daily-triage",
  "date": "2026-07-03",
  "runs_today": 3,
  "tokens_used_today": 45000,
  "sub_agent_spawns_this_run": 2,
  "retries_this_cause": 1,
  "cost_microunits_today": 225000,
  "stagnant_cycles": 0,
  "iterations_this_run": 1
}
```

## 与控制器的契约

控制器在每次状态转移前检查预算：

```text
IF any budget dimension exceeded:
    transition to budget_exhausted
    pause scheduler
    append run log
    open maintainer issue
ELSE IF kill_switch active:
    transition to cancel
ELSE:
    proceed with AI's suggested transition
```

AI 无法绕过预算检查——预算是控制器的硬护栏，不是 AI 的建议。
