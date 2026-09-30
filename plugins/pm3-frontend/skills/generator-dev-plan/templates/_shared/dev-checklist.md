---

## 开发流程检查清单

### 前置检查
- [ ] 已确认当前模块使用的 Skill：`{{skillName}}`
- [ ] 已阅读 PRD 对应章节：[{{prdSection}}]({{prdPath}})
- [ ] 已确认参考模块：`{{refModule}}`

### 编码检查
- [ ] 代码生成后，目录结构符合 `directory-structure.md` 规范
- [ ] 组件使用符合 `check.md` 推荐列表
- [ ] 数字输入符合 `comp-storage.md` 规范
- [ ] 表单校验完整

### 强制 Code Review
- [ ] **编码完成后，必须启动 `superpowers:code-reviewer` agent 进行代码审查**
- [ ] Reviewer 反馈的问题已全部修复
- [ ] 通过项目 `check.md` 提交前检查清单

> 审查命令：在 Claude Code 中完成编码后，告知"编码完成，请启动 code-reviewer 审查"。
