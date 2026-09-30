---
name: pattern-upload
description: 附件上传组件选择与代码生成器。当需求涉及附件、文件、材料上传/下载/预览时触发。优先使用 Upload 组件 + onlyShowFileList 控制编辑/只读态，禁止混用多个上传组件。
category: code-generation
tools: AskUserQuestion, Read, Glob, Grep, Write, Edit
version: 2.0.0
---

# 附件上传组件选择与代码生成

## 铁律（违反即错误）

1. **Upload 优先**：80% 场景用 Upload + `onlyShowFileList` 即可，禁止同一字段混用 Upload 和 AttachmentFileList
2. **接口数据必须转换**：接口返回的 `fileUrl` → 必须映射为 `url` + `path`，初始化和 watch 都要转
3. **customRender 中 v-model 是伪绑定**：`text` 是值拷贝，回写靠 `onChange` 回调
4. **`useFileCard` 模式下必须绑定 `onRemove`**：只写 `showDelete` 不绑 `onRemove` → 点击删除后数据不同步，页面刷新才消失

> 具体代码示例见 `references/reference.md` Block 9（铁律与踩坑）

## 执行前准备

1. 读取 `references/reference.md` 获取代码模板、类型定义和踩坑示例
2. 读取项目 `CLAUDE.md` 确认组件路径和编码规范

## Step 1：选组件

```
需要按类型分组管理（多种附件类型，各有必填/数量限制）？
└── 是 → AttachmentFileList
└── 否 → Upload（覆盖上传、展示、预览、下载、表格内嵌全部场景）
```

| 组件 | 导入路径 | 一句话定位 |
|------|----------|-----------|
| Upload | `@/components/Upload/Upload.vue` | 通用上传，覆盖 80% 场景 |
| AttachmentFileList | `@/components/AttachmentFileList` | 仅用于多类型附件聚合管理 |

> FileCard、UploadTable、ProgressUpload 按需使用，优先级低于 Upload。

## Step 2：选模式

| 模式 | 字段名 | 数据类型 | Block |
|------|--------|----------|-------|
| 工程管理（eng-manage） | `attachmentList` | `Attachment[]` | Block 3 |
| 开发管理（dmanage） | `attachmentDTOList` | `FileDTO[]` | Block 7 |
| 表格内嵌 | 自定义 | 接口返回 | Block 4 |
| 审批操作 | 无类型标识 | 本地 state | Block 5 |

## Step 3：生成代码

从 `references/reference.md` 选择对应 Block，替换 `[REPLACE]` 标记。

## Step 4：自检清单

生成代码后逐项检查，**未通过则立即修正**：

- [ ] 同一字段是否只用了 Upload（没有混用 AttachmentFileList 做编辑/只读切换）
- [ ] 接口返回的文件数据是否转换了 `url` 和 `path` 字段
- [ ] 转换是否覆盖了初始化赋值和 watch 更新两处
- [ ] `onlyShowFileList` 逻辑是否正确（`!editable` = 非编辑态只显示列表）
- [ ] Table customRender 中是否通过 `onChange` 回写数据（不是靠 v-model）
- [ ] **`useFileCard` 模式下是否同时绑定了 `onChange` + `onRemove`**（只绑一个会导致删除不同步）
- [ ] AttachmentFileList 数据 prop 是否为 `dataSource`（不是 `files`）
- [ ] watch 是否放在 `onMounted` 中

## 引用文件

- 代码模板 + 铁律示例 → `references/reference.md`（必须先读取）
- 核心组件表 → 项目 `CLAUDE.md`
