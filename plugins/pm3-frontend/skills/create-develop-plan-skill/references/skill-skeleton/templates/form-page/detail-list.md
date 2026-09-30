# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

## 明细表格配置

| # | 列标题 | dataIndex | 宽度 | 可编辑 | 必填 | 备注 |
|---|--------|-----------|------|--------|------|------|
{{#each detailColumns}}| {{@index}} | {{title}} | `{{dataIndex}}` | {{#if width}}{{width}}{{else}}-{{/if}} | {{#if editable}}✅{{else}}-{{/if}} | {{#if required}}✅{{else}}-{{/if}} | {{#if note}}{{note}}{{else}}-{{/if}} |
{{/each}}

---

## 明细表格功能

| 功能 | 说明 |
|------|------|
| 行增删 | {{#if allowAddDelete}}支持{{else}}不支持{{/if}} |
| 合计行 | {{#if hasSummaryRow}}支持{{else}}不支持{{/if}} |
| 批量导入 | {{#if hasBatchImport}}支持{{else}}不支持{{/if}} |
| 行校验 | {{#if hasRowValidation}}支持{{else}}不支持{{/if}} |

---

## 明细表格详细配置

{{#each detailColumns}}
### 列{{@index}}：{{title}}（{{dataIndex}}）

| 属性 | 值 |
|------|-----|
| title | `{{title}}` |
| dataIndex | `{{dataIndex}}` |
{{#if width}}| width | {{width}} |
{{/if}}{{#if editable}}| editable | true |
{{/if}}{{#if required}}| required | true |
{{/if}}{{#if dictCode}}| dictCode | `{{dictCode}}` |
{{/if}}{{#if customRender}}| customRender | {{customRender}} |
{{/if}}

---
{{/each}}

---

{{> self-check }}

{{> dev-checklist }}
