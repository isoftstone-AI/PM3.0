# PM 移动端迁移 - 代码模板与组件参考

> 本文件是 `pm-mobile-migration` skill 的参考库，按需加载。
> **所有签名均核对自项目真实代码**（2026-09-09），使用前若怀疑过期，先 grep 确认。

## 目录

1. [审批外壳标准模板](#1-审批外壳标准模板)
2. [节点配置 config.ts 模板](#2-节点配置-configts-模板)
3. [字段渲染模板](#3-字段渲染模板)
4. [附件上传与文件列表](#4-附件上传与文件列表)
5. [审批通用组件速查表（真实签名）](#5-审批通用组件速查表真实签名)
6. [通用区块与 hook 模板](#6-通用区块与-hook-模板)
7. [常见错误](#7-常见错误)
8. [保留模板：富文本 / 明细列表 / Loading / 空状态 / 性能](#8-保留模板)

---

## 1. 审批外壳标准模板

> **两级方案**：首选公共容器 `ApprovalContainer`（§1.1，一个组件替代整个手写外壳）；组件不在当前分支或需特殊定制时，回退手写外壳模板（§1.3）。
> 使用容器前先确认存在：`ls src/views/office/todo/components/ApprovalContainer/`
> ⚠️ 该组件自分支 `feat/mobile-approval-container` 起维护，在未合入的工作分支上使用前，确认该分支已合入当前工作基线。
> **节点配置一律放 `config.ts`（见 §2），两种方案都只消费配置。**

### 1.1 ApprovalContainer 接入（首选）

组件：`src/views/office/todo/components/ApprovalContainer/index.vue`（内部渲染 `ApprovalActionBar`）。

容器已内置，**禁止在业务页面重复实现**：getOperationRole 权限加载、PC-only 双维度拦截（operationType + templateKey）、懒加载（非 PC-only 才渲染 slot）、按钮矩阵（提交/同意/驳回/确认/抄送/已阅）、审批结论 Select（`approve_spjl`）、审批意见 + 附件上传、已阅签收区、抄送弹窗 + 选人、审批记录入口、completeTodoApi 提交、校验失败 toast。

```vue
<script setup lang="ts">
import { ref } from "vue";
import ApprovalContainer from "@/views/office/todo/components/ApprovalContainer/index.vue";
import { PC_ONLY_OPERATIONS } from "./config";
import XxxForm from "./form.vue";

const props = defineProps<{
  modalType: "approve" | "approveRecord";
  record: any;
}>();

const primaryKey = ref("");
const isEndEvent = ref(false);
const detail = ref(null);

// @permission：权限加载成功且非 PC-only 时触发一次，在此加载业务详情
async function onPermission(p: {
  templatePermission: string;
  operationType: string;
  otherOperationType: string;
}) {
  isEndEvent.value = p.otherOperationType === "endEvent";
  primaryKey.value = parsePrimaryKey(); // 从 record.businessKey / record.variable.json 解析，按业务实际
  const res = await getXxxDetail(primaryKey.value);
  detail.value = res?.data ?? null;
}
</script>

<template>
  <ApprovalContainer
    :modalType="props.modalType"
    :todoInfo="props.record"
    :fileCategory="'xxx_file'"
    :pcOnlyOperations="PC_ONLY_OPERATIONS"
    :isEndEvent="isEndEvent"
    @permission="onPermission"
  >
    <template #default="{ operationType }">
      <XxxForm v-if="primaryKey" :detail="detail" :operationType="operationType" />
    </template>
  </ApprovalContainer>
</template>
```

页面职责仅剩三件事：解析主键、`@permission` 回调加载详情、渲染只读业务表单。

Props 速查（透传 ActionBar 的详见 §5）：

| Prop | 必填 | 说明 |
|---|---|---|
| `modalType` | ✓ | `"approve"` 审批 / `"approveRecord"` 已办只读（自动隐藏审批表单与按钮） |
| `todoInfo` | ✓ | 待办任务对象（含 `id`、`procInstId`、`variable`） |
| `fileCategory` | ✓ | 附件分类，如 `"xxx_file"` |
| `pcOnlyOperations` | | operationType 维度 PC-only 节点，来自 config.ts |
| `pcOnlyTemplateKeys` | | 默认 `["submit_save","submit_save_close","apply_system"]`，一般不用传 |
| `viewPermissionKeys` | | 默认 `["card_approve_make_copy"]`，一般不用传 |
| `isEndEvent` | | true 时同意按钮文案为"批准"（用 permission 回调的 `otherOperationType === 'endEvent'`） |
| `getOtherParam` | | 提交时附加 otherParam |

Emits：`permission({ templatePermission, operationType, otherOperationType })`、`success`。
Slot：`default`，作用域 `{ operationType }`。

### 1.2 等价性验收清单（容器接入后必查）

对照组件 README 的等价性清单（基准：initiationApproval/list.vue）：

- [ ] PC-only 命中（operationType 或 templateKey）→ 只弹"请到电脑端完成操作！"，确认后返回，不渲染业务表单
- [ ] 按钮模式：`approve_reject`→同意+驳回；`approve`→同意；`confirm`→确认；`card_approve_make_copy`→已阅
- [ ] `approve_spjl` 节点显示审批结论 Select（通过/不通过，必填）
- [ ] 附件上传带 fileCategory，可删除
- [ ] 抄送弹窗 + 选人、审批记录入口正常
- [ ] `modalType === 'approveRecord'` → 只读，无审批表单与底部按钮

### 1.3 手写外壳模板（后备：容器不在当前分支时）

审批页 `list.vue` 的手写标准结构。提炼自立项/预立项/机会三个已交付审批模块的共性。**容器可用时禁止使用本节（会重复 400+ 行已组件化的代码）。**

```vue
<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { cloneDeep } from "lodash-es";
import { $t } from "@/locales";
import { getOperationRole } from "@/api/system/flow";
import { useTodoActions } from "../red-line/hooks/index"; // 待办操作一站式 hook
import { successToast, failToast } from "@/utils/toast";
import BaseForm from "./form.vue";
import {
  PC_ONLY_OPERATIONS,
  SUBMIT_PERMISSIONS,
  VIEW_PERMISSIONS,
} from "./config";
import userSelectPopup from "@/views/office/todo/components/user-select-popup/index.vue";
import ApproveRecordPopup from "@/views/office/todo/components/approveRecord/index.vue";

const props = defineProps<{
  modalType: "approve" | "approveRecord";
  record: any;
}>();

const router = useRouter();
const loading = ref(false);
const loaded = ref(false);            // PC 专属操作时不加载表单
const pcOnlyDialogShow = ref(false);  // PC 专属操作拦截弹窗
const templatePermission = ref("");   // getOperationRole 返回的权限键
const operationType = ref("");        // 当前审批节点类型
const todoInfo = ref<any>({});
const formRef = ref(null);

const modelForm = ref(cloneDeep({ passType: "", approvalOpinion: "", attachmentList: [] }));

// ── 权限初始化：决定「拦截 or 加载表单」──────────────
onMounted(async () => {
  todoInfo.value = props.record;
  try {
    const res: any = await getOperationRole({ taskId: todoInfo.value?.id });
    if (res?.code === 0) {
      templatePermission.value = res.data?.templateKey ?? "";
      operationType.value = res.data?.operationType || "";
      const isPcOnly = PC_ONLY_OPERATIONS.includes(operationType.value as any);
      const isSubmit = SUBMIT_PERMISSIONS.includes(templatePermission.value);
      pcOnlyDialogShow.value = isPcOnly || isSubmit;
      loaded.value = !pcOnlyDialogShow.value; // 提交类与 PC 专属节点不加载详情
    }
  } catch (e) {
    console.error(e);
  }
});

// ── 提交类节点（submit_save 等）：拼装完整单据提交 ──
// 参数结构参考已交付模块；variable.json 需回写业务字段时在此扩展
async function handleSubmit() { /* 按业务实现，参考 §1.2 */ }

// ── 抄送 / 已阅 / 同意 / 驳回：复用 useTodoActions ──
const {
  forwardShow, forwardFormRef, forwardForm,
  handleForward, handleForwardConfirm,
  userPopupShow, selectedUsers, handleUserSelect, userSelectConfirm,
  viewShow, viewFormRef, viewForm, handleViewConfirm,
} = useTodoActions({ todoInfo, operationType });
</script>
```

#### 1.3.1 模板骨架

```vue
<template>
  <div class="BaseClass">
    <!-- PC 端专属操作拦截弹窗 -->
    <van-dialog
      v-model:show="pcOnlyDialogShow"
      :title="$t('common.tips', '提示')"
      :show-cancel-button="false"
      @confirm="router.back()"
    >
      <div class="p-[20px] text-center" style="color: #606266">
        {{ $t("constructionDesign.pcOnlyTip", "请到电脑端完成操作！") }}
      </div>
    </van-dialog>

    <!-- 抄送弹窗 + 选人组件 -->
    <van-dialog v-model:show="forwardShow" :title="$t('Office.Todo.forwardTitle', '流程抄送')"
      show-cancel-button @confirm="handleForwardConfirm" @cancel="forwardShow = false"
      :before-close="() => false">
      <van-form ref="forwardFormRef"><!-- 转发签收人 + 签收意见，见已有模块 --></van-form>
    </van-dialog>
    <userSelectPopup type="forward" :multiple="true" :selectedUsers="selectedUsers"
      :show="userPopupShow" @submit="userSelectConfirm" @close="userPopupShow = false" />

    <!-- 详情表单：仅在 loaded 时渲染 -->
    <BaseForm v-if="loaded" :procInst="todoInfo" :isDetail="true"
      :done="props.modalType === 'approveRecord'"
      :formDetail="{ id: detailId }" :operationType="operationType" />

    <!-- 审批意见区（非只读权限时显示）：审批结论 + 意见 + 附件 -->
    <!-- 已阅区（card_approve_make_copy 时显示）：签收意见 + 附件 -->
  </div>

  <!-- 底部按钮区：按 templatePermission 条件渲染 -->
  <div class="btns" v-if="props.modalType === 'approve'">
    <van-button v-if="SUBMIT_PERMISSIONS.includes(templatePermission)" type="primary"
      @click="handleSubmit">{{ $t("common.submit", "提交") }}</van-button>
    <van-button v-if="['approve_reject'].includes(templatePermission)" type="primary"
      @click="handleAgree">{{ $t("common.agree", "同意") }}</van-button>
    <van-button v-if="['approve_reject'].includes(templatePermission)" type="danger"
      @click="handleReject">{{ $t("common.reject", "驳回") }}</van-button>
    <van-button v-if="['approve'].includes(templatePermission)" type="primary"
      @click="handleAgree">{{ $t("common.agree", "同意") }}</van-button>
    <van-button type="default" @click="handleForward">{{ $t("Office.Todo.cc", "抄送") }}</van-button>
    <van-button v-if="VIEW_PERMISSIONS.includes(templatePermission)" type="primary"
      @click="handleViewConfirm">{{ $t("Office.Todo.read", "已阅") }}</van-button>
  </div>
</template>

<style scoped lang="less">
.BaseClass { min-height: 100vh; background: #f5f5f5; }
.btns {
  position: fixed; bottom: 0; left: 0; right: 0;
  display: flex; flex-wrap: wrap; gap: 8px; padding: 12px;
  background: #fff; box-shadow: 0 -2px 8px rgba(0, 0, 0, 0.05);
}
</style>
```

#### 1.3.2 审批结论（approve_spjl 类节点）

结论为必选时用项目 `Select` 组件 + 校验规则；提交参数中 `passType` 写入 `variable.json`：

```vue
<Select v-if="operationType === 'approve_spjl'" name="passType"
  :label="$t('Office.Todo.conclusion', '审批结论')" v-model="modelForm.passType" required
  :rules="[{ required: true, message: $t('common.selectApprovalConclusion', '请选择审批结论'), trigger: ['onSubmit'] }]"
  :options="[
    { label: $t('common.approvalStatus.pass', '通过'), value: '1' },
    { label: $t('common.approvalStatus.reject', '不通过'), value: '2' }
  ]" />
```

### 1.4 completeTodoApi 参数结构（手写提交时参考；容器已内置相同逻辑）

```typescript
const params = {
  id: todoInfo.value?.id,
  procInst: todoInfo.value?.procInstId,
  otherParam: JSON.stringify({ operationType: operationType.value }), // 按需
  variable: {
    ...todoInfo.value?.variable,
    json: JSON.stringify({
      ...JSON.parse(todoInfo.value?.variable?.json || "{}"),
      passType: modelForm.value.passType, // 审批结论按需回写
    }),
  },
  comment: JSON.stringify({ _pass: "approve" /* or "reject" */, comment: modelForm.value.approvalOpinion }),
  actHiAttachments: modelForm.value.attachmentList?.map(item => ({
    name: item.fileName, url: item.filePath || "",
  })) ?? [],
};
await completeTodoApi(params);
successToast();
router.replace({ path: "/success" });
```

表单校验失败处理惯例：

```typescript
catch (error) {
  const errorField = (error as any)?.errorFields?.[0] ?? "";
  if (errorField) {
    const msg = errorField.errors?.[0];
    msg && failToast(msg);
  }
  loading.value = false;
}
```

---

## 2. 节点配置 config.ts 模板

**禁止把节点清单/权限/映射内联在 list.vue**（立项模块 731 行的教训）。独立文件，list.vue 只 import：

```typescript
/**
 * xxx 审批节点配置
 * 来源：PC 端 apply-modal/xxx.tsx + getOperationRole 实测
 * 维护：新增节点时同步更新本文件与 SKILL Phase1 四张表
 */

/** 移动端不支持、需拦截到 PC 端的节点 */
export const PC_ONLY_OPERATIONS = [
  "submit_save",
  "submit_save_close",
  "apply_system",
  // ... 按表④填写
] as const;

/** 提交类权限键（命中时不加载详情表单，走单据提交） */
export const SUBMIT_PERMISSIONS = ["submit_save", "submit_save_close", "apply_system"];

/** 已阅权限键 */
export const VIEW_PERMISSIONS = ["card_approve_make_copy"];

/** 评审模式映射：节点 → 移动端展示模式 */
export const REVIEW_MODE_MAP: Record<string, "review" | "reply" | "readonly" | "none"> = {
  // 按表③填写
};

/** 节点角色中文名 */
export const OPERATION_TYPE_ROLE_MAP: Record<string, string> = {
  // 按表①填写
};
```

---

## 3. 字段渲染模板

项目惯例：**只读字段用 `van-field readonly input-align="right"`**（不是 van-cell），空值统一显示 `-`。

### 3.1 普通文本字段

```vue
<van-field
  :model-value="detail.projectName || '-'"
  :label="$t('xxx.projectName', '项目名称')"
  readonly
  input-align="right"
/>
```

### 3.2 字典字段（真实 useDict 签名）

```vue
<script setup lang="ts">
import { computed } from "vue";
import { useDict } from "@/hooks/useDict";

const props = defineProps<{ detail: Partial<XxxDetail> }>();

// 真实签名：传 { default: 字典code }，返回 { dictData, dictMap, run }
// dictMap 是 { [dataValue]: dataLabel } 映射
const { dictMap: bizTypeMap } = useDict({ default: "OVERSEA_PROJ_BIZ_TYPE" });

const bizTypeDisplay = computed(() => {
  // 惯例：接口若直接给 name 字段则优先用（省一次翻译）
  const name = props.detail.projectTypesName;
  if (name) return name;
  const value = props.detail.projectTypes;
  if (!value) return "-";
  return bizTypeMap.value[Number(value)] || value; // 找不到回退原始值
});
</script>
<template>
  <van-field :model-value="bizTypeDisplay" label="项目业态" readonly input-align="right" />
</template>
```

多值字典（逗号/JSON 数组存储）翻译惯例见已交付模块 `initiationApproval/components/BasicInfoSection` 的 `priceTypeDisplay`。

### 3.3 日期字段

```vue
<script setup lang="ts">
import dayjs from "dayjs";
const dateDisplay = computed(() => {
  const v = props.detail.applyDate;
  return v ? dayjs(v).format("YYYY-MM-DD") : "-";
});
</script>
```

### 3.4 金额/数字字段

```vue
<script setup lang="ts">
const amountDisplay = computed(() => {
  const v = props.detail.estimatedInvestment;
  if (v === undefined || v === null) return "-";
  const unit = props.detail.costUnit || "万元";
  return `${Number(v).toLocaleString("zh-CN")} ${unit}`;
});
</script>
```

### 3.5 条件渲染字段

```vue
<!-- 业态细分：仅风电(1)/光伏(2)显示 -->
<van-field v-if="['1', '2'].includes(String(detail.projectTypes))"
  :model-value="subTypeDisplay" label="业态细分" readonly input-align="right" />
```

---

## 4. 附件上传与文件列表

项目方案是 **`Upload`（上传触发）+ `FileCard`（文件条目展示）组合**。
⚠️ 不存在 `MobileFileUpload` 组件，规范旧版的该组件模板已废弃。

### 4.1 上传 + 列表（审批附件场景）

```vue
<van-field :label="$t('common.attachment', '附件')" input-align="right">
  <template #button>
    <Upload @onSuccess="file => onAttachmentAfterRead('attachmentList', file)">
      <van-button size="mini" plain type="primary">
        {{ $t("common.upload", "上传") }}
      </van-button>
    </Upload>
  </template>
</van-field>

<div class="flex flex-col items-start gap-[12px] bg-white px-[12px] py-[10px]">
  <FileCard v-for="(file, index) in modelForm.attachmentList || []" :key="index"
    :file="file" :showDelete="true"
    @delete="() => removeAttachment('attachmentList', index)" />
</div>
```

```typescript
// 上传成功回调：按业务附件结构入列（结构以各业务后端为准，参考立项模块）
const onAttachmentAfterRead = (secKey: string, file: any) => {
  const list = modelForm.value?.[secKey] || [];
  list.push({
    fileCategory: "xxx_file",
    fileName: file.file?.name || "",
    filePath: file.path || "",
    fileSize: file.file?.size || 0,
    id: String(Date.now()),
    uploadName: user.userInfo?.name || "",
    uploadTime: dayjs().format("YYYY-MM-DD HH:mm:ss"),
  });
  modelForm.value[secKey] = list;
};

const removeAttachment = (secKey: string, idx: number) => {
  modelForm.value?.[secKey]?.splice(idx, 1);
};
```

### 4.2 只读附件列表（详情展示场景）

详情接口的附件字段名可能为 `attachmentList` / `attachmentDTOList` / `attachments` 并存，取值需兼容：

```typescript
const attachmentList = computed<AttachmentItem[]>(() => {
  if (!detail.value) return [];
  const d = detail.value as any;
  return d.attachmentDTOList || d.attachmentList || d.attachments || [];
});
```

文件数据结构参考（以接口实际为准）：

```typescript
interface AttachmentItem {
  id: string;
  fileName: string;      // 文件名
  fileUrl?: string;      // 预览地址
  filePath?: string;     // 存储路径
  fileSize?: number | null;
  attachmentType?: string;
  uploadName?: string;   // 上传人
  uploadTime?: string;
}
```

> ⚠️ FileCard 的下载在组件内未实现（onDownload 处理函数被注释），只读场景按现有模块惯例传 `:showDownload="false"`、`showDelete` 不传，否则渲染出点击无反应的死按钮。

---

## 5. 审批通用组件速查表（真实签名）

> 新模块**必须优先复用**以下组件；使用前可 grep 路径确认未变更。

| 组件 / hook | 路径 | 用法 |
|---|---|---|
| `ApprovalContainer` | `src/views/office/todo/components/ApprovalContainer/index.vue` | 审批公共容器（**首选**）：权限加载 + PC-only 双维度拦截 + 懒加载；slot `{ operationType }` 放只读表单；`@permission` 回调加载详情。接入方式见 §1.1 |
| `ApprovalActionBar` | `src/views/office/todo/components/ApprovalActionBar/index.vue` | 审批操作栏：按钮矩阵/审批结论/附件/抄送/completeTodoApi 提交。经 ApprovalContainer 间接使用，**不单独引入** |
| `useDict` | `@/hooks/useDict` | `const { dictMap } = useDict({ default: "DICT_CODE" })`；`dictMap.value[value]` 取 label。支持 `{ manual: true }` 延迟加载，`run(key)` 手动触发 |
| `useTodoActions` | `src/views/office/todo/red-line/hooks/index.ts` | `useTodoActions({ todoInfo, operationType, beforeAgree?, beforeReject?, agreeExtraApi?, successPath?, successMessage? })`；返回同意/驳回/抄送/已阅全套状态与方法（forwardShow/handleForward/handleForwardConfirm/userPopupShow/handleViewConfirm 等） |
| `TitleBar` | `@/components/TitleBar/index.vue` | `<TitleBar title="基础信息">` 区块标题栏，默认插槽放右侧操作 |
| `Select` | `@/components/Select/index.vue` | `<Select v-model :options="{label,value}[]" name label required :rules />` |
| `Upload` | `@/components/Upload/Upload.vue` | `<Upload @onSuccess="file => ...">触发按钮</Upload>`；file 为 `{ file, path }` 结构 |
| `FileCard` | `@/components/FileCard/index.vue` | `<FileCard :file :showDelete @delete />` 文件条目卡片；下载未实现，只读场景传 `:showDownload="false"` |
| `ApproveRecordPopup` | `@/views/office/todo/components/approveRecord/index.vue` | `<ApproveRecordPopup ispage v-model:show="show" />` 审批记录；配合 `TempVar` 控制显隐 |
| `userSelectPopup` | `@/views/office/todo/components/user-select-popup/index.vue` | `<userSelectPopup type="forward" :multiple :selectedUsers :show @submit @close />` 选人 |
| `NavBar` | `@/components/NavBar/` | 页面导航栏（layout 控制时无需手动引入） |

流程接口：

| API | 路径 | 说明 |
|---|---|---|
| `getOperationRole` | `@/api/system/flow` | `{ taskId }` → `{ data: { templateKey, operationType } }`，决定按钮与拦截 |
| `completeTodoApi` | `@/api/system/flow` | 审批完成提交，参数结构见 §1.3 |
| `forwardTodoApi` / `TodoType` | `@/api/todo` | 抄送等，`useTodoActions` 内部已封装 |

工具：

| 工具 | 路径 | 说明 |
|---|---|---|
| `$t` | `@/locales` | `$t(key, "中文兜底")`，**所有文案必须走此函数** |
| `successToast` / `failToast` | `@/utils/toast` | 操作结果提示 |
| `dayjs` | - | 日期格式化惯例 `dayjs(v).format("YYYY-MM-DD HH:mm:ss")` |

---

## 6. 通用区块与 hook 模板

### 6.1 详情加载 hook

```typescript
// hooks/useDetail.ts
import { ref } from "vue";

export function useDetail(id: string, fetchApi: (id: string) => Promise<any>) {
  const detail = ref<XxxDetail | null>(null);
  const loading = ref(false);

  const loadDetail = async () => {
    if (!id) return;
    loading.value = true;
    try {
      const res = await fetchApi(id);
      detail.value = res?.data ?? res;
    } catch (error) {
      console.error("加载详情失败", error);
    } finally {
      loading.value = false;
    }
  };

  return { detail, loading, loadDetail };
}
```

### 6.2 Section 区块组件

每个业务区块一个组件，**只接收 detail props，内部自行完成字典翻译与空值处理**：

```vue
<script setup lang="ts">
import TitleBar from "@/components/TitleBar/index.vue";
import { useDict } from "@/hooks/useDict";
import { computed } from "vue";
import type { XxxDetail } from "../../types";

const props = defineProps<{ detail: Partial<XxxDetail> }>();

const { dictMap: typeMap } = useDict({ default: "XXX_TYPE" });

const typeDisplay = computed(() => {
  const v = props.detail.type;
  if (!v) return "-";
  return typeMap.value[String(v)] || v;
});
</script>

<template>
  <div class="xxx-section">
    <TitleBar title="区块标题" />
    <van-cell-group>
      <van-field :model-value="detail.name || '-'" label="名称" readonly input-align="right" />
      <van-field :model-value="typeDisplay" label="类型" readonly input-align="right" />
    </van-cell-group>
  </div>
</template>
```

`form.vue` 组装各 Section，按 `operationType` / 数据有无控制显隐：

```vue
<van-loading v-if="loading" class="py-[40px]" />
<template v-else-if="detail">
  <DocumentInfo :detail="detail" />
  <BasicInfoSection :detail="detail" />
  <EconomicInfoSection v-if="showEconomic" :detail="detail" />
  <ReviewSection v-if="hasReviewData" :review-records="reviewRecords" :mode="reviewMode" />
</template>
```

### 6.3 类型定义惯例

```typescript
// types.ts：字段全部可选 + 逐字段中文注释 + 标注接口路径
/**
 * xxx 审批详情
 * @api /api/pm-xxx/detail/{id}
 */
export interface XxxDetail {
  /** 项目名称 */
  projectName?: string;
  /** 附件列表（后端实际字段） */
  attachmentList?: AttachmentItem[];
  /** 附件DTO列表（PC端使用，兼容取值） */
  attachmentDTOList?: AttachmentItem[];
}
```

---

## 7. 常见错误

### 7.1 历史教训（立项模块 7 次 fix 根因）

| 错误 | 现象 | 预防 |
|---|---|---|
| 只迁移字段展示，不梳理审批流 | 漏掉评审/变更/评分整块业务、漏审批结论、漏 PC 专属节点拦截 | SKILL Phase 1 四张表强制先行 |
| 节点配置内联 list.vue | 单文件 700+ 行，每次加节点全文件改动 | config.ts 独立（§2） |
| 字段与 PC 端不对齐 | 上线后逐个字段返工 | SKILL Phase 2 清单逐行打勾 |
| 未盘点既有组件 | 重复造轮子、风格不一 | SKILL Phase 0 盘点表 |

### 7.2 技术错误

**字典显示原始值而非中文**
```typescript
// 错：签名不存在
const { getDictLabel } = useDict("dict_type");
// 对：真实签名
const { dictMap } = useDict({ default: "DICT_CODE" });
const label = dictMap.value[String(value)] || value; // 回退原始值
```

**空值渲染出 undefined / [object Object]**
```vue
<!-- 错 --><van-field :model-value="data.field" />
<!-- 对 --><van-field :model-value="data.field || '-'" />
<!-- 附件对象必须取具体字段 file.fileName，不能直接渲染对象 -->
```

**附件字段名不匹配**
接口可能返回 `attachmentList` / `attachmentDTOList` / `attachments`，取值三选一兼容（§4.2）；文件名字段可能是 `name` / `fileName`，渲染前确认。

**文本溢出撑破布局**

flex 子项加 `min-width: 0`，长文本加 `overflow: hidden; text-overflow: ellipsis; white-space: nowrap`（多行用 line-clamp）。

**`pnpm lint` 会全仓改写文件**

`pnpm lint` 脚本带 `--fix`，直接运行会把全仓历史文件 prettier 重排版（一次 252 文件事故，靠 `git checkout -- .` 回滚）。校验本次改动用 `npx eslint <涉及文件>`。仓库基线本身不干净：`.eslintrc.js` 曾有语法错误（`overrides` 前缺逗号，2026-09-09 已修）导致 eslint 崩溃；`pnpm type-check`（vue-tsc）在干净工作树上也报 6 个存量 TS6504——新代码核对必须 scoped 过滤（grep 模块路径），不能以全仓命令退出码为准。

**fileCategory / 字典 code 命名实测（禁止猜，从 PC 源码抄）**

- fileCategory 惯例 `{业务}_file`：`financing_apply_file`、`withdraw_apply_file`、`epc_contract_file`
- 字典 code 无 `DICT_` 前缀：业态 `PROJ_BIZ_TYPE`、业务模式 `BUSINESS_MODE`、是否 `yes_no`（权威来源 PC 仓库 `src/hooks/dict/index.ts` 常量）
- 提款 `canWithdraw` 为硬编码 Y/N（非字典），历史值 PENDING 按 `-` 兜底

**PC 同意时回写 variable.json 的网关变量，移动端用 getOtherParam 保持一致**

PC 端 handleAgree 把业务变量合并进 variable.json 供流程网关路由（如融资申请的 projectName/projectId/projectType/financingSpecialistId/investmentHandlerId 五字段）。移动端只读节点通过容器 `getOtherParam` 从已加载详情返回同样字段；PC 普通节点不带 extraData 时移动端不传（如提款申请，可编辑节点全被 PC-only 拦截）。参考首两个 consumer：`financingApplication/list.vue`、`withdrawalApproval/list.vue`（2026-09-09）。

---

## 8. 保留模板

### 8.1 富文本只读展示

```vue
<template>
  <div class="rich-text-viewer">
    <div v-if="label" class="field-label">{{ label }}</div>
    <div class="field-content" v-html="sanitizedContent" />
  </div>
</template>
<script setup lang="ts">
import { computed } from "vue";
import DOMPurify from "dompurify";

const props = defineProps<{ label?: string; value?: string }>();

const sanitizedContent = computed(() =>
  props.value ? DOMPurify.sanitize(props.value) : ""
);
</script>
```

### 8.2 页面 Loading / 空状态

```vue
<van-loading v-if="loading" class="py-[40px]" />
<van-empty v-else-if="!detail" description="暂无数据" />
<template v-else><!-- 正常内容 --></template>
```

空状态文案规范：无数据"暂无数据"、无附件"暂无附件"、无审批记录"暂无审批记录"、搜索无结果"未找到相关内容"，均走 `$t()`。

### 8.3 明细/子表列表（卡片式）

结构：卡片容器（白底圆角）+ 行式 label/value 字段 + `van-empty` 空态。参考实现：`initiationApproval/components/ReviewSection/index.vue`。

```vue
<div class="review-card" v-for="record in records" :key="record.id">
  <div class="review-field">
    <span class="label">评审项</span>
    <span class="value">{{ record.reviewItem || "-" }}</span>
  </div>
</div>
<van-empty v-if="records.length === 0" description="暂无评审记录" />
```

```less
.review-card { background: #fff; border-radius: 8px; padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05); }
.review-field { display: flex; justify-content: space-between; font-size: 14px; padding: 6px 0;
  .label { color: #969799; flex-shrink: 0; min-width: 80px; }
  .value { color: #323233; text-align: right; flex: 1; margin-left: 12px; min-width: 0; } }
```

### 8.4 性能要点

- `v-for` 绑定稳定 key（业务 id），避免索引
- 大列表用 `van-list` 分页
- 复杂展示逻辑放 computed，不写在模板里
- 定时器/监听器在 `onUnmounted` 清理
- 字典走 `useDictStore` 缓存（`useDict` 已内置）

---

## 版本历史

- v2.1.1 (2026-09-09): §4.2/§5 补 FileCard 下载未实现的注意事项；§7.2 新增三条教训——`pnpm lint` 带 --fix 会全仓改写（校验须 scoped）、fileCategory/字典 code 命名实测、PC 网关变量经 getOtherParam 对齐。依据：融资申请/提款申请两模块迁移（ApprovalContainer 首批 consumer）。
- v2.1.0 (2026-09-09): §1 审批外壳升级为两级方案——首选 `ApprovalContainer` 公共容器接入（新增 §1.1 接入模板 + §1.2 等价性验收清单），手写外壳降为后备（§1.3）；§5 补容器组件签名。依据：分支 `feat/mobile-approval-container` 新建的组件化审批外壳（把立项等模块 400-731 行重复外壳收敛为一个组件）。
- v2.0.0 (2026-09-09): 全面重构。废弃不存在的 MobileFileUpload 模板；useDict 修正为真实签名 `{ default }` → `dictMap`；字段渲染改为项目 van-field readonly 惯例；新增审批外壳标准模板（§1）、config.ts 节点配置模板（§2）、审批组件真实签名速查表（§5）、i18n 规范。依据：立项审批模块交付后 7 次 fix 的根因分析。
- v1.0.0 (2026-04-30): 初始版本，包含所有代码模板。
