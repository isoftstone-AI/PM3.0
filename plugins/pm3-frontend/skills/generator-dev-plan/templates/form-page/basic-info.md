# {{pageName}} - 模块 {{moduleCode}}：{{moduleName}}

{{> nav-links }}

{{> page-intro }}

---

{{> rule-reference }}

---

{{> design-style }}

---

## 字段总表

| # | 字段名 | 中文名 | 组件 | 必填 | 只读 | 字典 | 联动 |
|---|--------|--------|------|------|------|------|------|
{{#each fields}}| {{@index}} | `{{name}}` | {{label}} | {{component}} | {{#if required}}✅{{else}}-{{/if}} | {{#if readOnly}}✅{{else}}-{{/if}} | {{#if dictCode}}`{{dictCode}}`{{else}}-{{/if}} | {{#if linkage}}{{linkage}}{{else}}-{{/if}} |
{{/each}}

---

{{> field-detail }}

## 表单布局

| 项 | 值 |
|----|-----|
| **布局模式** | 卡片包裹（Card） |
| **列数** | {{#if colSpan}}{{colSpan}} 列{{else}}3 列{{/if}} |
| **标签对齐** | 右对齐 |
| **标签宽度** | {{#if labelWidth}}{{labelWidth}}px{{else}}120px{{/if}} |
| **自动填充** | 部分字段通过接口回填 |

### 布局代码示例

```typescript
const formConfig = {
  labelWidth: {{#if labelWidth}}{{labelWidth}}{{else}}120{{/if}},
  baseColProps: { span: {{#if colSpan}}{{divide 24 colSpan}}{{else}}8{{/if}} },
};
```

---

## 联动逻辑

{{#each linkages}}
### {{name}}

| 触发字段 | 触发条件 | 影响字段 | 影响行为 |
|---------|---------|---------|---------|
| {{triggerField}} | {{triggerCondition}} | {{affectedFields}} | {{action}} |

**代码示例：**
```typescript
watch(() => formModel.{{triggerField}}, (val) => {
  if ({{triggerCondition}}) {
    {{action}}
  }
});
```

---
{{/each}}

{{> skill-guide }}

---

{{> api-section }}

---

{{> self-check }}

{{> dev-checklist }}

{{> dev-reconciliation }}
