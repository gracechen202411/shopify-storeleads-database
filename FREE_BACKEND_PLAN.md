# 免费自建后端 API 方案（$0 成本）

## 🎯 目标

像 SiteData 一样提供实时查询功能，但是：
- ✅ **完全免费**（利用现有资源）
- ✅ **无需额外服务器**
- ✅ **使用 Vercel + Neon**

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                     用户访问网站                              │
│                  (yoursite.vercel.app)                       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Next.js 前端（已有）                             │
│           - 搜索框：输入域名                                   │
│           - 显示：流量、广告、关键词等                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│         Vercel API Routes（Serverless Functions）            │
│                                                              │
│  /api/check-ads?domain=keychron.com                         │
│  /api/get-traffic?domain=keychron.com                       │
│  /api/get-keywords?domain=keychron.com                      │
│                                                              │
│  每个函数：                                                   │
│  1. 检查缓存（Neon DB）                                       │
│  2. 如果没有缓存，爬取数据                                     │
│  3. 保存到缓存                                                │
│  4. 返回结果                                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   数据来源（免费）                            │
│                                                              │
│  ├─ Google Ads Transparency Center（爬取）                  │
│  ├─ Google 搜索结果（爬取）                                  │
│  ├─ 网站源代码（AdSense ID）                                 │
│  └─ Neon PostgreSQL（缓存 - 免费）                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 💰 成本分析（全部免费）

| 资源 | 免费额度 | 您的使用量 | 成本 |
|------|---------|-----------|------|
| **Vercel 托管** | 100 GB 带宽/月 | < 10 GB | **$0** ✅ |
| **Vercel Functions** | 100 小时/月 | < 5 小时 | **$0** ✅ |
| **Neon PostgreSQL** | 0.5 GB 存储 | < 0.1 GB | **$0** ✅ |
| **GitHub** | 无限公开仓库 | 1 个 | **$0** ✅ |
| **域名** | 自带 .vercel.app | yoursite.vercel.app | **$0** ✅ |

**总成本：$0/月** 🎉

---

## 📁 实现步骤

### 步骤 1: 创建 API Routes

创建文件：`app/api/check-ads/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';
import { sql } from '@vercel/postgres';

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const domain = searchParams.get('domain');

  if (!domain) {
    return NextResponse.json({ error: 'Domain required' }, { status: 400 });
  }

  try {
    // 1. 检查缓存（Neon DB）
    const cached = await sql`
      SELECT * FROM ads_cache
      WHERE domain = ${domain}
      AND cached_at > NOW() - INTERVAL '7 days'
      LIMIT 1
    `;

    if (cached.rows.length > 0) {
      return NextResponse.json({
        ...cached.rows[0].data,
        source: 'cache'
      });
    }

    // 2. 如果没有缓存，爬取数据
    const adsData = await fetchGoogleAdsData(domain);

    // 3. 保存到缓存
    await sql`
      INSERT INTO ads_cache (domain, data, cached_at)
      VALUES (${domain}, ${JSON.stringify(adsData)}, NOW())
      ON CONFLICT (domain)
      DO UPDATE SET data = ${JSON.stringify(adsData)}, cached_at = NOW()
    `;

    // 4. 返回结果
    return NextResponse.json({
      ...adsData,
      source: 'fresh'
    });

  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to fetch ads data' },
      { status: 500 }
    );
  }
}

async function fetchGoogleAdsData(domain: string) {
  // 使用 Playwright 或简单的 fetch 爬取
  const url = `https://adstransparency.google.com/?region=anywhere&domain=${domain}`;

  // 方法 1: 使用 puppeteer-core + chrome-aws-lambda（Vercel 兼容）
  // 方法 2: 使用简单的 fetch + HTML 解析
  // 方法 3: 调用 SerpApi（如果有 API Key）

  // 这里简化示例
  const response = await fetch(url);
  const html = await response.text();

  // 解析 HTML 提取广告数量
  const adCountMatch = html.match(/(\d+)\s*个广告/);
  const adCount = adCountMatch ? parseInt(adCountMatch[1]) : 0;

  return {
    domain,
    has_ads: adCount > 0,
    ad_count: adCount,
    checked_at: new Date().toISOString()
  };
}
```

### 步骤 2: 创建数据库表

```sql
-- 在 Neon 中执行
CREATE TABLE IF NOT EXISTS ads_cache (
  domain TEXT PRIMARY KEY,
  data JSONB NOT NULL,
  cached_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ads_cache_time ON ads_cache(cached_at);
```

### 步骤 3: 前端调用

创建文件：`app/components/DomainChecker.tsx`

```typescript
'use client'

import { useState } from 'react'

export default function DomainChecker() {
  const [domain, setDomain] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  const checkDomain = async () => {
    setLoading(true)
    try {
      const res = await fetch(`/api/check-ads?domain=${domain}`)
      const data = await res.json()
      setResult(data)
    } catch (error) {
      console.error('Error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold mb-4">检查域名广告</h2>

      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="输入域名，如：keychron.com"
          className="flex-1 px-4 py-2 border rounded"
        />
        <button
          onClick={checkDomain}
          disabled={loading}
          className="px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          {loading ? '查询中...' : '查询'}
        </button>
      </div>

      {result && (
        <div className="bg-gray-100 p-4 rounded">
          <h3 className="font-bold mb-2">{result.domain}</h3>
          <p>广告状态: {result.has_ads ? '✅ 有广告' : '❌ 无广告'}</p>
          <p>广告数量: {result.ad_count}</p>
          <p>查询时间: {result.checked_at}</p>
          <p className="text-sm text-gray-500">
            数据来源: {result.source === 'cache' ? '缓存' : '实时查询'}
          </p>
        </div>
      )}
    </div>
  )
}
```

---

## 🚀 Vercel Serverless Functions 限制

### 免费额度：
- ✅ **100 小时执行时间/月**
- ✅ **10 秒最大执行时间/请求**
- ✅ **1024 MB 内存**
- ✅ **50 MB 代码大小**

### 对您的场景：
```
假设平均每次查询 3 秒：
100 小时 = 6000 分钟 = 360,000 秒
360,000 秒 ÷ 3 秒/查询 = 120,000 次查询/月

您的需求：
- 首次查询 6,251 个域名 = 6,251 次
- 每月增量 ~300 个 = 300 次
- 用户实时查询 ~1000 次/月

总计：< 10,000 次/月 ✅ 完全够用！
```

---

## 🎯 对比三种方案（更新版）

| 方案 | 实现方式 | 成本 | 速度 | 控制权 |
|------|---------|------|------|--------|
| **Playwright（当前）** | 本地脚本 | $0 | 5-10秒 | ✅ 完全 |
| **SerpApi** | 第三方API | $75-225 | 1-2秒 | ❌ 依赖第三方 |
| **自建 Vercel API（新）** ⭐ | Serverless | **$0** | 3-5秒 | ✅ 完全 |

---

## ✅ 推荐方案（更新）

### 🥇 最佳方案：自建 Vercel API（完全免费）

**优点：**
- ✅ **$0 成本**（利用现有资源）
- ✅ **速度快**（3-5秒，有缓存更快）
- ✅ **完全控制**（您的代码，您的数据）
- ✅ **Web 界面**（可以给朋友用）
- ✅ **自动缓存**（避免重复查询）
- ✅ **易于维护**（Vercel 自动部署）

**适合：**
- ✅ 您的项目（已有 Vercel + Neon）
- ✅ 想要 Web 界面
- ✅ 长期使用

### 📊 实施计划

#### 第1步：准备数据库（10分钟）
```sql
-- 在 Neon 执行
CREATE TABLE ads_cache (
  domain TEXT PRIMARY KEY,
  data JSONB NOT NULL,
  cached_at TIMESTAMP DEFAULT NOW()
);
```

#### 第2步：创建 API（1-2小时）
```bash
# 创建 API Routes
mkdir -p app/api/check-ads
# 复制上面的代码
```

#### 第3步：创建前端界面（1-2小时）
```bash
# 创建检查器组件
# 添加到主页面
```

#### 第4步：部署（5分钟）
```bash
git add .
git commit -m "Add domain checker API"
git push

# Vercel 自动部署 ✅
```

**总时间：2-4 小时**
**总成本：$0**

---

## 🆚 最终对比

### 检查 6,251 个店铺 + 提供 Web 查询

| 方案 | 开发时间 | 首次成本 | 月度成本 | 速度 | 推荐度 |
|------|---------|---------|---------|------|--------|
| Playwright | 0（已有） | $0 | $0 | 慢 | ⭐⭐⭐ |
| SerpApi | 1小时 | $75 | $0-75 | 最快 | ⭐⭐⭐⭐ |
| **Vercel API** | **2-4小时** | **$0** | **$0** | **快** | **⭐⭐⭐⭐⭐** |

---

## 💡 我的最终建议

**立即开始：**
1. ✅ 使用 Playwright 完成首次批量检查（免费）
2. ✅ 同时开发 Vercel API（2-4小时，免费）
3. ✅ 上线后提供 Web 查询功能给朋友测试

**长期运营：**
- ✅ 批量后台任务：继续用 Playwright
- ✅ 实时 Web 查询：使用 Vercel API
- ✅ 所有数据缓存到 Neon
- ✅ **总成本：$0/月** 🎉

---

## 🚀 下一步

想要我帮您实现这个免费的 Vercel API 方案吗？

我可以：
1. ✅ 创建 API Routes 代码
2. ✅ 设置数据库表
3. ✅ 创建前端界面
4. ✅ 配置 Vercel 部署

全部免费，2-4 小时就能完成！
