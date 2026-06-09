# 灵魂准则

> 基于 Andrej Karpathy 哲学：谨慎 > 速度。简单任务自行判断。

## 1. 先思考，再编码

- 不确定 → 提问。不假设。
- 多理解 → 呈现选项，不默默选。
- 有简单方案 → 说出来。

## 2. 极简优先

- 不加需求外功能。不抽象一次性代码。不提供未要求的灵活性。
- 不处理不可能场景的错误。
- 200行能压到50行 → 重写。

## 3. 精准修改

- 不碰相邻代码、注释、格式。不重构没坏的东西。匹配现有风格。
- 只删**你的改动**导致的孤儿代码。
- 检验：每一行改动追溯到用户请求。

## 4. 目标驱动

- "添加验证" → "为无效输入写测试，让它们通过"
- "修复bug" → "写复现测试，让它通过"
- "重构X" → "重构前后测试都通过"

---

# 生产级标准定义（量化指标）

## 代码质量门

| 维度 | 通过标准 | 验证方式 |
|------|---------|---------|
| **类型安全** | `tsc --noEmit` 零错误 | 命令行 |
| **Lint** | ESLint + Prettier 零错误 | 命令行 |
| **测试覆盖** | 修改域有 Smoke Test（≥3 个断言） | 测试运行 |
| **死代码** | 无未使用导入/变量/函数（ESLint `no-unused`） | 静态分析 |
| **循环复杂度** | 单函数 ≤ 15 | 静态分析 |
| **文件行数** | 单文件 ≤ 400 行（超则拆分） | 人工 |

## 设计质量门（UI 项目）

| 维度 | 权重 | 通过标准 | 验证方式 |
|------|------|---------|---------|
| 视觉独特性 | 20% | 非默认字体、无紫色渐变白底、有明确调色板 | 肉眼 |
| 可用性 | 25% | Krug 定律：自明、点击无痛苦、文案可扫描 | 启发式评估 |
| 无障碍 | 20% | WCAG 2.2 AA：正文 4.5:1、UI 3:1、语义 HTML、键盘可访问 | axe-core / 手动 |
| 技术质量 | 15% | 图片有尺寸、首屏外 lazy、无 `transition: all`、动画 60fps | Lighthouse |
| 动效 | 10% | 仅 `transform`/`opacity`、尊重 `prefers-reduced-motion`、可中断 | 性能面板 |
| 文案 | 10% | 主动语态、具体按钮标签、错误信息含下一步 | 人工 |
| **总分** | 100% | **≥ 7.5/10** | 自评 |

## 测试标准

- Smoke Test：每模块 ≥ 3 个断言，verbose 说明"测什么、为何测"
- E2E：覆盖主链路（登录→核心操作→退出）
- 3+ 测试失败 → 模块需重构
- 优先 E2E，非 unit test

## 安全标准

- 无敏感信息硬编码（密钥、密码、token）
- 用户输入有验证 + 转义
- SQL 用参数化查询
- 无 `eval()` / `new Function()` 处理用户输入
- OWASP Top 10 自查无高危

---

# AI Native 八阶段工作流

## 决策树

```
用户说 "build X"
    │
    ▼
<= 15 min ? ──→ gsd-fast / caveman → 验证 → Done
    │
    └─→ > 15 min
            │
            UI ? ──→ 含 Phase 3 设计
            │
            新/现有项目 ? ──→ gsd-new-project / brainstorming
```

## 阶段定义（输入 → 动作 → 输出 → 退出标准）

### P1 感知（Perceive）
- **输入：** 用户请求、项目上下文
- **动作：**
  1. 加载 README + API 文档 + 设计稿 + claude-mem 历史
  2. **代码库索引** —— 如项目有 `.codegraph/` 目录，使用 CodeGraph 快速获取项目结构和模块关系；如无，提示初始化
- **输出：** Foundation Report（技术栈 + 模块划分 + 目标用户）
- **退出：** 能复述"项目为何存在、目标用户是谁"
- **Skill：** `everything-claude-code`, `codebase-onboarding`, `gsd-ingest-docs`, `search-first`
- **Tool：** `mcp__codegraph__codegraph_files`, `mcp__codegraph__codegraph_context`

### P2 规划（Plan）
- **输入：** Foundation Report
- **动作：**
  1. **深度对齐** —— `grill-me` 或 `grill-with-docs` 深度追问，确保理解无偏差
  2. **共享语言** —— 如用 `grill-with-docs`，同步建立/更新 `CONTEXT.md`；或用 `ubiquitous-language` 提取 DDD 术语表
  3. **接口设计** —— 调用 `design-an-interface` 生成多方案 API/模块接口设计（Design It Twice）
  4. **架构设计** —— 复杂系统调用 `code-architect` 生成架构图和接口设计
  5. **数据模型** —— 涉及数据库时调用 `schema-designer` 设计 schema 和 ERD
  6. **重构规划** —— 如涉及重构，调用 `request-refactor-plan` 生成增量提交计划
  7. **拆步骤** —— 拆 3-12 个 PR 级步骤 → 画依赖图 → 对抗性审查
- **输出：** PLAN.md + CONTEXT.md + 架构图（如适用）
- **退出：** 每步骤可独立冷启动执行；审查无 CRITICAL；用户确认理解无误
- **Skill：** `blueprint`, `writing-plans`, `to-prd`, `architecture-designer-0.1.0`, `plan-orchestrate`, `gsd-plan-phase`, `grill-me`, `grill-with-docs`, `ubiquitous-language`, `design-an-interface`, `request-refactor-plan`
- **Plugin：** `/plugin run code-architect`, `/plugin run schema-designer`, `/plugin run plan`

### P3 设计（Design）—— UI 项目必做
- **输入：** PLAN.md
- **动作：**
  1. 定基调 → ASCII Wireframe / 原型 → 设计评分卡
  2. **UI 草图** —— 调用 `ui-designer` 生成高保真设计稿或组件规范
  3. **响应式设计** —— 调用 `responsive-designer` 验证多端适配
  4. **视觉审计** —— 调用 `design-review` 检测 AI slop 和视觉不一致
- **输出：** DESIGN.md + 原型 + 设计稿 + 评分 ≥ 7.5
- **退出：** 评分 ≥ 7.5/10
- **Skill：** `vibe-design-workflow`, `frontend-design-3-0.1.0`, `prototype`, `motion-patterns`, `design-system`, `gsd-ui-phase`, `design-review`
- **Plugin：** `/plugin run ui-designer`, `/plugin run responsive-designer`

### P4 执行（Execute）
- **输入：** PLAN.md / DESIGN.md / CONTEXT.md
- **动作：**
  1. `using-git-worktrees` → Smoke Test 先行 → RED-GREEN-REFACTOR → 原子提交
  2. **代码影响分析** —— 修改前调用 CodeGraph 的 `codegraph_impact` 和 `codegraph_callers` 评估变更范围
  3. **前端实现** —— UI 组件开发时调用 `frontend-developer` 确保最佳实践
  4. **前端架构** —— 复杂页面调用 `frontend-excellence` 进行架构指导
- **输出：** 代码 + Smoke Test + 提交历史
- **退出：** Smoke Test 全绿；Lint 零错误
- **Skill：** `tdd-workflow`, `test-driven-development`, `coding-standards`, `error-handling`, `executing-plans`, `subagent-driven-development`, `dispatching-parallel-agents`, `gsd-execute-phase`
- **Plugin：** `/plugin run frontend-developer`, `/plugin run frontend-excellence`
- **Tool：** `mcp__codegraph__codegraph_impact`, `mcp__codegraph__codegraph_callers`, `mcp__codegraph__codegraph_trace`
- **规则：** "Analyze existing patterns. Minimal edits. Don't refactor unless asked."
- **检查点：** 每 3 模块 → Refactor Checkpoint（重复代码、接口一致性、命名）
- **紧急恢复：** 迷失/过度复杂时 → `zoom-out` 跳出细节看全局

### P5 验证（Verify）
- **输入：** 代码
- **动作：** 全量测试 → 浏览器验证（UI）→ Lint → 对照 PLAN.md 逐项确认 → 手动验证功能
- **输出：** 验证报告（全绿 / 失败清单）
- **退出：** 测试全绿；Lint 零错误；PLAN.md 项项确认
- **Skill：** `verification-loop`, `verification-before-completion`, `e2e-testing`, `browser-qa`, `test-runner-1.0.0`, `ai-regression-testing`, `verify`, `benchmark`, `qa-mattpocock`

### P6 审查（Review）
- **输入：** 验证通过的代码
- **动作：**
  1. **技术维度** —— 代码审查（bugs/simplify/reuse）
  2. **视觉维度** —— 设计审计（`design-review` 检测 AI slop + 视觉不一致）
  3. **风险维度** —— 安全审计 + 无障碍审计
  4. **双轴审查** —— `review` 并行运行 Standards + Spec 两个子审查
  5. **角色化审查：**
     - **CEO 视角** —— 符合商业目标？范围是否蔓延？（`product-lens`）
     - **Eng 视角** —— 架构合理？技术债可控？（`architecture-designer-0.1.0`）
     - **DevEx 视角** —— 开发者体验？onboarding 成本？（`codebase-onboarding`）
     - **QA 视角** —— 测试覆盖？边缘情况？（`browser-qa` / `e2e-testing` / `qa-mattpocock`）
     - **Security 视角** —— OWASP Top 10？STRIDE 威胁？（`cso` / `security-auditor-1.0.0`）
     - **Design 视角** —— 视觉一致性？AI slop？（`design-review` / `ui-design-review`）
  6. **增强审查（Toolkit）：**
     - **代码审查增强** —— `code-review-assistant` 分级审查（致命/严重/警告/建议）
     - **质量守护** —— `code-guardian` 安全扫描 + 坏味道检测
     - **死代码清理** —— `dead-code-finder` 移除无用代码
     - **无障碍审计** —— `a11y-audit` WCAG 合规检查
     - **打包分析** —— `bundle-analyzer` 检测体积回归
- **输出：** 审查报告（问题清单 + 严重程度 + 角色化反馈 + Toolkit 扫描结果）
- **退出：** 无阻塞问题；安全无高危；设计 ≥ 7.5；所有角色视角通过；Toolkit 无致命/严重
- **Skill：** `requesting-code-review`, `receiving-code-review`, `review`, `caveman-review`, `plankton-code-quality`, `ui-design-review`, `design-review`, `security-review`, `security-auditor-1.0.0`, `security-scan`, `cso`, `gsd-code-review`, `gsd-review`, `gsd-ui-review`, `simplify`, `product-lens`, `architecture-designer-0.1.0`
- **Plugin：** `/plugin run code-review-assistant`, `/plugin run code-guardian`, `/plugin run dead-code-finder`, `/plugin run security-guidance`, `/plugin run a11y-audit`, `/plugin run bundle-analyzer`

### P7 发布（Ship）
- **输入：** 审查通过的代码
- **动作：**
  1. 干净 PR → CI 全绿
  2. **部署自动化** —— `deploy-pilot` 生成 Dockerfile、CI/CD 配置、基础设施代码
  3. **版本管理** —— `release-manager` 语义化版本管理和自动发布工作流
  4. 部署 → 5 分钟监控 → 文档更新
  5. **文档生成** —— `document-generate` 从代码生成 Diataxis 文档；`codebase-documenter` 生成 API 文档
- **输出：** 合并的 PR + 部署确认 + 更新文档 + 自动生成文档
- **退出：** CI 通过；核心指标 5 分钟无异常
- **Skill：** `gsd-ship`, `finishing-a-development-branch`, `deployment-patterns`, `canary-watch`, `production-audit`, `gsd-docs-update`, `gsd-complete-milestone`, `document-generate`
- **Plugin：** `/plugin run deploy-pilot`, `/plugin run release-manager`, `/plugin run codebase-documenter`, `/plugin run code-explainer`

### P8 反思（Reflect）
- **输入：** 发布结果
- **动作：** 计划 vs 实际差异 → 提取经验 → 写入 claude-mem
- **输出：** Learnings 记录
- **退出：** 无（持续改进）
- **Skill：** `continuous-agent-loop`, `handoff`, `gsd-extract-learnings`, `gsd-pause-work`, `improve-codebase-architecture`

---

# 技能路由表

**原则：** 不确定 → 调 skill。Process skill > Implementation skill。`vibe-coding` 为 PRIMARY 入口。

| 场景 | 主 Skill | 辅助 Skill |
|------|---------|-----------|
| **任何创建/构建/设计请求** | `vibe-coding` | — |
| **新项目** | `gsd-new-project` | `brainstorming` |
| **需求澄清** | `brainstorming` | `product-lens` |
| **深度对齐（追问）** | `grill-me` | — |
| **深度对齐（带文档）** | `grill-with-docs` | `ubiquitous-language` |
| **加载项目约定** | `everything-claude-code` | `codebase-onboarding` |
| **多步骤计划** | `blueprint` | `writing-plans`, `plan-orchestrate` |
| **PRD** | `to-prd` | — |
| **架构设计** | `architecture-designer-0.1.0` | `plan-orchestrate` |
| **接口设计** | `design-an-interface` | — |
| **重构规划** | `request-refactor-plan` | — |
| **UI 设计** | `vibe-design-workflow` | `frontend-design-3-0.1.0`, `prototype`, `motion-patterns` |
| **设计系统** | `design-system` | — |
| **TDD** | `tdd-workflow` | `test-driven-development` |
| **编码规范** | `coding-standards` | — |
| **计划执行** | `executing-plans` | `subagent-driven-development` |
| **并行任务** | `dispatching-parallel-agents` | — |
| **调试** | `systematic-debugging` | `debug-pro-1.0.0`, `diagnose`, `investigate`, `gsd-debug` |
| **浏览器 QA** | `browser-qa` | `gstack` |
| **E2E 测试** | `e2e-testing` | `test-runner-1.0.0` |
| **代码审查** | `review` | `requesting-code-review`, `caveman-review`, `plankton-code-quality` |
| **UI 审查** | `ui-design-review` | `design-review`, `vibe-design-workflow` |
| **安全审计** | `cso` | `security-review`, `security-auditor-1.0.0`, `security-scan` |
| **发布** | `gsd-ship` | `deployment-patterns`, `canary-watch` |
| **会话交接** | `handoff` | `gsd-pause-work` |
| **上下文压缩** | `caveman` | `compress` |
| **跳出细节看全局** | `zoom-out` | `blueprint` |
| **Git 安全护栏** | `git-guardrails-claude-code` | — |
| **预提交钩子设置** | `setup-pre-commit` | — |
| **代码库索引** | `mcp__codegraph__codegraph_init` | `mcp__codegraph__codegraph_files` |
| **代码影响分析** | `mcp__codegraph__codegraph_impact` | `mcp__codegraph__codegraph_callers` |
| **调用链路追踪** | `mcp__codegraph__codegraph_trace` | `mcp__codegraph__codegraph_explore` |
| **架构设计（Plugin）** | `/plugin run code-architect` | `/plugin run schema-designer` |
| **前端实现（Plugin）** | `/plugin run frontend-developer` | `/plugin run frontend-excellence` |
| **代码审查增强（Plugin）** | `/plugin run code-review-assistant` | `/plugin run code-guardian` |
| **死代码检测（Plugin）** | `/plugin run dead-code-finder` | — |
| **无障碍审计（Plugin）** | `/plugin run a11y-audit` | — |
| **打包分析（Plugin）** | `/plugin run bundle-analyzer` | — |
| **部署自动化（Plugin）** | `/plugin run deploy-pilot` | `/plugin run release-manager` |
| **文档生成（Plugin）** | `/plugin run codebase-documenter` | `/plugin run code-explainer` |
| **紧急：迷失** | `blueprint` / `zoom-out` | `gsd-explore` |
| **紧急：范围蔓延** | `product-lens` | `plan-orchestrate` |

---

# 质量关卡（Hooks）

`.claude/hooks.json`：

```json
{
  "pre-commit": {
    "commands": [
      "prettier --write .",
      "eslint --fix .",
      "tsc --noEmit"
    ]
  },
  "pre-test": {
    "commands": [
      "vitest run --coverage",
      "playwright test"
    ]
  },
  "pre-ship": {
    "skills": ["security-review", "browser-qa", "code-review"]
  },
  "pre-merge": {
    "skills": ["simplify", "caveman-review"]
  }
}
```

**关卡速查：**

| 关卡 | 触发 | 检查 | 通过 |
|------|------|------|------|
| Lint | 保存 | Prettier/ESLint/TS | 零错误 |
| Smoke Test | 每模块 | ≥3 断言 | 全绿 |
| Design Score | 设计完成 | 6 维度 | ≥ 7.5/10 |
| Code Review | 功能完成 | bugs/simplify/reuse | 无阻塞 |
| Security | 发布前 | OWASP/密钥/注入 | 无高危 |
| Browser QA | 发布前 | 截图/响应式/E2E | 无回归 |
| Production | 发布后 5min | 核心指标 | 无异常 |

---

# 附录：可用 Skill 总览（155 个）

**Vibe Coding 黄金路径 Skill：**
`vibe-coding` → `brainstorming`/`gsd-new-project` → `grill-me`/`grill-with-docs`/`ubiquitous-language` → `blueprint`/`writing-plans`/`design-an-interface` → `vibe-design-workflow`/`frontend-design-3-0.1.0`/`design-review` → `tdd-workflow`/`executing-plans` → `verification-loop`/`browser-qa`/`verify` → `review`/`cso`/`security-review` → `gsd-ship`/`deployment-patterns`/`canary-watch` → `document-generate`/`handoff`

**完整列表：** `agent-eval`, `agent-harness-construction`, `agentic-engineering`, `ai-first-engineering`, `ai-regression-testing`, `andrej-karpathy-skills`, `architecture-designer-0.1.0`, `autonomous-agent-harness`, `benchmark`, `blueprint`, `brainstorming`, `browser-qa`, `canary-watch`, `caveman`, `caveman-review`, `code-tour`, `codebase-onboarding`, `coding-standards`, `compress`, `continuous-agent-loop`, `cso`, `debug-pro-1.0.0`, `design-an-interface`, `design-review`, `design-system`, `diagnose`, `dispatching-parallel-agents`, `document-generate`, `e2e-testing`, `error-handling`, `everything-claude-code`, `everything-claude-code-conventions`, `executing-plans`, `finishing-a-development-branch`, `frontend-design-3-0.1.0`, `frontend-design-direction`, `grill-me`, `grill-with-docs`, `gsd-add-tests`–`gsd-workstreams` (67 个 gsd-*), `gstack`, `handoff`, `improve-codebase-architecture`, `investigate`, `make-interfaces-feel-better`, `motion-advanced`, `motion-foundations`, `motion-patterns`, `plan-orchestrate`, `plankton-code-quality`, `product-lens`, `production-audit`, `prototype`, `qa-mattpocock`, `receiving-code-review`, `request-refactor-plan`, `requesting-code-review`, `review`, `rules-distill`, `search-first`, `security-auditor-1.0.0`, `security-review`, `security-scan`, `setup-pre-commit`, `simplify`, `skill-creator-0.1.0`, `subagent-driven-development`, `systematic-debugging`, `tdd-workflow`, `tech-evaluator`, `test-driven-development`, `test-runner-1.0.0`, `to-issues`, `to-prd`, `triage`, `ubiquitous-language`, `ui-design-review`, `using-git-worktrees`, `using-superpowers`, `verification-before-completion`, `verification-loop`, `verify`, `vibe-coding`, `vibe-design-workflow`, `write-a-skill`, `writing-plans`, `writing-skills`, `zoom-out`

**整合 Toolkit Plugin：** `code-architect`, `schema-designer`, `ui-designer`, `responsive-designer`, `frontend-developer`, `frontend-excellence`, `code-review-assistant`, `code-guardian`, `code-explainer`, `dead-code-finder`, `security-guidance`, `codebase-documenter`, `onboarding-guide`, `a11y-audit`, `bundle-analyzer`, `regex-builder`, `rag-builder`, `web-dev`, `feature-dev`, `product-shipper`, `pr-reviewer`, `bug-detective`, `e2e-runner`, `test-writer`, `plan`, `discuss`, `deploy-pilot`, `release-manager`, `monitoring-setup`
