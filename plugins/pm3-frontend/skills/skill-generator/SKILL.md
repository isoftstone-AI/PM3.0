---
name: skill-generator
description: |
  创建"设计方案生成器" skill 的 meta-skill。
  通过配置生成针对新项目的 generate-{project}-guide skill。
  触发词：创建设计方案skill、生成设计文档生成器、创建generate-prd-guide、新项目设计方案、skill生成器
arguments: config
argument-hint: [config=<YAML配置文件路径>]
compatibility: 需要现有 generate-prd-guide skill 作为模板源。生成的 skill 写入 .claude/skills/generate-{project.name}-guide/
---

# Skill Generator

这是一个 meta-skill：它的输出不是文档，而是**另一个 skill**。

它读取现有 `generate-prd-guide` 的模板和 agent 定义，注入项目特定配置，生成一个完全可用的设计方案生成器 skill。

---

## 两种模式

| 模式 | 触发方式 | 适用场景 |
|------|---------|---------|
| **交互式问答** | 直接调用，无 config 参数 | 新项目，需要引导配置 |
| **配置文件导入** | `config=<path>` 指向 YAML 文件 | 已有配置，快速生成 |

---

## 交互式问答流程

共四轮 + 确认轮。核心问题必问，可选配置有默认值。

### 第一轮：核心信息（必问）

| 问题 | 作用 | 示例 |
|------|------|------|
| 项目名称是什么？ | 生成 skill 名和目录名 | `pm3.0` |
| 项目主要业务领域？ | 写入生成 skill 的描述 | `管理后台` |
| 输出文档保存在哪个目录？ | 配置默认输出路径 | `docs/design` |

### 第二轮：目录结构（必问）

| 问题 | 选项 | 默认 |
|------|------|------|
| 使用模板还是自定义目录？ | 见下方预设模板 | 模板 |
| 字段命名规范？ | camelCase / snake_case | camelCase |

#### 目录结构预设模板

| 模板名称 | 适用场景 | 目录结构 |
|---------|---------|---------|
| **通用管理后台** | CRUD 为主的后台系统 | `src/views/{模块}/`, `src/api/{模块}/`, `src/components/` |
| **单体应用 SPA** | 单页应用 | `src/pages/`, `src/api/`, `src/shared/` |
| **微前端子应用** | 微前端架构下的子模块 | `src/views/`, `src/services/`, `src/common/` |

用户选择模板后可微调个别路径。

### 第三轮：字典与公共字段（必问）

| 问题 | 选项 | 默认 |
|------|------|------|
| 字典数据来源？ | backend / frontend / config | backend |
| 是否有预定义的公共字段？ | 列出字段列表 | 创建人、创建时间、更新人、更新时间、删除标记 |

公共字段支持以下类型：`user`, `datetime`, `boolean`, `string`, `number`。

### 第四轮：可选配置（有默认值，可跳过）

| 配置项 | 默认值 |
|--------|--------|
| API 接口文档格式 | markdown |
| 日期字段格式 | YYYY-MM-DD |
| 数字精度 | 2 位小数 |
| 输出语言 | zh-CN |
| 设计图格式 | yaml（支持 yaml/markdown/ascii） |
| 字典速查表生成 | 启用 |
| 审批流专题生成 | 启用 |
| 弹窗详情生成 | 启用 |

### 确认轮

展示完整配置表，等待用户确认。确认后进入模板渲染。

---

## 配置文件格式

配置文件为标准 YAML，支持导出/导入以复用。

```yaml
version: "1.0"

# 项目基本信息（必填）
project:
  name: "my-project"              # 字母数字+连字符，3-50 字符
  domain: "管理后台"
  description: "企业内部管理系统"

# 目录结构
directory:
  output: "docs/design"           # 设计方案输出目录
  pages: "src/views"
  components: "src/components"
  api: "src/api"

# 命名规范
naming:
  fieldCase: "camelCase"          # camelCase / snake_case
  fileCase: "kebab-case"          # kebab-case / PascalCase / snake_case
  apiPrefix: "/api/v1"

# 字典/枚举管理
dictionaries:
  source: "backend"               # backend / frontend / config
  naming: "camelCase"
  predefined:                     # 预定义字典列表
    - name: "status"
      label: "状态"
      values:
        - { value: 0, label: "待处理" }
        - { value: 1, label: "进行中" }
        - { value: 2, label: "已完成" }

# 公共字段定义
commonFields:
  - name: "createBy"
    label: "创建人"
    type: "user"
    readonly: true
  - name: "createTime"
    label: "创建时间"
    type: "datetime"
    format: "YYYY-MM-DD HH:mm:ss"
    readonly: true

# 设计图格式
designFormat:
  primary: "yaml"                # yaml / markdown / ascii / html
  supported: ["yaml", "markdown"]

# API 规范
api:
  format: "markdown"             # markdown / openapi / json
  paramStyle: "camelCase"

# 字段类型约束
fieldConstraints:
  dateFormat: "YYYY-MM-DD"
  numberPrecision: 2
  textMaxLength: 255

# 输出配置
output:
  language: "zh-CN"
  includeGapAnalysis: true
  includePageRelations: true
  includePrdFieldIndex: true

# 生成器开关
generators:
  approval: true                 # 审批流专题
  dictNav: true                  # 字典速查表
  modal: true                    # 弹窗详情
```

---

## 配置验证规则

| 字段 | 必填 | 合法值 | 默认值 | 非法时处理 |
|------|------|--------|--------|-----------|
| `version` | 是 | `"1.0"` | 无 | 拒绝生成，提示版本不支持 |
| `project.name` | 是 | 字母数字+连字符，3-50 字符 | 无 | 拒绝生成，提示命名规则 |
| `project.domain` | 是 | 非空字符串 | 无 | 拒绝生成 |
| `naming.fieldCase` | 否 | `camelCase`, `snake_case` | `camelCase` | 警告，使用默认值 |
| `naming.fileCase` | 否 | `kebab-case`, `PascalCase`, `snake_case` | `kebab-case` | 警告，使用默认值 |
| `dictionaries.source` | 否 | `backend`, `frontend`, `config` | `backend` | 警告，使用默认值 |
| `designFormat.primary` | 否 | `yaml`, `markdown`, `ascii`, `html` | `yaml` | 警告，使用默认值 |
| `designFormat.supported` | 否 | `primary` 必须在列表中 | 与 primary 相同 | 拒绝 |
| `generators.*` | 否 | `true`, `false` | `true` | 警告，使用默认值 |
| `commonFields[].type` | 否 | `user`, `datetime`, `boolean`, `string`, `number` | 无 | 警告，保留但不做特殊处理 |

---

## 模板渲染流程

模板源来自现有 `generate-prd-guide` skill。

### 渲染逻辑

模板变量语法（由 LLM 执行替换）：

| 语法 | 含义 |
|------|------|
| `{{variable}}` | 变量替换 |
| `{{#if condition}}...{{/if}}` | 条件渲染 |
| `{{#each array}}...{{/each}}` | 循环渲染 |

### 文件渲染规则

| 文件 | 渲染方式 | 说明 |
|------|---------|------|
| `SKILL.md.template` | 变量替换 | 主入口，注入项目配置到 name/description/工作流 |
| `references/*.template` | 静态复制 | 直接从 generate-prd-guide/references/ 复制，不做替换 |
| `agents/*.template` | 静态复制 | 直接从 generate-prd-guide/agents/ 复制，不做替换 |
| `config/project-config.yaml` | 序列化配置 | 将收集到的配置写入此文件，供后续复用 |

### SKILL.md.template 变量替换点

| 变量 | 替换位置 |
|------|---------|
| `{{project.name}}` | skill name、标题、描述 |
| `{{project.domain}}` | skill 描述、项目配置表 |
| `{{directory.output}}` | 项目配置表 |
| `{{naming.fieldCase}}` | 项目配置表 |
| `{{dictionaries.source}}` | 项目配置表 |
| `{{designFormat.primary}}` | 项目配置表、兼容性说明 |
| `{{designFormat.supported}}` | 兼容性说明 |
| `{{dictionaries.predefined}}` | 字典定义章节（循环渲染） |
| `{{commonFields}}` | 公共字段章节（循环渲染） |
| `{{generators.*}}` | 工作流阶段开关（条件渲染） |

工作流的静态内容（阶段 0 到阶段 3 的详细流程）直接复制自 generate-prd-guide，不替换变量。

---

## 生成的 Skill 结构

```
.claude/skills/generate-{project.name}-guide/
├── SKILL.md                        # 主入口（变量已替换）
├── references/
│   ├── scanner-rules.md            # 设计图解析规则（静态复制）
│   ├── indexer-rules.md            # 检索策略（静态复制）
│   └── output-templates.md         # 输出模板（静态复制）
├── agents/
│   ├── scanner.md                  # Scanner agent（静态复制）
│   ├── validator.md                # Validator agent（静态复制）
│   ├── indexer.md                  # Indexer agent（静态复制）
│   ├── generator-module.md         # Generator agent（静态复制）
│   └── assembler.md                # Assembler agent（静态复制）
└── config/
    └── project-config.yaml          # 项目配置快照
```

### 生成的 Skill 核心能力

| 能力 | 说明 |
|------|------|
| 设计图解析 | 支持 YAML/Markdown/ASCII/HTML 格式 |
| PRD 交叉验证 | 检测设计图与 PRD 的差异，三级验证（P0/P1/P2） |
| 三源索引 | 设计图 + PRD + API 文档交叉匹配 |
| 字典处理 | 自动识别和映射字典字段 |
| 公共字段注入 | 自动添加创建人、创建时间等只读字段 |
| 缝隙检测 | 识别未明确的信息，输出缝隙清单 |
| 模块级输出 | 每个页面/模块独立成文 |
| Mermaid 功能地图 | 页面/模块跳转关系图 |
| PRD 字段索引 | 章节号 + 锚点位置索引 |

### 生成的 Skill 工作流

```
阶段 0：Scanner — 设计图扫描（提取页面/模块/字段/按钮）
阶段 0.5：Validator — 设计图与 PRD 交叉验证（P0 失败则终止）
阶段 1：Indexer — 三源交叉索引（PRD 四轮检索 + API 匹配）
阶段 2：Generator — 模块级生成
  → 页面详情（始终启用）
  → 字典速查（generators.dictNav=true）
  → 审批流专题（generators.approval=true）
  → 弹窗详情（generators.modal=true）
阶段 2.5：生成物确认（用户确认后继续）
阶段 3：Assembler — 组装 + 缝隙检测
```

---

## 执行流程

```
用户调用 /skill-generator
    │
    ▼
  是否有 config 参数？
    ├── 是 → 加载 YAML 配置文件
    └── 否 → 交互式问答（四轮 + 确认轮）
    │
    ▼
  配置验证（按验证规则检查）
    ├── 失败 → 报错，提示修正
    └── 通过 → 继续
    │
    ▼
  渲染模板（替换变量 + 复制静态文件）
    │
    ▼
  写入 .claude/skills/generate-{project.name}-guide/
    │
    ▼
  导出配置文件到 config/project-config.yaml（可选）
    │
    ▼
  输出完成提示 + 生成的 skill 触发词示例
```

---

## 完成后提示

生成完成后，告知用户：

1. 生成的 skill 位置：`.claude/skills/generate-{project.name}-guide/`
2. 触发方式：`/generate-{project.name}-guide prdPath=@prd.md designPath=@design.yaml moduleName=<名称> version=v1.0 outputDir=@output`
3. 配置快照位置：`.claude/skills/generate-{project.name}-guide/config/project-config.yaml`
4. 重新生成时可直接传入 config 路径跳过问答
