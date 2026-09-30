# 详情页代码模板

> 基准代码来源：`src/views/eng-manage/start-apply/components/` 实际上线版本
> 所有 `[REPLACE]` 标记的区域需要根据 PRD/API 文档替换
> 所有 `[KEEP]` 标记的区域保持模板代码不变

---

## Block 1: utils/dataTransform.ts

```typescript
// [REPLACE] 整个文件的类型定义和转换函数根据 API 文档替换
// 以下为基准模板，保留结构，替换业务字段

import type { XxxDetail, BasicInfoForm, OtherInfoForm } from '../api/types';

/**
 * 将详情数据转换为基础信息表单格式
 * 字段严格遵循接口 Request 定义
 *
 * 设计思路：后端返回的是扁平的详情数据（XxxDetail），
 * 每个 Section 组件需要的字段子集不同，
 * 转换函数负责按模块拆分，并做空值兜底。
 */
export function detailToBasicInfo(detail: Partial<XxxDetail>): BasicInfoForm {
  return {
    // [REPLACE] 根据模块字段逐一映射
    id: detail.id || '',
    projectName: detail.projectName || '',
    projectCode: detail.projectCode || '',
    projectType: detail.projectType,
    // 字符串字段：做空字符串兜底
    provinceName: detail.provinceName || '',
    cityName: detail.cityName || '',
    // 编码字段：保留 undefined 即可（下拉组件支持 undefined）
    provinceCode: detail.provinceCode,
    cityCode: detail.cityCode,
    // 数字字段：保留 undefined（InputNumber 组件支持 undefined）
    capacityTotal: detail.capacityTotal,
    // ...根据 PRD 补充更多字段映射
  };
}

/**
 * 将详情数据转换为其他信息表单格式
 * 附件列表需要特殊处理：过滤对应类型 + 空数组兜底
 */
export function detailToOtherInfo(detail: Partial<XxxDetail>): OtherInfoForm {
  return {
    // [REPLACE] 根据模块字段逐一映射
    summary: detail.summary || '',
    // 附件字段：空数组兜底
    attachmentList: (detail.attachmentList || [])
      .filter((a: any) => a.attachmentType === 'TYPE_CODE') // [REPLACE] 替换为实际附件类型编码
      .map((att: any) => ({
        ...att,
        attachmentType: att.attachmentType || 'TYPE_CODE', // [REPLACE]
      })),
  };
}

// [NOTE] 新增模块时，在此文件中添加对应的转换函数
// 函数命名规范：detailTo{ModuleName}，如 detailToCostInfo、detailToEconomicInfo
```

---

## Block 2: components/XxxSection/index.tsx

> 每个 Card 模块对应一个 Section 组件，以下为通用模板

**[NOTE] 数据绑定模式选择**：
- **详情页内部编排**：用 `value + update:value`（本模板默认）
- **审批页嵌入场景**：用 `modelValue + update:modelValue`
两种模式等价，选择其一并在项目内保持一致。

```tsx
// [REPLACE] 文件路径：components/XxxSection/index.tsx（XxxSection 替换为实际模块名）
import { defineComponent, type PropType, ref, computed } from 'vue';
import { Form, Input, Select, Row, Col } from 'ant-design-vue';
import type { FormInstance, Rule } from 'ant-design-vue';
// [REPLACE] 导入本模块的表单类型
import type { BasicInfoForm } from '../../api/types';

export interface Props {
  value: BasicInfoForm;       // [REPLACE] 替换为实际表单类型
  disabled?: boolean;         // 是否禁用（控制只读/编辑）
}

export default defineComponent({
  // [REPLACE] 组件名 — 替换为 PascalCase 模块名 + Section
  name: 'BasicInfoSection',

  props: {
    value: {
      type: Object as PropType<BasicInfoForm>, // [REPLACE]
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

    // ====== 表单校验 ======

    // disabled 时返回空数组，跳过必填校验
    // 这样详情页查看模式不会触发红色校验提示
    const requiredRule = (msg: string): Rule[] =>
      props.disabled ? [] : [{ required: true, message: msg, trigger: ['blur', 'change'] as any }];

    const rules = computed(() => ({
      // [REPLACE] 根据模块必填字段配置校验规则
      projectName: requiredRule('请选择项目'),
      projectType: requiredRule('请选择项目业态'),
    }));

    // ====== 字段更新 ======

    // 更新单个字段 — 通过 emit 通知父组件
    const updateValue = (key: keyof BasicInfoForm, value: any) => { // [REPLACE] BasicInfoForm
      emit('update:value', { ...props.value, [key]: value });
    };

    // 更新多个字段 — 用于联动场景（如选择项目后批量填充）
    const updateValues = (values: Partial<BasicInfoForm>) => { // [REPLACE] BasicInfoForm
      emit('update:value', { ...props.value, ...values });
    };

    // ====== 暴露方法 ======

    // 校验：供父组件在提交前调用
    const validate = async () => {
      if (!formRef.value) return Promise.resolve();
      return formRef.value.validate();
    };

    // 获取数据：供父组件收集各模块数据
    const getValues = () => props.value;

    expose({ validate, getValues });

    // ====== 渲染 ======

    return () => {
      const value = props.value || {};
      const isDisabled = props.disabled;

      return (
        <article>
          <Form
            ref={formRef}
            model={value}
            rules={rules.value}
            labelCol={{ style: 'width:160px' }}
            colon={false}
            labelWrap
          >
            <Row gutter={24}>
              {/* [REPLACE] 以下为字段模板，根据 PRD 替换 */}

              {/* 文本输入 */}
              <Col span={8}>
                <Form.Item label="项目名称" name="projectName" required={!isDisabled}>
                  <Input
                    value={value.projectName}
                    placeholder="请输入"
                    disabled={isDisabled}
                    onChange={e => updateValue('projectName', e.target.value)}
                  />
                </Form.Item>
              </Col>

              {/* 下拉选择 */}
              <Col span={8}>
                <Form.Item label="项目业态" name="projectType">
                  <Select
                    value={value.projectType}
                    placeholder="请选择"
                    disabled={isDisabled}
                    options={[
                      // [REPLACE] 替换为实际选项或使用 DictSelect
                      { label: '风电', value: '1' },
                      { label: '光伏', value: '2' },
                      { label: '储能', value: '3' },
                    ]}
                    onChange={val => updateValue('projectType', val)}
                  />
                </Form.Item>
              </Col>

              {/* 只读展示字段（如自动带出的编码） */}
              <Col span={8}>
                <Form.Item label="SAP项目编码">
                  <Input value={value.projectCode} disabled />
                </Form.Item>
              </Col>

              {/* 数字输入（带单位） */}
              <Col span={8}>
                <Form.Item label="项目总容量" name="capacityTotal">
                  <InputNumber
                    value={value.capacityTotal}
                    placeholder="请输入"
                    disabled={isDisabled}
                    precision={2}
                    addonAfter="MW"
                    style={{ width: '100%' }}
                    onChange={val => updateValue('capacityTotal', val)}
                  />
                </Form.Item>
              </Col>

              {/* 长文本 */}
              <Col span={24}>
                <Form.Item label="申请概述" name="summary">
                  <Input.TextArea
                    value={value.summary}
                    rows={4}
                    maxlength={500}
                    showCount
                    disabled={isDisabled}
                    placeholder="请输入"
                    onChange={e => updateValue('summary', e.target.value)}
                  />
                </Form.Item>
              </Col>

              {/* [NOTE] 更多字段按上述模式添加 */}
            </Row>
          </Form>
        </article>
      );
    };
  },
});
```

### Section 组件变体说明

#### 变体 A：纯展示型 Section（如单据信息）

不需要 Form，直接用 `Descriptions` 组件：

```tsx
// 纯展示型模块 — 无校验、无编辑，直接用 Descriptions
<section id="bill" class={styles.section}>
  <Card size="small" title="单据信息" class="!mt-10px">
    <Descriptions bordered size="small" column={4} labelStyle={{ width: '130px', textAlign: 'right' }}>
      <Descriptions.Item label="申请单号">{detail.value?.applyNo || '-'}</Descriptions.Item>
      <Descriptions.Item label="申请人">{detail.value?.applicantName || '-'}</Descriptions.Item>
      <Descriptions.Item label="申请时间">{detail.value?.applyTime || '-'}</Descriptions.Item>
      <Descriptions.Item label="审批状态">
        <Tag color={getStatusColor(detail.value?.approvalStatus ?? 0)}>
          {getStatusText(detail.value?.approvalStatus ?? 0)}
        </Tag>
      </Descriptions.Item>
    </Descriptions>
  </Card>
</section>
```

**适用场景**：单据信息、审批记录等纯展示模块，不含表单交互。

#### 变体 B：带附件的 Section

```tsx
// 在 Section 组件中处理附件上传
import AttachmentFileList, { type AttachmentFile } from '@/components/AttachmentFileList';

// 附件列表转换
const attachmentFileList = computed<AttachmentFile[]>(() => {
  return (props.value.attachmentList || []).map(att => ({
    id: att.id,
    fileName: att.filename,
    filename: att.filename,
    filePath: att.filePath,
    uploader: att.uploadName,
    uploadName: att.uploadName,
    uploadTime: att.uploadTime,
    attachmentType: att.attachmentType,
  }));
});

// 渲染
<Form.Item label="附件" name="attachmentList" required={!isDisabled}>
  <AttachmentFileList
    dataSource={attachmentFileList.value}
    showTitle={false}
    showDownloadAll={true}
    showAttachmentType={true}
    readonly={isDisabled}
    showDelete={!isDisabled}
    emptyText="暂无附件"
    onUploadSuccess={handleUploadSuccess}
    onDelete={handleRemoveAttachment}
  />
</Form.Item>
```

#### 变体 C：审批节点权限控制的 Section（用于详情页嵌入审批页）

**适用场景**：详情页被审批页嵌入时，需要根据审批节点（operationType）控制哪些字段可编辑。

```tsx
// 变体 C：审批节点权限控制
import { defineComponent, PropType, inject, computed } from 'vue';
import { Form, Input, InputNumber } from 'ant-design-vue';
// [REPLACE] 导入审批页面的 ProvideContext
import { ProvideContext } from '@/views/office/todo/components/apply-modal/xxxApproval';
// [REPLACE] 导入审批节点枚举
import { approveEnum } from '../../api/config';
import type { templatePermission } from '../../api/types';

export interface Props {
  value: XxxForm;
  disabled?: boolean;
}

setup(props, { emit, expose }) {
  // 注入审批权限上下文
  const permission = inject<templatePermission>(ProvideContext.Permission);
  
  // 根据审批节点计算可编辑性
  const isCostEditable = computed(() => 
    permission?.operationType === approveEnum.approve_cbcs  // [REPLACE] 替换节点枚举
  );
  const isEconomicEditable = computed(() => 
    permission?.operationType === approveEnum.approve_ycbp
  );
  
  // disabled 优先级：props.disabled > 权限控制
  const effectiveDisabled = computed(() => 
    props.disabled || !isCostEditable.value
  );
  
  const requiredRule = (msg: string): Rule[] =>
    effectiveDisabled.value ? [] : [{ required: true, message: msg }];
    
  return () => (
    <Form>
      {/* 仅在成本测算节点可编辑 */}
      <Form.Item label="单瓦成本" name="unitCost" required={!effectiveDisabled.value}>
        <InputNumber 
          value={value.unitCost} 
          disabled={effectiveDisabled.value}
          onChange={v => emit('update:value', { ...props.value, unitCost: v })}
        />
      </Form.Item>
    </Form>
  );
}
```

**关键点**：
1. `inject<templatePermission>(ProvideContext.Permission)` 获取审批权限
2. `permission.operationType` 决定当前节点
3. 用 `computed` 计算 `effectiveDisabled`，合并 props.disabled 和权限控制
4. 适用场景：成本测算、经济信息、会议纪要等审批节点填写的模块

---

## Block 3: components/DetailModal/useDetail.ts

```typescript
// [KEEP] 数据加载 hook — 通用模板，大部分场景不需要修改
import { ref, onMounted, watch, isRef, type Ref } from 'vue';
// [REPLACE] 替换为实际的 API 函数和类型
import { getXxxDetail } from '../../api';
import type { XxxDetail } from '../../api/types';

interface UseDetailOptions {
  enabled?: boolean; // 是否启用 API 调用（embedded 模式传 false）
}

/**
 * 详情数据加载 hook
 *
 * 设计思路：
 * - modal 模式：组件内部通过此 hook 加载数据（enabled=true）
 * - embedded 模式：外部传入数据，此 hook 不调用 API（enabled=false）
 * - 自动监听 id 变化，重新加载
 */
export function useDetail(id: string | Ref<string>, options: UseDetailOptions = {}) {
  const { enabled = true } = options;

  const detail = ref<Partial<XxxDetail>>({}); // [REPLACE] XxxDetail
  const loading = ref(false);

  const getId = () => (isRef(id) ? id.value : id);

  const loadDetail = async () => {
    const currentId = getId();
    if (!currentId || !enabled) return;
    loading.value = true;
    try {
      // [REPLACE] 替换为实际的详情 API 调用
      const res = await getXxxDetail({ id: currentId });
      if (res.code === 0 && res.data) {
        detail.value = res.data;
      }
    } finally {
      loading.value = false;
    }
  };

  onMounted(() => {
    loadDetail();
  });

  // 监听 id 变化，自动重新加载
  watch(isRef(id) ? id : () => id, () => {
    if (enabled) {
      loadDetail();
    }
  });

  return {
    detail,
    loading,
    loadDetail,
  };
}
```

---

## Block 4: components/DetailModal/index.tsx

```tsx
// [REPLACE] 文件路径：components/XxxDetailModal/index.tsx
import { defineComponent, computed, toRef, ref, watch, type PropType } from 'vue';
import { Spin, Card, Descriptions, Tag } from 'ant-design-vue';
import { BasicModal } from '@/components/Modal';
// [KEEP] 审批记录组件 — 固定导入，禁止删除
import ApprovalProcess from '@/components/ApprovalProcess';
import { useDetail } from './useDetail';
// [REPLACE] 导入各 Section 组件
import BasicInfoSection from '../BasicInfoSection';
import OtherInfoSection from '../OtherInfoSection';
// [REPLACE] 导入数据转换函数
import { detailToBasicInfo, detailToOtherInfo } from '../../utils/dataTransform';
// [REPLACE] 导入类型
import type { XxxDetail } from '../../api/types';
import styles from './style.module.less';

export type DisplayMode = 'modal' | 'embedded';

export default defineComponent({
  // [REPLACE] 组件名 — 替换为 PascalCase 模块名 + DetailModal
  name: 'XxxDetailModal',

  props: {
    open: {
      type: Boolean,
      default: false,
    },
    id: {
      type: String,
      default: '',
    },
    displayMode: {
      type: String as PropType<DisplayMode>,
      default: 'modal',
    },
    className: {
      type: String,
      default: '',
    },
    // 嵌入模式下支持外部传入数据
    externalData: {
      type: Object as () => Partial<XxxDetail>,
      default: () => ({}),
    },
    // [REPLACE] 表单操作类型
    type: {
      type: String as PropType<'view' | 'edit'>,
      default: 'view',
    },
  },

  setup(props, { emit, expose }) {
    // ====== 双模式判断 ======
    const isModalMode = computed(() => props.displayMode === 'modal');
    const isDisabled = computed(() => props.type === 'view');

    // ====== 数据加载 ======
    const idRef = toRef(props, 'id');
    const { detail: apiDetail, loading: apiLoading } = useDetail(idRef, {
      enabled: isModalMode.value,
    });

    // 合并数据：弹窗模式用 API 数据，嵌入模式用外部数据
    const detail = computed(() => {
      if (isModalMode.value) {
        return apiDetail.value;
      }
      return props.externalData;
    });

    const loading = computed(() => {
      if (isModalMode.value) {
        return apiLoading.value;
      }
      return false;
    });

    // ====== 各模块数据（从 detail 转换而来） ======

    // [REPLACE] 每个模块一个 ref，通过 watch 同步
    const basicInfoData = ref(detailToBasicInfo(detail.value));
    const otherInfoData = ref(detailToOtherInfo(detail.value));

    // 监听 detail 变化，同步到各模块
    watch(
      detail,
      val => {
        basicInfoData.value = detailToBasicInfo(val);
        otherInfoData.value = detailToOtherInfo(val);
      },
      { immediate: true },
    );

    // ====== Section ref（用于调用子组件 expose 的方法） ======
    const basicInfoRef = ref<{ validate: () => Promise<any>; getValues: () => any } | null>(null);
    const otherInfoRef = ref<{ validate: () => Promise<any>; getValues: () => any } | null>(null);

    // ====== 状态映射 ======
    // [REPLACE] 根据实际业务状态替换
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

    // ====== 关闭弹窗 ======
    const handleClose = () => {
      emit('update:open', false);
    };

    // ====== 暴露方法 ======
    // getData：供父组件收集各模块数据（如提交审批时）
    expose({
      getData() {
        return {
          ...detail.value,
          ...basicInfoRef.value?.getValues(),
          ...otherInfoRef.value?.getValues(),
        };
      },
    });

    // ====== 详情内容渲染 ======
    const renderDetailContent = () => (
      <Spin spinning={loading.value}>
        <div class={isModalMode.value ? styles.detailContainer : styles.detailContainerEmbedded}>

          {/* ====== 单据信息（纯展示，不需要 Section 组件） ====== */}
          <section id="bill" class={styles.section}>
            <Card size="small" title="单据信息" class="!mt-10px">
              <Descriptions bordered size="small" column={4} labelStyle={{ width: '130px', textAlign: 'right' }}>
                {/* [REPLACE] 替换为实际的单据字段 */}
                <Descriptions.Item label="申请单号">{detail.value?.applyNo || '-'}</Descriptions.Item>
                <Descriptions.Item label="申请人">{detail.value?.applicantName || '-'}</Descriptions.Item>
                <Descriptions.Item label="申请时间">{detail.value?.applyTime || '-'}</Descriptions.Item>
                <Descriptions.Item label="审批状态">
                  <Tag color={getStatusColor(detail.value?.approvalStatus ?? 0)}>
                    {getStatusText(detail.value?.approvalStatus ?? 0)}
                  </Tag>
                </Descriptions.Item>
              </Descriptions>
            </Card>
          </section>

          {/* ====== 基础信息（可编辑 Section） ====== */}
          <section id="basic" class={styles.section}>
            <Card size="small" title="基础信息" class="!mt-10px">
              <BasicInfoSection
                ref={basicInfoRef}
                value={basicInfoData.value}
                disabled={isDisabled.value}
                onUpdate:value={(v: any) => {
                  basicInfoData.value = v;
                }}
              />
            </Card>
          </section>

          {/* ====== 其他信息（可编辑 Section） ====== */}
          <section id="other" class={styles.section}>
            <Card size="small" title="其他信息" class="!mt-10px">
              <OtherInfoSection
                ref={otherInfoRef}
                value={otherInfoData.value}
                disabled={isDisabled.value}
                onUpdate:value={(v: any) => {
                  otherInfoData.value = v;
                }}
              />
            </Card>
          </section>

          {/* [NOTE] 按 PRD 添加更多 Section，每个遵循相同模式 */}

          {/* [KEEP] 审批记录模块（P0 强制）— 固定代码，禁止删除或替换 */}
          {/* 规则：只要不是首次新建（有 id），都应该展示审批记录 */}
          {!!detail.value?.id && (
            <section id="record" class={styles.section}>
              <Card size="small" title="审批记录" class="!mt-10px">
                <ApprovalProcess primaryKey={detail.value?.id} />
              </Card>
            </section>
          )}
        </div>
      </Spin>
    );

    // ====== 双模式渲染 ======
    return () => (
      <>
        {isModalMode.value ? (
          // [REPLACE] 替换弹窗标题
          <BasicModal
            title="详情"
            open={props.open}
            width="100vw"
            defaultFullscreen={true}
            footer={null}
            onCancel={handleClose}
            destroyOnClose
          >
            {renderDetailContent()}
          </BasicModal>
        ) : (
          <div class={[styles.embeddedContainer, props.className]}>
            {renderDetailContent()}
          </div>
        )}
      </>
    );
  },
});
```

### 条件显示模式

某些模块需要根据条件显示/隐藏：

```tsx
{/* 条件显示示例：仅审批完成时显示历史记录 */}
{detail.value?.approvalStatus === 2 && (
  <section id="history" class={styles.section}>
    <Card size="small" title="历史记录" class="!mt-10px">
      <HistorySection data={detail.value?.historyList || []} />
    </Card>
  </section>
)}

{/* 条件显示示例：仅重新开工时显示原因 */}
{detail.value?.applyType === 'RESTART' && (
  <section id="restart" class={styles.section}>
    <Card size="small" title="重新开工原因" class="!mt-10px">
      <RestartReasonSection value={detail.value?.restartReason || ''} disabled />
    </Card>
  </section>
)}
```

### 模块间联动模式

当模块 A 的数据变化需要影响模块 B 时，有两种方式：

```tsx
// 方式一：通过 watch 监听 props（推荐，适用于简单联动）
watch(
  () => basicInfoData.value.projectType,
  (newType) => {
    // 项目业态变化时，更新开工信息的容量字段配置
    otherInfoData.value = {
      ...otherInfoData.value,
      capacityUnit: newType === '1' ? 'MW' : newType === '2' ? 'MWp' : 'MW/MWh',
    };
  },
);

// 方式二：provide/inject（适用于深层嵌套）
// 父组件 provide
import { provide, inject } from 'vue';
const ProjectTypeKey = Symbol('projectType');
provide(ProjectTypeKey, computed(() => basicInfoData.value.projectType));

// 子组件 inject
const projectType = inject<ComputedRef<string>>(ProjectTypeKey);
```

---

## Block 5: components/DetailModal/style.module.less

```less
// 弹窗模式：内容区域
.detailContainer {
  display: block;
}

// 嵌入模式：内容区域（无最大高度限制）
.detailContainerEmbedded {
  display: block;
}

// 嵌入模式外层容器
.embeddedContainer {
  width: 100%;
}

// 模块间距
.section {
  margin-top: 10px;
}
```

---

## 目录结构参考

```
src/views/模块名/功能名/
├── components/
│   ├── XxxDetailModal/          # [REPLACE] 主编排组件
│   │   ├── index.tsx            # Block 4
│   │   ├── useDetail.ts         # Block 3
│   │   └── style.module.less    # Block 5
│   ├── BasicInfoSection/        # [REPLACE] 基础信息模块
│   │   └── index.tsx            # Block 2 变体
│   ├── OtherInfoSection/        # [REPLACE] 其他信息模块
│   │   └── index.tsx            # Block 2 变体
│   └── ...                      # [REPLACE] 更多 Section 按需添加
├── utils/
│   └── dataTransform.ts         # Block 1
└── api/
    ├── types.ts                 # 类型定义（已有，可能需要补充）
    └── index.ts                 # API 封装（已有，可能需要补充详情接口）
```

---

## 标记说明

| 标记 | 含义 |
|------|------|
| `[REPLACE]` | 必须根据 PRD/API 文档替换的内容 |
| `[KEEP]` | 保持模板代码不变 |
| `[NOTE]` | 需要特别注意的细节 |

---

## 常见模块类型速查

| 模块类型 | 实现方式 | Section 组件? | 说明 |
|---------|----------|:---:|------|
| 单据信息 | Descriptions（Block 4 内联） | 否 | 申请单号、申请人、状态等，纯展示 |
| 基础信息 | Form + Section 组件（Block 2） | 是 | 项目名称、业态、地址等，可编辑 |
| 业务信息 | Form + Section 组件（Block 2） | 是 | 容量、附件等，业态驱动显示 |
| 附件管理 | AttachmentFileList（变体 B） | 是 | 上传/预览/下载 |
| 审批记录 | `@/components/ApprovalProcess` | 否 | **P0 强制**，所有详情页必须包含，条件 `!!detail.value?.id`，直接写入 DetailModal |
| 历史记录 | Table 组件 | 可选 | 条件显示，可内联或独立 Section |
| 预审意见 | 自定义组件 | 是 | 复杂计算，通常需独立开发 |
