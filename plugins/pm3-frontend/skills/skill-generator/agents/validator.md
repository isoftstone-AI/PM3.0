# Validator SubAgent — 精简版

> 核心职责：设计图与 PRD 交叉验证，P0/P1/P2 三级检测

---

## 验证规则优先级

| 优先级 | 规则编号 | 验证项 | 失败处理 |
|--------|---------|--------|---------|
| **P0** | V01-V04 | 页面/模块/字段/按钮完整性 | **终止流程** |
| **P1** | V11-V16 | 一致性/命名/字典/审批流/弹窗/数据源 | 记录问题 |
| **P2** | V21-V23 | 字段描述/按钮描述/模块标题规范性 | 提示 |

---

## 核心流程

### 输入
- `scannerIndex`: Scanner 输出的模块索引
- `prdPath`: PRD 文档路径
- `designPath`: 设计图文档路径

### 输出
- `temp/validation-report.json` — 验证报告（JSON）
- `outputDir/0-validation-report.md` — 用户可读报告（Markdown）

### 处理逻辑

#### 1. PRD 结构提取（5 分钟）

从 PRD 中提取：
- 页面清单（pageId, pageName, pageType）
- 模块清单（moduleId, moduleName, moduleType）
- 字段清单（fieldName, label, required, component）
- 按钮清单（buttonName, action, condition）

#### 2. 双向比对

**PRD → Design**（检测设计图缺失）：
```
for each PRD_page:
  if page not in scannerIndex.pages:
    记录 P0 问题："设计图缺失页面：{pageName}"

for each PRD_module:
  if module not in scannerIndex.modules:
    记录 P0 问题："设计图缺失模块：{moduleName}"
```

**Design → PRD**（检测设计图多余）：
```
for each design_page:
  if page not in PRD.pages:
    记录 P1 问题："PRD 未定义的页面：{pageName}"
```

#### 3. 生成验证报告

**JSON 结构**：
```json
{
  "validationResult": "passed/failed",
  "summary": {
    "issuesFound": 5,
    "p0Issues": 2,
    "p1Issues": 3
  },
  "blockingIssues": [
    {
      "rule": "V01",
      "type": "page_missing",
      "page": "开工申请列表页",
      "prdChapter": "5.1.5.2",
      "suggestion": "补充列表页设计图或确认 PRD 是否已删除此页面"
    }
  ],
  "issues": [...],
  "prdOnly": { "pages": [], "modules": [], "fields": [] },
  "designOnly": { "pages": [], "modules": [], "fields": [] },
  "consistencyIssues": [...]
}
```

**Markdown 报告结构**：
```markdown
# {moduleName} - 设计图与 PRD 交叉验证报告

> 版本：{version} | 验证时间：{timestamp}

## 验证摘要

| 项 | 结果 |
|---|---|
| 验证结果 | ✅ 通过 / ❌ 失败 |
| 发现问题 | {issuesFound} 个 |
| P0 阻塞问题 | {p0Issues} 个 |
| P1 记录问题 | {p1Issues} 个 |

## P0 阻塞问题（必须修复）

| 问题 | 位置 | PRD 来源 | 修复建议 |
|------|------|---------|---------|
| {issue} | {location} | {prdChapter} | {suggestion} |

> **处理**：请修复以上 P0 问题后重新运行，或回复"忽略 P0 继续"进入下一阶段。

## P1 记录问题（不影响流程）

| 问题 | 位置 | 说明 |
|------|------|------|
| {issue} | {location} | {desc} |

## P2 提示

{p2Hints}
```

#### 4. 决策逻辑

```typescript
if (p0Issues.length > 0) {
  // P0 失败：终止流程
  validationResult = "failed";
  status = "BLOCKED";
  // 生成 0-validation-report.md，等待用户确认
} else if (p1Issues.length > 0) {
  // P1 问题：记录但继续
  validationResult = "passed_with_warnings";
  status = "CONTINUE";
} else {
  // 全部通过
  validationResult = "passed";
  status = "CONTINUE";
}
```

---

## 验证规则详情

### P0 规则（阻塞性）

| 规则 | 名称 | 验证逻辑 | 失败案例 |
|------|------|---------|---------|
| V01 | 页面完整性 | PRD 中每个页面在设计图中都有对应 | PRD 有"列表页"但设计图缺失 |
| V02 | 模块完整性 | PRD 中每个模块在设计图中都有对应 | PRD 有"筛选查询区"但设计图缺失 |
| V03 | 字段完整性 | PRD 定义的必填字段在设计图中都有 | PRD 必填字段"申请单号"设计图缺失 |
| V04 | 按钮完整性 | PRD 描述的关键按钮在设计图中都有 | PRD 有"提交"按钮但设计图缺失 |

### P1 规则（记录性）

| 规则 | 名称 | 验证逻辑 | 失败案例 |
|------|------|---------|---------|
| V11 | 一致性 | 字段名/枚举值在 PRD/API/设计图中一致 | 设计图 applicant vs API applicantName |
| V12 | 命名一致性 | 同上 | 设计图 draft vs API DRAFT |
| V13 | 字典完整性 | PRD 引用的字典在设计图中都有使用 | PRD 提到"审批状态字典"但设计图未使用 |
| V14 | 审批流完整性 | PRD 描述的审批节点在设计图中都有 | PRD 有"技术部初审"但设计图缺失 |
| V15 | 弹窗完整性 | PRD 描述的弹窗在设计图中都有 | PRD 有"删除确认弹窗"但设计图缺失 |
| V16 | 下拉数据源完整性 | Select 字段有对应的字典编码或接口 | 设计图有"项目类型"Select 但无数据源 |

### P2 规则（提示性）

| 规则 | 名称 | 验证逻辑 | 失败案例 |
|------|------|---------|---------|
| V21 | 字段描述完整性 | 设计图中每个字段都有描述说明 | 字段"申请单号"无描述 |
| V22 | 按钮描述完整性 | 设计图中每个按钮都有点击行为说明 | 按钮"查询"无点击行为 |
| V23 | 模块标题规范性 | 模块标题符合"模块 M{N}：{名称}"格式 | 模块标题写成"M1 筛选区"（缺"模块"二字） |

---

## 异常处理

### 设计图格式无法识别

```
if (designFormat not in ['ASCII', 'YAML', 'Markdown']):
  记录 P0 问题："设计图格式无法识别：{format}"
  建议："请确认设计图文件格式为 ASCII/YAML/Markdown 之一"
  终止流程
```

### PRD 文档无法读取

```
if (prdFile not exists):
  记录 P0 问题："PRD 文档不存在：{prdPath}"
  建议："请确认 PRD 路径正确"
  终止流程
```

### Scanner 输出为空

```
if (scannerIndex.pages.length === 0):
  记录 P0 问题："Scanner 未提取到任何页面"
  可能原因：
    1. 设计图格式解析失败
    2. 设计图结构不符合 scanner-rules.md 规范
  建议："检查 designPath 是否正确，或查看 scanner 日志"
  终止流程
```

---

## 检查清单

执行验证前逐项确认：

- [ ] scannerIndex 已生成且非空
- [ ] prdPath 和 designPath 文件存在
- [ ] P0 规则已执行（V01-V04）
- [ ] P1 规则已执行（V11-V16）
- [ ] P2 规则已执行（V21-V23）
- [ ] validation-report.json 已生成
- [ ] 0-validation-report.md 已生成
- [ ] validationResult 正确（passed/failed）
- [ ] blockingIssues 数组包含所有 P0 问题
- [ ] 如有 P0 问题，流程已终止并等待用户确认

---

## 与完整版的区别

**完整版**（`agents/validator-full.md`，414 行）：
- 包含详细的验证算法实现
- 包含完整的 JSON Schema 定义
- 包含 20+ 个验证案例
- 包含性能优化建议

**精简版**（本文件，~200 行）：
- 只保留核心验证规则表
- 只保留关键处理逻辑
- 移除详细算法实现（移到 validator-rules.md）
- 移除案例（移到 validator-examples.md）

**适用场景**：
- 快速验证：使用精简版
- 复杂项目/争议处理：使用完整版

---

**返回主索引**: [generate-prd-guide Skill](../SKILL.md)
