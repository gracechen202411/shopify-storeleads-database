# Vercel API 真实情况分析

## ⚠️ 重要更正：我之前的说法不准确

让我诚实地告诉您 Vercel Serverless Functions 的真实情况。

---

## 🚫 Vercel 免费套餐的严格限制

### 关键限制（Hobby Plan - 免费）：

| 限制项 | 免费额度 | 您的需求 | 是否够用 |
|--------|---------|---------|---------|
| **执行时间上限** | **10 秒/请求** ⚠️ | 爬取需要 15-20 秒 | ❌ **不够** |
| **总执行时间** | 100 小时/月 | 批量查询可能超 | ⚠️ **勉强** |
| **内存限制** | 1024 MB | Playwright 需要更多 | ⚠️ **勉强** |
| **部署大小** | 50 MB | 包含 Chromium 会超 | ❌ **不够** |
| **冷启动延迟** | 1-3 秒 | 首次调用慢 | ⚠️ **影响体验** |
| **并发请求** | 无限制 | 可以并发 | ✅ **够用** |

### 🔴 致命问题：10 秒超时限制

```
Google Ads Transparency 页面加载：
- 页面导航：2-3 秒
- 等待元素加载：3-5 秒
- 解析数据：1-2 秒
- 总计：6-10 秒（边缘情况会超时）

❌ Vercel 免费版：10 秒后强制终止
❌ 如果网络慢一点，就会失败
```

---

## 💡 真实对比（重新修正）

### 方案对比表（诚实版）

| 方案 | 速度 | 成本 | 稳定性 | 限制 | 推荐度 |
|------|------|------|--------|------|--------|
| **本地 Playwright** | 5-10秒 | $0 | 90% | 需要本地运行 | ⭐⭐⭐⭐ |
| **SerpApi** | 1-2秒 | $75首次 | 99.9% | 需付费 | ⭐⭐⭐⭐⭐ |
| **Vercel Function + Playwright** | 8-15秒 | $0 | 60% | **10秒超时** ❌ | ⭐⭐ |
| **Vercel Function + SerpApi** | 2-3秒 | $75 | 95% | 还是要付费 | ⭐⭐⭐ |

---

## 🤔 为什么 Vercel API 不是最佳方案？

### 问题 1: 浏览器自动化在 Serverless 里很难

```javascript
// 在 Vercel Function 里运行 Playwright/Puppeteer：

❌ 问题：
1. 需要安装 Chromium（~300MB）→ 超过 50MB 部署限制
2. 需要特殊包 @sparticuz/chromium（增加复杂度）
3. 冷启动慢（首次加载 Chromium 需要 2-5 秒）
4. 10 秒超时限制容易触发

✅ 解决方案：
- 使用 puppeteer-core + @sparticuz/chromium
- 但是：复杂、不稳定、容易超时
```

### 问题 2: 如果调用 SerpApi，为什么不直接本地调用？

```python
# 方案 A: Vercel Function → SerpApi
用户请求 → Vercel Function → SerpApi → 返回
延迟：     1-2秒         +   1秒    = 2-3秒

# 方案 B: 直接调用 SerpApi（更简单）
用户请求 → 直接 SerpApi → 返回
延迟：         1秒

结论：没必要通过 Vercel 中转！
```

### 问题 3: 冷启动延迟

```
首次请求：
- Vercel 启动容器：1-2 秒
- 加载依赖：0.5-1 秒
- 执行代码：5-10 秒
- 总计：6.5-13 秒 ⚠️ 可能超时

后续请求（热启动）：
- 执行代码：5-10 秒
- 总计：5-10 秒 ✅ 勉强可以
```

---

## ✅ Vercel 适合做什么？

### Vercel 的优势场景：

```
✅ 1. 展示现有数据（数据库查询）
   - 从 Neon 读取已有的广告数据
   - 速度：< 1 秒
   - 完美适合！

✅ 2. 简单 API 调用（转发请求）
   - 调用第三方 API
   - 速度：1-2 秒
   - 可以使用

❌ 3. 浏览器自动化（爬取数据）
   - 运行 Playwright/Selenium
   - 速度：8-15 秒（可能超时）
   - 不推荐！
```

---

## 🎯 重新推荐方案

### 方案 1: 本地 Playwright + Vercel 展示（推荐）⭐⭐⭐⭐⭐

```
架构：
┌─────────────────────────────────────┐
│  定时任务（本地或 GitHub Actions）     │
│  - 使用 Playwright 批量检查          │
│  - 更新 Neon 数据库                 │
│  - 每天/每周运行一次                 │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Neon PostgreSQL                    │
│  - 存储所有广告数据                  │
│  - 缓存查询结果                      │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│  Vercel Next.js                     │
│  - 展示数据（从数据库读取）          │
│  - 提供搜索/筛选界面                 │
│  - 速度：< 1 秒 ✅                   │
└─────────────────────────────────────┘
```

**优点：**
- ✅ **完全免费**
- ✅ **速度快**（读数据库 < 1 秒）
- ✅ **无超时问题**
- ✅ **稳定可靠**

**实现：**
```typescript
// app/api/get-ads/route.ts
export async function GET(request: NextRequest) {
  const domain = request.nextUrl.searchParams.get('domain');

  // 只是从数据库读取，速度很快
  const result = await sql`
    SELECT * FROM stores
    WHERE domain = ${domain}
  `;

  return NextResponse.json(result.rows[0]);
}
```

---

### 方案 2: GitHub Actions 定时爬取（完全免费）⭐⭐⭐⭐

```yaml
# .github/workflows/check-ads.yml
name: Check Google Ads
on:
  schedule:
    - cron: '0 0 * * *'  # 每天运行
  workflow_dispatch:  # 手动触发

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install playwright psycopg2-binary
          playwright install chromium

      - name: Run ads checker
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
        run: python Storeleads/batch_check_all.py
```

**优点：**
- ✅ **完全免费**（GitHub Actions 2000 分钟/月）
- ✅ **无超时限制**（最长 6 小时）
- ✅ **自动化运行**
- ✅ **可以用 Playwright**

**缺点：**
- ❌ 不是实时查询（定时更新）

---

### 方案 3: SerpApi（付费但最快）⭐⭐⭐⭐⭐

```python
# 直接使用 SerpApi，不需要 Vercel
from serpapi_ads_checker import SerpApiAdsChecker

checker = SerpApiAdsChecker(api_key="your_key")
result = checker.check_domain_ads("keychron.com")

# 速度：1-2 秒
# 成本：$75/月（5000 次查询）
```

**优点：**
- ✅ **最快**（1-2 秒）
- ✅ **最稳定**（99.998%）
- ✅ **无需维护**

**缺点：**
- ❌ 需要付费

---

## 📊 最终推荐（诚实版）

### 您的情况（6251 个店铺）：

#### 🥇 推荐方案：本地 Playwright + Vercel 展示

```
1. 批量检查（后台任务）
   → 本地运行 Playwright
   → 或使用 GitHub Actions（免费）
   → 每天/每周更新一次

2. Web 展示（实时查询）
   → Vercel Next.js（已有）
   → 从 Neon 数据库读取（速度快）
   → 用户体验好

总成本：$0/月 ✅
总时间：首次检查 14-29 小时（可以后台运行）
```

#### 🥈 备选方案：SerpApi 快速完成

```
1. 首次批量检查
   → 使用 SerpApi Starter Plan ($75)
   → 2-3 小时完成 6251 个店铺

2. 后续增量检查
   → 每月 ~300 个新店铺
   → 使用 SerpApi Free Plan（100 次/月）+ Playwright（200 次）

总成本：首月 $75，之后 $0
```

---

## 💡 关于 Vercel 的真实定位

### Vercel 擅长的：
- ✅ 前端部署（Next.js）
- ✅ 静态网站托管
- ✅ 简单 API（< 10 秒）
- ✅ 数据库查询和展示
- ✅ 边缘计算（CDN）

### Vercel 不擅长的：
- ❌ 长时间运行任务（> 10 秒）
- ❌ 浏览器自动化（Playwright/Selenium）
- ❌ 大规模数据处理
- ❌ 定时任务（需要外部触发）

---

## 🎯 总结：我的诚实建议

**别用 Vercel Function 做爬虫！**

**正确用法：**
```
Vercel = 展示层（前端 + 简单 API）
本地/GitHub Actions = 数据采集层（Playwright 爬虫）
Neon = 数据存储层
```

**您已经对接了 Vercel，这是正确的！**
- ✅ 用来展示店铺数据
- ✅ 用来提供搜索/筛选功能
- ❌ 不要用来跑 Playwright 爬虫

**我之前错误地说 Vercel API 更快，实际上：**
- Vercel 读数据库 → 快（< 1 秒）✅
- Vercel 跑爬虫 → 慢且容易超时（8-15 秒）❌

---

## 🚀 下一步建议

1. ✅ **保持现状**：Vercel 用于展示数据（已经很好）
2. ✅ **批量爬取**：本地运行 Playwright 或用 GitHub Actions
3. ✅ **可选升级**：如果需要快速完成首次检查，考虑 SerpApi

需要我帮您设置 GitHub Actions 定时爬取吗？这样可以完全免费自动化！
