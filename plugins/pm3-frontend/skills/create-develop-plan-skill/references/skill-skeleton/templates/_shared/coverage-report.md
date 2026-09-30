## 覆盖度检查报告

> 生成开发方案后自动输出，用于验证设计方案的所有模块是否都已覆盖。

---

### 设计方案页面覆盖度

| # | 设计方案页面 | 页面类型 | 开发方案文档 | 状态 |
|---|------------|---------|-------------|------|
{{#each designPages}}| {{@index}} | {{pageName}} | {{pageType}} | {{outputDoc}} | {{#if covered}}✅ 已覆盖{{else}}❌ **未覆盖**{{/if}} |
{{/each}}

---

### 覆盖度统计

| 维度 | 总数 | 已覆盖 | 未覆盖 | 覆盖率 |
|------|------|--------|--------|--------|
| 页面 | {{totalPages}} | {{coveredPages}} | {{uncoveredPages}} | {{coverageRate}}% |

---

### 未覆盖清单（需要补充生成）

{{#each uncoveredItems}}
- [ ] **{{itemType}}：** {{itemName}} → 缺少 `{{outputDoc}}`
{{/each}}

{{#unless uncoveredItems}}
✅ 所有设计方案模块均已覆盖，无需补充。
{{/unless}}

---

### 特别强调检查

{{#each specialNotes}}
| # | 特别强调内容 | 开发方案是否体现 | 状态 |
|---|------------|----------------|------|
| {{@index}} | {{note}} | {{devPlanRef}} | {{#if applied}}✅{{else}}❌ **遗漏**{{/if}} |
{{/each}}
