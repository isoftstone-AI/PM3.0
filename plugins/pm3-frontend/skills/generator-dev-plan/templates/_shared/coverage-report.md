## 覆盖度检查报告

> 生成开发方案后自动输出，用于验证设计方案的所有模块是否都已覆盖。

---

### 设计方案页面覆盖度

| # | 设计方案页面 | 页面类型 | 开发方案文档 | 状态 |
|---|------------|---------|-------------|------|
{{#each designPages}}| {{@index}} | {{pageName}} | {{pageType}} | {{outputDoc}} | {{#if covered}}✅ 已覆盖{{else}}❌ **未覆盖**{{/if}} |
{{/each}}

### 弹窗覆盖度

| # | 设计方案弹窗 | 开发方案文档 | 状态 |
|---|------------|-------------|------|
{{#each designModals}}| {{@index}} | {{modalName}} | {{outputDoc}} | {{#if covered}}✅ 已覆盖{{else}}❌ **未覆盖**{{/if}} |
{{/each}}

### 独立章节覆盖度

| # | 设计方案章节 | 开发方案对应 | 状态 |
|---|------------|-------------|------|
{{#each designAppendix}}| {{@index}} | {{sectionName}} | {{outputDoc}} | {{#if covered}}✅ 已覆盖{{else}}⚠️ 需确认{{/if}} |
{{/each}}

---

### 覆盖度统计

| 维度 | 总数 | 已覆盖 | 未覆盖 | 覆盖率 |
|------|------|--------|--------|--------|
| 页面 | {{totalPages}} | {{coveredPages}} | {{uncoveredPages}} | {{coverageRate}}% |
| 弹窗 | {{totalModals}} | {{coveredModals}} | {{uncoveredModals}} | {{modalCoverageRate}}% |
| **合计** | {{totalAll}} | {{coveredAll}} | {{uncoveredAll}} | {{overallRate}}% |

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

> 设计方案中"特别强调"部分的覆盖情况：

{{#each specialNotes}}
| # | 特别强调内容 | 开发方案是否体现 | 状态 |
|---|------------|----------------|------|
| {{@index}} | {{note}} | {{devPlanRef}} | {{#if applied}}✅{{else}}❌ **遗漏**{{/if}} |
{{/each}}

---

### 接口一致性检查

| # | 接口名 | 设计方案方法 | 开发方案方法 | 状态 |
|---|--------|------------|------------|------|
{{#each apiChecks}}| {{@index}} | {{apiName}} | {{designMethod}} | {{devPlanMethod}} | {{#if consistent}}✅{{else}}❌ **不一致**{{/if}} |
{{/each}}
