# PM3.0 Skill 商店发布设计

> 日期：2026-09-30
> 目标仓库：https://github.com/isoftstone-AI/PM3.0.git（已确认存在且为空仓库）
> 源目录：`REDACTED-PATH/work/个人积累/ai/.claude`（个人 skill/agent 工作区，gitee 私有仓库）
> 源 CLAUDE.md：`REDACTED-PATH/work/个人积累/ai/CLAUDE.md`

---

## 1. 背景与目标

PM3.0 前端项目沉淀了一套 AI 辅助开发资产（设计方案生成、开发方案生成、API 代码生成、页面场景生成器、工作流代理、项目规范等），当前通过符号链接（`pm3.0_frontend/.claude -> ~/work/个人积累/ai/.claude`）供单一项目使用。

目标：以 **Claude Code Plugin Marketplace** 形态发布到 `isoftstone-AI/PM3.0`，后续项目两条命令即可入项使用，`/plugin update` 跟进更新。

## 2. 决策记录

| # | 决策点 | 结论 |
|---|--------|------|
| D1 | 提取范围 | **完整依赖闭包**：3 个生成 skill + workflow-agent + CLAUDE.md + rules/global + scene-* / pattern-upload skills |
| D2 | 仓库形态 | **Plugin Marketplace**（官方商店机制，`.claude-plugin/marketplace.json`） |
| D3 | 敏感信息 | **彻底剥离**：账密、内网 IP、个人 MCP/skill 引用全部删除 |
| D4 | plugin 拆分 | **按项目类型拆 3 个**：pm3-frontend / pm3-mobile / pm3-common |
| D5 | 同步管道 | **导出同步脚本**：单一事实源仍是个人 `ai/.claude`，脚本负责清洗+重建+泄漏扫描 |
| D6 | 新增内容 | 补充 `pm-mobile-migration`（移动端迁移）、`isoftstone-debug-recovery`（bug 分析）两个全局 skill |
| D7 | workflow-agent 形态 | 作为 **skill** 发布（它是 SKILL.md 目录形态，非单文件 agent），放 `skills/` 不放 `agents/` |

清单笔误澄清：原需求"API 代码生成 → generator-dev-plan"实为 `generate-api`（workflow-agent 路由表佐证）。

## 3. 仓库总体结构

```
PM3.0/  (github.com/isoftstone-AI/PM3.0)
├── .claude-plugin/
│   └── marketplace.json              # 商店清单：注册 3 个 plugin
├── plugins/
│   ├── pm3-frontend/                 # PC 前端项目
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/
│   │   │   ├── generate-prd-guide/   # 设计方案生成（清洗后）
│   │   │   ├── generator-dev-plan/   # 开发方案生成（清洗后）
│   │   │   ├── generate-api/         # API 代码生成
│   │   │   ├── workflow-agent/       # 工作流代理（skill 形态）
│   │   │   ├── skill-generator/      # 设计方案 meta-skill（workflow-agent Step 3 依赖）
│   │   │   ├── create-develop-plan-skill/  # 开发方案 meta-skill（同上）
│   │   │   ├── scene-list/  scene-form/  scene-detail/  scene-approval/
│   │   │   └── pattern-upload/       # scene-form 内部引用（form-map.md:479）
│   │   └── templates/
│   │       ├── CLAUDE.md             # 清洗后的项目规范
│   │       └── rules/global/         # 9 个规则文件（api/check/comp-storage/css/
│   │                                 # directory-structure/naming/override/tsx/uncertain）
│   ├── pm3-mobile/
│   │   ├── .claude-plugin/plugin.json
│   │   ├── skills/pm-mobile-migration/
│   │   └── commands/pm-migrate.md    # 新建 wrapper（SKILL.md 声明的入口，原文件缺失）
│   └── pm3-common/
│       ├── .claude-plugin/plugin.json
│       └── skills/isoftstone-debug-recovery/
├── scripts/
│   └── sync-from-local.py            # 同步 + 清洗 + 泄漏扫描
└── README.md                         # 商店说明 + 入项指引 + 依赖声明
```

### 结构决策理由

- **workflow-agent 放 skills/**：Claude Code 的 agent 仅支持单 .md 文件；workflow-agent 是带 SKILL.md 的目录，作为 skill 发布功能不变。
- **meta-skill 一并发布**：workflow-agent Step 3 在目标 skill 缺失时调用 `skill-generator` / `create-develop-plan-skill`，不带上则该功能断链。
- **删除 workflow-agent 内嵌 `skills/` 副本**：其内含 generate-api 等副本，与顶层版本存在分叉风险，统一消费顶层发布版。
- **CLAUDE.md + rules 以 templates/ 附带**：plugin 机制不支持项目级 `rules/` 自动加载，入项时复制到项目 `.claude/rules/global/`（README 提供复制命令）。
- **不带的内容**：`code-review`、`i18n`、`filter-config`、`ma-zhenxiao-perspective`、`pattern-component` —— 已 grep 验证不在 CLAUDE.md / scene-* / workflow-agent 的依赖闭包内。

## 4. 清洗规则（sync 脚本内置）

### 4.1 敏感信息剥离（内容编辑）

| 位置 | 处理 |
|------|------|
| CLAUDE.md「登录禅道」「登录系统测试」两节 | 整节删除（账密、内网 IP `REDACTED-IP152.128`、playwright 引用） |
| CLAUDE.md 工作流规则中 gbrain 引用 | 删除该行（个人私有 MCP，入项项目不存在） |
| CLAUDE.md 中 graphify 引用（`~/.claude/skills/graphify`） | 删除该行（个人全局 skill） |
| pm-mobile-migration SKILL.md 铁律 2 硬编码 `REDACTED-PATH/work/pm/pm3.0_frontend` | 改写为"PC 仓库根目录（由调用方工作目录或输入参数确定）" |

### 4.2 开发产物剔除（不复制）

| 位置 | 排除项 |
|------|--------|
| `generate-prd-guide/` | `temp/`、`OPTIMIZATION-PLAN.md`、`OPTIMIZATION-REPORT.md`、`REVISION-SUMMARY.md`（保留 SKILL.md、agents/、references/、evals/、CHANGELOG.md） |
| `generator-dev-plan/` | `tasks/`（plan.md/todo.md 过程记录） |
| `workflow-agent/` | `logs/`、内嵌 `skills/` 副本目录 |
| 全部 | `.DS_Store` |

### 4.3 泄漏扫描（最后一道闸）

脚本对**产出文件**逐一 grep 黑名单，命中即**报错终止**（非静默跳过）：

```
REDACTED、REDACTED、REDACTED、REDACTED、REDACTED-IP、REDACTED-PATH
```

规则固化在脚本中 —— CLAUDE.md 未来更新可能重新带入凭据，只有脚本化才能持续拦截。

### 4.4 外部依赖声明（README 显式列出）

| 依赖 | 使用方 | 入项要求 |
|------|--------|---------|
| Apifox MCP | generate-api、generator-dev-plan（apifox 模式） | 项目自行配置 Apifox MCP；仅 md 模式可不配 |
| superpowers plugin | isoftstone-debug-recovery（`requesting-code-review`） | 先安装 superpowers |
| agent-skills plugin | isoftstone-debug-recovery（`debugging-and-error-recovery`） | 先安装 agent-skills |
| 移动端项目 `pm3.0_frontend_h5` | pm-mobile-migration | 使用时需要移动端仓库在场 |
| PM3.0 组件库 `@/components/*` | generator-dev-plan 的 components.json/模板 | 预期耦合：商店目标受众即 PM3.0 系项目 |

## 5. 入项使用方式（README 内容）

```bash
# 1. 添加商店（新项目一次性）
/plugin marketplace add isoftstone-AI/PM3.0

# 2. 按项目类型安装
/plugin install pm3-frontend@PM3.0    # PC 前端项目
/plugin install pm3-mobile@PM3.0      # 移动端项目
/plugin install pm3-common@PM3.0      # 通用：bug 分析编排（需先装 superpowers + agent-skills）

# 3. 项目规范落盘（仅 PC 前端，从 plugin 缓存复制）
cp ~/.claude/plugins/cache/PM3.0/plugins/pm3-frontend/templates/CLAUDE.md ./CLAUDE.md
mkdir -p .claude/rules && cp -r ~/.claude/plugins/cache/PM3.0/plugins/pm3-frontend/templates/rules/* .claude/rules/
```

安装后即可使用 `/scene-list`、`/dev-plan`、`/api-gen`、`/pm-migrate` 等；`/plugin update` 拉取商店更新。

> 注：plugin 缓存实际路径以安装后 Claude Code 提示为准（可能含 marketplace owner 前缀），README 中以 `$(claude plugin path pm3-frontend)` 类指引或实测路径为准，实现时确认。

## 6. 同步维护流程

单一事实源仍是个人 `ai/.claude`：

```
个人目录开发 → python3 scripts/sync-from-local.py（增量重建+清洗+扫描）
  → git diff 复核 → commit + push → 入项项目 /plugin update 生效
```

脚本职责：
1. 按白名单从 `ai/.claude` 复制内容到 `plugins/` 对应位置（全量重建：先清空目标目录再复制，避免源端已删除文件残留）
2. 应用 4.1 内容清洗（对已知位置做确定性替换/删节）
3. 应用 4.2 排除清单
4. 执行 4.3 泄漏扫描，命中即退出码非零
5. 输出变更摘要（新增/更新/剔除文件清单）

## 7. 验证方式（完成的判据）

1. **泄漏扫描有效性**：构造一个含账密的临时文件通过脚本处理，验证拦截报错
2. **本地安装测试**：`/plugin marketplace add <本地仓库路径>`，三个 plugin 逐一 install，确认 skills 出现在列表、`/pm-migrate` 命令可用
3. **入项模拟**：临时目录建假项目 → 装插件 + 复制模板 → 触发 `/scene-list` 验证 skill 加载与执行
4. **清洗比对**：diff 确认发布的 CLAUDE.md 无账密/gbrain/graphify 残留，pm-mobile-migration 无本机绝对路径

## 8. 风险与注意事项

| 风险 | 缓解 |
|------|------|
| 凭据进入 git 历史不可撤销 | 首次 push 前必须跑通泄漏扫描；扫描失败绝不 push |
| 本机已装同名 skill（generate-api 等通过 symlink 挂载） | 本机测试安装时可能出现 skill 重名遮蔽，属预期；入项项目无此问题（README 注明） |
| marketplace.json / plugin.json schema 细节（字段名、缓存路径） | 实现时以 Claude Code 官方文档为准，先本地 add 验证再 push |
| 个人目录后续演进与商店脱节 | D5 同步流程写入 README 维护章节，约定每次个人目录大改后跑同步 |
| pm-migrate 命令为新建 wrapper | 实现时按 pm-mobile-migration SKILL.md 的参数约定（`<pc-vue-path> <mobile-ref-path>`）编写，保持行为一致 |

## 9. 范围外（明确不做）

- 不迁移 `code-review`、`i18n`、`filter-config`、`ma-zhenxiao-perspective`、`pattern-component`
- 不处理 gitee 个人仓库（ai.git）本身的任何变更
- 不修改现有 `pm3.0_frontend/.claude` 符号链接（本机继续用个人目录）
- 不编写自动化 CI（同步由手动触发脚本完成，YAGNI）
