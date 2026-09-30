## 页面导览

> **强制要求（必须先执行）**：开发本页面前，必须先阅读对应 Skill 的全部规则，再开始生成代码。
>
> | 页面类型 | 对应 Skill | 必须阅读的内容 |
> |----------|-----------|---------------|
> | 列表页 | `/scene-list` | 强制规则（11条）、执行步骤（Step 1-4）、生成后自检清单 |
> | 表单页 | `/scene-form` | 五条铁规则、执行步骤（Step 1-7）、生成后自检清单 |
> | 详情页 | `/scene-detail` | 执行步骤（Step 1-5）、数据绑定模式、生成后自检清单 |
> | 审批页 | `/scene-approval` | 审批架构、执行步骤（Step 1-4）、生成后自检清单 |
> | 弹窗 | `/scene-list` 或 `/scene-form` | 根据弹窗类型选择对应 Skill |
>
> **违反后果**：不阅读 Skill 直接生成代码，可能导致代码结构错误、组件使用不当、自检项不通过，Code Review 不予通过。

| 项 | 内容 |
|---|---|
| 页面名称 | {{pageName}} |
| 页面类型 | {{pageTypeText}} |
| 页面路径 | `src/views/{{pagePath}}` |
| 所属模块 | {{moduleCode}} - {{moduleName}} |
| 推荐 Skill | `{{skillName}}` |
| 设计方案章节 | {{prdSection}} |

> **开发提示**：本模块为 {{pageTypeText}} 的 {{moduleName}}。{{skillHint}}

### 预计代码位置

| 文件类型 | 预计路径 |
|---|---|
| 页面入口 | `src/views/{{pagePath}}/index.tsx` |
| 页面逻辑 | `src/views/{{pagePath}}/useIndex.ts` |
| API 定义 | `src/views/{{pagePath}}/api/index.ts` |
| API 类型 | `src/views/{{pagePath}}/api/types.ts` |
| 页面样式 | `src/views/{{pagePath}}/style.module.less` |
| 组件目录 | `src/views/{{pagePath}}/components/` |

### 页面关系图

> 当前页面在整体流程中的位置：

```mermaid
{{mermaidDiagram}}
```

> 完整页面关系图参见：[开发方案索引](../00-索引.md#页面关系图)
