# {{moduleName}} 开发方案索引

> PRD 文档：[{{prdPath}}]({{prdPath}})

## 开发模块总览

| 序号 | 页面名称 | 页面类型 | 推荐 Skill | 包含模块 |
|---|---|---|---|---|
{{#each pages}}
| {{index}} | {{pageName}} | {{pageTypeText}} | `{{skillName}}` | {{modules}} |
{{/each}}

{{#if mermaidDiagram}}
## 页面关系图

```mermaid
{{mermaidDiagram}}
```
{{/if}}

## Skill 速查表

| 页面类型 | Skill | 适用场景 |
|---|---|---|
{{#each sceneMappings}}
| {{scene}} | `{{skill}}` | {{description}} |
{{/each}}

## 文件索引

{{#each files}}
### {{pageName}}
{{#each modules}}
- [{{moduleCode}} {{moduleName}}](./{{fileName}})
{{/each}}
{{/each}}
