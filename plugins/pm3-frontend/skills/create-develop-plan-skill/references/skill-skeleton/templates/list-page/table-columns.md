# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

## 表格列配置

| # | 列标题 | dataIndex | 宽度 | 固定 | 排序 | 省略 | 字典 | 备注 |
|---|--------|-----------|------|------|------|------|------|------|
{{#each columns}}| {{@index}} | {{title}} | `{{dataIndex}}` | {{#if width}}{{width}}{{else}}-{{/if}} | {{#if fixed}}{{fixed}}{{else}}-{{/if}} | {{#if sorter}}✅{{else}}-{{/if}} | {{#if ellipsis}}✅{{else}}-{{/if}} | {{#if dictCode}}`{{dictCode}}`{{else}}-{{/if}} | {{#if note}}{{note}}{{else}}-{{/if}} |
{{/each}}

---

## 列详细配置

{{#each columns}}
### 列{{@index}}：{{title}}（{{dataIndex}}）

| 属性 | 值 |
|------|-----|
| title | `{{title}}` |
| dataIndex | `{{dataIndex}}` |
{{#if width}}| width | {{width}} |
{{/if}}{{#if fixed}}| fixed | `{{fixed}}` |
{{/if}}{{#if sorter}}| sorter | true |
{{/if}}{{#if ellipsis}}| ellipsis | true |
{{/if}}{{#if dictCode}}| dictCode | `{{dictCode}}` |
{{/if}}{{#if customRender}}| customRender | {{customRender}} |
{{/if}}

{{#if columnLogic}}
#### 列交互逻辑
{{columnLogic}}
{{/if}}

---
{{/each}}

---

{{> self-check }}

{{> dev-checklist }}
