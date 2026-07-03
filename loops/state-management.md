# 状态脊柱与上下文交接

状态管理是 Loop Engineering 的记忆系统。没有持久状态的 loop 每轮都从零开始，跨 agent 交接时丢失目标和证据。这套机制把"任务交接不丢目标/证据/决定"做成可校验的协议，而非依赖聊天记忆。

## STATE.md — loop 的记忆脊柱

STATE.md 是 loop 之外的可持久脊柱。每 run 开始读、结束写、每 run prune 已解决/已合并项。它是 loop 产出的最重要产物——回答"当前在做什么/上次试了什么结果/在等谁"。

### 模板

```markdown
# Loop State

Last run: 2026-07-03T14:30:00+08:00
Run ID: <uuid>
Pattern: <localize-repair-validate|sequential-quality-loop|...>
Readiness: <L1|L2|L3>

## Goal
<本轮 loop 要达成的可机械验证目标>

## Acceptance Criteria
- [ ] <验收条件 1>
- [ ] <验收条件 2>

## High Priority (waiting on human)
- <项> — waiting since <时间> — <原因>

## Watch List
- <项> — last action <动作> — <状态>

## Recent Noise (pruned next run)
- <项> — <为什么是噪音>

## Current Evidence
<本轮的命令输出/观察/测试结果>

## Decisions
- <决策> — <理由> — <时间>

## Failed Attempts
- <尝试> — <根因假设> — <是否要重试>

## Next Smallest Step
<一个最小的下一步>

## Post-Run Critique
- High noise items: <项>
- False positives: <项>
- Should downgrade: <项>
- One improvement for next run: <改进>
```

### 状态文件规则

1. **每 run 开始读**——加载历史决策和失败尝试，避免重复试错
2. **每 run 结束写**——记录本轮发生了什么
3. **每 run prune**——已解决/已合并项移到 Recent Noise，下轮删除
4. **不做日记**——只保留恢复 loop 所需的事实
5. **`acting_on` 字段**——多 loop 时记录当前操作的 branch/PR ID，用于碰撞检测

### 多 loop 状态布局

```
.agent/
├── state/
│   ├── STATE.md                    # 主状态文件
│   ├── loop-run-log.md             # 追加式运行历史（所有 loop 共享）
│   ├── daily-triage.state.md       # 每个模式独立 state
│   ├── ci-sweeper.state.md
│   └── issue-triage.state.md
├── runs/
│   └── <run_id>/
│       ├── run.json                # 单次运行状态
│       ├── ledger.jsonl            # 哈希链事件账本
│       └── checkpoints/            # 检查点与恢复游标
```

## loop-run-log.md — 追加式运行历史

所有 loop 共享的运行历史，每次 run 追加一条：

```markdown
## Run <run_id>
- Time: <开始-结束>
- Pattern: <模式>
- Duration: <时长>
- Items found: <数量>
- Actions taken: <数量>
- Escalations: <数量>
- Tokens estimate: <数量>
- Outcome: <complete|fail|cancel|budget_exhausted>
- Notes: <一句话>
```

这个文件用于跨 run 分析趋势（噪音项、误报率、token 燃烧速度），不是用来重放历史。

## 带版本上下文交接包

多 agent 交接时，必须用带版本的交接包，不能用聊天记忆。

### 交接包 schema

```json
{
  "context_id": "<同意图链稳定 ID，同任务的多轮交接保持不变>",
  "task_id": "<单任务 ID>",
  "handoff_id": "<单次交付去重 ID>",
  "context_version": <递增整数，变化时+1>,
  "context_hash": "<上下文内容的 SHA-256>",
  "from_agent": "<agent 标识>",
  "to_agent": "<agent 标识>",
  "goal": "<目标>",
  "acceptance_criteria": ["<条件>"],
  "decisions": [{"decision": "<决策>", "reason": "<理由>", "timestamp": "<时间>"}],
  "evidence": [{"claim": "<声称>", "evidence": "<证据>", "fresh": true}],
  "failed_attempts": [{"attempt": "<尝试>", "root_cause_hypothesis": "<假设>"}],
  "next_step": "<下一步>",
  "references": [{"path": "<文件路径>", "hash": "<文件 hash>", "reason": "<为什么引用>"}],
  "unknowns": ["<不知道什么>"],
  "budget_used": {"iterations": <n>, "tokens": <n>, "cost_microunits": <n>}
}
```

### 三类身份 ID

| ID | 用途 | 生命周期 |
| --- | --- | --- |
| `context_id` | 同意图链稳定——同一任务的多轮交接保持不变 | 任务全生命周期 |
| `task_id` | 单任务标识 | 单次任务 |
| `handoff_id` | 单次交付去重——同一次交接只处理一次 | 单次交接 |

### 接收方确认协议

接收方必须显式确认，未确认不算完成：

- `accept` — 接收并继续
- `request_context` — 上下文不足，请求补充
- `reject` — 上下文有问题，拒绝接收

### 交接包禁止内容

- 私有思维链（chain of thought）
- 密码、密钥、令牌
- 其他租户数据
- "摘要再摘要"（大文件只存一份按引用传递）

## 大文件引用传递

禁止把大文件整段塞进交接包。规则：

1. 大文件只存一份，按引用传递（path + hash + reason）
2. 接收方按需读取，不预加载
3. 引用必须带 hash，接收方校验文件未变
4. 禁止"摘要再摘要"——每次交接都从原始资料引用

## 检查点与恢复

### 检查点

每个 run 维护检查点目录：

```
.agent/runs/<run_id>/checkpoints/
├── cp-001.json    # 第一轮结束后的状态快照
├── cp-002.json
└── current.json   # 当前游标
```

检查点内容：当前节点、决策、预算已用、产物指针、上下文 hash。

### 恢复协议

从检查点恢复时：

1. 只加载确认后的上下文差量 + 当前决定 + 原始资料引用
2. **不重放全部聊天历史**
3. 副作用必须可幂等/可去重/需显式确认
4. 禁止整段重来，只重做最小可重做单元
5. 恢复后第一轮强制跑 Context 节点校验状态

## 终态不可变

终态任务（complete/fail/cancel/budget_exhausted）不可变。后续改进创建新 run，沿用同 `context_id`，但生成新 `task_id` 和 `run_id`。

这条规则保证历史可审计——过去的失败不会被悄悄修改，改进是显式的新动作。

## GUI 契约

如果有可视化界面：

- GUI 只能渲染后端状态，不能自行推断或修改阶段
- 任何状态变化必须由控制器执行
- GUI 的"暂停/恢复"按钮调用控制器 API，不直接改 state 文件
