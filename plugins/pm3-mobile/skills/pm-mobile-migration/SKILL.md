---
name: pm-mobile-migration
description: PM3.0 PC 端页面迁移到移动端 H5 的强制工作流。当用户要求"PC 转移动端"、"开发移动端审批页面"、"迁移 xx 页面到移动端"时使用。使用前必须先取得两个必需参数：<pc-vue-path>（PC 端页面 .vue 路径）与 <mobile-ref-path>（移动端参考页面 .vue 路径），缺失时先询问用户。核心纪律：先盘点组件、梳理审批流配置表、字段映射清单，然后才生成代码。
argument-hint: "<pc-vue-path> <mobile-ref-path>"
---

# PM 移动端迁移开发 Skill（强制工作流）

> 所有代码模板与组件真实签名见 [REFERENCE.md](./REFERENCE.md)。
> 本文件只规定"必须做什么、按什么顺序做"，不重复模板代码。

## 输入参数

> 标准入口：`/pm-migrate <pc-vue-path> <mobile-ref-path>` 命令（项目 `.claude/commands/pm-migrate.md`）。直接触发 skill 时参数约定相同。

| 参数 | 必需 | 说明 |
|---|---|---|
| `<pc-vue-path>` | ✓ | PC 端待迁移页面 .vue 文件路径（如 `pm3.0_frontend/src/views/office/todo/pro-init/index.vue`，审批弹窗通常在其 apply-modal 目录） |
| `<mobile-ref-path>` | ✓ | 移动端参考页面 .vue 路径（如 `src/views/office/todo/initiationApproval/index.vue`），作为 Phase 0 盘点与 Phase 3 风格对齐的基准 |

**未传入时的行为（与 /pm-migrate 命令一致）**：用 AskUserQuestion 依次询问：
1. "请提供需要迁移的 PC 端页面路径"
2. "请提供移动端参考页面路径"

禁止凭模块名猜测 PC 端文件位置；用户只给模块名时，先在 PC 仓库搜索定位候选文件，列给用户确认后才进入 Phase 1。

## 铁律

1. **每个 Phase 有硬性产出物，缺产出不得进入下一 Phase。**
2. **PC 端代码必须读真实文件**（PC 仓库根目录由调用方工作目录或输入参数确定，页面文件由输入参数 `<pc-vue-path>` 指定），不得凭记忆或描述推断字段与流程。
3. **移动端只显示不编辑**：业务表单字段全部只读展示；审批操作（同意/驳回/提交/抄送/已阅）走标准审批外壳——优先公共容器 `ApprovalContainer`（REFERENCE.md §1.1），容器不可用时才手写外壳（§1.3）。
4. **禁止凭想象写 API**：字典、上传、审批提交等一律使用 REFERENCE.md 中的项目真实签名。
5. **所有用户可见文案走 i18n**：`$t("key", "中文兜底")`，import 自 `@/locales`。

## 背景：为什么有这个流程

立项审批模块（initiationApproval）首次迁移时因跳过流程梳理与组件盘点，交付后经历了 7 次 fix（补评审模块、补审批结论、补节点拦截、字段对齐）。本工作流的 Phase 0/1/2 就是为了在生成前堵住这些缺口。

---

## Phase 0：组件盘点

**做什么**：在移动端项目（`pm3.0_frontend_h5`）中盘点本次迁移可复用的既有组件与 hook。

**怎么盘**：
```bash
# 待办审批通用组件（优先复用，不要重复造轮子）
ls src/views/office/todo/components/
ls src/components/
# 审批操作 hook（同意/驳回/抄送/已阅一站式）
grep -n "export function useTodoActions" src/views/office/todo/*/hooks/index.ts
```

**产出物**：`组件清单表`，至少包含：
| 组件/hook | 路径 | 关键 props/签名 | 本次是否使用 |
|---|---|---|---|

已知必盘项（签名详见 REFERENCE.md §5）：**`ApprovalContainer` / `ApprovalActionBar`（审批公共容器，存在则首选，见 REFERENCE.md §1.1）**、`ApproveRecordPopup`、`userSelectPopup`、`TitleBar`、`FileCard`、`Upload`、`Select`、`useTodoActions`、`useDict`、`NavBar`。

> ApprovalContainer 自分支 `feat/mobile-approval-container` 起维护，盘点时先确认已在当前分支：
> ```bash
> ls src/views/office/todo/components/ApprovalContainer/
> ```
> 不存在（未合入当前工作基线）则回退 REFERENCE.md §1.3 手写外壳模板，并提示用户。

---

## Phase 1：审批流梳理（最高优先级）

**做什么**：读 PC 端真实代码，梳理审批流程配置。PC 端审批组件通常在 `src/views/office/todo/components/apply-modal/` 下，从中提取节点类型、权限、模式。

**产出物：四张表，缺一不得进入 Phase 2。**

### 表① 节点清单表
PC 端全部 operationType + 中文名 + 阶段分组：
| operationType | 中文名 | 阶段(Phase1/2/3/4) | 移动端是否支持操作 |
|---|---|---|---|

> 移动端不支持的节点（需填表单/上传/编辑类操作）列入"PC 端专属"，进入表④。

### 表② 权限矩阵表
`getOperationRole` 返回的 templatePermission × 按钮可见性：
| templatePermission | 提交 | 同意 | 驳回 | 抄送 | 已阅 |
|---|---|---|---|---|---|
已知值：`submit_save`/`submit_save_close`/`apply_system`→提交；`approve_reject`→同意+驳回；`approve`→同意；`card_approve_make_copy`→已阅。新值须从 PC 端代码确认。

### 表③ 模式映射表
每个节点在移动端详情区的展示模式：
| operationType | 评审模式(review/reply/readonly/none) | 额外展示区块(经济信息/评分/评审列表) |
|---|---|---|

### 表④ PC 端专属操作表
| operationType | PC 端独占原因 | 移动端拦截方式 |
|---|---|---|

> 拦截方式统一：`van-dialog` 提示"请到电脑端完成操作"，确认后 `router.back()`，且**不加载详情表单**（`v-if="loaded"` 控制）。

---

## Phase 2：字段映射

**做什么**：从 PC 端表单/详情页逐字段提取，建立对照清单。

**产出物**：`字段对照清单`：
| PC 字段名 | 中文标签 | 数据来源字段 | 类型(文本/字典/日期/金额/附件) | 字典 code | 移动端渲染组件 | 条件渲染规则 |
|---|---|---|---|---|---|---|

要点：
- 字典字段必须查出真实字典 code（如 `OVERSEA_PROJ_BIZ_TYPE`），从 PC 端代码或接口文档确认，禁止猜
- 附件字段确认接口真实字段名（`attachmentList`/`attachmentDTOList`/`attachments` 可能并存，需兼容）
- 条件渲染（如"业态细分仅风电/光伏显示"）必须在此表标注，不留到写码时才发现

---

## Phase 3：代码生成

**目录结构**（以 `xxxApproval` 为例）：
```
src/views/office/todo/xxxApproval/
├── list.vue              # 首选 ApprovalContainer 接入（REFERENCE.md §1.1）；容器不可用时才手写外壳（§1.3）
├── form.vue              # 详情表单组装（只读 Section 组合）
├── config.ts             # 节点配置：Phase1 四张表的数据（禁止内联 list.vue）
├── types.ts              # 接口类型定义
├── enums/index.ts        # 枚举
├── hooks/
│   ├── useDetail.ts      # 详情加载
│   └── useXxxLabels.ts   # 字典/区域等翻译 hook（如有）
└── components/
    ├── XxxSection/index.vue   # 每个业务区块一个 Section 组件
    └── ...
```

**纪律**：
- 节点清单/权限/模式数据全部放 `config.ts`，list.vue 只做消费——禁止 700 行内联配置
- Section 组件只接收 `detail` 等 props，内部自行做字典翻译与空值处理
- 路由注册：`src/views/office/todo/index.vue` 的映射配置中加入新模块
- API 定义放 `src/api/` 对应模块，类型与 PC 端接口实际响应对齐

模板按需查 REFERENCE.md：审批外壳 §1、节点配置 §2、字段渲染 §3、附件 §4、组件签名 §5、通用区块 §6。

---

## Phase 4：强制自检

生成后逐项核对，全部通过才算完成：

**流程核对（对照 Phase 1 四张表）**
- [ ] 每个 operationType 的移动端行为与表①③一致（支持操作 or 拦截）
- [ ] 每种 templatePermission 的按钮可见性与表②一致
- [ ] PC 专属节点：弹窗拦截 + 不加载表单

**字段核对（对照 Phase 2 清单）**
- [ ] 清单逐行打勾：无遗漏字段、标签与 PC 一致、顺序一致
- [ ] 字典字段显示 label 而非 code，字典未加载时回退显示原始值
- [ ] 空值显示 `-`（项目惯例），不出现 `undefined`/`null`/`[object Object]`
- [ ] 附件：文件名完整显示（超长省略）、disabled 态无删除按钮、可预览
- [ ] 条件渲染字段按清单规则显隐

**工程核对**
- [ ] `pnpm type-check` 通过
- [ ] `pnpm lint` 通过
- [ ] 所有文案走 `$t()`
- [ ] 节点配置在 config.ts 中，list.vue 无内联大对象

**运行核对**（浏览器移动端模拟）
- [ ] 详情各区块正常渲染，接口报错不白屏
- [ ] 审批提交/驳回全流程走通（测试环境）

---

## Phase 5：知识沉淀

会话结束前：
- 本次盘点发现的新通用组件/新字典 code/新 templatePermission 值 → 回写 REFERENCE.md §5
- 踩坑经验（接口字段名不一致、字典 code 错误等）→ 追加到 REFERENCE.md §7 常见错误
- 按 gbrain 规则同步：`rules/comp-{name}`、`experiences/{module}-{issue}`

---

## 常见错误速查（历史教训，生成前先读）

| 错误 | 后果 | 预防 |
|---|---|---|
| 跳过 Phase 1，只迁移"字段展示" | 漏评审/变更/评分整块业务（立项模块教训） | 四张表缺一不得写码 |
| useDict 签名写错 `useDict(dictType)` | 编译失败，字典全不显示 | 用真实签名 `useDict({ default: CODE })` → `dictMap` |
| 用不存在的组件（如 MobileFileUpload） | 运行时报错 | 先 Phase 0 盘点，只用清单内组件 |
| 容器可用却重复手写审批外壳 | 每模块 400-700 行重复按钮/拦截/提交代码，改一处漏一处 | 优先 ApprovalContainer（REFERENCE.md §1.1），手写仅作后备 |
| 字段渲染用 van-cell 而非项目惯例 | 风格不统一，返工 | 用 `van-field readonly input-align="right"` |
| 节点配置内联在 list.vue | 单文件 700+ 行，难维护 | config.ts 独立 |
| 硬编码中文不走 i18n | 国际化缺失 | `$t(key, fallback)` 全覆盖 |

## 版本历史

- v2.1.0 (2026-09-09): 审批外壳升级为两级方案——首选 `ApprovalContainer` 公共容器（Phase 0 盘点、铁律 3、Phase 3 目录结构、常见错误速查同步更新），手写外壳降为后备。依据：分支 `feat/mobile-approval-container` 组件化审批外壳落地。
- v2.0.0 (2026-09-09): 结构化重构。强制六 Phase 工作流 + 四张审批流表；模板与项目真实 API 对齐（useDict/FileCard/Upload/useTodoActions/i18n）；新增审批外壳标准模板与 config.ts 规范。依据：立项审批模块 7 次 fix 的根因分析。
- v1.0.0 (2026-04-30): 初始版本，PC 到移动端迁移规范。
