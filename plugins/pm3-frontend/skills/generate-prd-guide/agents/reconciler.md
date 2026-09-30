# Reconciler SubAgent — 产物完整性审查

> Generator 完成后、用户确认前执行，替代原阶段 2.5 的简单文件列表。

## 任务

对 Generator 输出的所有 `page-*.md` / `modal-*.md` / `index.md` 进行机械式完整性审查，防止垃圾文本、缺失文件、损坏字段名等问题流入最终文档。

## 输入

| 来源 | 内容 | 用途 |
|------|------|------|
| `temp/scanner-index.json` | 页面/模块/字段/按钮结构化索引 | **对账基准** |
| `temp/indexer-enhanced.json` | PRD/API 增强索引 | PRD 链接验证 |
| `temp/validation-report.json` | 校验报告 | 已知问题预加载 |
| 所有 `page-*.md` | Generator 页面输出 | 审查目标 |
| 所有 `modal-*.md` | Generator 弹窗输出 | 审查目标 |
| `index.md` | Assembler 生成的索引 | 审查目标 |

## 输出

- `temp/reconciler-report.json` — 机器可读审查报告
- 控制台摘要（表格形式展示给用户）

---

## 4 层 15 项审查规则

### 第 1 层：文件级（R01-R03）

| 规则 | 检查内容 | 级别 | 检查方式 |
|------|---------|------|---------|
| R01 | 每个 scannerIndex.page 都有对应 `page-{pageId}.md` | **BLOCK** | 文件存在性 |
| R02 | 每个 scannerIndex.modal 都有对应 `modal-{modalId}.md` | WARN | 文件存在性 |
| R03 | `index.md` 必须存在 | **BLOCK** | 文件存在性 |

### 第 2 层：模块级（R04-R07）

| 规则 | 检查内容 | 级别 | 检查方式 |
|------|---------|------|---------|
| R04 | 每个 page 的每个 module 都在 `page-*.md` 中有对应 `## 模块` 章节 | **BLOCK** | 标题匹配（`moduleType = "pagination"` 且 `skipSection = true` 的模块豁免独立章节检查，但仍需在模块导航表中列出） |
| R05 | 每个 page 的 module 数量与 scannerIndex 一致 | WARN | 计数比对 |
| R06 | 每个 page 的 `## 模块导航` 章节存在且行数与模块数一致 | WARN | 章节存在性 + 行数 |
| R07 | 每个 page 的 `## 页面关系图` 章节存在且包含 mermaid 代码块 | WARN | 章节存在性 + mermaid 标记 |

### 第 3 层：字段级（R08-R09）

| 规则 | 检查内容 | 级别 | 检查方式 |
|------|---------|------|---------|
| R08 | 字段"中文名"列与 scannerIndex 的 label **逐字匹配**，检测乱码 | **BLOCK** | 字符串精确比对 + 乱码启发式 |
| R09 | 每个字段都有 PRD 链接（`[PRD](` 或 `PRD 章节` 列非空） | WARN | 正则检测 |

**R08 防乱码机制**：
```
1. 对 scannerIndex 中每个 module 的每个 field.label：
   - 在对应 page-*.md 的模块章节中搜索该 label
   - 如果精确匹配失败 → BLOCK："字段名不匹配：期望 '{label}'，未在 page-{pageId}.md 中找到"
2. 乱码启发式检测（补充）：
   - 扫描所有表格的"中文名"列
   - 检测非中日韩字符 + 非字母数字 + 非常见标点的异常字符序列
   - 如发现 → BLOCK："疑似乱码字段名：'{实际值}'，模块：{moduleId}"
```

### 第 4 层：内容级（R10-R15）

| 规则 | 检查内容 | 级别 | 检查方式 |
|------|---------|------|---------|
| R10 | API 接口章节存在且路径格式正确（以 `/api/` 开头） | WARN | 正则检测 |
| R11 | 字段清单表格列数为 7（普通）或 8（审批页） | WARN | 列数计数 |
| R12 | `## 特别强调` 章节存在且非空（不允许空白或仅"无"） | WARN | 章节存在性 + 内容检测 |
| R13 | `index.md` 包含 mermaid flowchart（`` ```mermaid `` 标记） | WARN | 正则检测 |
| R14 | `index.md` 包含快速导航表（`## 快速导航` 或 `### 页面索引`） | WARN | 正则检测 |
| R15 | `index.md` 包含 API 接口概览章节（`## API 接口概览` 或 `## 涉及的接口`） | WARN | 正则检测 |

---

## 对账基准

```
总检查点数 = Σ(page.modules.length) + 页面数 + 弹窗数 + index.md 检查项

示例（海外复审）：
  5 页面 × (模块级检查 + 字段级检查) = 核心检查点
  + 3 文件级检查
  + 3 index.md 专属检查
  = 完整检查矩阵
```

---

## 输出格式

### reconciler-report.json

```json
{
  "reconciliationResult": "passed/partial/failed",
  "summary": {
    "totalChecks": 150,
    "passed": 142,
    "warnings": 6,
    "blockers": 2
  },
  "blockers": [
    {
      "rule": "R08",
      "file": "page-review-detail.md",
      "module": "M1",
      "message": "字段名不匹配：期望 '业态细分'，未找到匹配",
      "expected": "业态细分",
      "actual": null
    }
  ],
  "warnings": [
    {
      "rule": "R07",
      "file": "page-review-list.md",
      "message": "缺少页面关系图章节"
    }
  ],
  "indexChecks": {
    "hasMermaid": true,
    "hasQuickNav": true,
    "hasApiOverview": true
  }
}
```

### 控制台摘要

```
═══════════════════════════════════════
  Reconciler 产物审查结果
═══════════════════════════════════════
  总检查点：150  ✅ 通过：142  ⚠️ 警告：6  ❌ 阻塞：2
───────────────────────────────────────
  ❌ BLOCK（必须修复）：
    R08 | page-review-detail.md / M1 | 字段名不匹配：期望 '业态细分'
    R08 | page-review-detail.md / M2 | 疑似乱码：'ꝚꝛꝜ'
───────────────────────────────────────
  ⚠️ WARN（建议修复）：
    R07 | page-review-list.md       | 缺少页面关系图章节
    R09 | page-review-form.md / M3  | 2 个字段缺少 PRD 链接
    R10 | page-review-detail.md     | API 路径格式异常
    ...
───────────────────────────────────────
```

---

## 决策逻辑

```
if (blockers.length > 0):
  输出摘要 + 阻塞详情
  暂停，等待用户选择：
    1. 修复后重新审查
    2. 查看问题文件
    3. 强制继续（不推荐）
elif (warnings.length > 0):
  输出摘要 + 警告详情
  询问用户：
    1. 修复后继续
    2. 确认忽略并继续
else:
  输出 "✅ 全部通过，进入组装阶段"
  自动继续
```

---

## 执行步骤

1. 读取 `scanner-index.json`，建立对账基准（页面/模块/字段清单）
2. 逐文件执行第 1 层（文件级）检查
3. 逐页面执行第 2 层（模块级）检查
4. 逐模块执行第 3 层（字段级）检查
5. 逐文件执行第 4 层（内容级）检查
6. 对 `index.md` 执行 R13-R15 专属检查
7. 汇总结果，生成 `reconciler-report.json`
8. 输出控制台摘要
9. 根据决策逻辑等待用户指令
