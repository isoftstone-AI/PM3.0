# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

## 列配置总览

| # | 列名 | 字段名 | 宽度 | 固定 | 排序 | 渲染 |
|---|------|--------|------|------|------|------|
{{#each columns}}| {{@index}} | {{title}} | `{{dataIndex}}` | {{#if width}}{{width}}{{else}}auto{{/if}} | {{#if fixed}}✅ {{fixed}}{{else}}-{{/if}} | {{#if sorter}}✅{{else}}-{{/if}} | {{#if render}}自定义{{else}}文本{{/if}} |
{{/each}}

---

## 列详细配置

> **注意：** 以下为 Skill 模板参数，由 `/scene-list` skill 决定最终 columns 代码结构。
> **禁止在 columns 中使用 `ellipsis: true`**，改用合适宽度。

{{#each columns}}
### 列{{@index}}：{{title}}

| 属性 | 值 |
|------|-----|
| title | `{{title}}` |
| dataIndex | `{{dataIndex}}` |
| width | {{#if width}}{{width}}{{else}}150{{/if}} |
{{#if fixed}}| fixed | `{{fixed}}` |
{{/if}}{{#if sorter}}| sorter | `true` |
{{/if}}{{#if dictCode}}| dictCode | `{{dictCode}}` |
{{/if}}{{#if tagColors}}| Tag 颜色 | {{tagColors}} |
{{/if}}{{#if render}}| customRender 说明 | {{render}} |
{{/if}}{{#if editable}}| 可编辑 | ✅ 是 |
{{/if}}

---
{{/each}}

## 分页配置

| 项 | 值 |
|----|-----|
| **默认页大小** | {{#if pageSize}}{{pageSize}}{{else}}10{{/if}} |
| **可选页大小** | [10, 20, 50, 100] |
| **显示总数** | ✅ `showTotal: (total) => 共 ${total} 条` |
| **显示快速跳转** | ✅ `showQuickJumper: true` |
| **显示页大小选择** | ✅ `showSizeChanger: true` |

{{> skill-guide }}

---

{{> api-section }}

---

{{> self-check }}

{{> dev-checklist }}

{{> dev-reconciliation }}
