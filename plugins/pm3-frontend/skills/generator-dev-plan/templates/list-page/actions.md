# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

## 按钮配置总览

| 审批状态 | 按钮名 | 触发接口 | 二次确认 | 跳转/弹窗 |
|---------|--------|---------|---------|----------|
{{#each buttons}}| {{status}} | {{buttons}} | {{#if api}}{{api}}{{else}}无{{/if}} | {{#if confirm}}✅{{else}}无{{/if}} | {{action}} |
{{/each}}

---

## 按钮详细配置

{{#each buttons}}
### 按钮：{{buttons}}（{{status}}状态）

| 项 | 值 |
|----|-----|
| **显示条件** | `status === '{{status}}'` |
| **按钮文本** | {{buttons}} |
| **点击行为** | {{action}} |
| **二次确认** | {{#if confirm}}文案：{{confirm}}{{else}}无{{/if}} |
| **接口调用** | {{#if api}}{{api}}{{else}}无{{/if}} |

{{/each}}

---

{{> api-section }}

---

{{> self-check }}

{{> dev-checklist }}

{{> dev-reconciliation }}
