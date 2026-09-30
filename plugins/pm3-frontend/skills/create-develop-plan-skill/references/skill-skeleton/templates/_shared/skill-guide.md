## Skill 使用指引

{{#if sceneSkillList}}
{{#each sceneSkillList}}
### {{pageTypeText}}

{{#if skillCommand}}
使用 `{{skillCommand}}` 生成基础框架：

```bash
{{skillCommand}} prdPath={{prdPath}} outputPath={{pageBasePath}}/{{pagePath}}/
```

{{#if postGenNotes}}
生成后需调整：
{{#each postGenNotes}}- {{this}}
{{/each}}
{{/if}}
{{else}}
> ⚠️ CLAUDE.md 中未定义 `{{pageType}}` 类型的代码生成 Skill。请手动编写或补充场景映射。
{{/if}}

{{/each}}
{{else}}
> ⚠️ CLAUDE.md 中未定义场景→Skill 映射。请手动编写代码，或在 CLAUDE.md 中补充映射后重新生成。
{{/if}}
