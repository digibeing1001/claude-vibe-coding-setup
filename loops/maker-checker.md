# Maker/Checker 物理分离

Maker/Checker 分离是"可靠 loop 最重要的结构模式"。执行者（Maker）不能标记自己工作完成，验证者（Checker）必须是独立的 agent 或脚本——用不同的指令、不同的模型、在隔离的环境里跑验证。

## 为什么需要物理分离

同一个 agent 写代码又验证代码，有三类致命失败：

1. **自我确认偏差**——agent 倾向于相信自己刚写的代码是对的，验证时找"通过理由"而非"拒绝理由"
2. **上下文污染**——写代码时的思考框架会延续到验证，看不到自己的盲点
3. **Verifier Theater**——名义上有验证，实际是橡皮图章，不提供真实信号

物理分离把"写"和"验证"拆成两个独立实体，各自带不同的指令和上下文。

## Maker 职责

Maker 是执行者，负责产出代码/文档/变更。

### Maker 的硬约束

- **不能标记自己工作完成**——产出后必须交给 Checker
- **不能跑最终验证**——可以跑本地测试调试，但不能用通过本地测试当作"完成证据"
- **必须产出可被 Checker 读取的产物**——代码 + diff + 测试命令 + 预期行为
- **必须声明假设**——我假设了什么、哪些是不确定的、哪些是已知风险

### Maker 输出格式

```markdown
## Maker Report
Goal: <目标>
Changed: <文件列表 + 行数变化>
Tests added: <测试列表>
Assumptions: <假设列表>
Known risks: <已知风险>
Commands to verify: <Checker 应跑的命令>
Expected behavior: <预期结果>
```

## Checker 职责

Checker 是验证者，负责判断 Maker 的产出是否满足验收标准。

### Checker 的硬约束

- **必须是独立实体**——不同 agent、不同 session、或不同脚本
- **用"找拒绝理由"指令**——不是"验证这是否正确"，而是"找出拒绝合并的理由"
- **用更强或对等的模型**——Checker 不能比 Maker 弱
- **在隔离 worktree 跑验证**——不污染 Maker 的工作目录
- **必须报告原始输出**——不是"测试通过了"，而是测试的原始 stdout/stderr

### Checker 指令模板

```markdown
你是独立的 Verifier。你的任务是找出拒绝这次变更的理由，不是确认它正确。

变更内容：
<Maker 的 diff>

验收标准：
<acceptance criteria>

请执行：
1. 跑测试命令：<commands>
2. 跑类型检查：<type check>
3. 跑 lint：<lint>
4. 跑安全扫描：<security scan>
5. 审查 diff：找无关变更、dead code、过度抽象、缺失测试
6. 跑端到端验证（如适用）：<e2e>

输出格式：
## Verifier Verdict
- Verdict: APPROVE | REJECT | REQUEST_CHANGES
- Blockers: <必须修复才能合并的问题>
- Concerns: <非阻塞但应关注的问题>
- Evidence: <命令原始输出>
- Missing: <未验证的部分及原因>
```

## 6 阶段验证流程

Checker 默认跑 6 阶段验证，确定性检查为主、AI 审查为辅：

```
Build → TypeCheck → Lint → Test → Security → Diff Review
```

### 1. Build

```bash
npm run build  # 或对应语言的构建命令
```

构建必须通过。失败即 REJECT。

### 2. TypeCheck

```bash
npx tsc --noEmit  # 或对应语言的类型检查
```

类型检查必须通过。失败即 REJECT。

### 3. Lint

```bash
npx eslint .  # 或对应语言的 lint
```

Lint 必须通过。失败即 REJECT。

### 4. Test

```bash
npm test  # 单元测试
npx playwright test  # E2E（如适用）
```

测试必须全绿。失败即 REJECT。

### 5. Security

```bash
npm audit --audit-level=moderate
# 密钥扫描
git diff --cached | grep -iE "(api_key|secret|password|token).*=.*['\"]"
```

安全扫描必须通过。失败即 REJECT。

### 6. Diff Review

AI 审查 diff，找：
- 无关变更（不在任务范围内的改动）
- dead code（删除了但没清理的引用）
- 过度抽象（不必要的接口/层级）
- 缺失测试（改了行为但没加测试）
- 不一致（与项目现有模式不符）

Diff Review 输出 REQUEST_CHANGES 而非 REJECT——是建议而非阻塞。

## Verifier Theater 反模式

以下都是 Verifier Theater（名义上有验证，实际无信号），必须避免：

| 反模式 | 表现 | 修复 |
| --- | --- | --- |
| 同 session 验证 | Maker 和 Checker 在同一对话里 | 强制不同 session/agent |
| 同模型验证 | Maker 和 Checker 用同一模型 | Checker 用更强或对等模型 |
| 找通过理由 | Checker 指令是"验证这是否正确" | 改为"找拒绝理由" |
| 只跑 Maker 跑过的测试 | Checker 复跑 Maker 的测试 | Checker 跑独立测试集 |
| 无原始输出 | Checker 报告"测试通过" | 必须附原始 stdout/stderr |
| 验证部分遗漏 | 只跑 build 不跑 test | 6 阶段全跑（或显式声明跳过原因） |

## 隔离 Worktree

Checker 必须在隔离 worktree 跑验证：

```bash
# 创建隔离 worktree
git worktree add ../verify-<run_id> <branch>

# Checker 在隔离 worktree 跑
cd ../verify-<run_id>
npm ci
npm test
npm run build

# 验证完清理
cd ..
git worktree remove ../verify-<run_id>
```

隔离的目的：
- 不污染 Maker 的工作目录
- 避免 Maker 的本地修改影响验证
- 可重复验证（同一 diff 在干净环境跑）

## 重试上限

同一 PR/变更的自动修复有硬上限：**3 次 → 升级人工**。

```text
Attempt 1: Maker 写 → Checker 拒绝 → 反馈给 Maker
Attempt 2: Maker 修 → Checker 拒绝 → 反馈给 Maker
Attempt 3: Maker 修 → Checker 拒绝 → 升级人工
```

记录 attempt count 在 STATE.md。同 PR >3 次自动修复无进展即停，转 `wait_human`。

## 与控制器的契约

Checker 的 verdict 是控制器状态转移的输入：

| Verdict | 控制器动作 |
| --- | --- |
| APPROVE | 转 `complete`（如预算够且验收全通过） |
| REJECT | 转 `retry`（attempts < 3）或 `wait_human`（attempts >= 3） |
| REQUEST_CHANGES | 转 `retry`，带 Checker 的 concerns |

AI 不能覆盖 Checker 的 verdict。Maker 不能直接转 `complete`，必须等 Checker 的 APPROVE。
