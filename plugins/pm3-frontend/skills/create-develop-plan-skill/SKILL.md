---
name: create-develop-plan-skill
description: |
  为新项目从零搭建「开发方案生成器 Skill」（generator-dev-plan）。
  当用户提到以下意图时触发：
  - "创建开发方案 skill"、"搭建 generator-dev-plan"、"生成开发方案生成器"
  - "为新项目创建 skill"、"从零搭建开发方案 skill"
  - "create develop plan skill"、"create generator-dev-plan"
  - "我有一个新项目，需要生成开发方案的 skill"
  - "帮我搭建一个能生成字段级开发方案的 skill"

  也适用于：用户已有 CLAUDE.md/AGENTS.md，想基于项目规范自动生成配套的开发方案生成器。

arguments: |
  必填：无（交互式收集）
  可选：skillName, claudeMdPath, pageTypes, dicts, modules, templateStyle, outputPath

argument-hint: |
  [skillName="generator-dev-plan"] [claudeMdPath="CLAUDE.md路径"] [pageTypes="list,form,approval"] [outputPath="输出目录"]
  所有参数均可选，未提供时交互式询问。
---

# 开发方案生成器 Skill 创建器

> **版本：** v1.0
> **用途：** 根据项目的 CLAUDE.md/AGENTS.md 规范，自动生成配套的「开发方案生成器 Skill」
> **定位：** 元 Skill（生成 Skill 的 Skill）

## 核心原理

```
CLAUDE.md / AGENTS.md（项目规范 DNA）
        ↓ 自动提取
┌───────────────────────────────┐
│  技术栈 → SKILL.md 技术栈描述   │
│  组件表 → components.json      │
│  字段表 → field-reference.md   │
│  规则   → self-check.md        │
│  目录结构 → 模板路径规范        │
└───────────────────────────────┘
        ↓ 组合
  完整的 generator-dev-plan skill
```

**为什么必须依赖 CLAUDE.md/AGENTS.md？**
- 开发方案生成器需要知道项目用什么组件、什么技术栈、什么规范
- 这些信息已经存在于 CLAUDE.md/AGENTS.md 中，不应让用户重复提供
- 两者相辅相成：CLAUDE.md 定义规范，generator-dev-plan 按规范生成方案

---

## 执行流程

### Step 0: 参数预检

**操作**：检查用户是否提供了参数

| 参数 | 处理 |
|------|------|
| `skillName` | 未提供 → 询问 |
| `claudeMdPath` | 未提供 → 询问（**必填，无法跳过**） |
| `pageTypes` | 未提供 → Step 2 询问 |
| `outputPath` | 未提供 → 默认 `~/.claude/skills/{skillName}/` |

**询问 skillName 时**：
> "请提供新 skill 的名称（默认：`generator-dev-plan`）"

**询问 claudeMdPath 时**：
> "请提供项目的 CLAUDE.md 或 AGENTS.md 文件路径。该文件是项目规范的核心，包含技术栈、组件库、目录结构等必要信息。"

---

### Step 1: 读取并校验 CLAUDE.md

> **这是最关键的步骤。** CLAUDE.md 的质量直接决定生成 skill 的质量。

#### 1.1 读取文件

读取 `claudeMdPath` 指定的文件。

**异常处理**：
- 文件不存在 → 报错停止，提示用户检查路径
- 文件为空 → 报错停止

#### 1.2 结构化校验

按照 `references/claude-md-schema.json` 中定义的规则校验文件结构。

**校验规则**（读取 `references/claude-md-schema.json` 获取完整规则）：

| 级别 | 章节 | 权重 | 缺失处理 |
|------|------|------|---------|
| **必填** | 技术栈定义 | 30分 | ❌ 必须补充 |
| **必填** | 组件库清单 | 30分 | ❌ 必须补充 |
| **必填** | 目录结构规范 | 30分 | ❌ 必须补充 |
| 建议 | 常用字段表 | 10分 | ⚠️ 可后续补充 |
| 建议 | 隐含规则/禁止项 | 10分 | ⚠️ 可后续补充 |
| 建议 | 场景→Skill映射 | 10分 | ⚠️ 可后续补充 |

**评分规则**：
- ≥ 90 分：✅ 完全可用，直接进入 Step 2
- 60-89 分：⚠️ 部分缺失，需补充必填项后继续
- < 60 分：❌ 严重缺失，建议用户先完善 CLAUDE.md

#### 1.3 提取关键信息

从 CLAUDE.md 中提取以下数据（提取规则见 `references/extract-rules.md`）：

```yaml
提取结果:
  techStack:
    framework: "Vue 3"        # 从技术栈章节提取
    language: "TypeScript"
    uiLib: "Ant Design Vue 4"
    buildTool: "Vite"
    styleScheme: "Tailwind CSS + CSS Module + Less"

  components:                  # 从组件表提取
    - name: "BasicTable"
      import: "@/components/BasicTable"
      usage: "表格"
    - name: "DictSelect"
      import: "@/components/DictSelect"
      usage: "字典选择"
    # ...

  fieldReference:               # 从字段表提取（如有）
    - name: "proName"
      label: "项目名称"
      component: "Input"
      required: true

  rules:                       # 从隐含规则提取（如有）
    - rule: "Modal 显隐使用 open prop"
      correct: "open"
      wrong: "visible"

  directoryStructure:           # 从目录结构章节提取（框架无关）
    pagePattern: "从 CLAUDE.md 提取的页面文件模式"
    apiPattern: "从 CLAUDE.md 提取的 API 文件模式"
    componentPattern: "从 CLAUDE.md 提取的组件目录模式"
    stylePattern: "从 CLAUDE.md 提取的样式文件模式（如有）"
    basePaths: "从 CLAUDE.md 提取的源码根目录"
```

#### 1.4 输出校验报告

向用户展示提取结果：

```
📋 CLAUDE.md 校验报告

✅ 技术栈：{从 CLAUDE.md 提取的技术栈}
✅ 组件库：已提取 N 个组件
✅ 目录结构：{从 CLAUDE.md 提取的页面文件模式}
⚠️ 常用字段表：未找到（可选，不影响生成）
⚠️ 隐含规则：已提取 N 条

校验得分：X/120 分
状态：✅ 可以继续 / ⚠️ 部分缺失 / ❌ 严重缺失
```

**⏸️ 检查点 1：CLAUDE.md 校验确认**

- **得分 ≥ 90**：直接继续 Step 2
- **得分 60-89**：列出缺失项，询问用户「是否继续？缺失项将使用默认值」
- **得分 < 60**：停止，提示用户先完善 CLAUDE.md，给出具体补充建议

---

### Step 2: 收集页面类型配置

**操作**：确认需要支持的页面类型

> "需要支持哪些页面类型？"

选项（多选）：
1. 列表页（搜索 + 表格 + 分页）
2. 表单页（新增/编辑表单）
3. 审批页（审批参数配置）
4. 详情页（只读详情展示）
5. 选择弹窗（搜索 + 表格 + 单选）
6. 自定义（请描述）

**每种页面类型的模块划分**：

| pageType | 默认模块划分 | 模板文件 |
|----------|------------|---------|
| `list` | M1: 筛选查询区 / M2: 表格区 / M3: 操作按钮 | search-fields / table-columns / actions |
| `form` | M1: 基础信息 / M2: 明细列表 | basic-info / detail-list |
| `approval` | M1: 审批参数总览 | approval-params |
| `detail` | M1: 全量详情 | index |
| `modal` | M1: 搜索+选择 | select-modal |

用户可自定义模块划分，覆盖默认值。

---

### Step 3: 收集可选配置

#### 3.1 字典配置

> "是否有业务字典需要预配置？"
> 选项：[有，我来提供] [没有] [从 CLAUDE.md 提取] [稍后配置]

如果用户选择提供，接受 JSON 格式：
```json
{
  "approvalStatus": {
    "dictCode": "approvalStatus",
    "items": { "DRAFT": "草稿", "PROCESSING": "审批中" }
  }
}
```

#### 3.2 参考模块

> "是否有参考模块（优秀实现）？提供模块路径，生成器会用它做对比参考。"
> 选项：[有，我来提供] [没有] [稍后配置]

如果用户选择提供，接受 JSON 格式：
```json
{
  "list": {
    "search": { "refModule": "example-module", "path": "{{pageBasePath}}/example-module" }
  }
}
```

#### 3.3 模板详细程度

> "模板详细程度？"
> 选项：[简洁版（仅字段表）] [标准版（字段+逻辑+自检）] [详细版（完整参考）]

默认：标准版

---

### Step 4: 参数完整性终检

**最终检查清单**：

| 条件 | 来源 | 状态 |
|------|------|------|
| `skillName` | 用户/默认 | ☐ |
| `claudeMdPath` + 校验通过 | 用户 | ☐ |
| `techStack` | CLAUDE.md 提取 | ☐ |
| `components` | CLAUDE.md 提取 | ☐ |
| `pageTypes` | 用户确认 | ☐ |
| `outputPath` | 用户/默认 | ☐ |
| `dicts` | 可选 | ☐ |
| `modules` | 可选 | ☐ |

**全部必填项完成 → 进入 Step 5**
**仍有缺失 → 回到对应步骤补充**

---

### Step 4.5: 产物预览

> **⏸️ 检查点 2：生成前预览确认**

在正式生成文件前，向用户展示以下预览信息：

```
📋 生成预览

📁 输出目录：{outputPath}/
📄 将生成文件：
  - SKILL.md（约 {预估行数} 行）
  - templates/_shared/（10 个共享片段）
  - templates/list-page/（3 个模板）
  - references/components.json（{组件数} 个组件，{分类数} 个分类）
  - .skill-meta.json

🔧 技术栈：{techStack}
📦 页面类型：{pageTypes}
🧩 组件分类预览（前 5 个）：
  - table: BasicTable, ...
  - select: DictSelect, OrgSelect, ...
  - input: Input, ...
```

**用户确认后 → 进入 Step 5**
**用户要求调整 → 回到对应步骤修改配置**

---

### Step 5: 生成 Skill

> **核心步骤**：基于提取的数据和骨架模板，生成完整的 generator-dev-plan skill。

#### 5.1 生成目录结构

```
{outputPath}/
├── SKILL.md
├── templates/
│   ├── _shared/
│   │   ├── nav-links.md
│   │   ├── page-intro.md
│   │   ├── field-detail.md
│   │   ├── skill-guide.md
│   │   ├── self-check.md
│   │   ├── dev-checklist.md
│   │   ├── coverage-report.md
│   │   ├── design-style.md
│   │   ├── rule-reference.md
│   │   └── index-template.md
│   ├── list-page/          ← 仅当 pageTypes 包含 list
│   ├── form-page/          ← 仅当 pageTypes 包含 form
│   ├── approval-page/      ← 仅当 pageTypes 包含 approval
│   ├── detail-page/        ← 仅当 pageTypes 包含 detail
│   └── modal-page/         ← 仅当 pageTypes 包含 modal
└── references/
    ├── components.json
    ├── dicts.json
    └── modules.json
```

#### 5.2 生成 SKILL.md

**数据来源映射**：

| SKILL.md 章节 | 数据来源 |
|--------------|---------|
| `name` | `skillName` |
| `description` | 基于 `techStack` + `pageTypes` 生成 |
| 技术栈说明 | `techStack` |
| 支持的页面类型表 | `pageTypes` 配置 |
| 输入参数定义 | 固定模板 + `pageTypes` 动态生成 |
| 执行流程（Step 1-10） | 骨架模板 |
| 模板路由规则 | `pageTypes` + 模块划分 |
| 参考数据来源 | `components` + `dicts` + `modules` |

**SKILL.md 生成规则**：
1. 读取 `references/skill-skeleton/SKILL.md` 作为骨架
2. 替换 `{{techStack}}` → 从 CLAUDE.md 提取的技术栈（如 `Vue 3 + TypeScript + Ant Design Vue 4 + Vite`）
3. 替换 `{{pageTypeTable}}` → 根据 pageTypes 动态生成页面类型表，格式示例：

   ```
   | pageType | 描述 | 模块划分 |
   |----------|------|---------|
   | `list` | 列表页（搜索+表格+分页） | M1: 筛选查询区 / M2: 表格区 / M3: 操作按钮 |
   | `form` | 表单页（新增/编辑） | M1: 基础信息 / M2: 明细列表 |
   ```

4. 替换 `{{templateRoutes}}` → 根据 pageTypes + 模块划分生成路由规则，格式示例：

   ```
   ### 列表页 (list)
   | moduleCode | moduleName | 模板文件 |
   |------------|------------|----------|
   | M1 | 筛选查询区 | templates/list-page/search-fields.md |
   ```

5. 替换 `{{componentCount}}` → 组件数量（如 `28`）
6. 替换 `{{skillName}}` → skill 名称（如 `generator-dev-plan`）
7. 替换 `{{pageTypeOptions}}` → pageType 枚举值（如 `list|form|approval|detail|modal`）
8. 替换 `{{dictCount}}` → 字典数量（如 `3`）
9. 替换 `{{moduleCount}}` → 参考模块数量（如 `2`）

#### 5.3 生成 templates/

**共享片段**（`_shared/`）：
- 从 `references/skill-skeleton/templates/_shared/` 复制骨架
- 替换通用占位符（skillName、techStack 等）
- `self-check.md` 中注入从 CLAUDE.md 提取的规则
- `rule-reference.md` 中注入项目特定规则

**页面模板**（`{type}-page/`）：
- 仅生成 `pageTypes` 中包含的类型
- 从骨架模板复制，替换占位符
- 每种类型的模块划分按 Step 2 确认的配置

#### 5.4 生成 references/

| 文件 | 生成方式 |
|------|---------|
| `components.json` | 从 CLAUDE.md 组件表转换，按功能分类 |
| `dicts.json` | 用户提供的字典 + CLAUDE.md 提取的字典 |
| `modules.json` | 用户提供的参考模块 |

**components.json 转换规则**：

从 CLAUDE.md 的组件表：
```
| BasicTable | @/components/BasicTable | 表格 |
```

转换为分类结构：
```json
{
  "table": {
    "BasicTable": {
      "component": "BasicTable",
      "import": "@/components/BasicTable",
      "defaultProps": { "useSearchForm": true },
      "note": "表格（强制使用）"
    }
  }
}
```

**分类规则**（两阶段匹配）：

1. **框架特定匹配**（优先）：如果 CLAUDE.md 提取的 framework 匹配 `claude-md-schema.json` 中的 `framework_overrides`，使用框架特定映射。例如 Vue 项目中 `DictSelect` → `select` 类。
2. **通用关键词匹配**（兜底）：按组件名关键词匹配通用分类规则：

   | 分类 | 匹配关键词 |
   |------|-----------|
   | `table` | Table, DataGrid, DataTable, Grid |
   | `select` | Select, Dropdown, Combobox, Picker, TreeSelect, Cascader |
   | `input` | Input, Text, Number, TextArea, Editor |
   | `date` | Date, Time, Calendar, Range, Period |
   | `upload` | Upload, File, Attachment, Dropzone |
   | `display` | Title, Heading, Loading, Export, Badge, Tag |
   | `layout` | Layout, Card, Panel, Modal, Dialog, Drawer |
   | `navigation` | Menu, Breadcrumb, Pagination, Steps |
   | `feedback` | Alert, Message, Notification, Toast, Progress |
   | `special` | Chart, Map, Timeline, Tree, Drag |

3. **未匹配**：归入 `special` 类

**处理大量组件**：如果 CLAUDE.md 提取的组件数 > 30，按分类分组输出，每个分类最多展示前 10 个，其余折叠为 `_more: [...]`。

#### 5.5 产物模板变量填充规则

> 产物模板（`templates/_shared/` 下的文件）使用 `{{变量名}}` 占位符。以下定义每个变量的来源和填充逻辑。

**从 CLAUDE.md 直接提取的变量**：

| 变量名 | 使用位置 | 来源 | 填充逻辑 |
|--------|---------|------|---------|
| `{{pageBasePath}}` | page-intro.md | CLAUDE.md 目录结构章节 | 提取源码根目录（如 `src/views/`、`pages/`、`app/`）。未找到则默认 `src/` |
| `{{fileExtension}}` | page-intro.md | CLAUDE.md 技术栈 + 目录结构 | 从目录结构中的文件扩展名提取（如 `.tsx`、`.vue`、`.jsx`、`.py`、`.java`）。未找到则默认 `.ts` |
| `{{styleExtension}}` | page-intro.md | CLAUDE.md 样式方案 | 从技术栈的样式方案提取（如 `less`、`scss`、`css`、`module.css`）。未找到则默认 `less` |

**从 CLAUDE.md 场景映射合成的变量**：

| 变量名 | 使用位置 | 来源 | 填充逻辑 |
|--------|---------|------|---------|
| `{{sceneMappings}}` | page-intro.md, rule-reference.md | CLAUDE.md 场景→Skill 映射 | 提取场景映射表格，转为数组：`[{scene, skill, pageType}]` |
| `{{sceneSkillList}}` | skill-guide.md | CLAUDE.md 场景→Skill 映射 | 与 `sceneMappings` 同源，但结构不同：`[{pageTypeText, skillCommand, postGenNotes}]` |

**sceneSkillList 填充示例**：

假设 CLAUDE.md 场景映射为：
```
| 列表页 | /my-list-skill |
| 表单页 | /my-form-skill |
```

填充结果：
```json
[
  { "pageTypeText": "列表页", "skillCommand": "/my-list-skill", "postGenNotes": ["根据项目实际情况调整"] },
  { "pageTypeText": "表单页", "skillCommand": "/my-form-skill", "postGenNotes": ["根据项目实际情况调整"] }
]
```

**directoryStructure 变量**（page-intro.md 条件渲染）：

如果 CLAUDE.md 目录结构章节有明确的文件列表，填充为结构化数组：
```json
[
  { "type": "页面", "files": [
    { "type": "页面入口", "path": "src/views/example/index.tsx" },
    { "type": "页面逻辑", "path": "src/views/example/useIndex.ts" }
  ]}
]
```

如果 CLAUDE.md 只有模式描述（如 "index.tsx + useIndex.ts 分离"），则使用默认的 `{{else}}` 分支动态生成。

#### 5.5 生成 .skill-meta.json

记录生成元数据，便于后续更新：

```json
{
  "skillName": "generator-dev-plan",
  "version": "1.0.0",
  "createdAt": "2024-01-15T10:00:00Z",
  "source": {
    "claudeMdPath": "CLAUDE.md",
    "claudeMdHash": "sha256:abc123...",
    "validationScore": 100
  },
  "extractedData": {
    "techStack": { "framework": "Vue 3", "language": "TypeScript", "uiLib": "Ant Design Vue 4" },
    "componentCount": 28,
    "fieldCount": 15,
    "ruleCount": 12
  },
  "config": {
    "pageTypes": ["list", "form", "approval", "detail", "modal"],
    "templateStyle": "standard"
  }
}
```

---

### Step 6: 验证 + 交付

#### 6.1 文件完整性检查

| 文件 | 必须存在 |
|------|---------|
| `SKILL.md` | ✅ |
| `templates/_shared/` (10 files) | ✅ |
| `templates/{type}-page/` (按 pageTypes) | ✅ |
| `references/components.json` | ✅ |
| `.skill-meta.json` | ✅ |

#### 6.2 内容一致性检查

- SKILL.md 中的技术栈 ≈ CLAUDE.md 技术栈
- components.json 组件数 = CLAUDE.md 提取的组件数
- 模板中引用的组件名存在于 components.json

#### 6.3 输出生成报告

```
✅ Skill 生成完成！

📁 生成目录：{outputPath}/
├── SKILL.md                    ✓ 已生成
├── .skill-meta.json            ✓ 已生成
├── templates/
│   ├── _shared/ (10 files)     ✓ 已生成
│   ├── list-page/ (3 files)    ✓ 已生成
│   ├── form-page/ (2 files)    ✓ 已生成
│   └── approval-page/ (1 file) ✓ 已生成
└── references/
    ├── components.json         ✓ 已生成（28 个组件）
    ├── dicts.json              ✓ 已生成（3 个字典）
    └── modules.json            ✓ 已生成（2 个参考模块）

📋 使用方式：
/{skillName} designDocPath="设计方案.md" outputPath="输出.md" pageType=list

⚠️ 后续可配置：
- 补充更多字典到 references/dicts.json
- 添加参考模块到 references/modules.json
- 调整模板详细程度
```

---

## 异常处理汇总

| 场景 | 触发条件 | 处理方式 |
|------|---------|---------|
| CLAUDE.md 不存在 | 文件路径错误 | 报错停止，提示检查路径 |
| CLAUDE.md 非 Markdown 格式 | 文件内容无 `#` 或 `##` 标题层级 | 报错停止，提示 CLAUDE.md 必须使用 Markdown 格式编写 |
| CLAUDE.md 校验不通过 | 必填章节缺失 | 列出缺失项，指导补充 |
| 组件表为空 | 无组件库清单 | 必须补充，否则无法生成 |
| 组件表格式不标准 | 不是 `| 名称 | 路径 | 用途 |` 格式 | 宽松解析（容忍多余空格、缺失分隔行），解析失败则提示格式化 |
| outputPath 已存在文件 | 目录下已有同名 SKILL.md | 询问：覆盖/重命名/取消 |
| outputPath 已存在目录 | 目录下已有完整 skill 结构 | 询问：覆盖/合并/取消 |
| pageTypes 为空 | 未选择任何类型 | 至少需要 1 种 |
| JSON 格式错误 | dicts/modules 参数 | 报错 + 提供正确格式示例 |
| 生成产物超过预期大小 | SKILL.md > 500 行 | 告警，建议精简模板或减少 pageTypes |
| CLAUDE.md 中无场景映射 | 缺少「场景→Skill 映射」章节 | 使用通用默认值，在生成报告中标注「建议补充场景映射」 |

---

## 参考文件

| 文件 | 用途 | 何时读取 | 文件性质 |
|------|------|---------|---------|
| `references/claude-md-schema.json` | CLAUDE.md 校验规则定义 | Step 1.2 | **配置**（定义校验规则和分类规则） |
| `references/extract-rules.md` | 从 CLAUDE.md 提取数据的规则 | Step 1.3 | **配置**（定义提取策略和输出格式） |
| `references/skill-skeleton/SKILL.md` | 生成产物的 SKILL.md 骨架 | Step 5.2 | **产物骨架**（占位符模板，替换后成为产物主文件） |
| `references/skill-skeleton/templates/` | 生成产物的页面模板 | Step 5.3 | **产物模板**（占位符模板，复制到产物目录） |
| `references/skill-skeleton/templates/_shared/` | 共享片段模板 | Step 5.3 | **产物模板**（被页面模板引用的公共片段） |
| `references/skill-skeleton/references/` | 参考数据骨架 | Step 5.4 | **产物骨架**（JSON 结构模板，填充后成为产物参考数据） |

> **职责说明**：
> - **配置文件**（`claude-md-schema.json`、`extract-rules.md`）：定义"如何读取和校验 CLAUDE.md"，不参与产物生成
> - **产物骨架**（`skill-skeleton/SKILL.md`、`skill-skeleton/references/*.json`）：占位符模板，替换变量后直接成为产物的一部分
> - **产物模板**（`skill-skeleton/templates/**`）：占位符模板，复制到产物目录后成为产物的一部分
