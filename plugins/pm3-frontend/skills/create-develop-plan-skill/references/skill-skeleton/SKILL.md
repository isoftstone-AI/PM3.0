---
name: {{skillName}}
description: |
  根据 PRD 文档、字段数据和设计图文档，自动生成字段级开发方案文档（Markdown 格式，模块化架构）。

  当用户有以下需求时触发此 skill：
  - 需要生成字段级开发方案文档
  - 需要将 PRD + 字段数据转换为开发指引
  - 提到"生成开发方案"、"字段级开发文档"、"开发方案生成器"等关键词
  - 提供了 PRD 路径和字段数据，需要按模块生成详细开发文档

  参数通过 args 传递，格式：key=value，空格分隔。
  基础使用示例（仅需设计方案地址和输出路径）：
  /{{skillName}} designDocPath="设计管理/设计方案v2/xxx.md" outputPath="开发方案/01-列表页-M1-筛选查询区.md"

  完整参数示例（覆盖所有可选参数）：
  /{{skillName}} designDocPath="设计管理/设计方案v2/xxx.md" outputPath="开发方案/01-列表页-M1-筛选查询区.md" pageType=list pageName="xxx列表页" pagePath="module/page" moduleCode="M1" moduleName="筛选查询区" fieldData='{"fields":[...]}' refModule="reference-module"

arguments: |
  必填：designDocPath, outputPath
  可选：pageType, pageName, pagePath, moduleCode, moduleName, fieldData, refModule, prdPath, pages, mermaidDiagram, designSection, styleConfig, logicReference, skillDocPath, projectRulePath, ruleSection

argument-hint: |
  designDocPath="设计方案文档路径" outputPath="输出文件路径" [pageType=<{{pageTypeOptions}}>] [pageName="页面中文名"] [pagePath="模块/页面-kebab-case"] [moduleCode=<M1|M2|M3|M4>] [moduleName="模块中文名"] [fieldData='{"fields":[...]}'] [refModule=参考模块] [prdPath=PRD路径] [pages=页面汇总JSON] [mermaidDiagram=流程图定义] [designSection=设计图章节] [styleConfig=样式配置JSON] [logicReference=逻辑文档引用] [skillDocPath=Skill文档路径] [projectRulePath=项目规范路径] [ruleSection=规范章节]
---

# 开发方案生成器

> **版本：** v1.0
> **用途：** 根据 PRD 和字段数据生成字段级开发方案文档
> **架构：** 模板文件 + 显式变量替换 + 共享片段组合
> **技术栈：** {{techStack}}

根据 PRD 文档、字段数据和设计图文档，自动生成字段级开发方案文档。**模块化架构**采用模板驱动生成，目标是让开发者拿到文档后可以直接按字段编写代码，每个字段都有组件、属性、校验规则。

**重要原则：** 生成的开发方案是对应页面类型的代码生成 Skill 的**输入参数**，不是代码模板。方案中只提供字段属性（field、label、component、dictCode 等）和业务逻辑描述，**不生成可复制粘贴的代码示例**。最终代码结构由 Skill 模板决定。

---

## 核心架构说明

| 维度 | 说明 |
|------|------|
| **驱动方式** | 字段数据 + 模板驱动 |
| **生成粒度** | 模块维度（每个模块一个文件） |
| **输出结构** | 主索引 + 模块子文件 |
| **模板机制** | 读取模板文件 → 用入参值替换占位符 → 展开循环 → 组合共享片段 → 输出 Markdown |
| **自检集成** | 每个模块内嵌自检清单 + 参考模块对比 |

参数缺失时交互式询问。

---

## 支持的页面类型

{{pageTypeTable}}

> **注意**：页面类型和对应的代码生成 Skill 由 CLAUDE.md 中的「场景→Skill 映射」决定。
> 如果 CLAUDE.md 未定义映射，则使用以下通用默认值：

| pageType | 通用描述 | 默认代码生成方式 |
|----------|---------|----------------|
| `list` | 列表页（搜索+表格+分页） | 手动或项目 Skill |
| `form` | 表单页（新增/编辑） | 手动或项目 Skill |
| `approval` | 审批页（只读+填写+操作） | 手动或项目 Skill |
| `detail` | 详情页（只读展示） | 手动或项目 Skill |
| `modal` | 选择弹窗（搜索+表格+单选） | 手动或项目 Skill |

---

## 输入参数

### 必填参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `designDocPath` | string | 设计方案文档路径（优先读取"特别强调"章节） | `设计管理/设计方案v2/xxx.md` |
| `outputPath` | string | 输出文件路径 | `开发方案/01-列表页-M1-筛选查询区.md` |

> **仅传 designDocPath + outputPath 时**：从设计方案文档中自动提取 pageType、pageName、fieldData 等信息。如果设计方案内容不足以提取，则交互式询问缺失参数。

### 可选参数（显式传递时优先级高于设计方案提取）

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `pageType` | string | 页面类型：{{pageTypeOptions}} | `list` |
| `pageName` | string | 页面中文名 | xxx列表页 |
| `pagePath` | string | 页面路径（kebab-case） | `module/page` |
| `moduleCode` | string | 模块编码 | `M1` / `M2` / `M3` / `M4` |
| `moduleName` | string | 模块中文名 | 筛选查询区 |
| `fieldData` | JSON | 字段数据（见下方格式） | 见下方 |
| `refModule` | string | 参考模块路径 | `reference-module` |
| `prdPath` | string | 开发方案文档路径（供代码生成 Skill 读取） | `设计管理/开发方案/01-xxx.md` |
| `pages` | JSON | 页面汇总信息（用于生成索引） | 见下方格式 |
| `mermaidDiagram` | string | Mermaid 页面关系图定义 | `flowchart TD\n  A --> B` |
| `designSection` | string | 设计图章节引用 | `3.2.1 表单布局样式` |
| `styleConfig` | JSON | 样式配置对象（间距、对齐、宽度等） | `{"layout":"2列","gutter":"16px"}` |
| `logicReference` | string | 逻辑对应的设计文档章节引用 | `4.3.2 字段交互规则` |
| `skillDocPath` | string | 对应 Skill 的使用文档路径 | `开发规范/Skill使用指南/` |
| `projectRulePath` | string | 项目规范文档路径 | `开发规范/前端开发规范.md` |
| `ruleSection` | string | 项目规范对应章节 | `5.2 表单开发规范` |

### fieldData 格式

```json
{
  "fields": [
    {
      "name": "fieldName",
      "label": "字段中文名",
      "component": "Input",
      "required": true,
      "maxLength": 128,
      "dictCode": null,
      "readOnly": false,
      "linkage": null,
      "defaultValue": null,
      "placeholder": "请输入"
    }
  ],
  "columns": [
    {
      "title": "列标题",
      "dataIndex": "fieldName",
      "width": 180,
      "fixed": "left",
      "sorter": true
    }
  ],
  "nodePermissions": [
    {
      "nodeKey": "APPLICANT",
      "nodeName": "申请人",
      "editableFields": ["ALL"],
      "readonlyFields": ["submitStatus"]
    }
  ],
  "linkages": [
    {
      "name": "联动名称",
      "triggerField": "triggerField",
      "triggerCondition": "val === '1'",
      "affectedFields": "affectedField",
      "action": "setRequired('affectedField', true)"
    }
  ],
  "buttons": [
    {
      "status": "DRAFT",
      "buttons": "编辑",
      "api": "updateApi",
      "action": "跳转编辑页"
    }
  ]
}
```

---

## 执行流程

> **模板处理方式**：本 skill 不使用 Handlebars 编译器。AI 直接读取模板文件（Markdown 格式），将 `{{变量名}}` 替换为入参值，将 `{{#each}}` 循环展开为多行，将 `{{> partial}}` 共享片段替换为对应文件内容。

### Step 1: 解析输入 + 读取设计方案

**输入**：`designDocPath`, `outputPath`, 以及可选参数

**操作**：
1. 读取 `designDocPath` 指定的设计方案文档
2. 从设计方案中提取高优先级信息：
   - "特别强调"章节 → 逐条记录
   - "关键差异提醒"章节 → 逐条记录
   - 含"以 API 为准"、"以设计图为准"标记的说明 → 记录覆盖规则
3. 如果用户显式传递了参数，**以用户传值为准**
4. 如果用户只传了 `designDocPath` + `outputPath`，从设计方案中提取缺失参数；提取失败则**交互式询问**

**异常处理**：
- `designDocPath` 文件不存在 → 报错并停止
- `fieldData` JSON 格式错误 → 报错并提示具体解析错误位置
- `outputPath` 父目录不存在 → 自动创建父目录

---

### Step 2: 选择模板

根据 `pageType` 确定模板目录和模块模板文件（见下方[模板路由规则](#模板路由规则)）。

**⏸️ 检查点 1：暂停确认**
展示选择的模板文件路径、共享片段列表、特别强调内容摘要，等待确认。

---

### Step 3: 加载模板 + 共享片段 + 参考数据

1. 读取 Step 2 确定的模板文件
2. 读取所有共享片段（`templates/_shared/` 下的文件）
3. 读取参考数据（`references/` 下的 JSON 文件）

---

### Step 4: 精度规则校验 + 字段映射

1. 从设计方案的"节点编辑权限配置"表格中**逐字复制** requiredFields 列表
2. operationType、节点标识等枚举值**直接使用原始值**
3. 接口定义（HTTP 方法、路径、参数结构）**直接使用设计方案的定义**
4. 分页配置从设计方案精确提取
5. 为每个字段准备完整的 4 段逻辑数据
6. 将组件名与 `references/components.json` 比对

**⏸️ 检查点 2：暂停确认**
展示字段映射总览、精度规则校验结果、与参考模块的差异点。

---

### Step 5: 生成文档（变量替换）

**替换规则**（按优先级执行）：

1. **共享片段替换**：`{{> 片段名}}` → 读取对应文件内容
2. **条件渲染**：`{{#if 变量}}...{{else}}...{{/if}}` → 条件分支
3. **循环展开**：`{{#each 数组}}...{{/each}}` → 遍历展开
4. **变量替换**：`{{变量名}}` → 入参值

**替换顺序**：partial → if → each → variable

---

### Step 6: 写入文件

确保 `outputPath` 的父目录存在，写入 Markdown 内容。

---

### Step 7: 生成/更新索引文件

如果入参包含 `pages` 字段，生成 `00-索引.md`。

---

### Step 8: 覆盖度检查

扫描已生成文件，与设计方案对比，标记已覆盖/未覆盖。输出 `0-coverage-report.md`。

**⏸️ 检查点 3：暂停确认**

---

### Step 9: 自检清单验证

根据 fieldData 逐项执行自检，生成 `0-self-check-result.md`。

---

### Step 10: 输出汇总

展示生成结果、覆盖度统计、自检结果摘要、后续操作建议。

---

## 模板路由规则

{{templateRoutes}}

---

## 参考数据来源

> 以下数据从项目 CLAUDE.md/AGENTS.md 自动提取，主要适用于当前项目。其他业务模块使用时，应替换为对应业务的实际数据。

### components.json

包含 {{componentCount}} 个组件的选型映射。详见 `references/components.json`。

### dicts.json

包含 {{dictCount}} 个字典编码映射。详见 `references/dicts.json`。

### modules.json

包含 {{moduleCount}} 个参考模块路径。详见 `references/modules.json`。

---

## 输出文档结构

```
{outputDir}/
├── 0-coverage-report.md          # 覆盖度检查报告
├── 0-self-check-result.md        # 自检清单结果
├── 00-索引.md                    # 主索引
├── 01-列表页-M1-筛选查询区.md    # 模块文档
├── ...
├── 10-全局接口清单.md             # 手动维护
├── 11-全局组件清单.md             # 手动维护
└── 12-Skill 使用指引.md           # 手动维护
```

---

## 异常处理汇总

| 场景 | 触发条件 | 处理动作 |
|------|---------|---------|
| 设计方案不存在 | `designDocPath` 文件读取失败 | 报错并停止 |
| fieldData JSON 格式错误 | JSON.parse 失败 | 报错并提示具体解析错误位置 |
| outputPath 父目录不存在 | 写入前检查目录 | 自动 `mkdir -p` |
| pageType 非法 | 不在合法范围 | 报错并列出合法值 |
| 模板路由不匹配 | pageType + moduleCode 组合无对应模板 | 报错并展示可用 moduleCode |
| 模板文件缺失 | templates/ 下对应文件不存在 | 报错并列出实际存在的文件 |
| refModule 路径不存在 | 参考模块路径无效 | 警告但不停止 |
| 覆盖率 < 100% | 覆盖度检查发现未覆盖项 | 列出未覆盖清单 |
| 参数缺失 | 必填参数为空且无法提取 | 交互式逐一询问 |

---

## 扩展新页面类型

1. 创建 `templates/{pageType}-page/` 目录
2. 添加模块模板文件（使用 `{{变量}}` 占位符 + `{{#each}}` 循环语法）
3. 在 `references/` 中添加参考数据
4. 在本文件的"模板路由规则"中添加新规则
5. 更新 `argument-hint` 中的 pageType 可选值
