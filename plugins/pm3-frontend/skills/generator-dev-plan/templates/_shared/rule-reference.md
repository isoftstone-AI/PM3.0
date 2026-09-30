### 前置规则参考

> ⚠️ **重要提示**：开发本模块前请务必阅读并遵守以下规则，不符合规则的实现将不予通过Code Review。

{{#if skillName}}
#### 1. Skill 使用规范
- 必须使用 `{{skillName}}` 生成代码
- 参考文档：[{{skillName}} 使用指南]({{skillDocPath}})
- 注意事项：开发方案仅作为Skill的输入参数，代码结构必须由Skill模板生成，禁止手动修改结构
{{/if}}

{{#if projectRulePath}}
#### 2. 项目开发规范
- 本模块需符合 [PM3.0 前端开发规范]({{projectRulePath}}) 第 {{ruleSection}} 章要求
- 目录结构必须严格遵循 `rules/global/directory-structure.md` 规范
- 组件选型必须从推荐组件列表中选择，禁止使用废弃组件
{{/if}}

{{#if refModule}}
#### 3. 参考模块实现
- 逻辑实现可参考 [{{refModule}} 模块代码]({{refModulePath}})
- 参考要点：交互逻辑、权限控制、接口调用方式、代码组织结构
{{/if}}

#### 4. 通用规则检查
- ✅ 表单使用 `ant-design-vue` 原生组件，禁止使用废弃的 `Myth*` 系列组件
- ✅ 表格必须使用 `BasicTable` 组件，禁止直接使用 `a-table`
- ✅ 字典选择必须使用 `DictSelect` 组件，禁止手动实现字典映射
- ✅ 用户选择优先使用 `LovSelect` 组件，特殊场景使用 `UserSelect`
- ✅ 文件上传必须使用项目统一的 `Upload` 组件，禁止使用原生上传
