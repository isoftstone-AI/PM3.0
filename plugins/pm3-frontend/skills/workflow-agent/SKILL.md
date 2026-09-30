---
name: workflow-agent
description: |
  工作流代理 — 蒸馏工作方式，智能路由到设计方案/开发方案/API 生成场景。
  自动检测 skill 是否存在，不存在时引导创建，创建后引导用户提供参数并执行。
  触发词：设计方案、开发方案、生成API、接口代码、/design-plan、/dev-plan、/api-gen
arguments: scene, params
argument-hint: "[design-plan|dev-plan|api-gen] [参数...]"
---

# Workflow Agent — 工作流代理

智能路由到设计方案、开发方案、API 生成三大场景。自动检测 skill 存在性，按需创建后引导执行。

---

## 触发方式

| 方式 | 示例 |
|------|------|
| 命令 | `/design-plan`、`/dev-plan`、`/api-gen` |
| 自然语言 | "帮我创建设计方案"、"生成开发方案"、"生成API代码" |

---

## 执行流程

```
用户输入
  ↓
Step 1: 触发词检测 + 关键词匹配路由
  ↓
Step 2: 扫描目录检测 skill 是否存在
  ├─ 存在 → Step 4
  └─ 不存在 → Step 3
  ↓
Step 3: 确认后创建 skill（调用 meta-skill）
  ↓
Step 4: 引导用户提供必要参数
  ↓
Step 5: 调用目标 skill 执行
  ↓
Step 6: 记录结构化日志
```

---

## Step 1: 触发词检测 + 关键词匹配路由

### 命令触发

| 命令 | 路由场景 |
|------|---------|
| `/design-plan` | 设计方案 |
| `/dev-plan` | 开发方案 |
| `/api-gen` | API 生成 |

### 关键词匹配

**设计方案场景** — 用户输入包含以下任一关键词即匹配：
- 设计方案、设计文档、设计指南、PRD生成、生成设计

**开发方案场景** — 用户输入包含以下任一关键词即匹配：
- 开发方案、开发文档、开发指南、字段级开发、生成开发方案

**API 场景** — 用户输入包含以下任一关键词即匹配：
- 生成API、生成接口、接口代码、API文档、接口文档

**匹配优先级**：命令触发 > 关键词匹配 > 无法匹配时询问用户意图

**无法匹配处理**：当用户输入不包含任何已定义关键词时，回复：
> 我可以帮你执行以下操作：
> 1. **设计方案** — 生成 PRD 设计文档（/design-plan）
> 2. **开发方案** — 生成字段级开发方案（/dev-plan）
> 3. **API 生成** — 根据接口文档生成代码（/api-gen）
>
> 请告诉我你需要哪个？

---

## Step 2: 扫描目录检测 skill 是否存在

使用 Glob 工具扫描以下目录的 `skills/*/SKILL.md` 文件：

| 目录 | 说明 |
|------|------|
| `.claude` | Claude Code 项目配置 |
| `.opencode` | OpenCode 项目配置 |
| `.agent` | Agent 项目配置 |
| `.qoder` | Qoder 项目配置 |

**扫描命令**：
```
Glob: {目录}/skills/*/SKILL.md
```

**扫描顺序**：按上表从上到下扫描，找到第一个匹配即停止。

### 检测规则

| 场景 | 检测的 skill 名称模式 | 匹配方式 |
|------|---------------------|---------|
| 设计方案 | `generate-*guide` | glob 模式匹配 `skills/generate-*/SKILL.md` |
| 开发方案 | `generator-dev-plan` | 精确匹配 `skills/generator-dev-plan/SKILL.md` |
| API 生成 | `generate-api` | 精确匹配 `skills/generate-api/SKILL.md` |

**检测结果**：
- 找到匹配文件 → 记录 skill 完整路径，进入 Step 4
- 未找到 → 进入 Step 3
- **找到多个匹配** → 列出所有匹配项，让用户选择使用哪一个

---

## Step 3: 确认后创建 skill

当检测到 skill 不存在时：

1. 向用户确认："检测到 {skillName} skill 不存在，是否创建？"
2. 用户确认后，调用对应的 meta-skill 创建

### 场景 → meta-skill 映射

| 场景 | meta-skill | 创建产物 | 创建后执行 |
|------|-----------|---------|-----------|
| 设计方案 | `skill-generator` | `generate-{project}-guide` | `/generate-{project}-guide` |
| 开发方案 | `create-develop-plan-skill` | `generator-dev-plan` | `/generator-dev-plan` |
| API 生成 | 无需创建（直接使用） | — | `/generate-api` |

### 创建失败处理

- 重试最多 2 次
- 重试失败后向用户报告错误，询问是否继续

---

## Step 4: 引导用户提供必要参数

创建完成后（或 skill 已存在），引导用户提供目标 skill 所需的参数。

### 设计方案参数

| 参数 | 必填 | 说明 |
|------|------|------|
| prdPath | 是 | PRD 文档路径，如 `@prd.md` |
| designPath | 是 | 设计图文档路径（yaml/markdown/html） |
| moduleName | 是 | 模块名称，如"开工管理" |
| version | 否 | 版本号，默认 `v1.0` |
| outputDir | 是 | 输出目录路径 |
| apiDocPath | 否 | API 文档路径 |

### 开发方案参数

| 参数 | 必填 | 说明 |
|------|------|------|
| designDocPath | 是 | 设计方案文档路径 |
| outputPath | 是 | 输出路径 |
| pageType | 否 | 页面类型（list/form/detail/approval/modal），默认 list |
| pageName | 否 | 页面名称 |
| pagePath | 否 | 页面路径 |
| moduleCode | 否 | 模块编码 |
| moduleName | 否 | 模块名称 |
| fieldData | 否 | JSON 格式字段数据 |
| refModule | 否 | 参考模块 |

### API 生成参数

| 参数 | 必填 | 说明 |
|------|------|------|
| source | 是 | 接口文档来源（apifox 或 md:文件路径） |
| scope | 否 | 生成范围，默认 all |
| target | 是 | 输出目录 |

### 引导方式

逐个检查必填参数：
- 用户已提供 → 跳过
- 用户未提供 → 询问用户

全部必填参数收集完成后，进入 Step 5。

---

## Step 5: 调用目标 skill 执行

使用收集到的参数，通过 `skill` 工具调用目标 skill：

### 调用格式

```typescript
skill(
  name: "{targetSkill}",
  user_message: "{收集到的参数，格式化为 key=value 空格分隔}"
)
```

### 各场景调用示例

**设计方案**：
```typescript
skill(
  name: "generate-prd-guide",
  user_message: "prdPath=@prd.md designPath=@design.yaml moduleName=开工管理 version=v1.0 outputDir=output"
)
```

**开发方案**：
```typescript
skill(
  name: "generator-dev-plan",
  user_message: "designDocPath=\"设计方案.md\" outputPath=\"输出.md\" pageType=list"
)
```

**API 生成**：
```typescript
skill(
  name: "generate-api",
  user_message: "source=apifox scope=all target=api-output"
)
```

### 调用说明

- **设计方案**：如果 skill-generator 创建了项目专属的 `generate-{project}-guide`，使用该名称调用；否则使用 `generate-prd-guide`
- **开发方案**：固定调用 `generator-dev-plan`
- **API 生成**：固定调用 `generate-api`

### 执行失败处理

- 记录错误日志（level: error）
- 向用户报告错误信息
- 询问用户是否重试

### 执行后确认

执行完成后，向用户确认结果：

> ✅ {场景}执行完成
> - 使用的 skill：{skillName}
> - 输出位置：{outputDir/target}
> - 日志已记录到 logs/ 目录
>
> 是否需要进一步操作？

---

## Step 6: 记录结构化日志

每次执行完成后，记录结构化日志到 `logs/` 目录。

### 日志格式（JSON）

```json
{
  "timestamp": "2024-01-15T10:00:00Z",
  "level": "info",
  "scene": "design",
  "action": "execute",
  "skill": "generate-pm3-guide",
  "params": {
    "prdPath": "@prd.md",
    "designPath": "@design.yaml",
    "moduleName": "开工管理"
  },
  "result": "success",
  "duration": 45000,
  "message": "设计方案生成完成"
}
```

### 日志级别

| 级别 | 用途 |
|------|------|
| debug | 详细调试信息 |
| info | 正常操作记录 |
| warn | 可恢复的异常 |
| error | 执行失败 |

---

## 异常与边界条件

| 场景 | 触发条件 | 处理方式 |
|------|---------|---------|
| 用户中途取消 | 用户在任意步骤输入"取消"、"cancel"、"停止" | 立即停止流程，记录日志（level: info, action: cancel） |
| 用户未确认创建 | Step 3 用户回复"否"或"不需要" | 记录日志，流程结束 |
| Skill 文件损坏 | 检测到 SKILL.md 但内容为空或格式错误 | 提示用户 skill 文件可能损坏，询问是否重新创建 |
| 参数验证失败 | 用户提供的参数格式不正确 | 提示具体错误，要求重新提供 |
| 目录权限不足 | 无法读取 skills/ 目录 | 提示用户检查目录权限 |
| 配置文件缺失 | config/workflow.yaml 不存在 | 使用内置默认配置继续执行 |

---

## 私有 Skills

Agent 自带以下 skills（从项目 `.claude/skills/` 复制）：

| Skill | 用途 |
|-------|------|
| `skill-generator` | 创建设计方案生成器 skill |
| `create-develop-plan-skill` | 创建开发方案生成器 skill |
| `generate-api` | 前端 API 代码生成器 |

---

## 配置文件

所有配置存储在 `config/workflow.yaml`，包括：
- 扫描目录
- 触发词
- 场景路由
- 参数定义
- 日志配置
- 错误处理策略
