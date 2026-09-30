---
paths:
  - "src/**/*.tsx"
  - "src/**/*.ts"
  - "src/**/*.less"
  - "src/**/*.css"
---
# 样式规范

---

## 样式方案

- **Tailwind CSS**：优先使用，用于快速布局
- **CSS Module**：组件私有样式
- **Less**：全局变量和复杂样式

## 优先级

```
1. Tailwind CSS（优先）
2. CSS Module（组件级）
3. Less（全局）
4. 内联 styles（极少用）
```

## 常用 Tailwind 类

| 用途 | 类名 |
|-----|------|
| 外边距 | `mt-[10px]`, `mb-4`, `mx-auto` |
| 内边距 | `p-4`, `px-6`, `py-2` |
| 布局 | `flex`, `grid`, `justify-between` |
| 尺寸 | `w-full`, `h-screen`, `min-h-[200px]` |

## CSS Module 示例

```tsx
import styles from './style.module.less';

export default defineComponent({
  setup() {
    return () => (
      <div class={styles.container}>
        <div class={styles.header}>标题</div>
      </div>
    );
  },
});
```

## 样式文件命名

| 类型 | 命名 |
|-----|------|
| CSS Module | `style.module.less` |
| 普通 Less | `variables.less` |
| Tailwind 配置 | `tailwind.config.js` |
