#!/bin/bash
set -e

echo "========================================"
echo "Claude Code Vibe Coding Setup Installer"
echo "========================================"
echo ""

# 检测操作系统
OS="unknown"
case "$(uname -s)" in
    Linux*)     OS="linux";;
    Darwin*)    OS="macos";;
    CYGWIN*|MINGW*|MSYS*) OS="windows";;
esac

echo "Detected OS: $OS"
echo ""

# 检查 Claude Code 是否已安装
if command -v claude &> /dev/null; then
    echo "✓ Claude Code found: $(claude --version 2>/dev/null || echo 'installed')"
elif command -v claude-code &> /dev/null; then
    echo "✓ Claude Code found: $(claude-code --version 2>/dev/null || echo 'installed')"
else
    echo "✗ Claude Code not found."
    echo ""
    echo "Please install Claude Code first:"
    echo "  npm install -g @anthropic-ai/claude-code"
    echo "  or visit: https://claude.ai/code"
    echo ""
    exit 1
fi

# 设置路径
CLAUDE_DIR="$HOME/.claude"
SKILLS_DIR="$CLAUDE_DIR/skills"
BACKUP_DIR="$CLAUDE_DIR/backups/$(date +%Y%m%d_%H%M%S)"

# 创建备份
echo "Creating backup at: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

if [ -f "$CLAUDE_DIR/CLAUDE.md" ]; then
    cp "$CLAUDE_DIR/CLAUDE.md" "$BACKUP_DIR/"
    echo "  ✓ Backed up CLAUDE.md"
fi

if [ -d "$SKILLS_DIR" ]; then
    # 备份现有 skill 列表
    ls "$SKILLS_DIR" > "$BACKUP_DIR/skills.list" 2>/dev/null || true
    echo "  ✓ Backed up skill list"
fi

echo ""

# 复制灵魂文档
echo "Installing soul document (CLAUDE.md)..."
cp "$(dirname "$0")/../CLAUDE.md" "$CLAUDE_DIR/CLAUDE.md"
echo "  ✓ CLAUDE.md installed"

# 复制 hooks.json（项目级，询问用户）
echo ""
read -p "Install hooks.json to current project? (y/N): " install_hooks
if [[ $install_hooks =~ ^[Yy]$ ]]; then
    mkdir -p .claude
    cp "$(dirname "$0")/../hooks.json" .claude/hooks.json
    echo "  ✓ hooks.json installed to ./.claude/hooks.json"
else
    echo "  - Skipped hooks.json (you can copy it manually to your project's .claude/ directory)"
fi

# 复制 Skills
echo ""
echo "Installing Skills..."
mkdir -p "$SKILLS_DIR"

REPO_SKILLS="$(dirname "$0")/../skills"
SKILL_COUNT=0

for skill_dir in "$REPO_SKILLS"/*; do
    if [ -d "$skill_dir" ]; then
        skill_name=$(basename "$skill_dir")
        # 跳过非 skill 目录（如 SKILL_REGISTRY.md）
        if [ "$skill_name" = "SKILL_REGISTRY.md" ]; then
            continue
        fi

        target="$SKILLS_DIR/$skill_name"

        # 如果已存在，备份后覆盖
        if [ -e "$target" ]; then
            rm -rf "$BACKUP_DIR/$skill_name" 2>/dev/null || true
            cp -r "$target" "$BACKUP_DIR/" 2>/dev/null || true
        fi

        cp -r "$skill_dir" "$target"
        ((SKILL_COUNT++))
    fi
done

echo "  ✓ $SKILL_COUNT skills installed"

# 检查 awesome-claude-code-toolkit 插件
PLUGIN_DIR="$HOME/.claude/plugins/awesome-claude-code-toolkit"
echo ""
if [ -d "$PLUGIN_DIR" ]; then
    echo "✓ awesome-claude-code-toolkit plugin already installed"
else
    echo "⚠ awesome-claude-code-toolkit plugin not found"
    echo "  You can install it from: https://github.com/rohitg00/awesome-claude-code-toolkit"
    echo "  Or run: git clone https://github.com/rohitg00/awesome-claude-code-toolkit ~/.claude/plugins/awesome-claude-code-toolkit"
fi

# 完成
echo ""
echo "========================================"
echo "Installation Complete!"
echo "========================================"
echo ""
echo "Summary:"
echo "  - Soul document: $CLAUDE_DIR/CLAUDE.md"
echo "  - Skills: $SKILL_COUNT installed to $SKILLS_DIR"
echo "  - Backup: $BACKUP_DIR"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code or start a new session"
echo "  2. Try: 'vibe coding' or 'let's build a dashboard'"
echo "  3. Check: ls ~/.claude/skills/ | wc -l"
echo ""
echo "To uninstall: restore from $BACKUP_DIR"
echo ""
