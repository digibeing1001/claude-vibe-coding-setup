# Agent 自安装指南

> 本文件面向 Claude Code Agent。用户会将本仓库链接发给你，你需要按以下步骤自动完成全套部署。

---

## 你的任务

用户已向你发送了本仓库的 GitHub 链接。你的目标是：

1. **克隆仓库**到临时目录
2. **安装全部配置**（CLAUDE.md + 167 个 Skill + hooks.json）
3. **验证安装**并报告可用 Skill 数量
4. **向用户确认**配置已就绪，可以开始使用

---

## 安装步骤

### Step 1: 克隆仓库

```bash
cd /tmp  # 或系统合适的临时目录
git clone https://github.com/YOUR_USERNAME/claude-vibe-coding-setup.git
cd claude-vibe-coding-setup
```

> 如果用户提供了具体链接，使用用户提供的链接替代上方 URL。

### Step 2: 备份现有配置

```bash
# 创建备份目录
mkdir -p ~/.claude/backups/$(date +%Y%m%d_%H%M%S)

# 备份现有 CLAUDE.md（如存在）
if [ -f ~/.claude/CLAUDE.md ]; then
    cp ~/.claude/CLAUDE.md ~/.claude/backups/$(date +%Y%m%d_%H%M%S)/
    echo "已备份现有 CLAUDE.md"
fi

# 备份现有 skill 列表（如存在）
if [ -d ~/.claude/skills ]; then
    ls ~/.claude/skills > ~/.claude/backups/$(date +%Y%m%d_%H%M%S)/skills.list 2>/dev/null || true
    echo "已备份现有 skill 列表"
fi
```

### Step 3: 安装灵魂文档

```bash
cp CLAUDE.md ~/.claude/CLAUDE.md
echo "✓ CLAUDE.md 已安装"
```

### Step 4: 安装全部 Skill

```bash
mkdir -p ~/.claude/skills

for skill_dir in skills/*/; do
    skill_name=$(basename "$skill_dir")
    
    # 跳过非目录项和 SKILL_REGISTRY.md
    if [ "$skill_name" = "SKILL_REGISTRY.md" ]; then
        continue
    fi
    
    cp -r "$skill_dir" ~/.claude/skills/"$skill_name"
done

echo "✓ $(ls ~/.claude/skills/ | wc -l) 个 Skill 已安装"
```

### Step 5: 安装项目级 Hooks（如适用）

如果当前目录是某个项目的根目录（包含 package.json、.git 等标志）：

```bash
if [ -f "package.json" ] || [ -d ".git" ]; then
    mkdir -p .claude
    cp hooks.json .claude/hooks.json
    echo "✓ hooks.json 已安装到项目 .claude/"
fi
```

### Step 6: 验证安装

```bash
SKILL_COUNT=$(ls ~/.claude/skills/ | wc -l)
echo ""
echo "========================================"
echo "安装验证"
echo "========================================"
echo "Skill 数量: $SKILL_COUNT"
echo "预期: 167+"

if [ "$SKILL_COUNT" -ge 160 ]; then
    echo "✓ Skill 安装正常"
else
    echo "⚠ Skill 数量不足，请检查"
fi

# 检查关键 Skill
for skill in vibe-coding vibe-design-workflow blueprint brainstorming coding-standards; do
    if [ -d ~/.claude/skills/$skill ]; then
        echo "✓ $skill"
    else
        echo "✗ $skill 缺失"
    fi
done

echo ""
echo "灵魂文档前 3 行:"
head -3 ~/.claude/CLAUDE.md
```

### Step 7: 向用户报告

向用户发送如下消息：

---

**Vibe Coding 配置安装完成！**

- ✅ 灵魂文档（CLAUDE.md）已注入
- ✅ 167 个 Skill 已就绪
- ✅ 八阶段工作流已激活
- ✅ 质量关卡（Hooks）已配置

**你现在可以：**
- 说 `vibe coding` 或 `let's build` 启动完整工作流
- 说 `design this` 启动 UI/UX 设计流程
- 任何构建/设计/实现请求都会自动路由到对应 Skill

**工作流阶段：**
感知 → 规划 → 设计 → 执行 → 验证 → 审查 → 发布 → 反思

每阶段有明确的退出标准，AI 会自动推进并征求你的关键决策。

---

## 可选增强（询问用户）

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

1. **不要覆盖用户的个人 settings.json** —— 只更新 CLAUDE.md 和 skills/
2. **保留备份** —— 安装前已自动备份
3. **重启生效** —— 建议用户开启新 Claude Code 会话
4. **权限** —— 首次使用某些 Skill 可能需要确认权限
