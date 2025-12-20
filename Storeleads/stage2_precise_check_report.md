# Stage 2 精确检查报告 - Precise Check Report

**执行日期**: 2025-12-19
**检查类型**: 精确检查 (Precise Check)
**目标**: 验证 suspected_new_advertiser 是否为30天内的新广告主

---

## 📊 执行概述 (Execution Summary)

### 检查方法
- **Stage 1** (快速检查): 仅检查广告数量 (< 10个广告 = 疑似新广告主)
- **Stage 2** (精确检查): 点击第一个广告，提取"最后展示时间"，判断是否在30天内

### 时间基准
- **今天日期**: 2025-12-19
- **30天前**: 2025-11-19
- **判断标准**: last_seen_date > 2025-11-19 → new_advertiser_30d

---

## 🎯 检查结果 (Check Results)

### 待检查店铺 (3个)
从数据库中筛选出 `customer_type = 'suspected_new_advertiser'` 的店铺：

| 域名 | 广告数量 | Stage 1 分类 |
|------|----------|--------------|
| dokidokicos.com | 1 ads | suspected_new_advertiser |
| dolcewe.com | 4 ads | suspected_new_advertiser |
| joetoyss.com | 6 ads | suspected_new_advertiser |

---

## ✅ 精确检查结果 (Precise Check Results)

### 1. dokidokicos.com
- **广告数量**: 1 个广告
- **最后展示时间**: 2025-10-27
- **距离今天**: 53 天
- **最终分类**: ❌ **old_advertiser** (超过30天)

**详情**:
```
URL: https://adstransparency.google.com/?region=anywhere&domain=dokidokicos.com
第一个广告: AR10942234166510485505/CR14431286085327781889
广告主: BlueVision Interactive Limited
```

---

### 2. dolcewe.com ⭐
- **广告数量**: 4 个广告
- **最后展示时间**: 2025-12-18
- **距离今天**: 1 天
- **最终分类**: ✅ **new_advertiser_30d** (30天内的新广告主)

**详情**:
```
URL: https://adstransparency.google.com/?region=anywhere&domain=dolcewe.com
第一个广告: AR00911517645054935041/CR08466194969294536705
广告主: 苏州赛贸达信息科技有限公司
```

---

### 3. joetoyss.com ⭐
- **广告数量**: 6 个广告
- **最后展示时间**: 2025-12-18
- **距离今天**: 1 天
- **最终分类**: ✅ **new_advertiser_30d** (30天内的新广告主)

**详情**:
```
URL: https://adstransparency.google.com/?region=anywhere&domain=joetoyss.com
第一个广告: AR05051117076102512641/CR04401149968572743681
广告主: Naja Marketing Ltda
```

---

## 📈 最终统计 (Final Statistics)

### 按客户类型分类

| 客户类型 | 数量 | 占比 | 店铺列表 |
|---------|------|------|---------|
| **new_advertiser_30d** | 2 | 66.7% | dolcewe.com, joetoyss.com |
| **old_advertiser** | 1 | 33.3% | dokidokicos.com |

### 全数据库统计

| 客户类型 | 店铺数量 |
|---------|---------|
| never_advertised | 3 |
| new_advertiser_30d | 2 |
| old_advertiser | 1 |
| suspected_new_advertiser | 0 (全部已完成精确检查) |

---

## 🎯 重要发现 (Key Findings)

1. **验证准确率**: 66.7% (2/3) 的疑似新广告主确实是30天内的新广告主
2. **误判案例**: dokidokicos.com 虽然只有1个广告，但最后展示时间是53天前，属于旧广告主
3. **新广告主特征**:
   - dolcewe.com 和 joetoyss.com 都是昨天 (2025-12-18) 还在展示广告
   - 都属于活跃的广告主
   - 广告数量: 4-6 个

---

## 💾 数据库更新 (Database Updates)

所有店铺已更新以下字段：
- `customer_type`: 根据最后展示时间更新为 'new_advertiser_30d' 或 'old_advertiser'
- `ads_last_seen_date`: 新增字段，记录最后展示时间
- `ads_check_level`: 更新为 'precise' (精确检查)
- `ads_last_checked`: 更新为当前时间

### 数据验证示例
```sql
SELECT domain, customer_type, google_ads_count, ads_last_seen_date, ads_check_level
FROM stores
WHERE domain IN ('dokidokicos.com', 'dolcewe.com', 'joetoyss.com');
```

**结果**:
```
dokidokicos.com  | old_advertiser      | 1 | 2025-10-27 | precise
dolcewe.com      | new_advertiser_30d  | 4 | 2025-12-18 | precise
joetoyss.com     | new_advertiser_30d  | 6 | 2025-12-18 | precise
```

---

## 🔧 技术实现 (Technical Implementation)

### 工具和方法
- **工具**: Selenium WebDriver (Chrome headless mode)
- **页面访问**: https://adstransparency.google.com/
- **日期提取**: 正则表达式匹配 "最后展示时间：YYYY年M月D日"
- **分类逻辑**: 比较最后展示时间与30天前的日期

### 关键代码片段
```python
# 时间基准
TODAY = datetime(2025, 12, 19)
THIRTY_DAYS_AGO = TODAY - timedelta(days=30)  # 2025-11-19

# 分类逻辑
def classify_advertiser(last_shown_date):
    if last_shown_date > THIRTY_DAYS_AGO:
        return 'new_advertiser_30d'
    else:
        return 'old_advertiser'

# 日期提取正则
pattern = r'最后展示时间[：:]\s*(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日'
```

---

## 📋 下一步行动 (Next Steps)

### 建议
1. **监控新广告主**: dolcewe.com 和 joetoyss.com 是活跃的新广告主，可以跟踪他们的广告策略
2. **定期复查**: 建议每30天重新检查一次，更新分类
3. **扩展检查**: 如果有更多 'suspected_new_advertiser'，可以批量运行 Stage 2

### 自动化脚本
已创建完整的自动化脚本：
- **Stage 1**: `/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/stage1_fast_check.py`
- **Stage 2**: `/Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads/stage2_precise_check.py`

---

## 🎉 结论 (Conclusion)

Stage 2 精确检查成功识别出 **2个真正的30天内新广告主**：
- ✅ **dolcewe.com** - 4个广告，最后展示于昨天
- ✅ **joetoyss.com** - 6个广告，最后展示于昨天

这两个店铺是值得关注的目标客户！

---

**报告生成时间**: 2025-12-19 11:52:53
**检查耗时**: 约 30 秒 (每个店铺 ~10秒)
**成功率**: 100% (3/3 店铺成功提取日期)
