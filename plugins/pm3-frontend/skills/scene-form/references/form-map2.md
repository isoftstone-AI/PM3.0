# PM 3.0 开发管理模块字段维度组件映射

> 视角：以字段为维度，树形展示字段使用的组件
> 范围：src/views/dmanage/
> 生成时间：2026-03-13

---

## 字段索引

- [proName](#proname-项目名称)
- [area](#area-省市区)
- [format](#format-项目业态)
- [capacityTotal](#capacitytotal-项目总容量)
- [capacityWindPower](#capacitywindpower-风电容量)
- [capacityPv](#capacitypv-光伏交流容量)
- [capacityPvDc](#capacitypvdc-光伏直流容量)
- [energyScale](#energyscale-储能规模mw)
- [storageCapacity](#storagecapacity-储能容量mwh)
- [obtainDate](#obtaindate-获取日期)
- [expireDate](#expiredate-失效日期)
- [longValid](#longvalid-长期有效)
- [lockLevel](#locklevel-锁定级别)
- [subCode](#subcode-分公司)
- [regionCode](#regioncode-区域)
- [developerCode](#developercode-开发人员)
- [address](#address-项目地址)
- [addrAbbr](#addrabbr-地址简称)
- [townshipName](#townshipname-乡镇名称)
- [coverArea](#coverarea-用地面积)
- [dynamicPrice](#dynamicprice-动态电价)
- [unitCost](#unitcost-单位成本)
- [grossMargin](#grossmargin-毛利率)
- [grossProfitMargin](#grossprofitmargin-净利润率)
- [postTaxFullInvestment](#posttaxfullinvestment-税后全投资)
- [taxInclusiveCapital](#taxinclusivecapital-含税资本金)
- [establishmentDate](#establishmentdate-成立日期)
- [profitCenterName](#profitcentername-利润中心)
- [attachmentDTOList](#attachmentdtolist-附件列表)
- [updateReason](#updatereason-变更原因)
- [closeReason](#closereason-放弃原因)

---

## 字段详情

### proName (项目名称)

```
proName
├── 组件类型: Input
├── 必填: true
├── 属性配置
│   ├── maxLength: 128
│   └── placeholder: "请输入项目名称"
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    │       └── 无特殊逻辑
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       └── 支持自动生成（autoName）
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   │   └── 无特殊逻辑
    │   └── components/approval-form/useIndex.ts
    │       └── 注释掉了，未使用
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       └── 支持自动生成（autoName）
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            └── 支持自动生成（autoName）
```

---

### area (省市区)

```
area
├── 组件类型: Cascader（省市区级联）
├── 必填: true
├── 属性配置
│   ├── options: provinceCityDistrict
│   └── fieldNames: { label: "name", value: "code", children: "children" }
├── 输出字段
│   ├── provinceCode / provinceName
│   ├── cityCode / cityName
│   └── countyCode / countyName
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### format (项目业态)

```
format
├── 组件类型: Select / Select(MultiSelect)
├── 必填: true
├── 属性配置
│   └── options
│       ├── 1: "风电"
│       ├── 2: "光伏"
│       └── 3: "储能"
├── 驱动字段
│   ├── capacityTotal
│   ├── capacityWindPower
│   ├── capacityPv
│   ├── energyScale
│   └── storageCapacity
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    │       └── 单选，驱动容量字段校验
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       └── 多选，支持业态组合（风光储）
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   │   └── 单选
    │   └── components/approval-form/useIndex.ts
    │       └── 只读展示
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       └── 单选，驱动容量字段显示/隐藏
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            └── 单选，驱动容量字段显示/隐藏
```

---

### capacityTotal (项目总容量)

```
capacityTotal
├── 组件类型: InputNumber
├── 必填: 条件必填（format=1或2时）
├── 属性配置
│   ├── precision: 2
│   ├── addonAfter: "MW"
│   └── min: 0
├── 计算逻辑
│   ├── dev-auth: capacityWindPower + capacityPv
│   ├── pre-pro-init: capacityWindPower + capacityPv
│   └── pro-init: capacityWindPower + capacityPv
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: true（默认）
    │       └── 特殊校验: 与storageCapacity互斥
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format包含1或2时
    │       └── 计算: 风电+光伏
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   │   └── 非必填，仅校验格式
    │   └── components/approval-form/useIndex.ts
    │       └── 只读展示
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format=1或2时
    │       └── 计算: 风电+光伏
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            ├── 必填: format=1或2时
            └── 计算: 风电+光伏
```

---

### capacityWindPower (风电容量)

```
capacityWindPower
├── 组件类型: InputNumber
├── 必填: 条件必填（format=1时）
├── 属性配置
│   ├── precision: 2
│   ├── addonAfter: "MW"
│   └── min: 0.01（大于0）
├── 联动效果
│   └── 变化时自动计算 capacityTotal
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format包含1时
    │       └── 隐藏: format不包含1时，值设为"0.00"
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format=1时
    │       ├── 隐藏: format=2或3时，值设为"0.00"
    │       └── 计算: 变化时更新capacityTotal
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            ├── 必填: format=1时
            ├── 隐藏: format=2或3时，值设为"0.00"
            └── 计算: 变化时更新capacityTotal
```

---

### capacityPv (光伏交流容量)

```
capacityPv
├── 组件类型: InputNumber
├── 必填: 条件必填（format=2时）
├── 属性配置
│   ├── precision: 2
│   ├── addonAfter: "MW"
│   └── min: 0.01（大于0）
├── 联动效果
│   └── 变化时自动计算 capacityTotal
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format包含2时
    │       └── 隐藏: format不包含2时，值设为"0.00"
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format=2时
    │       ├── 隐藏: format=1或3时，值设为"0.00"
    │       └── 计算: 变化时更新capacityTotal
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            ├── 必填: format=2时
            ├── 隐藏: format=1或3时，值设为"0.00"
            └── 计算: 变化时更新capacityTotal
```

---

### capacityPvDc (光伏直流容量)

```
capacityPvDc
├── 组件类型: InputNumber
├── 必填: false
├── 属性配置
│   ├── precision: 2
│   └── addonAfter: "MW"
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       └── 隐藏: format不包含2时，值设为"0.00"
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       └── 隐藏: format=1或3时，值设为"0.00"
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            └── 隐藏: format=1或3时，值设为"0.00"
```

---

### energyScale (储能规模MW)

```
energyScale
├── 组件类型: InputNumber
├── 必填: 条件必填（format=3时）
├── 属性配置
│   ├── precision: 2
│   ├── addonAfter: "MW"
│   └── min: 0.01（大于0）
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: true（默认）
    │       └── 特殊校验: 与capacityTotal互斥
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format包含3时
    │       └── 隐藏: format不包含3时
    ├── indicator
    │   └── components/add-edit-form/useIndex.ts
    │       └── 非必填，仅校验格式
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format=3时
    │       └── 隐藏: format=1或2时，值设为"0.00"
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            ├── 必填: format=3时
            └── 隐藏: format=1或2时，值设为"0.00"
```

---

### storageCapacity (储能容量MWh)

```
storageCapacity
├── 组件类型: InputNumber
├── 必填: 条件必填（format=3时）
├── 属性配置
│   ├── precision: 2
│   ├── addonAfter: "MWh"
│   └── min: 0.01（大于0）
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: true（默认）
    │       └── 特殊校验: 与capacityTotal互斥
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format包含3时
    │       └── 隐藏: format不包含3时
    ├── indicator
    │   └── components/add-edit-form/useIndex.ts
    │       └── 非必填，仅校验格式
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       ├── 必填: format=3时
    │       └── 隐藏: format=1或2时，值设为"0.00"
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            ├── 必填: format=3时
            └── 隐藏: format=1或2时，值设为"0.00"
```

---

### obtainDate (获取日期)

```
obtainDate
├── 组件类型: DatePicker
├── 必填: true
├── 属性配置
│   └── format: "YYYY-MM-DD"
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### expireDate (失效日期)

```
expireDate
├── 组件类型: DatePicker
├── 必填: 条件必填（longValid=false时）
├── 属性配置
│   └── format: "YYYY-MM-DD"
├── 联动逻辑
│   └── longValid=true时，非必填且清空校验
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       └── 校验: 必须大于obtainDate
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### longValid (长期有效)

```
longValid
├── 组件类型: Switch
├── 必填: false
├── 属性配置
│   ├── checkedChildren: "是"
│   └── unCheckedChildren: "否"
├── 联动效果
│   └── 开启时expireDate非必填，关闭时expireDate必填
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### lockLevel (锁定级别)

```
lockLevel
├── 组件类型: Select
├── 必填: true
├── 属性配置
│   └── options: 字典项 LOCK_LEVEL
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### subCode (分公司)

```
subCode
├── 组件类型: Select
├── 必填: true
├── 属性配置
│   ├── options: 异步获取companyList
│   └── placeholder: "请选择分公司"
├── 联动逻辑
│   ├── 变化时清空: regionCode, regionName, developerCode, developerName
│   └── 触发获取: regionList
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### regionCode (区域)

```
regionCode
├── 组件类型: Select
├── 必填: true
├── 属性配置
│   ├── options: 异步获取regionList（依赖subCode）
│   └── placeholder: "请选择区域"
├── 联动逻辑
│   ├── 上级: subCode
│   ├── 变化时清空: developerCode, developerName
│   └── 触发获取: developerList
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### developerCode (开发人员)

```
developerCode
├── 组件类型: Select
├── 必填: true
├── 属性配置
│   ├── options: 异步获取developerList（依赖regionCode）
│   └── placeholder: "请选择开发人员"
├── 联动逻辑
│   └── 上级: regionCode
└── 被用于
    ├── clue
    │   └── components/add-edit-form/useIndex.ts
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### address (项目地址)

```
address
├── 组件类型: Input
├── 必填: true
├── 属性配置
│   └── placeholder: "请输入项目地址"
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts（注释掉了）
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### addrAbbr (地址简称)

```
addrAbbr
├── 组件类型: Input
├── 必填: true
├── 属性配置
│   └── placeholder: "请输入地址简称"
└── 被用于
    └── pre-pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### townshipName (乡镇名称)

```
townshipName
├── 组件类型: Input
├── 必填: true
├── 属性配置
│   └── placeholder: "请输入乡镇名称"
└── 被用于
    └── pre-pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### coverArea (用地面积)

```
coverArea
├── 组件类型: InputNumber
├── 必填: false
├── 属性配置
│   └── precision: 2
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### dynamicPrice (动态电价)

```
dynamicPrice
├── 组件类型: InputNumber
├── 必填: true
├── 属性配置
│   ├── precision: 4
│   └── addonAfter: "元/kWh"
└── 被用于
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### unitCost (单位成本)

```
unitCost
├── 组件类型: InputNumber
├── 必填: true
├── 属性配置
│   ├── precision: 4
│   └── addonAfter: "元/W"
└── 被用于
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### grossMargin (毛利率)

```
grossMargin
├── 组件类型: InputNumber
├── 必填: true
├── 属性配置
│   └── precision: 4
└── 被用于
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### grossProfitMargin (净利润率)

```
grossProfitMargin
├── 组件类型: InputNumber
├── 必填: true
├── 属性配置
│   └── precision: 4
└── 被用于
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   └── components/approval-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### postTaxFullInvestment (税后全投资)

```
postTaxFullInvestment
├── 组件类型: InputNumber
├── 必填: true
├── 属性配置
│   ├── precision: 2
│   └── addonAfter: "万元"
└── 被用于
    ├── indicator
    │   └── components/add-edit-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### taxInclusiveCapital (含税资本金)

```
taxInclusiveCapital
├── 组件类型: InputNumber
├── 必填: true
├── 属性配置
│   ├── precision: 2
│   └── addonAfter: "万元"
└── 被用于
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### establishmentDate (成立日期)

```
establishmentDate
├── 组件类型: DatePicker
├── 必填: true
├── 属性配置
│   └── format: "YYYY-MM-DD"
└── 被用于
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### profitCenterName (利润中心)

```
profitCenterName
├── 组件类型: Select
├── 必填: true
├── 属性配置
│   └── options: 异步获取（依赖regionCode）
├── 联动逻辑
│   └── 根据regionCode获取利润中心列表
└── 被用于
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### attachmentDTOList (附件列表)

```
attachmentDTOList
├── 组件类型: Upload / 自定义附件组件
├── 必填: 条件必填（根据attachmentType）
├── 属性配置
│   └── 支持多文件上传
├── 附件类型映射
│   ├── 1: 开发权申请附件
│   ├── 2: 预可研报告
│   ├── 3: 土地预审意见
│   ├── 4: 其他附件（预立项）
│   ├── 30: 可研报告
│   ├── 31: 环评批复
│   ├── 32: 其他附件（立项）
│   ├── 40: 指标申报附件
│   ├── 41: 指标文件
│   ├── 42: 指标获取证明
│   ├── 43: 未获取说明
│   └── 50: 产业投资附件
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    │       └── types: ["1"]
    ├── indicator
    │   ├── components/add-edit-form/useIndex.ts
    │   │   └── types: ["40"]
    │   └── components/approval-form/useIndex.ts
    │       └── 动态: obtainStatus=1时[41,42]，=0时[41,43]
    ├── industrial
    │   └── components/add-edit-form/useIndex.ts
    │       └── types: ["50"]
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    │       └── types: ["2", "3", "4"]
    └── pro-init
        └── components/add-edit-form/useIndex.ts
            └── types: ["30", "31", "32"]
```

---

### updateReason (变更原因)

```
updateReason
├── 组件类型: TextArea
├── 必填: 条件必填（change/resubmit类型时）
├── 属性配置
│   └── placeholder: "请输入变更原因"
└── 被用于
    ├── dev-auth
    │   └── components/add-edit-form/useIndex.ts
    ├── industrial
    │   └── components/add-edit-form/useIndex.ts
    ├── pre-pro-init
    │   └── components/add-edit-form/useIndex.ts
    └── pro-init
        └── components/add-edit-form/useIndex.ts
```

---

### closeReason (放弃原因)

```
closeReason
├── 组件类型: TextArea
├── 必填: 条件必填（giveUp类型时）
├── 属性配置
│   └── placeholder: "请输入放弃原因"
└── 被用于
    └── clue
        └── components/add-edit-form/useIndex.ts
```

---

## 特殊字段（仅单个模块使用）

### 产业投资专用字段

```
totalInvestment (项目总投资)
├── 组件: InputNumber
├── 必填: true
├── 精度: 2位小数
└── 仅用于: industrial/add-edit-form/useIndex.ts

alreadyInvested (已投资金额)
├── 组件: InputNumber
├── 必填: true
├── 精度: 2位小数
└── 仅用于: industrial/add-edit-form/useIndex.ts

nowInvestment (本次投资金额)
├── 组件: InputNumber
├── 必填: true
├── 精度: 2位小数
└── 仅用于: industrial/add-edit-form/useIndex.ts

agreementContent (协议内容)
├── 组件: TextArea
├── 必填: true
└── 仅用于: industrial/add-edit-form/useIndex.ts

investmentPlanRecordList (投资计划表)
├── 组件: 动态表格
├── 字段: advanceContent, energyProgress, investmentTime, planInvestment
└── 仅用于: industrial/add-edit-form/useIndex.ts
```

### 指标确认专用字段

```
obtainStatus (指标获取状态)
├── 组件: Select
├── 选项: 0-未获取, 1-已获取
├── 驱动: 附件类型切换
└── 仅用于: indicator/approval-form/useIndex.ts

declarationMethod (申报方式)
├── 组件: Select
├── 选项: 1-独立, 2-联合
└── 仅用于: indicator/approval-form/useIndex.ts

equityRatio (股权比例)
├── 组件: InputNumber
├── 范围: 0-100
├── 精度: 2位小数
└── 仅用于: indicator/approval-form/useIndex.ts
```

---

## 附录：字段使用频率统计

| 字段名 | 使用模块数 | 使用位置 |
|--------|-----------|----------|
| proName | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| area | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| format | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| subCode | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| regionCode | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| developerCode | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| capacityTotal | 4 | clue, dev-auth, pre-pro-init, pro-init |
| obtainDate | 5 | clue, dev-auth, indicator, pre-pro-init, pro-init |
| lockLevel | 4 | dev-auth, indicator, pre-pro-init, pro-init |
| attachmentDTOList | 5 | dev-auth, indicator, industrial, pre-pro-init, pro-init |
| dynamicPrice | 3 | indicator, pre-pro-init, pro-init |
| unitCost | 3 | indicator, pre-pro-init, pro-init |
| postTaxFullInvestment | 3 | indicator, pre-pro-init, pro-init |
| addrAbbr | 1 | pre-pro-init |
| townshipName | 1 | pre-pro-init |
| taxInclusiveCapital | 1 | pro-init |
| establishmentDate | 1 | pro-init |

---

## 附件管理组件（Upload 系列）

```
attachmentDTOList（扩展）
├── 组件类型（新增可选）
│   ├── Upload（原有，单类型附件上传）
│   ├── AttachmentFileList（多类型附件管理）
│   │   ├── enableAggregation: 按类型聚合展示
│   │   ├── attachmentTypeConfigs: 类型配置（必填、文件限制）
│   │   ├── showDownloadAll: 批量下载
│   │   └── Expose: validator(), getAttachmentList()
│   ├── ProgressUpload（增强版上传）
│   │   ├── maxSize: 文件大小限制(MB)，默认 200
│   │   ├── autoFetchUrl: 自动获取回显 URL
│   │   ├── onlyShowFileList: 只显示列表
│   │   └── 延迟删除机制
│   └── UploadTable（表格形式附件管理）
│       ├── type: 'add' | 'view'
│       ├── extColumns: 扩展表格列
│       ├── maxCount: 最大上传数量
│       └── Expose: clearFile(), getFormData()
└── 选型建议
    ├── 单类型简单上传 → Upload
    ├── 多类型分类管理 → AttachmentFileList
    ├── 需要进度跟踪 → ProgressUpload
    └── 表格形式管理 → UploadTable
```

---

## 选择类组件（Select 系列）

```
选择类字段（扩展）
├── PaginationSelect（分页选择器）
│   ├── 导入: @/components/PaginationSelect
│   ├── Props
│   │   ├── func: 数据请求函数（必填）
│   │   ├── mode: 'select' | 'label'
│   │   ├── keyword: 搜索字段名，默认 'keyword'
│   │   ├── fieldNames: 选项字段映射
│   │   ├── autoFeedback: 无匹配时自动回显，默认 true
│   │   ├── feedbackOnMounted: 挂载时自动回显
│   │   └── bottomDistance: 触底加载距离
│   ├── 子组件: CurrencySelect（币种选择器，CNY 置顶）
│   └── 适用: 大数据量下拉选择，触底自动加载
├── MaterialCategoryTreeSelect（物料分类树选择）
│   ├── 导入: @/components/MaterialCategoryTreeSelect
│   ├── Props
│   │   ├── onlyLabel: 只显示标签文本
│   │   ├── showSearch: 默认 true
│   │   └── fieldNames: { value: 'id', label: 'name' }
│   └── 适用: 物料分类树形选择
├── ProjectSelectModal（项目选择弹窗）
│   ├── 导入: @/components/ProjectSelectModal
│   ├── Props
│   │   ├── type: 'customer' | 'outer'
│   │   ├── onSuccess: 选择确认回调（必填）
│   │   ├── beforeOk: 确认前拦截
│   │   └── hideColumns: 隐藏表格列
│   ├── 内嵌: BasicTable + 搜索表单
│   └── 适用: 关联选择项目（SAP编号/业态/名称搜索）
└── 选型建议
    ├── 字典选择 → DictSelect
    ├── 组织选择 → OrgSelect
    ├── 用户选择 → UserSelect / LovSelect
    ├── 大数据量分页 → PaginationSelect
    ├── 树形分类 → MaterialCategoryTreeSelect
    ├── 项目关联 → ProjectSelectModal
    └── 搜索选择 → SearchSelect
```

---

## 输入类组件（Input 系列）

```
输入类字段（扩展）
├── I18nInput（多语言输入框）
│   ├── 导入: @/components/I18nInput
│   ├── 两个子组件
│   │   ├── I18nInput.vue: value 为多语言对象 Recordable<string>
│   │   └── I18nJsonInput.tsx: value 为 JSON 字符串
│   ├── Props
│   │   ├── type: 'input' | 'textarea'
│   │   ├── inputReadonly: 只读，点击打开多语言弹窗
│   │   └── trim: 自动去除前后空格
│   └── 适用: 国际化字段输入
├── RangeNumberInput（数值范围输入）
│   ├── 导入: @/components/RangeNumberInput
│   ├── Props
│   │   ├── value: [最小值, 最大值]
│   │   ├── separator: 分隔符，默认 '-'
│   │   ├── unit: 单位文本
│   │   └── min / max: 范围限制，默认 0 / 1000
│   ├── 校验: 自动校验最小值 ≤ 最大值
│   └── 适用: 数值范围输入（容量范围、金额范围）
├── DoubleInputNumber（双数字输入框）
│   ├── 导入: @/components/common/DoubleInputNumber
│   ├── Props
│   │   ├── label: Form.Item 标签（必填）
│   │   ├── first: 第一个输入框配置（value, addon, precision）
│   │   ├── second: 第二个输入框配置（可选）
│   │   └── precision: 全局默认精度，默认 2
│   └── 适用: 两个关联数值输入（如容量+储能容量）
├── StorageScaleInput（储能规模输入）
│   ├── 导入: @/components/common/StorageScaleInput
│   ├── Props
│   │   ├── value: { energyScale?, storageCapacity? }
│   │   ├── disabled / readonly / required
│   │   └── labelWidth: 默认 '120px'
│   ├── 替代: energyScale + storageCapacity 两个独立 InputNumber
│   └── 适用: 储能业态专用
└── Period（期间选择器）
    ├── 导入: @/components/Period
    ├── Props
    │   ├── value: [年份, 期间类型, 期间值]
    │   └── onChange: 值变化回调
    ├── 期间类型: 'monthly'(月度) | 'quarterly'(季度)
    ├── 辅助函数: getPeriod(data) 格式化为可读文本
    └── 适用: 年度+季度/月度业务期间选择
```

---

## 布局类组件

```
布局辅助（扩展）
├── ModuleTitle（模块标题）
│   ├── 导入: @/components/ModuleTitle
│   ├── Props
│   │   └── title: 标题文本（必填）
│   ├── Slots: extra（右侧额外内容）
│   ├── 样式: 带左侧竖条装饰
│   └── 适用: 表单分组标题、页面区域标题
└── 适用: 所有表单页面中的分组场景
```
