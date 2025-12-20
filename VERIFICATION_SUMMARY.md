# 30天新客户验证总结

## 背景

需要重新验证两个店铺的分类，确认它们在30天前（2025-11-18）是否已有Google广告。

---

## 正确的定义

**30天新客户 (new_advertiser_30d):**
- 30天前（2025-11-18）**没有**广告
- 现在（2025-12-19）**有**广告
- = 在过去30天内开始投放广告

**老客户 (old_advertiser):**
- 30天前（2025-11-18）**已经有**广告
- = 投放广告已超过30天

---

## 待验证店铺

### 1. joetoyss.com

**当前数据库状态:**
- 客户类型: `new_advertiser_30d`
- 检查级别: `precise`
- 最后检查: 2025-12-19 03:52:53
- 类别: /Apparel

**验证链接:**
https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com

**验证步骤:**
1. 打开上面的链接
2. 滚动到页面最底部，找到最老的广告
3. 点击最老的广告，查看"最后展示时间"
4. 判断:
   - 如果最老广告的"最后展示时间" >= 2025-11-19 → `new_advertiser_30d` ✅ (正确)
   - 如果最老广告的"最后展示时间" <= 2025-11-18 → `old_advertiser` ❌ (需要修正)

**验证结果:**
- [ ] 已验证
- 最老广告日期: __________
- 正确分类: __________
- 证据说明: __________

---

### 2. dolcewe.com

**当前数据库状态:**
- 客户类型: `new_advertiser_30d`
- 检查级别: `precise`
- 最后检查: 2025-12-19 03:52:38
- 类别: /Home & Garden

**验证链接:**
https://adstransparency.google.com/?region=anywhere&domain=dolcewe.com

**验证步骤:**
1. 打开上面的链接
2. 滚动到页面最底部，找到最老的广告
3. 点击最老的广告，查看"最后展示时间"
4. 判断:
   - 如果最老广告的"最后展示时间" >= 2025-11-19 → `new_advertiser_30d` ✅ (正确)
   - 如果最老广告的"最后展示时间" <= 2025-11-18 → `old_advertiser` ❌ (需要修正)

**验证结果:**
- [ ] 已验证
- 最老广告日期: __________
- 正确分类: __________
- 证据说明: __________

---

## 如何更新数据库

### 方法1: 使用Python脚本

1. 编辑文件: `/Users/hangzhouweineng/Desktop/shopify-storeleads-database/update_customer_types.py`

2. 找到 `STORE_RESULTS` 字典，更新为实际验证结果:

```python
STORE_RESULTS = {
    'joetoyss.com': {
        'customer_type': 'new_advertiser_30d',  # 或 'old_advertiser'
        'evidence': 'First ad last seen: 2025-12-20',  # 实际日期
        'had_ads_30_days_ago': False,  # 或 True
        'has_ads_now': True
    },
    'dolcewe.com': {
        'customer_type': 'old_advertiser',  # 或 'new_advertiser_30d'
        'evidence': 'First ad last seen: 2025-11-10',  # 实际日期
        'had_ads_30_days_ago': True,  # 或 False
        'has_ads_now': True
    }
}
```

3. 运行脚本:
```bash
python3 /Users/hangzhouweineng/Desktop/shopify-storeleads-database/update_customer_types.py
```

### 方法2: 直接告诉我结果

只需告诉我每个店铺的验证结果，格式如下:

```
joetoyss.com:
- 最老广告日期: 2025-12-20
- 分类: new_advertiser_30d
- 证据: First ad last seen 2025-12-20, no ads before 2025-11-19

dolcewe.com:
- 最老广告日期: 2025-11-10
- 分类: old_advertiser
- 证据: Had ads on 2025-11-18, first ad last seen 2025-11-10
```

我会帮你更新数据库。

---

## 重要提醒

1. **关键是找最老的广告**，不是最新的！
2. **分界日期是 2025-11-19**:
   - 2025-11-19或之后首次出现 → 新客户
   - 2025-11-18或之前就有 → 老客户
3. **"最后展示时间"可能混淆**:
   - 我们要看的是广告**首次出现**的时间
   - 通常最老的广告的"最后展示时间"能反映这个信息
4. **如果Google Ads Transparency有日期过滤器**:
   - 尝试筛选到2025-11-18看是否有广告
   - 这是最准确的方法

---

## 验证完成后

请在上面的"验证结果"部分填写:
- [x] 已验证
- 最老广告日期: (实际看到的日期)
- 正确分类: (根据日期判断)
- 证据说明: (简短描述你看到的信息)

然后使用上面的"方法1"或"方法2"更新数据库。
