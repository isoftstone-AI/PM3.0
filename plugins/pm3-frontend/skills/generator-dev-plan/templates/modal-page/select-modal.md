# {{pageName}} - 选择弹窗

{{> nav-links}}

{{> page-intro }}

---

## 使用 Skill 指引

| 步骤 | Skill | 用途 | 输入 | 输出 |
|------|-------|------|------|------|
| 1 | `/scene-list` | 生成弹窗内表格 | 搜索字段 + 表格列配置 | 搜索表单 + BasicTable |
| 2 | 手动补充 | 补充单选逻辑 + 返回值 | - | 完整弹窗 |

> **注意：** 弹窗本质是一个迷你列表页（搜索 + 表格 + 单选），可以复用 `/scene-list` 的搜索和表格逻辑。

---

## 弹窗概览

| 项 | 值 |
|----|-----|
| **弹窗标题** | {{modalTitle}} |
| **弹窗宽度** | {{modalWidth}} |
| **选择模式** | 单选 |
| **触发页面** | {{triggerPage}} |
| **触发字段** | {{triggerField}} |
| **确认后返回** | {{returnFields}} |

---

## 搜索条件

{{#each searchFields}}
### 搜索字段{{math @index "+" 1}}：{{name}}（{{label}}）

| 属性 | 值 |
|------|-----|
| field | `{{name}}` |
| label | `{{label}}` |
| component | `{{component}}` |
| required | 否 |
{{#if placeholder}}| placeholder | `{{placeholder}}` |
{{/if}}

{{/each}}

---

## 表格字段

| # | 列名 | 字段 | 宽度 | 渲染方式 | 选择 |
|---|------|------|------|----------|------|
{{#each tableColumns}}| {{math @index "+" 1}} | {{title}} | {{dataIndex}} | {{width}} | {{render}} | {{#if selectable}}✅{{else}}-{{/if}} |
{{/each}}

---

## 按钮清单

| 按钮名 | 功能 | 显示条件 | 事件流 |
|--------|------|---------|--------|
| 查询 | 执行搜索 | 一直显示 | 拼接搜索参数 → 调用接口 → 刷新列表 |
| 重置 | 清空搜索 | 一直显示 | 清空表单 → 调用接口 |
| 取消 | 关闭弹窗 | 一直显示 | 关闭弹窗，不返回数据 |
| 确定 | 确认选择 | 一直显示 | 关闭弹窗 → 返回选中行数据 |

---

## 选择逻辑

1. **单选模式**：只能选择一行数据
2. **选中行高亮**显示
3. 点击确定返回选中行数据

---

## 返回字段映射

| 接口返回字段 | 填充目标字段 | 说明 |
|-------------|-------------|------|
{{#each returnMapping}}| {{source}} | {{target}} | {{description}} |
{{/each}}

---

## 接口

| 接口 | 方法 | 路径 | 说明 |
|------|------|------|------|
| {{apiName}} | {{apiMethod}} | `{{apiPath}}` | {{apiDescription}} |

**请求参数：**
```typescript
interface {{apiParamsType}} extends Pagination {
{{#each searchFields}}  {{name}}?: {{type}}; // {{label}}
{{/each}}
}
```

---

## Skill 生成后的检查清单

- [ ] **单选模式**：Radio 或 click-row 选择
- [ ] **选中高亮**：选中行有视觉反馈
- [ ] **返回值完整**：所有映射字段都正确填充
- [ ] **接口参数正确**：搜索参数与接口定义一致
- [ ] **接口方法正确**：使用设计方案定义的 HTTP 方法，不自动推断

---

{{> self-check}}

{{> dev-checklist}}

{{> dev-reconciliation}}
