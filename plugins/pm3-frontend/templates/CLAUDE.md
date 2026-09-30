# PM 3.0 前端开发规范
Follow first principles: start from real needs and problem essence, not conventions.
I may not know my own needs clearly. Pause to clarify if goals are vague.
If your solution is not optimal, state it directly and propose a better one.
Solve root causes, not symptoms. Justify every decision with "why".
**我们使用中文进行交流**
**用最简单、最直接的方式解决问题**：优先用框架原生能力（如 v-if 条件渲染销毁组件），而非添加额外的 watch、reset 逻辑等补丁代码。能一行解决的不写十行。
Deliver only key points; cut irrelevant information.
**严格遵循**: 以下规范所述即是**铁的纪律**.
**令行禁止**,**言出法随**,**用户的命令既是铁律,既是第一行动准则**,**执行力当如我军,党指挥枪原则**

> 技术栈：Vue 3 + TypeScript + Ant Design Vue 4 + Vite

---

## 工作流规则（重要）
所有代码修改任务必须遵循以下流程：

1. **先输出方案**：分析需求，输出完整方案（涉及文件、修改内容、技术方案）
2. **等待确认**：明确告知"以上是方案，请确认后我开始实施"
3. **复杂任务使用 brainstorming**：在给方案前，先使用 brainstorming skill 辅助思考，给出答案前使用卡尼曼慢思考方法来审一下，保证方案逻辑准确，无遗漏。
4. **用户确认后编辑**：只有用户明确确认后才能开始修改代码

---

## 快速开始（必读）

### 1. 技术栈

- **框架**：Vue 3
- **语言**：TypeScript
- **UI 库**：Ant Design Vue 4
- **构建工具**：Vite
- **样式方案**：Tailwind CSS + CSS Module + Less
- **开发最佳搭配** vue3+tsx

### 2. 核心组件（编码时优先使用）
**注意事项**
- 上传组件有多种，如果业务无法确认，请打断提示用户使用哪个
- 用户选择组件，优先考虑使用 LovSelect

| 组件                    | 导入路径                     | 用途                                 |
| ----------------------- | ---------------------------- | ------------------------------------ |
| BasicTable              | `@/components/BasicTable`    | 表格（强制使用，禁止直接用 a-table） |
| useTable                | `@/components/BasicTable`    | 表格逻辑 hook                        |
| DictSelect              | `@/components/DictSelect`    | 字典选择（编辑表单/搜索表单）；表格列只读用 DictLabel |
| DictLabel               | `@/components/DictLabel`     | 字典标签只读展示（**列表表格列**专用，禁止用 DictSelect） |
| OrgSelect               | `@/components/OrgSelect`     | 组织选择                             |
| SearchSelect            | `@/components/SearchSelect`  | 搜索选择                             |
| LovSelect               | `@/components/LovSelect`     | 用户选择（优先考虑）                              |
| UserSelect              | `@/components/UserSelect`    | 用户选择                             |
| CountrySelect           | `@/components/CountrySelect` | 国家选择                             |
| BooleanSelect           | `@/components/BooleanSelect` | 是/否选择                            |
| Upload                  | `@/components/Upload`        | 文件上传 （简单模式）                            |
| FileCard                | `@/components/FileCard`      | 文件卡片                             |
| Export                  | `@/components/Export`        | 导出按钮                             |
| Loading                 | `@/components/Loading`       | 加载中                               |
| Input/Select/DatePicker | `ant-design-vue`             | 基础表单组件                         |
| AttachmentFileList      | `@/components/AttachmentFileList` | 多类型附件管理（上传/预览/下载），复杂分类含表格 |
| ProgressUpload          | `@/components/ProgressUpload` | 增强版文件上传（带进度），特殊要求             |
| UploadTable             | `@/components/UploadTable`   | 表格形式附件管理 （最后再考虑）                    |
| I18nInput               | `@/components/I18nInput`     | 多语言输入框                         |
| PaginationSelect        | `@/components/PaginationSelect` | 大数据量分页选择器                |
| MaterialCategoryTreeSelect | `@/components/MaterialCategoryTreeSelect` | 物料分类树选择       |
| Period                  | `@/components/Period`        | 年度+季度/月度期间选择               |
| ProjectSelectModal      | `@/components/ProjectSelectModal` | 项目选择弹窗                     |
| RangeNumberInput        | `@/components/RangeNumberInput` | 数值范围输入（最小-最大）          |
| DoubleInputNumber       | `@/components/common/DoubleInputNumber` | 双数字输入框                |
| StorageScaleInput       | `@/components/common/StorageScaleInput` | 储能规模输入(MW+MWh)     |
| ModuleTitle             | `@/components/ModuleTitle`   | 表单分组标题（带左侧竖条装饰）       |
| OverseasRegionCascader  | `@/components/OverseasRegionCascader` | **海外**区域级联（国家→省份），替代国内 Cascader |
| OSLovSelect             | `@/components/OSLovSelect` | **海外**用户选择器，替代国内 LovSelect |

### 3. 常用字段（快速参考）

> 来源：`.claude/skills/scene-form/references/form-map.md` / `form-map2.md`

| 字段名            | 中文名       | 组件        | 必填 | 特殊逻辑                              |
| ----------------- | ------------ | ----------- | ---- | ------------------------------------- |
| proName           | 项目名称     | Input       | ✅   | max: 128，部分模块支持自动生成        |
| area              | 省市区       | Cascader    | ✅   | 输出 provinceCode/cityCode/countyCode |
| format            | 项目业态     | Select      | ✅   | 1-风电, 2-光伏, 3-储能                |
| capacityTotal     | 项目总容量   | InputNumber | 条件 | 2位小数，addonAfter: MW，风电必填     |
| capacityWindPower | 风电容量     | InputNumber | 条件 | 2位小数，addonAfter: MW，>0           |
| capacityPv        | 光伏交流容量 | InputNumber | 条件 | 2位小数，addonAfter: MW，>0           |
| capacityPvDc      | 光伏直流容量 | InputNumber | -    | 2位小数，addonAfter: MW               |
| energyScale       | 储能规模     | InputNumber | 条件 | 2位小数，addonAfter: MW，储能必填     |
| storageCapacity   | 储能容量     | InputNumber | 条件 | 2位小数，addonAfter: MWh，储能必填    |
| subCode           | 分公司       | Select      | ✅   | 字典选择                              |
| regionCode        | 区域         | Select      | ✅   | 字典选择                              |
| developerCode     | 开发人员     | Select      | ✅   | 用户选择                              |
| obtainDate        | 获取日期     | DatePicker  | ✅   | -                                     |
| expireDate        | 失效日期     | DatePicker  | 条件 | longValid=true时非必填                |
| lockLevel         | 锁定级别     | Select      | ✅   | 字典选择                              |
| address           | 项目地址     | Input       | ✅   | -                                     |
| coverArea         | 用地面积     | InputNumber | -    | 2位小数                               |
| attachmentDTOList | 附件         | Upload      | ✅   | attachmentType: '1'                   |
| closeReason       | 放弃原因     | TextArea    | 条件 | giveUp类型必填                        |
| updateReason      | 变更原因     | TextArea    | ✅   | 变更时必填                            |

#### 海外业务字段
  
| 字段名            | 中文名       | 组件        | 必填 | 特殊逻辑                              |
| ----------------- | ------------ | ----------- | ---- | ------------------------------------- |
| countryCode       | 国家         | OverseasRegionCascader | ✅ | 海外特有，替代 area(Cascader)     |
| profitCenter      | 利润中心     | Input       | 条件 | 总部业财部(hwycsh)节点可编辑      |
| electricityPrice  | 电价         | ElectricityPriceInput | - | `@/components/common/ElectricityPriceInput` |
| sourceId          | 重提来源ID   | (内部)      | 条件 | 重提模式草稿保存时必须清空        |

#### 业态驱动规则
- 字典值口诀：1=风电 2=光伏 3=储能 4=风储 5=光储

| 业态           | 必填字段                     |  单位|
| -------------- | ---------------------------- |------|
| 风电(1) | capacityWindPower, machinePointWindPower |MW/个|
| 光伏(2) | capacityPv, capacityPvDc     |MW/MWp|
| 储能(3) | energyScale, storageCapacity |MW/MWh|
| 风储(4) | capacityWindPower, machinePointWindPower, energyScale, storageCapacity |MW/个/MW/MWh|
| 光储(5) | capacityPv, capacityPvDc, energyScale, storageCapacity |MW/MWp/MW/MWh|

### 4. 绝对禁止

- ❌ 使用 `render()` 函数
- ❌ 在 TSX 中使用 `this`
- ❌ 在 `defineComponent` 中写 `components` 配置
- ❌ 使用 `.claude/rules/global/check.md` 中「禁止」列表的组件

### 4.1 隐含规则（AI 容易犯错的地方）

| 规则 | 正确做法 | 错误做法 |
|------|----------|----------|
| Modal 显隐 | `open` prop | `visible` prop |
| **父子双向绑定** | `v-model:open={visible.value}` | `open={visible}` + `onClose` |
| TextArea | `import { Input } from 'ant-design-vue'` → `Input.TextArea` | `import { TextArea }` 独立导入 |
| Upload 导入 | `@/components/Upload/Upload.vue` | `@/components/Upload` |
| 只读附件展示 | `AttachmentFileList` 组件 | 自定义文本 `${count} 个附件` |
| org API 导入 | `@/api/system/org` | `@/api/myth-permission/v3/secOrg` |
| 搜索参数获取 | `form.getData()` 一次性获取 | `getForm().getFieldsValue()` 逐字段取值 |
| 审批页组件 | 需要 `ctx.expose` 暴露 `getData()`/`validate()` | 不暴露 |
| 列表查询 HTTP 方法 | `defHttp.post` + `data` | `defHttp.get` + `params` |
| 请求参数中的用户引用 | 只传 ID（`string`） | 传完整 `UserInfo` 对象 |
| API 前缀路径 | 从开发方案接口清单读取 | 猜测或编造路径 |
| index.tsx 布局 | `BasicTable` 的 `tableTitle` slot | `div` 包裹 + 独立按钮区 |

### 5. 强制规则（Skill 生成）

**禁止手动编写以下模块代码，必须通过 skill 生成：**
- 列表页 → `/scene-list`
- 表单页 → `/scene-form`
- 详情页 → `/scene-detail`
- 审批页 → `/scene-approval`

**违规处理**：代码不予合并

### 5-bis. 只读字段渲染规范（P0 强制）

> 完整决策矩阵参见：`.claude/skills/generator-dev-plan/templates/_shared/component-render-mode.md`

**铁律：组件类型不随 disabled 状态变化，只有 disabled prop 值变化。**

| 场景 | 必须使用 | 禁止使用 |
|------|---------|---------|
| 列表表格列 — 字典字段 | `DictLabel` | `DictSelect`（有下拉交互） |
| 列表表格列 — 数值字段 | `formThousands(val, {decimal:2})` | 裸数字 |
| 详情/只读 — 任意字段 | 原组件 + `disabled` | `<span>{v}</span>` |
| 详情/只读 — 附件 | `AttachmentFileList readonly` | 自定义文本 `${count}个附件` |
| 海外业务 — 区域选择 | `OverseasRegionCascader` | 国内 `Cascader` |
| 海外业务 — 用户选择 | `OSLovSelect` | 国内 `LovSelect` |

### 6. 目录结构规范（必须遵循）

> 所有新模块**必须遵循** `rules/global/directory-structure.md` 中定义的目录结构。

核心要点：
- `index.tsx`（渲染）+ `useIndex.ts`（逻辑）分离
- API 放 `api/` 目录（`index.ts` + `types.ts`）
- 组件用 PascalCase 目录，内含 `index.tsx` + hook + `style.module.less`
- 详情页用 Section 组件拆分，审批页位于 `office/` 下

### 7. 数字输入规范

**大额数字/金额/容量** 必须使用 `v-formThousands` 指令（千分位格式化 + 位数控制）。

**判断标准**：整数>6 位 | 需要千分位 | 严格位数控制

**快速示例**：
```tsx
const state = reactive({ unitCost: undefined });
<InputNumber
  value={value.unitCost}
  v-formThousands={[state, { intLength: 6, decimal: 4, key: 'unitCost' }]}
  onChange={v => { state.unitCost = v; }}
/>
```
**详细规范** → `rules/global/comp-storage.md`

---

## 工作流（按顺序执行）

| 步骤 | 操作 | 做什么 |
| ---- | ---- | ------ |
| 1    | 读本章「快速开始」 | 了解技术栈、组件、字段参考 |
| 2    | 识别场景 → 使用对应 Skill | `/scene-list`、`/scene-form`、`/scene-detail`、`/scene-approval`，生成的代码必须按「目录结构规范」调整不符合部分 |

> 基础规范（命名/API/TSX/样式/检查清单）已通过 `.claude/rules/global/` 自动加载，无需手动读取。

---

## 场景选择（我要开发...）

| 我要开发                   | 使用方式          |
| -------------------------- | ------------------- |
| 列表页（搜索+表格+分页）   | `/scene-list` Skill |
| 表单页（新增/编辑）        | `/scene-form` Skill |
| 详情页（只读展示）         | `/scene-detail` Skill |
| 审批页（只读+填写+操作）   | `/scene-approval` Skill |

---

## 问题排查（我遇到...）

| 问题             | 读这个文件           |
| ---------------- | -------------------- |
| 不确定用什么组件 | 本章「核心组件」表格 |
| 不确定字段怎么配 | 本章「常用字段」表格 |
| 模糊场景不确定   | 向用户确认           |

> 命名规范/TSX/API/样式/检查清单已通过 `.claude/rules/global/` 自动加载。

---

## 组件/模式速查

| 你要用       | 使用方式                |
| ------------ | ------------------- |
| 储能规模输入 | `.claude/rules/global/comp-storage.md` |
| 文件上传（所有附件场景） | `/pattern-upload` Skill |
| 多语言输入   | `.claude/skills/scene-form/references/form-map.md` 8.4节 |
| 分页选择器   | `.claude/skills/scene-form/references/form-map.md` 8.5节 |
| 物料分类选择 | `.claude/skills/scene-form/references/form-map.md` 8.6节 |
| 期间选择     | `.claude/skills/scene-form/references/form-map.md` 8.7节 |
| 项目选择弹窗 | `.claude/skills/scene-form/references/form-map.md` 8.8节 |
| 数值范围输入 | `.claude/skills/scene-form/references/form-map.md` 8.9节 |
| 双数字输入   | `.claude/skills/scene-form/references/form-map.md` 8.10节 |
| 模块标题     | `.claude/skills/scene-form/references/form-map.md` 8.12节 |
| 海外区域选择 | `OverseasRegionCascader`，替代 `Cascader` |
| 海外人员选择 | `OSLovSelect`，替代 `LovSelect` |
| 海外中英双语渲染 | `getChineseText()` / `getEnglishText()` from `@/views/overseas/shared/review/reviewItems` |

---

## 详细参考

- 按模块查看字段 → `.claude/skills/scene-form/references/form-map.md`
- 按字段查看组件 → `.claude/skills/scene-form/references/form-map2.md`
