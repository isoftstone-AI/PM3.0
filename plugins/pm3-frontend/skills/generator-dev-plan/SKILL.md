---
name: generator-dev-plan
description: |
  根据 PRD 文档、字段数据和设计图文档，自动生成字段级开发方案文档（Markdown 格式，模块化架构）。

  当用户有以下需求时触发此 skill：
  - 需要生成字段级开发方案文档
  - 需要将 PRD + 字段数据转换为开发指引
  - 提到"生成开发方案"、"字段级开发文档"、"开发方案生成器"等关键词
  - 提供了 PRD 路径和字段数据，需要按模块生成详细开发文档
  - 本 skill 采用状态机执行协议（借鉴 LangGraph 思想）：主会话编排 + subagent 隔离生成 + 黑板 state，解决多模块生成的上下文溢出

  参数通过 args 传递，格式：key=value，空格分隔。
  基础使用示例（仅需设计方案地址和输出路径）：
  /generator-dev-plan designDocPath="设计管理/设计方案v2/设备提资.md" outputPath="设备提资模块详情页 v2/01-列表页-M1-筛选查询区.md"

  完整参数示例（覆盖所有可选参数）：
  /generator-dev-plan designDocPath="设计管理/设计方案v2/设备提资.md" outputPath="设备提资模块详情页 v2/01-列表页-M1-筛选查询区.md" pageType=list pageName="设备提资列表页" pagePath="design-manage/equipment-submission" moduleCode="M1" moduleName="筛选查询区" fieldData='{"fields":[{"name":"projectName","label":"项目名称","component":"Input","required":false}]}' refModule="special-review"

arguments: |
  必填：designDocPath, outputPath, apiDocSource
  可选：pageType, pageName, pagePath, moduleCode, moduleName, fieldData, refModule, prdPath, pages, mermaidDiagram, designSection, styleConfig, logicReference, skillDocPath, projectRulePath, ruleSection

argument-hint: |
  designDocPath="设计方案文档路径" outputPath="输出文件路径" apiDocSource=<apifox|md:路径> [pageType=<list|form|approval|detail|modal>] [pageName="页面中文名"] [pagePath="模块/页面-kebab-case"] [moduleCode=<M1|M2|M3|M4>] [moduleName="模块中文名"] [fieldData='{"fields":[...]}'] [refModule=参考模块] [prdPath=PRD路径] [pages=页面汇总JSON] [mermaidDiagram=流程图定义] [designSection=设计图章节] [styleConfig=样式配置JSON] [logicReference=逻辑文档引用] [skillDocPath=Skill文档路径] [projectRulePath=项目规范路径] [ruleSection=规范章节]
  apiDocSource 格式说明：
    - apifox：通过 Apifox MCP 自动拉取 OpenAPI Spec，按模块名筛选相关接口
    - md:文件路径：读取本地 MD/YAML/JSON 接口文档（如 "md:设计管理/接口文档/设备提资接口.md"）
---

### 新增页面类型说明

| pageType | 说明 | 设计方案匹配规则 |
|----------|------|-----------------|
| `detail` | 审批详情页（全量只读+审批记录） | 文件名含 `approval-detail` 或 `detail` |
| `modal` | 选择弹窗（搜索+表格+单选） | 文件名含 `modal-select` 或 `modal` |

**使用示例：**
```bash
# 生成审批详情页
/generator-dev-plan pageType=detail pageName="设备提资审批详情页" pagePath="design-manage/equipment-submission" moduleCode="M1" moduleName="全量只读" fieldData='{"fields":[...]}' outputPath="开发方案v2/07-审批详情页.md"

# 生成选择弹窗
/generator-dev-plan pageType=modal pageName="选择项目弹窗" pagePath="design-manage/equipment-submission" moduleCode="M1" moduleName="搜索+选择" fieldData='{"searchFields":[...],"tableColumns":[...],"returnMapping":[...]}' outputPath="开发方案v2/13-选择项目弹窗.md"
```

# 开发方案生成器

> **版本：** v2.0
> **用途：** 根据 PRD 和字段数据生成字段级开发方案文档
> **架构：** 模板文件 + 显式变量替换 + 共享片段组合

根据 PRD 文档、字段数据和设计图文档，自动生成字段级开发方案文档。**模块化架构**采用模板驱动生成，目标是让开发者拿到文档后可以直接按字段编写代码，每个字段都有组件、属性、校验规则。

**重要原则：** 生成的开发方案是 skill（如 `/scene-list`、`/scene-form`）的**输入参数**，不是代码模板。方案中只提供字段属性（field、label、component、dictCode 等）和业务逻辑描述，**不生成可复制粘贴的代码示例**。最终代码结构由 skill 模板决定。

---

## 核心架构说明

| 维度 | 说明 |
|------|------|
| **驱动方式** | 字段数据 + 模板驱动 |
| **生成粒度** | 模块维度（每个模块一个文件） |
| **输出结构** | 主索引 + 模块子文件 |
| **模板机制** | 读取模板文件 → 用入参值替换占位符 → 展开循环 → 组合共享片段 → 输出 Markdown |
| **自检集成** | 每个模块内嵌自检清单 + 参考模块对比 |
| **编排方式** | 状态机执行协议（PARSE→CK1→GEN×N→JOIN→SUMMARY→CK3），借鉴 LangGraph 思想，主会话编排 + subagent 隔离 + 黑板 state（详见「编排层总览」） |

参数缺失时交互式询问。

---

## 编排层总览

> 本 skill 借鉴 LangGraph 状态机思想，把生成流程拆为节点 + 条件路由 + 黑板状态。状态机以本文件指令协议形式描述，Claude 作为运行时执行。

### LangGraph ↔ Claude Code 映射

| LangGraph 概念 | Claude Code 对应 |
|---|---|
| StateGraph（状态图） | 主会话编排逻辑（本文件指令描述） |
| State（共享状态） | 黑板文件 `.blackboard.json` + `.blackboard.md`（人类可读摘要） |
| Node（节点函数） | subagent（GEN 节点）或主会话内的阶段（PARSE/SUMMARY） |
| conditional edge（条件路由） | 主会话读黑板 `modules[].status` 做路由判断 |
| interrupt（human-in-the-loop） | 检查点 CK1/CK3，主会话暂停等用户确认 |
| checkpointer（断点续跑） | 黑板文件持久化 + `meta.signature` 匹配恢复 |
| map-reduce 的 map | 多模块 GEN subagent 并行 fan-out |

### 状态机拓扑

```
START → [PARSE·主会话] → ⏸️CK1 → [ROUTE] ⇄ [GEN·subagent×N] → [JOIN] → [SUMMARY·主会话] → ⏸️CK3 → END
```

详细节点规范、黑板 schema、路由规则、检查点、错误处理、断点续跑见下方「执行流程（状态机执行协议）」与「subagent 派发协议」「断点续跑协议」章节。

---

## 输入参数

### 必填参数

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `designDocPath` | string | 设计方案文档路径（优先读取"特别强调"章节） | `设计管理/设计方案v2/设备提资.md` |
| `outputPath` | string | 输出文件路径 | `设备提资模块详情页 v2/01-列表页-M1-筛选查询区.md` |
| `apiDocSource` | string | API 文档来源 | `apifox` 或 `md:设计管理/接口文档/设备提资接口.md` |

> **仅传 designDocPath + outputPath + apiDocSource 时**：从设计方案文档中自动提取 pageType、pageName、fieldData 等信息，从 apiDocSource 提取接口字段映射。如果设计方案内容不足以提取，则交互式询问缺失参数。

### 可选参数（显式传递时优先级高于设计方案提取）

| 参数 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `pageType` | string | 页面类型：`list` / `form` / `approval` / `detail` / `modal` | `list` |
| `pageName` | string | 页面中文名 | 设备提资列表页 |
| `pagePath` | string | 页面路径（kebab-case） | `design-manage/equipment-submission` |
| `moduleCode` | string | 模块编码 | `M1` / `M2` / `M3` / `M4` |
| `moduleName` | string | 模块中文名 | 筛选查询区 |
| `fieldData` | JSON | 字段数据（见下方格式） | 见下方 |
| `refModule` | string | 参考模块路径 | `special-review` |
| `prdPath` | string | 开发方案文档路径（供 scene-* skill 生成代码时读取） | `设计管理/开发方案/01-列表页-M1-筛选查询区.md` |
| `pages` | JSON | 页面汇总信息（用于生成索引） | 见下方格式 |
| `mermaidDiagram` | string | Mermaid 页面关系图定义 | `flowchart TD\n  A --> B` |
| `designDocPath` | string | 设计图文档路径（用于样式引用） | `设计管理/UI设计/设备提资设计稿.md` |
| `designSection` | string | 设计图章节引用 | `3.2.1 表单布局样式` |
| `styleConfig` | JSON | 样式配置对象（间距、对齐、宽度等） | `{"layout":"2列","gutter":"16px"}` |
| `logicReference` | string | 逻辑对应的设计文档章节引用 | `4.3.2 字段交互规则` |
| `skillDocPath` | string | 对应 Skill 的使用文档路径 | `开发规范/Skill使用指南/scene-form.md` |
| `projectRulePath` | string | 项目规范文档路径 | `开发规范/PM3.0前端开发规范.md` |
| `ruleSection` | string | 项目规范对应章节 | `5.2 表单开发规范` |

### fieldData 格式

```json
{
  "fields": [
    {
      "name": "projectName",
      "label": "项目名称",
      "component": "Input",
      "required": true,
      "maxLength": 128,
      "dictCode": null,
      "readOnly": false,
      "linkage": null,
      "defaultValue": null,
      "placeholder": "请输入项目名称",
      "apiFieldName": "projectName",
      "apiType": "string",
      "apiRequired": true,
      "apiEnum": null,
      "apiFieldDiff": false
    }
  ],
  "columns": [
    {
      "title": "申请单号",
      "dataIndex": "applyNo",
      "width": 180,
      "fixed": "left",
      "sorter": true,
      "dictCode": null
    }
  ],
  "nodePermissions": [
    {
      "nodeKey": "APPLICANT",
      "nodeName": "申请人",
      "allowAddRow": true,
      "allowDeleteRow": true,
      "editableFields": ["ALL"],
      "editableFieldsList": ["equipmentName", "specModel", "quantity"],
      "readonlyFields": ["submitStatus"]
    }
  ],
  "linkages": [
    {
      "name": "业态联动容量字段",
      "triggerField": "format",
      "triggerCondition": "val === '1'",
      "affectedFields": "capacityTotal",
      "action": "setRequired('capacityTotal', true)"
    }
  ],
  "buttons": [
    {
      "status": "DRAFT",
      "buttons": "编辑",
      "api": "updateSubmission",
      "confirm": null,
      "action": "跳转编辑页"
    }
  ],
  "prdSection": "4.11.5.1.3",
  "specialNotes": "分公司 - 区域需要联动",
      "apis": [
        {
          "apiName": "getEquipmentSubmissionList",
          "method": "POST",
          "path": "/api/pm-design/equipmentSubmission/list",
          "description": "分页查询设备提资列表",
          "callTiming": "列表页初始化、搜索、分页",
          "requestType": "EquipmentSubmissionSearchParams",
          "responseType": "Page<EquipmentSubmissionRecord>",
          "requestParams": [
            { "paramName": "pageNum", "paramType": "number", "required": true, "description": "页码" },
            { "paramName": "projectName", "paramType": "string", "required": false, "description": "项目名称（模糊查询）" }
          ],
          "responseFields": [
            { "fieldName": "id", "fieldType": "string", "description": "提资 ID" },
            { "fieldName": "submissionNo", "fieldType": "string", "description": "提资单号" }
          ]
        }
      ],
  "pages": [
    {
      "pageId": "equipment-submission-list",
      "pageName": "设备提资列表页",
      "pageType": "list",
      "modules": ["M1-筛选查询区", "M2-主内容表格区"]
    }
  ],
  "mermaidDiagram": "flowchart TD\n  List[设备提资列表页] --> Form[设备提资申请表单]\n  Form --> List"
}
```

#### `pages` 字段说明

用于自动生成 `00-索引.md`，汇总所有页面和模块。

| 字段 | 类型 | 说明 |
|------|------|------|
| `pageId` | string | 页面标识（kebab-case） |
| `pageName` | string | 页面中文名 |
| `pageType` | string | 页面类型：list / form / approval / detail / modal |
| `modules` | string[] | 该页面包含的模块列表 |

#### `mermaidDiagram` 字段说明

Mermaid 流程图定义字符串，用于在索引文件和每个模块文档头部渲染页面关系图。不提供时不渲染图。

---

## 执行流程（状态机执行协议）

> 本流程遵循状态机执行协议（PARSE→CK1→GEN×N→JOIN→SUMMARY→CK3），借鉴 LangGraph 思想。主会话负责 PARSE/SUMMARY 与黑板管理，GEN 阶段每个模块由独立 subagent 执行（隔离上下文）。黑板 `.blackboard.json` 贯穿全程作为 State。

> **模板处理方式**：本 skill 不使用 Handlebars 编译器。AI 直接读取模板文件（Markdown 格式），将 `{{变量名}}` 替换为入参值，将 `{{#each}}` 循环展开为多行，将 `{{> partial}}` 共享片段替换为对应文件内容。

### 节点归属表

下方 Step 1-10 按状态机节点重组执行：

| 状态机节点 | 承接原 Step | 执行者 | 黑板交互 |
|---|---|---|---|
| **PARSE**（解析） | Step 1 + 1.5 + 2（路由）+ 3（仅定路径）+ 4（精度校验+字段映射） | 主会话 | 读设计方案 → 初始化 `.blackboard.json`（meta/designDigest/modules/progress） |
| **CK1**（检查点1） | 原 ⏸️1 + ⏸️2 合并 | 主会话↔用户 | 读黑板展示，用户确认后进 GEN |
| **ROUTE**（路由） | — | 主会话 | 读 `modules[].status` 决定下一步 |
| **GEN**（生成） | Step 5 + 6 | **subagent ×N 并行** | 读黑板 designDigest+slice → 写模块 .md → 返回 {ok,error} |
| **JOIN**（汇入） | — | 主会话 | 收集 GEN 返回 → 更新 modules[].status/progress（黑板只此节点写） |
| **SUMMARY**（汇总） | Step 7 + 8 + 9 | 主会话 | 读黑板+扫 outputDir → 写索引/覆盖度/自检 |
| **CK3**（检查点3） | 原 ⏸️3 | 主会话↔用户 | 展示覆盖率，确认/补生成/终止 |
| **END**（汇总输出） | Step 10 | 主会话 | — |

### 关键变化（相对旧版线性流程）

1. **PARSE 节点只定路径不持全文**：Step 3 仅确定 `templatePath` 与 `sharedPartials` 并写黑板，**不读取模板全文**（模板全文由 GEN subagent 各自读取，避免主会话上下文膨胀）
2. **GEN 由 subagent 执行**：Step 5-6 的变量替换 + 写文件改为每个模块派一个 `general-purpose` subagent，主会话读 `templates/_shared/gen-subagent-prompt.md` 注入槽位后用 Agent tool 派发，并发上限 4-6
3. **黑板只由主会话在 JOIN 写**：subagent 不写黑板，只返回结果 → 无并发竞态
4. **检查点合并**：原 ⏸️1（Step 2 后）+ ⏸️2（Step 4 后）合并为 CK1（fan-out 前一次确认）；原 ⏸️3 保留为 CK3
5. **断点续跑**：PARSE 入口先读 `.blackboard.json`，`meta.signature` 匹配则跳过 done 模块（详见「断点续跑协议」）

> 下方 Step 1-10 的**业务内容保持不变**，仅执行者与编排方式按上表调整。GEN 阶段（Step 5-6）的实际执行由 subagent 完成（见 Step 5/6 开头的 GEN 节点注记与「subagent 派发协议」章节）。

### Step 1: 解析输入 + 读取设计方案

**输入**：`designDocPath`, `outputPath`, 以及可选参数

**操作**：
1. 判断 `designDocPath` 模式：
   - 以 `apifox` 开头 → **apifox 模式**：从 Apifox MCP 拉取设计方案数据
   - 否则 → **md 模式**：读取本地 MD 文件（现有逻辑）

2. **apifox 模式下读取设计方案**：
   a. 调用 MCP 工具 `read_project_oas` 获取 OpenAPI Spec 的 paths 列表
   b. 按 `designDocPath` 中指定的模块名（如 `apifox:设备提资`）筛选相关接口
   c. 调用 `read_project_oas_ref_resources` 批量读取接口详情
   d. 递归读取 `components/schemas`（上限 3 层）
   e. 从接口 summary/description 提取业务规则描述
   f. 从 schema 字段提取：字段英文名、类型、枚举值、必填性
   g. 将提取结果组装为 fieldData 结构化数据（字段→API 映射）

3. **md 模式下读取设计方案**（现有逻辑）：
   a. 读取 `designDocPath` 指定的设计方案文档
   b. **精度规则 #1（铁律）**：提取"特别强调"章节、"关键差异提醒"章节
   c. 含"以 API 为准"、"以设计图为准"标记的说明 → 记录覆盖规则41580

4. 如果用户显式传递了 `pageType`、`pageName`、`fieldData` 等，**以用户传值为准**

5. 如果用户只传了 `designDocPath` + `outputPath`，从设计方案中提取缺失参数；提取失败则**交互式询问**

**异常处理**：
- `designDocPath` 文件不存在（md 模式）或 MCP 不可用（apifox 模式）→ 报错并停止，提示用户检查
- `fieldData` JSON 格式错误 → 报错并提示具体解析错误位置
- `outputPath` 父目录不存在 → 自动创建（`mkdir -p`）

**输出**：解析后的完整参数对象

---

### Step 1.5: 加载 API 文档（如有 apiDocSource）

> **执行条件**：入参包含 `apiDocSource`（非空）。如未提供则跳过此步骤，字段 API 映射留空。

**输入**：`apiDocSource`

**操作**：

根据 `apiDocSource` 类型执行：

#### apifox 模式（apiDocSource=apifox）

1. 调用 MCP 工具 `read_project_oas` 获取 OpenAPI Spec 的 paths 列表
2. **接口筛选**：按当前模块的关键词（`pagePath`、`moduleName`）筛选相关接口：
   - 路径匹配：接口路径包含模块关键词
   - summary 匹配：接口 summary 包含模块中文名
   - 筛选后展示给用户确认（列出匹配到的接口及数量）
3. 调用 `read_project_oas_ref_resources` 传入筛选后的 `$ref` 路径数组，批量读取接口详情
4. 从接口详情中收集所有 `#/components/schemas/XXX` 引用
5. 递归读取 schemas（上限 3 层），提取字段名、类型、必填性、枚举值、描述5075

#### md 模式（apiDocSource=md:路径）

1. 解析 `md:` 后的文件路径，读取文件内容
2. 文件格式支持：
   - **Markdown 表格**：解析接口表格（方法/路径/参数/响应列）
   - **YAML/JSON Swagger**：直接解析结构
   - **JSON OpenAPI**：同 apifox 的解析
3. 提取：方法、路径、参数、响应字段、描述

**输出**：结构化 API 接口清单（`apiSpec`），含以下内容：

```json
{
  "sourceType": "apifox" | "md",
  "sourceRef": "MCP" | "/path/to/doc.md",
  "interfaces": [
    {
      "apiName": "getXxxList",
      "method": "POST",
      "path": "/api/pm-design/xxx/list",
      "description": "分页查询列表",
      "callTiming": "列表页初始化、搜索、分页",
      "requestType": "XxxSearchParams",
      "responseType": "Page<XxxRecord>",
      "requestParams": [
        { "paramName": "pageNum", "paramType": "number", "required": true, "description": "页码" }
      ],
      "responseFields": [
        { "fieldName": "id", "fieldType": "string", "description": "ID" }
      ]
    }
  ],
  "schemas": {
    "XxxRecord": { "fields": [...] },
    "XxxSearchParams": { "fields": [...] }
  }
}
```

> 此数据用于 Step 4 的字段 API 自动映射和 Step 5 的接口章节生成。

---

### Step 2: 选择模板

**输入**：`pageType`, `moduleCode`

**操作**：
1. 根据 `pageType` 确定模板目录：

   | pageType | 模板目录 |
   |----------|---------|
   | `list` | `templates/list-page/` |
   | `form` | `templates/form-page/` |
   | `approval` | `templates/approval-page/` |
   | `detail` | `templates/detail-page/` |
   | `modal` | `templates/modal-page/` |

2. 根据 `pageType` + `moduleCode` 确定模块模板文件（见下方[模板路由规则](#模板路由规则)）

**异常处理**：
- `pageType` 不在合法范围 → 报错并列出合法值，让用户确认
- `pageType` + `moduleCode` 组合无对应模板 → 报错并展示该 pageType 下所有可用 moduleCode

**输出**：确定的模板文件路径

**⏸️ CK1 检查点（合并原检查点1+2）：暂停确认**

> 原 ⏸️1（此处）与 ⏸️2（Step 4 后）合并为一次 CK1，在 fan-out 前统一展示。

展示以下信息给用户，等待确认后继续：
- 选择的模板文件路径
- 即将读取的共享片段列表
- 从设计方案提取的"特别强调"内容摘要
- 字段映射总览（字段数、组件选型摘要）
- 精度规则校验结果：
  - 特别强调是否全部覆盖
  - 必填字段列表
  - 枚举值是否保留原始值
- 与参考模块的差异点

---

### Step 3: 加载模板 + 共享片段 + 参考数据

**操作**：
1. 读取 Step 2 确定的模板文件
2. 读取所有共享片段（模板中 `{{> xxx}}` 引用的文件）：

   | 片段名 | 文件路径 | 用途 |
   |--------|---------|------|
   | `nav-links` | `templates/_shared/nav-links.md` | 模块间导航链接 |
   | `page-intro` | `templates/_shared/page-intro.md` | 页面导览（Skill 提示、代码位置） |
   | `rule-reference` | `templates/_shared/rule-reference.md` | 前置规则参考 |
   | `design-style` | `templates/_shared/design-style.md` | 设计图样式参考 |
   | `field-detail` | `templates/_shared/field-detail.md` | 字段详细配置（4段逻辑） |
   | `api-section` | `templates/_shared/api-section.md` | 接口章节（业务接口 + 参数详情 + Select 数据源 + 字段映射） |
   | `skill-guide` | `templates/_shared/skill-guide.md` | Skill 使用指引 |
   | `self-check` | `templates/_shared/self-check.md` | 开发自检清单 |
   | `dev-checklist` | `templates/_shared/dev-checklist.md` | 开发流程检查清单 |
   | `dev-reconciliation` | `templates/_shared/dev-reconciliation.md` | 模块完成对账单（字段/接口/逻辑/签字的 4 段 checklist） |

3. 读取参考数据（按需）：

   | 文件 | 用途 |
   |------|------|
   | `references/components.json` | 组件选型 + 默认 props |
   | `references/dicts.json` | 字典编码映射 |
   | `references/modules.json` | 参考模块路径映射 |

**异常处理**：
- 模板文件或共享片段不存在 → 报错并列出该目录下实际存在的文件，让用户选择或修正路径

**输出**：所有模板和参考数据的内容（在内存中）

---

### Step 4: 精度规则校验 + 字段映射

> 本步将精度规则融入执行流程，而非事后检查。

**操作**：
1. **精度规则 #2（铁律）**：从设计方案的"节点编辑权限配置"表格中**逐字复制** `requiredFields` 列表，不省略、不推断、不合并
2. **精度规则 #3（铁律）**：`operationType`、节点标识等枚举值**直接使用设计方案中后端返回的原始值**，不自行简化
3. **精度规则 #4-bis（铁律）**：三源字段映射 — 当设计方案、设计图、API 三者定义同一字段时，按以下优先级处理：

   | 维度 | 以谁为准 | 说明 |
   |------|---------|------|
   | 字段名（英文 key） | **API**（如有 apiDocSource）→ 无 apiDocSource 时以设计方案字面值为准 | 设计图伪代码可能简写，API 定义才是最终交付的字段名 |
   | 字段类型（string/number/boolean） | **API** | 前端 type 定义必须与后端一致 |
   | 枚举值 | **API** | 枚举值以 API 的 enum/x-enum-comments 为准 |
   | 必填性 | **设计方案** | 业务需求决定哪些字段必填 |
   | 字段是否存在（增/删字段） | **设计方案** | API 有但设计方案无 → 标记为"补充字段"；设计方案有但 API 无 → 标记缝隙 |
   | 组件选择 | **设计图** | UI 呈现方式由设计图决定，但伪代码（枚举值/字段名）以 API 为准 |
   | 字段精度/格式化 | **设计方案** | 精度规则（小数位数、日期格式等）以业务需求为准，API 类型作为兜底 |

4. **精度规则 #5（铁律）**：分页配置（pageSize、pageSizeOptions）从设计方案精确提取，不使用默认值
5. **精度规则 #7（铁律）**：如果提供了 `designDocPath`（设计图）和 `styleConfig`，从设计图中提取样式规格，优先级高于组件默认样式
6. **精度规则 #8（铁律）**：为每个字段准备完整的 4 段逻辑数据：
   - 段1：基础信息（field, label, component, required, maxLength, apiFieldName 等）
   - 段2：交互逻辑（校验规则、联动逻辑）
   - 段3：权限控制（节点/角色的可编辑/只读）
   - 段4：业务规则（默认值、计算规则、接口映射）
7. **精度规则 #9（铁律）**：API 字段自动映射 — 如有 apiDocSource，对 fieldData.fields 中每个字段：
   - 用字段中文名（label）模糊匹配 API 的 description/summary
   - 用字段英文名（name）精确匹配 API 的 schema 字段名
   - 匹配成功 → 自动填充 apiFieldName、apiType、apiRequired、apiEnum
   - 匹配失败 → 标记 apiFieldName 为 `⚠️ 未匹配`，加入缝隙清单
   - 伪代码检测：若 name ≠ apiFieldName → apiFieldDiff = true，记录差异到自检报告
8. 将组件名与 `references/components.json` 比对，确认组件选型符合规范

**输出**：完成精度校验的字段映射表

**⏸️ 已合并至 CK1**（见 Step 2 处的 CK1 检查点）

> 原 ⏸️2 的展示内容（字段映射总览、精度规则校验、参考模块差异）并入 CK1 统一展示，不再单独暂停。

---

### Step 5: 生成文档（变量替换）— GEN 节点（subagent 执行）

> ⚠️ **本 Step 由 GEN 节点 subagent 执行，不在主会话跑**。主会话在 GEN 阶段对每个 pending 模块：读取 `templates/_shared/gen-subagent-prompt.md` → 注入 `{moduleCode}` `{moduleName}` `{pageName}` `{pageType}` `{outputFile}` `{designDigest}` `{fieldDataSlice}` `{templatePath}` `{sharedPartials}` → 用 Agent tool 派 `general-purpose` subagent。subagent 按下方 5.1-5.5 规则处理【该模块模板文件】并写文件，返回 `{moduleCode, outputFile, ok, error}`。主会话不持模板全文。详见「subagent 派发协议」。

> **核心步骤**：将模板中的占位符替换为实际值，生成最终 Markdown 文档。

**替换规则**（按优先级执行）：

#### 5.1 共享片段替换

将 `{{> 片段名}}` 替换为对应共享片段文件的**完整内容**：

```
{{> nav-links }}     → 读取 templates/_shared/nav-links.md 的内容替换
{{> field-detail }}   → 读取 templates/_shared/field-detail.md 的内容替换
```

#### 5.2 条件渲染替换

将 `{{#if 变量}}...{{else}}...{{/if}}` 替换为条件分支：

```
{{#if dictCode}}| dictCode | `{{dictCode}}` |{{/if}}
→ 如果该字段有 dictCode，输出 "| dictCode | `projectType` |"
→ 如果没有，不输出该行
```

```
{{#if (eq pageType "list")}}...{{/if}}
→ 如果 pageType === "list"，输出中间内容；否则不输出
```

#### 5.3 循环展开替换

将 `{{#each 数组}}...{{/each}}` 展开为多行：

```
{{#each fields}}| {{name}} | {{label}} | {{component}} |
{{/each}}
→ 遍历 fieldData.fields 数组，每个元素生成一行：
| projectName | 项目名称 | Input |
| format | 项目业态 | Select |
```

循环内可用 `{{@index}}` 获取序号（从 0 开始）。

#### 5.4 变量替换

将 `{{变量名}}` 替换为入参值：

| 模板占位符 | 替换来源 | 示例 |
|-----------|---------|------|
| `{{pageName}}` | 入参 `pageName` | `设备提资列表页` |
| `{{pagePath}}` | 入参 `pagePath` | `design-manage/equipment-submission` |
| `{{pageType}}` | 入参 `pageType` | `list` |
| `{{pageTypeText}}` | pageType 映射中文 | `列表页`（list→列表页, form→表单页, approval→审批页, detail→详情页, modal→选择弹窗） |
| `{{skillName}}` | pageType 映射 Skill | `/scene-list`（list→/scene-list, form→/scene-form, approval→/scene-approval, detail→/scene-detail, modal→/scene-list） |
| `{{moduleCode}}` | 入参 `moduleCode` | `M1` |
| `{{moduleName}}` | 入参 `moduleName` | `筛选查询区` |
| `{{prdSection}}` | fieldData.prdSection 或入参 | `4.11.5.1.3` |
| `{{prdPath}}` | 入参 `prdPath` | `设计管理/设计方案v2/设备提资.md` |
| `{{refModule}}` | 入参 `refModule` 或 modules.json | `special-review` |
| `{{mermaidDiagram}}` | fieldData.mermaidDiagram | `flowchart TD\n A --> B` |

**循环内的字段级变量**（在 `{{#each fields}}` 内）：

| 占位符 | 来源 | 示例 |
|--------|------|------|
| `{{name}}` | field.name | `projectName` |
| `{{label}}` | field.label | `项目名称` |
| `{{component}}` | field.component | `Input` |
| `{{required}}` | field.required → `✅ 是` / `否` | `✅ 是` |
| `{{dictCode}}` | field.dictCode | `projectType` |
| `{{readOnly}}` | field.readOnly → `✅ 是` / `否` | `否` |
| `{{maxLength}}` | field.maxLength | `128` |
| `{{placeholder}}` | field.placeholder | `请输入项目名称` |
| `{{linkage}}` | field.linkage | `业态变化→显示对应容量字段` |
| `{{interactiveLogic}}` | field.interactiveLogic | 段2 内容 |
| `{{permissionControl}}` | field.permissionControl | 段3 内容 |
| `{{businessRule}}` | field.businessRule | 段4 内容 |
| `{{logicReference}}` | 入参 `logicReference` | `4.3.2 字段交互规则` |

**循环内的列级变量**（在 `{{#each columns}}` 内）：`{{title}}`, `{{dataIndex}}`, `{{width}}`, `{{fixed}}`, `{{sorter}}`, `{{ellipsis}}`, `{{editable}}`, `{{render}}`

**循环内的按钮级变量**（在 `{{#each buttons}}` 内）：`{{status}}`, `{{buttons}}`, `{{api}}`, `{{confirm}}`, `{{action}}`

**循环内的节点权限变量**（在 `{{#each nodePermissions}}` 内）：`{{nodeKey}}`, `{{nodeName}}`, `{{allowAddRow}}`, `{{allowDeleteRow}}`, `{{editableFields}}`, `{{editableFieldsList}}`, `{{readonlyFields}}`

**循环内的联动规则变量**（在 `{{#each linkages}}` 内）：`{{name}}`, `{{triggerField}}`, `{{triggerCondition}}`, `{{affectedFields}}`, `{{action}}`

**对账单派生变量**（由 Step 5 根据 fieldData 自动计算）：
| 占位符 | 来源 | 示例 |
|--------|------|------|
| `{{hasLogicRules}}` | `linkages` 或 `nodePermissions` 非空 → true | `true` |
| `{{apiSourceType}}` | `apiScope.sourceType` | `apifox` / `md` |
| `{{apiSourceRef}}` | `apiScope.sourceRef` | `MCP` / `/path/doc.md` |
| `{{hasApiFieldDiff}}` | 任一字段 `apiFieldDiff` = true → true | `true` |

#### 5.5 替换顺序

1. 先替换 `{{> partial}}`（共享片段）→ 得到完整模板
2. 在完整模板上执行 `{{#if}}` 条件渲染
3. 执行 `{{#each}}` 循环展开
4. 最后替换剩余的 `{{variable}}` 单一变量

**输出**：替换完成后的 Markdown 文档内容

---

### Step 6: 写入文件 — GEN 节点（subagent 执行）

> 由 GEN subagent 在隔离上下文完成（承接 Step 5）。主会话在 JOIN 节点根据 subagent 返回的 `{ok, error}` 更新黑板 `modules[].status`（done/failed）。

**操作**：
1. 确保 `outputPath` 的父目录存在（不存在则创建）
2. 将 Step 5 生成的 Markdown 内容写入 `outputPath`

**输出**：文件写入成功确认（subagent 返回 ok=true）

---

### Step 7: 生成/更新索引文件 — SUMMARY 节点（主会话）

**条件**：如果入参包含 `pages` 字段（或 fieldData.pages 非空）

**操作**：
1. 读取 `templates/_shared/index-template.md` 模板
2. 按页面类型分组，填入页面汇总信息
3. 如果有 `mermaidDiagram`，渲染页面关系图
4. 生成 Skill 速查导航表
5. 写入 `00-索引.md`（与模块文件同目录）

---

### Step 8: 覆盖度检查 — SUMMARY 节点（主会话）

**操作**：
1. 扫描 outputDir 下所有已生成的 `.md` 文件
2. 与 `fieldData.pages`（或设计方案中的页面列表）对比，标记已覆盖/未覆盖
3. **精度规则 #6（铁律）**：检查"特别强调"内容是否在开发方案中体现48755
4. **API 字段匹配覆盖率**（如有 apiDocSource）：
   - 扫描所有字段，计算 `apiFieldName` 非空的百分比
   - 覆盖率 < 80% → 警告，提示用户补充 API 文档或手动确认字段名
5. **Select 数据源完整性**：
   - 扫描所有 Select 组件字段
   - 检查是否有 dictCode 或独立数据源接口（参见 `references/components.json` 的 `api.selectDataSources`）
   - 无数据源 → 在开发方案中标记 `[待确认: 数据源接口未明确]`
6. **接口方法/路径一致性**：
   - 对比 `apiSpec` 提取的接口与设计方案中定义的接口
   - HTTP 方法不一致 → ❌ 不一致，记录到覆盖度报告
   - 路径不一致 → ❌ 不一致，记录到覆盖度报告
7. 使用 `templates/_shared/coverage-report.md` 模板格式，注入实际数据
8. 输出到 `0-coverage-report.md`

**⏸️ CK3 检查点（原检查点3）：暂停确认**

展示覆盖度检查结果：
- 覆盖率百分比
- 未覆盖清单（如有）
- "特别强调"遗漏项（如有）
- API 字段匹配覆盖率 + 未匹配字段列表（如有 apiDocSource）
- Select 数据源缺失字段列表
- 接口不一致项（如有）

**如果覆盖率 < 100%**：列出未覆盖项，询问用户是否补充生成。

---

### Step 9: 自检清单验证 — SUMMARY 节点（主会话）

**操作**：
1. 根据 fieldData 逐项执行 self-check.md 中的 6 项检查
2. 自动填充状态（✅/❌/⚠️）
3. 参考 `references/modules.json` 进行参考模块对比
4. 生成测试用例（基于字段的必填/联动/校验规则）
5. 输出到 `0-self-check-result.md`

---

### Step 10: 输出汇总 — END（主会话）

**操作**：向用户展示生成结果：
- 生成的文件列表及路径
- 覆盖度统计
- 自检结果摘要
- 后续操作建议（如：使用 `/scene-list` 生成代码）

---

## subagent 派发协议

> 主会话在 GEN 节点按本协议派发 subagent，确保上下文隔离与无竞态。

### 派发流程
1. 读 `templates/_shared/gen-subagent-prompt.md` 作为 prompt 基模板
2. 从黑板取该 pending 模块的 `fieldDataSlice`、`templatePath`、`sharedPartials`、`outputFile`，及全局 `designDigest`、`pageName`、`pageType`
3. 注入单花括号槽位（`{moduleCode}` 等 9 个），生成完整 prompt
4. 用 Agent tool 派发 `general-purpose` subagent（每模块一个新 subagent，不跨模块复用）
5. 并发上限 4-6（受 Agent tool 并发约束），剩余 pending 模块排队等待下一轮 ROUTE

### 收集与黑板更新（JOIN）
- subagent 返回 `{moduleCode, outputFile, ok, error}` 结构化结果
- 主会话在 JOIN 节点统一更新黑板（subagent 不写黑板 → 无竞态）：
  - `ok=true` → `modules[].status=done`
  - `ok=false` → `modules[].status=failed`，记 `error`
- 更新 `progress.done/failed` 与 `.blackboard.md`

### 路由判断（ROUTE）
JOIN 更新黑板后，主会话读 `modules[].status` 决定下一步：
- 仍有 `pending` → 回「派发流程」跑下一批（受并发上限约束）
- 全部 `done`/`skipped`（无 `pending`、无 `failed`）→ 进 SUMMARY 节点
- 有 `failed` 但无 `pending` → 不自动重试，先进 SUMMARY，由 CK3 询问是否补生成（确认则回 ROUTE 单跑 `failed`）

### 隔离保证
- 每模块独立 subagent，上下文仅含该模块模板+片段+slice+designDigest
- 主会话不持有任何模块的模板全文 → 主会话上下文不随模块数线性增长

---

## 断点续跑协议

> 黑板落盘即 LangGraph checkpointer。支持中断恢复、补生成、审计。

### signature 计算
`meta.signature = hash(designDocPath + outputPath + canonical(fieldData))`
- `canonical(fieldData)`：对 fieldData JSON 做 key 排序后的稳定序列化
- signature 在 PARSE 一次性写入，不可变

### 启动时判断（PARSE 入口）
1. 检查 `outputDir/.blackboard.json` 是否存在
2. 存在 → 比对 `meta.signature`：
   - **匹配** → 中断恢复：跳过 `done`/`skipped` 模块，直接从 ROUTE 跑 `pending`/`failed` 模块（不重新解析、不重新确认 CK1）
   - **不匹配** → 视为新任务：归档旧黑板（改名 `.blackboard.<时间戳>.archived.json`，时间戳由主会话通过系统命令获取），重建新黑板走完整流程
3. 不存在 → 新任务，正常走 PARSE

### 补生成（CK3 触发）
用户在 CK3 选"补生成" → 不重新解析，直接回 ROUTE，只跑未覆盖/failed 模块

### 审计
`.blackboard.md` 记录每模块 code/name/status/startedAt/finishedAt/error，作为生成过程审计轨迹

### 清理
任务完成且用户确认后，可选清理：删除 `.blackboard.json` 与 `.blackboard.md`（或保留作审计）

---

## 模板路由规则

### 列表页 (list)

| moduleCode | moduleName | 模板文件 |
|------------|------------|----------|
| M1 | 筛选查询区 | templates/list-page/search-fields.md |
| M2 | 主内容表格区 | templates/list-page/table-columns.md |
| M3 | 操作列按钮 | templates/list-page/actions.md |

### 申请表单页 (form)

| moduleCode | moduleName | 模板文件 |
|------------|------------|----------|
| M1 | 基础信息 | templates/form-page/basic-info.md |
| M2 | 设备提资明细 | templates/form-page/equipment-list.md |

### 审批页 (approval)

> **架构约束**：审批页开发方案只输出 `/scene-approval` Skill 需要的业务参数清单（组件名、API、渲染模式等），**不定义代码结构**。审批页代码结构由 `/scene-approval` 的模板控制（两层分离：审批模板页面 + ApprovalForm 组件）。**禁止**在开发方案中出现 Section 组件拆分、自定义 BPM 回调 API 定义。

| moduleCode | moduleName | 模板文件 |
|------------|------------|----------|
| M1 | 审批页参数总览 | templates/approval-page/approval-page.md |

> **说明**：审批页统一生成一份参数文档，不再按模块拆分。所有业务参数（查看/编辑组件、API、渲染模式、节点校验等）合并在一个文档中输出，直接作为 `/scene-approval` 的输入。`moduleCode` 固定为 M1。

### 审批详情页 (detail)

| moduleCode | moduleName | 模板文件 |
|------------|------------|----------|
| M1 | 全量（单据+基础信息+明细+审批记录+按钮） | templates/detail-page/index.md |

> **说明：** 详情页为全量只读页面，所有模块合并在一个文档中生成。

### 选择弹窗 (modal)

| moduleCode | moduleName | 模板文件 |
|------------|------------|----------|
| M1 | 全量（搜索+表格+选择逻辑） | templates/modal-page/select-modal.md |

> **说明：** 弹窗为独立交互模块，搜索条件、表格字段、返回值映射合并在一个文档中生成。

---

## 参考数据来源

> **注意**：以下 JSON 数据为默认参考值，主要适用于设备提资等工程管理模块。其他业务模块使用时，应替换为对应业务的实际数据。

### components.json

```json
{
  "list": {
    "search": {
      "Input": { "import": "ant-design-vue", "defaultProps": { "allowClear": true } },
      "Select": { "import": "ant-design-vue", "defaultProps": { "allowClear": true } },
      "DictSelect": { "import": "@/components/DictSelect", "defaultProps": {} }
    },
    "table": {
      "BasicTable": { "import": "@/components/BasicTable", "defaultProps": { "useSearchForm": true } }
    }
  },
  "form": {
    "basicInfo": {
      "ProjectSelectModal": { "import": "@/components/ProjectSelectModal" },
      "LovSelect": { "import": "@/components/LovSelect", "defaultProps": { "lovCode": "USER_SELECT" } },
      "DictSelect": { "import": "@/components/DictSelect" },
      "Upload": { "import": "@/components/Upload/Upload.vue" }
    }
  }
}
```

### dicts.json

```json
{
  "approvalStatus": {
    "dictCode": "approvalStatus",
    "dictName": "审批状态",
    "items": {
      "DRAFT": "草稿",
      "PROCESSING": "审批中",
      "REJECTED": "审批驳回",
      "COMPLETED": "审批完成",
      "CLOSED": "关闭"
    }
  },
  "projectType": {
    "dictCode": "projectType",
    "dictName": "项目业态",
    "items": {
      "1": "风电",
      "2": "光伏",
      "3": "储能"
    }
  }
}
```

### modules.json

```json
{
  "list": {
    "search": {
      "refModule": "special-review",
      "path": "src/views/eng-manage/special-review",
      "fieldFile": "modules/search-fields.ts",
      "note": "筛选查询区参考：special-review 的搜索表单"
    },
    "table": {
      "refModule": "construction-design-review",
      "path": "src/views/eng-manage/construction-design-review",
      "fieldFile": "modules/table-columns.ts",
      "note": "主内容表格区参考：construction-design-review 的表格列"
    },
    "actions": {
      "refModule": "construction-design-review",
      "path": "src/views/eng-manage/construction-design-review",
      "fieldFile": "modules/action-buttons.ts",
      "note": "操作列按钮参考：construction-design-review 的操作按钮"
    }
  },
  "form": {
    "basicInfo": {
      "refModule": "start-apply",
      "path": "src/views/eng-manage/start-apply",
      "fieldFile": "components/StartApplyForm/useForm.ts",
      "note": "基础信息表单参考：start-apply 的基础信息字段",
      "commonFields": [
        "projectName", "format", "capacityTotal", "capacityWindPower",
        "capacityPv", "capacityPvDc", "energyScale", "storageCapacity",
        "subCode", "regionCode", "developerCode", "obtainDate",
        "expireDate", "lockLevel", "address", "coverArea"
      ]
    },
    "equipmentList": {
      "refModule": "start-apply",
      "path": "src/views/eng-manage/start-apply",
      "fieldFile": "components/EquipmentList/index.tsx",
      "note": "设备明细表格参考：start-apply 的可编辑设备列表",
      "features": [
        "可编辑单元格",
        "行增删",
        "合计行",
        "批量导入"
      ]
    }
  },
  "approval": {
    "unified": {
      "refModule": "start-apply",
      "path": "src/views/office/todo/components/apply-modal/startApplyApproval.tsx",
      "fieldFile": "approval-form/StartApplyApprovalForm.tsx",
      "note": "审批页统一参数模板参考：startApplyApproval 是最完整的参考实现",
      "features": [
        "两层分离（审批模板页面 + ApprovalForm）",
        "provide/inject 权限下发",
        "isRejected 驳回重发",
        "completeTodoApi 标准审批提交",
        "displayMode=embedded 组件复用"
      ]
    }
  },
  "detail": {
    "docInfo": {
      "refModule": "special-review",
      "path": "src/views/office/todo/components/apply-modal/special-review.tsx",
      "fieldFile": "components/DocumentInfoSection/index.tsx",
      "note": "详情页单据信息参考：复用审批页 DocumentInfoSection 组件"
    },
    "basicInfo": {
      "refModule": "construction-design-review",
      "path": "src/views/eng-manage/construction-design-review",
      "fieldFile": "components/BasicInfoSection/index.tsx",
      "note": "详情页基础信息参考：复用 BasicInfoSection editable=false"
    },
    "equipmentReadonly": {
      "refModule": "construction-design-review",
      "path": "src/views/eng-manage/construction-design-review",
      "fieldFile": "components/EquipmentSection/index.tsx",
      "note": "详情页设备明细只读表格参考：全量只读 + 附件预览/下载"
    },
    "approvalRecord": {
      "refModule": "special-review",
      "path": "src/views/office/todo/components/apply-modal/special-review.tsx",
      "fieldFile": "components/ApprovalRecordSection/index.tsx",
      "note": "审批记录表格参考：序号/节点/审批人/动作/时间/意见/附件"
    }
  },
  "modal": {
    "selectProject": {
      "refModule": "start-apply",
      "path": "src/views/eng-manage/start-apply",
      "fieldFile": "components/SelectProjectModal/index.tsx",
      "note": "选择项目弹窗参考：搜索 + 表格 + 单选 + 返回字段映射",
      "commonFeatures": [
        "搜索表单",
        "BasicTable 单选",
        "返回 projectId/projectName/sapProjectCode 等"
      ]
    },
    "selectMaterial": {
      "refModule": "start-apply",
      "path": "src/views/eng-manage/start-apply",
      "fieldFile": "components/SelectMaterialModal/index.tsx",
      "note": "选择规格型号弹窗参考：MDM 数据源 + 搜索 + 表格 + 单选",
      "commonFeatures": [
        "外部数据源搜索",
        "返回 materialCode/specificationModel/equipmentName"
      ]
    }
  },
  "graphifyQueries": {
    "_comment": "推荐的 /graphify query 查询语句",
    "listSearch": "查找 special-review 的搜索表单字段定义",
    "listTable": "查找 construction-design-review 的表格列配置",
    "formBasicInfo": "查找 start-apply 的基础信息表单字段定义",
    "approvalDocInfo": "查找 special-review 审批页的单据信息字段",
    "approvalEquipment": "查找 start-apply 审批页的设备明细 NODE_EDIT_CONFIG",
    "approvalOpinion": "查找 special-review 审批页的审批意见字段"
  }
}
```

---

## 输出文档结构

一次完整的模块生成输出单个文件。多模块组合后的完整文档集：

```
{outputDir}/
├── 0-coverage-report.md          # 覆盖度检查报告（自动生成）
├── 0-self-check-result.md        # 自检清单结果（自动生成）
├── .blackboard.json               # 黑板 state（自动生成，断点续跑用，可清理）
├── .blackboard.md                 # 黑板人类可读进度摘要（自动生成，可清理）
├── 00-索引.md                    # 主索引（自动生成，含页面关系图+Skill导航）
├── 01-列表页-M1-筛选查询区.md    # search-fields 模板
├── 02-列表页-M2-主内容表格区.md   # table-columns 模板
├── 03-列表页-M3-操作列按钮.md     # actions 模板
├── 04-基础信息字段主文档.md        # basic-info 模板
├── 05-申请表单-M2-设备提资明细.md # equipment-list 模板
├── 06-审批页参数总览.md            # approval-page 模板
├── 10-全局接口清单.md             # 手动维护（接口唯一真相源）
├── 11-全局组件清单.md             # 手动维护（组件交叉引用）
├── 12-Skill 使用指引.md           # 手动维护（Skill 命令唯一真相源）
├── 开发自检清单.md                # 手动维护（9模块自检清单）
├── 参考模块对比总表.md            # 手动维护（字段→参考模块映射）
└── 自检自测方案.md                # 手动维护（17 测试用例）
```

### 文件职责

| 文件 | 职责 | 维护方式 |
|------|------|---------|
| 模块文档 (01-09) | 字段级开发方案，含校验规则、4段逻辑 | **Skill 生成** |
| 全局接口清单 (10) | 所有接口定义的唯一真相源 | 手动维护 |
| 全局组件清单 (11) | 组件→使用文档交叉引用 | 手动维护 |
| Skill 使用指引 (12) | Skill 命令/清单唯一真相源 | 手动维护 |
| 质量保障 (自检清单/对比表/自测方案) | 开发自检参考 | 手动维护 |
| 黑板文件 (.blackboard.*) | 状态机 state + 进度审计 | **Skill 生成**（可清理） |

---

## 使用示例

### 示例 1：生成列表页 - 筛选查询区

```bash
/generator-dev-plan pageType=list pageName="设备提资列表页" pagePath="design-manage/equipment-submission" moduleCode="M1" moduleName="筛选查询区" fieldData='{"fields":[{"name":"projectName","label":"项目名称","component":"Input","required":false,"placeholder":"请输入项目名称"}]}' outputPath="设备提资模块详情页 v2/01-列表页-M1-筛选查询区.md"
```

### 示例 2：生成申请表单 - 基础信息

```bash
/generator-dev-plan pageType=form pageName="设备提资申请表单" pagePath="design-manage/equipment-submission" moduleCode="M1" moduleName="基础信息" fieldData='{"fields":[{"name":"projectId","label":"项目名称","component":"ProjectSelectModal","required":true}]}' outputPath="设备提资模块详情页 v2/04-基础信息字段主文档.md"
```

### 示例 3：生成审批页 - 参数总览

```bash
/generator-dev-plan pageType=approval pageName="设备提资审批页" pagePath="design-manage/equipment-submission" moduleCode="M1" moduleName="设备提资" fieldData='{"englishId":"EquipmentFund","approvalRegisterKey":"equipment_fund_submission","viewComponentName":"EquipmentFundDetailModal","editComponentName":"EquipmentFundForm","detailApiFn":"getEquipmentSubmissionDetail"}' outputPath="设备提资模块详情页 v2/06-审批页参数总览.md"
```

---

## 异常处理汇总

| 场景 | 触发条件 | 处理动作 |
|------|---------|---------|
| 设计方案不存在 | `designDocPath` 文件读取失败 | 报错并停止，提示用户检查路径 |
| fieldData JSON 格式错误 | JSON.parse 失败 | 报错并提示具体解析错误位置，让用户修正后重传 |
| outputPath 父目录不存在 | 写入前检查目录 | 自动 `mkdir -p` 创建父目录 |
| pageType 非法 | 不在 {list,form,approval,detail,modal} 中 | 报错并列出合法值 |
| 模板路由不匹配 | pageType + moduleCode 组合无对应模板 | 报错并展示该 pageType 下所有可用 moduleCode |
| 模板文件缺失 | templates/ 下对应文件不存在 | 报错并列出该目录下实际存在的文件 |
| refModule 路径不存在 | 参考模块路径无效 | 警告但不停止，标注"参考模块路径无效，跳过对比" |
| 覆盖率 < 100% | 覆盖度检查发现未覆盖项 | 列出未覆盖清单，提示用户补充生成 |
| 参数缺失 | 必填参数为空且无法从设计方案提取 | 交互式逐一询问 |
| subagent 生成失败 | GEN subagent 返回 ok=false / 超时 | JOIN 标 `failed` 记 error，不阻塞其他模块；CK3 询问重试 → 回 ROUTE 单跑该模块 |
| signature 不匹配 | 重跑时 fieldData/designDocPath 变更 | 归档旧黑板，重建新任务走完整流程 |
| 黑板读写异常 | `.blackboard.json` 损坏/不可写 | 报错停止，提示从 `.blackboard.<时间戳>.archived.json` 恢复或重跑 |

---

## 扩展新页面类型

如需支持新的页面类型：

1. 创建 `templates/{pageType}-page/` 目录
2. 添加模块模板文件（使用 `{{变量}}` 占位符 + `{{#each}}` 循环语法）
3. 在 `references/` 中添加参考数据（如需要）
4. 在本文件的"模板路由规则"中添加新规则
5. 更新 `argument-hint` 中的 pageType 可选值说明
6. 在 Step 5 的 pageTypeText 和 skillName 映射表中添加新条目
