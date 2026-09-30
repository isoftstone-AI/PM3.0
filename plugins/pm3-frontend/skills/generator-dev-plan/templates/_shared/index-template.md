# {{moduleName}} 开发方案索引

> PRD 文档：[{{prdPath}}]({{prdPath}})

## 开发模块总览

| 序号 | 页面名称 | 页面类型 | 推荐 Skill | 包含模块 |
|---|---|---|---|---|
{{#each pages}}
| {{index}} | {{pageName}} | {{pageTypeText}} | `{{skillName}}` | {{modules}} |
{{/each}}

## 页面关系图

```mermaid
{{mermaidDiagram}}
```

## Skill 速查表

| 页面类型 | Skill | 适用场景 |
|---|---|---|
| 列表页 | `/scene-list` | 搜索 + 表格 + 操作列 |
| 表单页 | `/scene-form` | 表单字段 + 校验 + 提交 |
| 详情页 | `/scene-detail` | 只读详情展示 |
| 审批页 | `/scene-approval` | 审批页（只读 + 审批操作）|
| 弹窗 | 手动开发 | 搜索 + 表格 + 单选/多选 |

## 文件索引

{{#each files}}
### {{pageName}}
{{#each modules}}
- [{{moduleCode}} {{moduleName}}](./{{fileName}})
{{/each}}
{{/each}}
