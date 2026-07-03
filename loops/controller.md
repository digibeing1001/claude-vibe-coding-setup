# 确定性 Loop 控制器

控制器是 Loop Engineering 的核心约束：**AI 只能建议，控制器决定**。模型可以提出下一步动作，但只有确定性控制器能在 8 种状态间切换。这条规则从架构上杜绝 AI 自行其是和无限自我反思。

## 为什么需要确定性控制器

没有控制器的 loop 有三类致命失败：

1. **无限自我反思**——AI 反复"再想想"，烧光预算无产出
2. **状态模糊**——loop 在什么阶段、为什么转移、何时停，全靠聊天记忆，跨 agent 交接时丢失
3. **AI 自我声称完成**——同一个 agent 写代码又验证代码，verdict 不可信

确定性控制器把"状态转移权"从模型手里收回来，交给可审计的规则。

## 四节点工作循环

每个节点可被记录、测试、回看。简单任务可跳过 Decide，但不能跳过 Context/Act/Evaluate。

```
Context → Decide → Act → Evaluate → (回到 Context 或终态)
```

### 1. Context（装载上下文）

装载完成下一步所需的最小可信上下文。

- 大文件按引用取回，不整段塞进上下文
- `unknowns` 显式声明（不知道什么和知道什么一样重要）
- 检查 STATE.md 加载历史决策和失败尝试
- 验证上下文 hash 是否变化（避免基于过期信息决策）

### 2. Decide（形成决策）

形成结构化决策、路线/计划、风险和下一步动作契约。

- 输出：决策 + 路线 + 风险 + 下一步动作
- 简单任务可跳过此节点
- 决策必须可被 Evaluate 节点机械验证

### 3. Act（执行）

调用 Agent、Skill 和工具执行，记录观察与产物。

- 记录：调用了什么工具、消耗了多少预算、产出了什么
- 副作用必须可幂等/可去重/需显式确认
- 遇到 denylist 路径或高风险动作立即暂停

### 4. Evaluate（评估）

按证据、验收标准、进度和预算判断结果。

- 证据优先，确定性检查为主，AI 审查为辅
- 对照 Evals/验收标准，不是对照"感觉对了"
- 进度：本轮是否真的推进了目标（无进展检测）
- 预算：剩余预算是否够下一轮

## 8 状态转移

控制器独占状态转移权，接受 8 种决定：

| 状态 | 触发条件 | 控制器动作 |
| --- | --- | --- |
| `continue` | Evaluate 通过且预算够 | 回到 Context，开始下一轮 |
| `replan` | 发现新信息需要改计划 | 回到 Decide，丢弃旧计划 |
| `retry` | 失败但根因已知且可重试 | 回到 Act，带新上下文重试（最多 3 次） |
| `wait_human` | 高影响缺口/目标漂移/证据冲突/高风险不可逆 | 暂停，通知人类，等待显式恢复 |
| `complete` | 验收通过且产物可访问 | 终态，归档 run |
| `fail` | 永久失败或硬性要求不可满足 | 终态，记录根因，归档 run |
| `cancel` | 用户取消 | 终态，归档 run |
| `budget_exhausted` | 预算耗尽 | 终态，记录消耗，归档 run |

### 状态转移规则

- AI 可"建议"任何状态，但只有控制器能"执行"状态转移
- 终态（complete/fail/cancel/budget_exhausted）不可逆，后续改进创建新 run
- `retry` 同一根因最多 3 次，第 4 次强制升级 `wait_human`
- `replan` 不重置预算，只重置计划

## 硬护栏

两个硬护栏由控制器强制执行，AI 无法绕过：

### max_stagnant_cycles（进度停滞上限）

连续 N 轮 STATE.md 的"Next Smallest Step"未变化，或 Evaluate 报告"无进展"，自动转 `budget_exhausted` 或 `fail`。

默认值：3 轮无进展。

### max_cost_microunits（费用上限）

单 run 累计费用超过上限自动转 `budget_exhausted`。

默认值：见 [budget-management.md](budget-management.md)。

## 人类介入点

两类人工门，AI 可请求但只有控制系统能冻结/恢复：

### 执行前上下文门

- 意图复述（AI 用自己的话重述任务）
- 3 道第一性原理问题（这个任务的不可分解核心是什么？/ 验收标准能机械验证吗？/ 失败模式是什么？）
- 准备度门槛（上下文 hash 已校验、unknowns 已声明、预算已设定）
- 哈希确认（上下文未变才放行）

### 执行中精准中断

仅以下情况暂停：
- 高影响缺口（缺少关键能力或权限）
- 目标漂移（实际做的事偏离 spec）
- 证据冲突（AI 声称完成但验证失败）
- 高风险不可逆动作（生产部署、数据库迁移、删除操作）

意图变化时，原确认自动失效。

## 恢复协议

从检查点恢复时：

1. 只加载确认后的上下文差量 + 当前决定 + 原始资料引用
2. **不重放全部聊天历史**
3. 副作用必须可幂等/可去重/需显式确认
4. 禁止整段重来，只重做最小可重做单元
5. 恢复后第一轮强制跑 Context 节点校验状态

## 状态机定义（机读）

```json
{
  "states": ["context", "decide", "act", "evaluate"],
  "terminals": ["complete", "fail", "cancel", "budget_exhausted"],
  "transitions": {
    "context": ["decide", "act", "wait_human", "cancel"],
    "decide": ["act", "replan", "wait_human", "cancel"],
    "act": ["evaluate", "wait_human", "cancel", "budget_exhausted"],
    "evaluate": ["continue", "replan", "retry", "wait_human", "complete", "fail", "budget_exhausted"]
  },
  "hard_guards": {
    "max_stagnant_cycles": 3,
    "max_retry_per_cause": 3
  },
  "human_gates": {
    "pre_act_context_gate": true,
    "mid_act_interrupt_on": ["high_impact_gap", "goal_drift", "evidence_conflict", "high_risk_irreversible"]
  }
}
```

## 与 AI 的契约

AI 在每轮必须输出：

```markdown
## Loop Status
Node: <context|decide|act|evaluate>
Suggested next state: <continue|replan|retry|wait_human|complete|fail|cancel|budget_exhausted>
Reason: <一句话理由>
Evidence: <命令输出或观察>
Budget used: <已用/上限>
Progress: <本轮推进了什么，或"no progress">
```

控制器根据这份报告 + 硬护栏规则决定实际状态转移。AI 的"suggested next state"只是建议，控制器可覆盖。
