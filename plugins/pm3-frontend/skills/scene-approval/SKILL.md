---
name: scene-approval
description: 审批页代码生成器。根据业务组件信息和 API 文档，基于实际上线代码模板生成完整的审批页代码（审批模板页面 + ApprovalForm 审批组件 + 注册入口）。当用户说"开发审批页"、"生成审批页"、"新增审批"、"审批页面"、"为 XX 模块添加审批"时触发。也适用于需求包含"业务详情展示 + 审批操作按钮 + 权限判断 + 驳回重发"组合特征的场景。前提：业务的查看组件和编辑组件已存在。即使用户没有明确说"审批页"，只要需求涉及待办审批、审批流对接、审批操作页面的开发，就应使用此 skill。
category: code-generation
tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
version: 1.0.0
---

# 审批页代码生成器

根据业务组件信息和 API 文档，生成可直接使用的审批页代码。

## 核心原则

审批页是**业务组件和审批逻辑的编排层**。模板提供了固定的审批流程骨架——你的工作是识别业务组件的差异点，精确替换 `[REPLACE]` 区域，不触碰 `[KEEP]` 标记的审批框架代码。

## 审批页架构

审批页分为两层，职责明确分离：

| 层级 | 文件 | 职责 |
|------|------|------|
| 审批模板页面 | `apply-modal/xxxApproval.tsx` | 加载详情、provide 权限、驳回重发判断、提交前校验 |
| 审批表单组件 | `apply-modal/approval-form/XxxApprovalForm.tsx` | 获取权限、模式判断、审批操作、按钮渲染（通用，几乎不变） |

### 数据流

```
approval/index.tsx（待办入口，调用 getTaskById）
  → register.tsx（applyName 路由到对应审批模板）
    → xxxApproval.tsx（审批模板页面）
       ├── 业务查看/编辑组件（由各模块提供）
       └── XxxApprovalForm.tsx（审批表单组件）
           ├── getOperationRole → 权限判断
           ├── onParentSubmit → 触发父组件校验 & 保存
           ├── completeTodoApi → 提交审批
           └── onAfterSbumit → 审批成功后回调
```

### 权限模式（templatePermission）

审批表单组件通过 `getOperationRole` API 获取当前用户的操作权限，根据返回的 `templateKey` 决定显示哪些按钮和表单：

| templateKey | 含义 | 按钮显示 |
|-------------|------|----------|
| `submit_save` | 驳回重发 / 补录 | 提交 + 取消 |
| `apply_system` | 系统补录 | 提交 + 取消 |
| `approve_reject` | 可审批可驳回 | 同意 + 驳回 + 抄送 |
| `approve` | 仅同意 | 同意 + 抄送 |
| `card_approve_make_copy` | 已阅 | 已阅 |
| `confirm` | 确认 | 确定 + 取消 |

`operationType` 字段标识当前审批节点（如 `approve_sjrl` 技术部门、`approve_cbcs` 成本部），用于节点级别的特殊校验。

## 目录结构（实际）

```
src/views/office/
├── todo/
│   ├── index.tsx                              # 待办列表页
│   ├── track.vue                              # 审批追踪组件
│   ├── approval/
│   │   └── index.tsx                          # 待办审批入口
│   ├── hooks/
│   │   └── useTableColumn.ts
│   ├── service/
│   │   └── api.ts                             # BPM API（completeTodoApi、getOperationRole 等）
│   └── components/
│       ├── register.tsx                       # ← [修改] 审批组件路由注册
│       ├── apply-modal/                       # ← [新增] 审批模板页面放这里
│       │   ├── xxxApproval.tsx                #   Block 1 生成的文件
│       │   └── approval-form/
│       │       └── XxxApprovalForm.tsx        #   Block 2 生成的文件
│       ├── approval-record/                   # 审批记录展示（已有）
│       ├── forward-modal/                     # 转发弹窗（已有）
│       └── view-modal/                        # 查阅弹窗（已有）
├── done/                                      # 已办（不涉及）
└── launch/                                    # 发起审批（不涉及）
```

## 执行前准备

1. 读取 `references/reference.md` 获取完整代码模板（2 个 Block）
2. 读取项目 `CLAUDE.md` 获取核心组件表
3. 用 Glob 查看目标业务模块已有的组件目录，确认查看/编辑组件是否已存在

如果用户未提供业务信息，用 AskUserQuestion 收集（见 Step 1）。

## 执行步骤

### Step 1：收集业务信息

用 AskUserQuestion 收集信息。分两轮提问，第一轮收集必填项，第二轮根据需要确认可选项。

**第一轮：必填项**

| # | 参数 | 说明 | 示例 |
|---|------|------|------|
| 1 | 业务模块名（中文） | 用于注释和标题 | 施工组织设计评审 |
| 2 | 英文标识 | 用于组件命名和文件路径 | ConstructionDesign |
| 3 | 审批注册 key | register.tsx 中 map 的 key | construction_design_review |
| 4 | 详情组件名 | DetailModal 组件名（用于查看/审批编辑双模式） | EquipmentFundDetailModal |
| 5 | 详情组件导入路径 | 组件文件路径 | @/views/design-manage/equipment-submission/components/EquipmentFundDetailModal |
| 6 | 编辑组件名 | Form 组件名（仅用于驳回重发场景） | EquipmentFundForm |
| 7 | 编辑组件导入路径 | 组件文件路径 | @/views/design-manage/equipment-submission/components/EquipmentFundForm |
| 8 | 详情 API 函数名 | 加载详情的 API | getReviewDetail |
| 9 | 详情 API 导入路径 | API 文件路径 | @/views/eng-manage/construction-design-review/api |

**第二轮：可选项（有默认值，不问直接用默认，仅异常时确认）**

| # | 参数 | 默认值 | 何时需要确认 |
|---|------|--------|------------|
| 10 | businessKey 取法 | `businessKey → primaryKey` | **必须确认**：`businessKey` 还是 `variable.json → businessId` |
| 11 | 详情 API 调用方式 | `getDetail(id)` | 如果需要 `{id}` 包装 |
| 12 | 草稿保存方式 | 组件 ref 方法 `editRef.value?.saveDraft()` | 如果方式不同 |
| 13 | 编辑组件 expose 方法 | `saveDraft` | 如果方法名不同 |
| 14 | 驳回重发回调 | 有，API 名 `updateStatusToApproving` | 如果不需要 |
| 15 | 提交前特殊校验 | 无 | 如果用户提到按节点校验 |
| 16 | 审批结论下拉 | 不需要 | 如果审批节点包含 `approve_spjl` |

**智能推断**（减少问答）：

| 已知信息 | 自动推断 |
|----------|----------|
| 英文标识 `ConstructionDesign` | 组件名 → `ConstructionDesignApproval` / `ConstructionDesignApprovalForm` |
| 审批注册 key | 文件名 → `constructionDesign` |
| 查看组件导入路径 | 详情 API 路径大概率在同级 `api` 目录 |
| 查看和编辑组件同名 | 自动复用，仅 mode 不同 |

**输出**：整理成表格展示给用户确认，格式：

```
## 基本信息
| 项目 | 值 |
|------|-----|
| 业务模块 | 施工组织设计评审 |
| 英文标识 | ConstructionDesign |
| 注册 key | construction_design_review |
| ... | ... |

## 确认以下推断
| 推断项 | 推断结果 |
|--------|----------|
| 文件名 | constructionDesignApproval.tsx |
| 组件名 | ConstructionDesignApproval |
| 详情 API 路径 | @/views/.../api |
```

### Step 2：生成审批模板页面（Block 1）

根据 Step 1 收集的信息，替换模板中 Block 1 的 `[REPLACE]` 区域。

**替换清单**：

| 替换项 | 替换内容 | 来源 |
|--------|----------|------|
| 文件注释 | 业务模块名 | Step 1-1 |
| 组件名 name | `{EnglishId}Approval` | Step 1-2 |
| 详情 API 导入 | 函数名和路径 | Step 1-4/5 |
| 详情组件导入 | 组件名和路径 | Step 1-4/5 |
| 编辑组件导入 | 组件名和路径 | Step 1-6/7 |
| businessKey 取法 | 取值表达式 | Step 1-10 |
| 详情 API 调用 | 调用方式 | Step 1-11 |
| 提交前校验 | 自定义校验区域 | Step 1-15 |
| 驳回重发回调 | onAfterSbumit 函数体 | Step 1-14 |
| 编辑组件 expose 方法 | 方法名 | Step 1-13 |
| 详情组件 expose 方法 | 方法名（如 validateDetail, getDetailData） | Step 1-16 |

**草稿保存方式对照表**——根据实际情况选择对应代码片段填入 `onSubmit`：

| 方式 | 代码片段 |
|------|----------|
| 独立 API 调用 | `await saveDraft(data); return Promise.resolve();` |
| 组件 ref 方法 | `return await editRef.value?.saveDraft();` |
| 组件 ref 提交方法 | `return await contentRef.value?.submitReset();` |

**业务组件渲染模式对照表**——根据组件类型选择渲染代码：

| 场景 | 组件类型 | 渲染代码 |
|------|----------|----------|
| 驳回重发（全量编辑） | 编辑组件（如 EquipmentFundForm） | `<EditComp ref={editRef} type="edit" mode="rejected" id={key} displayMode="embedded" />` |
| 查看/审批（双模式） | 详情组件（如 EquipmentFundDetailModal）查看模式 | `<DetailComp ref={detailRef} displayMode="embedded" v-model:externalData={state.detailData} detailEditable={false} />` |
| 查看/审批（双模式） | 详情组件（如 EquipmentFundDetailModal）审批编辑模式 | `<DetailComp ref={detailRef} displayMode="embedded" v-model:externalData={state.detailData} detailEditable={true} nodeType={currentNodeType} />` |

### Step 3：生成 ApprovalForm 审批组件（Block 2）

ApprovalForm 组件是**高度标准化的**，优先复用 `StartApplyApprovalForm` 标准审批模块。

**复用策略**：

| 场景 | 处理方式 |
|------|----------|
| 标准审批操作（同意/驳回/已阅/转发/抄送） | 基于 `StartApplyApprovalForm` 模板生成，仅替换组件名和类型名 |
| 特殊审批需求（自定义操作、特殊权限判断） | 在标准模板基础上扩展，或独立实现 |

**替换项**（仅 2 处）：

| 替换项 | 替换内容 | 示例 |
|--------|----------|------|
| 组件名 name | `{EnglishId}ApprovalForm` | `StartApplyApprovalForm` → `CostReductionApprovalForm` |
| 导出类型名 | `I{EnglishId}ApprovalForm` | `IStartApplyApprovalForm` → `ICostReductionApprovalForm` |

其余代码保持模板不变。这个组件封装了完整的审批操作流程：权限获取、模式判断、同意/驳回/已阅/转发操作、审批意见表单、操作按钮栏。

### Step 4：更新注册入口

在 `register.tsx` 的 map 对象中新增一行映射。

文件路径：`src/views/office/todo/components/register.tsx`

在 map 中添加：

```typescript
'{审批注册key}': '{camelCase文件名}',
// 例：construction_design_review: 'constructionDesignApproval',
```

**输出确认**：展示新增的 map 行和文件路径，让用户确认。

## 输出

完成所有步骤后，输出以下文件内容，**按文件逐个展示**：

1. `apply-modal/{camelCaseName}.tsx` — 审批模板页面（Block 1 替换后）
2. `apply-modal/approval-form/{PascalCaseName}ApprovalForm.tsx` — 审批表单组件（Block 2 替换后）
3. `register.tsx` 变更说明 — 新增的 map 行

每个文件输出后，告知用户："以上是 `{文件名}` 的代码，请确认是否正确。"

## 生成后自检

代码生成完成后，执行以下自检，**在输出中明确标注通过/未通过**：

| 检查项 | 检查方式 |
|--------|----------|
| 使用 `defineComponent` 定义组件 | 搜索 `defineComponent` |
| 未使用 `render()` 函数 | 搜索 `render()` 在组件定义中 |
| 未在 TSX 中使用 `this` | 搜索 `this.` |
| 未在 `defineComponent` 中写 `components` | 搜索 `components:` 配置 |
| 审批模板页面有 provide 权限 | 搜索 `provide.*Permission` |
| 审批模板页面有 loadDetail | 搜索 `loadDetail` |
| 审批模板页面有 isRejected 判断 | 搜索 `isRejected` |
| ApprovalForm 引用了 `getOperationRole` | 搜索 `getOperationRole` |
| ApprovalForm 引用了 `completeTodoApi` | 搜索 `completeTodoApi` |
| ApprovalForm 有 handleAgree / handleReject / handleRead | 搜索三个函数 |
| ApprovalForm 有 ForwardModal 和 TodoViewModal | 搜索两个弹窗 |
| register.tsx 的 map 中有新 key | 搜索新增 key |
| 使用 `InnerLayout` 包裹 | 搜索 `InnerLayout` |
| **loading 绑定到 `loaded` ref** | **搜索 `v-loading={!loaded.value}`，禁止用 `state.loading`** |
| watch 在 `onMounted` 中调用 | 确认 watch 包裹在 onMounted 内 |
| **businessKey 取法兼容两种模式** | **确认同时处理了 `businessKey` 和 `variable.json`** |

如果任何检查项未通过，**立即修正后再输出**。

## 注意事项

1. **onAfterSbumit 拼写**：已有代码中拼写为 `onAfterSbumit`（少一个 u），保持一致不要修正，否则与 ApprovalForm 组件的 prop 名不匹配
2. **ProvideContext 重复定义**：每个审批模板页面独立定义 `ProvideContext` 枚举，不要尝试抽取公共——业务组件通过具体文件路径 import（如 `import { ProvideContext } from '@/views/office/todo/components/apply-modal/startApplyApproval'`）
3. **样式类名**：审批页面使用 `office-approval-wrapper`、`office-card`、`office-btn-wrapper`、`office-approval-content`、`FormLabelWithd100` 等固定类名，保持一致
4. **loaded 判断**：使用 `loaded` ref 控制业务组件渲染时机，确保详情数据加载完成后再渲染，避免组件拿到空数据报错。**禁止使用 `state.loading` 控制渲染，统一用 `loaded` ref**
5. **watch 位置**：推荐在 `onMounted` 中使用 `watch`（参考 constructionDesignApproval 模式），startApplyApproval 中直接在 setup 用 watch 的方式也可接受
6. **provide 写法**：推荐使用 getter 包装（`get templatePermission() { return state.templatePermission; }`），比直接传 `state` 更安全。直接传 `state` 也可接受（如 `startApplyApproval` 的写法），但 getter 方式避免了 reactive 代理可能泄漏到子组件的问题
7. **useDetail hook 类型**：审批页嵌入模式下，`id` 可能为 `ComputedRef<string>`，`enabled` 可能为 `Ref<boolean>`，useDetail 必须支持这两种类型
8. **businessKey 取法决策**：
   - 优先尝试 `props.record?.businessKey`
   - 如果为空，尝试 `JSON.parse(props.record?.variable?.json || '{}')?.businessId`
   - 如果仍为空，尝试 `JSON.parse(props.record?.variable?.json || '{}')?.id`
   - 在代码中同时处理两种取法，提高兼容性

## 引用文件

- 代码模板 → `references/reference.md`（必须先读取）
- 核心组件表 → 项目 `CLAUDE.md`
- 已有审批模板参考 → `startApplyApproval.tsx`（最完整的参考实现）
- 注册入口 → `src/views/office/todo/components/register.tsx`
- BPM API → `src/views/office/todo/service/api.ts`
