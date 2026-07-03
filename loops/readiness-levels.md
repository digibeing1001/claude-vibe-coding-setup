# 就绪度分层与渐进上线

新 loop 永远先 L1 report-only 跑 1-2 周，再 L2 assisted，再 L3 unattended。跳过 L1 直接上 L3 是最常见的翻车原因——loop 还没校准就让它自己跑生产。

## 四级就绪度

| 级别 | 名称 | 能做什么 | 不能做什么 |
| --- | --- | --- | --- |
| L0 | Draft | 文档化意图 | 任何自动动作 |
| L1 | Report | triage → state，生成报告 | 自动修复、自动合并、自动部署 |
| L2 | Assisted | 小修复 + verifier 验证 | 无人值守、auto-merge、生产部署 |
| L3 | Unattended | 无人值守运行 | 无（但需 denylist + budget + metrics + human gates 全具备） |

## L0 — Draft

仅有文档化的 loop 意图。**不能自动跑任何东西**。

- 写在 `loops/patterns/<pattern>.md` 里
- 描述目标、节奏、风险、就绪度目标
- 人类手动跑，不调度

## L1 — Report

triage → state，生成报告。**只看不动**。

### L1 能做

- 定期扫描 CI 失败、issue、提交、旧 state
- 把高优项写入 STATE.md
- 生成报告（哪些项需要处理、建议的处理方式）
- 估算成本

### L1 不能做

- 自动修复代码
- 自动创建 PR
- 自动合并
- 自动部署
- 任何对代码库的写操作

### L1 上线条件

- 跑通 `loop-audit` 评分 >= 38（满分 100）
- STATE.md 模板已就位
- 预算表已声明
- kill switch 已配置
- 人类 review 节奏已确定（至少每天看一次）

## L2 — Assisted

小修复 + verifier 验证。**能改代码，但必须人类 review 后才合并**。

### L2 能做

- L1 的一切
- spawn 子 agent 做小修复（typo、lint、import 排序、明显 bug）
- 跑 Maker/Checker 流程
- 创建 PR（但不 auto-merge）
- 跑测试和验证

### L2 不能做

- auto-merge
- 生产部署
- 改 denylist 路径
- 改 CI 配置
- 改依赖版本
- 跨服务变更

### L2 上线条件

- 跑通 `loop-audit` 评分 >= 58
- L1 已稳定跑 1-2 周
- Maker/Checker 物理分离已实现
- denylist 已配置
- 预算上限已验证（实际消耗 < 预算的 50%）
- 重试上限（3 次）已验证有效
- 人工 review 流程已就位

## L3 — Unattended

无人值守运行。**所有护栏必须就位**。

### L3 能做

- L2 的一切
- auto-merge（限 allowlist 内的非行为变更）
- 定期部署（限预发布环境）
- 跨 loop 协调

### L3 不能做

- 改 denylist 路径
- 改 auto-merge 配置
- 改预算配置
- 改 kill switch
- 生产环境破坏性操作
- 跨服务契约变更

### L3 上线条件

- 跑通 `loop-audit` 评分 >= 78
- L2 已稳定跑 2-4 周
- **denylist + budget + metrics + human gates 全具备**
- 失败模式目录已覆盖该 loop 的已知失败
- kill switch 已测试（能真的停下来）
- 监控和告警已就位
- 回滚流程已验证

## 上线前自检清单

每个新 loop 上线前必须跑 10 节自检：

### 1. 目标可机械验证

- [ ] loop 的成功条件能写成命令或断言
- [ ] 不是"提升代码质量"这类模糊目标
- [ ] 验收标准在 spec 里显式声明

### 2. 停止条件

- [ ] max iterations 已设
- [ ] max retries/cause 已设（默认 2）
- [ ] max stagnant cycles 已设（默认 3）
- [ ] 预算上限已设

### 3. 状态管理

- [ ] STATE.md 模板已就位
- [ ] loop-run-log.md 已初始化
- [ ] 检查点目录已创建
- [ ] 大文件引用传递规则已确认

### 4. 验证

- [ ] Maker/Checker 物理分离已实现
- [ ] 6 阶段验证流程已配置
- [ ] Verifier Theater 反模式已排除
- [ ] 重试上限 3 次已强制

### 5. 安全

- [ ] denylist 已加载
- [ ] auto-merge 配置已声明（默认关闭）
- [ ] MCP 权限已按最小权限配置
- [ ] 风险评分阈值已设（>= 0.65 转 wait_human）

### 6. 预算

- [ ] 预算表已声明
- [ ] watchlist 空→早退已实现
- [ ] kill switch 已配置并测试
- [ ] 超限流程已验证

### 7. 人类介入

- [ ] 执行前上下文门已配置
- [ ] 执行中精准中断条件已声明
- [ ] 升级路径已明确（什么情况通知谁）
- [ ] 通知渠道已就位

### 8. 多 loop 协调

- [ ] acting_on 字段已配置
- [ ] 优先级已声明
- [ ] 共享 inbox 已就位

### 9. 自我修正

- [ ] Post-Run Critique 模板已就位
- [ ] 失败模式目录已覆盖该 loop
- [ ] 任务循环 vs 系统迭代分离已确认

### 10. 监控

- [ ] 实际消耗 vs 预算可观测
- [ ] 失败率可观测
- [ ] 噪音率可观测
- [ ] 回滚流程已验证

## 红旗信号

出现以下任一信号，立即降级（L3→L2 或 L2→L1）：

| 信号 | 含义 | 动作 |
| --- | --- | --- |
| 同 PR >3 次自动修复无进展 | 重试上限失效 | 降级 + 修复 retry 逻辑 |
| Verifier 同 session | 物理分离失效 | 降级 + 修复 Checker 隔离 |
| 无 state 文件 | 状态脊柱缺失 | 降级 + 创建 STATE.md |
| 每次都通知人类 | 升级阈值过低 | 调整阈值或降级 |
| auto-merge 无 allowlist | 安全护栏缺失 | 立即降级 + 配置 allowlist |
| 实际消耗 > 预算 80% | 预算不准 | 重新校准预算或降级 |
| STATE.md 不 prune | 状态膨胀 | 修复 prune 逻辑 |
| 噪音率 > 30% | 误报过多 | 降级 + 调整 triage 规则 |

## loop-audit 评分

`scripts/loop_audit.py` 评分维度（18 维，满分 100）：

| 维度 | 分值 | L1 阈值 | L2 阈值 | L3 阈值 |
| --- | --- | --- | --- | --- |
| 目标可机械验证 | 8 | 4 | 6 | 7 |
| 停止条件 | 8 | 4 | 6 | 7 |
| STATE.md | 6 | 3 | 4 | 5 |
| 检查点 | 4 | 0 | 2 | 3 |
| Maker/Checker 分离 | 8 | 0 | 6 | 7 |
| 6 阶段验证 | 6 | 0 | 4 | 5 |
| denylist | 6 | 3 | 5 | 5 |
| auto-merge 策略 | 4 | 0 | 2 | 4 |
| MCP 最小权限 | 4 | 2 | 3 | 4 |
| 预算表 | 6 | 3 | 5 | 5 |
| kill switch | 6 | 3 | 5 | 6 |
| watchlist 早退 | 4 | 2 | 3 | 4 |
| 人类介入点 | 6 | 3 | 5 | 6 |
| 多 loop 协调 | 4 | 0 | 2 | 4 |
| Post-Run Critique | 4 | 2 | 3 | 4 |
| 失败模式覆盖 | 6 | 3 | 4 | 6 |
| 监控可观测 | 6 | 2 | 4 | 6 |
| 回滚流程 | 4 | 1 | 3 | 4 |
| **总分** | **100** | **38** | **58** | **78** |

```bash
python scripts/loop_audit.py --pattern daily-triage --suggest --badge
```

输出示例：

```text
Loop: daily-triage
Score: 72/100
Level: L2 (Assisted) — meets L1 (38) and L2 (58), does not meet L3 (78)

Weak dimensions:
- Maker/Checker separation: 2/8 (need 6 for L3)
- 6-stage verification: 2/6 (need 5 for L3)
- Monitoring: 3/6 (need 6 for L3)

Suggested actions:
- Implement Maker/Checker physical separation
- Configure 6-stage verification flow
- Add monitoring dashboards
```
