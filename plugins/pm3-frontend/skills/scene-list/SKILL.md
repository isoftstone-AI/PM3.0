---
name: scene-list
description: 列表页代码生成器。根据 PRD 文档、API 文档和设计稿，基于实际上线代码模板生成完整的列表页代码（index.tsx + useIndex.tsx + api/）。当用户说"开发列表页"、"生成列表页"、"新建列表页"、"列表页"时触发。也适用于用户提供了 PRD + API 文档并要求生成带有搜索+表格+分页的页面场景。即使用户没有明确说"列表页"，只要需求包含搜索条件、表格展示、分页查询的组合特征，就应该使用此 skill。
category: code-generation
tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
version: 1.0.0
---

# 列表页代码生成器

根据 PRD 文档、API 文档和设计稿，生成可直接使用的列表页代码。

## 核心原则

模板不是让你照抄的——它是骨架。你的工作是**按步骤替换骨架中的业务内容**，保持框架不动。

## 强制规则（违反即失败）

以下规则**不可被开发方案中的字段级代码示例覆盖**。当开发方案的字段示例与这些规则冲突时，**以本规则为准**，开发方案只提供字段属性和业务逻辑。

1. **api 参数传递**：`useTable.api` 中使用 `form.getData()` 获取搜索参数，与 `pageParams` 合并后传给 API 函数。**禁止手动 `getForm().getFieldsValue()` 逐字段取值**。
2. **index.tsx 布局**：必须使用 `BasicTable` 的 `tableTitle` slot 放置操作按钮和导出按钮。**禁止用 `div` 包裹 BasicTable**，禁止用 `styles.container` 外层包裹。
3. **操作列渲染**：使用 `bodyCell` slot + `TableAction` 组件渲染操作按钮。**禁止在 columns 中用 `customRender` 渲染操作列**。
4. **Modal 显隐**：使用 `open` prop（Ant Design Vue 4 规范）。**禁止使用 `visible`**。
5. **HTTP 方法**：列表查询一律使用 `defHttp.post` + `data`。**禁止使用 `defHttp.get` + `params` 做列表查询**。
6. **API 前缀**：必须从开发方案的「全局接口清单」中读取 `Api.Prefix`，**禁止猜测或编造前缀路径**。
7. **请求参数中的用户/组织引用**：提交参数只传 ID（string 或 string[]），**禁止传完整 UserInfo 对象**。响应数据中的用户字段才返回完整对象。
8. **组件导入路径**：严格使用 CLAUDE.md 核心组件表中的路径。特别注意：
   - `Upload` → `@/components/Upload/Upload.vue`
   - `Input.TextArea` → 从 `ant-design-vue` 导入 `Input`，使用 `Input.TextArea`（禁止独立导入 `TextArea`）
   - `AttachmentFileList` → `@/components/AttachmentFileList`（只读附件展示用此组件，禁止自定义文本展示）
9. **审批页组件 expose**：所有可被审批页引用的组件，必须通过 `ctx.expose` 暴露 `getData()` 和 `validate()` 方法。
10. **搜索表单**：使用 `formConfig.schemas` 配置驱动，**禁止手动管理搜索表单状态**。联动逻辑通过 `componentProps` 的函数形式 + `formModel` 实现。
11. **模板优先级**：当开发方案中的字段级代码示例与 `references/reference.md` 模板结构冲突时，**以模板结构为准**，只从开发方案中提取字段属性（field、label、component、dictCode 等）和业务逻辑。

## 执行前准备

1. 读取 `references/reference.md` 获取完整代码模板
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
| 表格展示字段 | 替换 columns | SAP项目编码、项目名称、项目业态... |
| 查询条件 | 替换 formConfig.schemas | 项目名称(输入)、项目业态(选择)... |
| 操作按钮规则 | 替换 getTableActions 逻辑 | 草稿→编辑/删除，审批完成→二次申请 |
| 状态枚举 | 替换审批状态选项 | 0=草稿, 1=审批中, 2=通过, 3=驳回 |
| 业务术语 | 按钮文案、页面标题 | "开工成果审批" 而非 "新增" |

**输出**：整理成表格展示给用户确认，格式：

```
## 表格字段
| 字段名 | 中文名 | 宽度建议 |
|--------|--------|----------|

## 查询条件
| 字段名 | 中文名 | 组件类型 |
|--------|--------|----------|

## 操作按钮规则
| 状态 | 可用操作 |
|------|----------|
```

### Step 2：替换 columns

根据 Step 1 提取的表格字段，替换模板中 `useIndex.tsx` 的 `columns` 数组。

**替换规则**：
- `title` → PRD 中的中文名
- `dataIndex` → API 返回字段名（从 API 文档获取）
- `width` → 根据字段类型估算：短文本 100-120，中文字 140-160，长文本用 `ellipsis: true`
- 保留模板中的 `actionColumn` 配置（操作列由 getTableActions 动态生成）
- 保留模板中的 `showIndexColumn: true`（序号列）

**特殊列处理**：
- 状态列：需要在 `bodyCell` 中自定义渲染，模板已内置
- 操作列：由 `getTableActions` 动态生成，不需要在 columns 中定义
- 时间列：统一 width: 170

### Step 3：替换 API

根据 API 文档，替换模板中的 3 个 API 文件。

**api/types.ts 替换**：
- 删除 start-apply 的业务类型（如 `StartApplyRecord`、`StartApplySearchParams` 等）
- 根据 API 文档定义新的 Record、SearchParams、ExportParams 等类型
- 保留模板中的通用工具类型

**api/index.ts 替换**：
- 替换 `Api.Prefix` 为实际接口前缀（格式：`/api/pm3/模块名`）
- 替换 API 函数：至少包含 `getList`（分页查询）、`deleteDraft`（删除）、`exportList`（导出）
- 所有函数使用 `defHttp` 封装，入参出参类型明确

**useIndex.tsx 中 api 参数映射**：
```typescript
// useTable 的 pageParams 与后端参数映射
const [registerTable, { reload, getForm }] = useTable({
  api: async (pageParams) => {
    const form = getForm();
    let searchParams = {};
    if (form) {
      searchParams = form.getData();   // 自动获取所有搜索表单字段
    }
    const res = await getList({
      current: pageParams.page,       // pageParams.page → 后端 current
      size: pageParams.pageSize,      // pageParams.pageSize → 后端 size
      ...searchParams,                // 搜索参数自动合并
    });
    // 直接返回，由 BasicTable 内部自动从 res.data 中提取 records 和 total
    return res;
  },
});
```

**注意**：
- 不同后端接口的分页参数名可能不同（pageNum/current、pageSize/size），需要根据实际 API 文档调整映射。
- **禁止手动 `getForm().getFieldsValue()` 逐字段取值**，使用 `form.getData()` 一次性获取。

**搜索参数转换规则**（在 `api` 回调中处理）：

```typescript
api: async (pageParams) => {
  const searchParams: Record<string, any> = {};

  // 1. 分页字段映射（根据后端实际字段名调整）
  if (pageParams.pageNo !== undefined) {
    searchParams.pageNum = pageParams.pageNo;   // pageNo → pageNum
  }
  if (pageParams.limit !== undefined) {
    searchParams.pageSize = pageParams.limit;   // limit → pageSize
  }

  // 2. 日期范围字段拆分（RangePicker 返回 [start, end] 数组）
  if (pageParams.applyTime && Array.isArray(pageParams.applyTime)) {
    searchParams.applyTimeStart = pageParams.applyTime[0];
    searchParams.applyTimeEnd = pageParams.applyTime[1];
  }

  // 3. 多选字段转字符串（DictSelect mode="multiple" 返回 string[]）
  if (pageParams.majors && Array.isArray(pageParams.majors)) {
    searchParams.majors = pageParams.majors.join(',');
  }

  // 4. 其他普通字段直接透传（过滤空值）
  ['keyword', 'approvalStatus', 'companyId'].forEach((key) => {
    if (pageParams[key] !== undefined && pageParams[key] !== null && pageParams[key] !== '') {
      searchParams[key] = pageParams[key];
    }
  });

  const res = await getList(searchParams);
  // 直接返回，由 BasicTable 内部自动从 res.data 中提取 records 和 total
  return res;
},
```

**关键转换点**：
| 场景 | 处理方式 | 示例 |
|------|---------|------|
| 分页字段映射 | `pageParams.pageNo` → `pageNum`，`pageParams.limit` → `pageSize` | 根据后端字段名调整 |
| 日期范围拆分 | `RangePicker` 返回数组 → 拆分为 `xxxStart`/`xxxEnd` | `applyTime: [start, end]` → `applyTimeStart`, `applyTimeEnd` |
| 多选转字符串 | `string[]` → `join(',')` | `majors: ['1','2']` → `majors: '1,2'` |
| 空值过滤 | 跳过 `undefined`/`null`/`''` | 避免传空字符串给后端 |

### Step 4：替换 searchForm（查询表单）

根据 Step 1 提取的查询条件，替换模板中 `useIndex.tsx` 的 `formConfig.schemas`。
**特别注意** formConfig 中要求 showAdvancedSearch: false， autoAdvancedLine: 3， useSearchForm: true, showIndexColumn: true,默认不启用高级查询，默认只展示两行
**组件选择优先级**（从高到低）：

| 优先级 | 来源 | 适用场景 |
|--------|------|----------|
| 1 | CLAUDE.md 核心组件表 | DictSelect、UserSelect、OrgSelect 等项目封装组件 |
| 2 | ant-design-vue 基础组件 | Input、Select、DatePicker、RangePicker |
| 3 | AskUserQuestion | 以上都找不到合适的，停下来问用户 |

**常见字段与组件映射**：

| 查询字段特征 | 推荐组件 | 配置示例 |
|-------------|----------|----------|
| 自由文本输入 | `Input` | `component: 'Input', componentProps: { placeholder: '请输入', allowClear: true }` |
| 固定选项（3-8个） | `Select` | `component: 'Select', componentProps: { options: [...], allowClear: true }` |
| 字典选项 | `DictSelect` | `component: 'DictSelect'`（需确认字典编码） |
| 组织选择 | `OrgSelect` | `component: 'OrgSelect'` |
| 人员选择 | `LovSelect` | `component: 'LovSelect'` |
| 时间范围 | `RangePicker` | `component: 'RangePicker'` |
| 多选字典 | `DictSelect` + `mode: 'multiple'` | `component: 'DictSelect', componentProps: { mode: 'multiple', code: 'xxx' }` |
| 是否类 | `BooleanSelect` | `component: 'BooleanSelect'` |

**schema 配置模板**：
```typescript
{
  field: 'fieldName',          // API 字段名
  label: '中文名',              // PRD 中的显示名
  component: 'Input',          // 组件名
  colProps: { span: 6 },       // 默认每行 4 个
  componentProps: {
    placeholder: '请输入',
    allowClear: true,
  },
}
```

**停下来问用户的场景**：
- 查询条件在 CLAUDE.md 核心组件表中找不到对应组件
- PRD 中某个查询条件的含义不明确
- API 文档字段名与 PRD 描述不匹配

## 输出

完成 4 个步骤后，输出以下文件内容，**按文件逐个展示**：

1. `api/types.ts` — 类型定义
2. `api/index.ts` — API 封装
3. `useIndex.tsx` — 表格逻辑
4. `index.tsx` — 页面入口

每个文件输出后，告知用户："以上是 `{文件名}` 的代码，请确认是否正确。"

## 生成后自检

代码生成完成后，执行以下自检，**在输出中明确标注通过/未通过**：

| 检查项 | 检查方式 |
|--------|----------|
| 未使用原生 `Table` | 搜索 `from 'ant-design-vue'` 导入中是否包含 `Table` |
| 未使用 `Card` 包裹 | 搜索 `<Card` |
| 使用了 `BasicTable` | 搜索 `BasicTable` |
| 使用了 `InnerLayout` | 搜索 `InnerLayout` |
| 搜索表单用 schemas 配置 | 搜索 `formConfig` 和 `schemas` |
| 未手动管理 loading/pagination | 搜索 `const loading = ref`、`const pagination = ref` |
| API 使用 defHttp 封装 | 搜索 `defHttp` |
| useTable 配置完整 | 确认有 `api`、`columns`、`formConfig` |
| 分页默认 pageSize=20 | 确认分页配置 |
| **状态列渲染检查** | **确认所有状态字段都有 bodyCell 渲染逻辑** |
| **搜索参数转换** | **确认日期范围已拆分、多选已转字符串、分页字段已映射** |

如果任何检查项未通过，**立即修正后再输出**。

---

## 规则 12-14：表格列渲染规则（P1）

> 完整决策矩阵参见：`templates/_shared/component-render-mode.md`

### 规则 12：字典字段列必须使用 DictLabel

表格列中的字典字段，必须用 `<DictLabel>` 渲染纯文本，**禁止用 `<DictSelect>`**（后者有下拉交互，不适合列表展示）。

```tsx
// ✅ 正确
{
  title: '审批状态',
  dataIndex: 'approvalStatus',
  customRender: ({ text }) => <DictLabel code="approval_status" value={text} />,
}

// ❌ 错误
{
  title: '审批状态',
  dataIndex: 'approvalStatus',
  customRender: ({ text }) => <DictSelect code="approval_status" value={text} disabled />,
}
```

**导入**：`import DictLabel from '@/components/DictLabel'`（与 DictSelect 同目录）。

### 规则 13：数值字段列必须格式化

表格列中的数值字段，**禁止直接渲染裸数字**，必须用 `formThousands` 工具函数格式化：

```tsx
// ✅ 正确（千分位 + 2位小数）
{
  title: '毛利额（万元）',
  dataIndex: 'grossProfit',
  customRender: ({ text }) => <span>{formThousands(text, { decimal: 2 })}</span>,
}

// ❌ 错误
{
  title: '毛利额（万元）',
  dataIndex: 'grossProfit',
}
// 直接显示原始数字，无格式化
```

**导入**：`import { formThousands } from '@/directives/formThousands'`（或项目实际路径，搜索 `formThousands` 确认）。

### 规则 14：容量/规模单位动态读取

列表列中显示容量单位（MW / MWp）时，必须根据 `record` 中的业态字段动态计算，**禁止硬编码**：

```tsx
// ✅ 正确（业态 2=光伏/5=光储 → MWp，其他 → MW）
{
  title: '批复容量',
  dataIndex: 'approvedCapacity',
  customRender: ({ text, record }) => {
    const unit = [2, 5].includes(record.stadiumNumber) ? 'MWp' : 'MW';
    return <span>{formThousands(text, { decimal: 2 })} {unit}</span>;
  },
}

// ❌ 错误（硬编码单位）
{
  title: '批复容量',
  dataIndex: 'approvedCapacity',
  customRender: ({ text }) => <span>{text} MW</span>,
}
```

### 生成后自检追加项（P1）

在现有自检表末尾追加：

| 检查项 | 优先级 | 检查方式 |
|--------|--------|----------|
| 字典列用 DictLabel（非 DictSelect） | P1 | 搜索 columns 中 `DictSelect`，应为 0 |
| 数值列有 formThousands 格式化 | P1 | 搜索 `customRender` 中是否包含 `formThousands` |
| 容量单位动态读取（非硬编码） | P1 | 搜索 `'MW'`，确认无硬编码字符串 |

## 引用文件

- 代码模板 → `references/reference.md`（必须先读取）
- 核心组件表 → 项目 `CLAUDE.md`
- 字段规范 → `form-map.md` / `form-map2.md`
- 命名规范 → `base-naming.md`
- API 规范 → `base-api.md`
