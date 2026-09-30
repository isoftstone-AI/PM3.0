# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

## 表格列配置

| # | 列名 | 字段名 | 组件 | 必填 | 宽度 | 编辑模式 |
|---|------|--------|------|------|------|---------|
{{#each columns}}| {{@index}} | {{title}} | `{{dataIndex}}` | {{#if component}}{{component}}{{else}}文本{{/if}} | {{#if required}}✅{{else}}-{{/if}} | {{#if width}}{{width}}{{else}}auto{{/if}} | {{#if editable}}可编辑{{else}}只读{{/if}} |
{{/each}}

---

## 列详细配置

{{#each columns}}
### 列{{@index}}：{{title}}

| 项 | 值 |
|----|-----|
| **字段名** | `{{dataIndex}}` |
| **组件** | {{#if component}}{{component}}{{else}}纯文本展示{{/if}} |
| **必填** | {{#if required}}✅ 是{{else}}否{{/if}} |
| **可编辑** | {{#if editable}}✅ 是{{else}}否（只读）{{/if}} |
{{#if dictCode}}
| **字典** | `{{dictCode}}` |
{{/if}}
{{#if maxLength}}
| **最大长度** | {{maxLength}} |
{{/if}}
{{#if precision}}
| **精度** | {{precision}} 位小数 |
{{/if}}
{{#if addonAfter}}
| **后缀** | `{{addonAfter}}` |
{{/if}}

{{#if editable}}
**可编辑单元格代码示例：**
```typescript
{
  title: '{{title}}',
  dataIndex: '{{dataIndex}}',
  width: {{#if width}}{{width}}{{else}}150{{/if}},
  customRender: ({ record, index }) => (
    {{#if (eq component "Input")}}
    <Input
      value={record.{{dataIndex}}}
      onChange={(e) => handleCellChange(index, '{{dataIndex}}', e.target.value)}
      maxLength={{{maxLength}}}
    />
    {{/if}}
    {{#if (eq component "InputNumber")}}
    <InputNumber
      value={record.{{dataIndex}}}
      onChange={(val) => handleCellChange(index, '{{dataIndex}}', val)}
      precision={{{{precision}}}}
      addonAfter="{{addonAfter}}"
    />
    {{/if}}
    {{#if (eq component "DictSelect")}}
    <DictSelect
      value={record.{{dataIndex}}}
      onChange={(val) => handleCellChange(index, '{{dataIndex}}', val)}
      dictCode="{{dictCode}}"
    />
    {{/if}}
  ),
}
```
{{/if}}

---
{{/each}}

## 表格操作

| 操作 | 条件 | 行为 |
|------|------|------|
| 新增行 | 默认可用 | 插入空行到底部 |
| 删除行 | 选中行时可用 | 二次确认后删除选中行 |
| 批量导入 | 默认可用 | 打开导入弹窗 |
| 导出模板 | 默认可用 | 下载 Excel 模板 |

## 合计行

| 字段 | 合计方式 | 显示位置 |
|------|---------|---------|
{{#each summaryFields}}| {{name}} | {{method}} | 表格底部 |
{{/each}}

{{> skill-guide }}

---

{{> api-section }}

---

{{> self-check }}

{{> dev-checklist }}

{{> dev-reconciliation }}
