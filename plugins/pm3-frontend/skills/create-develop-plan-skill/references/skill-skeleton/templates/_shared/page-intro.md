## 页面导览

> **强制要求（必须先执行）**：开发本页面前，必须先阅读对应 Skill 的全部规则，再开始生成代码。
>
> | 页面类型 | 对应 Skill | 必须阅读的内容 |
> |----------|-----------|---------------|
{{#each sceneMappings}}
> | {{scene}} | `{{skill}}` | 强制规则、执行步骤、生成后自检清单 |
{{/each}}
>
> **违反后果**：不阅读 Skill 直接生成代码，可能导致代码结构错误、组件使用不当、自检项不通过。

| 项 | 内容 |
|---|---|
| 页面名称 | {{pageName}} |
| 页面类型 | {{pageTypeText}} |
| 页面路径 | `{{pageBasePath}}/{{pagePath}}` |
| 所属模块 | {{moduleCode}} - {{moduleName}} |
| 推荐 Skill | `{{skillName}}` |
| 设计方案章节 | {{prdSection}} |

> **开发提示**：本模块为 {{pageTypeText}} 的 {{moduleName}}。

### 预计代码位置

> **注意**：以下文件结构基于 CLAUDE.md 中的目录规范。如果 CLAUDE.md 定义了不同的结构，以 CLAUDE.md 为准。

{{#if directoryStructure}}
{{#each directoryStructure}}
| 文件类型 | 预计路径 |
|---|---|
{{#each files}}| {{type}} | `{{path}}` |
{{/each}}
{{/each}}
{{else}}
| 文件类型 | 预计路径 |
|---|---|
| 页面入口 | `{{pageBasePath}}/{{pagePath}}/index.{{fileExtension}}` |
| 页面逻辑 | `{{pageBasePath}}/{{pagePath}}/hooks/index.{{fileExtension}}` 或由框架决定 |
| API 定义 | `{{pageBasePath}}/{{pagePath}}/api/index.{{fileExtension}}` |
| API 类型 | `{{pageBasePath}}/{{pagePath}}/api/types.{{fileExtension}}` |
| 页面样式 | `{{pageBasePath}}/{{pagePath}}/style.module.{{styleExtension}}` |
| 组件目录 | `{{pageBasePath}}/{{pagePath}}/components/` |
{{/if}}

{{#if mermaidDiagram}}
### 页面关系图

```mermaid
{{mermaidDiagram}}
```
{{/if}}
