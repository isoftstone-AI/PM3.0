---
name: scene-detail
description: 详情页代码生成器。根据 PRD 文档、API 文档和设计稿，基于实际上线代码模板生成完整的详情页代码（多模块 Section 组件 + DetailModal 主编排 + useDetail hook + dataTransform 数据转换）。当用户说"开发详情页"、"生成详情页"、"新建详情页"、"详情页"时触发。也适用于用户提供了 PRD + API 文档并要求生成包含多个 Card 模块、支持只读/编辑、弹窗/嵌入双模式的详情展示页面。即使用户没有明确说"详情页"，只要需求包含多个信息模块展示、Card 布局、支持查看/编辑切换的组合特征，就应该使用此 skill。
category: code-generation
tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
version: 1.0.0
---

# 详情页代码生成器

根据 PRD 文档、API 文档和设计稿，生成可直接使用的详情页代码。

## 核心原则

详情页的本质是**多个模块的编排**。模板提供了骨架和数据流范式——你的工作是识别模块、映射字段、生成各 Section 组件，并正确编排它们之间的数据联动。

**审批记录模块强制**：所有详情页必须包含审批记录模块，使用 `@/components/ApprovalProcess` 组件，放置在最后一个业务 Section 之后。该模块不需要独立 Section 组件，直接在 DetailModal 主编排组件中接入。展示条件：`!!detail.value?.id`（非首次新建时展示）。

## 执行前准备

1. 读取 `references/reference.md` 获取完整代码模板（5 个 Block）
2. 读取项目 `CLAUDE.md` 获取核心组件表和字段规范
3. 收集用户提供的输入材料（PRD、API 文档、设计稿路径）

如果用户未提供任何输入材料，用 AskUserQuestion 询问：
- PRD 文档路径（或直接粘贴内容）
- API 文档路径（或直接粘贴内容）
- 设计稿路径（可选）

## 执行步骤

### Step 1：提取 PRD 信息

从 PRD 文档中提取以下内容：

| 提取项 | 用途 | 示例 |
|--------|------|------|
| 模块列表 | 每个 Card 对应一个 Section 组件 | 基础信息、开工信息、成本测算... |
| 模块字段 | 每个模块包含哪些表单字段 | 项目名称、SAP编码、项目业态... |
| 模块间联动 | 哪些模块之间有数据依赖 | 基础信息.项目业态 → 开工信息.容量字段显示 |
| 状态枚举 | 审批状态、单据类型等 | 0=草稿, 1=审批中, 2=审批完成 |
| 条件显示 | 某些模块是否按条件显示 | 审批完成才显示历史记录 |

**输出**：整理成表格展示给用户确认，格式：

```
## 模块清单
| 模块名 | Section 组件名 | 包含字段数 | 联动关系 | 条件显示 |
|--------|---------------|-----------|---------|---------|

## 模块字段详情
### 模块1：基础信息
| 字段名 | 中文名 | 类型 | 必填 | 组件 | 特殊逻辑 |
|--------|--------|------|------|------|---------|

## 状态枚举
| 枚举名 | 值 | 含义 |
|--------|-----|------|
```

**关键**：模块识别时注意以下规律——
- PRD 中的"标题"、"区域"、"模块"通常对应一个 Card
- 共享同一组数据的字段归入同一模块
- 如果模块字段超过 15 个，考虑拆分为子模块

### Step 2：识别组件映射

为 Step 1 识别的每个字段选择合适的组件。

**组件选择优先级**（从高到低）：

| 优先级 | 来源 | 适用场景 |
|--------|------|----------|
| 1 | CLAUDE.md 核心组件表 | DictSelect、LovSelect、OrgSelect 等项目封装组件 |
| 2 | ant-design-vue 基础组件 | Input、Select、DatePicker、InputNumber |
| 3 | AskUserQuestion | 以上都找不到合适的，停下来问用户 |

**常见字段与组件映射**：

| 字段特征 | 推荐组件 | 说明 |
|---------|----------|------|
| 自由文本（短） | `Input` | placeholder + disabled |
| 自由文本（长） | `Input.TextArea` | rows=4, maxlength=500, showCount |
| 固定选项 | `Select` | options + disabled |
| 字典选项 | `DictSelect` | code + disabled |
| 组织选择 | `OrgSelect` | disabled |
| 用户选择 | `LovSelect` | disabled |
| 数字输入 | `InputNumber` | precision=2, addonAfter 单位 |
| 日期选择 | `DatePicker` | valueFormat="YYYY-MM-DD" |
| 是/否选择 | `Select` 或 `BooleanSelect` | Option value=1/0 |
| 省市区选择 | `Cascader` 或 `AreaSelector` | 输出 code + name |
| 附件上传 | `AttachmentFileList` | readonly 控制 |
| 状态标签 | `Tag` | color 映射 |
| 纯文本展示 | 直接文本 | `{value || '-'}` 空值兜底 |

**停下来问用户的场景**：
- 字段在 CLAUDE.md 核心组件表中找不到对应组件
- PRD 中某字段的含义不明确
- API 文档字段名与 PRD 描述不匹配
- 字段的交互方式不常见（如地图选点、签名板等）

### Step 3：生成 dataTransform

根据 API 文档和 Step 1/2 的分析结果，生成数据转换函数。

**核心职责**：将后端返回的扁平详情数据，转换为各 Section 组件需要的表单数据结构。

**模板参考**：`references/reference.md` Block 1

**生成规则**：
- 每个模块一个转换函数，命名为 `detailTo{ModuleName}`
- 函数入参为 `detail: Partial<XxxDetail>`，返回对应 Section 的类型
- 字段映射时做空值兜底：`detail.fieldName || ''`
- 数组类型字段做空数组兜底：`detail.fieldName || []`
- 附件列表需要特殊处理 attachmentType 映射

### Step 4：生成各 Section 组件

每个模块生成一个独立的 tsx 组件文件。

**模板参考**：`references/reference.md` Block 2

**文件结构**：
```
components/
├── BasicInfoSection/
│   ├── index.tsx
│   └── style.module.less
├── StartInfoSection/
│   ├── index.tsx
│   └── style.module.less
└── ...（每个模块一个目录）
```

**每个 Section 必须包含**：
1. **Props 定义**：`value`（数据）+ `disabled`（是否禁用）
2. **Form 校验**：disabled 时返回空数组跳过必填校验
3. **expose**：暴露 `validate()` 和 `getValues()`
4. **双向绑定**：通过 `emit('update:value', {...props.value, [key]: value})`
5. **disabled 渲染**：**统一使用组件 `disabled` 属性，禁止用 `<span>` 替换组件渲染**

**disabled 渲染规则**：
- **禁止**：用 `<span>{text || '-'}</span>` 替换组件（Input/Select/LovSelect 等一律用 `disabled`）
- **允许**：纯展示模块（单据信息、审批记录）用 `Descriptions` 组件
- **附件**：用 `AttachmentFileList readonly` 或 Upload `onlyShowFileList`

### Step 5：生成主编排组件

生成 DetailModal 主编排组件，负责整合所有 Section。

**模板参考**：`references/reference.md` Block 3（useDetail）+ Block 4（index.tsx）+ Block 5（style）

**必须包含的能力**：

1. **双模式渲染**：`displayMode: 'modal' | 'embedded'`
   - modal 模式：用 `BasicModal` 包裹，支持 `defaultFullscreen`
   - embedded 模式：用 div 包裹，适配审批页嵌入

2. **数据加载策略**：
   - modal 模式：内部调用 `useDetail` hook 加载数据
   - embedded 模式：接收 `externalData` prop，不调用 API

3. **数据分发**：
   - 从 `detail` 提取各模块数据（通过 dataTransform）
   - 用 `watch` 监听 detail 变化，实时同步到各模块

4. **Card 编排**：
   - 每个 Section 用 `<Card size="small" title="xxx" class="!mt-10px">` 包裹
   - 用 `<section id="xxx">` 配合锚点导航（可选）

5. **expose**：暴露 `getData()` 供父组件收集各模块数据

6. **审批记录模块（强制，P0）**：

   所有详情页在最后一个业务 Section 之后，**必须**包含审批记录模块。

   | 项 | 说明 |
   |----|------|
   | 组件 | `@/components/ApprovalProcess`（全局公共组件，无需自建 Section） |
   | 入参 | `primaryKey={detail.value?.id}` |
   | 展示条件 | `!!detail.value?.id`（非首次新建时展示） |
   | 包裹 | `<Card size="small" title="审批记录" class="!mt-10px">` |
   | 定位 | 所有业务 Section 之后，文件末尾 |

   **模板代码**（直接写入 DetailModal index.tsx，不要遗漏）：

   ```tsx
   // [KEEP] 审批记录模块 — 固定代码，禁止删除或替换
   {!!detail.value?.id && (
     <section id="record" class={styles.section}>
       <Card size="small" title="审批记录" class="!mt-10px">
         <ApprovalProcess primaryKey={detail.value?.id} />
       </Card>
     </section>
   )}
   ```

   **依赖导入**（必须包含）：

   ```tsx
   import ApprovalProcess from '@/components/ApprovalProcess';
   ```

   **特殊情况**：如果业务需要自定义审批记录展示（如海外商机），可参考 `overseas/opportunity/components/ApprovalProcessSection` 模式，但必须使用 `@/components/ApprovalProcess` 作为基础，不得自行实现审批记录查询逻辑。

**文件清单**：
```
components/DetailModal/
├── index.tsx              # 主编排组件
├── useDetail.ts           # 数据加载 hook
└── style.module.less      # 样式
```

## 输出

完成所有步骤后，输出以下文件内容，**按文件逐个展示**：

1. `utils/dataTransform.ts` — 数据转换函数
2. 各 `components/XxxSection/index.tsx` — 每个 Section 组件
3. `components/DetailModal/useDetail.ts` — 数据加载 hook
4. `components/DetailModal/index.tsx` — 主编排组件
5. `components/DetailModal/style.module.less` — 样式

每个文件输出后，告知用户："以上是 `{文件名}` 的代码，请确认是否正确。"

## 生成后自检

代码生成完成后，执行以下自检，**在输出中明确标注通过/未通过**：

| 检查项 | 优先级 | 检查方式 |
|--------|--------|----------|
| **审批记录模块（ApprovalProcess）** | **P0 强制** | 搜索 `import ApprovalProcess from '@/components/ApprovalProcess'`；确认 DetailModal 中有 `!!detail.value?.id && <ApprovalProcess` 渲染块 |
| 每个 Section 有独立 tsx 文件 | P1 | 确认文件存在 |
| 每个 Section 有 expose validate/getValues | P1 | 搜索 `expose` |
| 使用 `defineComponent` 定义组件 | P1 | 搜索 `defineComponent` |
| 未使用 `render()` 函数 | P1 | 搜索 `render()` 在组件定义中 |
| 未在 TSX 中使用 `this` | P1 | 搜索 `this.` |
| 未在 `defineComponent` 中写 `components` | P1 | 搜索 `components:` 配置 |
| 每个 Card 用 `size="small"` 包裹 | P1 | 搜索 `Card size="small"` |
| 模块间距用 `!mt-10px` 或 `class={styles.section}` | P1 | 搜索间距配置 |
| 支持 displayMode 双模式 | P1 | 确认 `displayMode` prop 和分支渲染 |
| 支持 type view/edit 双时态 | P1 | 确认 `type` prop 和 `disabled` 计算 |
| 弹窗模式用 BasicModal | P1 | 搜索 `BasicModal` |
| API 使用 defHttp 封装 | P1 | 搜索 `defHttp` |
| 空值兜底处理 | P1 | 搜索 `\|\| '-'` 或 `?? '-'` |
| disabled 时跳过必填校验 | P1 | 确认 `requiredRule` 逻辑 |
| 只读字段用 disabled 而非 span 替换 | P1 | 搜索 `<span>` 在 Section 组件中 |

**P0 检查项未通过时，禁止输出代码。必须先修正再继续。**

---

## 数据绑定模式选择

Section 组件支持两种绑定模式，根据使用场景选择：

| 模式 | Props | Emits | 适用场景 |
|------|-------|-------|----------|
| **value 模式** | `value: Object` | `update:value` | 详情页内部编排，由 DetailModal 统一管理数据 |
| **modelValue 模式** | `modelValue: Object` | `update:modelValue` | 审批页嵌入场景，或需要与 v-model 配合使用 |

**选择建议**：
- 如果 Section 只被 DetailModal 使用 → 用 `value` 模式
- 如果 Section 需要被审批页嵌入且直接编辑 → 用 `modelValue` 模式
- 同一个项目内保持统一，推荐优先使用 `value` 模式

**代码差异**：
```tsx
// value 模式
props: { value: { type: Object, required: true } }
emits: ['update:value']
emit('update:value', { ...props.value, [key]: value })

// modelValue 模式
props: { modelValue: { type: Object, required: true } }
emits: ['update:modelValue']
emit('update:modelValue', { ...props.modelValue, [key]: value })
```

---

## Section 组件嵌入模式契约（P0 强制）

> 本节规则优先级 P0：违反时禁止输出代码，必须先修正。
> 依据：`templates/_shared/component-render-mode.md`

### 标准 Props 接口

每个 Section 组件必须声明以下 Props，**缺一不可**：

```typescript
// 标准 Section props 契约（每个 Section 必须符合）
interface SectionProps<T> {
  value: T;                    // [必须] 受控数据对象，禁止内部维护 reactive 副本
  disabled: boolean;           // [必须] 全局只读开关，true = 只读，false = 可编辑
  editableFields?: string[];   // [可选] 可编辑字段白名单（用于节点级精细权限）
}
// 标准 emits
emits: ['update:value']
// 标准 expose（所有 Section 必须暴露，缺少则审批页无法调用）
expose({ getData(): T, validate(): Promise<void> })
```

### isFieldDisabled 标准实现

```typescript
// 每个 Section 中的字段禁用判断，必须使用此函数签名
const isFieldDisabled = (fieldName: string): boolean => {
  if (props.disabled) return true;
  if (props.editableFields && props.editableFields.length > 0) {
    return !props.editableFields.includes(fieldName);
  }
  return false;
};

// 在模板中使用
<Input value={props.value.fieldName} disabled={isFieldDisabled('fieldName')} />
```

### 四条禁止行为（违反即 P0 失败）

| # | 禁止行为 | 正确做法 |
|---|---------|---------|
| 1 | Section 内部调用 API（如 `getDetail`） | 数据由父级（DetailModal/ApprovalPage）提供，通过 `value` prop 传入 |
| 2 | Section 内部包裹 `<Card>` | Card 由编排层（DetailModal/ReviewApplyForm）负责，Section 只输出字段内容 |
| 3 | 用 `<span>{value.field \|\| '-'}</span>` 替代 disabled 组件 | 组件类型不变，只切换 `disabled` prop（见 `component-render-mode.md`） |
| 4 | `const state = reactive({...props.value})` 内部副本 | 直接读 `props.value`，修改通过 `emit('update:value', {...props.value, [key]: v})` |

### 生成后自检追加项（P0）

在现有自检表末尾追加：

| 检查项 | 优先级 | 检查方式 |
|--------|--------|----------|
| Section props 包含 value + disabled（+ 可选 editableFields） | **P0** | 搜索每个 Section 的 `props:` 定义 |
| Section expose 包含 getData() 和 validate() | **P0** | 搜索 `expose(` |
| Section 内无 API 调用 | **P0** | 搜索 Section 文件内的 `defHttp` 或 `await get` |
| Section 内无 `<Card` 包裹 | **P0** | 搜索 Section 文件内的 `<Card` |
| isFieldDisabled 函数存在（当有 editableFields 时） | P1 | 搜索 `isFieldDisabled` |

---

## 引用文件

- 代码模板 → `references/reference.md`（必须先读取）
- 核心组件表 → 项目 `CLAUDE.md`
- 字段规范 → `form-map.md` / `form-map2.md`
- 命名规范 → `base-naming.md`
- API 规范 → `base-api.md`
- TSX 规范 → `base-tsx.md`
