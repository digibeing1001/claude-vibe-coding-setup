# 失败模式目录

Loop Engineering 的失败模式有规律。这份目录按严重度 S1/S2/S3 分类，每个模式都有症状、根因、修复。新 loop 上线前必须对照这份目录检查，运行中遇到问题时按目录排查。

## 严重度定义

| 严重度 | 含义 | 响应 |
| --- | --- | --- |
| S1 | 数据损坏、安全漏洞、生产事故 | 立即停所有 loop，人工介入 |
| S2 | 浪费资源、产出错误、loop 失控 | 停当前 loop，降级就绪度 |
| S3 | 效率低下、信号稀释、噪音过多 | 调整参数，下轮修复 |

---

## S1 失败模式

### 1. Over-Reach（越界操作）

**症状**：loop 改了 denylist 路径、执行了高风险命令、跨服务变更未确认。

**根因**：denylist 未加载 / denylist 不全 / 风险评分失效 / AI 绕过 loop-constraints skill。

**修复**：
- 立即 kill switch 暂停所有 loop
- 回滚越界变更
- 检查 denylist 配置
- 检查 loop-constraints skill 是否被跳过
- 补全 denylist 条目

**预防**：每轮 Context 节点强制跑 loop-constraints，denylist 哈希记录在 STATE.md。

### 2. Secret Leakage（密钥泄漏）

**症状**：loop 把密钥写入交接包、写入 STATE.md、写入日志、或推送到 PR。

**根因**：交接包禁止内容未强制 / denylist 的 read 规则缺失 / 日志未脱敏。

**修复**：
- 立即轮换泄漏的密钥
- 清理泄漏的文件/日志/PR
- 检查 denylist 的 read 规则
- 检查交接包 schema 的禁止内容字段
- 加日志脱敏过滤器

**预防**：交接包 schema 强制禁止密码密钥令牌；denylist 默认覆盖所有常见密钥路径。

### 3. Production Damage（生产破坏）

**症状**：loop 改了生产配置、执行了生产删除操作、部署了未验证代码。

**根因**：denylist 未覆盖生产路径 / 风险评分阈值过低 / L3 未达条件就跑 L3 行为。

**修复**：
- 立即 kill switch
- 回滚生产变更
- 事故复盘，写入 `stories/`
- 降级 loop 就绪度
- 补全生产路径 denylist

**预防**：生产路径默认在 denylist；L3 上线必须 denylist + budget + metrics + human gates 全具备。

---

## S2 失败模式

### 4. Infinite Fix Loop（无限修复循环）

**症状**：同 PR 自动修复 >3 次仍无进展，token 持续燃烧。

**根因**：重试上限失效 / 同根因重试计数未记录 / AI 用"换个角度试"绕过计数。

**修复**：
- 强制转 `wait_human`
- 检查重试计数逻辑
- 检查根因是否真的相同（同根因才累计计数）

**预防**：max retries/cause 默认 2，第 3 次强制升级；STATE.md 记录 failed_attempts 的根因 hash。

### 5. State Rot（状态腐烂）

**症状**：STATE.md 越来越大，已解决项堆积，loop 读 state 越来越慢，旧项干扰新判断。

**根因**：prune 逻辑缺失 / prune 逻辑过保守 / 已解决项未移到 Recent Noise。

**修复**：
- 手动 prune STATE.md
- 修复 prune 逻辑：每 run 必须把已解决/已合并项移到 Recent Noise，下 run 删除
- 检查 prune 阈值（多少天未变化才 prune）

**预防**：每 run 结束必跑 prune；STATE.md 模板有 Recent Noise 区。

### 6. Verifier Theater（验证剧场）

**症状**：有 Checker 但 Checker 总是 APPROVE，REJECT 率异常低（<5%），实际合并后 bug 频出。

**根因**：Maker 和 Checker 同 session / 同模型 / Checker 指令是"验证正确"而非"找拒绝理由" / Checker 只跑 Maker 跑过的测试。

**修复**：
- 强制 Checker 用不同 session/agent
- Checker 用更强或对等模型
- 改 Checker 指令为"找出拒绝理由"
- Checker 跑独立测试集
- 必须附原始 stdout/stderr

**预防**：Maker/Checker 物理分离是硬约束；上线前自检第 4 节。

### 7. Token Burn（token 燃烧）

**症状**：watchlist 空时仍 spawn 子 agent，单 run 消耗远超基准，预算快速耗尽。

**根因**：watchlist 空→早退未实现 / 子 agent spawn 无门槛 / Context 节点加载了无关文件。

**修复**：
- 实现 watchlist 空→早退（<5k token）
- 子 agent spawn 前检查"是否真的需要"
- Context 节点只加载最小可信上下文
- 检查大文件是否按引用传递

**预防**：预算表 + watchlist 早退是 L1 上线条件。

### 8. Parallel Collision（并行碰撞）

**症状**：多个 loop 同时操作同一 branch/PR，互相覆盖，结果不可预测。

**根因**：acting_on 字段未配置 / spawn 前未读其他 state / 优先级未声明。

**修复**：
- 立即停冲突的 loop
- 配置 acting_on 字段
- spawn 前读所有其他 state，匹配则 skip 并 log
- 声明优先级

**预防**：多 loop 协调协议强制 acting_on；优先级表见 [multi-loop-coordination.md](multi-loop-coordination.md)。

### 9. Escalation Failure（升级失败）

**症状**：loop 转 wait_human 后，人类没收到通知，项卡在 "waiting on human" >24h。

**根因**：通知渠道未配置 / 通知渠道失效 / 升级阈值过低导致噪音淹没真信号。

**修复**：
- 检查通知渠道（Slack/邮件/工单）
- 检查升级阈值是否过低
- 检查 STATE.md 的 High Priority 区是否被监控

**预防**：升级路径必须明确（什么情况通知谁）；>24h 未响应触发告警。

---

## S3 失败模式

### 10. Comprehension Debt Spiral（理解债螺旋）

**症状**：loop 跑得快，但人不读 diff，循环越久偏差越大，review 沦为橡皮图章。

**根因**：人没时间 review / diff 太大 / review 节奏不固定 / 无人强制 review。

**修复**：
- 强制非平凡 PR 必须人工 review
- 控制单 PR 大小（>500 行强制拆分）
- 固定 review 节奏（每天或每两天）
- 每周生成 loop digest 供人读

**预防**：L2/L3 上线条件包括"人工 review 流程已就位"。

### 11. Cognitive Surrender（认知放弃）

**症状**：人类不再质疑 loop 的产出，"AI 说的就对吧"，逐渐失去对系统的理解。

**根因**：loop 输出过于自信 / 人类没参与 spec 迭代 / L2 反馈循环失效。

**修复**：
- 强制 loop 输出"假设"和"不确定项"，不只输出结论
- 恢复 L2 review 节奏
- 关键决策必须人类签字
- 定期做"loop 审计"——随机抽 N 个 run 人工复核

**预防**：L2 是开发者反馈循环，不能因为 L1 快就跳过 L2。

### 12. False Completion（虚假完成）

**症状**：loop 报告 complete，但实际验收标准未全通过 / 证据过期 / 测试被修改。

**根因**：Evaluate 节点失效 / Evals 不完备 / AI 修改测试用例让代码通过 / 证据不是 fresh 的。

**修复**：
- 强制 Evaluate 用 fresh 命令输出
- 测试用例不能由 Maker 修改（测试在独立 worktree）
- 验收标准逐项打勾，不能整体"感觉对了"
- 完成证据附原始 stdout

**预防**：Maker/Checker 分离；完成证据要求 fresh。

### 13. No-Progress Churn（无进展空转）

**症状**：loop 连续多轮"做了点什么"但 Next Smallest Step 不变，目标未推进。

**根因**：max_stagnant_cycles 未配置 / 进度判断失效 / AI 用"换个角度"绕过无进展检测。

**修复**：
- 强制 max_stagnant_cycles = 3
- 进度判断基于"Next Smallest Step 是否变化"+"验收标准是否推进"
- 无进展即转 budget_exhausted 或 fail

**预防**：硬护栏 max_stagnant_cycles 是控制器强制执行。

### 14. Context Pollution（上下文污染）

**症状**：loop 加载了无关文件、旧日志、过期 skill，上下文膨胀，判断质量下降。

**根因**：Context 节点未做最小化 / 大文件未按引用传递 / 旧 skill 未清理。

**修复**：
- Context 节点只加载当前 phase 所需文件
- 大文件按引用传递（path + hash）
- 定期清理过期 skill
- 用 code search 而非全文件加载

**预防**：原仓库已有"Context boundary"规则，Loop Engineering 强化它。

### 15. Spec Drift（规格漂移）

**症状**：loop 跑着跑着偏离了原 spec，做了一堆 spec 没要求的事。

**根因**：spec 未版本化 / spec 模糊 / AI 靠猜补洞 / L2 review 未发现漂移。

**修复**：
- spec 可版本化，git 管理
- spec 必须有 non-goals 字段
- 每轮 Context 节点校验"当前动作是否在 spec 范围内"
- L2 review 对照 spec 而非对照"感觉合理"

**预防**：L2 工程要点第 3 条——Spec 可版本化，含目标、非目标、验收证据、权限边界、预算边界、停止条件。

---

## 失败模式与就绪度

新 loop 上线前必须对照失败模式目录检查：

| 失败模式 | L1 必须覆盖 | L2 必须覆盖 | L3 必须覆盖 |
| --- | --- | --- | --- |
| Over-Reach | ✓ | ✓ | ✓ |
| Secret Leakage | ✓ | ✓ | ✓ |
| Production Damage | ✓ | ✓ | ✓ |
| Infinite Fix Loop | ✓ | ✓ | ✓ |
| State Rot | ✓ | ✓ | ✓ |
| Verifier Theater | - | ✓ | ✓ |
| Token Burn | ✓ | ✓ | ✓ |
| Parallel Collision | - | ✓ | ✓ |
| Escalation Failure | ✓ | ✓ | ✓ |
| Comprehension Debt | - | ✓ | ✓ |
| Cognitive Surrender | - | ✓ | ✓ |
| False Completion | ✓ | ✓ | ✓ |
| No-Progress Churn | ✓ | ✓ | ✓ |
| Context Pollution | ✓ | ✓ | ✓ |
| Spec Drift | - | ✓ | ✓ |

## Post-Mortem 流程

每次 S1/S2 失败后：

1. 立即停所有相关 loop
2. 写 post-mortem 到 `stories/<date>-<pattern>-<failure>.md`
3. 包含：症状、根因、影响、修复、预防、时间线
4. 更新失败模式目录（如果是新模式）
5. 降级 loop 就绪度
6. 修复后再从 L1 重新上线
