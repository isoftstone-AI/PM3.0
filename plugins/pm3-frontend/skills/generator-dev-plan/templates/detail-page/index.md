# {{pageName}} - 审批详情页（全量只读）

{{> nav-links}}

{{> page-intro }}

---

## 使用 Skill 指引

| 步骤 | Skill | 用途 | 输入 | 输出 |
|------|-------|------|------|------|
| 1 | `/scene-detail` | 生成详情页基础框架 | PRD 路径、API 文档路径 | `{{componentName}}DetailModal/index.tsx` + `useDetail.ts` |
| 2 | 手动调整 | 补充附件预览/下载逻辑 | - | 符合本规范 |

> **Skill 使用说明：**
> ```bash
> /scene-detail prdPath=设计管理/开发方案/xx-详情页-Mx-xxx.md apiPath=src/views/{{pagePath}}/api/index.ts
> ```

---

## 模块结构布局

**使用 Card 包裹每个 Section：**

```tsx
// {{componentName}}DetailModal/index.tsx
import { Card, Button } from 'ant-design-vue';
import DocumentInfoSection from '../DocumentInfoSection/index.tsx';
import BasicInfoSection from '../BasicInfoSection/index.tsx';
import EquipmentDetailSection from '../EquipmentDetailSection/index.tsx';
import styles from './style.module.less';
```

---

## M1：单据信息

> **复用组件：** `DocumentInfoSection`（与审批页共用）

| # | 字段名 | 中文名 | 只读 | 数据源 |
|---|--------|--------|------|--------|
| 1 | applicantName | 申请人 | ✅ | 详情接口 |
| 2 | applicantDeptName | 申请部门 | ✅ | 详情接口 |
| 3 | applyTime | 申请时间 | ✅ | 时间戳格式化 |
| 4 | status | 审批状态 | ✅ | Tag + 字典映射 |
| 5 | approvalFinishTime | 审批通过时间 | ✅ | 时间戳格式化 |
| 6 | submissionNo | 申请单号 | ✅ | 详情接口 |

---

## M2：基础信息（只读）

> **复用组件：** `BasicInfoSection`（`editable=false`）

{{#each fields}}
### 字段{{math @index "+" 1}}：{{name}}（{{label}}）

| 属性 | 值 |
|------|-----|
| field | `{{name}}` |
| label | `{{label}}` |
| 只读 | ✅ 是 |
{{#if specialRender}}| 渲染方式 | {{specialRender}} |
{{/if}}

{{/each}}

---

## M3：设备提资明细（只读表格）

| # | 列名 | 字段 | 宽度 | 渲染方式 |
|---|------|------|------|----------|
| 1 | 序号 | index | 60px | 自动序号 |
| 2 | 设备名称 | equipmentName | 150px | 文本 |
| 3 | 规格型号 | equipmentSpecModel | 180px | 文本 |
| 4 | 技术规范书及图纸 | technicalSpecFiles | 200px | FileList（预览+下载） |
| 5 | 技术负责人 | techLeaders | 120px | 多人","拼接 |
| 6 | 供货厂家 | supplierName | 140px | 文本 |
| 7 | 采购负责人 | procurementLeaders | 120px | 多人","拼接 |
| 8 | 技术协议 | technicalAgreementFiles | 180px | FileList（预览+下载） |
| 9 | 厂家提资资料 | manufacturerFiles | 180px | FileList（预览+下载） |
| 10 | 备注 | detailRemark | 100px | 文本 |

---

## M4：审批记录

> **数据源：** 详情接口返回的 `approvalRecords` 字段

| # | 列名 | 字段 | 宽度 | 渲染方式 |
|---|------|------|------|----------|
| 1 | 序号 | index | 60px | 自动序号 |
| 2 | 审批节点 | nodeName | 200px | 文本 |
| 3 | 审批人 | approverName | 150px | 文本 |
| 4 | 动作 | action | 100px | 文本 |
| 5 | 时间 | approveTime | 180px | YYYY-MM-DD HH:mm:ss |
| 6 | 审批意见 | comment | 300px | 文本 |
| 7 | 附件 | attachment | 100px | 文件下载 |

**顶部操作：** 查看流程图 → 打开流程图弹窗

---

## M5：底部按钮

| 按钮名 | 功能 | 点击行为 |
|--------|------|---------|
| 关闭 | 关闭弹窗 | 关闭弹窗 |

---

## 接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| getEquipmentSubmissionDetail | GET | `/api/pm-design/equipmentSubmission/detail/{id}` | 获取详情 |

---

## Skill 生成后的检查清单

- [ ] **DocumentInfoSection 复用**：是否复用了审批页的单据信息组件
- [ ] **BasicInfoSection 复用**：是否复用了 editable=false 模式
- [ ] **设备明细只读**：所有字段均为只读，无编辑功能
- [ ] **文件列操作**：技术规范书、技术协议、厂家提资资料支持预览和下载
- [ ] **审批记录**：包含查看流程图按钮
- [ ] **全量只读**：整个页面无可编辑字段

---

{{> self-check}}

{{> dev-checklist}}

{{> dev-reconciliation}}
