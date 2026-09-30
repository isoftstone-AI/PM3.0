### 前置规则参考

> ⚠️ **重要提示**：开发本模块前请务必阅读并遵守以下规则，不符合规则的实现将不予通过 Code Review。

{{#if skillName}}
#### 1. Skill 使用规范
- 必须使用 `{{skillName}}` 生成代码
- 注意事项：开发方案仅作为 Skill 的输入参数，代码结构必须由 Skill 模板生成，禁止手动修改结构
{{/if}}

{{#if projectRulePath}}
#### 2. 项目开发规范
- 本模块需符合 [项目开发规范]({{projectRulePath}}) 第 {{ruleSection}} 章要求
- 目录结构必须严格遵循项目规范
- 组件选型必须从推荐组件列表中选择，禁止使用废弃组件
{{/if}}

{{#if refModule}}
#### 3. 参考模块实现
- 逻辑实现可参考 [{{refModule}} 模块代码]({{refModulePath}})
- 参考要点：交互逻辑、权限控制、接口调用方式、代码组织结构
{{/if}}

#### 4. 通用规则检查
{{#each rules}}
- ✅ {{rule}}
{{/each}}
