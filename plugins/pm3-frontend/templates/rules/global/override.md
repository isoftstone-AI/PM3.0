---
paths:
  - "src/**/*.tsx"
  - "src/**/*.ts"
---
# 项目特殊规则（PM 3.0）

> 以下规则覆盖中央规则库的通用规范

---

## 命名覆盖

| 规则 | 通用规范 | 本项目覆盖 |
|-----|---------|-----------|
| 列表页组件后缀 | `List` 或 `Index` | **必须为 `List`**（如 `ProjectList`） |
| 详情页组件后缀 | `Detail` 或 `View` | **必须为 `Detail`**（如 `ProjectDetail`） |
| 表单页组件后缀 | `Form` | 保持 `Form`（如 `ProjectForm`） |
| 审批页组件后缀 | - | **必须为 `Approval`**（如 `ProjectApproval`） |

## API 覆盖

| 规则 | 通用规范 | 本项目覆盖 |
|-----|---------|-----------|
| API 前缀 | `/api/xxx` | **统一为 `/api/pm3`** |

## 表格覆盖

| 规则 | 通用规范 | 本项目覆盖 |
|-----|---------|-----------|
| 默认 pageSize | 10 | **20** |
| 分页选项 | [10, 20, 50, 100] | **[20, 50, 100]** |

## 权限编码覆盖

| 规则 | 通用规范 | 本项目覆盖 |
|-----|---------|-----------|
| 权限前缀 | 无要求 | **统一加模块前缀**（如 `construct-review:add`） |

## 路由覆盖

| 规则 | 通用规范 | 本项目覆盖 |
|-----|---------|-----------|
| 路由路径 | kebab-case | **模块前缀 + 功能**（如 `/pm-engineering/construct-review/list`） |

---

## 快速参考

```typescript
// 组件命名示例
export default defineComponent({
  name: 'ConstructReviewList',     // ✅ 列表页
  // name: 'ConstructReviewDetail', // ✅ 详情页
  // name: 'ConstructReviewForm',   // ✅ 表单页
  // name: 'ConstructReviewApproval', // ✅ 审批页
});

// API 前缀示例
export enum Api {
  Prefix = '/api/pm3/construct-review', // ✅
}

// 表格分页示例
const [registerTable] = useTable({
  pagination: {
    pageSize: 20, // ✅ 默认 20
    pageSizeOptions: ['20', '50', '100'], // ✅ 选项
  },
});
```
