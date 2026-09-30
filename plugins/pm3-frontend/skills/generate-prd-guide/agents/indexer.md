# Indexer SubAgent — 三源交叉索引器

> 详细规则见 `references/indexer-rules.md`

## 任务

将 Scanner 输出的模块索引与 PRD 文档、API 文档进行交叉匹配，为每个字段/按钮建立双向链接。

## 输入

- `scannerIndex`: Scanner 输出（`temp/scanner-index.json`）
- `prdPath`: PRD 文档路径
- `apiDocPath`: API 文档路径（可选）

## 输出

增强索引 JSON，保存到 `temp/indexer-enhanced.json`

## 执行步骤

### Step 1：PRD 字段检索（四轮搜索）

> 详见 `references/indexer-rules.md` §1

对每个字段依次执行：

| 轮次 | 搜索策略 | 搜索范围 | 停止条件 |
|------|---------|---------|---------|
| 第 1 轮 | 字段中文名精确匹配 | PRD 全文 | 找到直接定义 |
| 第 2 轮 | 去掉通用后缀后模糊匹配 | PRD 全文 | 找到变体描述 |
| 第 3 轮 | prdKeyword + 页面上下文 | 页面对应 PRD 章节 | 找到散落规则 |
| 第 4 轮 | 模块类型关键词 | 通用规则章节 | 记录结果 |

**PRD 提取内容**：

```json
{
  "fieldName": "PRD 中的字段英文名",
  "section": "PRD 章节号",
  "anchor": "PRD 锚点",
  "rules": {
    "required": "Y/N/条件必填：[条件]",
    "readonly": "Y/N/条件只读：[条件]",
    "maxLength": "最大长度",
    "precision": "精度",
    "format": "格式",
    "dict": "字典编码",
    "searchType": "搜索类型",
    "autoFrom": "自动带出来源",
    "linkage": "联动逻辑"
  },
  "description": "字段说明原文",
  "confidence": "high/medium/low/unmatched"
}
```

### Step 2：PRD 按钮检索（两轮搜索）

| 轮次 | 搜索策略 | 搜索范围 |
|------|---------|---------|
| 第 1 轮 | 按钮名称 + "按钮" | PRD 按钮逻辑章节 |
| 第 2 轮 | 按钮名称模糊匹配 | PRD 全文 |

**提取内容**：section, anchor, displayCondition, validate, action, successResult, failResult, position, confidence

### Step 3：API 检索（如有 apiDocPath）

> 详见 `references/indexer-rules.md` §4

**匹配方式**：
1. 字段英文名精确匹配 API 字段
2. 字段中文名匹配 API 说明文字
3. prdKeyword 匹配 API 参数说明

**提取内容**：

```json
{
  "apiFieldName": "API 字段英文名",
  "apiType": "string/number/boolean",
  "endpoint": "接口地址",
  "method": "GET/POST",
  "paramType": "query/body/path",
  "required": "Y/N",
  "example": "示例值",
  "enum": "枚举值",
  "confidence": "high/medium/low/unmatched"
}
```

**三源冲突优先级**（详见 `references/indexer-rules.md` §4.4）：

| 维度 | 以谁为准 |
|------|---------|
| 字段名/枚举值 | **API** |
| 必填性 | **PRD** |
| 字段是否缺失 | **PRD** |
| 字段类型/组件 | **设计图** |

**下拉数据源检测**（详见 `references/indexer-rules.md` §4.5）：
- 对每个 Select 字段，检查是否有字典编码或独立数据源接口
- 无数据源 → 记录 `missingDataSource`，加入缝隙清单

### Step 4：置信度判定

> 详见 `references/indexer-rules.md` §5

| 等级 | 字段条件 | 按钮条件 |
|------|---------|---------|
| **high** | 第 1 轮命中，英文名+规则都找到 | 第 1 轮命中，行为+校验都找到 |
| **medium** | 第 2-3 轮命中 | 第 1 轮命中，仅行为 |
| **low** | 第 4 轮命中 | 第 2 轮命中 |
| **unmatched** | 4 轮都未找到 | 2 轮都未找到 |

### Step 5：缝隙分析

> 详见 `references/indexer-rules.md` §6

- `prdUnmatched`：PRD 中未找到（confidence = low/unmatched）
- `apiUnmatched`：API 中未找到（api = null 或 unmatched）
- `consistencyIssues`：PRD 多章节描述矛盾

### Step 6：业务规则提取

> 详见 `references/indexer-rules.md` §9

从 PRD 中提取：
- **业务背景**：搜索"业务流程/功能概述/适用于"
- **校验规则**：搜索"校验/验证/提交时/前置条件/不允许"
- **失败提示**：搜索"提示/请先/尚未/未完成"

仅在找到校验规则或失败提示时输出 `businessRules`。

### Step 7：页面关系提取

**提取规则**：
- 弹窗触发关系：triggerPage → modal
- 页面类型推断：list→form（新增/编辑）、list→detail（查看）、form→approval（提交）
- PRD 跳转说明：提取"跳转到/从XX进入/返回XX"

### Step 8：输出增强索引

输出到 `temp/indexer-enhanced.json`，结构示例：

```json
{
  "moduleName": "开工管理",
  "pages": [{
    "pageId": "start-apply-list",
    "prdChapter": "5.1.5.2",
    "prdAnchor": "#5152-开工申请列表",
    "modules": [{
      "moduleId": "M1",
      "fields": [{
        "label": "申请单号",
        "component": "Input",
        "prd": { "fieldName": "applyNo", "section": "5.1.5.2", "rules": {...}, "confidence": "high" },
        "api": { "apiFieldName": "applyNo", "apiType": "String", "confidence": "high" }
      }],
      "buttons": [{
        "name": "查询",
        "prd": { "action": "根据筛选条件刷新列表", "confidence": "high" }
      }]
    }]
  }],
  "gapAnalysis": { "prdUnmatched": [...], "apiUnmatched": [...] },
  "businessRules": { "background": "...", "validationRules": [...], "failMessages": [...] },
  "pageRelations": [{ "from": "list", "to": "form", "label": "新增/编辑" }]
}
```

## 质量检查清单

- [ ] 所有字段都执行了 PRD 四轮检索
- [ ] 所有按钮都执行了 PRD 两轮检索
- [ ] 匹配置信度标注正确
- [ ] PRD 锚点格式正确（`#章节号-描述`）
- [ ] 字段英文名已提取
- [ ] 必填/只读规则已提取
- [ ] Select 字段数据源已检测
- [ ] 三源冲突已按优先级处理
- [ ] 缝隙清单完整
- [ ] API 检索（如有）完成
- [ ] 业务规则已提取（如有）
- [ ] 页面关系已提取
