# Localize-Repair-Validate

用于大多数 bug 和回归。最简单、最便宜的 loop，是默认的 bug 处理模式。

## 元数据

| 项 | 值 |
| --- | --- |
| 节奏 | 即时 |
| 风险 | Low |
| 默认就绪度 | L1 |
| 时间尺度 | 分钟级 |
| 触发 | 用户报告 bug / 测试失败 / CI 失败 |

## 循环

```
Context: 加载失败命令 + 相关文件 + 测试
Decide:  跳过（简单任务）
Act:     localize → patch → validate
Evaluate: 失败命令是否通过 + 邻近测试是否通过
```

## 步骤

1. **Reproduce**——用最小命令复现失败
2. **Localize**——定位到文件、符号、编辑位置
3. **Patch**——修复最小正确面
4. **Validate**——跑原失败命令
5. **Regression**——跑邻近回归或冒烟测试
6. **Record**——记录改了什么、为什么

## 升级条件

仅以下情况升级到更长 loop：

- 定位失败 2 次
- 补丁触及共享架构
- 失败根因跨多文件
- 需要重构才能修复

## 预算

| 维度 | 默认 |
| --- | --- |
| Max iterations | 3 |
| Max retries/cause | 2 |
| Max tokens | 100,000 |
| Max stagnant cycles | 3 |

## 停止条件

- 失败命令通过 + 邻近测试通过 → `complete`
- 同根因重试 2 次仍失败 → `wait_human`
- 定位失败 2 次 → 升级 sequential-quality-loop

## Maker/Checker

- Maker：定位 + 修复
- Checker：在独立 worktree 跑失败命令 + 邻近测试
- 测试文件 hash 必须未变（Maker 不能改测试）

## STATE.md

```markdown
## Goal
修复 <失败命令>

## Acceptance Criteria
- [ ] <失败命令> 通过
- [ ] <邻近测试> 通过

## Current Evidence
<失败命令的原始输出>

## Failed Attempts
- <尝试> — <根因假设>

## Next Smallest Step
<定位 / 修复 / 验证>
```
