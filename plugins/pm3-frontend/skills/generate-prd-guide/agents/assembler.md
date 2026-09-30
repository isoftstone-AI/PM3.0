# Assembler SubAgent — 文档组装器

> 输出模板见 `references/output-templates.md` §3

## 任务

合并所有生成的文档片段，输出完整文档集。

## 输入

- `enhancedIndex`: Indexer 输出（`temp/indexer-enhanced.json`）
- `generatedFiles`: 所有 Generator 生成的子文件路径列表
- `outputDir`: 输出目录
- `moduleName`: 模块名称
- `version`: 版本号
- `prdPath`: PRD 文档路径
- `designPath`: 设计图文档路径
- `validationReport`: `temp/validation-report.json`

## 输出

| 文件 | 说明 | 排序 |
|------|------|------|
| `0-validation-report.md` | 校验报告 | 1（排序第一） |
| `index.md` | 主索引 | 2 |
| `1-dict-nav.md` | 字典速查表 + 需求导航 | 3 |
| `2-approval-flow.md` | 审批流专题（如有） | 4 |
| `page-{pageId}.md` | 页面详情 | 每页一个 |
| `modal-{modalId}.md` | 弹窗详情 | 每弹窗一个 |
| `9-gap-analysis.md` | 信息缝隙清单 | 最后 |

## 组装步骤

### Step 1：生成 `index.md`

**包含章节**（详见 `references/output-templates.md` §3）：

1. **项目目录结构**：基于设计图路径推断 moduleKebab/pageKebab，生成标准目录树
2. **路由配置表**：仅列出有独立路由的页面
3. **页面关系图**：基于 `pageRelations` 生成 mermaid flowchart
4. **快速导航**：按页面类型排序的表格（列表页 > 表单页 > 审批页 > 详情页）
5. **API 接口概览**：从 `apiDetails.endpoints` 提取完整接口信息
6. **字典速查表（摘要）**：列出所有字典编码和字典项
7. **审批流专题（摘要）**：如有审批流，生成 MindWord 格式
8. **信息缝隙清单（摘要）**：列出所有未明确信息
9. **业务流程说明**：从 `businessRules` 提取背景 + 校验规则

**目录结构生成规则**：
- `moduleKebab`：从设计图路径推断，无法推断时用 `moduleName` 转 kebab-case
- `pageKebab`：从列表页 pageName 提取核心业务名词
- 组件名 PascalCase：Form → `{名词}Form`，Detail → `{名词}DetailModal`，Section → `{区块名}Section`

### Step 2：生成 `0-validation-report.md`

将 `validation-report.json` 转换为用户可读的 Markdown：

```markdown
# {moduleName} - 设计图与 PRD 交叉验证报告

## 验证摘要

| 项 | 结果 |
|---|---|
| 验证结果 | ✅ 通过 / ❌ 失败 |
| 发现问题 | {N} 个 |
| P0 阻塞 | {N} 个 |
| P1 记录 | {N} 个 |

## P0 阻塞问题（必须修复）
| 问题 | 位置 | 修复建议 |
...

## P1 记录问题（不影响流程）
...
```

### Step 3：生成 `1-dict-nav.md`

从 enhancedIndex 中提取所有字典字段，生成速查表：

```markdown
# 字典速查表 + 需求导航

## 字典速查表

| 字典编码 | 字典名称 | 字典项 |
|----------|----------|--------|
| project_format | 项目业态 | 风电/光伏/储能 |

## 需求导航地图

### 按页面 → 模块 → 字段的三级索引
...
```

### Step 4：生成 `2-approval-flow.md`（如有）

从 enhancedIndex 中提取审批流信息，生成 MindWord 格式的审批流程图。

**触发条件**：`enhancedIndex.pages` 中存在 `pageType = "approval"` 的页面。

### Step 5：组装缝隙清单 `9-gap-analysis.md`

合并以下来源：
- `gapAnalysis.prdUnmatched`：PRD 未明确字段
- `gapAnalysis.apiUnmatched`：API 未定义字段
- `validationReport.consistencyIssues`：一致性矛盾
- `validationReport.designOnly`：设计图多余内容
- `validationReport.prdOnly`：PRD 多余内容

**分类**：

| 类型 | 说明 |
|------|------|
| PRD 未明确 | prd.confidence = low/unmatched |
| API 未定义 | api = null/unmatched |
| PRD 矛盾 | 同一字段多章节描述不一致 |
| 设计图与 PRD 不一致 | 设计图描述 ≠ PRD 描述 |
| 缺失数据源 | Select 字段无字典/接口 |

### Step 6：检查点

组装完成后，执行质量检查（见下方清单）。

## 质量检查清单

- [ ] 所有 Generator 生成的子文件都已包含在输出中
- [ ] index.md 包含完整的页面索引和弹窗索引
- [ ] 页面关系图与弹窗引用一致
- [ ] API 接口概览完整（如有 API 文档）
- [ ] 字典速查表覆盖所有字典字段
- [ ] 审批流专题（如有）已生成
- [ ] 0-validation-report.md 已生成（排序第一）
- [ ] 9-gap-analysis.md 缝隙清单完整
- [ ] 所有文件使用相对路径链接
- [ ] 校验报告中的 P0 问题已全部解决或用户已确认忽略
