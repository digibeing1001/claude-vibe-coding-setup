# Sequential Quality Loop

用于单一聚焦的功能或重构。比 localize-repair-validate 长一点，但仍属分钟-小时级。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 分钟-小时 |
| 风险 | Low |
| 默认就绪度 | L1 |
| 时间尺度 | 分钟-小时 |
| 触发 | 用户请求功能 / 重构 / spec 单元 |

## 循环

```
Context: 加载相关计划 + 文件 + 现有模式
Decide:  形成实现切片计划
Act:     实现一个连贯切片
Evaluate: 跑 scoped 测试 + lint/type + de-sloppify + 再验证
```

## 步骤

1. **Read**——只读相关计划和文件
2. **Implement**——实现一个连贯切片
3. **Scoped verify**——跑 scoped 测试、lint/type 检查
4. **De-sloppify**——移除冗余检查、dead code、过度抽象、框架行为测试
5. **Re-verify**——再跑一次验证
6. **Checkpoint**——证据 fresh 后才 commit/checkpoint

## De-sloppify 检查项

- 冗余的 null 检查
- dead code（删除了但没清理的引用）
- 过度抽象（不必要的接口/层级）
- 框架行为测试（测试框架本身而非业务逻辑）
- 重复逻辑
- 过时注释

## 预算

| 维度 | 默认 |
| --- | --- |
| Max iterations | 3 |
| Max retries/cause | 2 |
| Max tokens | 300,000 |
| Max stagnant cycles | 3 |

## 停止条件

- scoped 测试通过 + lint/type 通过 + de-sloppify 通过 → `complete`
- 同根因重试 2 次仍失败 → `wait_human`
- 切片触及 spec 外范围 → `wait_human`（spec drift）

## Maker/Checker

- Maker：实现切片
- Checker：6 阶段验证 + de-sloppify review
- 测试文件 hash 必须未变

## 升级条件

- 切片间有真实依赖 → 升级 rfc-dag-loop
- 需要多个创意方向 → 升级 parallel-generation-loop
- 需要 PR/CI 自动化 → 升级 continuous-pr-loop

## STATE.md

```markdown
## Goal
实现 <切片描述>

## Acceptance Criteria
- [ ] <scoped 测试> 通过
- [ ] lint/type 通过
- [ ] de-sloppify 通过

## Decisions
- <决策> — <理由>

## Current Evidence
<测试原始输出>

## Next Smallest Step
<实现 / 验证 / de-sloppify>
```
