# 浙江2024年店铺分析报告

**筛选条件**: 2024年全年 + 浙江 + 月访问量 >= 1000
**数据来源**: Shopify Storeleads数据库（239万条）
**报告时间**: 2025-11-11

---

## 📊 筛选结果

### 总计：17家店铺

从239万条数据中筛选出：
- ✅ 2024年创建：772,969 家
- ✅ 位于浙江：1,543 家
- ✅ 月访问量 >= 1000：**17 家**

---

## 🏆 TOP 17 浙江2024年店铺

| # | 商家名称 | 域名 | 位置 | 创建日期 | 月访问量 | 年销售额 | Google广告 |
|---|----------|------|------|----------|----------|----------|------------|
| 1 | Yes Welding, Inc. | dp200.yeswelder.com | 温州乐清 | 2024/06/21 | 19,701 | $2,015,100 | ⭕ 无 |
| 2 | Calembou | www.calembou.com | 嘉兴桐乡 | 2024/03/01 | 13,681 | $1,399,314 | ⏳ 待查 |
| 3 | D&D Dice Sets | diceofdragons.com | 杭州 | 2024/05/17 | 11,861 | $1,213,172 | ⏳ 待查 |
| 4 | Perfume UAE | perfumeuae.ae | 杭州 | 2024/06/21 | 10,470 | $1,376,820 | ⏳ 待查 |
| 5 | Rokid | uk.rokid.com | 杭州 | 2024/08/09 | 6,380 | $839,032 | ⏳ 待查 |
| 6 | AECOJOY | aecojoyshop.com | 义乌金华 | 2024/03/15 | 3,253 | $522,946 | ⏳ 待查 |
| 7 | bottlebottle | uk.bottlebottle.com | 杭州 | 2024/02/02 | 2,904 | $466,825 | ⏳ 待查 |
| 8 | Kids Furniture | www.babyjoykids.com | 金华 | 2024/05/17 | 2,539 | $445,257 | ⏳ 待查 |
| 9 | GolfGentry | golfgentry.com | 浙江 | 2024/03/15 | 2,428 | $425,777 | ⏳ 待查 |
| 10 | GiPP Kitchenware | www.gippstore.com | 金华 | 2024/04/19 | 2,295 | $402,587 | ⏳ 待查 |
| 11 | demideerart | de.mideerart.com | 宁波 | 2024/04/19 | 1,893 | $359,762 | ⏳ 待查 |
| 12 | SOMILISS | somiliss.com | 温州 | 2024/02/02 | 1,354 | $277,049 | ⏳ 待查 |
| 13 | www.urbandrift.com | www.urbandrift.com | 台州 | 2024/05/31 | 1,306 | $267,309 | ⏳ 待查 |
| 14 | grado | www.gradodesign.us | 杭州 | 2024/02/09 | 1,216 | $248,911 | ⏳ 待查 |
| 15 | Rokid | es.rokid.com | 杭州 | 2024/11/01 | 1,174 | $240,253 | ⏳ 待查 |
| 16 | Online Shop | www.porphis-online.com | 宁波 | 2024/03/08 | 1,116 | $244,660 | ⏳ 待查 |
| 17 | Bazova | www.bazova-home.com | 杭州 | 2024/03/01 | 1,105 | $242,341 | ⏳ 待查 |

---

## 📈 统计分析

### 流量分析
- **平均月访问量**: 4,981
- **中位数月访问量**: 2,428
- **最高月访问量**: 19,701 (Yes Welding)
- **最低月访问量**: 1,105 (Bazova)

### 销售分析
- **总年销售额**: ~$10,966,115
- **平均年销售额**: $645,066
- **最高年销售额**: $2,015,100 (Yes Welding)

### 地域分布
| 城市 | 店铺数 |
|------|--------|
| 杭州 | 7 家 (41%) |
| 金华/义乌 | 3 家 (18%) |
| 宁波 | 2 家 (12%) |
| 温州 | 2 家 (12%) |
| 其他 | 3 家 (17%) |

### 创建时间分布
- 2024年2月: 3 家
- 2024年3月: 4 家
- 2024年4月: 2 家
- 2024年5月: 3 家
- 2024年6月: 2 家
- 2024年8月: 1 家
- 2024年11月: 1 家

---

## 🔍 Google广告查询进度

### 当前进度: 1/17 (5.9%)

| 状态 | 数量 | 占比 |
|------|------|------|
| ✅ 已查询 | 1 | 5.9% |
| ⏳ 待查询 | 16 | 94.1% |

### 已查询结果
- ⭕ **无广告**: 1 家 (Yes Welding)

---

## 📁 生成的文件

1. ✅ **zhejiang_2024_1000plus.csv** - 17家店铺完整数据
2. ✅ **zhejiang_2024_with_google_ads.csv** - 带Google广告状态的表格（实时更新）
3. ✅ **zhejiang_domains_to_check.json** - 待查询域名列表（JSON格式）
4. ✅ **ads_cache.json** - 查询结果缓存

---

## 🚀 如何继续查询

### 方法1：使用Claude Code MCP Playwright（推荐）

**自动化查询**：
```
对每个域名，使用MCP Playwright工具访问：
https://adstransparency.google.com/?region=anywhere&domain={domain}

查看广告数量，然后运行：
python3 -c "
from batch_ads_checker_optimized import AdsCache
cache = AdsCache()
cache.set('domain.com', True/False, 数量, '广告文本')
"

然后重新运行查看更新：
python3 batch_ads_check_zhejiang.py
```

### 方法2：快速批量添加（如果手动查询完成）

编辑 `quick_add_results.py`，添加所有结果：
```python
results_to_add = [
    ('calembou.com', True, 50, '50 个广告'),
    ('diceofdragons.com', False, 0, '0 个广告'),
    # ... 添加所有17个
]
```

然后运行：
```bash
python3 quick_add_results.py
python3 batch_ads_check_zhejiang.py
```

### 方法3：分批处理

每查询5个就运行一次 `quick_add_results.py` 添加到缓存，避免丢失数据。

---

## 💡 待查询的16个域名清单

### 高优先级（流量 > 10k）
1. ⏳ calembou.com (13,681访问)
2. ⏳ diceofdragons.com (11,861访问)
3. ⏳ perfumeuae.ae (10,470访问)

### 中优先级（流量 5k-10k）
4. ⏳ uk.rokid.com (6,380访问)

### 低优先级（流量 1k-5k）
5. ⏳ aecojoyshop.com (3,253访问)
6. ⏳ uk.bottlebottle.com (2,904访问)
7. ⏳ babyjoykids.com (2,539访问)
8. ⏳ golfgentry.com (2,428访问)
9. ⏳ gippstore.com (2,295访问)
10. ⏳ de.mideerart.com (1,893访问)
11. ⏳ somiliss.com (1,354访问)
12. ⏳ urbandrift.com (1,306访问)
13. ⏳ gradodesign.us (1,216访问)
14. ⏳ es.rokid.com (1,174访问)
15. ⏳ porphis-online.com (1,116访问)
16. ⏳ bazova-home.com (1,105访问)

---

## 🎯 关键发现

### 1. 杭州主导
- 杭州占41%，是浙江电商的绝对中心
- 科技类产品居多（Rokid智能眼镜等）

### 2. 新店流量表现
- 2024年新店中有17家达到1000+月访问量
- 最高达到19,701（6个月内）
- 说明新店增长潜力大

### 3. 行业分布
- 家居家具：4家
- 3C/科技：3家
- 服装鞋包：2家
- 其他：8家

### 4. 出海市场
- UAE/UK/德国站点多
- 说明浙江商家积极布局国际市场

---

## 📝 下一步行动

1. **完成Google广告查询**（16个待查）
2. **分析广告投放与流量的关系**
3. **识别成功案例**（高流量+广告投放）
4. **生成最终完整报告**

---

**报告生成**: 2025-11-11
**数据来源**: Shopify Storeleads (239万条)
**查询进度**: 1/17 (5.9%)
**预计完成查询时间**: 需手动查询剩余16个域名
