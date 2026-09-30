## 开发自检

> 自检自测优先使用 `/graphify query` 查询参考模块实现

### 自检清单

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | 字段名与 PRD 一致 | {{check1Status}} | {{check1Detail}} |
| 2 | 组件选型与规范一致 | {{check2Status}} | {{check2Detail}} |
| 3 | 必填/只读状态正确 | {{check3Status}} | {{check3Detail}} |
| 4 | 字典编码正确 | {{check4Status}} | {{check4Detail}} |
| 5 | 联动逻辑实现完整 | {{check5Status}} | {{check5Detail}} |
| 6 | 校验规则完整 | {{check6Status}} | {{check6Detail}} |
| 7 | Select 字段数据源已确认 | {{check7Status}} | {{check7Detail}} |
| 8 | 字段 API 名称已确认 | {{check8Status}} | {{check8Detail}} |
| 9 | 接口方法/路径与 API 文档一致 | {{check9Status}} | {{check9Detail}} |

### 参考模块对比

> 使用 `/graphify query` 查询参考模块中相同字段的实现方式

**参考模块：** `{{#if refModule}}{{refModule}}{{else}}待确认{{/if}}`

| 字段名 | 当前方案组件 | 参考模块实现 | 是否一致 |
|--------|-------------|-------------|---------|
{{#each fields}}| {{name}} | {{component}} | {{refModuleComponent}} | {{consistencyStatus}} |
{{/each}}

### 测试用例

| # | 场景 | 操作 | 预期结果 |
|---|------|------|---------|
{{#each testCases}}| {{@index}} | {{scenario}} | {{operation}} | {{expected}} |
{{/each}}
