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

- 泄漏扫描黑名单内置在 `scripts/sync_from_local.py` 的 `LEAK_PATTERNS`；扫描失败（退出码 2）禁止 push
- 新增 skill 时：在脚本 `COPY_PLAN` 加一行，跑同步
- 结构设计文档：`docs/spec/2026-09-30-skill-marketplace-design.md`
