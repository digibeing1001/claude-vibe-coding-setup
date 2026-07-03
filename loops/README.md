# Loop Engineering

Loop Engineering 是这套配置的核心骨架。它把"让 AI 写代码"升级为"设计驱动 AI 的循环"——不是 prompt 一次跑一次，而是设计嵌套的反馈系统，让 AI 在受控的循环里迭代，让开发者和真实用户的反馈能回流到下一轮。

## 为什么需要 Loop Engineering

单次 prompt 的瓶颈不在模型能力，而在反馈速度的分层。AI 编码循环（分钟级）跑得越快，开发者反馈（小时级）和真实用户反馈（天/周级）的质量就越决定成败。瓶颈不会消失，只会沿嵌套层次向外迁移——从"代码能否跑通"迁到"规格是否正确"再迁到"产品方向是否成立"。

只优化 AI 编码循环而不升级外层反馈，团队会高速产出"看起来完整"的版本，方向却一直没对齐。

## 三层嵌套反馈架构

整套 Loop Engineering 是三个不同时间尺度的嵌套控制系统：

| 层 | 名称 | 时间尺度 | 驱动者 | 核心产物 |
| --- | --- | --- | --- | --- |
| L1 | Agentic Coding Loop（AI 编码循环） | 分钟级 | AI Agent | 通过验证的可运行代码 |
| L2 | Developer Feedback Loop（开发者反馈） | 小时级 | 开发者 | 可版本化的 Spec + 决策记录 |
| L3 | External Feedback Loop（外部用户反馈） | 天/周级 | 真实用户 | 产品愿景修正 + 优先级重排 |

详细设计见 [three-layer-architecture.md](three-layer-architecture.md)。

## 核心机制

整套 Loop Engineering 由以下机制组成，每个机制都有明确的契约和文件：

| 机制 | 文件 | 作用 |
| --- | --- | --- |
| 确定性控制器 | [controller.md](controller.md) | AI 只建议，控制器独占 8 状态转移 |
| 状态脊柱 | [state-management.md](state-management.md) | STATE.md 记忆 + 带版本交接包 |
| 预算与 kill switch | [budget-management.md](budget-management.md) | token/次数/费用上限 + 一键暂停 |
| Maker/Checker 分离 | [maker-checker.md](maker-checker.md) | 执行者不能标记自己完成 |
| 安全护栏 | [safety-guardrails.md](safety-guardrails.md) | Path Denylist + auto-merge 策略 |
| 就绪度分层 | [readiness-levels.md](readiness-levels.md) | L1→L2→L3 渐进上线 |
| 失败模式目录 | [failure-modes.md](failure-modes.md) | S1/S2/S3 严重度分类 |
| 多 loop 协调 | [multi-loop-coordination.md](multi-loop-coordination.md) | 优先级 + 碰撞检测 |
| 自我修正 | [self-correction.md](self-correction.md) | Post-Run Critique + 任务vs系统分离 |

## Loop 模式目录

可直接复用的生产模式，每个模式都有节奏、风险、就绪度建议：

| 模式 | 节奏 | 风险 | 默认就绪度 |
| --- | --- | --- | --- |
| [localize-repair-validate](patterns/localize-repair-validate.md) | 即时 | Low | L1 |
| [sequential-quality-loop](patterns/sequential-quality-loop.md) | 分钟-小时 | Low | L1 |
| [rfc-dag-loop](patterns/rfc-dag-loop.md) | 小时-天 | Medium | L2 |
| [parallel-generation-loop](patterns/parallel-generation-loop.md) | 分钟-小时 | Medium | L2 |
| [continuous-pr-loop](patterns/continuous-pr-loop.md) | 分钟-小时 | Medium | L2 |
| [daily-triage](patterns/daily-triage.md) | 1天 | Low | L1 |
| [ci-sweeper](patterns/ci-sweeper.md) | 5-15分钟 | Medium | L2 |
| [issue-triage](patterns/issue-triage.md) | 2小时-1天 | Low | L1 |
| [post-merge-cleanup](patterns/post-merge-cleanup.md) | 1天-6小时 | Low | L1 |

详见 [patterns/README.md](patterns/README.md)。

## 与现有配置的关系

| 现有机制 | Loop Engineering 中的位置 |
| --- | --- |
| `continuous-agent-loop` skill | 升级为 Loop Engineering 的 L1 入口 |
| `vibe-coding` orchestrator | 接入三层架构，按层路由 |
| `vibe-run-review` score gate | L1 完成前的验证门 |
| `verification-loop` skill | Maker/Checker 中的 Checker 职责 |
| `hooks.json` 质量门 | 控制器的部分确定性约束 |
| `score_vibe_run.py` | L1 完成证据采集 |
| `find_skill_candidates.py` | L1 能力缺口发现 |

## 入口 skill

- `loop-engineering` — Loop Engineering 总入口，加载三层架构和核心机制
- `loop-controller` — 确定性控制器实现
- `loop-state` — 状态脊柱管理
- `loop-budget` — 预算与 kill switch
- `maker-checker` — Maker/Checker 物理分离
- `loop-constraints` — 安全护栏约束
- `loop-triage` — 调度类 loop 模式

## 落地纪律

1. **L1 必须有可演进 Evals**——不是一次性测试集，Evals 本身要进 L2 循环
2. **L2 建立固定 review 节奏**——每天或每两天深度 review，把"翻译愿景为 spec"变成可训练能力
3. **L3 尽早开启低成本采集**——结构化访谈模板 + 自动化埋点
4. **新 loop 永远先 L1 report-only 跑 1-2 周**，再 L2 assisted，再 L3 unattended
5. **试跑先收小**——选低风险窄场景跑一周，核心交易链路等状态/证据/权限/回滚跑顺后再纳入
