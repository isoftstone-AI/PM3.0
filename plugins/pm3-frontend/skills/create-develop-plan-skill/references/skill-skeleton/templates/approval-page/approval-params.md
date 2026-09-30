# {{pageName}} - 审批页参数总览

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

## 业务组件信息

> **架构约束**：审批页开发方案只输出 Skill 需要的业务参数清单，**不定义代码结构**。审批页代码结构由 Skill 模板控制。**禁止**在开发方案中出现 Section 组件拆分、自定义 BPM 回调 API 定义。

### 查看组件

| 属性 | 值 |
|------|-----|
| 组件名 | `{{viewComponentName}}` |
| 导入路径 | `{{viewComponentImport}}` |
| 渲染模式 | `{{viewDisplayMode}}` |

### 编辑组件

| 属性 | 值 |
|------|-----|
| 组件名 | `{{editComponentName}}` |
| 导入路径 | `{{editComponentImport}}` |
| expose 方法 | `{{editExposeMethods}}` |

### API 配置

| 属性 | 值 |
|------|-----|
| 详情 API | `{{detailApiFn}}` |
| 导入路径 | `{{detailApiImport}}` |

### 审批配置

| 属性 | 值 |
|------|-----|
| 审批注册 key | `{{approvalRegisterKey}}` |
| 英文标识 | `{{englishId}}` |

---

## 节点校验规则

| # | 节点 | 校验字段 | 校验规则 |
|---|------|---------|---------|
{{#each nodeValidations}}| {{@index}} | {{nodeKey}} | {{fields}} | {{rules}} |
{{/each}}

---

## Skill 使用指引

{{> skill-guide }}

---

{{> self-check }}

{{> dev-checklist }}
