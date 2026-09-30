
# 命名规范

---

## 文件命名

| 类型 | 规则 | 示例 |
|-----|------|------|
| 页面目录 | kebab-case | `construct-review/` |
| 组件目录 | PascalCase | `BaseInfoForm/` |
| 页面文件 | kebab-case | `index.tsx` |
| 类型文件 | kebab-case | `types.ts` |
| 样式文件 | name.module.less | `style.module.less` |

## 变量命名

| 类型 | 规则 | 示例 |
|-----|------|------|
| 组件名 | PascalCase | `ConstructReviewList` |
| 函数/方法 | camelCase | `handleSubmit` |
| 常量 | UPPER_SNAKE_CASE | `MAX_PAGE_SIZE` |
| 布尔值 | is/has/can 前缀 | `isLoading` |
| Ref 变量 | Ref 后缀 | `tableRef` |
| 弹框开关 | open 前缀 | `openModal` |

## 组件名后缀（本项目覆盖）

| 页面类型 | 后缀 | 示例 |
|---------|------|------|
| 列表页 | `List` | `ConstructReviewList` |
| 表单页 | `Form` | `ConstructReviewForm` |
| 详情页 | `Detail` | `ConstructReviewDetail` |
| 审批页 | `Approval` | `ConstructReviewApproval` |

## 接口/类型命名

| 类型 | 规则 | 示例 |
|-----|------|------|
| API 记录 | {业务名}Record | `ReviewRecord` |
| API 参数 | {业务名}Params | `ReviewParams` |
| 表单模型 | {业务名}Model | `ReviewFormModel` |
| 组件暴露 | {组件名}Expose | `BaseInfoFormExpose` |
