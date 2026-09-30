# 文件目录结构规范
> 版本：V2.0
> 生效时间：202X-XX-XX
> 适用范围：本时间节点之后新建的所有模块
> 标准参考：`eng-manage` 模块

---

## 一、页面模块标准结构

```
src/views/
├── {module}/                # 业务域根目录（kebab-case，如 eng-manage/pro-manage）
│   ├── hooks/               # 模块级共享 hook（多个子页面共用）
│   ├── components/          # 模块级共享组件
│   └── {page}/              # 子页面目录（kebab-case，如 start-apply/review-list）
│       ├── index.tsx        # 页面入口（只负责渲染）
│       ├── useIndex.ts(.tsx)# 页面主 hook（含 JSX 用 .tsx，纯逻辑用 .ts）
│       ├── style.module.less# 页面级样式
│       ├── api/
│       │   ├── index.ts     # API 接口函数（export function + defHttp）
│       │   ├── types.ts     # 类型定义（入参/出参/表单模型）
│       │   └── config.ts    # 可选：业务枚举常量
│       ├── utils/           # 可选：页面级工具函数
│       │   └── dataTransform.ts
│       ├── hooks/           # 可选：页面级 hook
│       │   └── useXxx.ts
│       └── components/      # 页面级组件
│           ├── {Name}Form/  # 表单组件（PascalCase）
│           │   ├── index.tsx
│           │   ├── useForm.ts
│           │   └── style.module.less
│           ├── {Name}DetailModal/ # 详情弹窗组件
│           │   ├── index.tsx
│           │   ├── useDetail.ts
│           │   └── style.module.less
│           └── {Name}Section/ # Section 区块组件（详情页拆分）
│               ├── index.tsx
│               └── style.module.less
```

### 文件职责说明
| 文件 | 职责 | 禁止 |
|------|------|------|
| `index.tsx` | 页面渲染（JSX 布局），引入 useIndex 导出的变量和方法 | 禁止在 index.tsx 中写业务逻辑 |
| `useIndex.ts` | 页面主逻辑（表格注册、搜索、操作回调、状态管理） | - |
| `api/index.ts` | API 请求函数（defHttp + enum Api） | 禁止在组件中直接调用 defHttp |
| `api/types.ts` | 所有 TypeScript 类型定义（入参、出参、表单模型） | 禁止将类型定义散落在组件文件中 |
| `api/config.ts` | 业务枚举常量（如审批节点枚举） | 仅放枚举/常量，不放逻辑代码 |
| `components/{Name}/useXxx.ts` | 组件核心逻辑 hook | - |

### 简单页面兼容规则
对于无复杂组件的简单页面（如纯配置页），可以省略 `components/` 等目录，但必须保留：
- `index.tsx`
- `useIndex.ts`
- `api/`（如有 API 请求）
- `style.module.less`（如有样式）

---

## 二、四种页面类型对应的文件组织

### 列表页
```
{page}/
├── index.tsx            # BasicTable + 搜索表单布局
├── useIndex.tsx         # registerTable, reload, handleSearch, handleReset, getTableActions
├── style.module.less
└── api/
    ├── index.ts         # get{PageName}List, delete{PageName}, export{PageName}
    └── types.ts         # {PageName}Record, {PageName}Params
```
- 使用 `BasicTable` 组件（禁止直接用 `a-table`）
- `useIndex` 导出 `registerTable` + `reload` + 操作回调
- 表格列定义在 `useIndex.tsx` 中（含 JSX 渲染函数时用 `.tsx`）

### 表单页
```
{page}/components/{Name}Form/
├── index.tsx            # 表单容器（弹窗或嵌入模式）
├── useForm.ts           # 表单核心逻辑（字段定义、校验、提交）
└── style.module.less
```
- 表单字段定义在 `useForm.ts` 中
- 弹窗模式使用 `BasicModal`
- `index.tsx` 只负责渲染表单布局

### 详情页
```
{page}/components/{Name}DetailModal/
├── index.tsx            # 详情容器（锚点导航 + 多 Section 组装）
├── useDetail.ts         # 详情数据加载 hook
├── style.module.less
```
- 复杂详情页拆分为多个 `{Name}Section` 组件
- 使用 `SectionAnchorNav` 锚点导航
- 每个 Section 独立目录：`{Name}Section/index.tsx + style.module.less`

### 审批页
审批页**不在业务模块内**，位于统一的 `office` 目录：
```
src/views/office/todo/components/apply-modal/
├── {business}.tsx       # 审批组件（复用业务模块 DetailModal）
└── approval-form/
    └── {Name}ApprovalForm.tsx # 审批专用表单
```

#### 新增审批页操作流程：
1. 业务模块导出公共 `{Name}DetailModal` 组件
2. 在 `office/todo/components/apply-modal/` 新建业务审批组件，引用上述详情组件
3. 在 `apply-modal/approval-form/` 新建审批专用表单（同意/驳回/意见/附件）
4. 在 `register.tsx` 中添加 `procDef.key` 与审批组件的映射：
   ```typescript
   const map = {
     'XXX_CREATE': 'xxx', // key 为工作流定义标识，value 对应组件名
   }
   ```
5. 通过 `modalType` 属性区分 `approve`（审批操作）和 `approveRecord`（只读查看）

---

## 三、全局 API 目录结构
```
src/api/
├── types/
│   └── index.ts               # 全局共享类型
└── {domain}/                  # 按业务域划分（system/permission/supplier/workFlow 等）
    ├── {feature}.ts           # API 函数文件
    └── types/                 # 可选：该域的共享类型
```

### 全局类型（`src/api/types/index.ts`）
| 类型 | 用途 |
|------|------|
| `NormalResponse<T>` | 通用响应结构 |
| `Page<T>` | 分页列表响应 |
| `Pagination<T>` | 分页参数 |
| `List<T>` | 列表数据 |
| `FileDTO` | 文件信息 |
| `Attachment` | 附件信息 |

### API 文件规范
```typescript
// api/index.ts 标准模板
import { defHttp } from '@/utils/http/axios';
import type { NormalResponse, Page } from '@/api/types';

enum Api {
  Prefix = '/api/pm3/xxx',
}

export function getXxxList(data: XxxParams) {
  return defHttp.post<Page<XxxRecord>>({ url: Api.Prefix + '/list', data });
}
```
- 统一使用 `defHttp`（来自 `@/utils/http/axios`）
- 统一使用 `export function` 导出
- URL 常量用文件内 `enum Api` 管理

---

## 四、待办/已办/审批结构
```
src/views/office/
├── todo/                        # 待办
│   ├── index.tsx                # 待办列表页
│   ├── approval/index.tsx       # 审批操作页（容器）
│   ├── hooks/useTableColumn.ts  # 表格列配置
│   ├── service/api.ts           # 审批相关 API
│   └── components/
│       ├── register.tsx         # 动态组件分发器
│       ├── apply-modal/         # 各业务审批组件
│       │   ├── index.tsx        # 通用审批模板
│       │   ├── {business}.tsx   # 具体业务审批组件
│       │   └── approval-form/   # 审批专用表单
│       │       └── {Name}ApprovalForm.tsx
│       ├── approval-record/     # 审批记录展示
│       │   ├── index.tsx
│       │   └── components/
│       │       ├── approvalRecordTable.tsx
│       │       └── approval-track.tsx
│       ├── forward-modal/       # 转发弹窗
│       └── view-modal/          # 已阅弹窗
├── done/                        # 已办
│   ├── index.tsx                # 已办列表页
│   ├── detail/index.tsx         # 已办详情页
│   ├── hooks/useTableColumn.ts
│   ├── service/api.ts
│   └── interface/               # 类型定义
│       └── doneInterface.ts
└── launch/                      # 我发起的
    ├── index.tsx                # 发起列表页
    ├── detail/index.tsx         # 发起详情页
    ├── hooks/useTableColumn.ts
    └── service/api.ts
```

### 核心机制
1. **动态分发**：`register.tsx` 通过 `procDef.key` 映射表（如 `{ 'KFQ_CREATE': 'dev' }`）动态加载 `apply-modal/` 下对应组件
2. **模式区分**：通过 `modalType` 属性区分 `'approve'`（审批操作）和 `'approveRecord'`（只读查看）
3. **组件复用**：审批组件引用业务模块的详情组件（方向：`office → 业务模块`），不反向引用
4. **权限控制**：通过 `getOperationRole` 接口获取 `templateKey`，决定显示哪些操作按钮

---

## 五、关键规则
- `index.tsx` 只负责渲染，逻辑在 `useIndex.ts` 中
- API 统一用 `api/` 目录（新模块），旧模块保持 `service/` 不强制迁移
- 组件目录用 **PascalCase**（如 `StartApplyForm/`），内含 `index.tsx` + hook + `style.module.less`
- 样式文件统一用 `style.module.less`
- 新代码禁止 `.vue` 和 `.tsx` 混用
- `hooks/` 用于模块级共享 hook，组件级 hook 放在组件目录内
- **例外规则**：特殊场景确实需要打破规范时，必须在代码评审时说明理由并获得批准

---

## FAQ 常见问题
| 问题 | 答案 |
|------|------|
| 简单页面没有子组件，是否可以省略 `components/`？ | 可以，只保留核心文件即可 |
| 多个子页面共享的组件放在哪里？ | 模块根目录下的 `components/`，多个模块共享的放在全局 `@/components/` |
| `types.ts` 中的类型需要全部导出吗？ | 是的，方便其他模块引用 |
| 工具函数什么时候放在模块级 `utils/`，什么时候放在全局 `@/utils/`？ | 仅本模块使用放模块级，多模块共用放全局 |
| 用 `/scene-form` 等 skill 生成的代码不符合规范怎么办？ | 以本规范为准，生成后调整不符合部分 |
| 审批页需要修改业务详情展示怎么办？ | 先修改业务模块的 `DetailModal` 组件，再更新审批页的引用 |
