### 样式参考（来自设计图）

{{#if designDocPath}}
| 设计项 | 规格 | 来源 |
|--------|------|------|
{{#if styleConfig.layout}}
| 表单布局 | {{styleConfig.layout}} | [设计图 {{designSection}}]({{designDocPath}}) |
{{/if}}
{{#if styleConfig.gutter}}
| 字段间距 | {{styleConfig.gutter}} | [设计图 {{designSection}}]({{designDocPath}}) |
{{/if}}
{{#if styleConfig.labelWidth}}
| 标签宽度 | {{styleConfig.labelWidth}} | [设计图 {{designSection}}]({{designDocPath}}) |
{{/if}}
{{#if styleConfig.align}}
| 对齐方式 | {{styleConfig.align}} | [设计图 {{designSection}}]({{designDocPath}}) |
{{/if}}
{{#if styleConfig.colspan}}
| 栅格占比 | {{styleConfig.colspan}} | [设计图 {{designSection}}]({{designDocPath}}) |
{{/if}}
{{#if styleConfig.special}}
| 特殊样式 | {{styleConfig.special}} | [设计图 {{designSection}}]({{designDocPath}}) |
{{/if}}

> ⚠️ **样式优先级**：设计图规格 > 组件默认样式 > 通用规范，必须严格按照设计图实现。
{{else}}
> 📝 提示：请提供设计图文档路径和样式配置，以便生成精确的样式参考。
{{/if}}