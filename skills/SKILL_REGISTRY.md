# Skill 注册表

本仓库不直接托管第三方 Skill 源码，而是提供精选 Skill 清单及获取方式。

## 核心工作流 Skill（必备）

| Skill | 来源 | 用途 | 安装方式 |
|-------|------|------|---------|
| `vibe-coding` | ECC / Community | Vibe Coding 统一编排器 | 已随 Claude Code 内置或从 ECC 获取 |
| `vibe-design-workflow` | ECC / Community | UI/UX 设计工作流编排 | 同上 |
| `brainstorming` | ECC / Community | 需求澄清与头脑风暴 | 同上 |
| `blueprint` | ECC / Community | 多步骤工程计划生成 | 同上 |
| `writing-plans` | ECC / Community | 通用计划编写 | 同上 |
| `executing-plans` | ECC / Community | 计划执行 | 同上 |
| `test-driven-development` | ECC / Community | TDD | 同上 |
| `systematic-debugging` | ECC / Community | 系统调试 | 同上 |
| `verification-before-completion` | ECC / Community | 完成前验证 | 同上 |
| `using-superpowers` | ECC / Community | Skill 使用指南 | 同上 |
| `using-git-worktrees` | ECC / Community | Git 工作树隔离 | 同上 |

## 设计 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `frontend-design-3-0.1.0` | `.agents/skills` | 前端视觉设计 |
| `frontend-design-direction` | `.agents/skills` | 设计方向 |
| `design-system` | `.agents/skills` | 设计系统 |
| `prototype` | `.agents/skills` | 原型生成 |
| `motion-patterns` | `.agents/skills` | 动效模式 |
| `motion-foundations` | `.agents/skills` | 动效基础 |
| `motion-advanced` | `.agents/skills` | 高级动效 |
| `make-interfaces-feel-better` | `.agents/skills` | 界面打磨 |

## 质量 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `coding-standards` | `.agents/skills` | 编码规范 |
| `tdd-workflow` | `.agents/skills` | TDD 工作流 |
| `error-handling` | `.agents/skills` | 错误处理 |
| `e2e-testing` | `.agents/skills` | E2E 测试 |
| `browser-qa` | `.agents/skills` | 浏览器 QA |
| `ai-regression-testing` | `.agents/skills` | AI 回归测试 |
| `test-runner-1.0.0` | `.agents/skills` | 测试运行 |
| `caveman-review` | `.agents/skills` | 精简审查 |
| `plankton-code-quality` | `.agents/skills` | 代码质量 |
| `ui-design-review` | `.agents/skills` | UI 审查 |
| `review` | mattpocock/skills | 双轴代码审查（标准 + 规范） |
| `design-review` | garrytan/gstack | 视觉不一致与 AI slop 检测 |
| `qa-mattpocock` | mattpocock/skills | 交互式 QA 会话 |

## 架构 / 设计 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `design-an-interface` | mattpocock/skills | API/模块接口设计（Design It Twice） |
| `ubiquitous-language` | mattpocock/skills | DDD 术语表提取与规范化 |
| `request-refactor-plan` | mattpocock/skills | 重构计划与增量提交 |

## 调试 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `debug-pro-1.0.0` | `.agents/skills` | 专业调试 |
| `diagnose` | `.agents/skills` | 诊断 |
| `investigate` | garrytan/gstack | 系统性根因调试 |

## 安全 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `security-auditor-1.0.0` | `.agents/skills` | 安全审计 |
| `security-scan` | `.agents/skills` | 安全扫描 |
| `cso` | garrytan/gstack | OWASP + STRIDE 安全审计 |

## 文档 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `document-generate` | garrytan/gstack | Diataxis 文档生成（教程/指南/参考/解释） |

## 调试 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `debug-pro-1.0.0` | `.agents/skills` | 专业调试 |
| `diagnose` | `.agents/skills` | 诊断 |

## 发布 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `deployment-patterns` | `.agents/skills` | 部署模式 |
| `canary-watch` | `.agents/skills` | 金丝雀监控 |
| `production-audit` | `.agents/skills` | 生产审计 |

## 安全 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `security-auditor-1.0.0` | `.agents/skills` | 安全审计 |
| `security-scan` | `.agents/skills` | 安全扫描 |

## AI / Agent 工程 Skill

| Skill | 来源 | 用途 |
|-------|------|------|
| `ai-first-engineering` | `.agents/skills` | AI 优先工程 |
| `agentic-engineering` | `.agents/skills` | Agent 工程 |
| `continuous-agent-loop` | `.agents/skills` | 持续 Agent 循环 |
| `autonomous-agent-harness` | `.agents/skills` | 自主 Agent 框架 |
| `agent-eval` | `.agents/skills` | Agent 评估 |

## GSD 工作流 Skill（83 个）

完整 GSD Skill 套件包括 `gsd-new-project`, `gsd-plan-phase`, `gsd-execute-phase`, `gsd-debug`, `gsd-code-review`, `gsd-ship` 等 83 个 Skill。

来源：`~/.claude/skills/`（备份恢复）

## 安装说明

### 方式一：使用 install.sh 脚本（推荐）

```bash
./scripts/install.sh
```

### 方式二：手动安装

1. 复制 `CLAUDE.md` 到 `~/.claude/CLAUDE.md`
2. 复制 `hooks.json` 到项目根目录 `.claude/hooks.json`
3. 按需从 `.agents/skills/` 复制 Skill 到 `~/.claude/skills/`
4. 安装 awesome-claude-code-toolkit 插件

### 方式三：Awesome Claude Code Toolkit（Plugin）

```bash
# 插件提供 120+ agent / plugin
# 安装于 ~/.claude/plugins/awesome-claude-code-toolkit/
```

## 完整 Skill 列表

参见 [CLAUDE.md 附录](../CLAUDE.md) 或运行：

```bash
ls ~/.claude/skills/
```
