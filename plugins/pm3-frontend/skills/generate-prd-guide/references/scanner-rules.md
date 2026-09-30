# Scanner 规则 — 设计图解析规范

> 本文件供 Scanner SubAgent 使用，包含设计图格式识别、模块提取、字段提取的完整规则。

---

## 1. 设计图格式识别

### 1.1 格式检测顺序

```
1. 检查文件扩展名 .html/.htm 或内容包含 <!DOCTYPE html> 或 <html
   → 是：HTML 格式（优先级最高，因 HTML 可能含 ASCII/YAML-like 文本）
   → 否：继续

2. 检查是否包含 ASCII 框图特征字符（─│┌┐└┘├┤┬┴┼）
   → 是：ASCII 格式
   → 否：继续

3. 检查是否包含 YAML 特征（开头为 page: 或 modules:）
   → 是：YAML 格式
   → 否：继续

4. 默认为 Markdown 表格格式
```

### 1.2 ASCII 格式特征

```
┌─────────────────────────────────────────────────────────────┐
│ 【模块 1：页面标题栏】                                        │
│ 标题：开工申请                                               │
└─────────────────────────────────────────────────────────────┘
```

**解析规则**：
- 模块名称：提取 `【模块 X：xxx】` 中的 xxx
- 字段：识别 `标签：值` 或 `标签：□□□` 格式
- 按钮：识别 `┌───┐` 框内的文字

### 1.3 YAML 格式特征

```yaml
page: 开工申请列表页
type: list
route: /engineering/start-apply/list
modules:
  - name: 筛选查询区
    type: search
    fields:
      - label: 项目名称
        component: Input
```

**解析规则**：
- 直接解析 YAML 结构
- 缺失字段根据 context 推断

### 1.4 Markdown 表格格式特征

```markdown
## 开工申请列表页

### 模块：筛选查询区

| 字段名 | 组件类型 | 必填 |
|--------|----------|------|
| 项目名称 | Input | N |
```

**解析规则**：
- 页面名称：`##` 标题
- 模块名称：`###` 标题
- 字段：解析表格行

### 1.5 HTML 格式特征

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head><title>项目复审管理 - 列表页</title></head>
<body>
  <!-- 搜索筛选区 -->
  <div class="search-area">
    <div class="search-item">
      <label>国家</label>
      <select>...</select>
    </div>
  </div>
  <!-- 数据表格 -->
  <table class="data-table">...</table>
</body>
</html>
```

**解析规则**：

1. **页面识别**：
   - 每个 `.html` 文件 = 一个页面（跳过 `index.html`、`_style.css` 等非页面文件）
   - 页面名称：`<title>` 标签内容（去掉模块名前缀，如 `"项目复审管理 - 列表页"` → `"列表页"`）

2. **模块边界**：
   - 优先级1：HTML 注释 `<!-- xxx -->` → 模块名（如 `<!-- 搜索筛选区 -->` → `搜索筛选区`）
   - 优先级2：CSS 类名映射（见下表）
   - 优先级3：语义化标签（`<section>`、`<header>`、`<main>`）
   - 模块结束：下一个同级注释 / CSS 类块 / 关闭 `</div>` + 同级开始

   | CSS 类名 | 模块类型 |
   |---------|---------|
   | `.search-area`、`.search-item`、`.filter-area` | search |
   | `.data-table`、`.table-area`、`.list-area` | table |
   | `.form-grid`、`.form-area`、`.form-item` | form |
   | `.detail-area`、`.info-area`、`.display-area` | display |
   | `.attachment-area`、`.file-upload`、`.upload-area` | attachment |
   | `.approval-area`、`.approval-info` | approval |
   | `.search-buttons`、`.toolbar`、`.action-area` | action |
   | `.pagination` | table（分页，合并到 table 模块） |

3. **字段提取**：
   - 字段名：`<label>` 标签文本内容
   - 组件推断：`<input type="text">` → Input，`<select>` → Select，`<textarea>` → TextArea，`<input type="date">` → DatePicker
   - 必填标识：`<label class="required">` 或 `label` 含 `*` 号
   - 只读标识：`<input readonly>` 或 `readonly` 属性
   - 单位后缀：`.with-unit` 类或 `<span class="unit">` → 提取单位文本
   - 禁用状态：`<button class="btn-link disabled">` → 记录条件

4. **按钮提取**：
   - 按钮名：`<button>` 标签文本内容
   - 按钮样式：`.btn-primary` → 主按钮，`.btn-default` → 默认按钮，`.btn-link` → 链接按钮
   - 禁用状态：`.disabled` 类 → 记录为条件禁用按钮
   - 链接按钮：`<a class="text-orange">` → 可点击链接（如 SAP 编号跳转）

5. **表格列提取**：
   - `<th>` 标签文本 = 列名
   - `<td>` 中 `.btn-link` = 操作列按钮
   - `<td>` 中 `.status-dot` + 文本 = 状态列（解析状态值）
   - `<td>` 中 `<a class="text-orange">` = 可点击链接列

---

## 2. 模块提取规则

### 2.1 模块识别关键词

| 模块类型 | 识别关键词 |
|---------|-----------|
| search | 筛选、查询、搜索、条件区 |
| action | 按钮区、操作区、功能键、功能按钮 |
| table | 列表、表格、数据区、数据列表 |
| form | 基础信息、表单、信息录入、填报区 |
| display | 展示区、详情区、只读区、信息展示 |
| attachment | 附件、文件上传、材料区 |
| approval | 审批意见、审批信息、审批区 |

### 2.2 模块边界判定

**ASCII 格式**：
- 模块开始：`┌─` 且包含 `【模块`
- 模块结束：`└─` 且下一个 `┌─` 之前

**YAML/Markdown 格式**：
- 模块开始：`- name:` 或 `### 模块：`
- 模块结束：下一个同级标题或列表项

**HTML 格式**：
- 模块开始：`<!-- 注释 -->`（优先）或特定 CSS 类名的 `<div>` 开始标签
- 模块结束：下一个同级 `<!-- 注释 -->` 或同级 `<div>` 开始之前
- 特殊规则：`.search-area` + `.search-buttons` 合并为一个 search 模块；`.data-table` + `.pagination` 合并为一个 table 模块

### 2.3 模块归一化

将设计图中的模块名映射到标准类型：

| 设计图原名 | 归一化类型 |
|-----------|-----------|
| 筛选区、查询区、搜索区、筛选查询区、条件区 | search |
| 按钮区、操作区、功能键区、功能按钮区、工具栏 | action |
| 列表区、表格区、数据区、数据列表区、表格组件 | table |
| 基础信息区、表单区、信息录入区、填报区、表单组件 | form |
| 详情区、展示区、只读区、信息展示区、查看区 | display |
| 附件区、文件上传区、材料区、上传区 | attachment |
| 审批意见区、审批信息区、审批区 | approval |

---

## 3. 字段提取规则

### 3.1 字段识别

**ASCII 格式**：
```
项目名称：□□□  项目业态：□□□
```
- 字段名：`：` 前的文字
- 组件推断：`□□□` → Input，`□□▼` → Select，`□□□-□□□` → DateRange

**YAML/Markdown 格式**：
- 直接从表格或 YAML 中提取

### 3.2 组件类型推断

| 设计图特征 | 推断组件 |
|-----------|---------|
| □□□、输入框、文本框 | Input |
| □□▼、下拉、选择器 | Select |
| □□□-□□□、日期范围 | DateRange |
| 📅、日期选择器 | DatePicker |
| 多行、文本域、备注 | TextArea |
| 表格列、列 | TableColumn |
| □、复选框 | Checkbox |
| ○、单选框 | Radio |
| ☐、开关 | Switch |

### 3.3 prdKeyword 生成规则

对每个字段生成搜索关键词：

```
1. 基础词 = 字段中文名
2. 去掉通用后缀：["名称", "编号", "号", "ID", "码", "日期", "时间", "类型", "状态"]
3. 添加同义词（常见映射）：
   - 项目 → 工程
   - 单号 → 编号
   - 状态 → 审批状态
4. 输出数组
```

**示例**：
```
"申请单号" → ["申请单号", "申请单", "单据编号", "单号"]
"项目名称" → ["项目名称", "项目", "工程名称"]
"审批状态" → ["审批状态", "状态", "单据状态"]
```

---

## 4. 按钮提取规则

### 4.1 按钮识别

**ASCII 格式**：
```
┌────────┐
│ 查询   │
└────────┘
```
- 按钮名：框内文字

**YAML/Markdown 格式**：
- 直接从 `buttons:` 列表提取

### 4.2 按钮 prdKeyword 生成

```
1. 基础词 = 按钮名称
2. 添加上下文词：
   - 列表页按钮 → ["按钮", "操作"]
   - 表单页按钮 → ["按钮", "提交", "保存"]
3. 输出数组
```

**示例**：
```
"查询" → ["查询", "查询按钮", "搜索"]
"删除" → ["删除", "删除按钮", "删除操作"]
```

---

## 5. 弹窗识别规则

### 5.1 弹窗特征

| 弹窗类型 | 设计图特征 |
|---------|-----------|
| confirm | 确认弹窗、提示框、dialog |
| select | 选择弹窗、Lov、列表选择 |
| display | 展示弹窗、详情弹窗、查看 |

### 5.2 触发关系提取

```
页面：开工申请列表页
  按钮：删除
    → 弹窗：删除确认弹窗
```

提取：
- `triggerPage`: 页面名称
- `triggerButton`: 按钮名称
- `modalName`: 弹窗名称
- `modalType`: confirm/select/display

---

## 6. 设计图位置标注规则

### 6.1 行号计算

```
1. 读取设计图文档
2. 对每个页面/模块/字段，记录起始行号和结束行号
3. 输出格式：#L 起始行 - 结束行
```

### 6.2 锚点生成

```
行号范围 → #L12-L58
页面锚点 → #page-start-apply-list
模块锚点 → #M1、#M2
```

### 6.3 设计图文件名提取（新增）

```
1. 检测设计图输入类型：
   - 单个 YAML 文件 → 直接使用该文件名
   - 单个 Markdown 文件 → 使用该文件名
   - 目录 → 按页面提取对应的文件名

2. 输出格式：
   - designFileName: "设备提资申请表单页.yaml"
   - designLocation: "#L44-L201"
   - 组合引用：[设计图](设备提资申请表单页.yaml#L44-L201)
```

### 6.4 设计图片段提取（格式感知）

对每个模块，提取设计图内容片段用于文档嵌入：

```
1. 定位模块在设计图文件中的行号范围
2. 读取该范围内的内容
3. 根据 designFormat 决定输出格式：
   - HTML 格式 → 输出原始 HTML 片段，代码块标记为 ```html
   - YAML 格式 → 输出原始 YAML 片段，代码块标记为 ```yaml
   - ASCII/Markdown 格式 → 输出原始文本片段，代码块标记为 ```text
4. 输出 designSnippet 字段（通用字段名）
5. 保留 yamlSnippet 作为向后兼容别名（值与 designSnippet 相同）
```

**输出格式**：
```json
{
  "moduleId": "M1",
  "moduleName": "基础信息区",
  "designFileName": "设备提资申请表单页.yaml",
  "designLocation": "#L44-L201",
  "designFormat": "YAML",
  "designSnippet": "sections:\n  - name: \"basicInfo\"\n    title: \"基础信息\"\n    fields: [...]",
  "yamlSnippet": "sections:\n  - name: \"basicInfo\"\n    title: \"基础信息\"\n    fields: [...]"
}
```

**HTML 格式示例**：
```json
{
  "moduleId": "M1",
  "moduleName": "搜索筛选区",
  "designFileName": "01-list.html",
  "designLocation": "#L20-L42",
  "designFormat": "HTML",
  "designSnippet": "<!-- 搜索筛选区 -->\n<div class=\"search-area\">\n  <div class=\"search-item\">\n    <label>国家</label>\n    <select>...</select>\n  </div>\n</div>",
  "yamlSnippet": "<!-- 搜索筛选区 -->\n<div class=\"search-area\">\n  ..."
}
```

---

## 7. 特殊情况处理

### 7.1 模块嵌套

设计图中可能出现模块嵌套：
```
【模块 4：基础信息区】
  【子模块 4.1：项目信息】
  【子模块 4.2：申请人信息】
```

处理规则：
- 扁平化嵌套，将子模块视为独立模块
- moduleId 使用 `M4-1`、`M4-2` 格式

### 7.2 字段分组

设计图中字段可能有分组：
```
【基础信息】
  项目名称、项目业态
【经济信息】
  总投资、装机容量
```

处理规则：
- 将分组视为子模块
- 字段归属到对应子模块

### 7.3 动态字段

设计图中标注"按业态动态显示"的字段：
- 在字段对象中添加 `dynamic: true`
- 记录显示条件（如 `format=3 时显示`）

---

## 8. 质量检查清单

Scanner 输出前确认：
- [ ] 设计图格式已正确识别
- [ ] 所有页面都已提取
- [ ] 所有模块都已提取
- [ ] 模块类型映射正确
- [ ] 字段 label 与设计图一致
- [ ] 组件类型推断合理
- [ ] prdKeyword 已生成
- [ ] 按钮 name 与设计图原文一致
- [ ] 弹窗已提取并关联到触发页面
- [ ] designLocation 格式正确（#L 起始行 - 结束行）
- [ ] designSnippet 已提取（HTML 格式为 HTML 片段，其他格式为 YAML/文本片段）
- [ ] designFormat 已正确设置（HTML/YAML/ASCII/Markdown）
- [ ] 嵌套模块已扁平化
- [ ] 动态字段已标记
