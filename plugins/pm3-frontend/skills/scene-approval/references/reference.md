# 审批页代码模板（分层模式）

> 基准代码来源：
> - 审批模板页面：`src/views/office/todo/components/apply-modal/startApplyApproval.tsx`
> - 审批表单组件：`src/views/office/todo/components/apply-modal/approval-form/StartApplyApprovalForm.tsx`
>
> 所有 `[REPLACE]` 标记的区域需要根据业务信息替换
> 所有 `[KEEP]` 标记的区域保持模板代码不变
> 所有 `[OPTIONAL]` 标记的区域根据需求决定是否保留
> 所有 `[NOTE]` 标记的区域需要特别注意

---

## Block 1: 审批模板页面 xxxApproval.tsx

```typescript
/**
 * [REPLACE:业务模块名] 审批模板页面
 * 对齐 startApplyApproval 架构：
 * - isRejected ? <编辑组件 displayMode="embedded"> : <详情组件 displayMode="embedded">
 * - provide/inject 权限下发
 * - loaded 控制渲染时机
 * [OPTIONAL:- 非驳回场景：根据审批节点动态控制可编辑性]
 */

import {
  defineComponent,
  ref,
  reactive,
  computed,
  onMounted,
  provide,
  type PropType,
} from 'vue';
import InnerLayout from '@/layouts/innerLayout';

// [REPLACE] 业务相关导入
import { [REPLACE:详情API函数名][OPTIONAL:, [REPLACE:业务保存API函数名]] } from '[REPLACE:详情API导入路径]';
import type { [REPLACE:详情类型名] } from '[REPLACE:详情类型导入路径]';
[OPTIONAL:import {
  [REPLACE:节点枚举名],
  type [REPLACE:节点类型名],
} from '[REPLACE:节点配置导入路径]';]

import [REPLACE:详情组件名], {
  type [REPLACE:详情组件Ref类型名],
} from '[REPLACE:详情组件导入路径]';
import [REPLACE:编辑组件名], {
  type [REPLACE:编辑组件Ref类型名],
} from '[REPLACE:编辑组件导入路径]';
import [REPLACE:ApprovalForm组件名], {
  type [REPLACE:IApprovalForm类型名],
} from './approval-form/[REPLACE:ApprovalForm文件名]';
import { useMessage } from '@/hooks/web/useMessage';

// [KEEP] 权限上下文（对齐 startApplyApproval）
export enum ProvideContext {
  Permission = 'Permission',
}

export type PermissionData = {
  templatePermission: string;
  operationType: string;
  otherOperationType: string;
};

type DetailData = Partial<[REPLACE:详情类型名]>;

[OPTIONAL:
/**
 * operationType → [REPLACE:节点类型名] 映射
 * 后端 getOperationRole 接口返回的 operationType 值映射到前端节点配置
 */
const OPERATION_TYPE_TO_NODE: Record<string, [REPLACE:节点类型名]> = {
  [REPLACE:operationType映射]
};

/**
 * 需要编辑的审批节点
 * 不在此列表中的节点，为只读展示
 */
const EDITABLE_NODES: [REPLACE:节点类型名][] = [
  [REPLACE:可编辑节点列表]
];
]

const props = {
  record: {
    type: [Object, null] as PropType<Record<string, any> | null>,
    default: () => null,
  },
  applyName: {
    type: String,
    default: () => '',
  },
  modalType: {
    type: String as PropType<'approve' | 'approveRecord'>,
    default: () => 'approve',
  },
};

export default defineComponent({
  name: '[REPLACE:组件名]',  // 如 EquipmentSubmissionApproval
  props,
  setup(props) {
    const { createMessage } = useMessage();
    const approvalFormRef = ref<[REPLACE:IApprovalForm类型名]>();
    const loading = ref(false);
    const loaded = ref(false);
    const primaryKey = ref('');

    // [REPLACE] 详情组件 ref（用于查看/审批编辑）
    const detailModalRef = ref<[REPLACE:详情组件Ref类型名]>();
    // [REPLACE] 编辑组件 ref（仅用于驳回重发）
    const formRef = ref<[REPLACE:编辑组件Ref类型名]>();

    const state = reactive<{
      detailData: DetailData;
      templatePermission: string;
      operationType: string;
      otherOperationType: string;
    }>({
      detailData: {},
      templatePermission: '',
      operationType: '',
      otherOperationType: '',
    });

    [OPTIONAL:
    // [REPLACE] 当前审批节点类型
    const currentNodeType = computed<[REPLACE:节点类型名]>(() => {
      return OPERATION_TYPE_TO_NODE[state.operationType] || [REPLACE:默认节点];
    });

    // [REPLACE] 业务数据是否可编辑（按审批节点控制）
    const detailEditable = computed(() => {
      if (isRejected.value) return false;
      if (!state.operationType || !OPERATION_TYPE_TO_NODE[state.operationType]) {
        return false;
      }
      return EDITABLE_NODES.includes(currentNodeType.value);
    });
    ]

    // [KEEP] provide 权限
    provide<PermissionData>(ProvideContext.Permission, {
      get templatePermission() { return state.templatePermission; },
      get operationType() { return state.operationType; },
      get otherOperationType() { return state.otherOperationType; },
    });

    onMounted(() => {
      init();
    });

    // [KEEP] 初始化
    async function init() {
      try {
        // [KEEP] businessKey 取法 — 兼容两种模式
        let _primaryKey = '';
        try {
          const businessKey = JSON.parse(props.record?.businessKey || '{}');
          _primaryKey = businessKey.primaryKey || businessKey.id || '';
        } catch {
          // businessKey 解析失败，尝试 variable.json
        }
        if (!_primaryKey && props.record?.variable?.json) {
          try {
            const variable = JSON.parse(props.record.variable.json);
            _primaryKey = variable.businessId || variable.id || '';
          } catch {
            // variable.json 解析失败
          }
        }
        primaryKey.value = _primaryKey;
        await loadDetail(_primaryKey);
        loaded.value = true;
      } catch (error) {
        console.error('初始化失败', error);
      }
    }

    // [KEEP] 权限更新
    const handlePermissionUpdate = (data: {
      templatePermission: string;
      otherOperationType: string;
      operationType: string;
    }) => {
      // [OPTIONAL] MOCK: 支持通过 URL query ?mockOperationType=xxx 强制指定节点，用于测试
      const urlParams = new URLSearchParams(window.location.search);
      const mockOp = urlParams.get('mockOperationType');

      state.templatePermission = data.templatePermission || '';
      state.otherOperationType = data.otherOperationType || '';
      state.operationType = mockOp || (data.operationType === 'null' ? '' : (data.operationType || ''));
    };

    // [KEEP] 是否驳回重新发起
    const isRejected = computed(() => {
      return ['submit_save'].includes(state.templatePermission) && props.modalType === 'approve';
    });

    // [KEEP] 加载详情
    const loadDetail = async (id?: string) => {
      if (!id) return;
      try {
        loading.value = true;
        // [REPLACE] 详情 API 调用
        const res = await [REPLACE:详情API函数名](id);
        if (res?.data) {
          state.detailData = res.data as unknown as DetailData;
        }
      } catch (error) {
        console.error('加载详情数据失败', error);
      } finally {
        loading.value = false;
      }
    };

    // [REPLACE] 提交前校验 & 草稿保存
    const onSubmit = async () => {
      // [KEEP] 驳回重发场景：调用编辑组件的保存方法
      if (isRejected.value) {
        [OPTIONAL:// [REPLACE] 编辑组件 expose 方法名
        return await formRef.value?.[REPLACE:编辑组件expose方法]();]
        [KEEP:return Promise.resolve();]
      }

      [OPTIONAL:
      // [REPLACE] 按审批节点校验并保存业务数据
      if (detailEditable.value) {
        // 1. 校验业务组件数据
        await detailModalRef.value?.[REPLACE:校验方法]();

        // 2. 获取并转换数据
        const detailData = detailModalRef.value?.[REPLACE:获取数据方法]();
        if (detailData && detailData.length > 0) {
          // [REPLACE] 业务数据转换
          const cleanedData = detailData.map((item: any) => {
            // [KEEP] 提取需要保留的基础字段
            const clean: any = {
              id: item.id || undefined,
              submissionId: item.submissionId,
              equipmentName: item.equipmentName,
              equipmentSpecModel: item.equipmentSpecModel,
              materialCode: item.materialCode,
              supplierName: item.supplierName,
              detailRemark: item.detailRemark,
            };

            // [KEEP] 文件字段清洗：提取为后端 FileInfo 格式（去掉前端 uid/status 等）
            const FILE_FIELDS = ['technicalSpecFiles', 'technicalAgreementFiles', 'manufacturerFiles'] as const;
            FILE_FIELDS.forEach((field) => {
              const files = item[field];
              if (Array.isArray(files)) {
                clean[field] = files.map((f: any) => ({
                  fileName: f.name || f.fileName || '',
                  fileUrl: f.path || f.url || f.fileUrl || (f.response?.path) || '',
                  fileType: f.fileType || '',
                  fileSize: f.size || f.fileSize || 0,
                }));
              } else {
                clean[field] = [];
              }
            });

            // [KEEP] 人员字段清洗：LovSelect {label, value} → 后端 {userId, userName}
            const USER_FIELDS = ['techLeaders', 'procurementLeaders'] as const;
            USER_FIELDS.forEach((field) => {
              const users = item[field];
              if (Array.isArray(users)) {
                clean[field] = users.map((u: any) => ({
                  userId: u.value || u.userId || u.uid,
                  userName: u.label || u.userName || u.name,
                }));
              } else {
                clean[field] = [];
              }
            });

            return clean;
          });

          // [REPLACE] 调用业务保存 API
          await [REPLACE:业务保存API函数名](cleanedData);
        }
      }
      ]

      return Promise.resolve();
    };

    // [KEEP] 驳回重发回调
    async function onAfterSbumit() {
      [OPTIONAL:
      if (isRejected.value && primaryKey.value) {
        // [REPLACE] 如需驳回重发后调用 API
        // return await [REPLACE:驳回重发API](primaryKey.value);
      }
      ]
      return Promise.resolve();
    }

    return () => (
      <InnerLayout v-loading={!loaded.value}>
        <div class="office-approval-wrapper">
          <div class="office-card">
            {/* 业务详情模块 */}
            <div>
              {primaryKey.value && (
                <>
                  {isRejected.value ? (
                    // [REPLACE] 驳回重发模式：使用编辑组件（全量编辑）
                    <[REPLACE:编辑组件名]
                      ref={formRef}
                      type="edit"
                      [OPTIONAL:mode="rejected"]
                      id={primaryKey.value}
                      displayMode="embedded"
                    />
                  ) : (
                    // [REPLACE] 详情展示模式：支持查看/审批编辑双模式
                    // - 查看模式（approveRecord）：detailEditable=false，只读
                    // - 审批编辑模式（approve）：detailEditable=true，按 nodeType 开放指定字段编辑
                    <[REPLACE:详情组件名]
                      ref={detailModalRef}
                      displayMode="embedded"
                      v-model:externalData={state.detailData}
                      [OPTIONAL:detailEditable={detailEditable.value}]
                      [OPTIONAL:nodeType={currentNodeType.value}]
                    />
                  )}
                </>
              )}
            </div>

            {/* [KEEP] 审批模块 */}
            {props.modalType !== 'approveRecord' && (
              <[REPLACE:ApprovalForm组件名]
                ref={approvalFormRef}
                class="!mt-[10px]"
                record={{
                  ...(props?.record ?? {}),
                  variable: props?.record?.variable,
                }}
                modalType={props.modalType}
                onParentSubmit={onSubmit}
                onAfterSbumit={onAfterSbumit}
                onUpdate:permission={handlePermissionUpdate}
              />
            )}
          </div>
        </div>
      </InnerLayout>
    );
  },
});
```

---

## Block 2: 审批表单组件 XxxApprovalForm.tsx

```typescript
/**
 * [REPLACE:业务模块名] 审批表单组件
 */

import { defineComponent, ref, computed, onMounted, PropType } from 'vue';
import { Card, Form, Button, Space, Select, FormItem, Textarea } from 'ant-design-vue';
import { useModal } from '@/components/Modal';
import { cloneDeep } from 'lodash-es';
import { useMessage } from '@/hooks/web/useMessage';
import { useI18n } from '@/hooks/web/useI18n';
import { useTabs } from '@/hooks/web/useTabs';
import { completeTodoApi, getOperationRole } from '@/views/office/todo/service/api';
import ApprovalRecord from '../../approval-record';
import Track from '../../../track.vue';
import ForwardModal from '../../forward-modal';
import TodoViewModal from '../../view-modal';
import Upload from '@/components/Upload/Upload.vue';

// [KEEP] 审批数据类型
interface TodoType {
  id: string;
  procInst: string;
  variable: {
    json: string;
  };
  comment: string;
  approvalOpinion?: string;
  passType?: string;
  signatureComment?: string;
}

// [KEEP] props 定义
const props = {
  record: { type: [Object, null] as PropType<Record<string, any> | null>, default: () => null },
  modalType: { type: String as PropType<'approve' | 'approveRecord'>, default: () => 'approve' },
  onSubmit: { type: Function as PropType<() => Promise<void>> },
  onParentSubmit: { type: Function as PropType<() => Promise<void>> }, // 用来处理父级提交
  onAfterSbumit: { type: Function as PropType<(templatePermission: string) => Promise<void>> }, // 提交成功后回调
};

// [REPLACE] 仅替换类型名
export type [REPLACE:IApprovalForm类型名] = {
  handleAgree: () => Promise<void>;
};

const [REPLACE:ApprovalForm组件名] = defineComponent({
  name: '[REPLACE:组件名]',  // 如 EquipmentSubmissionApprovalForm
  props,
  setup(props, { emit, expose }) {
    const { createMessage } = useMessage();
    const { t } = useI18n();
    const tabs = useTabs();

    const loading = ref(false);
    const actHiAttachments = ref<any[]>([]);
    const templatePermission = ref<string>('');
    const otherOperationType = ref<string>('');
    const operationType = ref<string>('');

    // [KEEP] 获取操作权限
    const getOperationPermission = async () => {
      try {
        const res = await getOperationRole({ taskId: props.record?.id });
        if (res?.code === 0) {
          const { templateKey = '' } = res.data ?? {};
          templatePermission.value = templateKey;
          otherOperationType.value = res?.data?.otherOperationType ?? '';
          operationType.value = res?.data?.operationType ?? '';
          // 通过 emit 将权限信息传回父组件
          emit('update:permission', {
            templatePermission: templatePermission.value,
            otherOperationType: otherOperationType.value,
            operationType: operationType.value,
          });
        }
      } catch (error) {
        console.error('获取操作权限失败', error);
      }
    };

    onMounted(() => {
      getOperationPermission();
    });

    // [KEEP] 表单数据初始化
    const initModel: TodoType = {
      id: '',
      procInst: '',
      variable: {
        json: '',
      },
      comment: t('common.readAlready', '已阅'),
      approvalOpinion: '',
      passType: '',
      signatureComment: '',
    };

    const modelForm = ref<TodoType>(cloneDeep(initModel));
    const formRef = ref<any>();

    // [KEEP] 权限计算属性
    const effectiveTemplatePermission = computed(() => templatePermission.value);
    const effectiveOtherOperationType = computed(() => otherOperationType.value);

    // [KEEP] 是否最终节点
    const isEndEvent = computed(() => {
      return effectiveOtherOperationType.value === 'endEvent' ? true : false;
    });

    // [KEEP] 判断当前模式
    const isViewMode = computed(() => {
      return effectiveTemplatePermission.value && ['card_approve_make_copy'].includes(effectiveTemplatePermission.value);
    });

    const isSubmitMode = computed(() => {
      return ['submit_save', 'apply_system'].includes(effectiveTemplatePermission.value);
    });

    const isApproveRejectMode = computed(() => {
      return ['approve_reject'].includes(effectiveTemplatePermission.value);
    });

    const isApproveOnlyMode = computed(() => {
      return ['approve'].includes(effectiveTemplatePermission.value);
    });

    const isReadMode = computed(() => {
      return effectiveTemplatePermission.value && ['card_approve_make_copy'].includes(effectiveTemplatePermission.value);
    });

    // [KEEP] 同意审批
    const handleAgree = async () => {
      try {
        loading.value = true;
        props?.onParentSubmit && (await props.onParentSubmit());
        await formRef.value?.validate();
        const commentParse = {
          _pass: 'approve',
          comment: modelForm.value.approvalOpinion,
        };
        const params = {
          id: props.record?.id,
          procInst: props.record?.procInstId,
          variable: {
            ...props.record?.variable,
            json: JSON.stringify({
              ...JSON.parse(props.record?.variable?.json || '{}'),
              passType: modelForm.value.passType,
            }),
          },
          comment: JSON.stringify(commentParse),
          actHiAttachments: actHiAttachments.value?.map(item => {
            return {
              name: item.name,
              url: item.response?.path,
            };
          }),
        };
        await completeTodoApi(params);
        createMessage.success(t('constructionDesign.message.approveSuccess', '审批成功'));
        props?.onAfterSbumit && (await props.onAfterSbumit(effectiveTemplatePermission.value));
        tabs.closeCurrent();
      } catch (error) {
        const errorField = (error as any)?.errorFields?.[0];
        if (errorField) {
          const msg = errorField.errors?.[0];
          msg && createMessage.warning(msg);
        }
      } finally {
        loading.value = false;
      }
    };

    // [KEEP] 驳回审批
    const handleReject = async () => {
      try {
        loading.value = true;
        await formRef.value?.validate();
        const commentParse = {
          _pass: 'reject',
          comment: modelForm.value.approvalOpinion,
        };
        const params = {
          id: props.record?.id,
          procInst: props.record?.procInstId,
          variable: {
            ...props.record?.variable,
            json: JSON.stringify({
              ...JSON.parse(props.record?.variable?.json || '{}'),
              passType: modelForm.value.passType,
            }),
          },
          comment: JSON.stringify(commentParse),
          actHiAttachments: actHiAttachments.value?.map(item => {
            return {
              name: item.name,
              url: item.response?.path,
            };
          }),
        };
        await completeTodoApi(params);
        createMessage.success(t('common.rejectSuccess', '驳回成功'));
        props?.onAfterSbumit && (await props.onAfterSbumit(effectiveTemplatePermission.value));
        tabs.closeCurrent();
      } catch (error) {
        const errorField = (error as any)?.errorFields?.[0];
        if (errorField) {
          const msg = errorField.errors?.[0];
          msg && createMessage.warning(msg);
        }
      } finally {
        loading.value = false;
      }
    };

    // [KEEP] 已阅
    const handleRead = async () => {
      try {
        loading.value = true;
        await formRef.value?.validate();
        const commentParse = {
          _pass: 'have_read',
          comment: modelForm.value.signatureComment,
        };
        const params = {
          id: props.record?.id,
          procInst: props.record?.procInstId,
          variable: { json: JSON.stringify({ pass: 'have_read' }) },
          comment: JSON.stringify(commentParse),
          actHiAttachments: actHiAttachments.value?.map(item => {
            return {
              name: item.name,
              url: item.response?.path,
            };
          }),
        };
        await completeTodoApi(params);
        createMessage.success(t('layout.setting.operatingTitle', '操作成功'));
        props?.onAfterSbumit && (await props.onAfterSbumit(effectiveTemplatePermission.value));
        tabs.closeCurrent();
      } catch (error) {
        const errorField = (error as any)?.errorFields?.[0];
        if (errorField) {
          const msg = errorField.errors?.[0];
          msg && createMessage.warning(msg);
        }
      } finally {
        loading.value = false;
      }
    };

    // [KEEP] 转发
    const handleForward = () => {
      openForwardModal(true, { id: props.record?.id, type: 'forward' });
    };

    // [KEEP] 弹窗注册
    const [registerForwardModal, { openModal: openForwardModal }] = useModal();
    const [registerViewModal] = useModal();

    const handleForwardConfirm = () => {
      tabs.closeCurrent();
    };

    const handleViewSubmit = () => {
      tabs.closeCurrent();
    };

    // [KEEP] 提交（补录/重新申请场景）
    const handleSubmit = async () => {
      try {
        loading.value = true;
        props.onSubmit && (await props.onSubmit());
        props.onParentSubmit && (await props.onParentSubmit());
        await formRef.value?.validate();
        modelForm.value.passType = '1';
        await handleAgree();
      } finally {
        loading.value = false;
      }
    };

    // [KEEP] 取消
    const handleCancel = () => {
      tabs.closeCurrent();
    };

    const handleRemove = async (file: any) => {
      actHiAttachments.value = actHiAttachments.value.filter(v => v.uid !== file.uid);
    };

    // [KEEP] 普通审批模式渲染
    const renderApproveMode = () => {
      if (props.modalType !== 'approve' || isViewMode.value || isSubmitMode.value) return null;

      const exprotMethods: [REPLACE:IApprovalForm类型名] = {
        handleAgree: handleAgree,
      };
      expose(exprotMethods);
      return (
        <Card
          class="FormLabelWithd100"
          size="small"
          title={operationType.value === 'approve_spjl' ? t('Office.Todo.conclusion', '审批结论') : t('Office.Todo.comments', '审批意见')}>
          <Form ref={(el: any) => (formRef.value = el)} model={modelForm.value}>
            {/* [OPTIONAL] 审批结论下拉 — 仅 approve_spjl 节点需要 */}
            {operationType.value === 'approve_spjl' && (
              <FormItem
                class="!w-[33%]"
                colon={false}
                name="passType"
                label={t('Office.Todo.conclusion', '审批结论')}
                rules={[{ required: true, message: t('Office.Todo.selectConclusion', '请选择审批结论') }]}
              >
                <Select
                  v-model:value={modelForm.value.passType}
                  placeholder={t('common.selectPlaceholder')}
                  allowClear
                  options={[
                    { label: t('common.approvalStatus.pass', '通过'), value: '1' },
                    { label: t('common.approvalStatus.reject', '不通过'), value: '2' },
                  ]}
                />
              </FormItem>
            )}

            <FormItem class="!w-[100%]" colon={false} label={t('Office.Todo.comments', '审批意见')}>
              <Textarea
                v-model:value={modelForm.value.approvalOpinion}
                maxlength={1000}
                placeholder={t('common.pleaseInput') + '（' + t('common.input.max.length.1000') + '）'}
                autoSize={{ minRows: 3 }}
                allowClear
              />
            </FormItem>
            <FormItem class="!w-[100%]" colon={false} label={t('common.attachment', '附件')}>
              <Upload
                v-model={actHiAttachments.value}
                bucketName="public"
                path="fileUrl"
                useFileCard={true}
                multiple={true}
                showDelete={true}
                showDownload={true}
                showView={true}
                showName={true}
                showTime={false}
                onRemove={(file: any) => handleRemove(file)}
              />
            </FormItem>
          </Form>
        </Card>
      );
    };

    // [KEEP] 已阅模式渲染
    const renderReadMode = () => {
      if (!isReadMode.value) return null;

      return (
        <Card class="FormLabelWithd100">
          <Form ref={(el: any) => (formRef.value = el)} model={modelForm.value}>
            <div class="cellBox">
              <span class="cellBoxTag"></span>
              {t('common.readAlready', '已阅')}
            </div>
            <FormItem class="!w-[100%]" colon={false} label={t('common.signatureOpinion', '签字意见')} rules={[{ required: true }]}>
              <Textarea
                v-model:value={modelForm.value.signatureComment}
                maxlength={1000}
                placeholder={t('common.pleaseInput') + '（' + t('common.input.max.length.1000') + '）'}
                autoSize={{ minRows: 3 }}
                allowClear
              />
            </FormItem>
            <FormItem class="!w-[100%]" colon={false} label={t('common.attachment', '附件')}>
              <Upload
                v-model={actHiAttachments.value}
                bucketName="public"
                path="fileUrl"
                useFileCard={true}
                multiple={true}
                showDelete={true}
                showDownload={true}
                showView={true}
                showName={true}
                showTime={false}
                onRemove={(file: any) => handleRemove(file)}
              />
            </FormItem>
          </Form>
        </Card>
      );
    };

    // [KEEP] 审批记录渲染
    const renderApprovalRecord = () => {
      if (props.modalType !== 'approveRecord') return null;

      return (
        <Card>
          <ApprovalRecord procInstId={props.record?.procInst} />
          <Track procInstId={props.record?.procInst} />
        </Card>
      );
    };

    // [KEEP] 操作按钮渲染
    const renderButtons = () => {
      if (props.modalType !== 'approve') return null;

      return (
        <div class="office-btn-wrapper absolute left-0 bottom-0 z-100 w-full h-[60px]">
          <Space class="!ml-10px">
            {/* 补录/重新申请 */}
            {isSubmitMode.value && (
              <>
                <Button type="primary" onClick={handleSubmit}>
                  {t('common.submitText', '提交')}
                </Button>
                <Button type="default" onClick={handleCancel}>
                  {t('common.cancelText', '取消')}
                </Button>
              </>
            )}

            {/* 同意/驳回/抄送 */}
            {isApproveRejectMode.value && (
              <>
                <Button type="primary" onClick={handleAgree}>
                  {(isEndEvent.value && t('Office.Todo.ratify', '批准')) || t('Office.Todo.agree', '同意')}
                </Button>
                <Button type="default" disabled={modelForm.value.passType == '1'} onClick={handleReject}>
                  {t('Office.Todo.reject', '驳回')}
                </Button>
                <Button type="default" onClick={handleForward}>
                  {t('Office.Todo.cc', '抄送')}
                </Button>
              </>
            )}

            {/* 仅同意 */}
            {isApproveOnlyMode.value && (
              <>
                <Button type="primary" onClick={handleAgree}>
                  {(isEndEvent.value && t('Office.Todo.ratify', '批准')) || t('Office.Todo.agree', '同意')}
                </Button>
                <Button type="default" onClick={handleForward}>
                  {t('Office.Todo.cc', '抄送')}
                </Button>
              </>
            )}

            {/* 已阅 */}
            {isReadMode.value && (
              <Button type="primary" onClick={handleRead}>
                {t('common.readAlready', '已阅')}
              </Button>
            )}
          </Space>
        </div>
      );
    };

    return () => (
      <article class="office-approval-content pb-[60px]">
        {renderApproveMode()}
        {renderReadMode()}
        {renderApprovalRecord()}
        {renderButtons()}

        <ForwardModal onRegister={registerForwardModal} onSuccess={handleForwardConfirm} />
        <TodoViewModal onRegister={registerViewModal} onSuccess={handleViewSubmit} />
      </article>
    );
  },
});

export default [REPLACE:ApprovalForm组件名];
```

---

## Block 3: 审批模板页面中的 LovSelect 人员选择配置

> 适用：审批节点需要选择技术负责人、采购负责人等人员字段
> 注意：项目实际使用 `config` 属性配置 LovSelect，而非 `lovCode`

```typescript
import LovSelect from '@/components/LovSelect';
import { getStaffApi } from '[REPLACE:当前业务API路径]';

// [KEEP] LovSelect 配置 - 人员选择
const getStaff = async (arg: any) => {
  const { searchKey, ...rest } = arg;
  const res = await getStaffApi({ name: searchKey, ...rest });
  if (res?.code === 0) {
    return res;
  }
  return { code: 0, data: { records: [] } };
};

const userLovConfig = computed(() => ({
  labelField: 'name',
  valueField: 'uid',
  modalConfig: { title: '选择人员', width: '800px' },
  formConfig: {
    showAdvancedSearch: false,
    alwaysShowLines: 1,
    schemas: [
      { field: 'uid', label: '工号', component: 'Input', componentProps: { placeholder: '请输入' } },
      { field: 'name', label: '姓名', component: 'Input', componentProps: { placeholder: '请输入' } },
    ],
  },
  tableConfig: {
    columns: [
      { title: '工号', dataIndex: 'uid', width: 120 },
      { title: '姓名', dataIndex: 'name', width: 180 },
      { title: '手机号', dataIndex: 'mobile', width: 180 },
      { title: '部门', dataIndex: 'deptmentName', width: 200 },
    ],
    rowKey: 'uid',
    api: getStaff,
  },
}));
```

在表格/表单中使用：

```tsx
<LovSelect
  v-model:value={text}
  config={userLovConfig.value}
  mode="multiple"
  disabled={!editable}
  onChange={(v) => handleUserSelectChange(index, 'techLeaders', v)}
/>
```

---

## Block 4: 审批提交时的数据清洗模板

> 适用：审批页 `onSubmit` 中，从详情组件获取的数据包含前端组件注入的格式，需要清洗为后端接口格式

### 4.1 文件字段清洗

```typescript
// [KEEP] 文件字段：提取为后端 FileInfo 格式（去掉前端 uid/status/response 等）
const FILE_FIELDS = ['technicalSpecFiles', 'technicalAgreementFiles', 'manufacturerFiles'] as const;
FILE_FIELDS.forEach((field) => {
  const files = item[field];
  if (Array.isArray(files)) {
    clean[field] = files.map((f: any) => ({
      fileName: f.name || f.fileName || '',
      fileUrl: f.path || f.url || f.fileUrl || (f.response?.path) || '',
      fileType: f.fileType || '',
      fileSize: f.size || f.fileSize || 0,
    }));
  } else {
    clean[field] = [];
  }
});
```

### 4.2 人员字段清洗（LovSelect）

```typescript
// [KEEP] 人员字段：LovSelect {label, value} → 后端 {userId, userName}
const USER_FIELDS = ['techLeaders', 'procurementLeaders'] as const;
USER_FIELDS.forEach((field) => {
  const users = item[field];
  if (Array.isArray(users)) {
    clean[field] = users.map((u: any) => ({
      userId: u.value || u.userId || u.uid,
      userName: u.label || u.userName || u.name,
    }));
  } else {
    clean[field] = [];
  }
});
```

### 4.3 人员字段清洗（纯 ID 数组）

```typescript
// [KEEP] 人员字段：提取为用户 ID 数组（字符串数组）
const USER_FIELDS = ['techLeaders', 'procurementLeaders'] as const;
USER_FIELDS.forEach((field) => {
  const users = item[field];
  if (Array.isArray(users)) {
    clean[field] = users.map((u: any) => u.value || u.userId || u.uid);
  } else {
    clean[field] = [];
  }
});
```

---

## 目录结构参考

```
src/views/office/todo/components/
├── register.tsx                                    # [修改] 在 map 中新增 key
├── apply-modal/
│   ├── [REPLACE:camelCaseName].tsx                 # [新增] Block 1 生成的审批模板页面
│   └── approval-form/
│       └── [REPLACE:PascalCaseName]ApprovalForm.tsx # [新增] Block 2 生成的审批表单组件
```

## 标记说明

| 标记 | 含义 |
|------|------|
| `[REPLACE]` | 必须根据业务信息替换的内容 |
| `[KEEP]` | 保持模板代码不变 |
| `[OPTIONAL]` | 可选功能，根据需求决定是否保留 |
| `[NOTE]` | 需要特别注意的细节 |
