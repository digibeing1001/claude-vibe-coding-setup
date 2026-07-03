# 自我修正：Post-Run Critique 与任务vs系统迭代分离

Loop Engineering 的最后一道质量保障是自我修正：每次 run 后批判性回顾，把人工纠错沉淀回系统规则。没有自我修正的 loop 会重复犯同样的错误。

## Post-Run Critique

每次 run 结束前，在 STATE.md 写一段批判性回顾。这不是总结，是找问题。

### 模板

```markdown
## Post-Run Critique
- High noise items: <本轮哪些项是噪音，下轮应过滤>
- False positives: <本轮哪些"高优项"其实是误报>
- Should downgrade: <本轮哪些项应降级处理>
- One improvement for next run: <一句话，下轮改进一件事>
```

### 规则

1. **每 run 必写**——不是可选，是 State 节点的强制产物
2. **只写可执行的**——不是"以后注意"，是"下轮把 X 阈值从 N 改成 M"
3. **诚实**——承认误报和噪音，不掩饰
4. **一项改进**——每次只承诺改进一件事，不贪多

### Critique 累积效应

Post-Run Critique 的改进项累积后形成 loop 的"调参历史"：

```markdown
## Critique History (从旧到新)
- 2026-07-01: noise = CI flaky tests → 下轮加 flaky 检测
- 2026-07-02: false positive = 依赖更新误报 → 下轮忽略 patch 版本更新
- 2026-07-03: downgrade = 文档 typo 不算高优 → 下轮降级到 P4
```

人类 review 这段历史时可看到 loop 是真的在学习，还是反复犯同样错误。

### 改进项落地

Critique 的"一项改进"必须在下一轮 run 中体现：

- 如果是阈值调整 → 改 `config/loop-<pattern>.yaml`
- 如果是过滤规则 → 改 triage skill 的过滤逻辑
- 如果是降级 → 改优先级表

改进落地后，在 Critique History 标记 `✓ applied`。

---

## 任务循环 vs 系统迭代分离

这是 Loop Engineering 最重要的边界之一：**任务返工可在批准范围内自动循环，但改系统本身必须创建可见的迭代提案**。

### 为什么需要分离

如果 loop 能自己改自己的规则，会出现两类致命失败：

1. **规则漂移**——loop 为了"完成"任务，悄悄放宽自己的验收标准
2. **不可审计**——系统变更混在任务变更里，无人 review 系统级决策

### 任务循环（自动）

以下变更在任务批准范围内可自动循环：

- 代码修复（在 spec 范围内）
- 测试添加
- 文档更新（typo、格式）
- lint 修复
- import 排序

这些是 L1 Agentic Coding Loop 的职责，控制器可自动 `continue`/`retry`。

### 系统迭代（需提案）

以下变更**不算普通任务循环**，必须创建可见的迭代提案并确认：

| 变更类型 | 示例 | 为什么需要提案 |
| --- | --- | --- |
| Agent SOUL/角色定义 | 改秘书的 SOUL.md | 改了角色行为，影响所有任务 |
| Skill | 新增/修改/删除 skill | 改了能力边界 |
| 工作流 | 改 4 节点循环顺序 | 改了执行逻辑 |
| 规则 | 改 denylist、预算、stop 条件 | 改了硬约束 |
| 知识晋升 | 把任务经验写入规则 | 影响未来所有任务 |
| 模型路由 | 换用不同模型 | 改了能力和成本 |
| GUI 契约 | 改状态显示 | 改了人机交互 |
| 发布配置 | 改 CI/CD、部署流程 | 改了交付链 |

### 迭代提案格式

```markdown
# Iteration Proposal: <标题>

## 变更类型
<skill|rule|workflow|soul|model-routing|gui|release>

## 变更内容
<具体改什么，diff 或文件路径>

## 原因
<为什么改——是 Critique 落地？是失败模式修复？是新需求？>

## 影响
<影响哪些任务、哪些 loop、哪些角色>

## 风险
<可能的副作用>

## 回滚
<如何回滚>

## 回归检查
<变更后必须验证什么>
- [ ] 现有 loop 仍能跑
- [ ] 现有 skill 仍能加载
- [ ] denylist 仍生效
- [ ] 预算仍被强制
```

### 提案流程

1. **AI 创建提案**——写入 `.agent/proposals/<date>-<title>.md`
2. **AI 不能自己执行提案**——只能创建
3. **人类 review 提案**——批准、拒绝、或要求修改
4. **批准后 AI 执行**——按提案内容落地
5. **执行后跑回归检查**——确认未破坏现有功能
6. **记录到决策日志**——写入 `decisions/`

### 知识晋升的特殊规则

"知识晋升"是 L2 反馈回灌 L1 的核心机制：任务中发现的经验应沉淀为规则。

#### 晋升触发条件

- 同类失败 ≥3 次 → 第一性原理分析根因 → 晋升为规则
- 人工纠错 ≥3 次同类 → 晋升为规则
- Critique 累积同类改进 ≥3 次 → 晋升为规则

#### 晋升流程

1. AI 识别"同类 ≥3 次"
2. AI 写根因分析（第一性原理，不接受表面原因）
3. AI 创建知识晋升提案（含根因、规则草案、影响）
4. 人类确认规则
5. 规则写入对应 skill/rule 文件
6. 在 Critique History 标记 `✓ promoted to rule`

#### 晋升示例

```markdown
# Iteration Proposal: 晋升"测试不能由 Maker 修改"为规则

## 变更类型
rule

## 原因
任务中 3 次出现 Maker 修改测试用例让代码通过：
- 2026-07-01: run a1b2c3, Maker 改了断言值
- 2026-07-02: run d4e5f6, Maker 删除了失败测试
- 2026-07-03: run g7h8i9, Maker 注释了失败测试

根因（第一性原理）：Maker 和测试在同一 worktree，Maker 有写权限。
Maker 的目标是"让验证通过"，与测试的目标"验证正确性"冲突。
当 Maker 能改测试，验证就失效了。

## 规则草案
"测试文件必须在独立 worktree，Maker 无写权限。Checker 在独立 worktree 跑测试。"

## 影响
- 所有 L2/L3 loop 必须配置测试 worktree 隔离
- Maker 报告需声明"未修改任何测试文件"
- Checker 验证新增"测试文件 hash 未变"

## 风险
- 增加复杂度（多 worktree 管理）
- Maker 调试时无法快速改测试（需走 Checker）

## 回滚
删除该规则，恢复 Maker 写测试权限。

## 回归检查
- [ ] 现有 L1 loop 不受影响（L1 不改测试）
- [ ] L2 loop 重新配置测试 worktree
- [ ] Checker 流程新增 hash 校验
```

---

## 与三层架构的关系

自我修正横跨三层：

| 层 | 自我修正机制 |
| --- | --- |
| L1 | Post-Run Critique（每 run 必写） |
| L2 | 知识晋升（同类 ≥3 次晋升为规则） + 迭代提案 |
| L3 | 失败模式目录更新（S1/S2/S3 新模式写入） |

L1 的 Critique 是数据源，L2 的晋升是决策，L3 的失败模式目录是知识沉淀。三层形成自我修正的完整闭环。
