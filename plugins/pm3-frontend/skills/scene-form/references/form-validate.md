# 表单校验代码模板

> 来源：设备提资 `BasicInfoSection` 实际上线版本

## Section 组件内

```tsx
import type { FormInstance, Rule } from 'ant-design-vue';

const formRef = ref<FormInstance>();
const isDisabled = computed(() => props.disabled);

// 普通必填
const requiredRule = (msg: string): Rule[] =>
  isDisabled.value ? [] : [{ required: true, message: msg, trigger: ['blur', 'change'] as any }];

// 单选人员必填（兼容 LovSelect {label,value} 和后端 {userId,userName}）
const userRequiredRule = (msg: string): Rule[] =>
  isDisabled.value ? [] : [{ required: true, trigger: ['blur', 'change'] as any, validator: (_r, v) => {
    if (v?.label && !v?.userId && !v?.value) return Promise.resolve();
    return (!v || (!v.userId && !v.value)) ? Promise.reject(msg) : Promise.resolve();
  }} as any];

// 多选人员必填（LovSelect mode=multiple）
const usersRequiredRule = (msg: string): Rule[] =>
  isDisabled.value ? [] : [{ required: true, trigger: ['blur', 'change'] as any, validator: (_r, v) => {
    return (!v || !v.length) ? Promise.reject(msg) : Promise.resolve();
  }} as any];

const rules = computed(() => ({
  fieldName: requiredRule('请输入字段名'),
  userField: userRequiredRule('请选择人员'),
  usersField: usersRequiredRule('请选择人员（可多选）'),
}));

const validate = async () => {
  if (isDisabled.value) return true;
  if (!formRef.value) return true;
  return formRef.value.validate();
};

expose({ validate });
```

## 父组件调用

```tsx
const sectionRef = ref<any>(null);

const validateForm = async (): Promise<boolean> => {
  try {
    await sectionRef.value?.validate();
    return true;
  } catch { return false; }
};
```

## 关键约定

- **统一 trigger**：所有规则均带 `trigger: ['blur', 'change']`
- **disabled 时跳过**：规则工厂在 disabled 时返回 `[]`，validate 直接返回 `true`
