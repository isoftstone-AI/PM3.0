# 组件渲染模式决策表

> 本文档为所有 Skill（scene-list / scene-form / scene-detail / scene-approval）的共享参考。
> 当某字段需要在不同页面出现时，按以下决策表选择渲染组件，**不得自行推断**。

## 三场景决策矩阵

| 字段类型 | 列表表格列 | 表单编辑态 | 详情/只读态 |
|---------|:----------:|:---------:|:---------:|
| 字典字段 | `<DictLabel code="X" value={text} />` | `<DictSelect code="X" value={v} onChange={...} />` | `<DictSelect code="X" value={v} disabled />` |
| 数值字段（普通） | `{formThousands(text, {decimal:2})}` | `<InputNumber value={v} onChange={...} />` | `<InputNumber value={v} disabled />` |
| 数值字段（大额/千分位） | `{formThousands(text, {decimal:2})}` | `<InputNumber v-formThousands={[state, {intLength:8, decimal:2, key:'f'}]} />` | `<InputNumber value={v} disabled />` |
| 用户字段 | 姓名文本 `{record.userName}` | `<LovSelect value={v.userId} onChange={...} />` | `<LovSelect value={v.userId} disabled />` |
| 附件字段 | 附件数量文本 `{count}个附件` | `<Upload v-model={value.files} />` | `<AttachmentFileList value={v} readonly />` |
| 地区字段（海外） | 地区文本 `{record.regionName}` | `<OverseasRegionCascader value={v} onChange={...} />` | `<OverseasRegionCascader value={v} disabled />` |
| 时间字段 | 格式化文本 `{formatDate(text)}` | `<DatePicker value={v} valueFormat="YYYY-MM-DD" onChange={...} />` | `<DatePicker value={v} disabled />` |
| 文本字段（短） | 原始文本 `{text \|\| '-'}` | `<Input value={v} onChange={...} />` | `<Input value={v} disabled />` |
| 文本字段（长/TextArea） | 截断文本 + ellipsis | `<Input.TextArea value={v} rows={4} onChange={...} />` | `<Input.TextArea value={v} rows={4} disabled />` |
| 是/否字段 | `{v === 1 ? '是' : '否'}` | `<BooleanSelect value={v} onChange={...} />` | `<BooleanSelect value={v} disabled />` |

## 铁律

1. **列表列禁止使用 DictSelect**：表格列字典字段必须用 `DictLabel`，渲染只读文本，无下拉行为。
2. **只读态禁止替换组件类型**：`disabled` 不改变组件类型，只改变 `disabled` prop 值。`<Input disabled />` 不可替换为 `<span>{v}</span>`。
3. **列表列数值必须格式化**：裸数字 `{123456.78}` 不可直接渲染，必须经过 `formThousands` 处理。
4. **单位动态读取**：列表列单位从 `record.stadiumNumber`（或等价字段）动态判断（如 `1/2=MW`, `其他=MWp`），禁止硬编码 `MW`。

## 海外专属组件映射

> 海外业务模块（路径含 `overseas/`）必须使用以下替换，**禁止使用国内版本**：

| 国内组件 | 海外替换 | 说明 |
|---------|---------|------|
| `Cascader`（省市区） | `OverseasRegionCascader` | 导入：`@/components/OverseasRegionCascader` |
| `LovSelect`（用户选择） | `OSLovSelect` | 导入：`@/components/OSLovSelect` |

## 特殊工具函数

| 函数 | 来源 | 用途 |
|------|------|------|
| `formThousands(val, opts)` | `@/directives/formThousands` | 格式化大数字（千分位+精度），用于表格列渲染 |
| `formatDate(val, fmt?)` | `@/utils/dateUtil` | 格式化日期字符串，默认 `YYYY-MM-DD` |
| `getChineseText(i18nVal)` | `@/utils/i18nUtil` | 从 I18nInput 值提取中文 |
| `getEnglishText(i18nVal)` | `@/utils/i18nUtil` | 从 I18nInput 值提取英文 |
