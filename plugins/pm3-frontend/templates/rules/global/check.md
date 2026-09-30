
# 提交前检查清单

> 代码提交前逐项确认

---

## 一、Git 提交规范

### 提交格式
```
<type>：(<scope>): <subject>
```

### Type 类型

| 类型 | 说明 | 示例 |
|-----|------|------|
| `feat` | 新功能 | `feat：(施工组织评审): 新增变更重提功能` |
| `fix` | Bug 修复 | `fix：(表格): 修复分页失效问题` |
| `docs` | 文档更新 | `docs：(README): 更新部署说明` |
| `style` | 代码格式 | `style：(表单): 调整按钮间距` |
| `refactor` | 重构 | `refactor：(审批页): 优化数据加载逻辑` |

### 检查项

- [ ] 提交类型正确
- [ ] 模块名准确
- [ ] 描述简洁（不超过 50 字）

---

## 二、组件使用检查

### 推荐组件 ✅

| 组件 | 路径 | 用途 |
|-----|------|------|
| BasicTable | `@/components/BasicTable` | 表格 |
| DictSelect | `@/components/DictSelect` | 字典选择 |
| UserSelect | `@/components/UserSelect` | 用户选择 |
| OrgSelect | `@/components/OrgSelect` | 组织选择 |
| Upload | `@/components/Upload` | 文件上传 |
| FileCard | `@/components/FileCard` | 文件卡片 |

### 废弃组件 ℹ️（请用 ant-design-vue 替换）

| 废弃 | 替换为 |
|-----|--------|
| MythInput | `a-input` |
| MythSelect | `a-select` |
| MythDatePicker | `a-date-picker` |
| MythButton | `a-button` |

### 禁止组件 ❌（绝对禁止使用）

| 组件 | 原因 |
|-----|------|
| Form/BasicForm/useForm | 表单逻辑复杂，建议用社区方案 |
| Button/BasicButton | 维护不足 |
| Tree/BasicLeftTree | 功能冗余 |
| Drawer/BasicDrawer | 维护不足 |

---

## 三、代码规范检查

### TSX 规范

- [ ] 使用 `defineComponent` 定义组件
- [ ] 定义 `name` 属性（PascalCase）
- [ ] `setup()` 返回渲染函数
- [ ] 未使用 `render()` 函数
- [ ] 未在 TSX 中使用 `this`
- [ ] 未在 `defineComponent` 中写 `components` 配置
- [ ] `watch` 在 `onMounted` 中调用（禁止在 setup 中直接调用）

### 命名规范

- [ ] 目录 kebab-case（如 `construct-review`）
- [ ] 组件 PascalCase（如 `ConstructReviewList`）
- [ ] 文件 kebab-case（如 `index.tsx`）
- [ ] 函数 camelCase（如 `handleSubmit`）
- [ ] 布尔值 is/has/can 前缀（如 `isLoading`）
- [ ] Ref 变量 Ref 后缀（如 `tableRef`）

### 样式规范

- [ ] 优先使用 Tailwind
- [ ] 组件私有样式用 CSS Module
- [ ] 全局变量用 Less
- [ ] 动态计算值用内联 styles（极少用）

---

## 四、API 规范检查

- [ ] 使用 `defHttp` 封装请求
- [ ] 定义明确的入参类型
- [ ] 定义明确的出参类型
- [ ] 使用 `NormalResponse<T>` / `Page<T>` / `Pagination<T>`
- [ ] 错误处理完善

---

## 五、文件结构检查

> 详细目录结构规范见 `rules/global/directory-structure.md`

```
src/views/{module}/{page}/
├── index.tsx              # ✅ 页面入口（只负责渲染）
├── useIndex.ts            # ✅ 页面主 hook（含 JSX 用 .tsx）
├── style.module.less      # ✅ 页面级样式
├── api/
│   ├── index.ts           # ✅ API 接口函数
│   ├── types.ts           # ✅ 类型定义
│   └── config.ts          # 可选：业务枚举常量
├── utils/                 # 可选：工具函数
├── hooks/                 # 可选：模块级共享 hook
└── components/            # ✅ 组件目录（PascalCase）
    ├── {Name}Form/        # ✅ 表单组件
    │   ├── index.tsx
    │   ├── useForm.ts     # 表单逻辑 hook
    │   └── style.module.less
    ├── {Name}DetailModal/ # 详情弹窗
    │   ├── index.tsx
    │   ├── useDetail.ts
    │   └── style.module.less
    └── {Name}Section/     # Section 区块
        ├── index.tsx
        └── style.module.less
```

- [ ] 目录结构符合规范（参见 `directory-structure.md`）
- [ ] `index.tsx` 只负责渲染，逻辑在 `useIndex.ts` 中
- [ ] API 放在 `api/` 目录（`index.ts` + `types.ts`）
- [ ] 组件目录使用 PascalCase 命名
- [ ] 组件内含 `index.tsx` + hook + `style.module.less`
- [ ] 文件命名符合规范
- [ ] 样式文件统一使用 `style.module.less`
