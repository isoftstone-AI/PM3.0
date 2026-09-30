# CLAUDE.md 数据提取规则

> 本文件定义如何从 CLAUDE.md / AGENTS.md 中提取结构化数据，供生成 skill 使用。

## 提取流程

```
CLAUDE.md 原文
    ↓
1. 章节定位（正则匹配标题）
    ↓
2. 内容提取（按章节类型选择提取策略）
    ↓
3. 结构化转换（表格→JSON / 列表→数组）
    ↓
4. 数据清洗（去空格、统一格式）
    ↓
提取结果对象
```

---

## 1. 技术栈提取

**定位方式**：查找包含"技术栈"关键词的章节标题

**提取策略**：从列表项中提取 key-value 对

**输入示例**：
```markdown
### 1. 技术栈
- **框架**：Vue 3
- **语言**：TypeScript
- **UI 库**：Ant Design Vue 4
- **构建工具**：Vite
- **样式方案**：Tailwind CSS + CSS Module + Less
```

**输出格式**：
```json
{
  "framework": "Vue 3",
  "language": "TypeScript",
  "uiLib": "Ant Design Vue 4",
  "buildTool": "Vite",
  "styleScheme": "Tailwind CSS + CSS Module + Less"
}
```

**提取规则**：
- 匹配 `**{key}**：{value}` 或 `- {key}：{value}` 格式
- key 标准化映射：`框架`→`framework`, `语言`→`language`, `UI库`→`uiLib`, `构建工具`→`buildTool`
- 如果用 `>` 引用块格式（如 `> 技术栈：Vue 3 + TypeScript`），按 `+` 分割提取

---

## 2. 组件库提取

**定位方式**：查找包含"组件"关键词的章节标题

**提取策略**：解析 Markdown 表格

**输入示例**：
```markdown
| 组件 | 导入路径 | 用途 |
|------|---------|------|
| BasicTable | `@/components/BasicTable` | 表格（强制使用，禁止直接用 a-table） |
| DictSelect | `@/components/DictSelect` | 字典选择 |
```

**输出格式**：
```json
[
  {
    "name": "BasicTable",
    "import": "@/components/BasicTable",
    "usage": "表格（强制使用，禁止直接用 a-table）"
  },
  {
    "name": "DictSelect",
    "import": "@/components/DictSelect",
    "usage": "字典选择"
  }
]
```

**提取规则**：
- 跳过表头行（含 `---` 的行）
- 跳过 `useTable` 等 hook 条目（非组件）
- 导入路径去除反引号
- 用途列可能包含括号注释，保留完整内容

**分类规则**（按 claude-md-schema.json 中的 component_classification）：
- 根据组件名关键词匹配分类
- 未匹配的归入 `special` 类

---

## 3. 字段参考提取

**定位方式**：查找包含"字段"关键词的章节标题

**提取策略**：解析 Markdown 表格

**输入示例**：
```markdown
| 字段名 | 中文名 | 组件 | 必填 | 特殊逻辑 |
|--------|--------|------|------|---------|
| proName | 项目名称 | Input | ✅ | max: 128 |
| format | 项目业态 | Select | ✅ | 1-风电, 2-光伏, 3-储能 |
```

**输出格式**：
```json
[
  {
    "name": "proName",
    "label": "项目名称",
    "component": "Input",
    "required": true,
    "specialLogic": "max: 128"
  }
]
```

**提取规则**：
- `必填` 列：`✅` → `true`，其他 → `false`
- `条件` 值 → `required: "conditional"`
- 特殊逻辑列保留原文

---

## 4. 隐含规则提取

**定位方式**：查找包含"隐含规则"或"正确做法"关键词的章节

**提取策略**：解析表格或列表

**输入示例**：
```markdown
| 规则 | 正确做法 | 错误做法 |
|------|---------|---------|
| Modal 显隐 | `open` prop | `visible` prop |
| TextArea | `import { Input }` → `Input.TextArea` | `import { TextArea }` 独立导入 |
```

**输出格式**：
```json
[
  {
    "rule": "Modal 显隐",
    "correct": "open prop",
    "wrong": "visible prop"
  }
]
```

---

## 5. 目录结构提取

**定位方式**：查找包含"目录结构"关键词的章节

**提取策略**：从描述文本中提取模式（框架无关）

**输入示例（前端项目）**：
```markdown
### 6. 目录结构规范
- `index.tsx`（渲染）+ `useIndex.ts`（逻辑）分离
- API 放 `api/` 目录（`index.ts` + `types.ts`）
- 组件用 PascalCase 目录
```

**输入示例（后端项目）**：
```markdown
### 目录结构规范
- Controller 放 `controller/` 目录
- Service 放 `service/` 目录
- Entity 放 `model/` 目录
```

**输出格式**（通用，基于实际项目内容动态提取）：
```json
{
  "pagePattern": "从 CLAUDE.md 中提取的页面文件模式",
  "apiPattern": "从 CLAUDE.md 中提取的 API 文件模式",
  "componentPattern": "从 CLAUDE.md 中提取的组件目录模式",
  "stylePattern": "从 CLAUDE.md 中提取的样式文件模式（如有）",
  "basePaths": "从 CLAUDE.md 中提取的源码根目录（如 src/views/、src/main/java/）"
}
```

> **注意**：不要假设固定的文件扩展名（`.tsx`、`.vue`、`.py`、`.java` 等）。从 CLAUDE.md 中提取项目实际使用的扩展名和文件组织方式。

---

## 6. 场景映射提取

**定位方式**：查找包含"场景选择"或"我要开发"关键词的章节

**提取策略**：解析表格

**输入示例**：
```markdown
| 我要开发 | 使用方式 |
|---------|---------|
| 列表页（搜索+表格+分页） | `对应项目的列表页生成方式` |
| 表单页（新增/编辑） | `对应项目的表单页生成方式` |
```

**输出格式**：
```json
[
  { "scene": "列表页", "skill": "从CLAUDE.md提取的Skill名", "pageType": "list" },
  { "scene": "表单页", "skill": "从CLAUDE.md提取的Skill名", "pageType": "form" }
]
```

> **注意**：Skill 名和命令从 CLAUDE.md 的「场景→Skill 映射」章节中提取。不要硬编码特定项目的 Skill 名称。

**pageType 推断规则**：
- 含"列表" → `list`
- 含"表单" → `form`
- 含"详情" → `detail`
- 含"审批" → `approval`
- 含"弹窗" → `modal`

---

## 提取失败处理

| 场景 | 处理 |
|------|------|
| 章节标题找不到 | 尝试模糊匹配（忽略空格、中英文混合） |
| 表格格式不标准 | 尝试宽松解析（容忍多余空格、缺失分隔行） |
| 提取结果为空 | 标记为缺失，进入交互式补充流程 |
| 数据格式异常 | 保留原文，标注 `raw: true` 供人工确认 |
