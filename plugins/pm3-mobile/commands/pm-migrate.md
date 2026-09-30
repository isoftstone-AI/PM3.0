---
description: PM3.0 PC 页面迁移移动端 H5（强制工作流）
argument-hint: <pc-vue-path> <mobile-ref-path>
---

调用 pm-mobile-migration skill 执行迁移工作流。

输入：$ARGUMENTS
- 第一个参数：PC 端待迁移页面 .vue 路径
- 第二个参数：移动端参考页面 .vue 路径

使用 Skill 工具调用 skill: "pm-mobile-migration"，args 传 $ARGUMENTS。
若两个路径未提供齐，按 skill 约定用 AskUserQuestion 依次询问：
1. "请提供需要迁移的 PC 端页面路径"
2. "请提供移动端参考页面路径"
禁止凭模块名猜测 PC 端文件位置。
