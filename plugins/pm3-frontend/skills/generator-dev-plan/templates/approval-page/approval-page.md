# {{pageName}} - 审批页参数总览

{{> nav-links }}

{{> page-intro }}

---

## 重要原则

> 本文档输出的是 `/scene-approval` Skill 需要的**业务参数清单**，不是代码结构定义。
> 审批页的代码结构（两层分离、ApprovalForm、权限模式等）完全由 `/scene-approval` 模板控制。
> **禁止**根据本文档自行创建 Section 组件、自定义 BPM API 或单体式审批页。

---

## 业务组件信息

| 项目 | 值 |
|------|-----|
| **业务模块名（中文）** | {{moduleName}} |
| **英文标识** | {{englishId}} |
| **审批注册 key** | {{approvalRegisterKey}} |
| **查看组件名** | {{viewComponentName}} |
| **查看组件导入路径** | `{{viewComponentImportPath}}` |
| **编辑组件名** | {{editComponentName}} |
| **编辑组件导入路径** | `{{editComponentImportPath}}` |
| **详情 API 函数名** | {{detailApiFn}} |
| **详情 API 导入路径** | `{{detailApiImportPath}}` |
| **详情类型名** | {{detailTypeName}} |
| **详情类型导入路径** | `{{detailTypeImportPath}}` |

### 渲染模式

> 从以下三种模式中选择，与 `/scene-approval` 的"查看/编辑组件渲染模式对照表"对应

| 模式 | 适用场景 | 本项目选择 |
|------|---------|-----------|
| **A：独立 DetailModal + 独立 EditForm** | 查看和编辑是两个独立组件 | {{renderMode}} |
| **B：同一组件 mode 控制** | 查看和编辑是同一组件，通过 mode/view/edit 区分 | {{renderMode}} |
| **C：独立 DetailView + 独立 EditContent** | 查看是纯展示组件，编辑是独立组件 | {{renderMode}} |

---

## 详情 API 配置

| 项目 | 值 |
|------|-----|
| **businessKey 取法** | {{businessKeyMethod}} |
| **详情 API 调用方式** | {{detailApiCallMethod}} |
| **API 响应数据路径** | {{detailApiDataPath}} |

### businessKey 取法选项

| 方式 | 代码 | 适用模块 |
|------|------|---------|
| A（工程管理通用） | `JSON.parse(props.record?.variable.json ?? '{}')?.businessId ?? ''` | 新模块 |
| B（老模块通用） | `JSON.parse(props.record?.businessKey ?? '{}').primaryKey ?? ''` | 老模块 |

### 详情 API 调用方式选项

| 方式 | 代码 |
|------|------|
| A | `await getDetail({ id })` |
| B | `await getDetail(id)` |
| C | `const { data } = await getDetail(id)` |

---

## 驳回重发配置

| 项目 | 值 |
|------|-----|
| **是否有驳回重发** | {{hasRejectResubmit}} |
| **编辑组件 expose 方法** | {{editExposeMethod}} |
| **草稿保存方式** | {{draftSaveMethod}} |
| **驳回重发回调 API** | {{rejectCallbackApi}} |
| **驳回重发回调 API 路径** | {{rejectCallbackApiPath}} |

### 草稿保存方式选项

| 方式 | 代码 | 适用场景 |
|------|------|---------|
| A（组件 ref 方法） | `return await editRef.value?.saveDraft()` | 编辑组件有 saveDraft 方法 |
| B（独立 API 调用） | `await saveDraft(data); return Promise.resolve();` | 有独立保存草稿 API |
| C（无特殊保存逻辑） | `return Promise.resolve();` | 仅查看，无保存需求 |

---

## 审批提交 API 配置

| 项目 | 值 |
|------|-----|
| **提交 API 类型** | {{submitApiType}} |
| **提交 API 函数名** | {{submitApiFn}} |
| **提交 API 导入路径** | {{submitApiImportPath}} |

### 提交 API 类型说明

| 类型 | 说明 | 适用场景 |
|------|------|---------|
| **标准** | 使用 `completeTodoApi`（从 `@/views/office/todo/service/api` 导入） | 大多数审批流程 |
| **自定义** | 使用业务自定义 BPM 回调 API（如 `equipmentSubmissionBpmCallback`） | 后端有特殊审批接口 |

> 如果选"自定义"，需额外提供：
> - API 函数名和导入路径
> - 调用参数结构（action、comment、attachments 之外还有哪些业务参数）

---

## 审批节点校验规则（可选）

> 如果不同审批节点需要校验不同字段，填写以下表格。
> 无节点校验则留空，生成后由开发者在 onSubmit 中手动补充。

{{#if nodePermissions}}
| 节点枚举 | 节点中文名 | 校验字段 | 错误提示 |
|----------|-----------|---------|---------|
{{#each nodePermissions}}| `{{nodeKey}}` | {{nodeName}} | {{#if validationFields}}{{validationFields}}{{else}}无特殊校验{{/if}} | {{#if validationMsg}}{{validationMsg}}{{else}}-{{/if}} |
{{/each}}
{{else}}
> 无节点级校验需求。
{{/if}}

---

## 额外 Props（可选）

> 如果 ApprovalForm 需要接收业务特有 props（如 detailData、currentNodeType），在此列出。
> 无额外 props 则留空。

{{#if extraProps}}
| Prop 名 | 类型 | 默认值 | 用途 |
|---------|------|--------|------|
{{#each extraProps}}| `{{name}}` | `{{type}}` | {{defaultValue}} | {{description}} |
{{/each}}
{{else}}
> 无额外 props。
{{/if}}

---

## 节点级权限控制（可选）

> 如果不同审批节点控制驳回按钮显示、字段可编辑性等，在此描述。
> 无节点级控制则留空。

{{#if nodePermissionControl}}
| 节点 | 控制项 | 规则 |
|------|--------|------|
{{#each nodePermissionControl}}| `{{nodeKey}}` | {{controlItem}} | {{rule}} |
{{/each}}
{{else}}
> 无节点级权限控制需求。
{{/if}}

---

## 节点权限矩阵（editableFields 映射）

> 当不同审批节点需要编辑不同字段时，填写以下矩阵。
> 此矩阵直接对应 `reviewConfig.ts` 中的权限配置和各 Section 的 `editableFields` prop。
> 无节点级编辑需求则填"全只读"。

{{#if nodeEditableMatrix}}
| 节点 operationType | 节点中文名 | 可编辑 Section 名 | editableFields（字段名数组） |
|---|---|---|---|
{{#each nodeEditableMatrix}}| `{{operationType}}` | {{nodeName}} | {{sectionName}} | `[{{#each fields}}'{{this}}'{{#unless @last}}, {{/unless}}{{/each}}]` |
{{/each}}
{{else}}
> 无节点级可编辑需求，全部节点只读。
{{/if}}

### ApprovalForm 策略决策

> 默认复用 `StartApplyApprovalForm`（标准操作：同意/驳回/已阅/转发）。
> 以下场景才新建自定义 ApprovalForm：

| 触发条件 | 本模块是否触发 | 说明 |
|---------|:------------:|------|
| 自定义审批 API（非 `completeTodoApi`） | {{customApiFlag}} | {{customApiNote}} |
| 非标准按钮逻辑（除同意/驳回/已阅外的按钮） | {{customButtonFlag}} | {{customButtonNote}} |
| 特殊校验流程（节点级字段校验） | {{customValidationFlag}} | {{customValidationNote}} |

**本模块策略**：{{approvalFormStrategy}}（复用 / 新建，原因：{{approvalFormReason}}）

---

## 与标准模板的差异点

> 生成后需要开发者手动调整的特殊逻辑，在此列出。
> 这部分无法被模板自动覆盖，需要针对性补充。

{{#if specialNotes}}
{{specialNotes}}
{{else}}
> 无特殊差异，完全遵循标准模板。
{{/if}}

---

## Skill 使用指引

使用 `/scene-approval` Skill 生成完整审批页代码：

```
/scene-approval
```

**必传参数（从上表复制）：**

| # | 参数 | 值 |
|---|------|-----|
| 1 | 业务模块名（中文） | {{moduleName}} |
| 2 | 英文标识 | {{englishId}} |
| 3 | 审批注册 key | {{approvalRegisterKey}} |
| 4 | 查看组件名 | {{viewComponentName}} |
| 5 | 查看组件导入路径 | {{viewComponentImportPath}} |
| 6 | 编辑组件名 | {{editComponentName}} |
| 7 | 编辑组件导入路径 | {{editComponentImportPath}} |
| 8 | 详情 API 函数名 | {{detailApiFn}} |
| 9 | 详情 API 导入路径 | {{detailApiImportPath}} |

### ApprovalForm 复用策略

> **优先复用标准审批模块**：`ApprovalForm` 优先基于 `StartApplyApprovalForm` 标准模板生成。
>
> | 场景 | 处理方式 |
> |------|----------|
> | 标准审批操作（同意/驳回/已阅/转发/抄送） | 复用 `StartApplyApprovalForm` 模板，仅替换组件名和类型名 |
> | 特殊审批需求（自定义操作、特殊权限判断） | 在标准模板基础上扩展，或独立实现 |
>
> **替换项**（仅2处）：
> - 组件名：`StartApplyApprovalForm` → `{EnglishId}ApprovalForm`
> - 导出类型名：`IStartApplyApprovalForm` → `I{EnglishId}ApprovalForm`

**生成后检查项：**
- ApprovalForm 由 skill 模板标准生成（[KEEP] 区域不修改）
- 审批操作统一走 `completeTodoApi`（除非"审批提交 API 配置"选择了自定义）
- 驳回重发逻辑按 `isRejected` 分支处理
- 节点校验规则按"审批节点校验规则"表格补充到 `onSubmit` 中
- 额外 props 和节点级权限控制按需手动补充

---

{{> self-check }}

{{> dev-checklist }}

{{> dev-reconciliation }}
