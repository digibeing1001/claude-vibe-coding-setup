# Claude Code Vibe Coding Setup Installer (PowerShell)
# Run as: .\scripts\install.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Claude Code Vibe Coding Setup Installer" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Claude Code
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $claudeCmd) {
    $claudeCmd = Get-Command claude-code -ErrorAction SilentlyContinue
}

if ($claudeCmd) {
    Write-Host "✓ Claude Code found" -ForegroundColor Green
} else {
    Write-Host "✗ Claude Code not found." -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Claude Code first:" -ForegroundColor Yellow
    Write-Host "  npm install -g @anthropic-ai/claude-code"
    Write-Host "  or visit: https://claude.ai/code"
    Write-Host ""
    exit 1
}

# 设置路径
$clauserDir = "$env:USERPROFILE\.claude"
$skillsDir = "$clauserDir\skills"
$backupDir = "$clauserDir\backups\$(Get-Date -Format 'yyyyMMdd_HHmmss')"

# 创建备份
Write-Host "Creating backup at: $backupDir" -ForegroundColor DarkGray
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

if (Test-Path "$clauserDir\CLAUDE.md") {
    Copy-Item "$clauserDir\CLAUDE.md" $backupDir
    Write-Host "  ✓ Backed up CLAUDE.md" -ForegroundColor Green
}

if (Test-Path $skillsDir) {
    Get-ChildItem $skillsDir -Name | Out-File "$backupDir\skills.list"
    Write-Host "  ✓ Backed up skill list" -ForegroundColor Green
}

Write-Host ""

# 复制灵魂文档
Write-Host "Installing soul document (CLAUDE.md)..." -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $PSScriptRoot
Copy-Item "$scriptDir\CLAUDE.md" "$clauserDir\CLAUDE.md" -Force
Write-Host "  ✓ CLAUDE.md installed" -ForegroundColor Green

# 复制 hooks.json
Write-Host ""
$installHooks = Read-Host "Install hooks.json to current project? (y/N)"
if ($installHooks -eq 'y' -or $installHooks -eq 'Y') {
    New-Item -ItemType Directory -Path ".claude" -Force | Out-Null
    Copy-Item "$scriptDir\hooks.json" ".claude\hooks.json" -Force
    Write-Host "  ✓ hooks.json installed to .claude\hooks.json" -ForegroundColor Green
} else {
    Write-Host "  - Skipped hooks.json" -ForegroundColor DarkGray
}

# 复制 Skills
Write-Host ""
Write-Host "Installing Skills..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $skillsDir -Force | Out-Null

$repoSkills = "$scriptDir\skills"
$skillCount = 0

Get-ChildItem $repoSkills -Directory | ForEach-Object {
    $skillName = $_.Name
    $target = "$skillsDir\$skillName"

    # 备份已存在的
    if (Test-Path $target) {
        Copy-Item $target "$backupDir\$skillName" -Recurse -Force -ErrorAction SilentlyContinue
    }

    Copy-Item $_.FullName $target -Recurse -Force
    $skillCount++
}

Write-Host "  ✓ $skillCount skills installed" -ForegroundColor Green

# 检查插件
$pluginDir = "$env:USERPROFILE\.claude\plugins\awesome-claude-code-toolkit"
Write-Host ""
if (Test-Path $pluginDir) {
    Write-Host "✓ awesome-claude-code-toolkit plugin already installed" -ForegroundColor Green
} else {
    Write-Host "⚠ awesome-claude-code-toolkit plugin not found" -ForegroundColor Yellow
    Write-Host "  You can install it from: https://github.com/rohitg00/awesome-claude-code-toolkit" -ForegroundColor DarkGray
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  - Soul document: $clauserDir\CLAUDE.md"
Write-Host "  - Skills: $skillCount installed to $skillsDir"
Write-Host "  - Backup: $backupDir"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Restart Claude Code or start a new session"
Write-Host "  2. Try: 'vibe coding' or 'let's build a dashboard'"
Write-Host "  3. Check: (ls $skillsDir).Count"
Write-Host ""
