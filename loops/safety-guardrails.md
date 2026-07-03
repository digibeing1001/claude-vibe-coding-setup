# 安全护栏

安全护栏把"loop 不能碰什么"做成可执行清单，而不是 advisory 文字。loop 跑得越快，越需要硬约束防止 AI 误碰高敏感路径。

## 三道护栏

| 护栏 | 作用 | 强制级别 |
| --- | --- | --- |
| Path Denylist | 禁止 loop 读写特定路径 | 硬约束，违反即停 |
| Auto-merge 策略 | 限制自动合并的变更类型 | 默认关闭，开启需 allowlist |
| MCP 最小权限 | 限制 connector 权限 | 配置时强制 |

## Path Denylist

loop 在每轮 Context 节点必须加载并强制执行 denylist。命中即转 `wait_human`，不执行任何 Act。

### 默认 denylist

```yaml
# config/loop-denylist.yaml
denylist:
  read:
    - "**/.env"
    - "**/.env.*"
    - "**/secrets/**"
    - "**/credentials/**"
    - "**/*_key.*"
    - "**/*_secret.*"
    - "**/auth/**"
    - "**/.aws/credentials"
    - "**/.ssh/id_*"
  write:
    - "**/.env"
    - "**/.env.*"
    - "**/secrets/**"
    - "**/credentials/**"
    - "**/*_key.*"
    - "**/*_secret.*"
    - "**/auth/**"
    - "**/payments/**"
    - "**/billing/**"
    - "**/migrations/**"        # 数据库迁移需人工确认
    - "**/k8s/production/**"     # 生产 k8s 配置
    - "**/terraform/prod/**"     # 生产基础设施
    - "**/.github/workflows/**"  # CI 配置改动需人工确认
  execute:
    - "rm -rf /"
    - "git push --force"          # 强制推送需人工确认
    - "git push --force-with-lease" # 同上
    - "DROP TABLE"                # 数据库删除操作
    - "DROP DATABASE"
    - "kubectl delete"            # k8s 删除操作
    - "terraform destroy"
    - "npm publish"               # 发布需人工确认
    - "docker push"               # 镜像推送需人工确认
```

### 项目级扩展

项目可在 `.agent/loop-denylist.yaml` 追加项目特定路径：

```yaml
# 项目级扩展
denylist:
  write:
    - "src/core/payment/**"       # 支付核心逻辑
    - "config/production/**"      # 生产配置
```

### 加载规则

- 默认 denylist 从 `config/loop-denylist.yaml` 加载
- 项目级 denylist 从 `.agent/loop-denylist.yaml` 加载，与默认合并
- 项目级只能追加，不能削弱默认 denylist
- 合并后的 denylist 在每轮 Context 节点加载，哈希记录在 STATE.md

### 命中处理

```text
IF AI 请求的路径/命令命中 denylist:
    transition to wait_human
    do not execute
    log: which rule, which path, which run
    notify human
```

## Auto-merge 策略

Auto-merge 默认**关闭**。开启需要显式 allowlist，且仅限低风险变更类型。

### 默认：关闭

```yaml
# config/loop-auto-merge.yaml
auto_merge:
  enabled: false  # 默认关闭
```

### 开启需 allowlist

开启时必须声明 allowlist，不在 allowlist 内的变更不能 auto-merge：

```yaml
auto_merge:
  enabled: true
  allowlist:
    - "**/*.md"                          # 文档
    - "**/comments/**"                   # 注释
    - "**/lint/**"                       # lint 修复
    - "**/test/**"                       # 测试文件
    - "**/*.test.*"                      # 测试文件
    - "**/*.spec.*"                      # 测试文件
    - "**/import-order/**"               # import 排序
  denylist:
    - "**/package.json"                  # 依赖变更
    - "**/package-lock.json"             # lockfile
    - "**/yarn.lock"
    - "**/Cargo.lock"
    - "**/go.mod"
    - "**/go.sum"
    - "**/.github/workflows/**"          # CI 配置
    - "**/migrations/**"                 # 数据库迁移
    - "config/loop-denylist.yaml"        # denylist 自身
    - "config/loop-auto-merge.yaml"      # auto-merge 自身
```

### 行为变更禁止 auto-merge

allowlist 只覆盖**非行为变更**。任何改变了运行时行为的变更（即使路径在 allowlist 内）也禁止 auto-merge，必须人工 review。

判断规则：
- 改了 `.test.ts` 但只是格式化 → 可 auto-merge
- 改了 `.test.ts` 但改了断言逻辑 → 禁止 auto-merge（行为变更）
- 改了 `.md` 但只是 typo → 可 auto-merge
- 改了 `.md` 但改了 API 文档描述的参数 → 禁止 auto-merge（可能误导调用方）

## MCP 最小权限

MCP connector 必须按最小权限配置，loop 不能拿到超出需要的权限。

### GitHub connector

```yaml
github:
  permissions:
    contents: read           # 读代码
    pull_requests: write     # 创建 PR、评论
    issues: write            # 创建 issue、评论
    actions: read            # 读 CI 状态
    # 禁止：administration, delete_repo, security_events
  auto_merge: false          # 不允许 connector 自己 merge PR
  allowed_repos:
    - "org/repo-1"
    - "org/repo-2"           # 限制可访问的 repo
```

### Slack connector

```yaml
slack:
  permissions:
    post_messages: true
  allowed_channels:
    - "#loop-escalations"    # 只能发到这个频道
  # 禁止：read_messages, delete_messages, invite_users
```

### Database connector

```yaml
database:
  production:
    enabled: false            # 生产数据库默认禁止
  staging:
    permissions:
      read: true              # 只读
      write: false
      ddl: false              # 禁止 DDL
```

### Linear/Jira connector

```yaml
linear:
  permissions:
    issues: write             # 创建/更新 issue
    comments: write
    # 禁止：delete_issues, manage_teams
```

## 风险评分

高风险动作必须人工确认。风险评分按以下维度：

| 风险类 | 阈值 | 示例 |
| --- | --- | --- |
| 不可逆 | 0.8+ | 删除操作、生产部署、数据库迁移 |
| 高影响 | 0.65+ | 改核心交易逻辑、改认证流程、改支付流程 |
| 跨服务 | 0.6+ | 改 API 契约、改共享库、改数据库 schema |
| 可逆但广泛 | 0.5+ | 改 CI 配置、改依赖版本、改构建配置 |
| 可逆且局部 | <0.5 | 改业务代码、加测试、改文档 |

风险评分 >= 0.65 的动作必须转 `wait_human`。

### 计算规则

```text
risk_score = max(
  irreversibility,        # 不可逆性
  blast_radius,           # 影响范围
  cross_service ? 0.6 : 0 # 是否跨服务
)
```

## loop-constraints skill

`loop-constraints` skill 在每轮 Context 节点强制执行：

1. 加载合并后的 denylist
2. 校验 denylist 哈希未变
3. 加载 auto-merge 配置
4. 加载 MCP 权限配置
5. 对本轮计划的所有路径/命令做 denylist 检查
6. 对本轮计划的所有动作做风险评分
7. 命中 denylist 或 risk >= 0.65 → 转 `wait_human`

AI 不能跳过 loop-constraints skill 的检查。
