# 📊 店铺分析功能使用指南

## 概述

本指南介绍如何为店铺数据添加深度分析字段，例如：
- ✅ Google Ads 投放检测
- ✅ 社交媒体粉丝数
- ✅ 使用的技术栈/应用
- ✅ SEO数据（域名权重、反链等）
- ✅ 产品分析
- ✅ 营销工具检测

## 🚀 快速开始

### 步骤1：扩展数据库Schema

```bash
# 为数据库添加新的分析字段
psql "你的Neon连接字符串" -f extend-schema.sql
```

这会添加30+个新字段，包括：
- `has_google_ads` - 是否投放Google广告
- `technologies` - 使用的技术栈（JSON）
- `analysis_score` - 综合质量评分
- `instagram_followers` - Instagram粉丝数
- 等等...

### 步骤2：运行分析脚本

```bash
# 安装依赖
pip install requests beautifulsoup4

# 设置数据库连接
export DATABASE_URL="你的Neon连接字符串"

# 运行分析（交互模式）
python3 analyze-stores.py

# 或自动模式（批量处理）
python3 analyze-stores.py --auto
```

### 步骤3：查看分析结果

```sql
-- 查看分析统计
SELECT * FROM store_analysis_stats;

-- 查看高质量店铺
SELECT * FROM high_quality_stores LIMIT 20;

-- 查看投放Google Ads的店铺
SELECT domain, merchant_name, analysis_score
FROM stores
WHERE has_google_ads = true
ORDER BY estimated_monthly_visits DESC
LIMIT 100;
```

## 📋 可分析的数据类型

### 1. 广告营销 (Advertising)

**字段**：
- `has_google_ads` (boolean) - 是否投放Google广告
- `google_ads_detected_date` (date) - 检测到广告的日期
- `ad_keywords` (text) - 广告关键词
- `estimated_ad_budget` (varchar) - 估算广告预算

**检测方法**：
- 页面源码中的Google Ads标记
- Google Ads Transparency Center API
- ads.txt 文件分析

**示例查询**：
```sql
-- 找出投放广告且流量高的店铺
SELECT domain, merchant_name, estimated_monthly_visits
FROM stores
WHERE has_google_ads = true
  AND estimated_monthly_visits > 100000
ORDER BY estimated_monthly_visits DESC;
```

### 2. SEO数据 (SEO)

**字段**：
- `alexa_rank` (integer) - Alexa排名
- `domain_authority` (integer) - 域名权重 (0-100)
- `backlinks_count` (integer) - 反向链接数

**数据源**（需要API）：
- Moz API (Domain Authority)
- Ahrefs API (Backlinks)
- SEMrush API
- SimilarWeb API

**示例代码**：
```python
def get_domain_authority(domain):
    """使用Moz API获取域名权重"""
    # 需要Moz API密钥
    url = f"https://lsapi.seomoz.com/v2/url_metrics"
    # ... API调用
    return domain_authority
```

### 3. 社交媒体 (Social Media)

**字段**：
- `instagram_followers` (integer)
- `facebook_likes` (integer)
- `tiktok_followers` (integer)

**数据源**：
- Instagram Graph API
- Facebook Graph API
- TikTok API
- 或爬虫方案

**示例代码**：
```python
def get_instagram_followers(username):
    """获取Instagram粉丝数"""
    if not username:
        return None
    # 使用Instagram API或爬虫
    # ...
    return followers_count
```

### 4. 技术栈 (Technology Stack)

**字段**：
- `uses_shopify_plus` (boolean)
- `payment_methods` (text/JSON)
- `shipping_countries` (text/JSON)
- `technologies` (text/JSON) - Klaviyo, Judge.me等

**检测方法**：
```python
def detect_technologies(html):
    """检测店铺使用的应用和工具"""
    technologies = []

    # Shopify Plus检测
    if 'shopify-plus' in html or 'plus.shopify.com' in html:
        uses_shopify_plus = True

    # 检测常用App
    app_signatures = {
        'Klaviyo': 'klaviyo.com',
        'Judge.me': 'judge.me',
        'Yotpo': 'yotpo.com',
        'Loox': 'loox.io',
        # ... 更多
    }

    for app, signature in app_signatures.items():
        if signature in html:
            technologies.append(app)

    return technologies
```

### 5. 产品分析 (Product Analysis)

**字段**：
- `product_count` (integer) - 产品数量
- `avg_product_price` (decimal) - 平均价格
- `price_range` (varchar) - 价格区间

**获取方法**：
```python
def get_product_data(domain):
    """从Shopify API获取产品数据"""
    try:
        # Shopify stores expose product JSON at /products.json
        url = f"https://{domain}/products.json?limit=250"
        response = requests.get(url)
        data = response.json()

        products = data.get('products', [])
        product_count = len(products)

        prices = [
            float(variant['price'])
            for product in products
            for variant in product.get('variants', [])
        ]

        avg_price = sum(prices) / len(prices) if prices else None

        return {
            'product_count': product_count,
            'avg_product_price': avg_price,
            'price_range': f"${min(prices):.2f} - ${max(prices):.2f}"
        }
    except:
        return None
```

### 6. 用户体验 (UX)

**字段**：
- `has_reviews` (boolean) - 是否有评价系统
- `avg_review_score` (decimal) - 平均评分
- `page_load_speed` (integer) - 页面加载速度(ms)
- `mobile_friendly` (boolean) - 移动端友好

**检测方法**：
```python
import time

def analyze_ux(domain_url):
    """分析用户体验"""
    start = time.time()
    response = requests.get(domain_url)
    load_time = (time.time() - start) * 1000

    soup = BeautifulSoup(response.text, 'html.parser')

    # 检测评价系统
    review_indicators = ['judge.me', 'yotpo', 'reviews', 'rating']
    has_reviews = any(ind in response.text.lower() for ind in review_indicators)

    # 检测移动端友好
    viewport = soup.find('meta', {'name': 'viewport'})
    mobile_friendly = viewport is not None

    return {
        'page_load_speed': int(load_time),
        'has_reviews': has_reviews,
        'mobile_friendly': mobile_friendly
    }
```

### 7. 营销工具 (Marketing Tools)

**字段**：
- `has_email_popup` (boolean) - 邮件订阅弹窗
- `has_discount_code` (boolean) - 折扣码
- `has_live_chat` (boolean) - 在线客服
- `uses_affiliate_marketing` (boolean) - 联盟营销

**检测标记**：
```python
MARKETING_INDICATORS = {
    'email_popup': ['klaviyo', 'privy', 'justuno', 'mailchimp'],
    'live_chat': ['intercom', 'zendesk', 'tawk.to', 'gorgias', 'tidio'],
    'affiliate': ['refersion', 'tapfiliate', 'affiliatly'],
}
```

## 🔧 高级分析方案

### 方案A：批量分析（推荐）

适用于：初次分析大量店铺

```bash
# 1. 运行Python脚本
python3 analyze-stores.py --auto

# 2. 脚本会：
#    - 每批处理50个店铺
#    - 自动保存到数据库
#    - 2秒延迟避免被封
#    - 显示进度

# 3. 预计时间：
#    - 50个店铺 ≈ 3-5分钟
#    - 1000个店铺 ≈ 1-2小时
#    - 55万个店铺 ≈ 数周
```

**优化建议**：
- 使用代理IP池
- 多线程/多进程
- 分布式爬虫（Scrapy Cluster）

### 方案B：API集成

适用于：需要准确的第三方数据

```python
# 使用各种API服务
from moz import Moz
from semrush import SEMrush
from similarweb import SimilarWeb

def enrich_with_apis(domain):
    """使用API丰富数据"""
    # Moz - Domain Authority
    moz = Moz(access_id='xxx', secret_key='xxx')
    da = moz.domain_authority(domain)

    # SEMrush - 流量和关键词
    semrush = SEMrush(api_key='xxx')
    traffic = semrush.domain_overview(domain)

    # SimilarWeb - 访问统计
    sw = SimilarWeb(api_key='xxx')
    visits = sw.total_visits(domain)

    return {
        'domain_authority': da,
        'estimated_monthly_visits': visits,
        # ...
    }
```

**成本**：
- Moz API: $79-599/月
- SEMrush API: $119-449/月
- SimilarWeb: 定制价格

### 方案C：实时分析（Vercel Cron）

适用于：增量更新和新店铺

```typescript
// app/api/cron/analyze/route.ts
export async function GET(request: Request) {
  // 每次分析10个店铺
  const stores = await getStoresToAnalyze(10);

  for (const store of stores) {
    const analysis = await analyzeStore(store);
    await updateStoreAnalysis(store.id, analysis);
  }

  return NextResponse.json({ analyzed: stores.length });
}
```

配置：
```json
// vercel.json
{
  "crons": [{
    "path": "/api/cron/analyze",
    "schedule": "0 */4 * * *"  // 每4小时
  }]
}
```

## 📊 前端展示

### 更新StoreCard组件

```typescript
// components/StoreCard.tsx
export default function StoreCard({ store }: StoreCardProps) {
  return (
    <div className="border rounded-lg p-6">
      {/* 现有内容 */}

      {/* 新增：分析数据 */}
      {store.analysis_score && (
        <div className="mt-4 border-t pt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="font-semibold">📊 分析数据</h4>
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
              store.analysis_score >= 80 ? 'bg-green-100 text-green-800' :
              store.analysis_score >= 60 ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-600'
            }`}>
              得分: {store.analysis_score}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-3 text-sm">
            {/* Google Ads */}
            {store.has_google_ads !== null && (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">广告投放:</span>
                <span className={store.has_google_ads ? 'text-green-600 font-semibold' : 'text-gray-400'}>
                  {store.has_google_ads ? '✓ 是' : '✗ 否'}
                </span>
              </div>
            )}

            {/* 技术栈 */}
            {store.technologies && (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">技术栈:</span>
                <span className="font-semibold">
                  {JSON.parse(store.technologies).length} 个工具
                </span>
              </div>
            )}

            {/* 移动端友好 */}
            {store.mobile_friendly !== null && (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">移动端:</span>
                <span className={store.mobile_friendly ? 'text-green-600' : 'text-red-600'}>
                  {store.mobile_friendly ? '✓ 友好' : '✗ 不友好'}
                </span>
              </div>
            )}

            {/* 加载速度 */}
            {store.page_load_speed && (
              <div className="flex items-center gap-2">
                <span className="text-gray-600">加载速度:</span>
                <span className={
                  store.page_load_speed < 2000 ? 'text-green-600' :
                  store.page_load_speed < 4000 ? 'text-yellow-600' :
                  'text-red-600'
                }>
                  {(store.page_load_speed / 1000).toFixed(1)}s
                </span>
              </div>
            )}
          </div>

          {/* 使用的技术 */}
          {store.technologies && (
            <div className="mt-3">
              <div className="flex flex-wrap gap-2">
                {JSON.parse(store.technologies).map((tech: string, idx: number) => (
                  <span
                    key={idx}
                    className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded"
                  >
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### 添加高级筛选

```typescript
// app/page.tsx
const [filters, setFilters] = useState({
  country: '',
  minVisits: '',
  hasGoogleAds: '',
  minScore: '',  // 新增
  technologies: '',  // 新增
});

// 筛选UI
<select
  value={filters.hasGoogleAds}
  onChange={(e) => setFilters({ ...filters, hasGoogleAds: e.target.value })}
>
  <option value="">所有店铺</option>
  <option value="true">投放广告</option>
  <option value="false">未投放广告</option>
</select>

<input
  type="number"
  placeholder="最低分数"
  value={filters.minScore}
  onChange={(e) => setFilters({ ...filters, minScore: e.target.value })}
/>
```

## 🎯 实用查询示例

```sql
-- 1. 找出投放广告且使用Klaviyo的高流量店铺
SELECT domain, merchant_name, estimated_monthly_visits, analysis_score
FROM stores
WHERE has_google_ads = true
  AND technologies LIKE '%Klaviyo%'
  AND estimated_monthly_visits > 50000
ORDER BY analysis_score DESC
LIMIT 50;

-- 2. 分析技术栈最丰富的店铺
SELECT domain, merchant_name,
       jsonb_array_length(technologies::jsonb) as tech_count,
       technologies
FROM stores
WHERE technologies IS NOT NULL
ORDER BY tech_count DESC
LIMIT 20;

-- 3. 找出加载速度最快的店铺
SELECT domain, merchant_name, page_load_speed, analysis_score
FROM stores
WHERE page_load_speed IS NOT NULL
ORDER BY page_load_speed ASC
LIMIT 50;

-- 4. 营销工具使用率统计
SELECT
    COUNT(*) FILTER (WHERE has_google_ads = true) * 100.0 / COUNT(*) as ads_rate,
    COUNT(*) FILTER (WHERE has_email_popup = true) * 100.0 / COUNT(*) as popup_rate,
    COUNT(*) FILTER (WHERE has_live_chat = true) * 100.0 / COUNT(*) as chat_rate,
    COUNT(*) FILTER (WHERE mobile_friendly = true) * 100.0 / COUNT(*) as mobile_rate
FROM stores
WHERE analysis_status = 'completed';
```

## ⚡ 性能优化

### 1. 索引优化
```sql
-- 为常用筛选创建索引
CREATE INDEX idx_stores_score_visits
ON stores(analysis_score DESC, estimated_monthly_visits DESC)
WHERE analysis_status = 'completed';
```

### 2. 缓存策略
```typescript
// 使用React Query缓存
const { data } = useQuery(
  ['stores', filters],
  () => fetchStores(filters),
  { staleTime: 5 * 60 * 1000 } // 5分钟缓存
);
```

### 3. 分页优化
```sql
-- 使用cursor-based pagination代替offset
SELECT * FROM stores
WHERE id > last_seen_id
ORDER BY id
LIMIT 50;
```

## 📈 后续扩展建议

1. **机器学习**
   - 预测店铺增长趋势
   - 推荐相似店铺
   - 自动分类

2. **实时监控**
   - 价格变化追踪
   - 新产品上架提醒
   - 营销活动检测

3. **竞品分析**
   - 同类店铺对比
   - 市场份额分析
   - 价格竞争力

4. **导出和报告**
   - PDF报告生成
   - Excel导出
   - API访问

## 🆘 常见问题

**Q: 分析会不会被封IP？**
A: 脚本默认2秒延迟。建议使用代理池或限制并发。

**Q: 能否加快分析速度？**
A: 可以：
- 多进程并行
- 使用付费API代替爬虫
- 云服务器（更快网络）

**Q: 数据准确性如何？**
A:
- 技术栈检测：90%+准确
- Google Ads：80%+（可能有假阳性）
- 建议结合人工审核

**Q: 成本多少？**
A:
- 基础爬虫：免费
- API服务：$100-1000/月
- 代理IP：$50-200/月

---

开始分析你的店铺数据吧！🚀
