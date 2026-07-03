# VibeCoding Setup

一套给 AI 编码助手用的通用化工程配置。它解决的核心问题是：**让 AI 编码从"一次性写完就交"变成"受控迭代、可验证、可恢复、可信任"**。

适用于 Claude Code、Codex、Hermes、OpenClaw 等主流宿主。

---

## 它能做什么

### 1. 三层循环工程：让 AI 编码不再"高速跑偏"

AI 编码最大的坑不是写得慢，而是写得快但方向错。这套配置把工作流分成三层嵌套的反馈循环：

| 层级 | 名称 | 时间尺度 | 谁驱动 |
| --- | --- | --- | --- |
| L1 | AI 编码循环 | 分钟级 | AI Agent |
| L2 | 开发者反馈循环 | 小时级 | 开发者 |
| L3 | 外部用户反馈循环 | 天/周级 | 真实用户 |

**关键洞见**：内层提速后，瓶颈会自动向外迁移。只优化 L1 会让 AI 高速产出"看起来完整但其实跑偏"的版本。三层必须同时存在，L2 和 L3 才是决定方向对不对的关键。

### 2. 确定性控制器：AI 只建议，不决策

AI 不能自己说自己完成了。所有状态转移由一个确定性控制器独占：

- AI 输出"建议下一步"（JSON 契约）
- 控制器根据硬规则决定 8 种状态之一：`continue` / `replan` / `retry` / `wait_human` / `complete` / `fail` / `cancel` / `budget_exhausted`
- 硬护栏自动触发：停滞超过 3 轮强制 `replan`，同一根因重试超 3 次强制 `wait_human`

这把"AI 自我宣称完成"这个最常见的翻车点彻底堵死。

### 3. 状态脊柱：每个循环都有记忆

每个循环维护一份 `STATE.md`，记录：

- 目标和验收标准
- 当前证据（命令输出/测试结果）
- 决策历史（决定/原因/时间）
- 失败尝试（尝试/根因假设/是否可重试）
- 下一步最小动作
- 上一轮退出状态

运行前读、运行后写、每轮自动清理已解决项。支持检查点（checkpoint）和回滚恢复——循环挂了能回到上一个已知好状态。

### 4. 预算和一键暂停：成本不会失控

每个循环必须声明预算表：

- 最大迭代次数 / token 数 / 费用（美元/天）/ 墙钟时长 / 同一根因重试次数 / 停滞轮数 / 并发循环数

任一维度超限自动转 `budget_exhausted` 状态并暂停。**Kill Switch** 支持三种触发方式（git label / STATE.md flag / 环境变量），一键暂停所有循环。

成本优化：watchlist 为空时循环早退，单轮可省 5k+ token。

### 5. Maker/Checker 物理分离：执行者不能给自己签字

这是对抗"AI 自我验证幻觉"的核心机制：

- **Maker**（执行者）：在隔离的 worktree 里干活，输出必须带证据，**不能标记自己完成**
- **Checker**（验证者）：物理上独立的实体，用"找拒绝理由"的指令做 6 阶段验证：构建 → 类型检查 → lint → 测试 → 安全 → diff 审查
- 重试上限 3 次，超过转人工

**Verifier Theater 反模式**：Checker 只跑了 `npm run build` 就放行 = 假验证。6 阶段缺一不可。

### 6. 安全护栏：AI 碰不到危险路径

三道护栏在每次循环的 Context 节点强制执行：

- **Path Denylist**：生产环境路径、密钥文件、凭据目录默认不可写不可执行
- **Auto-Merge 默认关闭**：只有在 allowlist 中的低风险 PR 才能跳过人工门
- **MCP 最小权限**：GitHub/Slack/数据库/Linear 等连接器只授予必要 scope
- **风险评分**：≥0.65 自动转 `wait_human`，不允许 AI 自行放行

### 7. 就绪度分层：新循环不能直接上无人值守

新循环必须按阶梯升级：

| 级别 | 能做 | 不能做 | 上线条件 |
| --- | --- | --- | --- |
| L0 Draft | 设计中 | 实际运行 | — |
| L1 Report | 跑完出报告 | 改代码 | 18 维评分 ≥ 38 |
| L2 Assisted | 改代码但需人工确认 | 自动合并 | 18 维评分 ≥ 58，跑 1-2 周 |
| L3 Unattended | 无人值守 | 碰 denylist | 18 维评分 ≥ 78，跑 2-4 周 |

18 维评分涵盖：目标可验证性、停止条件、状态管理、Maker/Checker、6 阶段验证、denylist、预算、kill switch、人工门、监控、回滚等。

### 8. 失败模式目录：15 种翻车场景都有预案

按严重度 S1/S2/S3 分类，每种失败模式都有：症状 / 根因 / 修复 / 预防。

举例：

- **Over-Reach（S1）**：循环越界改了不该改的 → denylist + diff 审查
- **Verifier Theater（S2）**：Checker 假验证 → 6 阶段强制 + 找拒绝理由指令
- **Infinite Fix Loop（S2）**：AI 反复修同一个 bug → 同一根因重试上限 3 次
- **State Rot（S3）**：STATE.md 越积越乱 → 每轮强制 prune
- **Token Burn（S2）**：循环空转烧钱 → watchlist 空→早退 + 预算护栏

循环必须覆盖目标就绪度级别的所有失败模式才能上线。

### 9. 9 种循环模式：选最小的那个

| 场景 | 模式 |
| --- | --- |
| Bug 或测试失败 | localize-repair-validate |
| 单个聚焦功能 | sequential-quality-loop |
| 大规格可分解 | rfc-dag-loop |
| 需要多个创意方案 | parallel-generation-loop |
| PR/CI 自动化 | continuous-pr-loop |
| 每日扫描报告 | daily-triage |
| CI 失败自动修复 | ci-sweeper |
| Issue 分类 | issue-triage |
| 合并后清理 | post-merge-cleanup |

原则：**选能产出证据的最小循环**。单次小修走 fast path，不必启动控制器。

### 10. 多循环协调：不会互相踩

同时跑多个循环时：

- 7 级优先级（生产事故 > CI 修复 > 计划任务 > ...）
- `acting_on` 字段碰撞检测（两个循环想改同一个文件 → 转人工）
- 共享 Human Inbox + 通知去重 + 超 24h 未处理告警
- 资源隔离（独立 worktree / 独立预算 / 独立通知通道）

### 11. 自我修正：每轮强制复盘

每轮循环结束强制写 Post-Run Critique：

- 高噪声项（下次该降级或删除）
- 误报项
- 一条下次改进

**任务循环 vs 系统迭代分离**：任务返工可在批准范围内自动循环；但改 skill / 规则 / 工作流 / soul 必须提迭代提案并经人工批准。同类调整累计 3 次会触发第一性原理分析，晋升为永久规则。

### 12. 运行评分门禁：完成前必须过闸

```bash
python scripts/score_vibe_run.py --live-skill-search --markdown
```

5 维评分（满分 100）：

| 分数 | 含义 | 动作 |
| --- | --- | --- |
| 85-100 | 通过 | 报告证据和剩余风险 |
| 70-84 | 复审 | 修最弱维度或说明接受的取舍 |
| <70 | 失败 | 不准发布，缩减范围或补证据 |

### 13. 能力缺口发现：缺能力先搜再写

运行中发现缺某项能力（如安全审查、浏览器测试）时：

1. 先搜 GitHub 和 findskill 兼容 registry
2. 列出候选 + 许可证 + 维护状态 + 与现有 skill 的重复度
3. 向用户说明推荐哪个、为什么、会改什么文件
4. 用户批准后才导入安装
5. 导入后重新验证

绝不默默写一个新 skill 顶上去。

### 14. 多宿主可移植：装一次到处用

一套配置装到 Claude Code / Codex / Hermes / OpenClaw。默认 `--mode preserve` 保留已有本地配置，覆盖前自动备份。

### 15. 自动化质量关卡：7 个 hook 节点

| 节点 | 作用 |
| --- | --- |
| pre-commit | 格式化、lint、类型检查 |
| pre-test | 单测、E2E |
| pre-loop | 读状态、检查 denylist/kill switch/预算、18 维就绪度评分 |
| post-loop | 写状态、追加运行日志、触发 Post-Run Critique |
| pre-ship | 安全审计、构建验证、Maker-Checker 签字确认 |
| pre-merge | 最终测试、auto-merge 守卫 |
| post-commit | git 状态检查、状态检查点落盘 |

外加 3 类循环质量门：`loop_readiness`（就绪度）/ `loop_budget`（预算）/ `loop_safety`（安全）。

---

## 安装

```bash
git clone https://github.com/digibeing1001/claude-vibe-coding-setup.git
cd claude-vibe-coding-setup
python scripts/validate_setup.py
python scripts/install-universal.py --host claude --mode preserve --install-rules --install-hooks
```

支持的宿主：

| 宿主 | Skill 目录 | 命令 |
| --- | --- | --- |
| Claude Code | `~/.claude/skills` | `--host claude --install-rules --install-hooks` |
| Codex | `~/.codex/skills` | `--host codex` |
| Hermes | `~/.hermes/skills` | `--host hermes` |
| OpenClaw | `~/.openclaw/skills` | `--host openclaw` |
| 全部 | 多个目录 | `--host all` |

只更新指定 skill：

```bash
python scripts/install-universal.py --host claude --mode overwrite --only loop-engineering --only maker-checker --only vibe-coding
```

全局安装后，运行脚本会复制到 `~/.<host>/vibe-coding/scripts/`（含 `loop_state.py` 和 `loop_audit.py`）。

---

## 验证

```bash
# 校验配置包结构（每个 skill 都有标准 SKILL.md，frontmatter 合规）
python scripts/validate_setup.py

# 当前运行的评分门禁
python scripts/score_vibe_run.py --required testing,review,security --live-skill-search --markdown

# 循环就绪度评分（18 维，看某个 pattern 够不够上 L1/L2/L3）
python scripts/loop_audit.py --pattern daily-triage --suggest --badge

# 估算某个循环的 token 成本
python scripts/loop_audit.py --estimate-cost --pattern ci-sweeper --items 5

# 初始化循环状态文件
python scripts/loop_state.py init

# 写入循环退出状态
python scripts/loop_state.py write --pattern daily-triage --outcome complete

# 追加运行日志
python scripts/loop_state.py append-log --pattern daily-triage --outcome complete --duration 12m --tokens 2500
```

---

## 主要入口

| Skill | 用途 |
| --- | --- |
| `vibe-coding` | 主编排入口，所有请求先走这里 |
| `loop-engineering` | 循环工程总入口，加载三层架构和 9 项核心机制 |
| `loop-controller` | 确定性控制器，8 状态转移 + 硬护栏 |
| `loop-state` | STATE.md 状态脊柱管理 |
| `loop-budget` | 预算表 + kill switch |
| `maker-checker` | Maker/Checker 物理分离 + 6 阶段验证 |
| `loop-constraints` | 安全护栏（denylist / auto-merge / MCP 权限） |
| `loop-triage` | 多循环调度 + 碰撞检测 |
| `vibe-run-review` | 运行评分门禁 + 能力缺口发现 |
| `codex-vibe-coding` | Codex 宿主适配 |
| `autonomous-agent-harness` | 跨宿主 harness 设计 |

---

## 运行流程

1. **识别任务类型**：bug / 功能 / 重构 / 研究 / 计划任务
2. **选最小循环**：能产出证据的最小模式（单次小修走 fast path）
3. **定就绪度**：新循环默认 L1
4. **加载核心 skill**：controller / state / budget / constraints
5. **声明预算和停止条件**
6. **跑四节点循环**：Context → Decide → Act → Evaluate
7. **Maker/Checker 分离**：任何代码改动都要 Checker 签字
8. **Post-Run Critique**：完成前强制复盘
9. **评分门禁**：`score_vibe_run.py` ≥ 85 才算完成
10. **L2/L3 升级**：固定节奏触发开发者评审，准备好后采集外部用户反馈

---

## 目录结构

```
.
├── CLAUDE.md                  # 项目记忆入口，所有宿主加载的核心规则
├── hooks.json                 # 7 个 hook 节点 + 3 类循环质量门
├── loops/                     # 循环工程设计文档
│   ├── three-layer-architecture.md   # 三层架构
│   ├── controller.md                  # 确定性控制器
│   ├── state-management.md            # STATE.md 状态脊柱
│   ├── budget-management.md           # 预算和 kill switch
│   ├── maker-checker.md               # Maker/Checker 分离
│   ├── safety-guardrails.md           # 安全护栏
│   ├── readiness-levels.md            # 就绪度分层（L0/L1/L2/L3）
│   ├── failure-modes.md               # 15 种失败模式目录
│   ├── multi-loop-coordination.md     # 多循环协调
│   ├── self-correction.md             # Post-Run Critique + 系统迭代
│   └── patterns/                      # 9 种循环模式
├── skills/                     # 160+ skill（含 7 个新建 loop skill）
│   ├── vibe-coding/                   # 主编排
│   ├── loop-engineering/              # 循环工程总入口
│   ├── loop-controller/               # 确定性控制器
│   ├── loop-state/                    # 状态脊柱
│   ├── loop-budget/                   # 预算管理
│   ├── maker-checker/                 # Maker/Checker
│   ├── loop-constraints/              # 安全护栏
│   ├── loop-triage/                   # 多循环调度
│   └── ...                            # 其余能力 skill
├── scripts/                    # 确定性脚本
│   ├── loop_state.py                  # 状态管理 CLI
│   ├── loop_audit.py                  # 18 维就绪度评分
│   ├── score_vibe_run.py              # 运行评分门禁
│   ├── validate_setup.py              # 配置包校验
│   ├── find_skill_candidates.py       # 能力缺口发现
│   └── install-universal.py           # 多宿主安装
└── docs/                       # 调研和对比文档
```

---

## 一句话总结

**VibeCoding Setup 把 AI 编码从"碰运气的一次性输出"变成"受控、可验证、可恢复、可信任的工程流程"。** AI 写得快不再是风险，因为三层循环、确定性控制器、Maker/Checker 和预算护栏会确保方向对、证据足、成本可控、失败可恢复。
