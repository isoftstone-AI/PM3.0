# {{pageName}} - 选择弹窗

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

## 搜索条件

| # | 字段名 | 中文名 | 组件 | 必填 |
|---|--------|--------|------|------|
{{#each searchFields}}| {{@index}} | {{name}} | {{label}} | {{component}} | {{#if required}}✅{{else}}N{{/if}} |
{{/each}}

---

## 表格列配置

| # | 列标题 | dataIndex | 宽度 | 备注 |
|---|--------|-----------|------|------|
{{#each tableColumns}}| {{@index}} | {{title}} | `{{dataIndex}}` | {{#if width}}{{width}}{{else}}-{{/if}} | {{#if note}}{{note}}{{else}}-{{/if}} |
{{/each}}

---

## 选择逻辑

| 属性 | 值 |
|------|-----|
| 选择模式 | {{#if singleSelect}}单选{{else}}多选{{/if}} |
| 选中高亮 | {{#if highlightRow}}是{{else}}否{{/if}} |
| 弹窗显隐 | `open` prop |

### 返回值映射

| # | 表格字段 | 返回字段名 | 目标字段 |
|---|---------|-----------|---------|
{{#each returnMapping}}| {{@index}} | `{{sourceField}}` | `{{returnField}}` | `{{targetField}}` |
{{/each}}

---

## Skill 使用指引

{{> skill-guide }}

---

{{> self-check }}

{{> dev-checklist }}
