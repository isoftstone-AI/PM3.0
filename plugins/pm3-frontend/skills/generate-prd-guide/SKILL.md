---
name: generate-prd-guide
description: |
  根据 PRD+ 设计图自动生成前端开发引导文档（v2 架构，设计图驱动）。
  
  触发词：生成开发指南、前端开发文档、根据 PRD 生成、PRD 转开发文档
  
  参数：prdPath designPath moduleName version outputDir apiDocPath(可选)
  示例：/skill:generate-prd-guide prdPath=@prd.md designPath=@design.yaml moduleName=开工管理 version=v1.0 outputDir=@output
  
  v2 特点：设计图驱动、模块级生成、多文件输出、缝隙检测、API 完整定义

arguments: prdPath designPath moduleName version outputDir apiDocPath
argument-hint: <prdPath> <designPath> <moduleName> <version> <outputDir> [apiDocPath]
compatibility: 需要 PRD 文档 (.md) + 设计图文档 (.yaml/.md/.html)
---

# generate-prd-guide (v2)

根据 PRD 文档和设计图文档，自动生成前端开发引导文档。**v2 架构采用设计图驱动**，目标是让开发者拿到文档后**不需要回头看 PRD**，所有细节都在文档里。

## 核心变更（v2 vs v1）

| 维度 | v1 架构 | v2 架构 |
|------|--------|--------|
| 驱动方式 | PRD 驱动 | **设计图驱动** |
| 生成粒度 | 页面维度 | **模块维度** |
| 输出结构 | 单一大文件 | **主索引 + 多个子文件** |
| PRD 链接 | 章节引用 | **每个字段都有 PRD 锚点链接** |
| API 映射 | 可选 | **字段清单中直接标注 API 字段名** |
| 缝隙检测 | 无 | **独立缝隙清单文件** |
| 页面关系图 | 无 | **mermaid 页面跳转关系图** |
| API 详情 | 仅接口名 | **完整参数定义 + TypeScript 类型** |
| 设计图引用 | 行号 | **文件名 + 行号 + 内容片段（格式感知）** |

---

## 参数

| 参数 | 必填 | 说明 |
|-------|------|------|
| `prdPath` | ✅ | PRD 文档路径 |
| `designPath` | ✅ | 设计图文档路径 |
| `moduleName` | ✅ | 模块名称（如：开工管理）|
| `version` | ✅ | 版本号 |
| `outputDir` | ✅ | 输出目录 |
| `apiDocPath` | ❌ | API 设计文档路径，用于生成接口映射 |

参数缺失时交互式询问。

---

## 工作流程（v2 架构）

### 阶段 0：Scanner — 设计图扫描

> 参考 `references/scanner-rules.md` 获取完整解析规则。

**职责**：从设计图出发，建立**模块索引**。

**输入**：
- `designPath`: 设计图文档路径
- `moduleName`: 模块名称

**输出**：`temp/scanner-index.json`

**处理逻辑**：
1. 读取设计图文档，识别格式（HTML/ASCII/YAML/Markdown）
2. 提取页面清单
3. 对每个页面，提取模块列表（筛选区、列表区、表单区等）
4. 对每个模块，提取字段和按钮
5. 对每个页面，提取关联弹窗
6. 模块归一化（将模块名映射到标准类型）
7. 生成 prdKeyword（为每个字段/按钮生成 PRD 搜索关键词）

**输出结构**：
```json
{
  "moduleName": "开工管理",
  "pages": [
    {
      "pageId": "start-apply-list",
      "pageName": "开工申请列表页",
      "modules": [
        {
          "moduleId": "M1",
          "moduleName": "筛选查询区",
          "moduleType": "search",
          "fields": [
            {
              "label": "申请单号",
              "component": "Input",
              "prdKeyword": ["申请单号", "申请单", "单据编号"]
            }
          ],
          "buttons": [{"name": "查询"}]
        }
      ]
    }
  ]
}
```

---

### <HARD-GATE> 阶段 0.5：Validator — 设计图与 PRD 交叉验证

> 参考 `agents/validator.md` 获取完整验证规则。

**职责**：主动比对设计图和 PRD，检测页面、模块、字段的缺失和歧义。

**输入**：
- `scannerIndex`: Scanner 输出的模块索引
- `prdPath`: PRD 文档路径
- `designPath`: 设计图文档路径

**输出**：
- `temp/validation-report.json` — 验证报告（JSON 格式，供后续步骤使用）
- `outputDir/0-validation-report.md` — 用户可读的校验报告（Markdown 格式，**必须输出**）

**验证规则优先级**：

| 优先级 | 规则 | 失败处理 |
|--------|------|---------|
| P0 | V01 页面完整性、V02 模块完整性、V03 字段完整性、V04 按钮完整性 | **终止流程** |
| P1 | V11 一致性、V12 命名一致性、V13 字典完整性、V14 审批流完整性、V15 弹窗完整性 | 记录问题 |
| P2 | V21 字段描述完整性、V22 按钮描述完整性、V23 模块标题规范性 | 提示 |

**处理逻辑**：
1. 从 PRD 中提取页面/模块/字段/按钮清单
2. 与 Scanner 输出进行双向比对（PRD→Design 和 Design→PRD）
3. 执行 P0/P1/P2 三级验证
4. **MUST**：无论 P0 是否通过，都必须生成 `0-validation-report.md` 用户可读报告
5. P0 失败时：
   - 在 `0-validation-report.md` 中清晰列出所有 P0 问题（含位置、PRD 来源、修复建议）
   - **终止后续流程**（不进入 Indexer）
   - 等待用户确认修复或忽略后继续
6. P0 通过时：`0-validation-report.md` 显示"✅ 全部通过"，继续执行

**验证报告结构**：
```json
{
  "validationResult": "passed/failed",
  "summary": { "issuesFound": 5, "p0Issues": 2, "p1Issues": 3 },
  "blockingIssues": [...],
  "issues": [...],
  "prdOnly": { "pages": [], "modules": [], "fields": [] },
  "designOnly": { "pages": [], "modules": [], "fields": [] },
  "consistencyIssues": [...]
}
```

---

### 阶段 1：Indexer — 三源交叉索引

> **前置检查**：确认 `temp/validation-report.json` 存在且 `validationResult` 为 `passed`（或用户已确认忽略 P0 问题）。如未通过 P0 且未获用户确认，**拒绝继续执行**。

> 参考 `references/indexer-rules.md` 获取完整检索规则。

**职责**：将 Scanner 输出的模块索引与 PRD、API 文档进行交叉匹配。

**输入**：
- `scannerIndex`: Scanner 输出的模块索引
- `prdPath`: PRD 文档路径
- `apiDocPath`: API 文档路径（可选）

**输出**：`temp/indexer-enhanced.json`

**核心处理逻辑**：

#### PRD 检索（四轮搜索）

对每个字段依次执行：

| 轮次 | 搜索策略 | 搜索范围 |
|------|---------|---------|
| 第 1 轮 | 字段中文名精确匹配 | PRD 全文 |
| 第 2 轮 | 模糊匹配（去掉后缀） | PRD 全文 |
| 第 3 轮 | prdKeyword + 页面上下文 | 页面对应 PRD 章节 |
| 第 4 轮 | 通用规则检索 | 通用规则章节 |

#### API 检索（如有 apiDocPath）

- 用字段英文名精确匹配 API 字段
- 用字段中文名匹配 API 说明文字
- 用 prdKeyword 匹配 API 参数说明

#### 输出结构

```json
{
  "pages": [
    {
      "pageId": "start-apply-list",
      "prdChapter": "5.1.5.2",
      "prdAnchor": "#5152-开工申请列表",
      "modules": [
        {
          "moduleId": "M1",
          "fields": [
            {
              "label": "申请单号",
              "component": "Input",
              "prd": {
                "fieldName": "applyNo",
                "section": "5.1.5.2",
                "anchor": "#5152-开工申请列表 - 查询条件",
                "rules": {
                  "required": "N",
                  "readonly": "N",
                  "maxLength": 64
                },
                "confidence": "high"
              },
              "api": {
                "apiFieldName": "applyNo",
                "apiType": "String",
                "endpoint": "POST /api/pm3/start-apply/list",
                "confidence": "high"
              }
            }
          ]
        }
      ]
    }
  ],
  "gapAnalysis": {
    "prdUnmatched": [...],
    "apiUnmatched": [...]
  }
}
```

#### 置信度阈值与重试机制

**置信度阈值**：

| 等级 | 条件 | 处理 |
|------|------|------|
| 高（≥80% high） | 大部分字段 confidence = "high" | 直接继续 |
| 中（50%-80%） | 部分 high，部分 low | 提示用户，询问是否继续 |
| 低（<50% high） | 大部分 confidence = "low"/"unmatched" | **自动重试** |

**重试策略**（最多 3 次）：

1. **第 1 次重试**：扩大搜索范围
   - 第 1 轮从"精确匹配"降级为"模糊匹配"
   - 增加同义词扩展

2. **第 2 次重试**：换搜索角度
   - 用页面名称而非字段名搜索
   - 搜索 PRD 的"字段说明"/"补充规则"等非标准章节

3. **第 3 次失败**：降级到 PRD 驱动模式
   - 以 PRD 章节结构为骨架
   - 标注"设计图解析失败，以下字段基于 PRD 推断"
   - 将所有 low/unmatched 字段加入缝隙清单

**SubAgent 上下文管理**：

当 references 文件过长时，按阶段分批加载：
- Scanner 阶段：只加载 `references/scanner-rules.md`
- Validator 阶段：只加载 `agents/validator.md`
- Indexer 阶段：只加载 `references/indexer-rules.md` 的检索策略（§1-5）
- Generator 阶段：只加载 `references/output-templates.md`
- Reconciler 阶段：只加载 `agents/reconciler.md`

---

### 阶段 2：并行 Generator — 模块级生成

各 SubAgent 生成内容时，必须遵循 `references/output-templates.md` 中的模板格式。

#### Generator-Module（页面详情生成器）

> 使用模板：`references/output-templates.md` §1

**职责**：为每个页面生成独立的详情文件 `page-{pageId}.md`。

**核心要求**：
1. **设计图完整嵌入（格式感知）**：每个模块章节必须嵌入完整的设计图内容，不能只给文件链接。嵌入格式根据 `designFormat` 决定：
   - `HTML` → ` ```html ` 代码块
   - `YAML` → ` ```yaml ` 代码块
   - `ASCII/Markdown` → ` ```text ` 代码块
2. **内容提取规则**：
   - 从设计图文档中提取对应模块的内容片段
   - 保持原格式，包括注释、缩进、样式
   - 在片段开头添加注释说明来源文件和行号
3. **模板变量**：
   - `{designSnippet}`：完整的内容片段（通用，替代原 `{designYamlContent}`）
   - `{designFormat}`：设计图格式（HTML/YAML/ASCII/Markdown）
   - `{designFileName}`：设计图文件名
   - `{startLine}` / `{endLine}`：对应行号范围
4. **模块导航 + 页面关系图**：每个 `page-*.md` 必须包含：
   - `## 模块导航`：本页所有模块的锚点跳转表
   - `## 页面关系图`：mermaid 图展示本页与其他页面的跳转关系 + 跳转关系说明表

**输出结构**：
```markdown
# {pageName}

> 返回：[主文档索引](./index.md#页面索引) | PRD 源章节：[章节名]({prdPath}#{prdAnchor})

## 页面概览
| 项 | 值 |
|---|---|
| 页面类型 | {pageType} |
| 路由 | {route} |
| PRD 章节 | [章节名]({prdPath}#{prdAnchor}) |

## 模块 M1：{moduleName}
> 设计图：[{designPath}#L15-L28]({designPath}#L15-L28) | PRD：[{prdPath}#5152]({prdPath}#5152)

### 字段清单
| 字段名 (API) | 中文名 | 组件 | 必填 | 只读 | 精度/格式 | PRD 说明 |
|-------------|-------|------|------|------|----------|---------|
| applyNo | 申请单号 | Input | N | N | 文本 | [PRD]({prdPath}#anchor)：支持模糊搜索 |
```

#### Generator-Dict-Nav

> 使用模板：`references/output-templates.md` §3

**职责**：生成字典速查表和需求导航地图，输出 `1-dict-nav.md`。

#### Generator-Approval

> 使用模板：`references/output-templates.md` §3

**职责**：生成审批流专题，输出 `2-approval-flow.md`（如有审批流）。

#### Generator-Modal

> 使用模板：`references/output-templates.md` §2

**职责**：为每个弹窗生成独立的详情文件 `modal-{modalId}.md`。

---

### <HARD-GATE> 阶段 2.5：Reconciler 产物审查

> 在 Generator 完成后、用户确认前执行。替代原有的简单文件列表确认。

> 参考 `agents/reconciler.md` 获取完整审查规则。

**职责**：对 Generator 输出的所有 `page-*.md` / `modal-*.md` / `index.md` 进行机械式完整性审查。

**输入**：
- `scanner-index.json`（对账基准）
- `indexer-enhanced.json`（PRD/API 索引）
- `validation-report.json`（已知问题）
- 所有 `page-*.md` / `modal-*.md` / `index.md`

**输出**：
- `temp/reconciler-report.json` — 机器可读审查报告
- 控制台摘要

**4 层 15 项审查规则**：

| 层级 | 规则 | 检查内容 | 级别 |
|------|------|---------|------|
| 文件级 | R01-R03 | 文件存在性（page/modal/index） | BLOCK/WARN |
| 模块级 | R04-R07 | 模块覆盖率 + 数量匹配 + **模块导航** + **页面关系图** | BLOCK/WARN |
| 字段级 | R08-R09 | 字段名匹配（防乱码）+ PRD 链接覆盖 | BLOCK/WARN |
| 内容级 | R10-R15 | API 路径 + 表格列数 + 特别强调 + **index.md 专属**（mermaid/快速导航/API概览） | WARN |

**决策逻辑**：
- BLOCK > 0 → 暂停，等待修复/查看/强制继续
- 仅 WARN → 建议修复，确认后继续
- 全部通过 → 直接进入 Assembler

---

### 阶段 3：Assembler — 组装 + 缝隙检测

> 参考 `agents/assembler.md` 获取完整组装规则。

**职责**：合并所有生成的文档片段，输出完整文档集。

**输入**：
- `enhancedIndex`: Indexer 输出的增强索引
- `generatedFiles`: 所有 Generator 生成的子文件路径
- `outputDir`: 输出目录
- `validationReport`: `temp/validation-report.json`（来自阶段 0.5）

**输出**：
- `0-validation-report.md` — **用户可读校验报告（排序第一，必须输出）**
- `index.md` — 主索引文件
- `1-dict-nav.md` — 字典速查表 + 需求导航
- `2-approval-flow.md` — 审批流专题（如有）
- `page-*.md` — 页面详情（每页一个）
- `modal-*.md` — 弹窗详情（每弹窗一个）
- `9-gap-analysis.md` — 信息缝隙清单

**组装步骤**：
1. 生成所有页面/弹窗子文件
2. 生成 `index.md` 主索引
3. **生成 `0-validation-report.md`**：将 `validationReport` 转换为用户可读的 Markdown 表格（含摘要、P0/P1/P2 问题清单、缝隙清单）
4. 生成 `9-gap-analysis.md`（合并缝隙检测 + validationReport 中的 consistencyIssues）

**缝隙检测逻辑**：
- 扫描所有 `prd.confidence = "low"` 或 `"unmatched"` 的字段 → PRD 未明确
- 扫描所有 `api = null` 的字段 → API 未定义
- 扫描同一字段在不同章节的矛盾描述 → PRD 矛盾

---

## 输出文档结构（v2）

```
{outputDir}/
├── 0-validation-report.md      # 校验报告（用户可读，排序第一，必须输出）
├── index.md                    # 主索引文件（页面关系图 + 快速导航 + API 概览）
├── 1-dict-nav.md               # 字典速查表 + 需求导航
├── 2-approval-flow.md          # 审批流专题（如有）
├── page-start-apply-list.md    # 列表页详情（含接口定义）
├── page-start-apply-form.md    # 表单页详情（含接口定义）
├── page-start-apply-detail.md  # 详情页详情
├── page-start-apply-approval.md # 审批页详情
├── modal-delete-confirm.md     # 删除确认弹窗
├── modal-select-project.md     # 选择项目弹窗
└── 9-gap-analysis.md           # 信息缝隙清单
```

---

## 输出文档特点

### 1. 主索引文件轻薄但完整

- 页面关系图（mermaid）展示页面跳转关系
- 快速导航索引所有页面/弹窗
- API 接口概览（含完整参数和 TypeScript 类型定义）
- 字典/审批流/缝隙清单摘要

### 2. 设计图完整嵌入（v1.1 新增）

**修订前**：每个模块只给出设计图文件链接和行号（如 `机会管理 - 列表.yaml#L20-L68`）

**修订后**：每个模块章节**嵌入完整的设计图内容**，实现「文档即设计图」：

```markdown
## 模块 M1：筛选查询区

> PRD：[4.1.2.1.1](...) | 设计图来源：`机会管理 - 列表.yaml`

### 设计图结构（完整内容）

```yaml
# 筛选查询区 - 设计图完整内容
- type: search-form
  props:
    layout: inline
  items:
    - name: 申请单号
      type: input
      width: 200
    # ... 完整字段列表
  actions:
    - label: 查询
      type: button
```

### 字段清单
...
```

**HTML 格式示例**：

```markdown
### 设计图结构（完整内容）

```html
<!-- 搜索筛选区 -->
<div class="search-area">
  <div class="search-item">
    <label>国家</label>
    <select>...</select>
  </div>
</div>
```
```

**优势**：
- ✅ 开发者无需跳转到设计图文件
- ✅ 字段定义、样式、选项一目了然
- ✅ 阅读体验流畅，开发效率提升 100%

### 2. 子文件独立

每个页面/弹窗独立成文，开发者只需看自己负责的部分。

### 3. PRD 锚点直达

每个字段都有 `[PRD]()` 链接，一键跳转到源文档对应章节。

### 4. 模块粒度清晰

每个模块独立成节，边界清晰，不混淆。

### 5. 缝隙清单独立

所有未明确的信息集中管理，方便与产品确认。

### 6. 设计图引用精确

每个模块标注设计图文件名 + 行号范围，复杂模块嵌入 YAML 片段。

---

## 注意事项

- 审批流使用 MindWord 格式，页面跳转使用 Mermaid 格式
- 弹窗必须包含完整的来源描述，方便追踪调用链
- 字段精度描述必须与附录一致，不一致时在「特别强调」中标注
- 所有外部链接使用相对路径
- 按钮名称必须与 PRD 原文一致
- API 类型定义必须与后端确认一致

---

## v2 架构优势

| 优势 | 说明 |
|------|------|
| **减少遗漏** | 从设计图出发，先识别"有什么"，再找 PRD 说明，避免跳过设计图中有但 PRD 未明确的内容 |
| **快速定位** | 每个字段都有 PRD 锚点链接，无需全文搜索 |
| **模块清晰** | 按模块组织输出，符合开发者阅读习惯 |
| **缝隙可追踪** | 独立的缝隙清单文件，方便与产品确认 |
| **文件轻量化** | 多文件结构，每个文件只关注一个页面/弹窗，阅读和编辑都更方便 |
| **API 完整** | 含完整参数定义和 TypeScript 类型，前端可直接使用 |
| **页面关系可视化** | mermaid 图展示页面跳转关系，新人快速上手 |
| **设计图可追溯** | 文件名 + 行号 + 内容片段（支持 HTML/YAML/ASCII/Markdown），精确定位设计图位置 |
