# PM3.0 Claude Code Plugin Marketplace

PM3.0 系列项目的 Claude Code 资产商店：PC 前端生成器套件、移动端迁移工作流、通用 bug 修复编排。

## 入项（新项目一次性配置）

在项目根目录的 Claude Code 会话中执行：

```bash
# 1. 添加商店
/plugin marketplace add isoftstone-AI/PM3.0

# 2. 按项目类型安装
/plugin install pm3-frontend@PM3.0    # PC 前端项目
/plugin install pm3-mobile@PM3.0      # 移动端项目
/plugin install pm3-common@PM3.0      # 通用 bug 修复编排
```

### PC 前端项目：项目规范落盘

plugin 提供 skills；项目级规范（CLAUDE.md + rules）需从 plugin 缓存复制到项目：

```bash
REPO=$(git rev-parse --show-toplevel)
CACHE=$(ls -d ~/.claude/plugins/cache/*/pm3-frontend/*/ 2>/dev/null | head -1)
# ↑ 若为空，用实际安装提示给出的缓存路径替换
cp "$CACHE/templates/CLAUDE.md" "$REPO/CLAUDE.md"
mkdir -p "$REPO/.claude/rules"
cp -r "$CACHE/templates/rules/"* "$REPO/.claude/rules/"
```

> 注：CLAUDE.md 中形如 `.claude/skills/scene-form/references/form-map.md` 的路径引用，在入项项目中对应 plugin 缓存内的 skill 文件（skill 本体已随 plugin 自动加载，`/scene-form` 等命令可直接使用）；需要查阅参考文档时到插件缓存目录读取，或在项目内建软链。

落盘后可用的主要命令：`/scene-list` `/scene-form` `/scene-detail` `/scene-approval` `/pattern-upload` `/generate-prd-guide` `/generator-dev-plan` `/generate-api` `/workflow-agent`（或 `/design-plan` `/dev-plan` `/api-gen`）。

## 核心内容介绍

### 三大生成 skill（pm3-frontend）

构成链路：**设计方案 → 开发方案 → 页面代码 / 接口层**。

#### `generate-prd-guide` — 设计方案生成（`/generate-prd-guide`，别名 `/design-plan`）

根据 PRD + 设计图文档（yaml/md/html）自动生成前端开发引导文档。v2 架构为设计图驱动：模块级生成、主索引 + 多子文件输出、字段级 PRD 锚点与 API 映射（含 TypeScript 类型）、缝隙检测清单、mermaid 页面关系图。目标是开发者拿到文档后不需要回头看 PRD。

调用方式（`参数名=value` 空格分隔，参数缺失时交互式询问）：

```
/generate-prd-guide prdPath=@prd.md designPath=@design.yaml moduleName=开工管理 version=v1.0 outputDir=@output
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `prdPath` | ✅ | PRD 文档路径 |
| `designPath` | ✅ | 设计图文档路径（.yaml/.md/.html） |
| `moduleName` | ✅ | 模块名称（如：开工管理） |
| `version` | ✅ | 版本号 |
| `outputDir` | ✅ | 输出目录 |
| `apiDocPath` | ❌ | API 设计文档路径，用于生成接口字段映射 |

#### `generator-dev-plan` — 开发方案生成（`/generator-dev-plan`，别名 `/dev-plan`）

根据 PRD、字段数据和设计图生成**字段级**开发方案文档——每个字段都有组件、属性、校验规则，开发者可按字段直接写代码。状态机执行协议（主会话编排 + subagent 隔离生成 + 黑板 state）解决多模块生成的上下文溢出；支持 `pageType=list|form|approval|detail|modal` 五种页面类型。产出的方案是 `/scene-*` skill 的**输入参数**（只提供字段属性与业务逻辑，不生成代码示例，代码结构由 scene skill 模板决定）。

调用方式（`key="value"` 空格分隔）。**最简用法**只传 3 个必填参数，其余信息从设计方案文档自动提取，提取不足时交互式询问：

```
/generator-dev-plan designDocPath="设计管理/设计方案v2/设备提资.md" outputPath="设备提资模块详情页 v2/01-列表页-M1-筛选查询区.md" apiDocSource=apifox
```

必填参数：

| 参数 | 说明 | 示例 |
|------|------|------|
| `designDocPath` | 设计方案文档路径（优先读取"特别强调"章节） | `设计管理/设计方案v2/设备提资.md` |
| `outputPath` | 输出文件路径 | `设备提资模块详情页 v2/01-列表页-M1-筛选查询区.md` |
| `apiDocSource` | API 文档来源 | `apifox` 或 `md:设计管理/接口文档/设备提资接口.md` |

可选参数（显式传递时优先级高于设计方案自动提取）：

| 参数 | 说明 | 示例 |
|------|------|------|
| `pageType` | 页面类型：`list` / `form` / `approval` / `detail` / `modal` | `list` |
| `pageName` | 页面中文名 | 设备提资列表页 |
| `pagePath` | 页面路径（kebab-case） | `design-manage/equipment-submission` |
| `moduleCode` | 模块编码 | `M1` / `M2` / `M3` / `M4` |
| `moduleName` | 模块中文名 | 筛选查询区 |
| `fieldData` | 字段数据 JSON（格式见下） | `{"fields":[...]}` |
| `refModule` | 参考模块路径 | `special-review` |
| `prdPath` | PRD 路径（供 scene-* 生成代码时读取） | `设计管理/开发方案/01-列表页-M1-筛选查询区.md` |
| `pages` | 页面汇总信息 JSON（生成索引用） | JSON |
| `mermaidDiagram` | Mermaid 页面关系图定义 | `flowchart TD ...` |
| `designSection` | 设计图章节引用 | `3.2.1 表单布局样式` |
| `styleConfig` | 样式配置 JSON（间距/对齐/宽度） | `{"layout":"2列","gutter":"16px"}` |
| `logicReference` | 逻辑对应的设计文档章节引用 | `4.3.2 字段交互规则` |
| `skillDocPath` | 对应 Skill 的使用文档路径 | `开发规范/Skill使用指南/scene-form.md` |
| `projectRulePath` | 项目规范文档路径 | `开发规范/PM3.0前端开发规范.md` |
| `ruleSection` | 项目规范对应章节 | `5.2 表单开发规范` |

`fieldData` 格式：

```json
{
  "fields": [
    { "name": "projectName", "label": "项目名称", "component": "Input", "required": false }
  ]
}
```

#### `generate-api` — API 代码生成（`/generate-api`，别名 `/api-gen`）

根据 Apifox MCP 或本地 MD/YAML/JSON 接口文档，生成符合项目规范的 `api/types.ts` + `api/index.ts`。

调用方式（位置参数，也支持自然语言描述需求由 skill 从上下文推断）：

```
/generate-api apifox all views/eng-manage/start-apply/api
/generate-api md:docs/设备提资接口.md 预立项 views/design-manage/equipment-submission/api
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `source` | ✅ | 接口文档来源：`apifox`（经 Apifox MCP）或 `md:文件路径` |
| `scope` | ❌ | 生成范围，默认 `all`；可传接口关键词，按路径 / summary / tags 三级匹配，生成前展示清单确认 |
| `target` | ✅ | 输出目录，如 `views/eng-manage/xxx/api`；只给模块名时自动推断为 `views/<业务域>/<kebab-case>/api` |

### workflow-agent — 工作流代理（pm3-frontend）

三大生成场景的统一智能入口：触发词检测 → 路由场景 → 自动检测目标 skill 是否存在（不存在时调用 meta-skill 创建）→ 引导补齐参数 → 调用目标 skill 执行 → 记录结构化日志。

| 调用方式 | 路由目标 |
|----------|---------|
| `/design-plan [参数...]` | 设计方案 → `generate-prd-guide` |
| `/dev-plan [参数...]` | 开发方案 → `generator-dev-plan` |
| `/api-gen [参数...]` | API 生成 → `generate-api` |

参数原样透传给目标 skill；也可直接自然语言触发（如"帮我生成开发方案"、"根据接口文档生成 API 代码"），无需记忆完整命令与参数。

### 支撑 skills（pm3-frontend）

| skill | 调用方式与用途 |
|-------|------|
| `scene-list` / `scene-form` / `scene-detail` / `scene-approval` | 页面代码生成器（列表/表单/详情/审批）。自然语言触发（"开发列表页"、"生成表单页"）或 `/scene-list` 等命令；输入 PRD + API 文档 + 设计稿，基于上线代码模板生成完整页面代码（`index.tsx` + `useIndex` + `api/` + Section 组件等）。scene-approval 前提：业务的查看/编辑组件已存在。消费 generator-dev-plan 的开发方案作为输入 |
| `pattern-upload` | 需求涉及附件上传/下载/预览时触发；统一使用 Upload 组件 + `onlyShowFileList` 控制编辑/只读态，禁止混用多个上传组件 |
| `skill-generator` / `create-develop-plan-skill` | meta-skill：为新项目从零生成配套的设计方案/开发方案生成器 |
| `templates/`（CLAUDE.md + rules） | PM3.0 前端项目规范，入项时落盘到项目根目录。CLAUDE.md 中登录账密为占位符（`<填写账号>` 等），落盘后自行填写，未填写前 Claude 会跳过登录节 |

### 其他 plugin

- **pm3-mobile · `pm-mobile-migration`**（`/pm-migrate <pc-vue-path> <mobile-ref-path>`）：PC 页面迁移移动端 H5 的强制工作流——必须读真实 PC 源文件（禁止凭记忆推断字段与流程），对照移动端参考页迁移。
- **pm3-common · `isoftstone-debug-recovery`**：Bug 修复编排——根因分析 → 方案经用户确认后修复 → code review 审查准确性与范围；自动判定前端/后端/双端问题，双端问题派发前后端独立 subagent 串行执行（接口变更先后端再前端）。输入：问题描述（必填）+ 前端/后端代码路径（选填，两端都提供即按双端处理）。依赖 `superpowers` 与 `agent-skills` plugin。

## 前置依赖

| plugin / 功能 | 依赖 | 说明 |
|---------------|------|------|
| pm3-common | `superpowers`、`agent-skills` plugin | isoftstone-debug-recovery 引用其子工作流，请先安装这两个公开 plugin |
| generate-api、generator-dev-plan（apifox 模式） | Apifox MCP | 项目需自行配置 Apifox MCP；仅用 `md:` 模式可不配 |
| pm3-mobile | 移动端仓库 `pm3.0_frontend_h5` | 执行迁移时需在场 |
| generator-dev-plan 模板、components.json | PM3.0 组件库 `@/components/*` | 预期耦合：本商店目标受众即 PM3.0 系项目 |

## 更新

已入项项目中执行 `/plugin update` 拉取商店最新。

## 维护（商店维护者）

单一事实源：个人工作区 `~/work/个人积累/ai/.claude`（含 `ai/CLAUDE.md`）与 `~/.claude/skills`。

```bash
cd <本仓库>
python3 scripts/sync_from_local.py   # 全量重建 + 内容清洗 + 泄漏扫描
git diff                              # 人工复核（重点：清洗结果与剔除项）
git add plugins && git commit && git push
```

- 泄漏扫描黑名单在 `scripts/leak_patterns.local`（git 忽略，不入库；从 `leak_patterns.example` 复制后填入真实值），缺失时直接报错拒绝执行；扫描范围含 scripts/ 全仓，扫描失败（退出码 2）禁止 push
- push 前执行 `claude plugin validate plugins/pm3-frontend`（另外两个同理）校验 skill frontmatter（如 argument-hint 以 `[` 开头必须加引号，否则 YAML 解析失败、元数据静默丢失）
- 新增 skill 时：在脚本 `COPY_PLAN` 加一行，跑同步
- 结构设计文档：`docs/spec/2026-09-30-skill-marketplace-design.md`
