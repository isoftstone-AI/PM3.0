# 附件上传代码模板

> 基准代码来源：`src/views/eng-manage/start-apply/`、`src/views/design-manage/equipment-submission/` 实际上线版本
> 所有 `[REPLACE]` 标记的区域需要根据业务需求替换
> 所有 `[KEEP]` 标记的区域保持模板代码不变

---

## Block 0: 通用类型定义

```typescript
// [KEEP] 附件 —— 后端返回/前端传输的附件对象
interface Attachment {
  id: string;
  filename: string;          // 文件名
  filePath: string;          // OSS 路径
  uploadName?: string;       // 上传人
  uploadTime?: string;       // 上传时间
  attachmentType?: string;   // 附件类型标识（区分业务类型）
}

// [KEEP] 附件类型配置 —— AttachmentFileList 聚合模式使用
interface AttachmentTypeConfig {
  type: string;              // 类型标识（对应 attachmentType）
  label: string;             // 显示名称
  required?: boolean;        // 是否必填
  maxCount?: number;         // 最大上传数量
  accept?: string;           // 允许的文件类型
  maxSize?: number;          // 最大文件大小(MB)
}

// [KEEP] 文件传输对象 —— UploadTable / 开发管理模块使用
type FileDTO = {
  fileCode?: string;
  fileName: string;
  fileUrl: string;
  fileFullUrl?: string;
  uploadName?: string;
  uploadTime?: string;
  [key: string]: any;
};
```

---

## Block 1: Upload Props 完整参考

```typescript
// Upload 组件 Props 参考（不需要全部配置，按需选取）
{
  bucketName: 'public',          // [KEEP] OSS 存储桶，统一用 public
  multiple: true,                // [OPTIONAL] 多文件上传
  maxCount: 5,                   // [OPTIONAL] 最大文件数量，不设则无限制
  maxSize: 200,                  // [OPTIONAL] 文件大小限制(MB)
  accept: '.doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.txt',
  defaultValue: state.attachmentList,  // [KEEP] 已上传文件列表
  onlyShowFileList: props.disabled,    // [KEEP] 只读模式控制（true=只显示列表，false=可上传）
  showUploadList: { showRemoveIcon: !props.disabled }, // [KEEP] 删除图标控制（非 useFileCard 模式）
  useFileCard: true,             // [KEEP] 启用 FileCard 渲染模式（推荐）
  showDelete: true,              // [KEEP] FileCard 显示删除按钮
  showDownload: true,            // [OPTIONAL] FileCard 显示下载按钮（审批场景建议 false，业务表单 true）
  showView: true,                // [KEEP] FileCard 显示预览按钮
  showName: true,                // [KEEP] FileCard 显示文件名
  showTime: false,               // [KEEP] FileCard 显示上传时间
  onSuccess: handleSuccess,      // [KEEP] 上传成功回调
  onRemove: handleRemove,        // [KEEP] 删除回调（useFileCard 模式下必须显式绑定）
  onChange: handleChange,        // [KEEP] 文件列表变化回调（Table 内嵌场景必须绑定）
}
```

---

## Block 2: AttachmentFileList Props 完整参考

```typescript
// AttachmentFileList 组件 Props 参考
{
  dataSource: attachmentFileList.value,  // [KEEP] 计算属性，类型 AttachmentFile[]
  showTitle: false,                     // [OPTIONAL] 是否显示标题
  title: '附件列表',                    // [OPTIONAL] 自定义标题
  showDownloadAll: true,                // [OPTIONAL] 一键下载
  showAttachmentType: true,             // [OPTIONAL] 显示附件类型列
  attachmentTypeTitle: '附件类型',      // [OPTIONAL] 类型列标题
  enableAggregation: true,              // [KEEP] 启用聚合模式（按类型分组）
  attachmentTypeConfigs: ATTACHMENT_TYPE_CONFIGS, // [REPLACE] 类型配置数组
  readonly: props.disabled,             // [KEEP] 只读控制
  showDelete: !props.disabled,          // [KEEP] 删除按钮控制
  emptyText: '暂无附件',               // [OPTIONAL] 空数据提示
  onUploadSuccess: handleUploadSuccess, // [KEEP] 上传成功回调
  onDelete: handleRemove,               // [KEEP] 删除回调
}

// Expose 方法
// validator(): { valid: boolean; missingTypes: AttachmentTypeConfig[] }
// getAttachmentList(): AttachmentFile[]
```

---

## Block 3: Upload 独立上传区（工程管理模式）

> 适用：表单中独立的附件上传区域（如会议纪要、成本测算附件）
> 特点：从统一 attachmentList 中按类型过滤，上传/删除后合并回去

```tsx
import { reactive, onMounted, watch } from 'vue';
import Upload from '@/components/Upload/Upload.vue';
// [REPLACE] 导入当前业务模块的附件类型枚举
import { Attachment_type_enum } from '@/store/modules/dict';

// [REPLACE] 替换为当前业务类型的枚举值
const MY_TYPE = Attachment_type_enum.eng_hyjy;

export default defineComponent({
  // [REPLACE] 替换组件名
  name: 'MeetingMinutesSection',
  props: {
    modelValue: { type: Object, default: () => ({}) },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const state = reactive({
      attachmentList: [] as any[],
    });

    // [KEEP] 加载数据：从统一 attachmentList 中过滤当前类型
    const loadData = (val: any) => {
      state.attachmentList = (val.attachmentList || [])
        .filter((a: any) => a.attachmentType === MY_TYPE)
        .map((a: any) => ({
          ...a,
          url: a.filePath,
          path: a.filePath,
          fileName: a.filename,
        }));
    };

    // [KEEP] watch 必须在 onMounted 中调用
    onMounted(() => {
      watch(() => props.modelValue, val => loadData(val), {
        immediate: true,
        deep: true,
      });
    });

    // [KEEP] 上传成功：添加到当前类型列表，同步到父组件
    const handleSuccess = (e: any, path: string) => {
      state.attachmentList.push({
        attachmentType: MY_TYPE,
        filename: e.file['name'],
        filePath: path,
        id: e.file['uid'],
      });
      syncToParent();
    };

    // [KEEP] 删除：从列表中移除
    const handleRemove = (e: any) => {
      state.attachmentList = state.attachmentList.filter(
        (a: any) => a.id !== (e['id'] || e['uid']),
      );
      syncToParent();
    };

    // [KEEP] 同步到父组件：排除其他类型附件 + 合并当前类型
    const syncToParent = () => {
      const otherAttachments = (props.modelValue?.attachmentList || [])
        .filter((a: any) => a.attachmentType !== MY_TYPE);
      emit('update:modelValue', {
        ...props.modelValue,
        attachmentList: [...otherAttachments, ...state.attachmentList],
      });
    };

    return () => (
      <Upload
        bucketName="public"
        multiple
        onlyShowFileList={props.disabled}
        // [REPLACE] 根据业务调整 accept
        accept=".doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.txt"
        defaultValue={state.attachmentList}
        useFileCard
        showDelete={!props.disabled}
        showDownload
        showView
        showName
        showTime={false}
        onSuccess={handleSuccess}
        onRemove={handleRemove}
      />
    );
  },
});
```

---

## Block 4: Upload 表格内嵌上传

> 适用：Table 的某一列中嵌入 Upload，每行独立管理附件（如经济信息毛利率表、设备提资明细）
> 特点：每行一个附件字段，直接操作父组件数据，无中间 state
> **铁律**：useFileCard 模式下必须同时绑定 `onChange` 和 `onRemove`，否则 FileCard 删除不会回写到 dataSource

```tsx
import Upload from '@/components/Upload/Upload.vue';

export default defineComponent({
  // [REPLACE] 替换组件名
  name: 'EconomicInfoSection',
  props: {
    modelValue: { type: Object, default: () => ({}) },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {

    // [KEEP] 按类型获取已有附件，转换为 Upload 需要的格式（补 url + path）
    const getDefaultValue = (type: string) =>
      (props.modelValue?.attachmentList || [])
        .filter((a: any) => a.attachmentType === type)
        .map((a: any) => ({
          ...a,
          url: a.filePath,
          name: a.filename,
          path: a.filePath,
        }));

    // [KEEP] 上传成功：排除同类型旧数据 + 合并新附件
    const handleSuccess = (type: string, e: any, path: string) => {
      const otherAttachments = (props.modelValue?.attachmentList || [])
        .filter((a: any) => a.attachmentType !== type);
      emit('update:modelValue', {
        ...props.modelValue,
        attachmentList: [
          ...otherAttachments,
          { attachmentType: type, filename: e.file['name'], filePath: path, id: e.file['uid'] },
        ],
      });
    };

    // [KEEP] 删除：按类型 + id 过滤
    const handleRemove = (type: string, e: any) => {
      emit('update:modelValue', {
        ...props.modelValue,
        attachmentList: (props.modelValue?.attachmentList || [])
          .filter((a: any) => !(a.attachmentType === type && a.id === e['id'])),
      });
    };

    // [REPLACE] 替换表格列定义
    const columns = [
      { title: '类型', dataIndex: 'capacityType' },
      // ... 其他数据列
      {
        title: '附件',
        customRender: ({ record }: any) => (
          <Upload
            defaultValue={getDefaultValue(record.type)}
            bucketName="public"
            accept=".doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.txt"
            onlyShowFileList={props.disabled}
            useFileCard
            showDelete={!props.disabled}
            showDownload
            showView
            showName
            showTime={false}
            onSuccess={(file: any, path: string) => handleSuccess(record.type, file, path)}
            onRemove={(file: any) => handleRemove(record.type, file)}
          />
        ),
      },
    ];

    // [REPLACE] 替换数据源
    return () => <Table columns={columns} dataSource={dataSource} pagination={false} />;
  },
});
```

---

## Block 5: Upload 审批操作上传（最简配置）

> 适用：审批意见补充材料等场景，无 attachmentType 标识，不参与类型过滤合并
> 特点：最简配置，本地 state 管理

```tsx
// [REPLACE] 替换组件名
export default defineComponent({
  name: 'ApprovalActionSection',
  setup() {
    const state = reactive({
      fileList: [] as any[],
    });

    return () => (
      <Upload
        bucketName="public"
        maxCount={5}
        multiple
        useFileCard
        showDelete
        showDownload={false}   // [KEEP] 审批附件默认不显示下载，业务表单才开启
        showView
        showName
        // [REPLACE] 根据业务调整 accept
        accept=".doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.txt"
        onSuccess={(e: any, path: string) => {
          state.fileList = [...state.fileList, {
            id: Date.now().toString(),
            filename: e.file?.name || path.split('/').pop() || '',
            filePath: path,
          }];
        }}
        onRemove={(e: any) => {
          state.fileList = state.fileList.filter(
            (item: any) => item.id !== (e.id || e.uid),
          );
        }}
      />
    );
  },
});
```

---

## Block 6: AttachmentFileList 聚合模式

> 适用：一个区域内有多种附件类型，各自有必填/数量限制，需要按类型分组展示
> 特点：AttachmentFileList 自带上传/删除/校验，通过 Expose 暴露 validator

```tsx
import { computed, ref, onMounted, watch } from 'vue';
import AttachmentFileList from '@/components/AttachmentFileList';
import type { AttachmentTypeConfig, AttachmentFileListExpose } from '@/components/AttachmentFileList';
// [REPLACE] 导入当前业务模块的附件类型枚举
import { Attachment_type_enum } from '@/store/modules/dict';

// [REPLACE] 定义附件类型配置 —— 根据业务替换 type、label、required 等
const ATTACHMENT_TYPE_CONFIGS: AttachmentTypeConfig[] = [
  {
    type: Attachment_type_enum.eng_kgsqbg,
    label: '开工申请报告',
    required: true,
    maxCount: 5,
    accept: '.doc,.docx,.xls,.xlsx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.ppt,.pptx,.txt',
    maxSize: 200,
  },
  {
    type: Attachment_type_enum.eng_kgpsb,
    label: '开工评审表',
    required: true,
    maxCount: 5,
    accept: '.doc,.docx,.xls,.xlsx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.ppt,.pptx,.txt',
    maxSize: 200,
  },
  {
    type: Attachment_type_enum.eng_other,
    label: '其他',
    required: false,
    maxCount: 10,
    accept: '.doc,.docx,.xls,.xlsx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.ppt,.pptx,.txt',
    maxSize: 200,
  },
];

export default defineComponent({
  // [REPLACE] 替换组件名
  name: 'StartInfoSection',
  props: {
    modelValue: { type: Object, default: () => ({}) },
    disabled: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const refAttachment = ref<AttachmentFileListExpose>();

    // [KEEP] 数据转换：Attachment → AttachmentFile
    // 注意：必须同时设置 fileName 和 filename
    const attachmentFileList = computed(() => {
      const list = props.modelValue?.attachmentList || [];
      return list.map((att: any) => ({
        id: att.id,
        fileName: att.filename,     // AttachmentFile 需要 fileName
        filename: att.filename,     // 同时保留 filename
        filePath: att.filePath,
        uploader: att.uploadName,
        uploadName: att.uploadName,
        uploadTime: att.uploadTime,
        attachmentType: att.attachmentType,
      }));
    });

    // [KEEP] 上传成功回调：添加新附件到列表
    const handleUploadSuccess = (attachment: any) => {
      const newAttachment = {
        id: attachment.id || Date.now().toString(),
        filename: attachment.filename || '',
        filePath: attachment.filePath || '',
        uploadName: attachment.uploadName || '',
        uploadTime: attachment.uploadTime || new Date().toLocaleString(),
        // [REPLACE] 默认附件类型根据业务调整
        attachmentType: attachment.attachmentType || 'eng_other',
      };
      const currentList = props.modelValue?.attachmentList || [];
      emit('update:modelValue', {
        ...props.modelValue,
        attachmentList: [...currentList, newAttachment],
      });
    };

    // [KEEP] 删除回调：用 id + filePath 双重匹配
    const handleRemove = (record: any) => {
      const newList = (props.modelValue?.attachmentList || [])
        .filter((item: any) => item.id !== record.id && item.filePath !== record.filePath);
      emit('update:modelValue', {
        ...props.modelValue,
        attachmentList: newList,
      });
    };

    // [KEEP] 校验方法（供父组件调用）
    const validate = async () => {
      const result = refAttachment.value?.validator();
      if (result && !result.valid) {
        const names = result.missingTypes.map((t: any) => t.label).join('、');
        return Promise.reject(`${names}为必填附件`);
      }
      return Promise.resolve();
    };

    ctx.expose({ validate });

    return () => (
      <AttachmentFileList
        ref={refAttachment}
        dataSource={attachmentFileList.value}
        showTitle={false}
        showDownloadAll={true}
        showAttachmentType={true}
        attachmentTypeTitle="附件类型"
        enableAggregation={true}
        attachmentTypeConfigs={ATTACHMENT_TYPE_CONFIGS}
        readonly={props.disabled}
        showDelete={!props.disabled}
        emptyText="暂无附件"
        onUploadSuccess={handleUploadSuccess}
        onDelete={handleRemove}
      />
    );
  },
});
```

---

## Block 7: 开发管理模块简化模式（dmanage）

> 适用：开发管理模块（dmanage），使用 `attachmentDTOList` 字段，通常只有一种附件类型
> 特点：简单绑定，无过滤合并逻辑

```tsx
import Upload from '@/components/Upload/Upload.vue';

export default defineComponent({
  // [REPLACE] 替换组件名
  name: 'DevAuthForm',
  setup() {
    const formData = reactive({
      // [REPLACE] 其他表单字段...
      attachmentDTOList: [] as FileDTO[],
    });

    // [KEEP] 简单模式：直接绑定，无需过滤合并
    return () => (
      <>
        {/* [REPLACE] 其他表单项... */}
        <FormItem label="附件" name="attachmentDTOList" rules={[{ required: true, message: '请上传附件' }]}>
          <Upload
            bucketName="public"
            multiple
            defaultValue={formData.attachmentDTOList}
            useFileCard
            showDelete
            showDownload
            showView
            showName
            showTime={false}
            onSuccess={(e: any, path: string) => {
              formData.attachmentDTOList.push({
                // [REPLACE] 根据业务设置 attachmentType
                attachmentType: '1',
                fileName: e.file.name,
                fileUrl: path,
              });
            }}
            onRemove={(e: any) => {
              formData.attachmentDTOList = formData.attachmentDTOList
                .filter((item: any) => item.fileUrl !== e.url);
            }}
          />
        </FormItem>
      </>
    );
  },
});
```

---

## Block 8: 父组件附件合并模板

> 适用：工程管理模式中，父组件需要监听多个子组件的附件变化并合并

```tsx
// [KEEP] 父组件中监听子组件变化，合并各子组件的附件
const handleSectionChange = (childType: string, v: any) => {
  if (v.attachmentList !== undefined) {
    // 排除该子组件管理的类型，再合并新数据
    const otherAttachments = (detail.value.attachmentList || [])
      .filter((a: any) => a.attachmentType !== childType);
    detail.value.attachmentList = [...otherAttachments, ...(v.attachmentList || [])];
  }
  // 其他字段直接合并
  Object.assign(detail.value, v);
};

// [KEEP] 最终提交时，attachmentList 已包含所有子组件的附件
const handleSubmit = async () => {
  const params = {
    ...detail.value,
    // attachmentList 会在提交时自动序列化
  };
  await saveApi(params);
};
```

---

## 附录：常见 accept 值

```
全格式：.doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.jpg,.jpeg,.png,.bmp,.rar,.zip,.txt
纯文档：.doc,.docx,.xls,.xlsx,.ppt,.pptx,.pdf,.txt
图片：  .jpg,.jpeg,.png,.bmp
```

---

## Block 9: 铁律与踩坑代码示例

> 本 Block 记录实际开发中踩过的坑，生成代码时必须对照检查。

### 9.1 同一字段禁止混用 Upload 和 AttachmentFileList

Upload 的 `onlyShowFileList` prop 可以同时覆盖编辑态和只读态，不需要切换组件。

```tsx
// ❌ 错误：编辑态用 Upload，只读态用 AttachmentFileList
// 问题：两个组件数据格式不同、prop 名不同，极易出错
// AttachmentFileList 的数据 prop 是 dataSource 不是 files，传错直接报 not iterable
{editable ? (
  <Upload v-model={text} onChange={...} />
) : (
  <AttachmentFileList files={text} readOnly />
)}

// ✅ 正确：统一用 Upload + onlyShowFileList + useFileCard
<Upload
  v-model={text}
  onlyShowFileList={!editable}   // true=只显示列表，false=可上传
  useFileCard
  showDelete={editable}
  showDownload
  showView
  showName
  showTime={false}
  onChange={...}
  onRemove={...}
/>
```

### 9.2 接口返回的文件数据必须转换

接口返回的 `FileInfo` / `FileDTO` 只有 `fileUrl`、`fileName`，但 Upload 组件的预览/下载依赖 `url` 和 `path` 字段。

Upload 组件内部预览/下载链路（`handlePreview`）：
1. 先找 `file.url` → 如果是有效 URL → 直接下载
2. 再找 `file[props.path]`（默认 `'path'`） → 通过 `getFileUrl` API 获取下载地址
3. 都没有 → 静默失败，无法下载

```typescript
// [KEEP] 转换函数：补 url/path/name/uid/status 字段
const convertFilesForUpload = (detail: Record<string, any>) => {
  const FILE_FIELDS = ['technicalSpecFiles', 'technicalAgreementFiles', 'manufacturerFiles'] as const;
  // [REPLACE] 替换为实际的文件字段名
  const converted = { ...detail };
  FILE_FIELDS.forEach((field) => {
    const files = converted[field];
    if (Array.isArray(files)) {
      (converted as any)[field] = files.map((f: any) => ({
        ...f,
        uid: f.uid || f.fileId,           // Upload 内部识别用
        name: f.name || f.fileName,       // FileCard 显示用
        status: 'done',                   // Upload 状态
        url: f.fileUrl,                   // Upload handlePreview 下载/预览用
        path: f.fileUrl,                  // Upload handlePreview 兜底用
      }));
    }
  });
  return converted;
};

// [KEEP] 初始化赋值时转换
const dataSource = reactive(
  (props.details || []).map(convertFilesForUpload),
);

// [KEEP] watch 更新时也要转换（不能只转一处）
onMounted(() => {
  watch(
    () => props.details,
    (newDetails) => {
      if (Array.isArray(newDetails)) {
        dataSource.splice(0, dataSource.length, ...newDetails.map(convertFilesForUpload));
      }
    },
    { deep: true },
  );
});
```

### 9.3 Table customRender 中 v-model 是伪绑定

`customRender` 的 `text` 参数是 Table 内部的值拷贝，不是响应式引用。`v-model={text}` 不会回写到 `dataSource`。

**在 useFileCard 模式下，FileCard 的删除按钮不走 Upload 默认的 `@remove` 事件流，必须通过 `onChange` + `onRemove` 双回调确保数据同步。**

```tsx
// ⚠️ v-model 只用于给 Upload 传入初始值
// ✅ 真正的回写靠 onChange / onRemove 回调
{
  title: '附件',
  dataIndex: 'fileList',
  customRender: ({ text, index }) => {
    const editable = isFieldEditable('fileList');
    return (
      <Upload
        v-model={text}                    // 传入初始值（伪绑定）
        onlyShowFileList={!editable}       // 控制编辑/只读
        useFileCard
        showDelete={editable}
        showDownload
        showView
        showName
        showTime={false}
        onChange={(v) => handleFileChange(index, 'fileList', v)}    // ✅ 上传/增删回写
        onRemove={(file) => handleFileRemove(index, 'fileList', file)} // ✅ FileCard 删除回写
      />
    );
  },
}
```

### 9.4 useFileCard 模式下 onRemove 必须显式处理

FileCard 组件的删除逻辑在 Upload 内部通过 `onDelete` 触发，虽然 Upload 会更新自身的 `fileList`，但**在 customRender 等伪绑定场景中，父组件的 dataSource 不会自动同步**。

```tsx
// ❌ 错误：只绑 onChange，FileCard 删除后 dataSource 不同步
<Upload v-model={text} useFileCard onChange={handleFileChange} />

// ✅ 正确：同时绑定 onChange + onRemove
<Upload
  v-model={text}
  useFileCard
  showDelete={editable}
  onChange={handleFileChange}
  onRemove={handleFileRemove}
/>

// 父组件中：onRemove 回调里手动过滤并同步
const handleFileRemove = (index: number, field: string, file: any) => {
  const currentFiles = dataSource[index][field] as any[];
  const filePath = file.url || file.path || file.fileUrl;
  const fileName = file.name || file.fileName;
  dataSource[index][field] = currentFiles.filter((f: any) => {
    const fPath = f.url || f.path || f.fileUrl;
    const fName = f.name || f.fileName;
    return fPath !== filePath || fName !== fileName;
  }) as any;
  props.onUpdateDetails([...dataSource]);
};
```

### 9.5 AttachmentFileList 数据 prop 是 dataSource 不是 files

如果确实需要使用 AttachmentFileList（多类型聚合场景），注意：

```tsx
// ❌ 错误：prop 名写错
<AttachmentFileList files={data} readOnly />
// files 不是组件声明的 prop，dataSource 实际为 undefined
// watch immediate 执行 [...undefined] → TypeError: not iterable

// ✅ 正确
<AttachmentFileList dataSource={data || []} readonly />
```

| 组件 | 数据 prop | 只读 prop |
|------|----------|-----------|
| Upload | `v-model` / `modelValue` | `onlyShowFileList` |
| AttachmentFileList | `dataSource` | `readonly` |

### 9.6 审批提交时的文件数据清洗

审批页 `onSubmit` 中，从详情组件获取的文件数据包含前端 Upload 注入的 `uid`、`status` 等字段，提交前必须清洗为后端需要的格式。

```typescript
// [KEEP] 文件字段清洗：提取为后端 FileInfo 格式
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
