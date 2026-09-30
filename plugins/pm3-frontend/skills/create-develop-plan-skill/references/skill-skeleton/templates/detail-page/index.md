# {{pageName}} - 全量详情

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

## 详情模块组成

| # | 模块 | 组件 | 说明 |
|---|------|------|------|
{{#each detailSections}}| {{@index}} | {{sectionName}} | {{componentName}} | {{description}} |
{{/each}}

---

## 模块详细配置

{{#each detailSections}}
### 模块{{@index}}：{{sectionName}}

| 属性 | 值 |
|------|-----|
| 组件名 | `{{componentName}}` |
| 导入路径 | `{{componentImport}}` |
| 渲染模式 | `{{displayMode}}` |
| 数据来源 | `{{dataSource}}` |

{{#if sectionFields}}
#### 字段列表

| # | 字段名 | 中文名 | 组件 | 备注 |
|---|--------|--------|------|------|
{{#each sectionFields}}| {{@index}} | {{name}} | {{label}} | {{component}} | {{#if note}}{{note}}{{else}}-{{/if}} |
{{/each}}
{{/if}}

---
{{/each}}

---

## Skill 使用指引

{{> skill-guide }}

---

{{> self-check }}

{{> dev-checklist }}
