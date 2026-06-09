# Claude Code 生产级 Vibe Coding 配置

> 一套面向 B 端交付的 AI Native 软件开发工作流配置，将 Claude Code 从"代码补全工具"升级为"全栈工程协作者"。

---

## 前置：安装 Claude Code

如果你还没有安装 Claude Code，请先完成安装：

### macOS / Linux

```bash
# 通过 npm 安装（推荐）
npm install -g @anthropic-ai/claude-code

# 或使用 npx（无需全局安装）
npx @anthropic-ai/claude-code
```

### Windows

```powershell
# 通过 npm 安装（推荐）
npm install -g @anthropic-ai/claude-code

# 或使用 npx
npx @anthropic-ai/claude-code
```

### 验证安装

```bash
claude --version
# 预期输出类似：claude 0.x.x
```

首次运行会提示登录 Anthropic 账号，按提示完成即可。

更多安装方式见官方文档：[claude.ai/code](https://claude.ai/code)

---

## 一键部署（推荐）

### 方式一：让 Claude Code 自己安装（最简单）

**把下面这段指令丢给 Claude Code，它会自动完成全套部署：**

```text
帮我安装 vibe coding 工作流配置。从 https://github.com/YOUR_USERNAME/claude-vibe-coding-setup 克隆仓库到临时目录，然后运行安装脚本，把 CLAUDE.md 和 skills 部署到 ~/.claude/。安装完成后告诉我有多少个 skill 可用。
```

> 替换 `YOUR_USERNAME` 为你的 GitHub 用户名。

### 方式二：手动运行安装脚本

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/claude-vibe-coding-setup.git
cd claude-vibe-coding-setup

# 2. 运行安装脚本
# macOS / Linux:
./scripts/install.sh

# Windows (PowerShell):
.\scripts\install.ps1
```

安装脚本会自动：
1. 备份现有 `~/.claude/CLAUDE.md` 和 skill 列表
2. 复制新的灵魂文档
3. 复制 167 个 skill 到 `~/.claude/skills/`
4. 可选：在项目根目录安装 `hooks.json`

### 方式三：手动复制

```bash
# 灵魂文档
cp CLAUDE.md ~/.claude/CLAUDE.md

# Skills（全部复制）
cp -r skills/* ~/.claude/skills/

# 项目级 Hooks（进入你的项目目录后）
mkdir -p .claude
cp hooks.json .claude/hooks.json
```

### 验证部署

```bash
# 检查 skill 数量
ls ~/.claude/skills/ | wc -l
# 预期：167+

# 检查灵魂文档
head -5 ~/.claude/CLAUDE.md
```

部署完成后，**重启 Claude Code 或开启新会话**即可生效。

---

## 这是什么？

本项目是一套**生产级 Vibe Coding 配置**，包含：

- **灵魂文档**（CLAUDE.md）—— 定义 AI 的行为准则、质量标准和决策逻辑
- **167 个 Skill** —— 覆盖从需求澄清到发布监控的完整软件工程生命周期
- **八阶段工作流** —— 感知→规划→设计→执行→验证→审查→发布→反思
- **质量关卡**（Hooks）—— 自动化 Lint、测试、安全审计、代码审查

**核心目标：** 让 Claude Code 产出**逼近资深工程师水准**的代码，并通过结构化的质量关卡确保交付可靠性。

---

## 能力概览

### 1. 八阶段 AI Native 工作流

```
感知(Perceive) → 规划(Plan) → 设计(Design) → 执行(Execute)
                                                        ↓
反思(Reflect) ← 发布(Ship) ← 审查(Review) ← 验证(Verify)
```

每阶段有明确的**输入、动作、输出、退出标准**，AI 可自动识别当前阶段并调用对应 Skill。

| 阶段 | 核心能力 | 退出标准 |
|------|---------|---------|
| **感知** | 加载项目上下文、技术栈、历史记忆 | 能复述"项目为何存在" |
| **规划** | 拆 PR 级步骤、画依赖图、对抗性审查 | 每步骤可冷启动执行 |
| **设计** | 视觉方向、原型、动效、无障碍 | 设计评分 ≥ 7.5/10 |
| **执行** | TDD、最小 surgial edit、原子提交 | Smoke Test 全绿 |
| **验证** | 全量测试、浏览器 QA、Lint | 零错误 + 逐项确认 |
| **审查** | 代码审查、设计审计、安全审计 | 无阻塞问题 |
| **发布** | 干净 PR、CI、部署、监控 | 5 分钟无异常 |
| **反思** | 差异分析、经验提取、记忆固化 | 持续改进 |

### 2. 量化质量标准（AI 可直接识别）

**代码质量：**
- `tsc --noEmit` 零错误
- ESLint + Prettier 零错误
- Smoke Test ≥ 3 断言/模块
- 单函数复杂度 ≤ 15
- 单文件 ≤ 400 行

**设计质量（6 维度评分卡）：**
- 视觉独特性（20%）—— 非默认字体、无 AI slop
- 可用性（25%）—— Krug 定律、Nielsen 启发式
- 无障碍（20%）—— WCAG 2.2 AA、语义 HTML
- 技术质量（15%）—— Lighthouse、性能面板
- 动效（10%）—— 60fps、`prefers-reduced-motion`
- 文案（10%）—— 主动语态、具体标签
- **通过线：≥ 7.5/10**

**安全标准：**
- 无敏感信息硬编码
- 用户输入验证 + 转义
- 参数化 SQL
- 无 `eval()` 处理用户输入
- OWASP Top 10 无高危

### 3. 设计工作流（UI/UX 专项）

- **设计策略** —— 1-2 分钟定基调、用户、差异化
- **视觉基础** —— 字体、色彩、空间构图、暗模式
- **动效体系** —— `transform`/`opacity` 优先、可中断、尊重减弱动效
- **无障碍基础** —— 语义 HTML 优先于 ARIA、键盘可访问、对比度 4.5:1
- **设计审查** —— 视觉/可用性/无障碍/技术 四维审计

### 4. 167 个 Skill 覆盖全生命周期

| 类别 | 数量 | 代表 Skill |
|------|------|-----------|
| Vibe Coding 核心 | 10+ | `vibe-coding`, `vibe-design-workflow`, `brainstorming`, `blueprint` |
| 设计 | 8 | `frontend-design-3-0.1.0`, `motion-patterns`, `design-system`, `prototype` |
| 编码质量 | 5 | `coding-standards`, `tdd-workflow`, `error-handling` |
| 测试 | 4 | `e2e-testing`, `browser-qa`, `ai-regression-testing` |
| 调试 | 3 | `debug-pro-1.0.0`, `diagnose`, `systematic-debugging` |
| 审查 | 5 | `caveman-review`, `plankton-code-quality`, `ui-design-review` |
| 发布 | 3 | `deployment-patterns`, `canary-watch`, `production-audit` |
| 安全 | 3 | `security-auditor-1.0.0`, `security-scan`, `security-review` |
| AI/Agent | 5 | `ai-first-engineering`, `continuous-agent-loop`, `agentic-engineering` |
| GSD 工作流 | 83 | `gsd-new-project` ~ `gsd-workstreams` |
| 飞书 Lark | 25 | `lark-doc`, `lark-im`, `lark-calendar` 等 |

---

## 适用场景

- **B 端全栈应用** —— 前端 + 后端 + 数据库，需稳定交付
- **AI Agent 开发** —— 需要结构化规划与评估
- **CLI 工具** —— 快速构建、测试、发布
- **设计系统** —— 统一视觉规范与组件库

---

## 使用示例

### 示例 1：快速原型（≤ 15 分钟）

```
用户：做一个待办列表页面
AI：调用 vibe-coding → Phase 0 判断为 trivial → gsd-fast → 编码 → 验证 → Done
```

### 示例 2：全栈功能（完整八阶段）

```
用户：做一个用户管理后台，含列表、搜索、分页、导出
AI：
  P1 感知 → 加载项目上下文
  P2 规划 → blueprint 生成 8 步骤计划
  P3 设计 → vibe-design-workflow → 设计评分 8.2/10
  P4 执行 → tdd-workflow → 每模块 Smoke Test → 原子提交
  P5 验证 → browser-qa + e2e-testing → 全绿
  P6 审查 → requesting-code-review + security-review → 无阻塞
  P7 发布 → gsd-ship → CI 通过 → 部署
  P8 反思 → continuous-agent-loop → 经验写入 claude-mem
```

### 示例 3：UI 设计专项

```
用户：让这个仪表盘好看点
AI：
  调用 vibe-design-workflow
  Phase 1 策略 → 定基调（brutalist / professional / playful）
  Phase 2 实现 → frontend-design-3-0.1.0 + motion-patterns
  Phase 3 审查 → ui-design-review → 6 维度评分
  Phase 4 优化 → 打磨至 ≥ 7.5
```

---

## 工作流原理

### 为什么需要结构化工作流？

Claude Code 极易**过度工程化**。无蓝图时，首试成功率低，返工率高。八阶段工作流通过以下机制解决：

1. **蓝图先于代码** —— 任何实现前有 PLAN.md，明确"做什么"与"不做什么"
2. **思考者与构建者分离** —— 规划阶段用最强模型，执行阶段遵循最小 surgial edit
3. **Smoke Test 先行** —— 每模块编码前先写测试，失败即重构信号
4. **质量关卡不可跳过** —— 设计评分、代码审查、安全审计为硬性门槛

### AI Native  vs  传统 AI 辅助

| | 传统 AI 辅助 | AI Native |
|---|---|---|
| 交互模式 | 人发起 → AI 响应 → 人判断 | 模型自主推进，人于关键决策点介入 |
| 计划性 | 即兴提示，无全局蓝图 | 蓝图先于代码，通过规划门 |
| 验证 | 人眼检查 | Smoke Test + 自动化验证为必备 |
| 质量门 | 可有可无 | Lint → Smoke → Review → Security → QA |
| 反思 | 人发现 bug 后反馈 | 模型自主检测失败并修正 |

---

## 目录结构

```
.
├── CLAUDE.md                 # 灵魂文档（行为准则 + 工作流 + 技能路由）
├── hooks.json                # 质量关卡自动化配置
├── README.md                 # 本文件
├── scripts/
│   ├── install.sh            # macOS / Linux 安装脚本
│   └── install.ps1           # Windows 安装脚本
├── skills/                   # 167 个 Skill 完整源码
│   ├── vibe-coding/
│   ├── vibe-design-workflow/
│   ├── blueprint/
│   ├── frontend-design-3-0.1.0/
│   ├── ... (163 more)
│   └── SKILL_REGISTRY.md     # Skill 清单及说明
└── docs/
    └── WORKFLOW.md           # 八阶段工作流详细说明（可选）
```

---

## 核心设计哲学

基于 **Andrej Karpathy** 的 Vibe Coding 理念：

> "先思考，再编码。最少代码解决问题。不做猜测。"

并结合生产级实践：
- **Karpathy 谨慎原则** —— 暴露权衡，不隐藏困惑
- **4 黄金法则** —— 极简、精准、目标驱动、可验证
- **Claude Code 防过度工程** —— Surgical Coding Prompt：分析现有模式，最小编辑，不擅自重构

---

## 贡献

本配置为个人/团队工作流沉淀。欢迎：
- 提交 Issue 讨论工作流改进
- Fork 后定制适合自己团队的版本
- 补充新的 Skill 到注册表

---

## 许可证

灵魂文档（CLAUDE.md）及本仓库配置采用 [MIT License](./LICENSE)。

第三方 Skill 遵循其原始许可证。详见 [skills/SKILL_REGISTRY.md](./skills/SKILL_REGISTRY.md)。

---

## 致谢

- [Andrej Karpathy](https://karpathy.ai/) —— Vibe Coding 哲学
- [Claude Code](https://claude.ai/code) —— Anthropic 官方 CLI
- [Everything Claude Code (ECC)](https://github.com/affaan-m/everything-claude-code) —— Skill 生态
- [Awesome Claude Code Toolkit](https://github.com/rohitg00/awesome-claude-code-toolkit) —— Plugin 生态
- [GSD (Get Shit Done)](https://github.com/jasonjmcghee/GSD) —— 项目管理工作流

---

> **记住：** 设计是解决问题，不是装饰。代码是沟通，不是炫技。如果不会自豪地展示给同行，就没做完。
