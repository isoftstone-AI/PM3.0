---
paths:
  - "src/**/*.tsx"
  - "src/**/*.ts"
---
# API 规范

---

## 请求封装

使用 `defHttp` 统一封装：

```typescript
import { defHttp } from '@/utils/http/axios';
import { NormalResponse, Page, Pagination } from '@/api/types';

export enum Api {
  Prefix = '/api/pm3/construct-review',  // ✅ 本项目前缀
}

// GET 请求
export function getDetail(id: string) {
  return defHttp.get<NormalResponse<ReviewDetail>>({
    url: Api.Prefix + '/detail',
    params: { id },
  });
}

// POST 请求
export function save(data: Partial<ReviewParams>) {
  return defHttp.post<NormalResponse>({
    url: Api.Prefix + '/save',
    data,
  });
}

// 列表查询
export function getList(params: Pagination<ReviewSearchParams>) {
  return defHttp.post<Page<ReviewRecord>>({
    url: Api.Prefix + '/list',
    data: params,
  });
}
```

## 响应类型

| 类型 | 用途 | 结构 |
|-----|------|------|
| `NormalResponse<T>` | 普通响应 | `{ code: number; msg: string; data: T }` |
| `Page<T>` | 分页列表 | `{ list: T[]; total: number }` |
| `Pagination<T>` | 分页参数 | `{ current: number; size: number } & T` |

## 错误处理

```typescript
const handleSubmit = useLockFn(async () => {
  try {
    const { code, msg } = await save(data);
    if (code !== 0) {
      createMessage.error(msg);
      return;
    }
    createMessage.success('保存成功');
  } catch (error) {
    console.error(error);
  }
});
```
