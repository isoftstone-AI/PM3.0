---
paths:
  - "src/**/*.tsx"
  - "src/**/*.ts"
---
# 组件：储能规模输入

**推荐组件**: `src/components/common/DoubleInputNumber/index.tsx`

**用途**: 用于输入储能规模（能量规模 MW / 储能容量 MWh）等双数字输入场景。

---

## Value 类型

储能场景下，两个输入框分别绑定 `energyScale` 和 `storageCapacity`：

```ts
// 储能规模
energyScale: number | string | undefined;      // 能量规模 (MW)
storageCapacity: number | string | undefined;  // 储能容量 (MWh)
```

---

## Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| first | InputConfig | - | 第一个输入框配置（必填） |
| second | InputConfig | - | 第二个输入框配置（可选） |
| disabled | boolean | false | 整体禁用 |
| precision | number | 2 | 全局默认精度，可被单个输入框覆盖 |

### InputConfig

| 属性 | 类型 | 说明 |
|------|------|------|
| value | number | 输入框的值 |
| addon | string \| null | 后缀单位，null 表示不显示 |
| show | boolean | 是否显示此输入框 |
| precision | number | 精度（小数位数），优先级高于全局 precision |
| formThousandsConfig | FormThousandsConfig | v-formThousands 指令配置 |
| onChange | (v: number \| undefined) => void | 值变更回调 |

### FormThousandsConfig

| 属性 | 类型 | 说明 |
|------|------|------|
| decimal | number | 小数位数 |
| min | number | 最小值 |
| max | number | 最大值 |
| intLength | number | 整数部分最大位数 |

---

## 使用示例

### 1. 储能规模（可编辑）

```tsx
import DoubleInputNumber from '@/components/common/DoubleInputNumber';

// state 用于 v-formThousands 指令绑定
const state = reactive({
  energyScale: undefined as number | undefined,
  storageCapacity: undefined as number | undefined,
});

// 同步 props -> state
watch(() => props.value, val => {
  state.energyScale = val?.energyScale;
  state.storageCapacity = val?.storageCapacity;
}, { immediate: true, deep: true });

<DoubleInputNumber
  disabled={false}
  first={{
    value: state.energyScale,
    addon: 'MW',
    formThousandsConfig: { intLength: 11, decimal: 6, max: 500 },
    onChange: v => {
      state.energyScale = v ?? undefined;
      updateValue('energyScale', v);
    },
  }}
  second={{
    value: state.storageCapacity,
    addon: 'MWh',
    show: true,
    formThousandsConfig: { intLength: 5, decimal: 6, max: 500 },
    onChange: v => {
      state.storageCapacity = v ?? undefined;
      updateValue('storageCapacity', v);
    },
  }}
/>
```

### 2. 储能规模（只读/禁用）

```tsx
<DoubleInputNumber
  disabled
  first={{
    value: detailData.energyScale,
    addon: 'MW',
  }}
  second={{
    value: detailData.storageCapacity,
    addon: 'MW/MWh',
    show: String(value.projectType) === '3',  // 仅储能业态显示
  }}
/>
```

### 3. 指标容量（根据业态动态显示）

```tsx
// 业态=风电/光伏 → 只显示第一个输入框（MW）
// 业态=储能 → 显示两个输入框（MW + MWh）
<DoubleInputNumber
  disabled
  precision={6}
  first={{
    value: value.indicatorCapacity,
    addon: String(value.projectType) !== '3' ? 'MW' : null,
    precision: 6,
  }}
  second={{
    value: value.indicatorStorageMwh,
    addon: 'MW/MWh',
    show: String(value.projectType) === '3',
    precision: 6,
  }}
/>
```

---

## 实际案例参考

详见 `src/views/eng-manage/start-apply/components/BasicInfoSection/index.tsx`（已上线）。

---

## 相关：数字输入指令（v-formThousands）

**适用场景**：单瓦成本、毛利额、容量等大额数字的千分位格式化和位数控制。

**判断标准**：满足以下任一条件 → 必须用 `v-formThousands`，禁止只用 `precision`

| 条件 | 说明 | 示例 |
|------|------|------|
| 大额数字 | 整数部分可能超过 6 位 | 毛利额（万元）、总容量（MW） |
| 千分位展示 | 需要友好的阅读格式 | 1,234,567.89 |
| 位数严格控制 | 需要限制最大/最小值 | 成本不能超过 999999 |

**参数配置速查**：
| 字段类型 | intLength | decimal | 单位 |
|---------|-----------|---------|------|
| 单瓦成本 | 6 | 4 | 元/W |
| 同类项目成本 | 6 | 4 | 元/W |
| 毛利额 | 12 | 6 | 万元 |
| 容量（MW/MWh） | 11 | 6 | MW/MWh |
| 毛利率 | 4 | 2 | % |
