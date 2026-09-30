# PM 3.0 开发管理模块表单字段映射

> 来源：`src/views/dmanage/` 目录下的所有表单组件
> 生成时间：2026-03-13

---

## 目录结构

```
src/views/dmanage/
├── clue/                    # 线索管理
├── dev-auth/                # 开发权管理
├── indicator/               # 指标管理
├── industrial/              # 产业投资决策
├── payment/                 # 付款管理
├── pre-pro-init/            # 预立项管理
└── pro-init/                # 立项管理
```

---

## 1. 线索管理 (clue)

### 文件位置
`src/views/dmanage/clue/components/add-edit-form/useIndex.ts`

### 表单字段

| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `proName` | Input | ✅ | max: 128 | 项目名称 |
| `area` | 省市区级联 | ✅ | - | 省/市/区对象 |
| `format` | Select | ✅ | - | 项目业态：1-风电, 2-光伏, 3-储能 |
| `capacityTotal` | Input Number | ✅ | 2位小数 | 项目总容量(MW) |
| `energyScale` | Input Number | 条件 | 2位小数 | 储能规模(MW) |
| `storageCapacity` | Input Number | 条件 | 2位小数 | 储能容量(MWh) |
| `obtainDate` | DatePicker | ✅ | - | 获取日期 |
| `subCode` | Select | ✅ | - | 分公司编码 |
| `regionCode` | Select | ✅ | - | 区域编码 |
| `developerCode` | Select | ✅ | - | 开发人员编码 |
| `closeReason` | TextArea | 条件 | - | 放弃原因(giveUp类型必填) |

### 特殊逻辑
- **业态驱动校验**：format=1(风电)时capacityTotal必填；format=3(储能)时energyScale和storageCapacity必填
- **容量互斥校验**：项目总容量>0 && 储能规模>=0 或 项目总容量=0 && 储能规模>0

---

## 2. 开发权管理 (dev-auth)

### 文件位置
`src/views/dmanage/dev-auth/components/add-edit-form/useIndex.ts`

### 表单字段

#### 基础信息
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `proName` | Input | ✅ | max: 128 | 项目名称 |
| `area` | 省市区级联 | ✅ | - | 省/市/区对象 |
| `format` | Select/MultiSelect | ✅ | - | 项目业态(支持多选组合) |
| `address` | Input | ✅ | - | 项目地址 |
| `obtainDate` | DatePicker | ✅ | - | 获取日期 |
| `lockLevel` | Select | ✅ | - | 锁定级别 |

#### 容量信息
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `capacityTotal` | Input Number | 条件 | 2位小数 | 项目总容量(MW) |
| `capacityWindPower` | Input Number | 条件 | 2位小数, >0 | 风电容量(MW) |
| `capacityPv` | Input Number | 条件 | 2位小数, >0 | 光伏交流容量(MW) |
| `capacityPvDc` | Input Number | - | 2位小数 | 光伏直流容量(MW) |
| `energyScale` | Input Number | 条件 | 2位小数, >0 | 储能规模(MW) |
| `storageCapacity` | Input Number | 条件 | 2位小数, >0 | 储能容量(MWh) |
| `coverArea` | Input Number | - | 2位小数 | 用地面积 |

#### 组织信息
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `subCode` | Select | ✅ | 分公司编码 |
| `regionCode` | Select | ✅ | 区域编码 |
| `developerCode` | Select | ✅ | 开发人员编码 |

#### 附件
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `attachmentDTOList` | Upload | ✅ | 附件列表(attachmentType: '1') |

### 特殊逻辑
- **多业态支持**：format支持多选，组合包括：风光一体化、风储一体化、光储一体化、风光储一体化
- **自动命名**：根据省市区+容量+业态自动生成项目名称
- **长期有效**：longValid为true时expireDate非必填

---

## 3. 指标管理 (indicator)

### 3.1 指标申报表单

#### 文件位置
`src/views/dmanage/indicator/components/add-edit-form/useIndex.ts`

#### 表单字段

| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `proName` | Input | ✅ | max: 128 | 项目名称 |
| `area` | 省市区级联 | ✅ | - | 省/市/区对象 |
| `format` | Select | ✅ | - | 项目业态 |
| `address` | Input | ✅ | - | 项目地址 |
| `obtainDate` | DatePicker | ✅ | - | 获取日期 |
| `lockLevel` | Select | ✅ | - | 锁定级别 |
| `subCode` | Select | ✅ | - | 分公司编码 |
| `regionCode` | Select | ✅ | - | 区域编码 |
| `developerCode` | Select | ✅ | - | 开发人员编码 |
| `capacityTotal` | Input Number | - | 2位小数 | 项目总容量 |
| `capacityWindPower` | Input Number | - | 2位小数 | 风电容量 |
| `capacityPv` | Input Number | - | 2位小数 | 光伏交流容量 |
| `capacityPvDc` | Input Number | - | 2位小数 | 光伏直流容量 |
| `energyScale` | Input Number | - | 2位小数 | 储能规模(MW) |
| `storageCapacity` | Input Number | - | 2位小数 | 储能容量(MWh) |
| `coverArea` | Input Number | - | 2位小数 | 用地面积 |
| `dynamicPrice` | Input Number | - | 4位小数 | 动态电价 |
| `unitCost` | Input Number | - | 4位小数 | 单位成本 |
| `grossMargin` | Input Number | - | 4位小数 | 毛利率 |
| `grossProfitMargin` | Input Number | - | 4位小数 | 净利润率 |
| `yearCable` | Input Number | - | 2位小数 | 年电缆用量 |
| `greenCablePrice` | Input Number | - | 2位小数 | 绿色电缆价格 |
| `customerPrice` | Input Number | - | 2位小数 | 客户电价 |
| `hydrogenProductionCapacity` | Input Number | - | 2位小数 | 制氢产能 |
| `postTaxFullInvestment` | Input Number | - | 2位小数 | 税后全投资 |
| `taxInclusiveCapital` | Input Number | - | 2位小数 | 含税资本金 |
| `headquartersApproval` | Select | ✅ | - | 总部是否审批 |
| `attachmentDTOList` | Upload | ✅ | - | 附件(attachmentType: '40') |

---

### 3.2 指标确认表单 (审批)

#### 文件位置
`src/views/dmanage/indicator/components/approval-form/useIndex.ts`

#### 表单字段

##### 基础信息
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `obtainStatus` | Select | ✅ | 指标获取状态：0-未获取, 1-已获取 |
| `obtainDate` | DatePicker | ✅ | 获取日期 |
| `lockLevel` | Select | ✅ | 锁定级别 |

##### 申报信息
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `headquartersApproval` | Select | ✅ | - | 总部是否审批 |
| `declarationMethod` | Select | ✅ | - | 申报方式：1-独立, 2-联合 |
| `effectStart` | DatePicker | ✅ | - | 指标生效日期 |
| `effectEnd` | DatePicker | ✅ | - | 指标失效日期 |
| `linkCompany` | Input | ✅ | max: 100 | 联合公司 |
| `equityRatio` | Input Number | ✅ | 0-100范围 | 股权比例 |

##### 本批次申报
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `requestCapacityTotal` | Input Number | - | 数字格式 | 申报总容量 |
| `requestCapacityWindPower` | Input Number | - | 数字格式 | 申报风电容量 |
| `requestCapacityPv` | Input Number | - | 数字格式 | 申报光伏容量 |
| `requestEnergyScale` | Input Number | - | 数字格式 | 申报储能规模(MW) |
| `requestStorageCapacity` | Input Number | - | 数字格式 | 申报储能容量(MWh) |

##### 可用容量
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `availableCapacityWindPower` | Input Number | - | 2位小数 | 可用风电容量 |
| `availableCapacityPv` | Input Number | - | 2位小数 | 可用光伏容量 |
| `availableCapacityPvDc` | Input Number | ✅ | 2位小数 | 可用光伏直流容量 |
| `availableEnergyScale` | Input Number | - | 2位小数 | 可用储能规模 |
| `availableStorageCapacity` | Input Number | - | 2位小数 | 可用储能容量 |
| `availableCoverArea` | Input Number | ✅ | 2位小数 | 可用用地面积 |

##### 附件
| 字段名 | 组件类型 | 说明 |
|--------|----------|------|
| `attachmentDTOList` | Upload | 附件(类型: 41, 42, 43) |

### 特殊逻辑
- **附件动态显示**：obtainStatus=1(已获取)时显示类型42附件；=0(未获取)时显示类型43附件
- **申报方式联动**：declarationMethod=1时projectBusinessModel='1'；=2时='2'

---

## 4. 产业投资决策 (industrial)

### 文件位置
`src/views/dmanage/industrial/components/add-edit-form/useIndex.ts`

### 表单字段

#### 变更信息
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `updateReason` | TextArea | ✅ | 变更原因(change/resubmit类型必填) |

#### 投资信息
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `totalInvestment` | Input Number | ✅ | 2位小数 | 项目总投资(万元) |
| `alreadyInvested` | Input Number | ✅ | 2位小数 | 已投资金额(万元) |
| `nowInvestment` | Input Number | ✅ | 2位小数 | 本次投资金额(万元) |

#### 协议信息
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `agreementContent` | TextArea | ✅ | 协议内容 |

#### 投资计划表
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `investmentPlanRecordList` | 动态表格 | ✅ | 投资计划记录列表 |
| ├─ `advanceContent` | Input | ✅ | 推进内容 |
| ├─ `energyProgress` | Input | ✅ | 能源进展 |
| ├─ `investmentTime` | DatePicker | ✅ | 投资时间 |
| └─ `planInvestment` | Input Number | ✅ | 计划投资 |

#### 附件
| 字段名 | 组件类型 | 说明 |
|--------|----------|------|
| `attachmentDTOList` | Upload | 附件(attachmentType: '50') |

---

## 5. 付款管理 (payment)

### 文件位置
`src/views/dmanage/payment/components/add-edit-form/useIndex.ts`

### 表单字段

> ⚠️ **注意**：当前表单为占位结构，字段命名不规范

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `code4` | Input | ✅ | 项目名称(占位) |
| `code5` | Select | ✅ | 占位字段 |
| `code6` | Select | ✅ | 占位字段 |
| `code7` | Select | ✅ | 占位字段 |
| `code8` | Select | ✅ | 占位字段 |
| `code9` | Select | ✅ | 占位字段 |
| `code10` | Select | ✅ | 占位字段 |
| `autoName` | Switch | - | 自动命名开关 |

---

## 6. 预立项管理 (pre-pro-init)

### 文件位置
`src/views/dmanage/pre-pro-init/components/add-edit-form/useIndex.ts`

### 表单字段

#### 基础信息
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `proName` | Input | ✅ | max: 128 | 项目名称 |
| `area` | 省市区级联 | ✅ | - | 省/市/区对象 |
| `format` | Select | ✅ | - | 项目业态 |
| `formatCreativity` | Select | - | - | 创新业态 |
| `address` | Input | ✅ | - | 项目地址 |
| `addrAbbr` | Input | ✅ | - | 地址简称 |
| `townshipName` | Input | ✅ | - | 乡镇名称 |
| `obtainDate` | DatePicker | ✅ | - | 获取日期 |
| `expireDate` | DatePicker | 条件 | - | 失效日期(非长期有效时必填) |
| `lockLevel` | Select | ✅ | - | 锁定级别 |
| `longValid` | Switch | - | - | 长期有效 |

#### 容量信息
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `capacityTotal` | Input Number | 条件 | 2位小数 | 项目总容量(MW) |
| `capacityWindPower` | Input Number | 条件 | 2位小数, >0 | 风电容量(MW) |
| `capacityPv` | Input Number | 条件 | 2位小数, >0 | 光伏交流容量(MW) |
| `capacityPvDc` | Input Number | - | 2位小数 | 光伏直流容量(MW) |
| `energyScale` | Input Number | 条件 | 2位小数, >0 | 储能规模(MW) |
| `storageCapacity` | Input Number | 条件 | 2位小数, >0 | 储能容量(MWh) |
| `coverArea` | Input Number | - | 2位小数 | 用地面积 |

#### 经济测算
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `dynamicPrice` | Input Number | ✅ | 4位小数 | 动态电价(元/kWh) |
| `unitCost` | Input Number | ✅ | 4位小数 | 单位成本(元/W) |
| `grossMargin` | Input Number | ✅ | 4位小数 | 毛利率(%) |
| `grossProfitMargin` | Input Number | ✅ | 4位小数 | 净利润率(%) |

#### 其他信息
| 字段名 | 组件类型 | 校验规则 | 说明 |
|--------|----------|----------|------|
| `yearCable` | Input Number | 2位小数 | 年电缆用量(万吨) |
| `greenCablePrice` | Input Number | 2位小数 | 绿色电缆价格(元/吨) |
| `customerPrice` | Input Number | 2位小数 | 客户电价(元/kWh) |
| `hydrogenProductionCapacity` | Input Number | 2位小数 | 制氢产能(万吨/年) |
| `postTaxFullInvestment` | Input Number | ✅ 2位小数 | 税后全投资(万元) |

#### 组织信息
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `subCode` | Select | ✅ | 分公司编码 |
| `regionCode` | Select | ✅ | 区域编码 |
| `developerCode` | Select | ✅ | 开发人员编码 |

#### 预立项结果
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `availableCapacityWindPower` | Input Number | 条件 | 2位小数, >0 | 可用风电容量 |
| `availableCapacityPv` | Input Number | 条件 | 2位小数, >0 | 可用光伏容量 |
| `availableCapacityPvDc` | Input Number | - | 2位小数 | 可用光伏直流容量 |
| `availableEnergyScale` | Input Number | 条件 | 2位小数, >0 | 可用储能规模 |
| `availableStorageCapacity` | Input Number | 条件 | 2位小数, >0 | 可用储能容量 |
| `availableCoverArea` | Input Number | - | 2位小数 | 可用用地面积 |
| `availableCapacityTotal` | Input Number | 条件 | 2位小数, >0 | 可用总容量(自动计算) |
| `availableDeveloperCode` | Select | ✅ | - | 可用开发人员 |
| `availableLargePayment` | Select | ✅ | - | 是否大支付 |
| `profitCenterName` | Select | ✅ | - | 利润中心名称 |
| `profitCenterCode` | Select | ✅ | - | 利润中心编码 |
| `expectDate` | DatePicker | 条件 | - | 预计日期(商务部审批时必填) |

#### 附件
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `attachmentDTOList` | Upload | ✅ | 附件(类型: 2, 3, 4) |

### 特殊逻辑
- **容量自动计算**：风电容量 + 光伏交流容量 = 项目总容量
- **利润中心联动**：根据regionCode获取利润中心选项

---

## 7. 立项管理 (pro-init)

### 文件位置
`src/views/dmanage/pro-init/components/add-edit-form/useIndex.ts`

### 表单字段

#### 基础信息 (同预立项)
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `proName` | Input | ✅ | 项目名称 |
| `area` | 省市区级联 | ✅ | 省/市/区对象 |
| `format` | Select | ✅ | 项目业态 |
| `address` | Input | ✅ | 项目地址 |
| `obtainDate` | DatePicker | ✅ | 获取日期 |
| `lockLevel` | Select | ✅ | 锁定级别 |
| `longValid` | Switch | - | 长期有效 |
| `expireDate` | DatePicker | 条件 | 失效日期 |

#### 容量信息 (同预立项)
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `capacityTotal` | Input Number | 条件 | 项目总容量 |
| `capacityWindPower` | Input Number | 条件 | 风电容量 |
| `capacityPv` | Input Number | 条件 | 光伏交流容量 |
| `capacityPvDc` | Input Number | - | 光伏直流容量 |
| `energyScale` | Input Number | 条件 | 储能规模 |
| `storageCapacity` | Input Number | 条件 | 储能容量 |
| `coverArea` | Input Number | - | 用地面积 |

#### 经济测算 (同预立项)
| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `dynamicPrice` | Input Number | ✅ | 动态电价 |
| `unitCost` | Input Number | ✅ | 单位成本 |
| `grossMargin` | Input Number | ✅ | 毛利率 |
| `grossProfitMargin` | Input Number | ✅ | 净利润率 |
| `yearCable` | Input Number | - | 年电缆用量 |
| `greenCablePrice` | Input Number | - | 绿色电缆价格 |
| `customerPrice` | Input Number | - | 客户电价 |
| `hydrogenProductionCapacity` | Input Number | - | 制氢产能 |

#### 立项结果
| 字段名 | 组件类型 | 必填 | 校验规则 | 说明 |
|--------|----------|------|----------|------|
| `availableCapacityTotal` | Input Number | - | 2位小数 | 可用总容量(自动计算) |
| `availableCapacityWindPower` | Input Number | - | 2位小数 | 可用风电容量 |
| `availableCapacityPv` | Input Number | - | 2位小数 | 可用光伏容量 |
| `availableCapacityPvDc` | Input Number | - | 2位小数 | 可用光伏直流容量 |
| `availableEnergyScale` | Input Number | - | 2位小数 | 可用储能规模 |
| `availableStorageCapacity` | Input Number | - | 2位小数 | 可用储能容量 |
| `postTaxFullInvestment` | Input Number | ✅ | 2位小数 | 税后全投资 |
| `taxInclusiveCapital` | Input Number | ✅ | 2位小数 | 含税资本金 |
| `establishmentDate` | DatePicker | ✅ | - | 成立日期 |
| `profitCenterName` | Select | ✅ | - | 利润中心名称 |

#### 附件
| 字段名 | 组件类型 | 说明 |
|--------|----------|------|
| `attachmentDTOList` | Upload | 附件(类型: 30, 31, 32) |

### 特殊逻辑
- **数据来源**：立项数据从预立项继承，可用容量字段自动带入
- **变更清空**：change/resubmit时清空postTaxFullInvestment、taxInclusiveCapital等字段
- **红线图**：支持查询红线图信息(redLineDiagram)

---

## 公共模式汇总

### 1. 省市区级联组件
```typescript
area: {
  province: { code: string, name: string },
  city: { code: string, name: string },
  district: { code: string, name: string }
}
// 提交时拆分为: provinceCode, provinceName, cityCode, cityName, countyCode, countyName
```

### 2. 组织三级联动
```typescript
// 联动顺序: subCode(分公司) → regionCode(区域) → developerCode(开发人员)
// 切换上级时自动清空下级选项
```

### 3. 业态驱动校验规则

| format值 | 必填字段 |
|----------|----------|
| '1' (风电) | capacityTotal, capacityWindPower |
| '2' (光伏) | capacityTotal, capacityPv |
| '3' (储能) | energyScale, storageCapacity |
| ['1','2'] (风光) | capacityTotal, capacityWindPower, capacityPv |
| ['1','2','3'] (风光储) | capacityTotal, capacityWindPower, capacityPv, energyScale, storageCapacity |

### 4. 数值精度规范

| 精度类型 | 字段示例 | 说明 |
|----------|----------|------|
| num2 (2位小数) | capacityTotal, coverArea, postTaxFullInvestment | 容量、面积、金额 |
| num4 (4位小数) | dynamicPrice, unitCost, grossMargin, grossProfitMargin | 价格、成本、比率 |

### 5. 附件类型映射

| 业务类型 | attachmentType | 说明 |
|----------|----------------|------|
| 开发权申请 | '1' | 开发权附件 |
| 预立项 | '2', '3', '4' | 预可研、土地预审、其他 |
| 立项 | '30', '31', '32' | 可研、环评、其他 |
| 指标申报 | '40' | 指标申报附件 |
| 指标确认-已获取 | '41', '42' | 指标文件、获取证明 |
| 指标确认-未获取 | '41', '43' | 指标文件、未获取说明 |
| 产业投资 | '50' | 产业投资附件 |

### 6. 自动命名规则
```typescript
// 格式: 省 + 市 + 区 + 容量(MW) + 业态 + '项目'
// 示例: 江苏省苏州市吴江区100MW光伏项目
proName = provinceName + cityName + countyName + capacityTotal + 'MW' + formatName + '项目'
```

---

## 注意事项

1. **付款管理表单**目前为占位实现，字段命名(code4-code10)不规范，需后续完善
2. **产业投资表单**的投资计划表为动态表格，需单独处理增删改逻辑
3. **指标确认表单**的附件根据obtainStatus动态切换类型
4. **预立项/立项表单**的利润中心选项通过regionCode异步获取
5. **所有表单**均支持add/edit/view/change/resubmit多种操作类型

---

## 8. 业务表单组件

> 以下组件在表单开发中可直接使用，替代或增强原生 ant-design-vue 组件

### 8.1-8.3 附件上传组件（Upload / AttachmentFileList / UploadTable / ProgressUpload）

> **详细文档和代码模板请使用 `/pattern-upload` Skill**，该 Skill 提供组件选择决策树、完整代码模板和踩坑提醒。

| 组件 | 导入路径 | 一句话定位 |
|------|----------|-----------|
| Upload | `@/components/Upload` | 通用上传，覆盖 80% 场景 |
| AttachmentFileList | `@/components/AttachmentFileList` | 多类型附件聚合管理 |
| UploadTable | `@/components/UploadTable` | 表格化文件管理 |
| ProgressUpload | `@/components/ProgressUpload` | 带进度上传 |
| FileCard | `@/components/FileCard` | 文件卡片展示 |

---

### 8.4 I18nInput（多语言输入框）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `value` | `Recordable<string>` / String | ✅ | I18nInput 为多语言对象；I18nJsonInput 为 JSON 字符串 |
| `type` | `'input' \| 'textarea'` | - | 输入框类型 |
| `maxlength` | Number | - | 最大长度 |
| `disabled / allowClear` | Boolean | - | 常规属性 |
| `inputReadonly` | Boolean | - | 只读模式，点击聚焦打开多语言弹窗 |
| `trim` | Boolean | - | 自动去除前后空格 |

**两个子组件**: `I18nInput.vue`（value 为多语言对象）, `I18nJsonInput.tsx`（value 为 JSON 字符串）

**适用场景**: 国际化字段输入，点击地球图标弹出多语言编辑弹窗

**导入路径**: `@/components/I18nInput/I18nInput.vue` 或 `@/components/I18nInput/I18nJsonInput.tsx`

---

### 8.5 PaginationSelect（分页选择器）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `mode` | `'select' \| 'label'` | - | 下拉选择器或纯文本回显 |
| `func` | Function | ✅ | 数据请求函数 |
| `keyword` | String | - | 搜索关键词字段名，默认 `'keyword'` |
| `params` | Object | - | 额外请求参数 |
| `fieldNames` | SelectProps['fieldNames'] | - | 选项字段映射 |
| `autoFeedback` | Boolean | - | 无匹配选项时自动回显，默认 true |
| `feedbackOnMounted` | Boolean | - | 挂载时自动根据 value 获取回显选项 |
| `optionFormatter` | Function | - | 选项格式化函数 |
| `bottomDistance` | Number | - | 触底加载距离 |

**子组件 CurrencySelect**: 基于 PaginationSelect 的币种选择器，CNY 默认置顶

**适用场景**: 大数据量下拉选择，自动触底加载更多数据

**导入路径**: `@/components/PaginationSelect/PaginationSelect.vue` 或 `@/components/PaginationSelect/CurrencySelect.tsx`

---

### 8.6 MaterialCategoryTreeSelect（物料分类树选择）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `onlyLabel` | Boolean | - | 只显示标签文本（不渲染选择器） |
| `showSearch` | Boolean | - | 默认 true，支持搜索 |
| `fieldNames` | Object | - | 默认 `{ value: 'id', label: 'name' }` |

继承 ant-design-vue TreeSelectProps，自动从主数据接口加载物料分类树数据

**适用场景**: 物料分类选择，树形结构

**导入路径**: `@/components/MaterialCategoryTreeSelect/MaterialCategoryTreeSelect.vue`

---

### 8.7 Period（期间选择器）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `value` | `[Dayjs, string, string]` | ✅ | [年份, 期间类型, 期间值] |
| `onChange` | Function | - | 值变化回调 |

**期间类型**: `'monthly'`(月度) \| `'quarterly'`(季度)

**辅助函数**: `getPeriod(data)` 将期间数据格式化为可读文本

**适用场景**: 年度+季度/月度的业务期间选择

**导入路径**: `@/components/Period`

---

### 8.8 ProjectSelectModal（项目选择弹窗）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `type` | `'customer' \| 'outer'` | - | 项目类型 |
| `onSuccess` | `(record) => void` | ✅ | 选择确认回调 |
| `beforeOk` | `(record) => boolean` | - | 确认前拦截 |
| `hideColumns` | `string[]` | - | 隐藏的表格列 |

内嵌带搜索表单的 BasicTable，支持按 SAP 项目编号、业态、名称搜索

**适用场景**: 需要关联选择项目时使用

**导入路径**: `@/components/ProjectSelectModal`

---

### 8.9 RangeNumberInput（数值范围输入）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `value` | `[number, number]` | ✅ | [最小值, 最大值] |
| `minPlaceholder / maxPlaceholder` | String | - | 占位文本 |
| `separator` | String | - | 分隔符，默认 `'-'` |
| `unit` | String | - | 单位文本 |
| `disabled` | Boolean | - | 是否禁用 |
| `min / max` | Number | - | 数值范围限制，默认 0 / 1000 |

自动校验最小值不大于最大值

**适用场景**: 需要输入数值范围（如容量范围、金额范围）时使用

**导入路径**: `@/components/RangeNumberInput/RangeNumberInput.vue`

---

### 8.10 DoubleInputNumber（双数字输入框）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `label` | String | ✅ | Form.Item 标签 |
| `first` | `InputConfig` | ✅ | 第一个输入框配置（value, addon, show, precision, onChange） |
| `second` | `InputConfig` | - | 第二个输入框配置（可选） |
| `disabled` | Boolean | - | 整体禁用 |
| `precision` | Number | - | 全局默认精度，默认 2 |

支持千分位格式化指令、独立精度控制和后缀单位

**适用场景**: 两个关联数值输入（如容量+储能容量）

**导入路径**: `@/components/common/DoubleInputNumber`

---

### 8.11 StorageScaleInput（储能规模输入）

> **详细文档**: `.claude/rules/global/comp-storage.md`

**适用场景**: 储能业态专用，替代 energyScale + storageCapacity 两个独立 InputNumber

**导入路径**: `@/components/common/StorageScaleInput`

---

### 8.12 ModuleTitle（模块标题）

| 字段名 | 组件类型 | 必填 | 说明 |
|--------|----------|------|------|
| `title` | String | ✅ | 标题文本 |
| `extra` | Slot | - | 右侧额外内容插槽 |

带左侧竖条装饰的标题组件

**适用场景**: 表单分组标题、页面区域标题

**导入路径**: `@/components/ModuleTitle`
