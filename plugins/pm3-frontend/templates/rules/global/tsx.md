---
paths:
  - "src/**/*.tsx"
  - "src/**/*.ts"
---
# TSX 基础规范

> Vue 3 + TypeScript + TSX 开发规范

---

## 生命周期规范

### watch 必须在 onMounted 中调用

**强制规则**：所有 `watch` 必须在 `onMounted` 生命周期中调用，禁止在 `setup` 中直接调用。

❌ 错误示例（禁止）：
```tsx
setup(props) {
  // 直接在 setup 中调用 watch
  watch(
    () => props.modelValue,
    val => {
      // ...
    },
  );
}
```

✅ 正确示例（必须）：
```tsx
import { defineComponent, onMounted, watch } from 'vue';

setup(props) {
  onMounted(() => {
    watch(
      () => props.modelValue,
      val => {
        // ...
      },
      { immediate: true, deep: true },
    );
  });
}
```

### 多个 watch 处理

如果组件需要监听多个数据源，统一放在一个 `onMounted` 中：

```tsx
onMounted(() => {
  // 监听数据变化
  watch(
    () => props.modelValue,
    data => {
      setTableData(data);
    },
    { immediate: true, deep: true },
  );

  // 监听状态变化
  watch(
    () => props.isEditing,
    () => {
      setColumns(getColumns());
    },
  );
});
```

---

## 组件定义

### 必须使用 defineComponent

```tsx
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'ComponentName',  // ✅ 必须：PascalCase
  setup(props, ctx) {
    // ...
    return () => (
      <div>JSX 内容</div>
    );
  },
});
```

### 禁止事项

| 禁止 | 正确写法 |
|-----|---------|
| ❌ `render()` 函数 | ✅ `setup()` 返回渲染函数 |
| ❌ 在 TSX 中使用 `this` | ✅ 使用 `setup` 参数 |
| ❌ `components` 配置 | ✅ 直接导入使用 |

---

## Props 定义

```typescript
// props.ts
import type { PropType } from 'vue';

export type PageType = 'add' | 'edit' | 'view';

export const props = {
  type: {
    type: String as PropType<PageType>,
    default: 'view',
  },
  id: {
    type: String,
    required: false,
  },
};
```

---

## 组件暴露

```tsx
export interface ComponentExpose {
  validate: () => Promise<boolean>;
  getValues: () => Recordable;
}

export default defineComponent({
  name: 'MyForm',
  setup(props, ctx) {
    // 暴露方法给父组件
    ctx.expose({
      validate: async () => { /* ... */ },
      getValues: () => { /* ... */ },
    } as ComponentExpose);

    return () => (
      <Form>...</Form>
    );
  },
});
```
