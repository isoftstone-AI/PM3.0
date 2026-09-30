## Skill 使用指引

{{#if (eq pageType "list")}}
使用 `/scene-list` Skill 生成基础框架：

```bash
/scene-list prdPath=设计管理/开发方案/xx-列表页-Mx-xxx.md apiPath=src/views/{{pagePath}}/api/index.ts
```

生成后需调整：
- 去掉 `ellipsis: true`
- 补充字典映射
- 调整列宽
{{/if}}

{{#if (eq pageType "form")}}
使用 `/scene-form` Skill 生成基础框架：

```bash
/scene-form prdPath=设计管理/开发方案/xx-表单页-Mx-xxx.md apiPath=src/views/{{pagePath}}/api/index.ts
```

生成后需调整：
- 补充设备明细表格（空列表）
- 设置字段只读/可编辑状态
{{/if}}

{{#if (eq pageType "approval")}}
使用 `/scene-approval` Skill 生成完整审批页代码。

```bash
/scene-approval
```

**必传参数（从本文档"业务组件信息"表格复制）：**
- 查看组件名 + 导入路径
- 编辑组件名 + 导入路径
- 详情 API 函数名 + 导入路径
- 审批注册 key
- 编辑组件 expose 方法名

**关键规则：**
- ApprovalForm 由 skill 模板标准生成（[KEEP] 区域不修改）
- 审批操作统一走 `completeTodoApi`（除非"审批提交 API 配置"选择了自定义）
- 驳回重发逻辑按 `isRejected` 分支处理
- 节点校验规则按"审批节点校验规则"表格补充到 `onSubmit` 中
{{/if}}

{{#if (eq pageType "detail")}}
使用 `/scene-detail` Skill 生成基础框架：

```bash
/scene-detail prdPath=设计管理/开发方案/xx-详情页-Mx-xxx.md apiPath=src/views/{{pagePath}}/api/index.ts
```

生成后需调整：
- 确保所有字段为只读模式
- 补充附件列的预览/下载逻辑
- 补充审批记录模块
- 复用 DocumentInfoSection 和 BasicInfoSection 组件
{{/if}}

{{#if (eq pageType "modal")}}
弹窗本质是迷你列表页，可参考 `/scene-list` 的搜索和表格逻辑：

```bash
/scene-list prdPath=设计管理/开发方案/xx-选择弹窗-Mx-xxx.md apiPath=src/views/{{pagePath}}/api/index.ts
```

生成后需手动补充：
- 单选逻辑（Radio 选择或点击行选择）
- 选中行高亮
- 返回值映射（确定后填充父页面字段）
- 弹窗显隐控制（`open` prop）
{{/if}}
