---
name: generate-api
description: 前端 API 代码生成器。根据 Apifox MCP 或 MD 接口文档，自动生成符合项目规范的 types.ts 和 index.ts。当用户提到"生成API"、"生成接口代码"、"根据文档生成API"、"Apifox生成代码"、"接口文档转代码"时触发。即使用户只是提到需要创建 API 文件、封装接口、写接口类型，也应考虑使用此 skill。
arguments: source, scope, target
argument-hint: <apifox|md:文件路径> [scope=all] <输出目录路径>
---

# 前端 API 代码生成器

根据接口文档（Apifox MCP 或 MD 文件）自动生成前端 API 代码（types.ts + index.ts）。

## 参数解析

用户可通过两种方式提供参数：
1. **命令行参数**：`/generate-api apifox all views/eng-manage/start-apply/api`
2. **自然语言描述**：在对话中说明需求，由 skill 从上下文推断

当命令行参数存在时，按位置解析：`$source`、`$scope`、`$target`。当通过自然语言描述时，按以下规则提取：

| 参数 | 必填 | 说明 | 示例 |
|------|------|------|------|
| source | 是 | 接口文档来源 | `apifox` 或 `md:/path/to/doc.md` |
| scope | 否 | 生成范围，默认 `all` | `all` 或接口名称列表 |
| target | 是 | 输出目录 | `views/eng-manage/xxx/api` |

### 参数识别规则

1. **source**：
   - 用户提到 "apifox"、"MCP" → `apifox`
   - 用户提供了文件路径（.md / .yaml / .json）→ `md:文件路径`
   - 都没提到 → 询问用户

2. **scope**：
   - 用户说"全部"、"所有" → `all`
   - 用户指定了接口名 → 具体列表
   - 没提到 → 默认 `all`

3. **target**：
   - 用户明确给了路径 → 直接使用
   - 用户只说了模块名（如"开工申请"）→ 推断为 `views/eng-manage/{kebab-case}/api`
   - 如果只声明了副文件目录，则在副文件的 `api/` 子目录下创建

### 接口筛选规则

当 scope 不是 `all` 时，按以下优先级匹配：
1. **路径匹配**：接口路径包含 scope 关键词（如 `preproject` 匹配 `/api/pm-oversea/preprojectApplication/*`）
2. **summary 匹配**：接口 summary 包含 scope 关键词（如"预立项"匹配所有 summary 含"预立项"的接口）
3. **标签匹配**：接口 tags 包含 scope 关键词

匹配后展示给用户确认：
```
找到 N 个匹配接口：
1. POST /api/pm-oversea/preprojectApplication/pageList - 分页查询预立项列表
2. GET /api/pm-oversea/preprojectApplication/detail/{id} - 获取预立项详情
...
确认生成这些接口？
```

## 执行流程

### 第一步：读取接口文档

根据 source 参数获取接口定义：

#### apifox（Apifox MCP）

分两步读取：

**1. 读取 OpenAPI Spec 总览**，使用 MCP 工具 `read_project_oas` 获取 paths 列表。总览中每个 path 含有 `$ref` 指向详细定义。

**2. 按 `$ref` 批量读取接口详情**，使用 MCP 工具 `read_project_oas_ref_resources`，传入 `$ref` 路径数组，一次性获取多个接口的完整定义。

```json
// 示例：读取列表、详情、新增三个接口
{ "path": [
  "/paths/_api_pm-development_pmDevQuotaProjectMain_list.json",
  "/paths/_api_pm-development_pmDevQuotaProjectMain_detail.json",
  "/paths/_api_pm-development_pmDevQuotaProjectMain_add.json"
]}
```

**提取规则**：
- OpenAPI Spec 的 `paths` 中的 `$ref` 值就是文件路径，直接传入即可
- 根据用户指定的 scope（all 或部分），筛选需要读取的 `$ref` 路径
- 如果 scope 是部分生成，根据接口路径或 summary 筛选匹配的接口

**3. 读取组件 schemas**，从接口详情中提取所有 `$ref` 指向 `components/schemas` 的引用：

a. 扫描已获取的接口详情，收集所有 `#/components/schemas/XXX` 引用
b. 使用 MCP 工具 `read_project_oas_ref_resources` 读取这些 schema 定义：
```json
{ "path": ["/components/schemas/PreProjectParam.json", "/components/schemas/PreProjectApplicationQueryParam.json"] }
```
c. 如果 schema 中还有嵌套 `$ref`，递归读取直到所有类型都有完整定义（递归上限 5 层）
d. 将 schema 字段映射为 TypeScript 类型定义的依据

#### md 文件

读取用户指定的 MD/YAML/JSON 文件，解析接口信息。支持：
- Swagger YAML/JSON 导出文件
- Markdown 格式接口文档（需包含路径、方法、参数、响应）

### 第二步：提取接口信息

从文档中提取每个接口的：
- HTTP 方法（GET/POST/PUT/DELETE）
- 请求路径
- 请求参数（query / path / body）
- 响应结构（优先从 response example 提取字段，比 $ref schema 更可靠）
- 接口描述（从 summary / description 提取）

**字段注释来源**：OpenAPI Spec 中每个 parameter 的 `description` 字段就是中文注释的来源，直接映射为 `/** 注释 */`。

**字段注释兜底规则**（按优先级）：
1. 优先使用 OpenAPI 的 `description` 字段
2. 如果 description 为空，使用字段名的 camelCase 转中文（如 `projectName` → `/** 项目名称 */`）
3. 如果无法推断，使用 `/** {fieldName} */` 并标记 `// TODO: 补充注释`
4. 对于枚举值，从 schema 的 `enum` + `description` 或 `x-enum-comments` 提取选项说明

### 第 2.5 步：判断类型依赖

检查项目是否已有全局类型定义：
1. 读取 `src/api/types/index.ts`
2. 如果存在 `ApiResponse`/`PageResponse`/`Attachment` 等通用类型：
   - types.ts 中**不重复定义**，改为 `import type { ApiResponse, PageResponse } from '@/api/types'`
   - 记录可用的全局类型列表，后续生成时直接引用
3. 如果项目没有全局类型，则在 types.ts 本地定义（参考 `references/reference.md`）

### 第三步：生成 types.ts

按照 `references/reference.md` 中的规范生成类型文件。核心规则：

#### 类型定义方式

- **对象结构**：使用 `interface`，如 `StartApplyRecord`
- **联合/字面量类型**：使用 `export type`，如 `export type ApprovalStatus = 0 | 1 | 2 | 3`
- **可选参数包装**：使用 `Partial<T>` 形式，如 `export type HistoryList = Partial<{ ... }>`

#### 命名规范

| 类别 | 规范 | 示例 |
|------|------|------|
| 响应泛型 | 沿用项目定义 | `ApiResponse<T>`, `PageResponse<T>` |
| 列表记录 | {业务名}Record | `StartApplyRecord` |
| 查询参数 | {业务名}SearchParams | `StartApplySearchParams` |
| 表单数据 | {业务名}FormData | `StartApplyFormData` |
| 详情 | {业务名}Detail | `StartApplyDetail` |
| 请求参数 | {业务名}Params | `ExportParams` |

#### 注释规范（强制）

每个字段**必须**有中文注释。方式如下：

```typescript
/** 项目业态名称 */
projectTypeName: string;

/** 审批状态：0-草稿/1-审批中/2-审批完成/3-审批驳回 */
approvalStatus: ApprovalStatus;
```

每个类型/接口**必须**有来源注释，包含 `@module` 和 `@api` 两个标签：

```typescript
/**
 * 开工申请记录（列表项）
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/pageList
 */
export interface StartApplyRecord { ... }
```

`@module` 的值格式：`{一级模块} / {二级功能}`，从接口路径中推断（如 `/api/pm-engineering/start-apply` → `工程管理 / 开工申请`）。`@api` 包含 HTTP 方法和完整路径。

#### 文件结构

types.ts 按以下顺序组织：
1. 外部依赖导入
2. 字面量/联合类型别名
3. 通用泛型（ApiResponse, PageResponse）
4. 附件相关类型
5. 列表相关类型（Record + SearchParams）
6. 详情相关类型
7. 表单相关类型
8. 子模块类型（按业务拆分）
9. 请求参数类型

### 第四步：生成 index.ts

按照参考规范生成 API 封装文件。核心规则：

#### 导入

```typescript
import { defHttp } from '@/utils/http/axios';
import type { ... } from './types';
```

#### API 前缀枚举

```typescript
export enum Api {
  Prefix = '/api/pm-engineering/{module-name}',
}
```

#### HTTP 方法判断规则

以 OpenAPI 定义为准，不以路径名推断：
- OpenAPI 定义为 `DELETE` → 使用 `defHttp.delete`
- OpenAPI 定义为 `POST`（即使路径含 delete）→ 使用 `defHttp.post`
- OpenAPI 定义为 `GET` → 使用 `defHttp.get`
- OpenAPI 定义为 `PUT` → 使用 `defHttp.put`

#### 函数签名模式

```typescript
// POST 请求 — 参数用 data
export function saveXxx(data: Partial<XxxFormData>) {
  return defHttp.post<ApiResponse<boolean>>({
    url: Api.Prefix + '/save',
    data,
  });
}

// GET 请求 — 参数用 params
export function getXxxDetail(params: { id: string }) {
  return defHttp.get<ApiResponse<XxxDetail>>({
    url: Api.Prefix + '/get/' + params.id,
  });
}

// DELETE 请求 — 路径参数
export function deleteXxx(params: { id: string }) {
  return defHttp.delete<ApiResponse<boolean>>({
    url: Api.Prefix + '/' + params.id,
  });
}

// 导出 — responseType: blob
export function exportXxxList(data: ExportParams) {
  return defHttp.post<Blob>(
    {
      url: Api.Prefix + '/export',
      data,
      responseType: 'blob',
    },
    { isTransformResponse: false },
  );
}
```

#### 注释规范（强制）

每个函数**必须**有 JSDoc 注释，包含中文说明、`@module` 和 `@api`：

```typescript
/**
 * 分页查询开工申请列表
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/pageList
 */
export function getStartApplyList(data: StartApplySearchParams) { ... }
```

### 第五步：写入文件

将生成的文件写入目标目录：
- `{target}/types.ts`
- `{target}/index.ts`

如果目标目录不存在，自动创建。

### 第六步：完整性校验

生成后执行以下校验，不通过则修复：

#### 6.1 接口完整性
- [ ] 源接口数量 = 生成的函数数量（对比 paths 列表和 index.ts 的 export function 数量）
- [ ] 每个接口都有对应的 types 定义

#### 6.2 类型引用闭环
- [ ] index.ts 导入的每个类型都在 types.ts 中有定义
- [ ] types.ts 中引用的类型（如 ApiResponse）都有来源（全局导入或本地定义）
- [ ] 无未使用的导入

#### 6.3 TypeScript 编译校验
运行 `npx tsc --noEmit {target}/types.ts {target}/index.ts` 检查是否有类型错误

#### 6.4 字段完整性（抽样）
- 随机抽取 1 个接口，对比 OpenAPI example 字段和生成的 Record/Params 类型字段
- 如有缺失字段，补充后重新校验

## 质量检查

生成后自动检查：
- [ ] 每个字段都有中文注释
- [ ] 每个类型都有 `@api` 来源注释
- [ ] 每个类型/函数都有 `@module` 模块定位注释
- [ ] 每个函数都有 JSDoc（说明 + `@module` + `@api`）
- [ ] 命名符合规范（Record/Params/FormData/Detail）
- [ ] 使用 `defHttp` 封装
- [ ] POST 用 `data`，GET 用 `params`
- [ ] 响应类型使用 `ApiResponse<T>` / `PageResponse<T>`

## 异常处理

| 场景 | 触发条件 | 处理动作 |
|------|----------|----------|
| MCP 工具不可用 | `read_project_oas` 报错 | 提示用户检查 MCP 配置，降级为手动粘贴接口 JSON |
| 接口搜索无结果 | scope 匹配 0 个接口 | 展示所有可用接口路径，让用户手动选择 |
| schema 循环引用 | 递归超过 5 层 | 截断并标记 `// TODO: 循环引用，需手动处理` |
| target 目录无权限 | 写入失败 | 输出到 stdout，让用户手动保存 |
| types.ts 已存在 | 文件已存在 | 询问：覆盖 / 合并（保留现有类型，只追加新类型） / 取消 |
| TypeScript 编译失败 | tsc 报错 | 读取错误信息，自动修复常见问题（缺少导入、类型不匹配） |
| description 全部为空 | 注释无法生成 | 使用字段名推断中文注释，标记 TODO |

## 参考文件

生成时必须阅读 `references/reference.md`，其中包含完整的参考代码示例。
