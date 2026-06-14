# 调研笔记：通用 Vibe Coding Harness

生成日期：2026-06-15

## 当前结论

这套配置已经从「Claude Code 专用提示词合集」调整为「跨宿主 Vibe Coding Harness」。调研结论没有停留在 README 里的愿景描述，而是落到安装器、验证脚本、运行评分、能力缺口发现、外部 skill 候选清单和 Codex 可调用的本地 runtime tools 上。

现在的设计重点是让 agent 在运行中保持三个动作：

1. 先判断当前任务需要哪些能力。
2. 本地已有能力能覆盖时直接调用本地 skill。
3. 发现能力缺口时主动查找外部候选，但不自动安装，先给用户说明候选和原因。

## Skill 生态调研信号

| 来源 | 调研发现 | 已落地的仓库变化 |
| --- | --- | --- |
| [openclaw/clawhub](https://github.com/openclaw/clawhub) | OpenClaw 有公开 skill/plugin registry，支持搜索、查看、安装、pin、本地保护、星标、评论、审核和向量搜索。 | `find_skill_candidates.py` 已支持 ClawHub/findskill 兼容发现链；`config/skill-candidates.json` 记录 `openclaw/clawhub`。 |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | Skills CLI 支持 Codex、Claude Code、OpenClaw 等宿主，并提供 `npx skills find`、`add --list`、`use`、按宿主安装等能力。 | `find_skill_candidates.py` 可调用 `npx skills find`；安装器也把运行脚本复制到宿主目录，便于跨项目使用。 |
| [anthropics/skills](https://github.com/anthropics/skills) | 公开 Agent Skills 示例和打包参考。 | 作为打包和结构参考记录，未进行整包内嵌。 |
| [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Claude Code 生态索引，覆盖 skills、hooks、commands、MCP servers 和工作流。 | 作为能力缺口时的候选来源写入 registry。 |
| [rohitg00/awesome-claude-code-toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) | 展示了 agent、skill、command、hook、MCP config 组合打包方式。 | 作为发现来源保留，不做默认批量安装。 |
| [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) | 偏生产工程实践的 skill 示例，覆盖 review、testing、frontend、web 质量等方向。 | 作为 review/testing/frontend 候选来源记录。 |
| [BehiSecc/VibeSec-Skill](https://github.com/BehiSecc/VibeSec-Skill) | 面向 Vibe Coding 安全审查的候选 skill。 | 作为 security 能力缺口候选；导入前需要用户确认和验证。 |
| [trailofbits/skills](https://github.com/trailofbits/skills) | Trail of Bits 的安全研究、漏洞发现和审计 skill 来源。 | 作为安全审计候选来源记录，适合在本地安全 skill 不足时评估。 |
| [kenryu42/cc-safety-net](https://github.com/kenryu42/cc-safety-net) | 基于 hook 的危险命令拦截模式。 | 作为 git/command safety 候选；需要按目标宿主 hook 机制适配。 |

## 论文与最佳实践

| 来源 | 关键发现 | 已落地的机制 |
| --- | --- | --- |
| [Anthropic Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Skill 应保持简洁，用渐进式披露加载额外材料，用真实任务验证，对确定性操作优先用脚本。 | 主入口 skill 已缩短；新增 `validate_setup.py`、`score_vibe_run.py` 和 `find_skill_candidates.py`。 |
| [Claude Code best practices](https://code.claude.com/docs/en/best-practices) | 项目记忆要简洁；hooks/skills 承载确定性流程；完成前需要证据。 | `CLAUDE.md` 改成运行边界、证据边界和能力缺口处理规则。 |
| [SWE-agent](https://arxiv.org/abs/2405.15793) | Agent-computer interface 会显著影响软件工程 agent 表现。 | 新增宿主适配、工具映射和标准化 evidence/score 输出。 |
| [Agentless](https://arxiv.org/abs/2407.01489) | 许多 bug 可通过定位、修复、补丁验证解决，不需要一开始就重型编排。 | `continuous-agent-loop` 和 `vibe-coding` 默认 bug 路径为 localize -> repair -> validate。 |
| [OpenHands](https://arxiv.org/abs/2407.16741) | 长任务 coding agent 需要 sandbox awareness、交互工具、状态、恢复和评估钩子。 | `autonomous-agent-harness`、`continuous-agent-loop` 和 `vibe-run-review` 增加状态、预算、停止条件和评分门。 |

## 当前已落地机制

- `scripts/install-universal.py`：支持 Codex、Claude Code、Hermes、OpenClaw；默认 `preserve`；支持 `--only` 定点覆盖；会把 runtime scripts/config 安装到 `~/<host>/vibe-coding/`。
- `scripts/validate_setup.py`：检查 skill 包结构、`SKILL.md`、frontmatter 和 gitlink 问题。
- `scripts/score_vibe_run.py`：从改动范围、验证证据、能力覆盖、可维护性、上下文/说明面变化给当前运行打分。
- `scripts/find_skill_candidates.py`：发现外部 skill 候选；支持本地 registry、GitHub 高星搜索、`npx skills find`、`npx clawhub search` 和 standalone `findskill`。
- `skills/vibe-run-review`：完成前评分门；当能力不足时触发外部 skill 候选提案。
- `skills/vibe-coding`：Phase 0 主动判断任务能力需求；发现缺口时触发发现链，而不是等用户手动下命令。
- `skills/codex-vibe-coding`：Codex 宿主适配；说明如何从 `~/.codex/vibe-coding/scripts` 调用 runtime tools。
- `config/skill-candidates.json`：外部候选 registry。
- `docs/EXTERNAL_SKILL_CANDIDATES.md`：外部 skill 引入清单和 intake 检查表。
- `README.zh-CN.md`：中文 README，方便中文用户按机制理解安装和使用方式。

## 安全与供应链决策

外部 skill 视为代码供应链输入。当前机制会在运行中主动发现并提出候选，但不会自动导入、安装或覆盖本地 skill。导入流程必须满足：

1. 说明为什么当前任务需要这个外部 skill。
2. 对比本地已有 skill，避免重复。
3. 检查许可证、维护状态、宿主适配性和安装影响。
4. 获得用户批准后再导入。
5. 导入后重新运行 `validate_setup.py` 和 `score_vibe_run.py`。

## 仍需注意

- GitHub live search 可能受到 rate limit 影响。
- `npx skills find`、`npx clawhub search`、standalone `findskill` 是可选工具；不可用时脚本会退回本地 registry 和 GitHub 搜索。
- 星标和安装量只能作为候选排序信号，不能等同于可信任。
- 安全、支付、认证、迁移、外部写入等高风险任务仍需要专项审查。
