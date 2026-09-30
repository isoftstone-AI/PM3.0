# Scanner SubAgent — 设计图扫描器

> 详细规则见 `references/scanner-rules.md`

## 任务

从设计图文档中提取页面、模块、字段、按钮的结构化索引，作为后续处理的**骨架**。

## 输入

- `designPath`: 设计图文档路径
- `moduleName`: 模块名称

## 输出

JSON 格式的模块索引，保存到 `temp/scanner-index.json`

## 执行步骤

### Step 1：格式识别

自动检测设计图格式（详见 `references/scanner-rules.md` §1）：

| 格式 | 特征 | 解析方式 |
|------|------|---------|
| ASCII 框图 | 包含 `─│┌┐└┘` 等字符 | 模块 = `【模块 X：xxx】`，字段 = `标签：值` |
| YAML | 开头为 `page:` 或 `modules:` | 直接解析 YAML 结构 |
| Markdown 表格 | `##` + `\|` 表格 | 标题 = 页面/模块，表格行 = 字段 |

### Step 2：页面提取

识别所有页面，提取：

| 字段 | 说明 | 来源 |
|------|------|------|
| `pageId` | kebab-case 标识 | 从 pageName 转换 |
| `pageName` | 页面名称 | 原文 |
| `pageType` | list/form/detail/approval/modal | 从内容推断 |
| `route` | 路由路径 | 如有 |
| `designFileName` | 设计图文件名 | 文件名 |
| `designLocation` | 行号范围 | `#L起始-L结束` |

### Step 3：模块提取

对每个页面识别所有模块：

| 字段 | 说明 |
|------|------|
| `moduleId` | M1, M2, M3... |
| `moduleName` | 模块名称（原文） |
| `moduleType` | 归一化类型（见下表） |
| `designLocation` | 行号范围 |
| `fields` | 字段列表 |
| `buttons` | 按钮列表 |

**模块类型归一化**（详见 `references/scanner-rules.md` §2.3）：

| 设计图原名 | → 标准类型 |
|-----------|-----------|
| 筛选区/查询区/搜索区/条件区 | `search` |
| 按钮区/操作区/功能键区 | `action` |
| 列表区/表格区/数据区 | `table` |
| 基础信息区/表单区/填报区 | `form` |
| 详情区/展示区/只读区 | `display` |
| 附件区/文件上传区 | `attachment` |
| 审批意见区/审批区 | `approval` |

### Step 4：字段提取

对每个模块中的每个字段：

| 字段 | 说明 |
|------|------|
| `label` | 字段中文名（原文） |
| `component` | 组件类型（见下表推断） |
| `prdKeyword` | 搜索关键词数组 |

**组件类型推断**（详见 `references/scanner-rules.md` §3.2）：

| 设计图特征 | → 组件 |
|-----------|-------|
| `□□□`、输入框、文本框 | `Input` |
| `□□▼`、下拉、选择器 | `Select` |
| `📅`、日期选择器 | `DatePicker` |
| 多行、文本域 | `TextArea` |
| 表格列 | `TableColumn` |
| 级联选择 | `Cascader` |

**prdKeyword 生成**（详见 `references/scanner-rules.md` §3.3）：

```
1. 基础词 = 字段中文名
2. 去掉通用后缀（名称/编号/号/ID/码/日期/时间/类型/状态）
3. 添加同义词（项目→工程, 单号→编号）
4. 输出数组
```

### Step 5：按钮提取

| 字段 | 说明 |
|------|------|
| `name` | 按钮名称（**原文**，禁止同义替换） |
| `prdKeyword` | 搜索关键词数组 |

### Step 6：弹窗识别

| 字段 | 说明 |
|------|------|
| `modalId` | kebab-case 标识 |
| `modalName` | 弹窗名称（原文） |
| `modalType` | confirm/select/display |
| `triggerButton` | 触发按钮 |
| `triggerPage` | 触发页面 |

### Step 7：特殊情况处理（详见 `references/scanner-rules.md` §7）

- **模块嵌套**：扁平化，moduleId 用 `M4-1`、`M4-2` 格式
- **字段分组**：将分组视为子模块
- **动态字段**：添加 `dynamic: true` + 显示条件

### Step 8：输出 JSON

输出到 `temp/scanner-index.json`，结构示例：

```json
{
  "moduleName": "开工管理",
  "pages": [{
    "pageId": "start-apply-list",
    "pageName": "开工申请列表页",
    "pageType": "list",
    "route": "/engineering/start-apply/list",
    "designFileName": "开工申请列表页.yaml",
    "designLocation": "#L12-L58",
    "modules": [{
      "moduleId": "M1",
      "moduleName": "筛选查询区",
      "moduleType": "search",
      "designLocation": "#L15-L28",
      "fields": [
        { "label": "申请单号", "component": "Input", "prdKeyword": ["申请单号", "申请单", "单据编号"] }
      ],
      "buttons": [
        { "name": "查询", "prdKeyword": ["查询", "查询按钮", "搜索"] }
      ]
    }],
    "modals": [{
      "modalId": "delete-confirm",
      "modalName": "删除确认弹窗",
      "modalType": "confirm",
      "triggerButton": "删除",
      "triggerPage": "开工申请列表页"
    }]
  }]
}
```

## 质量检查清单

- [ ] 设计图格式已正确识别
- [ ] 所有页面都已提取
- [ ] 所有模块都已提取且类型映射正确
- [ ] 字段 label 与设计图**原文一致**
- [ ] 按钮 name 与设计图**原文一致**（禁止同义替换）
- [ ] prdKeyword 已生成
- [ ] 弹窗已提取并关联到触发页面
- [ ] designLocation 格式正确（`#L起始-L结束`）
- [ ] 嵌套模块已扁平化
