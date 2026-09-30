# 表单页代码模板

> 基准代码来源：`src/views/eng-manage/start-apply/components/` 实际上线版本
> 所有 `[REPLACE]` 标记的区域需要根据 PRD/API 文档替换
> 所有 `[KEEP]` 标记的区域保持模板代码不变

---

## Block 1: api/types.ts

```typescript
// [REPLACE] 整个文件的类型定义根据 API 文档替换

// [REPLACE] 表单模式类型 — 根据业务是否需要多种申请类型
export type ApplicationType = 'FIRST' | 'SECOND' | 'RESTART';

// [KEEP] 表单操作类型
export type FormMode = 'edit' | 'view';

// [REPLACE] 业态类型 — 根据业务调整（1=风电, 2=光伏, 3=储能 是通用约定）
export type ProjectType = '1' | '2' | '3';

// [REPLACE] 表单数据类型 — 根据提交接口的请求体定义
// 注意：将所有 Section 的字段扁平化到一个类型中
export interface StartApplyFormData {
  id: string;
  // [REPLACE] 核心字段
  businessKey: string;
  applyNo: string;
  applicantId: string;
  applicantName: string;
  applicantDept: string;
  applicantDeptName: string;
  applyType: ApplicationType | undefined;
  projectId: string;
  // [REPLACE] 基础信息字段
  projectName: string;
  projectCode: string;
  projectType: string;
  typeDetail: string;
  provinceCode: string;
  provinceName: string;
  cityCode: string;
  cityName: string;
  countyCode: string;
  countyName: string;
  detailedAddress: string;
  subName: string;
  subCode: string;
  regionId: string;
  regionName: string;
  businessMode: string;
  indicatorCapacity: number | undefined;
  designCapacity: number | undefined;
  designCapacityMwh: number | undefined;
  isOmsService: number | undefined;
  isSafetyInsurance: number | undefined;
  // [REPLACE] 业务字段
  applyCapacity: number | undefined;
  applyStorageMw: number | undefined;
  applyStorageMwh: number | undefined;
  applySummary: string;
  unitCost: number | undefined;
  similarProjectCost: number | undefined;
  fullCapacityDate: string;
  icChangeDate: string;
  handoverDate: string;
  restartReason: string;
  attachmentList: any[];
  relatedProcessList: any[];
  // [REPLACE] 根据 API 文档添加更多字段...
}

// [REPLACE] 基础信息子类型 — 用于 Section 组件的 props
export interface BasicInfoForm {
  projectId: string;
  projectName: string;
  projectCode: string;
  projectType: string;
  typeDetail: string;
  provinceCode: string;
  provinceName: string;
  cityCode: string;
  cityName: string;
  countyCode: string;
  countyName: string;
  detailedAddress: string;
  subName: string;
  subCode: string;
  regionId: string;
  regionName: string;
  businessMode: string;
  indicatorCapacity: number | undefined;
  indicatorStorageMwh: number | undefined;
  designCapacity: number | undefined;
  designCapacityMwh: number | undefined;
  isOmsService: number | undefined;
  isSafetyInsurance: number | undefined;
}

// [REPLACE] 详情类型 — 根据详情 API 返回字段替换
export interface StartApplyDetail {
  id: string;
  // 根据 API 文档添加详情字段...
  // 详情通常比 FormData 多一些只读展示字段（如审批状态、审批时间等）
}

// [REPLACE] 其他 Section 子类型 — 按 PRD 分组定义
// export interface XxxSectionForm { ... }

// [KEEP] 附件类型配置
export interface AttachmentItem {
  id?: string;
  filename: string;
  filePath: string;
  attachmentType?: string;
  [key: string]: any;
}
```

---

## Block 2: api/index.ts

```typescript
import { defHttp } from '@/utils/http/axios';
import type { StartApplyFormData, StartApplyDetail } from './types';

// [REPLACE] API 前缀 — 替换为实际模块路径
export enum Api {
  Prefix = '/api/pm-engineering/start-apply',
}

// [REPLACE] 获取详情 — 替换接口路径
export function getStartApplyDetail(params: { id: string }) {
  return defHttp.post<{ code: number; data: StartApplyDetail; message: string }>({
    url: Api.Prefix + '/getDetail',
    data: params,
  });
}

// [OPTIONAL] 二次申请详情 — 如果业务有多种申请类型
export function getSecondaryDetail(params: { id: string }) {
  return defHttp.post<{ code: number; data: StartApplyDetail; message: string }>({
    url: Api.Prefix + '/getSecondaryDetail',
    data: params,
  });
}

// [OPTIONAL] 重新申请详情 — 如果业务有多种申请类型
export function getRestartDetail(params: { id: string }) {
  return defHttp.post<{ code: number; data: StartApplyDetail; message: string }>({
    url: Api.Prefix + '/getRestartDetail',
    data: params,
  });
}

// [REPLACE] 暂存 — 替换接口路径
export function saveDraft(data: Partial<StartApplyFormData>) {
  return defHttp.post<{ code: number; data: string; message: string }>({
    url: Api.Prefix + '/saveDraft',
    data,
  });
}

// [REPLACE] 提交 — 替换接口路径
export function submitApply(data: Partial<StartApplyFormData>) {
  return defHttp.post<{ code: number; message: string }>({
    url: Api.Prefix + '/submit',
    data,
  });
}

// [OPTIONAL] 验证项目选择 — 如果有项目选择功能
export function validateProjectSelection(params: { projectId: string }) {
  return defHttp.post<{ code: number; message: string }>({
    url: Api.Prefix + '/validateProject',
    data: params,
  });
}

// [OPTIONAL] 项目选择前的校验 — 如果有施工组织评审等前置校验
export function validateProjectSelectionOrgProjectSelection(projectId: string) {
  return defHttp.post({
    url: Api.Prefix + `/validateProjectSelection/${projectId}`,
  });
}

// [OPTIONAL] 流程通用查询 — 如果有关联流程功能
export function procinstCommon(params: { projectId: string; categoryKey: string }) {
  return defHttp.post({
    url: '/api/pm-bpm/procinstCommon/list',
    data: params,
  });
}

// [OPTIONAL] 根据 PRD 添加更多 API 函数...
```

---

## Block 3: utils/dataTransform.ts

```typescript
import type { StartApplyDetail, BasicInfoForm } from '../api/types';

// [REPLACE] 详情 → 基础信息表单映射
export function detailToBasicInfo(detail: Partial<StartApplyDetail>): Partial<BasicInfoForm> {
  return {
    projectId: detail.projectId || '',
    projectName: detail.projectName || '',
    projectCode: detail.projectCode || '',
    projectType: detail.projectType || '',
    typeDetail: detail.typeDetail || '',
    provinceCode: detail.provinceCode || '',
    provinceName: detail.provinceName || '',
    cityCode: detail.cityCode || '',
    cityName: detail.cityName || '',
    countyCode: detail.countyCode || '',
    countyName: detail.countyName || '',
    detailedAddress: detail.detailedAddress || '',
    subName: detail.subName || '',
    subCode: detail.subCode || '',
    regionId: detail.regionId || '',
    regionName: detail.regionName || '',
    businessMode: detail.businessMode || '',
    indicatorCapacity: detail.indicatorCapacity,
    designCapacity: detail.designCapacity,
    isOmsService: detail.isOmsService,
    isSafetyInsurance: detail.isSafetyInsurance,
  };
}

// [REPLACE] 详情 → 其他 Section 映射 — 按 PRD 添加
// export function detailToXxxInfo(detail: Partial<StartApplyDetail>): Partial<XxxForm> { ... }

// [KEEP] 业态 → 容量单位后缀
export function addon(projectType: string): string | null {
  const map: Record<string, string> = {
    '1': 'MW',     // 风电
    '2': 'MWp',    // 光伏
    '3': 'MW/MWh', // 储能
  };
  return map[projectType] || null;
}
```

---

## Block 4: useForm.ts

```typescript
import { ref, reactive, computed } from 'vue';
import { message } from 'ant-design-vue';
import type { FormInstance } from 'ant-design-vue';
import { saveDraft, submitApply, getStartApplyDetail } from './api';
// [OPTIONAL] import { getSecondaryDetail, getRestartDetail } from './api';
import type { StartApplyFormData, FormMode, StartApplyDetail, ApplicationType } from './api/types';

/** [REPLACE] 接口不支持的字段列表，提交前需要过滤 */
const EXCLUDED_FIELDS: string[] = [];

/**
 * 清洗表单数据，处理组件值 → 后端格式的转换
 *
 * 必须处理的转换场景：
 * 1. LovSelect 单选：{label, value} 对象 → 提取 value 字符串
 * 2. LovSelect 多选：{label, value}[] 数组 → 提取 value 数组或 {userId, userName}[]
 * 3. DictSelect 多选：string[] → join(',') 字符串
 * 4. Upload 文件列表：提取 url/path 为后端需要的格式
 * 5. 过滤接口不支持的字段
 */
function cleanFormData(data: StartApplyFormData): Partial<StartApplyFormData> {
  const result: Partial<StartApplyFormData> = {};

  for (const key of Object.keys(data) as (keyof StartApplyFormData)[]) {
    // 过滤接口不支持的字段
    if (EXCLUDED_FIELDS.includes(key)) continue;

    let value = data[key];

    // LovSelect 单选：提取 value 字符串
    if (key === 'projectChiefId' && value && typeof value === 'object') {
      value = (value as Recordable).value || (value as Recordable).uid || (value as Recordable).id || '';
    }

    // LovSelect 多选：转换为 {userId, userName}[]
    if (key === 'reviewers' && Array.isArray(value)) {
      value = value.map((item: Recordable) => ({
        userId: item.value || item.uid || item.id || item.userId || '',
        userName: item.label || item.name || item.userName || '',
      }));
    }

    // DictSelect 多选：数组转逗号分隔字符串
    if (key === 'majors' && Array.isArray(value)) {
      value = value.join(',');
    }

    // Upload 文件列表：提取后端需要的字段
    if (key === 'attachmentList' && Array.isArray(value)) {
      value = value.map((file: any, idx: number) => ({
        fileName: file.name || file.fileName,
        fileSize: file.size || file.fileSize || 0,
        fileUrl: file.response?.path || file.response?.data || file.fileUrl || file.url || '',
        fileSuffix: (file.name || file.fileName || '').split('.').pop() || '',
        sortOrder: idx,
      }));
    }

    result[key] = value;
  }

  return result;
}

/**
 * 后端详情数据 → 前端表单数据（回显转换）
 *
 * 必须处理的转换场景（与 cleanFormData 对称）：
 * 1. 后端返回 userId 字符串 → LovSelect 需要的 {label, value} 对象
 * 2. 后端返回 {userId, userName}[] → LovSelect 多选对象数组
 * 3. 后端返回逗号分隔字符串 → DictSelect 多选 string[]
 * 4. 后端返回平铺文件列表 → 按 fileType 分类到各字段
 */
function detailToFormData(detail: Partial<StartApplyDetail>): Partial<StartApplyFormData> {
  const result: Partial<StartApplyFormData> = {};

  // 基础字段直接复制
  Object.assign(result, detail);

  // LovSelect 单选回显：userId 字符串 → {label, value} 对象
  if (detail.projectChiefId) {
    result.projectChiefId = {
      value: detail.projectChiefId,
      label: detail.projectChiefName || '',
    } as any;
  }

  // LovSelect 多选回显：{userId, userName}[] → {value, label}[]
  if (detail.reviewers && Array.isArray(detail.reviewers)) {
    result.reviewers = detail.reviewers.map((r: any) => ({
      value: r.userId,
      label: r.userName,
      uid: r.userId,
      name: r.userName,
    })) as any;
  }

  // DictSelect 多选回显：逗号字符串 → string[]
  if (detail.majors && typeof detail.majors === 'string') {
    result.majors = detail.majors.split(',').filter(Boolean) as any;
  }

  // 文件列表回显：按 fileType 分类（示例：1=常规方案, 2=优化方案, 3=工程量对比）
  if (detail.fileList && Array.isArray(detail.fileList)) {
    const conventionalSchemeFileList: any[] = [];
    const optimizedSchemeFileList: any[] = [];
    const comparisonFileList: any[] = [];

    detail.fileList.forEach((f: any) => {
      const fileObj = {
        uid: f.id || `file_${f.sortOrder || Math.random()}`,
        name: f.fileName,
        fileName: f.fileName,
        size: f.fileSize,
        fileSize: f.fileSize,
        url: f.fileUrl,
        fileUrl: f.fileUrl,
        status: 'done',
      };
      if (f.fileType === 1) conventionalSchemeFileList.push(fileObj);
      else if (f.fileType === 2) optimizedSchemeFileList.push(fileObj);
      else if (f.fileType === 3) comparisonFileList.push(fileObj);
    });

    result.conventionalSchemeFileList = conventionalSchemeFileList as any;
    result.optimizedSchemeFileList = optimizedSchemeFileList as any;
    result.comparisonFileList = comparisonFileList as any;
  }

  return result;
}

export interface UseFormProps {
  mode?: ApplicationType;
  type?: FormMode;
  id?: string;
  projectId?: string;
}

export function useForm(props: UseFormProps) {
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const saving = ref(false);
  const applicationType = ref<ApplicationType>('FIRST');
  const formType = ref<FormMode>(props?.type || 'edit');

  // [REPLACE] 表单数据模型 - 严格遵循接口 Request 定义
  const modelRef = reactive<StartApplyFormData>({
    id: '',
    // 核心字段默认值...
    projectId: '',
    // 基础信息字段默认值...
    projectName: '',
    projectCode: '',
    projectType: '',
    // 业务字段默认值...
    applyCapacity: undefined,
    applySummary: '',
    attachmentList: [],
    relatedProcessList: [],
    // 根据 API 文档添加更多字段默认值...
  });

  // 详情数据（用于展示只读信息）
  const detailRef = reactive<Partial<StartApplyDetail>>({});

  // 加载详情数据
  const loadDetail = async () => {
    if (!props.id) return;
    loading.value = true;

    try {
      const res = await getStartApplyDetail({ id: props.id });
      if (res.code === 0 && res.data) {
        const data = res.data;
        Object.assign(detailRef, data);
        // [KEEP] 使用 detailToFormData 做回显转换（处理 LovSelect/DictSelect/Upload 等格式）
        const formData = detailToFormData(data);
        Object.assign(modelRef, formData);
      }
    } finally {
      loading.value = false;
    }
  };

  // [REPLACE] 获取 applicationType
  const getApplicationType = (): ApplicationType => {
    const isView = formType.value === 'view';
    return isView ? detailRef.applyType || modelRef.applyType || 'FIRST' : props.mode || 'FIRST';
  };

  // 提交申请
  const submit = async () => {
    // [REPLACE] 添加业务校验逻辑
    saving.value = true;
    try {
      const cleanData = cleanFormData(modelRef);
      const submitData = { ...cleanData, applyType: getApplicationType() } as StartApplyFormData;
      const res = await submitApply(submitData);
      if (res.code === 0) {
        message.success('提交成功');
        return Promise.resolve();
      } else {
        return Promise.reject(res.message);
      }
    } catch (error) {
      return Promise.reject(error);
    } finally {
      saving.value = false;
    }
  };

  // 保存草稿
  const saveDraftFn = async () => {
    saving.value = true;
    try {
      const cleanData = cleanFormData(modelRef);
      const submitData = { ...cleanData, applyType: getApplicationType() };
      const res = await saveDraft(submitData);
      if (res.code === 0) {
        if (res.data) {
          modelRef.id = res.data;
        }
        return Promise.resolve();
      } else {
        return Promise.reject(res.message);
      }
    } catch (error) {
      return Promise.reject(error);
    } finally {
      saving.value = false;
    }
  };

  // [REPLACE] 根据 mode/type 计算表单配置
  const formConfig = computed(() => {
    const isView = formType.value === 'view';
    const applyType = (isView ? detailRef.applyType || modelRef.applyType : props.mode) || 'FIRST';

    return {
      isFirstStart: applyType === 'FIRST',
      isEdit: formType.value === 'edit',
      isView,
      title: isView ? '表单详情' : '新建表单',
    };
  });

  return {
    formRef,
    modelRef,
    detailRef,
    loading,
    saving,
    formConfig,
    loadDetail,
    submit,
    saveDraft: saveDraftFn,
  };
}
```

---

## Block 5: index.tsx（表单容器）

```tsx
import { defineComponent, PropType, watch, computed, ref } from 'vue';
import { Button, Form, Spin, Card } from 'ant-design-vue';
import { BasicModal, useModal } from '@/components/Modal';
import { useForm } from './useForm';
// [REPLACE] 导入各 Section 组件
import BasicInfoSection from './components/BasicInfoSection';
// import XxxSection from './components/XxxSection';
import type { FormMode, BasicInfoForm, ApplicationType } from './api/types';
// [REPLACE] 导入数据转换函数
// import { detailToBasicInfo } from './utils/dataTransform';
import styles from './style.module.less';

export type DisplayMode = 'modal' | 'embedded';

export interface Props {
  open?: boolean;
  mode?: ApplicationType;
  type?: FormMode;
  id?: string;
  projectId?: string;
  displayMode?: DisplayMode;
}

// [RULE 3] expose 类型声明 — 必须定义对外抛出的类型接口
export interface XxxFormRef {
  validate: () => Promise<void>;
  submit: () => Promise<void>;
  saveDraft: () => Promise<void>;
  approveSaveDraft: () => Promise<void>;
  getFormData: () => Record<string, any>;
  resetForm: () => void;
}

export default defineComponent({
  // [REPLACE] 组件名 — 替换为 PascalCase 模块名 + Form
  name: 'XxxFormModal',

  props: {
    open: { type: Boolean },
    mode: { type: String as PropType<ApplicationType>, default: 'FIRST' },
    type: { type: String as PropType<FormMode>, default: 'edit' },
    id: String,
    projectId: String,
    displayMode: { type: String as PropType<DisplayMode>, default: 'modal' },
  },

  emits: ['update:open', 'success'],

  setup(props, { emit, expose }) {
    const { formRef, modelRef, detailRef, loading, saving, formConfig, loadDetail, submit, saveDraft } = useForm(props);

    const isModalMode = computed(() => props.displayMode === 'modal');
    const [registerModal] = useModal();

    // [KEEP] 子组件 ref
    const basicInfoSectionRef = ref();
    // const xxxSectionRef = ref();

    // [KEEP] 使用 computed 从 modelRef 提取子模块数据（双向绑定）
    // 原理：modelRef 是全量扁平数据，computed 的 get/set 做扁平→分组的映射
    const basicInfoState = computed<BasicInfoForm>({
      get: () => ({
        ...modelRef,
      }),
      set: val => {
        Object.assign(modelRef, { ...val });
      },
    });

    // [REPLACE] 其他 Section 的 computed — 按 PRD 分组添加
    // const xxxState = computed<XxxForm>({
    //   get: () => ({ ...modelRef, /* 提取对应字段 */ }),
    //   set: val => { Object.assign(modelRef, val); /* 同步各字段 */ },
    // });

    // [KEEP] 监听详情数据加载，同步到 modelRef
    watch(
      () => detailRef,
      val => {
        if (val && Object.keys(val).length > 0) {
          // [REPLACE] 使用 dataTransform 转换各 Section 数据
          // Object.assign(modelRef, detailToBasicInfo(val));
        }
      },
      { immediate: true, deep: true },
    );

    // [KEEP] 监听弹窗打开（弹窗模式）
    watch(
      () => props.open,
      val => {
        if (isModalMode.value && val) {
          loadDetail();
        }
      },
      { immediate: true },
    );

    // [KEEP] 嵌入模式：组件挂载时直接加载
    if (!isModalMode.value) {
      loadDetail();
    }

    // [KEEP] 弹窗标题
    const modalTitle = computed(() => formConfig.value.title || '表单');

    const handleClose = () => {
      emit('update:open', false);
    };

    // [KEEP] 统一校验所有子表单
    const validateAll = async () => {
      const validators = [
        basicInfoSectionRef.value?.validate?.(),
        // xxxSectionRef.value?.validate?.(),
      ].filter(Boolean);

      if (validators.length === 0) return Promise.resolve();

      try {
        await Promise.all(validators);
        return Promise.resolve();
      } catch (error) {
        return Promise.reject(error);
      }
    };

    const handleSubmit = async () => {
      await validateAll();
      await submit();
      emit('success');
      if (isModalMode.value) handleClose();
    };

    const handleSaveDraft = async () => {
      await saveDraft();
      emit('success');
      if (isModalMode.value) handleClose();
    };

    const isView = computed(() => formConfig.value.isView);

    expose({
      submit: handleSubmit,
      saveDraft: handleSaveDraft,
      approveSaveDraft: async () => {
        await validateAll();
        await saveDraft();
        emit('success');
        if (isModalMode.value) handleClose();
      },
      validate: validateAll,
      getFormData: () => ({ ...modelRef }),
      resetForm: () => { formRef.value?.resetFields(); },
    } as XxxFormRef);

    const renderFormContent = () => (
      <Spin spinning={loading.value}>
        <Form ref={formRef} model={modelRef} rules={{}} labelCol={{ style: 'width:120px' }}>
          {/* [REPLACE] 每个 Section 用 Card 包裹 */}
          <Card size="small" title="基础信息" class="!mt-[10px]">
            <BasicInfoSection
              ref={basicInfoSectionRef}
              value={basicInfoState.value}
              onUpdate:value={(val: BasicInfoForm) => {
                basicInfoState.value = val;
              }}
              disabled={isView.value}
            />
          </Card>

          {/* [REPLACE] 其他 Section 按此模式添加 */}
        </Form>
      </Spin>
    );

    return () => (
      <>
        {isModalMode.value ? (
          <BasicModal
            register={registerModal}
            open={props.open}
            title={modalTitle.value}
            canFullscreen={true}
            defaultFullscreen={true}
            width="100vw"
            destroyOnClose
            onCancel={handleClose}
            footer={
              <div class={styles.footer}>
                <Button onClick={handleClose}>{isView.value ? '关闭' : '取消'}</Button>
                {!isView.value && (
                  <Button onClick={handleSaveDraft} loading={saving.value}>
                    暂存
                  </Button>
                )}
                {!isView.value && (
                  <Button type="primary" loading={saving.value} onClick={handleSubmit}>
                    提交
                  </Button>
                )}
              </div>
            }
          >
            {renderFormContent()}
          </BasicModal>
        ) : (
          <div>{renderFormContent()}</div>
        )}
      </>
    );
  },
});
```

---

## Block 6: components/XxxSection/index.tsx（Section 子组件）

### 变体 A：标准表单 Section

```tsx
import { defineComponent, PropType, onMounted, watch, computed } from 'vue';
import { Form, Input, Select, Row, Col, InputNumber } from 'ant-design-vue';
import type { FormInstance, Rule } from 'ant-design-vue/es/form';
import type { BasicInfoForm } from '../../api/types';

export interface Props {
  value: BasicInfoForm;
  disabled?: boolean;
}

export default defineComponent({
  name: 'BasicInfoSection',
  props: {
    value: {
      type: Object as PropType<BasicInfoForm>,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:value'],
  setup(props, { emit, expose }) {
    const formRef = ref<FormInstance>();

    // [RULE 2] rules 动态化 — disabled 时不校验
    const requiredRule = (msg: string): Rule[] =>
      props.disabled ? [] : [{ required: true, message: msg, trigger: ['blur', 'change'] as any }];

    const rules = computed(() => ({
      projectId: requiredRule('请选择项目'),
      projectType: requiredRule('请选择项目业态'),
      // [REPLACE] 根据 PRD 添加更多校验规则
    }));

    // [RULE 1] 受控组件 — 直接读 props，不维护本地副本
    const updateValue = (key: keyof BasicInfoForm, value: any) => {
      emit('update:value', { ...props.value, [key]: value });
    };

    const updateValues = (values: Partial<BasicInfoForm>) => {
      emit('update:value', { ...props.value, ...values });
    };

    // [RULE 3] watch 必须在 onMounted 内
    onMounted(() => {
      watch(
        () => props.value,
        val => {
          // 如果有需要同步的本地状态（如特殊指令的中间变量），在这里处理
        },
        { immediate: true, deep: true },
      );
    });

    // [RULE 3] formRef 校验 + expose 类型声明
    const validate = async () => {
      if (!formRef.value) return Promise.reject('表单未初始化');
      return formRef.value.validate();
    };

    const getFormData = () => ({ ...props.value });
    const resetForm = () => { formRef.value?.resetFields(); };

    // [REPLACE] 根据 Section 实际暴露的方法调整类型名和方法
    expose({
      validate,
      getFormData,
      resetForm,
    } as XxxSectionRef);

    return () => {
      const value = props.value || {};
      const isDisabled = props.disabled;

      return (
        <article>
          {/* [RULE 1] Form + Row + Col + Form.Item 框架结构 */}
          <Form
            ref={formRef}
            model={value}
            rules={rules.value}
            labelCol={{ style: 'width:160px' }}
            colon={false}
            labelWrap
          >
            <Row gutter={24}>
              {/* [REPLACE] 根据 PRD 替换每个 Form.Item */}
              <Col span={8}>
                <Form.Item label="项目名称" name="projectId" required={!isDisabled}>
                  <Input
                    value={value.projectName}
                    placeholder="请选择项目"
                    readonly
                    disabled={isDisabled}
                    style={{ width: '100%' }}
                    onClick={() => {
                      if (!isDisabled) {
                        // 打开选择弹窗等
                      }
                    }}
                  />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item label="SAP项目编码">
                  <Input value={value.projectCode} disabled />
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item label="项目业态" name="projectType">
                  <Select
                    value={value.projectType}
                    options={projectTypeOptions.value}
                    placeholder="请选择"
                    disabled={isDisabled}
                    onChange={val => updateValue('projectType', val)}
                  />
                </Form.Item>
              </Col>

              {/* 更多字段按此模式添加... */}
            </Row>
          </Form>
        </article>
      );
    };
  },
});
```

### 变体 B：带远程数据加载的 Section（含 Hook）

**useXxx.ts**:

```typescript
import { ref, onMounted, watch } from 'vue';
import type { BasicInfoForm } from '../../api/types';

export interface UseBasicInfoProps {
  value: BasicInfoForm;
}

export function useBasicInfo(props: UseBasicInfoProps, emit: (event: 'update:value', value: BasicInfoForm) => void) {
  const companyOptions = ref<{ label: string; value: string }[]>([]);
  const regionOptions = ref<{ label: string; value: string }[]>([]);
  const loadingCompany = ref(false);
  const loadingRegion = ref(false);

  // 更新字段值
  const updateValue = (key: keyof BasicInfoForm, value: any) => {
    emit('update:value', { ...props.value, [key]: value });
  };

  const updateValues = (values: Partial<BasicInfoForm>) => {
    emit('update:value', { ...props.value, ...values });
  };

  // [REPLACE] 获取下拉选项
  const fetchCompanyList = async () => {
    loadingCompany.value = true;
    try {
      // const res = await getXxxList();
      // companyOptions.value = res.data.map(item => ({ label: item.name, value: item.code }));
    } finally {
      loadingCompany.value = false;
    }
  };

  const fetchRegionList = async (companyCode: string) => {
    if (!companyCode) { regionOptions.value = []; return; }
    loadingRegion.value = true;
    try {
      // const res = await getXxxList({ parentCode: companyCode });
      // regionOptions.value = res.data.map(item => ({ label: item.name, value: item.code }));
    } finally {
      loadingRegion.value = false;
    }
  };

  // [KEEP] watch 必须在 onMounted 内 — 此 hook 由调用方在 onMounted 中管理
  // 或者如果 hook 本身返回时就需要 watch，调用方需确保在 onMounted 中使用

  // 初始加载
  fetchCompanyList();

  return {
    companyOptions,
    regionOptions,
    loadingCompany,
    loadingRegion,
    updateValue,
    updateValues,
    fetchRegionList,
  };
}
```

**index.tsx（使用 Hook 的 Section）**:

```tsx
import { defineComponent, PropType, onMounted, watch, computed } from 'vue';
import { Form, Input, Select, Row, Col } from 'ant-design-vue';
import type { FormInstance, Rule } from 'ant-design-vue/es/form';
import type { BasicInfoForm } from '../../api/types';
import { useBasicInfo } from './useBasicInfo';

export interface Props {
  value: BasicInfoForm;
  disabled?: boolean;
  // [OPTIONAL] 额外的控制 props
  isFirstStart?: boolean;
}

export default defineComponent({
  name: 'BasicInfoSection',
  props: {
    value: {
      type: Object as PropType<BasicInfoForm>,
      required: true,
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    isFirstStart: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['update:value'],
  setup(props, { emit, expose }) {
    const formRef = ref<FormInstance>();
    const { companyOptions, regionOptions, loadingCompany, loadingRegion, updateValue, updateValues, fetchRegionList } = useBasicInfo(props, emit);

    const requiredRule = (msg: string): Rule[] =>
      props.disabled ? [] : [{ required: true, message: msg, trigger: ['blur', 'change'] as any }];

    const rules = computed(() => ({
      projectId: requiredRule('请选择项目'),
      subCode: requiredRule('请选择分公司'),
      regionId: requiredRule('请选择区域'),
    }));

    // 处理分公司变更
    const handleCompanyChange = (companyCode: string) => {
      const company = companyOptions.value.find(item => item.value === companyCode);
      updateValues({
        subName: company?.label || '',
        subCode: companyCode,
        regionId: '',
        regionName: '',
      });
    };

    // 处理区域变更
    const handleRegionChange = (regionId: string) => {
      const region = regionOptions.value.find(item => item.value === regionId);
      updateValues({ regionId, regionName: region?.label || '' });
    };

    // [RULE 3] watch 必须在 onMounted 内
    onMounted(() => {
      watch(
        () => props.value?.subCode,
        newCode => {
          if (newCode && regionOptions.value.length === 0) {
            fetchRegionList(newCode);
          }
        },
        { immediate: true },
      );
    });

    const validate = async () => {
      if (!formRef.value) return Promise.reject('表单未初始化');
      return formRef.value.validate();
    };

    const getFormData = () => ({ ...props.value });
    const resetForm = () => { formRef.value?.resetFields(); };

    expose({
      validate,
      getFormData,
      resetForm,
    } as XxxSectionRef);

    return () => {
      const value = props.value || {};
      const isDisabled = props.disabled;

      return (
        <article>
          <Form ref={formRef} model={value} rules={rules.value} labelCol={{ style: 'width:160px' }} colon={false} labelWrap>
            <Row gutter={24}>
              <Col span={8}>
                <Form.Item label="分公司" name="subCode">
                  <Select
                    value={value.subCode}
                    placeholder="请选择分公司"
                    loading={loadingCompany.value}
                    disabled={isDisabled}
                    onChange={handleCompanyChange}
                  >
                    {companyOptions.value.map(item => (
                      <Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
              <Col span={8}>
                <Form.Item label="区域" name="regionId">
                  <Select
                    value={value.regionId}
                    placeholder="请选择区域"
                    loading={loadingRegion.value}
                    disabled={isDisabled}
                    onChange={handleRegionChange}
                  >
                    {regionOptions.value.map(item => (
                      <Select.Option key={item.value} value={item.value}>{item.label}</Select.Option>
                    ))}
                  </Select>
                </Form.Item>
              </Col>
            </Row>
          </Form>
        </article>
      );
    };
  },
});
```

---

## 目录结构参考

```
src/views/模块名/功能名/
├── index.tsx                      # 表单容器（Block 5）
├── useForm.ts                     # 表单核心逻辑 Hook（Block 4）
├── style.module.less              # 样式
├── api/
│   ├── types.ts                   # 类型定义（Block 1）
│   ├── index.ts                   # API 封装（Block 2）
│   └── config.ts                  # [OPTIONAL] 业务配置枚举
├── utils/
│   └── dataTransform.ts           # 数据转换（Block 3）
└── components/
    ├── BasicInfoSection/           # Section 1
    │   ├── index.tsx               # 变体 A 或 B
    │   └── useBasicInfo.ts         # [OPTIONAL] Hook
    ├── XxxSection/                 # Section 2
    │   └── index.tsx
    └── ...                         # 更多 Section
```

## 标记说明

| 标记 | 含义 |
|------|------|
| `[REPLACE]` | 必须根据 PRD/API 文档替换的内容 |
| `[KEEP]` | 保持模板代码不变 |
| `[OPTIONAL]` | 可选功能，根据 PRD 决定是否保留 |
| `[RULE N]` | 对应五条铁规则的标注 |
| `[NOTE]` | 需要特别注意的细节 |
