## 字段详细配置

> **注意：** 以下为 Skill 模板参数，由对应页面类型的代码生成 Skill（见「Skill 使用指引」章节）决定最终代码结构。
> 当字段属性与 skill 模板结构冲突时，**以 skill 模板为准**，本方案只提供字段属性和业务逻辑。

{{#each fields}}
### 字段{{@index}}：{{name}}（{{label}}）

#### 段1：基础信息
| 属性 | 值 |
|------|-----|
| field | `{{name}}` |
| label | `{{label}}` |
| component | `{{component}}` |
| required | {{#if required}}✅ 是{{else}}否{{/if}} |
| readOnly | {{#if readOnly}}✅ 是{{else}}否{{/if}} |
{{#if dictCode}}| dictCode | `{{dictCode}}` |
{{/if}}{{#if maxLength}}| maxLength | {{maxLength}} |
{{/if}}{{#if placeholder}}| placeholder | `{{placeholder}}` |
{{/if}}{{#if defaultValue}}| defaultValue | `{{defaultValue}}` |
{{/if}}{{#if precision}}| 小数精度 | {{precision}} |
{{/if}}{{#if addonAfter}}| 后缀 | {{addonAfter}} |
{{/if}}

{{#if interactiveLogic}}
#### 段2：交互逻辑
> 参考文档：设计方案 {{logicReference}}
{{interactiveLogic}}
{{/if}}

{{#if permissionControl}}
#### 段3：权限控制
> 参考文档：设计方案 {{logicReference}}
{{permissionControl}}
{{/if}}

{{#if businessRule}}
#### 段4：业务规则
> 参考文档：设计方案 {{logicReference}}
{{businessRule}}
{{/if}}

{{#if api}}
#### 关联接口
{{api}}
{{/if}}

{{#if specialRender}}
#### 特殊渲染
{{specialRender}}
{{/if}}

---
{{/each}}
