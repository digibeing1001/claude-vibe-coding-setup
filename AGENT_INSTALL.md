# Agent 自安装指南

> 本文件面向 Claude Code Agent。用户会将本仓库链接发给你，你需要按以下步骤自动完成全套部署。

---

## 你的任务

用户已向你发送了本仓库的 GitHub 链接。你的目标是：

1. **克隆仓库**到临时目录
2. **先验证安装包**（`scripts/validate_setup.py`）
3. **按宿主安装配置**（Codex / Claude Code / Hermes / OpenClaw）
4. **默认保留已有同名 Skill**，不要覆盖用户个人规则
5. **验证安装**并报告新增、跳过、覆盖数量
6. **向用户确认**配置已就绪，可以开始使用

---

## 安装步骤

### Step 1: 克隆仓库

```bash
cd /tmp  # 或系统合适的临时目录
git clone https://github.com/YOUR_USERNAME/claude-vibe-coding-setup.git
cd claude-vibe-coding-setup
```

> 如果用户提供了具体链接，使用用户提供的链接替代上方 URL。

### Step 2: 验证仓库

```bash
python scripts/validate_setup.py
```

如果验证失败，先修复失败项，不要继续安装。

### Step 3: 选择宿主并安装

如果用户没有指定宿主：

- 在 Codex 会话里，默认安装到 Codex。
- 在 Claude Code 会话里，默认安装到 Claude Code。
- 如果用户要求通用安装，安装到 `all`。

```bash
# Codex：默认保留已有本地 Skill
python scripts/install-universal.py --host codex --mode preserve

# Claude Code：安装 rules/hooks 时也保留已有文件
python scripts/install-universal.py --host claude --mode preserve --install-rules --install-hooks

# Hermes / OpenClaw
python scripts/install-universal.py --host hermes --mode preserve
python scripts/install-universal.py --host openclaw --mode preserve

# 全部宿主
python scripts/install-universal.py --host all --mode preserve
```

只有用户明确要求覆盖时才使用：

```bash
python scripts/install-universal.py --host codex --mode overwrite
```

覆盖模式会创建备份目录；报告中必须告诉用户备份路径。

### Step 4: 验证安装结果

```bash
# Codex
test -f ~/.codex/skills/vibe-coding/SKILL.md
test -f ~/.codex/skills/codex-vibe-coding/SKILL.md

# Claude Code
test -f ~/.claude/skills/vibe-coding/SKILL.md
```

### Step 5: 向用户报告

向用户发送如下消息：

---

**Vibe Coding 配置安装完成！**

- ✅ 安装包验证已通过
- ✅ 已安装到目标宿主：<Codex/Claude/Hermes/OpenClaw>
- ✅ 新增 Skill：<N>
- ✅ 保留已有同名 Skill：<N>
- ✅ 覆盖 Skill：<N>（如有）
- ✅ 备份目录：<path>

**你现在可以：**
- 对 Codex/Claude 说 `vibe coding` 或 `let's build` 启动完整工作流
- 说 `design this` 启动 UI/UX 设计流程
- 任何构建/设计/实现请求都会自动路由到对应 Skill

**工作流阶段：**
感知 → 规划 → 设计 → 执行 → 验证 → 审查 → 发布 → 反思

每阶段有明确的退出标准，AI 会自动推进并征求你的关键决策。

---

## 可选增强（询问用户，不要擅自安装）

安装完成后，询问用户是否需要以下增强：

### 1. Claude Mem（跨会话记忆）

```bash
# 检查是否已安装 claude-mem MCP
# 如未安装，提供安装指引
```

Claude Mem 能让 AI 记住过往会话中的决策和模式，提升长期协作效率。

### 2. Awesome Claude Code Toolkit（Plugin）

```bash
# 安装 120+ agent/plugin
claude /plugin marketplace add rohitg00/awesome-claude-code-toolkit
```

提供额外的架构设计、代码审查、部署自动化等能力。

### 3. 模型配置优化

询问用户的模型偏好，如需调整可在 settings.json 中配置：
- effortLevel: high / medium / low
- 是否启用 autoDream

---

## 注意事项

1. **不要覆盖用户的个人 settings.json**
2. **默认 preserve** —— 不要覆盖已有同名 Skill
3. **覆盖必须显式** —— 只有用户要求时才 `--mode overwrite`
4. **重启生效** —— 建议用户开启新宿主会话
5. **权限** —— 外部发布、定时任务、浏览器/电脑控制、记忆写入都需要明确授权
