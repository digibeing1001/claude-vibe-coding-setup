# 原始配置与改进配置对比

生成日期：2026-06-15

## 摘要

原始仓库是一套偏 Claude Code 的 Vibe Coding 工作流合集。当前版本已经调整为通用型 Vibe Coding Harness，可安装到 Codex、Claude Code、Hermes、OpenClaw 以及类似宿主。

这次改进的重点不是增加更长的提示词，而是把运行质量拆成可验证机制：安装安全、skill 发现、评分门禁、能力缺口主动搜索、外部 skill 审批引入、Codex runtime tools 可调用。

## 总体对比

| 领域 | 原始配置 | 当前改进版 |
| --- | --- | --- |
| 宿主支持 | 主要面向 Claude Code | 支持 Codex、Claude Code、Hermes、OpenClaw |
| 安装行为 | 偏复制/覆盖 | 默认 `preserve`；支持 `--only` 定点覆盖；覆盖前备份 |
| Skill 发现 | 部分入口是小写 `skill.md`；存在损坏的 `gstack` gitlink | 标准 `SKILL.md`；替换损坏 gitlink；验证器可捕获回归 |
| Codex 可用性 | 没有 Codex 专用入口 | 新增 `codex-vibe-coding`，并把 runtime scripts 安装到 `~/.codex/vibe-coding/scripts` |
| Harness 形态 | 更像提示词合集 | 宿主适配、状态/证据契约、预算、停止条件、评分门 |
| Bug 循环 | 宽泛的 autonomous guidance | 默认 localize -> repair -> validate，再按需升级 |
| 完成标准 | 依赖人工或模型自觉 review | `score_vibe_run.py` 运行评分，要求证据和能力覆盖 |
| 能力缺口 | 用户需要主动提出，或 agent 临时发挥 | Phase 0 主动探测能力需求；缺口触发 findskill 兼容发现链 |
| 外部 skill | 未系统跟踪 | `config/skill-candidates.json` + `docs/EXTERNAL_SKILL_CANDIDATES.md` |
| 安全边界 | 没有明确外部 skill intake | 发现候选但不自动安装；用户批准后导入并重新验证 |
| 文档 | README 偏单语和安装说明 | 英文 README、中文 README、中文调研与对比文档 |

## 迭代过程

### 第一轮：可安装、可验证、可跨宿主

第一轮解决了基础阻塞：

- 新增 `scripts/install-universal.py`
- 新增 `scripts/validate_setup.py`
- 新增 `skills/codex-vibe-coding/SKILL.md`
- 将关键入口从 `skill.md` 统一为 `SKILL.md`
- 修复 `skills/gstack` 损坏 gitlink
- 给缺少 frontmatter 的 skill 补齐元数据
- 强化 `autonomous-agent-harness` 和 `continuous-agent-loop`

第一轮验证：

```text
python scripts/validate_setup.py
Skills: 156
OK: 156
Warnings: 0
Errors: 0

python scripts/install-universal.py --host codex --mode preserve
installed=133 skipped=23 overwritten=0
```

### 第二轮：运行评分与主动 skill 发现

第二轮把调研结论落成可执行机制：

- 新增 `scripts/score_vibe_run.py`
- 新增 `scripts/find_skill_candidates.py`
- 新增 `skills/vibe-run-review`
- 新增 `config/skill-candidates.json`
- 新增 `docs/EXTERNAL_SKILL_CANDIDATES.md`
- 安装器支持 `--only` 定点更新
- 安装器默认同步 runtime tools 到宿主 `vibe-coding/scripts`
- `vibe-coding` Phase 0 会判断任务所需能力
- `find_skill_candidates.py` 可调用 GitHub、Skills CLI、ClawHub 和 standalone `findskill`

第二轮验证：

```text
python -m py_compile scripts\install-universal.py scripts\validate_setup.py scripts\score_vibe_run.py scripts\find_skill_candidates.py
exit code: 0

python scripts\validate_setup.py
Skills: 157
OK: 157
Warnings: 0
Errors: 0
Notices: 113

python scripts\find_skill_candidates.py --capability security --query "claude code security skill" --limit 3 --min-stars 50 --timeout 10 --markdown
exit code: 0
Local registry candidates included BehiSecc/VibeSec-Skill and trailofbits/skills.
GitHub live search returned high-star security skill candidates.

python scripts\score_vibe_run.py --base HEAD~1 --head HEAD --required testing,review,security,browser-qa,findskill --live-skill-search --search-limit 2 --evidence docs\COMPARISON.md --markdown
Status: pass
Total: 92/100
Capability coverage: 20/20
Maintainability: 20/20
```

Codex 安装后验证：

```text
python scripts\install-universal.py --host codex --mode overwrite --only codex-vibe-coding --only vibe-coding --only vibe-run-review --only continuous-agent-loop
installed=0 skipped=0 overwritten=4
files: tool:overwritten, tool:overwritten, tool:overwritten, tool:overwritten, config:overwritten

python $HOME\.codex\vibe-coding\scripts\score_vibe_run.py --root . --skills-dir $HOME\.codex\skills --required testing,review,security,browser-qa,findskill --evidence docs\COMPARISON.md --markdown
Status: pass
Total: 92/100

python $HOME\.codex\vibe-coding\scripts\find_skill_candidates.py --root . --capability findskill --query "OpenClaw findskill skill registry" --limit 3 --min-stars 50 --timeout 10 --markdown
exit code: 0
Local registry candidates included openclaw/clawhub and vercel-labs/skills.
```

### 第三轮：中文文档补齐

第三轮补齐了中文入口：

- 新增 `README.zh-CN.md`
- 英文 README 顶部加入语言切换入口
- 本文档和调研文档改写为中文，并同步到当前机制状态

最近一次验证：

```text
python scripts\validate_setup.py
Skills: 157
OK: 157
Warnings: 0
Errors: 0
Notices: 113
```

## 改进后的实际优势

- Codex 可以直接调用 `codex-vibe-coding`、`vibe-coding`、`vibe-run-review`。
- 离开本仓库后，Codex 仍可通过 `~/.codex/vibe-coding/scripts` 调用评分和 skill 发现工具。
- 能力缺口不是靠用户提醒，而是在 Phase 0 和完成前评分中主动发现。
- 外部 skill 搜索不是一次性调研，而是运行时按任务需要触发。
- 外部 skill 不会被自动安装，避免把第三方内容静默塞进本地环境。
- 评分门会把验证证据、能力覆盖、可维护性、上下文/说明面变更显式化。
- README 已有英文和中文版本，降低中文用户安装和维护成本。

## 仍然存在的权衡

- Live GitHub 搜索可能遇到 rate limit。
- `npx skills find`、`npx clawhub search`、standalone `findskill` 是否可用取决于本机环境。
- 候选 skill 的星标、安装量和来源只能帮助排序，仍需要检查许可证、维护状态和实际内容。
- 当前评分器是轻量启发式门禁，不替代测试、CI、安全审查和人工判断。
- 跨宿主 hook 机制差异仍需按 Hermes/OpenClaw 的实际格式继续适配。
