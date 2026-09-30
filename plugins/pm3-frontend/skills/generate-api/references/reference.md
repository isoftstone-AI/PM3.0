# API 代码参考模板

> 本文件是 generate-api skill 的参考模板，基于 start-apply 模块的实际代码。

---

## 目录

1. [types.ts 完整示例](#1-typests-完整示例)
2. [index.ts 完整示例](#2-indexts-完整示例)
3. [代码模式速查](#3-代码模式速查)

---

## 1. types.ts 完整示例

### 1.1 字面量/联合类型（用 export type）

```typescript
/** 项目业态 */
export type ProjectType = '1' | '2' | '3'; // 1-光伏 2-风电 3-储能

/** 业态细分 */
export type SubType = '平地' | '山地' | '水面' | '渔光';

/** 业务模式 */
export type BusinessMode = 'BT' | 'EPC' | '自持';

/**
 * 审批状态
 * @value 0 - 草稿
 * @value 1 - 审批中
 * @value 2 - 审批完成
 * @value 3 - 审批驳回
 */
export type ApprovalStatus = 0 | 1 | 2 | 3;

/**
 * 开工决策意见
 * @value 1 - 全面开工
 * @value 2 - 部分开工
 * @value 3 - 形象开工
 * @value 4 - 不同意开工
 */
export type ApprovalDecision = 1 | 2 | 3 | 4;

/** 表单模式 */
export type FormMode = 'edit' | 'view';

/**
 * 申请类型
 * @value 'FIRST' - 首次开工
 * @value 'SECOND' - 二次开工
 * @value 'RESTART' - 重新开工
 */
export type ApplicationType = 'FIRST' | 'SECOND' | 'RESTART';
```

### 1.2 通用响应类型

```typescript
/**
 * 通用响应
 * @description code: 0-成功，其他-失败
 */
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T;
}

/**
 * 分页响应
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/pageList
 */
export interface PageResponse<T> {
  /** 总记录数 */
  total: number;
  /** 总页数 */
  pages: number;
  /** 当前页码 */
  current: number;
  /** 每页条数 */
  size: number;
  /** 记录列表 */
  records: T[];
}
```

### 1.3 附件类型

```typescript
/** 附件 */
export interface Attachment {
  id: string;
  filename: string;
  filePath: string;
  uploadName?: string;
  uploadTime?: string;
  attachmentType?: string;
}

/** 附件类型配置 */
export interface AttachmentTypeConfig {
  /** 附件类型标识 */
  type: string;
  /** 显示名称 */
  label: string;
  /** 是否必填 */
  required?: boolean;
  /** 最大上传数量 */
  maxCount?: number;
  /** 允许的文件类型 */
  accept?: string;
  /** 最大文件大小，单位MB */
  maxSize?: number;
}
```

### 1.4 列表类型（Record + SearchParams）

```typescript
/**
 * 开工申请记录（列表项）
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/pageList
 */
export interface StartApplyRecord {
  id: string;
  preVersionId: string;
  projectId: string;
  /** 流程实例 ID */
  processInstanceId?: string;
  /** SAP项目编号 */
  projectCode: string;
  projectName: string;
  /** 项目业态名称 */
  projectTypeName: string;
  branchCompany: string;
  region: string;
  /** 申请开工容量（MW/MWp） */
  applyCapacity: number;
  /** 累计通过开工容量 */
  cumulativeCapacity: number;
  approvalDecision: ApprovalDecision;
  /** 批准开工时间 */
  approvedStartDate: string;
  /** 审批通过时间 */
  approvalPassTime: string;
  /** 申请类型显示值 */
  applyTypeDisplay: string;
  /** 审批状态名称 */
  approvalStatusName: string;
  /** 审批状态 */
  approvalStatus: ApprovalStatus;
}

/**
 * 列表查询参数
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/pageList
 */
export interface StartApplySearchParams {
  /** 项目ID */
  projectId?: string;
  /** SAP项目编号 */
  projectCode?: string;
  /** 项目名称（模糊搜索） */
  projectName?: string;
  /** 项目业态代码 */
  projectType?: string;
  /** 业务模式代码 */
  businessMode?: string;
  /** 申请类型：FIRST-首次开工/SECOND-二次开工/RESTART-重新开工 */
  applicationType?: ApplicationType;
  /** 审批状态：0-草稿/1-审批中/2-审批完成/3-审批驳回 */
  approvalStatus?: ApprovalStatus;
  /** 分公司 */
  branchCompany?: string;
  /** 区域 */
  region?: string;
  /** 申请人ID */
  applicantId?: string;
  /** 申请单号 */
  applyNo?: string;
  /** 当前页码，默认1 */
  page: number;
  /** 每页条数，默认10 */
  limit: number;
}
```

### 1.5 详情类型

```typescript
/**
 * 开工申请详情
 * @module 工程管理 / 开工申请
 * @api GET /api/pm-engineering/start-apply/get/{id}
 * @api GET /api/pm-engineering/start-apply/secondary-detail/{id}
 * @api GET /api/pm-engineering/start-apply/restart-detail/{id}
 */
export interface StartApplyDetail {
  id: string;
  /** 业务主键 */
  businessKey: string;
  /** 申请单号 */
  applyNo: string;
  /** 申请人ID */
  applicantId: string;
  /** 申请人姓名 */
  applicantName: string;
  /** 申请时间 */
  applyTime: string;
  /** 申请类型枚举值 */
  applyType?: ApplicationType;
  /** 申请类型显示值 */
  applyTypeDisplay: string;
  /** 审批状态：0-草稿/1-审批中/2-审批完成/3-审批驳回 */
  approvalStatus: ApprovalStatus;

  // 项目信息
  projectId: string;
  /** SAP项目编号 */
  projectCode: string;
  projectName: string;
  /** 项目业态代码 */
  projectType: string;
  /** 项目业态名称 */
  projectTypeName: string;

  // ... 更多字段按实际接口定义
}
```

### 1.6 表单数据类型

```typescript
/**
 * 开工申请表单数据
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/draft
 * @api POST /api/pm-engineering/start-apply/submit
 */
export interface StartApplyFormData {
  id?: string;
  /** 业务主键（流程使用） */
  businessKey?: string;
  /** 项目ID */
  projectId: string;
  /** 申请类型 */
  applyType?: ApplicationType;
  /** 申请开工容量（MW/MWp） */
  applyCapacity?: number;
  /** 申请概述 */
  applySummary?: string;
  /** 附件列表 */
  attachmentList?: Attachment[];
}
```

### 1.7 Partial 包装类型

```typescript
/**
 * 开工申请历史VO
 */
export type HistoryList = Partial<{
  id: string;
  projectId: string; // 项目 ID
  applyTypeDisplay: string; // 申请类型
  applyCapacity: number; // 申请开工容量
  cumulativeCapacity: number; // 累计通过开工容量
  approvalDecisionName: string; // 开工决策意见
  approvalPassTime: string; // 审批通过时间
  approvalStatusName: string; // 审批状态
}>;
```

### 1.8 请求参数类型

```typescript
/**
 * 实时预审请求参数
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/realtime/pre-audit
 */
export interface RealtimePreAuditParams {
  projectId: string;
  applyCapacity: number;
  fullCapacityDate?: string;
  unitCost?: number;
}

/**
 * 导出参数
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/export
 */
export interface ExportParams extends Omit<StartApplySearchParams, 'page' | 'limit'> {
  projectName?: string;
  projectCode?: string;
}
```

---

## 2. index.ts 完整示例

```typescript
import { defHttp } from '@/utils/http/axios';
import type {
  ApiResponse,
  PageResponse,
  StartApplyRecord,
  StartApplySearchParams,
  StartApplyDetail,
  StartApplyFormData,
  HistoryRecord,
  PreAuditOpinion,
  RealtimePreAuditParams,
  ExportParams,
} from './types';

export enum Api {
  Prefix = '/api/pm-engineering/start-apply',
}

/**
 * 分页查询开工申请列表
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/pageList
 */
export function getStartApplyList(data: StartApplySearchParams) {
  return defHttp.post<ApiResponse<PageResponse<StartApplyRecord>>>({
    url: Api.Prefix + '/pageList',
    data,
  });
}

/**
 * 获取开工申请详情
 * @module 工程管理 / 开工申请
 * @api GET /api/pm-engineering/start-apply/get/{id}
 */
export function getStartApplyDetail(params: { id: string }) {
  return defHttp.get<ApiResponse<StartApplyDetail>>({
    url: Api.Prefix + '/get/' + params.id,
  });
}

/**
 * 开工申请暂存（通用）
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/draft
 */
export function saveDraft(data: Partial<StartApplyFormData>) {
  return defHttp.post<ApiResponse<string>>({
    url: Api.Prefix + '/draft',
    data,
  });
}

/**
 * 提交开工申请（统一入口）
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/submit
 */
export function submitApply(data: StartApplyFormData) {
  return defHttp.post<ApiResponse<boolean>>({
    url: Api.Prefix + '/submit',
    data,
  });
}

/**
 * 删除开工申请草稿
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/delete/{id}
 */
export function deleteDraft(params: { id: string }) {
  return defHttp.post<ApiResponse<boolean>>({
    url: Api.Prefix + '/delete/' + params.id,
  });
}

/**
 * 导出开工申请列表
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-engineering/start-apply/export
 */
export function exportStartApplyList(data: ExportParams) {
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

---

## 3. 代码模式速查

### 3.1 HTTP 方法与参数对应

| HTTP 方法 | 参数名 | 示例 |
|-----------|--------|------|
| POST | `data`（请求体） | `defHttp.post({ url, data })` |
| GET | `params`（查询参数） | `defHttp.get({ url, params })` |
| GET（路径参数） | 直接拼接 URL | `url: Api.Prefix + '/get/' + params.id` |

### 3.2 响应类型组合

| 场景 | 响应类型 |
|------|----------|
| 普通数据 | `ApiResponse<T>` |
| 分页列表 | `ApiResponse<PageResponse<T>>` |
| 无返回数据 | `ApiResponse<null>` 或 `ApiResponse<boolean>` |
| 导出文件 | `Blob`（需 `responseType: 'blob'` + `isTransformResponse: false`） |

### 3.3 函数命名规范

| 操作 | 前缀 | 示例 |
|------|------|------|
| 查询列表 | `get` + 名词 + `List` | `getStartApplyList` |
| 查询详情 | `get` + 名词 + `Detail` | `getStartApplyDetail` |
| 新增/保存 | `save` / `add` | `saveDraft` |
| 提交 | `submit` | `submitApply` |
| 删除 | `delete` | `deleteDraft` |
| 导出 | `export` + 名称 | `exportStartApplyList` |
| 验证 | `validate` | `validateProjectSelection` |

### 3.4 跨模块接口

跨模块的接口不使用 `Api.Prefix`，直接写完整路径：

```typescript
/**
 * 关联流程
 * @module 工程管理 / 开工申请
 * @api POST /api/pm-bpm/procinstCommon/list
 */
export function procinstCommon(data: { projectId: string }) {
  return defHttp.post<ApiResponse<ProcessLinkType[]>>({
    url: `/api/pm-bpm/procinstCommon/list`,
    data,
  });
}
```
