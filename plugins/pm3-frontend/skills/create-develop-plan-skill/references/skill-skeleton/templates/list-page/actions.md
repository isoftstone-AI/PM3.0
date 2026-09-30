# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

## 操作按钮配置

| # | 状态 | 按钮文字 | API | 确认提示 | 动作 |
|---|------|---------|-----|---------|------|
{{#each buttons}}| {{@index}} | {{status}} | {{buttons}} | `{{api}}` | {{#if confirm}}`{{confirm}}`{{else}}-{{/if}} | {{action}} |
{{/each}}

---

## 按钮详细配置

{{#each buttons}}
### 按钮{{@index}}：{{status}} - {{buttons}}

| 属性 | 值 |
|------|-----|
| 状态 | `{{status}}` |
| 按钮文字 | {{buttons}} |
{{#if api}}| API | `{{api}}` |
{{/if}}{{#if confirm}}| 确认提示 | `{{confirm}}` |
{{/if}}{{#if action}}| 动作 | {{action}} |
{{/if}}{{#if permission}}| 权限 | {{permission}} |
{{/if}}

{{#if buttonLogic}}
#### 按钮逻辑
{{buttonLogic}}
{{/if}}

---
{{/each}}

---

{{> self-check }}

{{> dev-checklist }}
