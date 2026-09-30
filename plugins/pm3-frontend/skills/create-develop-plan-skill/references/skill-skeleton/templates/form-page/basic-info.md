# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

{{> design-style }}

---

## 字段清单

| # | 字段名 | 中文名 | 组件 | 必填 | 联动 |
|---|--------|--------|------|------|------|
{{#each fields}}| {{@index}} | {{name}} | {{label}} | {{component}} | {{#if required}}✅{{else}}N{{/if}} | {{#if linkage}}{{linkage}}{{else}}-{{/if}} |
{{/each}}

---

{{> field-detail }}

## Skill 使用指引

{{> skill-guide }}

---

{{> self-check }}

{{> dev-checklist }}
