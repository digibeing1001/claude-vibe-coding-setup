# 通用 Vibe Coding 配置

中文 | [English](README.md)

这个仓库把一套可移植的 coding-agent 工作流打包给 Claude Code、Codex、Hermes、OpenClaw 以及类似宿主使用。

这套配置的核心不是一份长提示词，而是一组可执行机制：

- 按宿主安装，默认保留已有本地配置
- 严格校验 `SKILL.md` 发现规则
- 通过按需 skill 控制上下文加载范围
- bug 默认先走 localize -> repair -> validate
- 完成前运行评分门禁
- 运行中发现能力缺口时，主动使用 findskill 兼容发现链查找候选 skill

## 安装

```bash
git clone https://github.com/digibeing1001/claude-vibe-coding-setup.git
cd claude-vibe-coding-setup
python scripts/validate_setup.py
python scripts/install-universal.py --host codex --mode preserve
```

支持的宿主：

| 宿主 | Skill 目录 | 命令 |
| --- | --- | --- |
| Codex | `~/.codex/skills` | `python scripts/install-universal.py --host codex --mode preserve` |
| Claude Code | `~/.claude/skills` | `python scripts/install-universal.py --host claude --mode preserve --install-rules --install-hooks` |
| Hermes | `~/.hermes/skills` | `python scripts/install-universal.py --host hermes --mode preserve` |
| OpenClaw | `~/.openclaw/skills` | `python scripts/install-universal.py --host openclaw --mode preserve` |
| 全部 | 多个目录 | `python scripts/install-universal.py --host all --mode preserve` |

只有在确认要替换已有内容时才使用 `--mode overwrite`。覆盖前会在目标宿主目录下创建备份。

只更新指定 skill：

```bash
python scripts/install-universal.py --host codex --mode overwrite --only codex-vibe-coding --only vibe-coding --only vibe-run-review
```

## 验证

```bash
python scripts/validate_setup.py
python scripts/score_vibe_run.py --required testing,review,agent-harness --live-skill-search --markdown
```

`validate_setup.py` 检查配置包结构：

- 每个内置 skill 都有标准 `SKILL.md`
- frontmatter 包含 `name` 和 `description`
- 缺失或损坏的 gitlink 会被报告
- 非标准 skill 路径会在安装前暴露

`score_vibe_run.py` 检查当前运行：

- 改动范围
- 验证证据
- 必要能力覆盖
- 可维护性信号
- 上下文/说明面变更
- 缺失能力对应的外部 skill 候选

`find_skill_candidates.py` 是运行时发现层：

```bash
python scripts/find_skill_candidates.py --capability security --include-cli --markdown
```

它可以使用本地候选 registry、GitHub 高星搜索、`npx skills find`、`npx clawhub search`，也可以在可用时调用 standalone `findskill`。这个脚本只做发现，不会安装任何东西。

全局安装后，同一组运行工具会被复制到：

```text
~/<host>/vibe-coding/scripts/
~/<host>/vibe-coding/config/
```

Codex 对应路径是 `~/.codex/vibe-coding/scripts`。

## 主要入口

| Skill | 用途 |
| --- | --- |
| `codex-vibe-coding` | Codex 宿主适配和工具映射 |
| `vibe-coding` | 构建、设计、调试、审查、发布的主编排入口 |
| `continuous-agent-loop` | 带停止条件的受控迭代循环 |
| `autonomous-agent-harness` | 跨宿主 harness 设计 |
| `vibe-run-review` | 运行评分和外部 skill 缺口流程 |

## 运行流程

1. 选择当前宿主适配器。
2. 只读取当前阶段需要的项目文件和 skill。
3. bug 默认先走 localize -> repair -> validate。
4. 功能开发选择能产出证据的最小循环。
5. 按风险运行测试、lint、类型检查、构建或浏览器验证。
6. 完成前运行 `vibe-run-review` 或 `scripts/score_vibe_run.py`。
7. 如果必要能力缺失，先搜索 GitHub/ClawHub/Skills CLI，向用户说明候选和原因，获得批准后再安装。

## 外部 Skill 引入

可用的外部 skill 候选记录在 [`docs/EXTERNAL_SKILL_CANDIDATES.md`](docs/EXTERNAL_SKILL_CANDIDATES.md) 和 `config/skill-candidates.json`。

运行时策略：

1. 本地已有 skill 能覆盖时优先使用本地 skill。
2. 如果仍有缺口，先搜索 GitHub 或 findskill 兼容 registry。
3. 比较候选的许可证、维护状态、宿主适配性和重复度。
4. 导入或安装外部 skill 前先获得用户批准。
5. 导入后再次运行验证。

## 调研依据

这次迭代基于：

- Anthropic skill 指南：简洁 skill、渐进式披露、真实任务验证、确定性脚本
- Claude Code 指南：用 hooks 承载不可协商的自动化，用简洁项目记忆减少噪声
- Agentless：定位、修复、补丁验证可以作为默认 bug 循环
- SWE-agent：agent-computer interface 会影响软件工程 agent 表现
- OpenHands 类型 harness：长任务需要状态、沙箱意识、评估和恢复机制

更多细节见 [`docs/RESEARCH.md`](docs/RESEARCH.md) 和 [`docs/COMPARISON.md`](docs/COMPARISON.md)。
