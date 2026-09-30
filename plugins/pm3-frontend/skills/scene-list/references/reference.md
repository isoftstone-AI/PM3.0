# 列表页代码模板

> 基准代码来源：`src/views/eng-manage/start-apply/` 实际上线版本
> 所有 `[REPLACE]` 标记的区域需要根据 PRD/API 文档替换
> 所有 `[KEEP]` 标记的区域保持模板代码不变

---

## Block 1: api/types.ts

```typescript
// [REPLACE] 整个文件的类型定义根据 API 文档替换
// 以下为基准模板，保留结构，替换业务字段

// [REPLACE] 业务状态类型 — 根据 PRD 实际状态枚举替换
export type ApprovalStatus = 0 | 1 | 2 | 3;
// 0=草稿 1=审批中 2=审批完成 3=审批驳回（根据实际业务调整）

// [REPLACE] 列表记录类型 — 根据列表 API 返回字段替换
export interface StartApplyRecord {
  id: string;
  projectName: string;           // 项目名称
  sapProjectCode: string;        // SAP项目编码
  projectType: string;           // 项目业态
  branchCompany: string;         // 分公司
  region: string;                // 区域
  applyCapacity: number;         // 申请开工容量
  totalApprovedCapacity: number; // 累计通过开工容量
  startDecision: string;         // 开工决策意见
  approvalPassTime: string;      // 审批通过时间
  approvalStatus: ApprovalStatus;// 审批状态
  processInstanceId: string;     // 流程实例ID
  preVersionId: string;          // 前版本ID（用于历史查看）
  // 根据 API 文档添加更多字段...
}

// [REPLACE] 搜索参数类型 — 根据查询条件替换
export interface StartApplySearchParams {
  projectName?: string;
  projectType?: string;
  branchCompany?: string;
  approvalStatus?: ApprovalStatus | undefined;
  startDecision?: string;
}

// [REPLACE] 导出参数类型 — 通常与搜索参数相同
export interface ExportParams extends StartApplySearchParams {}

// [REPLACE] 表单模式类型 — 根据业务是否需要多种申请类型
export type ApplicationType = 'FIRST' | 'SECOND' | 'RESTART';

// [KEEP] 表单操作类型
export type FormMode = 'edit' | 'view';

// [REPLACE] 详情类型 — 根据详情 API 返回字段替换（复杂类型，按需添加）
export interface StartApplyDetail {
  id: string;
  // 根据 API 文档添加详情字段...
}

// [KEEP] 通用分页响应 — 如果项目有统一类型可直接 import
export interface PageResponse<T> {
  records: T[];
  total: number;
  size: number;
  current: number;
}
```

---

## Block 2: api/index.ts

```typescript
import { defHttp } from '@/utils/http/axios';
import type {
  StartApplyRecord,
  StartApplySearchParams,
  StartApplyDetail,
  ExportParams,
  PageResponse,
} from './types';

// [REPLACE] API 前缀 — 替换为实际模块路径
export enum Api {
  Prefix = '/api/pm-engineering/start-apply',  // 改为实际前缀
}

// [REPLACE] 分页查询列表 — 替换接口路径和参数映射
export function getStartApplyList(params: any) {
  return defHttp.post<PageResponse<StartApplyRecord>>({
    url: Api.Prefix + '/pageList',   // 改为实际列表接口路径
    data: params,
  });
}

// [REPLACE] 获取详情 — 替换接口路径
export function getStartApplyDetail(id: string) {
  return defHttp.get<{ data: StartApplyDetail }>({
    url: Api.Prefix + `/get/${id}`,  // 改为实际详情接口路径
  });
}

// [REPLACE] 删除草稿 — 替换接口路径和参数
export function deleteDraft(id: string) {
  return defHttp.post({
    url: Api.Prefix + `/delete/${id}`, // 改为实际删除接口路径
  });
}

// [REPLACE] 导出列表 — 替换接口路径
export function exportStartApplyList(params: ExportParams) {
  return defHttp.post({
    url: Api.Prefix + '/export',       // 改为实际导出接口路径
    data: params,
    responseType: 'blob',
  });
}

// [OPTIONAL] 获取待办任务ID — 如果有"去办理"功能需要保留
export function getTaskByProcInstId(params: { procInstId: string }) {
  return defHttp.post({
    url: '/api/pm-bpm/todo/getTaskByProcInstId',
    data: params,
  });
}

// [OPTIONAL] 根据 PRD 添加更多 API 函数...
// 例如：save、submit、validate 等
```

---

## Block 3: useIndex.tsx

```typescript
import { ref } from 'vue';
import { message, Modal } from 'ant-design-vue';
import { useTable } from '@/components/Table';
import type { StartApplyRecord, StartApplySearchParams } from './api/types';
import { getStartApplyList, deleteDraft } from './api';

// [REPLACE] 操作回调接口 — 根据 PRD 中的操作按钮调整
export interface TableActionCallbacks {
  onDetail: (record: StartApplyRecord) => void;
  onDetailPre?: (record: StartApplyRecord) => void;  // [OPTIONAL] 历史版本查看
  onEdit: (record: StartApplyRecord) => void;
  onSecond?: (record: StartApplyRecord) => void;     // [OPTIONAL] 二次申请
  onRestart?: (record: StartApplyRecord) => void;    // [OPTIONAL] 重新申请
  onDelete: (record: StartApplyRecord) => void;
}

// [REPLACE] 审批状态选项 — 根据 PRD 实际状态枚举替换
export const approvalStatusOptions = [
  { label: '草稿', value: 0 },
  { label: '审批中', value: 1 },
  { label: '审批完成', value: 2 },
  { label: '审批驳回', value: 3 },
];

export function useIndex() {
  // [KEEP] useTable 配置框架
  const [registerTable, { reload, getForm }] = useTable({
    // [REPLACE] API 请求函数和参数映射
    api: async (pageParams) => {
      const searchParams: Record<string, any> = {};

      // [KEEP] 分页字段映射（根据后端实际字段名调整）
      if (pageParams.pageNo !== undefined) {
        searchParams.pageNum = pageParams.pageNo;   // pageNo → pageNum
      }
      if (pageParams.limit !== undefined) {
        searchParams.pageSize = pageParams.limit;   // limit → pageSize
      }

      // [OPTIONAL] 日期范围字段拆分（RangePicker 返回 [start, end] 数组）
      // 根据实际查询条件添加/删除
      if (pageParams.applyTime && Array.isArray(pageParams.applyTime)) {
        searchParams.applyTimeStart = pageParams.applyTime[0];
        searchParams.applyTimeEnd = pageParams.applyTime[1];
      }

      // [OPTIONAL] 多选字段转字符串（DictSelect mode="multiple" 返回 string[]）
      // 根据实际查询条件添加/删除
      if (pageParams.majors && Array.isArray(pageParams.majors)) {
        searchParams.majors = pageParams.majors.join(',');
      } else if (pageParams.majors) {
        searchParams.majors = pageParams.majors;
      }

      // [KEEP] 其他普通字段直接透传（过滤空值）
      ['keyword', 'approvalStatus', 'projectName'].forEach((key) => {
        if (pageParams[key] !== undefined && pageParams[key] !== null && pageParams[key] !== '') {
          searchParams[key] = pageParams[key];
        }
      });

      const res = await getStartApplyList(searchParams);
      return res;
    },

    // [REPLACE] 表格列定义 — 根据 PRD 替换
    columns: [
      { title: 'SAP项目编码', dataIndex: 'sapProjectCode', width: 140 },
      { title: '项目名称', dataIndex: 'projectName', ellipsis: true },
      { title: '项目业态', dataIndex: 'projectType', width: 100 },
      { title: '分公司', dataIndex: 'branchCompany', width: 120 },
      { title: '区域', dataIndex: 'region', width: 120 },
      { title: '申请开工容量', dataIndex: 'applyCapacity', width: 130 },
      { title: '累计通过开工容量', dataIndex: 'totalApprovedCapacity', width: 150 },
      { title: '开工决策意见', dataIndex: 'startDecision', width: 120 },
      { title: '审批通过时间', dataIndex: 'approvalPassTime', width: 170 },
      { title: '审批状态', dataIndex: 'approvalStatus', key: 'approvalStatus', width: 100 },
    ],

    // [KEEP] 操作列配置
    actionColumn: {
      width: 200,
      title: '操作',
      dataIndex: 'action',
      fixed: 'right',
    },

    // [REPLACE] 搜索表单配置 — 根据 PRD 查询条件替换
    formConfig: {
      showAdvancedSearch: false,
      autoAdvancedLine: 3,
      labelWidth: 100,
      actionColOptions: { span: 6 },
      schemas: [
        {
          field: 'projectName',
          label: '项目名称',
          component: 'Input',
          colProps: { span: 6 },
          componentProps: {
            placeholder: '请输入项目名称',
            allowClear: true,
          },
        },
        {
          field: 'projectType',
          label: '项目业态',
          component: 'DictSelect',
          colProps: { span: 6 },
          componentProps: {
            dictCode: 'project_type',    // [REPLACE] 改为实际字典编码
            placeholder: '请选择',
            allowClear: true,
          },
        },
        {
          field: 'branchCompany',
          label: '分公司',
          component: 'DictSelect',
          colProps: { span: 6 },
          componentProps: {
            dictCode: 'branch_company',  // [REPLACE] 改为实际字典编码
            placeholder: '请选择',
            allowClear: true,
          },
        },
        {
          field: 'approvalStatus',
          label: '审批状态',
          component: 'Select',
          colProps: { span: 6 },
          componentProps: {
            options: approvalStatusOptions,
            placeholder: '请选择',
            allowClear: true,
          },
        },
        {
          field: 'startDecision',
          label: '开工决策意见',
          component: 'DictSelect',
          colProps: { span: 6 },
          componentProps: {
            dictCode: 'start_decision',  // [REPLACE] 改为实际字典编码
            placeholder: '请选择',
            allowClear: true,
          },
        },
        // 根据 PRD 添加更多查询条件...
      ],
    },

    // [KEEP] 以下配置保持不变
    useSearchForm: true,
    showIndexColumn: true,
    indexColumnProps: { width: 60 },
    showTableSetting: true,
    rowKey: 'id',
  });

  // [KEEP] 删除处理函数
  const handleDelete = (record: StartApplyRecord) => {
    Modal.confirm({
      title: '确认删除',
      content: `确定要删除该记录吗？`,   // [REPLACE] 确认文案
      onOk: async () => {
        const res = await deleteDraft(record.id);
        if (res.code === 0) {           // [NOTE] 注意后端成功码，可能是 0 或 200
          message.success('删除成功');
          reload();
        } else {
          message.error(res.msg || '删除失败');
        }
      },
    });
  };

  // [REPLACE] 操作按钮逻辑 — 根据 PRD 的操作按钮规则替换
  const getTableActions = (
    record: StartApplyRecord,
    callbacks: TableActionCallbacks,
  ) => {
    const actions: { label: string; onClick: () => void; type?: 'primary' | 'danger' }[] = [];

    // 草稿状态：显示编辑、删除
    if (record.approvalStatus === 0) {
      actions.push(
        { label: '编辑', onClick: () => callbacks.onEdit(record), type: 'primary' },
        { label: '删除', onClick: () => callbacks.onDelete(record), type: 'danger' },
      );
    }
    // 非草稿状态：显示详情
    if (record.approvalStatus !== 0) {
      actions.push({ label: '详情', onClick: () => callbacks.onDetail(record) });
    }
    // 审批完成状态：显示二次开工、重新开工
    if (record.approvalStatus === 2) {
      if (callbacks.onSecond) {
        actions.push({ label: '二次开工', onClick: () => callbacks.onSecond!(record) });
      }
      if (callbacks.onRestart) {
        actions.push({ label: '重新开工', onClick: () => callbacks.onRestart!(record) });
      }
    }

    return actions;
  };

  // [KEEP] 状态工具函数
  const getStatusColor = (status: number) => {
    const map: Record<number, string> = {
      0: 'default',
      1: 'processing',
      2: 'success',
      3: 'error',
    };
    return map[status] || 'default';
  };

  const getStatusText = (status: number) => {
    const map: Record<number, string> = {
      0: '草稿',
      1: '审批中',
      2: '审批完成',
      3: '审批驳回',
    };
    return map[status] || '未知';
  };

  return {
    registerTable,
    reload,
    getForm,
    handleDelete,
    getTableActions,
    getStatusColor,
    getStatusText,
  };
}
```

---

## Block 4: index.tsx

```typescript
import { defineComponent, ref } from 'vue';
import { Button, Space } from 'ant-design-vue';
import { ExportOutlined, PlusOutlined } from '@ant-design/icons-vue';
import { BasicTable } from '@/components/Table';
import InnerLayout from '@/layouts/innerLayout';
import { useRouter } from 'vue-router';
import { useIndex } from './useIndex';
// [REPLACE] 弹窗组件导入 — 替换为实际业务组件
import StartApplyFormModal from './components/StartApplyForm';
import StartApplyDetailModal from './components/StartApplyDetailModal';
import type { StartApplyRecord, FormMode, ExportParams, ApplicationType } from './api/types';
import type { TableActionCallbacks } from './useIndex';
import { exportStartApplyList, getTaskByProcInstId } from './api';

export default defineComponent({
  // [REPLACE] 组件名 — 替换为 PascalCase 模块名 + List
  name: 'StartApplyList',

  setup() {
    // [KEEP] 从 useIndex 获取表格能力
    const {
      registerTable,
      reload,
      getForm,
      handleDelete,
      getTableActions,
      getStatusColor,
      getStatusText,
    } = useIndex();
    const router = useRouter();

    // [KEEP] 弹窗状态管理
    const formModalOpen = ref(false);
    const detailModalOpen = ref(false);
    // [REPLACE] 表单模式类型 — 根据业务调整
    const formMode = ref<ApplicationType>('FIRST');
    const formType = ref<FormMode>('edit');
    const currentId = ref<string>('');
    const currentProjectId = ref<string>('');

    // [KEEP] 打开表单弹窗
    const openFormModal = (type: FormMode, mode: ApplicationType, record?: StartApplyRecord) => {
      formMode.value = mode;
      formType.value = type;
      currentId.value = record?.id || '';
      currentProjectId.value = record?.projectId || '';
      formModalOpen.value = true;
    };

    // [KEEP] 打开详情弹窗
    const openDetailModal = (id: string) => {
      currentId.value = id;
      formMode.value = 'FIRST';
      detailModalOpen.value = true;
    };

    // [KEEP] 导出功能
    const handleExport = async () => {
      const search = getForm().getData();
      try {
        const res = await exportStartApplyList(search as ExportParams);
        const blob = new Blob([res as BlobPart], { type: 'application/vnd.ms-excel' });
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = `列表导出_${new Date().toISOString().split('T')[0]}.xlsx`; // [REPLACE] 文件名
        link.click();
        URL.revokeObjectURL(link.href);
      } catch (error) {
        console.error('导出失败:', error);
      }
    };

    // [OPTIONAL] 去办理功能 — 如果 PRD 需要"去办理"按钮则保留
    const handleGoToHandle = async (record: StartApplyRecord) => {
      try {
        const res = await getTaskByProcInstId({ procInstId: record?.processInstanceId as string });
        const taskId = res.data?.id;
        if (taskId) {
          router.push(`/office/todo/approval?id=${taskId}`);
        }
      } catch (error) {
        console.error('获取待办任务失败:', error);
      }
    };

    // [KEEP] 渲染操作按钮
    const renderActionButtons = (record: StartApplyRecord) => {
      // [REPLACE] 回调配置 — 根据 PRD 操作按钮规则调整
      const actions = getTableActions(record, {
        onDetail: r => openDetailModal(r.id),
        onDetailPre: r => openDetailModal(r?.preVersionId),
        onEdit: r => openFormModal('edit', 'FIRST', r),
        onSecond: r => openFormModal('edit', 'SECOND', r),
        onRestart: r => openFormModal('edit', 'RESTART', r),
        onDelete: handleDelete,
      } as TableActionCallbacks);

      return (
        <Space size="small">
          {actions.map((action, index) => (
            <Button key={index} type="link" size="small" danger={action.type === 'danger'} onClick={action.onClick}>
              {action.label}
            </Button>
          ))}
          {/* [OPTIONAL] 去办理按钮 — 根据状态判断是否显示 */}
          {record.approvalStatus === 3 && (
            <Button type="link" size="small" onClick={() => handleGoToHandle(record)}>
              去办理
            </Button>
          )}
        </Space>
      );
    };

    // [KEEP] 渲染函数
    return () => (
      <InnerLayout>
        <BasicTable indexColumnProps={{ width: 60 }} onRegister={registerTable}>
          {{
            // [KEEP] 工具栏
            toolbar: () => (
              <div class="w-full flex justify-between">
                {/* [REPLACE] 按钮文案 */}
                <Button type="primary" icon={<PlusOutlined />} onClick={() => openFormModal('edit', 'FIRST')}>
                  开工成果审批
                </Button>
                <Button icon={<ExportOutlined />} onClick={handleExport}>
                  导出
                </Button>
              </div>
            ),
            // [KEEP] 自定义单元格渲染
            bodyCell: ({ column, record }: { column: any; record: StartApplyRecord }) => {
              if (column.key === 'action') {
                return renderActionButtons(record);
              }
              // [REPLACE] 状态列渲染 — 根据实际状态字段添加/修改
              if (column.key === 'approvalStatus') {
                return (
                  <span style={{ color: getStatusColor(record.approvalStatus) }}>
                    {getStatusText(record.approvalStatus)}
                  </span>
                );
              }
              // [OPTIONAL] 其他状态列 — 如 validityStatus、publishStatus 等
              if (column.key === 'validityStatus') {
                const color = record.validityStatus === 1 ? 'blue'
                  : record.validityStatus === 2 ? 'green'
                  : 'gray';
                const text = record.validityStatus === 1 ? '未生效'
                  : record.validityStatus === 2 ? '已生效'
                  : '已失效';
                return <Tag color={color}>{text}</Tag>;
              }
              return null;
            },
          }}
        </BasicTable>

        {/* [REPLACE] 表单弹窗 — 替换为实际组件 */}
        <StartApplyFormModal
          key={Date.now()}
          v-model:open={formModalOpen.value}
          mode={formMode.value}
          type={formType.value}
          id={currentId.value}
          projectId={currentProjectId.value}
          onSuccess={reload}
          onView={data => {
            openDetailModal(data.id);
          }}
        />

        {/* [REPLACE] 详情弹窗 — 替换为实际组件 */}
        <StartApplyDetailModal
          key={currentId.value || Date.now()}
          type="view"
          v-model:open={detailModalOpen.value}
          id={currentId.value}
          mode={formMode.value}
        />
      </InnerLayout>
    );
  },
});
```

---

## 目录结构参考

```
src/views/模块名/功能名/
├── index.tsx              # 页面入口（Block 4）
├── useIndex.tsx           # 表格逻辑抽离（Block 3）
├── api/
│   ├── types.ts           # 类型定义（Block 1）
│   └── index.ts           # API 封装（Block 2）
└── components/            # 业务组件（表单弹窗、详情弹窗等，按需创建）
    ├── StartApplyForm/    # [REPLACE] 替换为实际表单组件
    └── StartApplyDetailModal/  # [REPLACE] 替换为实际详情组件
```

## 标记说明

| 标记 | 含义 |
|------|------|
| `[REPLACE]` | 必须根据 PRD/API 文档替换的内容 |
| `[KEEP]` | 保持模板代码不变 |
| `[OPTIONAL]` | 可选功能，根据 PRD 决定是否保留 |
| `[NOTE]` | 需要特别注意的细节 |
