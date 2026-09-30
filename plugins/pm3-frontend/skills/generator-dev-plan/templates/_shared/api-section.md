## 涉及接口

> 接口来源：{{apiSourceType}}（{{apiSourceRef}}）
> 如未提供 apiDocSource，此章节标记为"待补充"，由开发者手动填写。

{{#if apis}}
### 业务接口

| 接口名 | 方法 | 路径 | 功能 | 调用时机 |
|--------|------|------|------|---------|
{{#each apis}}
| `{{apiName}}` | {{method}} | `{{path}}` | {{description}} | {{callTiming}} |
{{/each}}

### 接口参数详情

{{#each apis}}
#### {{apiName}}

{{#if requestParams}}
**请求参数** (`{{requestType}}`)：

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
{{#each requestParams}}
| {{paramName}} | {{paramType}} | {{#if required}}✅{{else}}-{{/if}} | {{description}} |
{{/each}}

{{/if}}
{{#if responseFields}}
**响应字段** (`{{responseType}}`)：

| 字段名 | 类型 | 说明 |
|--------|------|------|
{{#each responseFields}}
| {{fieldName}} | {{fieldType}} | {{description}} |
{{/each}}

{{/if}}
---

{{/each}}
{{else}}

> ⚠️ 未提供 apiDocSource，接口定义待补充。请手动填写以下内容：
> - 本模块调用的所有业务接口（名称、方法、路径、功能、调用时机）
> - 每个接口的请求参数和响应字段
> - Select 组件的下拉数据源接口（如有）
> - 字段与 API 返回字段的映射关系

{{/if}}

### 辅助接口（Select 数据源）

> 以下接口为下拉选择组件提供选项数据。如未找到数据源，标记 `[待确认]`。

| Select 字段 | 数据来源 | 接口/字典 | 状态 |
|------------|---------|----------|------|
{{#if selectDataSources}}
{{#each selectDataSources}}
| {{fieldLabel}} | {{sourceType}} | {{sourceRef}} | {{#if confirmed}}✅{{else}}⚠️ [待确认]{{/if}} |
{{/each}}
{{else}}
| - | - | - | ⚠️ 本模块无 Select 字段或数据源待确认 |
{{/if}}

### 字段→API 映射总表

> 开发时必须使用 API 字段名（apiFieldName）作为 dataIndex 和请求参数 key。

| # | 页面字段 (name) | API 字段 (apiFieldName) | API 类型 | 映射状态 |
|---|----------------|------------------------|---------|---------|
{{#each fields}}
| {{@index}} | `{{name}}` | {{#if apiFieldName}}`{{apiFieldName}}`{{else}}⚠️ 未匹配{{/if}} | {{#if apiType}}{{apiType}}{{else}}-{{/if}} | {{#if apiFieldDiff}}❌ 字段名不一致{{else}}{{#if apiFieldName}}✅{{else}}⚠️{{/if}}{{/if}} |
{{/each}}

{{#if hasApiFieldDiff}}
> ⚠️ **字段名不一致警告**：以上标记"字段名不一致"的字段，设计图/设计方案中使用的字段名与 API 返回的字段名不同。**开发时必须以 API 字段名为准**，不要使用设计图标注的伪代码字段名。
{{/if}}