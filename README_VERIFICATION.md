# 30天新客户验证指南

## 快速开始

运行这个命令，按照提示操作即可：

```bash
python3 /Users/hangzhouweineng/Desktop/shopify-storeleads-database/quick_update.py
```

---

## 验证逻辑

### 定义
- **30天新客户 (new_advertiser_30d)**: 在2025-11-19到2025-12-19之间开始投放广告
- **老客户 (old_advertiser)**: 在2025-11-18或之前就已经在投放广告

### 关键日期
- **今天**: 2025-12-19
- **30天前**: 2025-11-18
- **分界点**: 2025-11-19 00:00:00

---

## 验证步骤

### 第1步: 运行脚本

```bash
python3 quick_update.py
```

### 第2步: 对每个店铺进行验证

脚本会显示店铺的Google Ads检查链接，例如:
```
店铺: joetoyss.com
检查链接: https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com
```

### 第3步: 在浏览器中检查

1. **打开链接**
2. **滚动到页面最底部**，找到最老的广告
3. **点击最老的广告**，查看详情
4. **记录"最后展示时间"** (Last shown date)

### 第4步: 输入日期

在脚本提示时，输入你看到的最老广告日期，格式: `YYYY-MM-DD`

例如:
```
最老广告的日期 (格式: YYYY-MM-DD，例如 2025-12-20): 2025-12-15
```

### 第5步: 确认分类

脚本会自动判断并建议分类:
- 如果日期 > 2025-11-18 → 建议 `new_advertiser_30d`
- 如果日期 <= 2025-11-18 → 建议 `old_advertiser`

确认后按 `y` 更新数据库。

---

## 待验证店铺

1. **joetoyss.com**
   - 当前分类: new_advertiser_30d
   - 检查链接: https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com

2. **dolcewe.com**
   - 当前分类: new_advertiser_30d
   - 检查链接: https://adstransparency.google.com/?region=anywhere&domain=dolcewe.com

---

## 注意事项

### 1. 找最老的广告
不是最新的，是最老的！滚动到页面最底部。

### 2. 理解"最后展示时间"
- Google Ads可能会持续展示旧广告
- "最后展示时间"通常能反映广告的活跃期
- 对于最老的广告，这个日期通常接近首次投放时间

### 3. 替代验证方法
如果Google Ads Transparency有日期过滤器:
- 设置结束日期为 2025-11-18
- 如果显示0个广告 → new_advertiser_30d
- 如果显示有广告 → old_advertiser

### 4. 不确定时
如果不确定，可以:
1. 查看多个广告的日期，找到最早的
2. 截图记录作为证据
3. 保守处理: 有疑问时标记为 old_advertiser

---

## 脚本说明

### quick_update.py (推荐)
交互式脚本，引导你逐步验证和更新

### check_current_status.py
查看店铺当前的数据库状态

### update_customer_types.py
批量更新脚本 (需要手动编辑代码)

### VERIFICATION_SUMMARY.md
详细的验证总结文档

---

## 数据库字段

更新会修改以下字段:
- `customer_type`: 客户类型 (new_advertiser_30d / old_advertiser)
- `ads_check_level`: 设置为 'precise_manual_verified'
- `ads_last_checked`: 更新为当前时间

---

## 示例流程

```bash
$ python3 quick_update.py

================================================================================
30天新客户验证 - 快速更新工具
================================================================================
今天: 2025-12-19
30天前: 2025-11-18

定义:
  new_advertiser_30d: 30天前无广告，现在有广告
  old_advertiser: 30天前就有广告
================================================================================

================================================================================
店铺: joetoyss.com
检查链接: https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com
================================================================================

请打开上面的链接，找到最老的广告，查看其'最后展示时间'

最老广告的日期 (格式: YYYY-MM-DD，例如 2025-12-20): 2025-12-15

建议分类: new_advertiser_30d
判断依据: 最老广告日期 2025-12-15 晚于 2025-11-18

确认更新为 new_advertiser_30d? (y/n): y
✅ 更新成功!
   旧分类: new_advertiser_30d
   新分类: new_advertiser_30d
```

---

## 遇到问题?

如果脚本出错或需要手动更新，可以直接告诉我验证结果:

```
joetoyss.com:
- 最老广告日期: 2025-12-20
- 应该分类为: new_advertiser_30d

dolcewe.com:
- 最老广告日期: 2025-11-10
- 应该分类为: old_advertiser
```

我会帮你直接更新数据库。
