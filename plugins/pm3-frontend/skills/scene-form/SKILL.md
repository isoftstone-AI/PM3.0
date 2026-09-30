---
name: scene-form
description: 表单页代码生成器。根据 PRD 文档、API 文档和设计稿，基于实际上线代码模板生成完整的表单页代码（api/ + utils/ + useForm.ts + index.tsx + 多个 Section 组件）。当用户说"开发表单页"、"生成表单页"、"新建表单页"、"表单页"时触发。也适用于用户提供了 PRD + API 文档并要求生成包含表单校验、暂存/提交、多模块组合的页面场景。即使没有明确说"表单页"，只要需求包含表单填写、数据提交、多区域组合、编辑/查看双模式等特征，就应该使用此 skill。
category: code-generation
tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
version: 1.0.0
---

# 表单页代码生成器

根据 PRD 文档、API 文档和设计稿，生成可直接使用的完整表单页代码。

## 核心原则

模板是骨架。你的工作是**按步骤替换骨架中的业务内容**，保持框架不动。

## 五条铁规则

以下规则在生成代码时**必须严格执行**，不可省略：

### 规则 1：框架结构

使用 `Form` + `Row` + `Col` + `Form.Item` 包裹组件。默认参数：

```tsx
<Form
  ref={formRef}
  model={value}
  rules={rules.value}
  labelCol={{ style: 'width:160px' }}
  colon={false}
  labelWrap
>
  <Row gutter={24}>
    <Col span={8}>
      <Form.Item label="字段名" name="fieldName">
        {/* 组件 */}
      </Form.Item>
    </Col>
  </Row>
</Form>
```

### 规则 2：rules 动态化

三种规则工厂（`requiredRule` / `userRequiredRule` / `usersRequiredRule`），disabled 时返回空数组跳过校验。统一带 `trigger: ['blur', 'change']`。

**当 disabled 状态会动态切换时（如审批页嵌入模式下），rules 必须用 `computed` 包裹**：

```tsx
const isDisabled = computed(() => props.disabled);

const rules = computed(() => ({
  techName: [{ required: !isDisabled.value, message: '请输入新技术名称', trigger: 'blur' }],
  majors: [{ required: !isDisabled.value, message: '请选择涉及专业', trigger: 'change' }],
  // ...其他规则
}));

// 模板中绑定 rules.value
<Form rules={rules.value} ...>
```

代码模板 → `references/form-validate.md`

### 规则 3：formRef 校验与 expose 类型声明

Section 组件通过 `formRef` + `expose({ validate })` 暴露校验方法；父组件通过 ref 调用。**必须同时定义 expose 类型接口**。

代码模板 → `references/form-validate.md`

### 规则 4：组件选择优先级

选择表单组件时，按以下顺序决策：

1. **参考已存在的相似模块** — 在项目中搜索同类表单，复用其组件选择
2. **参考 CLAUDE.md 核心组件表** — DictSelect、OrgSelect、UserSelect 等项目封装组件
3. **使用 ant-design-vue 基础组件** — Input、Select、DatePicker 等
4. **不确定时打断用户确认** — 用 AskUserQuestion 询问

### 规则 5：字段映射

字段与组件的对应关系，按以下顺序查找：

1. **CLAUDE.md 常用字段表** — 已定义的字段直接使用对应组件
2. **已开发模块的使用方式** — 搜索项目中相同字段名的用法作为参考
3. **不确定时打断用户确认**

### 规则 6：组件绑定模式分类

按组件类型选择正确的绑定模式：

| 组件类型 | 绑定模式 | 示例 |
|---------|---------|------|
| ant-design-vue 原生基础组件（Input/InputNumber/DatePicker/TextArea） | `v-model:value` | `<Input v-model:value={value.name} />` |
| 项目自定义选择组件（DictSelect/LovSelect/SearchSelect/OrgSelect/UserSelect） | `value` + `onChange` | `<LovSelect value={value.userId} onChange={v => updateValue('userId', v)} />` |
| 项目自定义复杂组件（Upload/AttachmentFileList/I18nInput） | `v-model` | `<Upload v-model={value.fileList} />` |
| **表格 customRender 中的任何组件** | **`value` + `onChange`** | **禁止在 customRender 中使用 `v-model`** |

### 规则 7：表单初始值类型约定

| 组件 | 初始值 | 说明 |
|------|--------|------|
| Input / InputNumber / TextArea | `''` 或 `undefined` | 空字符串或 undefined |
| Select（单选） | `undefined` | 不要用空字符串 |
| DictSelect / LovSelect（单选） | `undefined` | 未选择状态 |
| DictSelect / LovSelect（多选 mode="multiple"） | `undefined` 或 `[]` | 根据组件实现 |
| DatePicker | `undefined` | 无日期 |
| Upload / 文件列表 | `[]` | 空数组 |

### 规则 8：事件通信规范

**禁止**使用 `window.dispatchEvent` / `window.addEventListener` 进行跨组件通信。

**正确方式**：通过 props 回调传递：

```tsx
// 父组件
<DetailListSection
  onEditContributors={(index, contributors) => handleEditContributors(index, contributors)}
/>

// 子组件
const handleEdit = () => {
  props.onEditContributors(props.index, props.contributorList);
};
```

### 规则 9：自动带出字段的组件选择

当字段由其他选择自动带出时（如选择项目后自动带出项目业态、分公司）：

- **禁止**使用纯 `Input` 展示
- **必须使用**对应的选择组件（如 `DictSelect`）并设置 `disabled` 属性
- 如果自动带出值是字典值，使用 `DictSelect` + `code` + `disabled`
- 如果自动带出值是纯文本且非字典，使用 `Input` + `disabled`

### 规则 10：必须支持 modal/embedded 双模式

表单页组件必须支持 `displayMode` prop，值为 `modal` 或 `embedded`。

**modal 模式**（列表页新增/编辑）：
- 使用 `BasicModal` 包裹
- 按钮放在 `v-slots={{ footer: () => ... }}`
- 包含：取消、暂存、提交 三个按钮
- 弹窗标题根据是否有 id 动态显示（新增/编辑）

**embedded 模式**（审批页驳回重发）：
- 直接渲染表单内容（`<div>{renderFormContent()}</div>`）
- 无按钮（由审批页控制）

**参考实现**：`src/views/design-manage/equipment-submission/components/EquipmentFundForm/index.tsx`

### 规则 11：必须提取 renderFormContent 公共方法

将表单内容提取到 `renderFormContent()` 方法，避免 modal 和 embedded 模式重复代码。

```tsx
const renderFormContent = () => (
  <Spin spinning={loading.value}>
    <Form ...>
      <Card size="small" title="基础信息" class="!mt-[10px]">
        <BasicInfoSection ... />
      </Card>
      {/* 其他 Section */}
    </Form>
  </Spin>
);

// 双模式渲染
return () => (
  <>
    {isModalMode.value ? (
      <BasicModal ...>{renderFormContent()}</BasicModal>
    ) : (
      <div>{renderFormContent()}</div>
    )}
  </>
);
```

### 规则 12：必须提供 approveSaveDraft expose 方法

审批页驳回重发场景需要调用此方法，签名：

```typescript
export interface XxxFormRef {
  approveSaveDraft: () => Promise<void>;  // 驳回重发保存
  approveSubmit: () => Promise<void>;     // 驳回重发提交
  getFormData: () => XxxFormData;         // 获取表单数据
}
```

**实现要点**：
- `approveSaveDraft`：校验表单 → 调用更新接口 → 返回 Promise
- `approveSubmit`：校验表单 → 调用提交接口 → 返回 Promise
- 审批页通过 `formRef.value?.approveSaveDraft()` 调用

## 执行前准备

1. 读取 `references/reference.md` 获取完整代码模板
2. 读取项目 `CLAUDE.md` 获取核心组件表和字段规范
3. 根据业务模块，按需读取 `references/form-map.md`（按模块查字段映射）或 `references/form-map2.md`（按字段查组件用法）
4. 收集用户提供的输入材料（PRD、API 文档、设计稿路径）

如果用户未提供任何输入材料，用 AskUserQuestion 询问：
- PRD 文档路径（或直接粘贴内容）
- API 文档路径（或直接粘贴内容）
- 设计稿路径（可选）

## 执行步骤

### Step 1：提取 PRD 信息

从 PRD 文档中提取以下内容：

| 提取项 | 用途 | 示例 |
|--------|------|------|
| 表单字段分组 | 决定 Section 数量和内容 | 基础信息、开工信息、计划节点... |
| 每组字段详情 | 替换各 Section 的 Form.Item | 字段名、中文名、组件类型、校验规则 |
| 字段联动规则 | 实现动态显示/隐藏、必填切换 | 业态→容量字段联动、模式→可编辑切换 |
| 操作按钮规则 | 替换提交/暂存逻辑 | 暂存不校验、提交校验必填 |
| 表单模式 | 决定 disabled/编辑控制 | 新增/编辑/查看、首次/二次/重新 |

**输出**：整理成表格展示给用户确认，格式：

```
## Section 划分
| Section 名称 | 字段数 | 说明 |
|--------------|--------|------|

## 字段详情（按 Section 分组）
| 字段名 | 中文名 | 组件类型 | 必填 | 联动规则 |
|--------|--------|----------|------|----------|

## 操作按钮
| 按钮 | 行为 | 校验 |
|------|------|------|
```

### Step 2：替换 api/types.ts

根据 API 文档替换模板中 `Block 1` 的类型定义。

**替换规则**：
- 删除 start-apply 的业务类型，替换为新的 Record、FormData、Detail 等
- 保留模板中的通用工具类型（FormMode 等）
- 类型定义严格遵循 API 文档字段名

**停下来问用户的场景**：
- API 文档字段与 PRD 描述不匹配
- 字段类型无法确定（如枚举值不明确）

### Step 3：替换 api/index.ts

根据 API 文档替换模板中 `Block 2` 的 API 封装。

**替换规则**：
- 替换 `Api.Prefix` 为实际接口前缀（格式：`/api/pm3/模块名` 或 `/api/pm-engineering/模块名`）
- 至少包含：getDetail（获取详情）、save（暂存）、submit（提交）
- 所有函数使用 `defHttp` 封装，入参出参类型明确
- 根据业务需要添加其他接口（删除、验证、导出等）

### Step 4：替换 utils/dataTransform.ts

根据 API 返回的字段和表单字段的映射关系，替换模板中 `Block 3` 的数据转换函数。

**替换规则**：
- 每个 Section 通常需要一个 `detailToXxx` 转换函数
- 转换函数处理字段名映射、默认值兜底、数据格式转换
- 保留模板中的通用辅助函数（如 `addon`）

### Step 5：替换 useForm.ts

根据业务逻辑替换模板中 `Block 4` 的表单核心 Hook。

**替换规则**：
- `modelRef`：定义全量表单数据，字段严格遵循 API 接口
- `loadDetail`：根据 ID 加载详情，填充 modelRef
- `submit` / `saveDraft`：提交前过滤不需要的字段
- `formConfig`：计算表单配置（是否编辑、是否首次、标题等）
- 校验函数：各业务的特殊校验逻辑

### Step 6：替换表单容器 index.tsx

根据 PRD 的 Section 划分，替换模板中 `Block 5` 的表单容器。

**替换规则**：
- 用 `computed` 做 modelRef 到各子 Section 数据的双向绑定（get/set）
- 用 `Card` 包裹每个 Section
- 用 `ref` 引用各 Section 实例，用于统一校验
- 支持弹窗(`modal`)和嵌入(`embedded`)两种显示模式
- 暴露 submit、saveDraft、validate 方法

### Step 7：替换各 Section 组件

根据 Step 1 的字段详情，为每个 Section 生成组件（基于 `Block 6` 模板）。

**Section 组件必须遵循**：

1. **Props 模式**：使用 `value` + `update:value`（受控组件）
   ```tsx
   props: { value: Object as PropType<XxxForm>, disabled: Boolean },
   emits: ['update:value'],
   ```

2. **状态管理**：直接读 props.value，不维护本地副本
   ```tsx
   const updateValue = (key, value) => {
     emit('update:value', { ...props.value, [key]: value });
   };
   const updateValues = (values) => {
     emit('update:value', { ...props.value, ...values });
   };
   ```

3. **watch 位置**：所有 watch 必须在 `onMounted` 中调用
   ```tsx
   onMounted(() => {
     watch(() => props.value, val => { ... }, { immediate: true, deep: true });
   });
   ```

4. **双模式控制**：使用 `disabled` prop 统一控制可编辑性
   ```tsx
   <Input value={value.fieldName} disabled={props.disabled} />
   ```

**复杂 Section 可能需要的额外 Hook**：
- 远程数据加载（如分公司/区域联动）→ 抽离到 `useXxx.ts`
- 项目选择弹窗 → 引入 `ProjectSelectModal` + beforeOk 校验
- 省市区选择 → 引入 `MythAreaSelector`

**停下来问用户的场景**：
- Section 字段无法从 PRD/API 明确分组
- 组件选择在 CLAUDE.md 中找不到对应项
- 字段联动规则不明确

## 输出

完成 7 个步骤后，输出以下文件内容，**按文件逐个展示**：

1. `api/types.ts` — 类型定义
2. `api/index.ts` — API 封装
3. `utils/dataTransform.ts` — 数据转换
4. `useForm.ts` — 表单核心逻辑
5. `index.tsx` — 表单容器
6. 各 `components/XxxSection/index.tsx` — Section 组件（按 PRD 分组）
7. 各 `components/XxxSection/useXxx.ts` — Section Hook（如需要）

每个文件输出后，告知用户："以上是 `{文件名}` 的代码，请确认是否正确。"

## 生成后自检

代码生成完成后，执行以下自检，**在输出中明确标注通过/未通过**：

| 检查项 | 检查方式 |
|--------|----------|
| 使用 Form + Row + Col + Form.Item 框架 | 搜索 `<Form` 和 `<Row` |
| rules 使用 computed 或变量定义 | 搜索 `const rules = computed` |
| formRef 校验 + expose 类型声明 | 搜索 `formRef`、`expose` 和 `Ref` 类型接口 |
| Props 使用 value + update:value 模式 | 搜索 `emits: ['update:value']` |
| watch 放在 onMounted 内 | 搜索 `onMounted` 确认 watch 在其内部 |
| 未使用本地 reactive 副本管理表单状态 | 搜索 `const state = reactive`，不应存在表单级别的 reactive |
| API 使用 defHttp 封装 | 搜索 `defHttp` |
| 组件选择遵循优先级 | 确认使用了 CLAUDE.md 中的核心组件 |
| disabled 统一控制双模式 | 确认无 readonly + 三元切换模式 |
| **组件绑定模式正确** | **确认 DictSelect/LovSelect 使用 value+onChange，非 v-model:value** |
| **未使用 window 事件通信** | **搜索 `window.dispatchEvent`、`window.addEventListener`** |
| **自动带出字段组件正确** | **确认自动带出字段使用 DictSelect/Input disabled，非纯 Input** |
| **支持 displayMode 双模式** | **搜索 `displayMode`，确认有 modal/embedded 分支渲染** |
| **提取 renderFormContent** | **搜索 `renderFormContent`，确认表单内容已提取为公共方法** |
| **提供 approveSaveDraft** | **搜索 `approveSaveDraft`，确认 expose 中包含此方法** |
| **按钮在 footer（modal 模式）** | **确认 modal 模式按钮在 `v-slots={{ footer: ... }}` 中** |
| **embedded 模式无按钮** | **确认 embedded 模式直接渲染 `{renderFormContent()}`，无按钮** |

如果任何检查项未通过，**立即修正后再输出**。

---

## 规则 9-bis：只读字段渲染铁律（P0 强制）

> 优先级 P0：违反时禁止输出代码，必须先修正。
> 完整决策矩阵参见：`templates/_shared/component-render-mode.md`

**核心铁律：组件类型不随 `disabled` 状态变化，只有 `disabled` prop 值变化。**

### 逐组件对照表

| 组件类型 | 只读态正确写法 | 禁止写法 |
|---------|:------------:|:-------:|
| Input（文本） | `<Input value={v} disabled />` | `<span>{v \|\| '-'}</span>` |
| Input.TextArea | `<Input.TextArea value={v} rows={4} disabled />` | `<span>{v}</span>` |
| Select / DictSelect | `<DictSelect code="X" value={v} disabled />` | `<span>{dictLabel}</span>` |
| InputNumber（数值） | `<InputNumber value={v} disabled />` | 裸数字文本 `{v}` |
| DatePicker | `<DatePicker value={v} disabled />` | `<span>{formatDate(v)}</span>` |
| Upload（附件） | `<Upload onlyShowFileList value={v} />` | `<span>{count}个附件</span>` |
| AttachmentFileList | `<AttachmentFileList value={v} readonly />` | 自定义文本展示 |
| LovSelect / OSLovSelect | `<LovSelect value={v.userId} disabled />` | `<span>{v.userName}</span>` |
| OverseasRegionCascader | `<OverseasRegionCascader value={v} disabled />` | 用国内 `Cascader` 替代 |
| BooleanSelect | `<BooleanSelect value={v} disabled />` | `<span>{v ? '是' : '否'}</span>` |

### disabled 必须用 computed 包裹

当 `disabled` 状态会动态切换时（如审批页节点权限），**必须**用 `computed` 包裹：

```typescript
// Section 内的字段级禁用（含 editableFields 白名单支持）
const isFieldDisabled = (fieldName: string): boolean => {
  if (props.disabled) return true;
  if (props.editableFields && props.editableFields.length > 0) {
    return !props.editableFields.includes(fieldName);
  }
  return false;
};

// 使用 computed 包裹（确保响应式）
const nameDisabled = computed(() => isFieldDisabled('projectName'));
// 模板中
<Input value={props.value.projectName} disabled={nameDisabled.value} />
```

### 生成后自检追加项（P0）

在现有自检表末尾追加：

| 检查项 | 优先级 | 检查方式 |
|--------|--------|----------|
| Section 内无 `<span>` 字段替换 | **P0** | 在每个 Section 文件中搜索 `<span>`；表格 customRender 中的 `<span>` 是允许的 |
| disabled 组件类型与编辑态一致 | **P0** | 对比 disabled=true 和 disabled=false 分支，组件名不变 |
| disabled 用 computed/isFieldDisabled 包裹 | P1 | 搜索 `isFieldDisabled` 或 `computed(() => props.disabled` |

## 引用文件

- 代码模板 → `references/reference.md`（必须先读取）
- 表单校验模板 → `references/form-validate.md`
- 核心组件表 → 项目 `CLAUDE.md`
- 字段规范 → `references/form-map.md`（按模块查字段）/ `references/form-map2.md`（按字段查组件）
- 命名规范 → `base-naming.md`
- API 规范 → `base-api.md`
- TSX 规范 → `base-tsx.md`
