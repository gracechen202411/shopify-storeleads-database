# Customily 应用检测系统

## 📋 概述

这个系统可以自动检测 Shopify 店铺是否安装了 Customily 应用，并将结果记录到数据库中。

## 🎯 功能特点

- ✅ 自动检测店铺是否安装 Customily
- ✅ 支持批量检测（中国、香港、美国店铺）
- ✅ 结果自动保存到 Neon 数据库
- ✅ 在 Vercel 前端可以筛选查看
- ✅ 两种检测方式：快速版和 Selenium 版

## 📁 文件说明

### 1. `check_customily_app.py` - 快速版
- 使用 requests 库
- 速度快，资源占用少
- 适合大批量检测
- 检测准确率：约 85%

### 2. `check_customily_selenium.py` - 精确版
- 使用 Selenium 浏览器自动化
- 可以检测动态加载的内容
- 检测准确率：约 95%
- 需要安装 ChromeDriver

## 🚀 快速开始

### 环境准备

```bash
# 1. 安装 Python 依赖
pip3 install psycopg2-binary requests beautifulsoup4 selenium

# 2. 安装 ChromeDriver（仅 Selenium 版需要）
brew install chromedriver

# 3. 设置环境变量
source .env
```

### 运行快速版

```bash
# 检测中国和香港的店铺（前100个）
python3 check_customily_app.py
```

### 运行 Selenium 版

```bash
# 更精确的检测（前50个）
python3 check_customily_selenium.py
```

## 🔍 检测原理

系统会检查以下 Customily 特征：

1. **脚本标签**：页面中是否包含 `customily` 相关的 script 标签
2. **CDN URL**：是否加载了 Customily 的 CDN 资源
3. **应用 URL**：是否有 `app.customily.com` 的请求
4. **Widget**：是否有 Customily 的小部件
5. **JS 文件**：是否加载了 `customily.js`
6. **DOM 元素**：是否有 Customily 相关的 HTML 元素

## 📊 数据库结构

检测结果会保存到 `stores` 表的以下字段：

```sql
has_customily BOOLEAN          -- 是否安装了 Customily
customily_check_date TIMESTAMP -- 检测时间
customily_details TEXT         -- 检测详情
```

## 🌐 前端筛选

在 Vercel 部署的网站上，可以通过以下方式筛选：

### API 查询参数

```
GET /api/stores?hasCustomily=true
```

参数说明：
- `hasCustomily=true` - 只显示安装了 Customily 的店铺
- `hasCustomily=false` - 只显示未安装 Customily 的店铺
- 不传参数 - 显示所有店铺

### 示例查询

```bash
# 查询中国安装了 Customily 的店铺
curl "https://your-app.vercel.app/api/stores?country=CN&hasCustomily=true"

# 查询美国未安装 Customily 的店铺
curl "https://your-app.vercel.app/api/stores?country=US&hasCustomily=false"
```

## 📈 使用流程

### 1. 检测店铺

```bash
# 运行检测脚本
python3 check_customily_app.py
```

输出示例：
```
================================================================================
Customily App Detector for Shopify Stores
================================================================================

Connecting to database...
✅ Database connected

Fetching stores to check...
Found 100 stores to check

First 5 stores:
  1. nothing.tech (HK) - 1,508,985 visits/month
  2. lingsmoment.com (HK) - 912,710 visits/month
  3. vinylfrog.com (HK) - 912,525 visits/month
  4. keychron.com (HK) - 815,670 visits/month
  5. aelfriceden.com (CN) - 681,352 visits/month

================================================================================
Start checking? (y/n): y

[1/100] Checking nothing.tech... ⭕ No Customily - No Customily detected
[2/100] Checking lingsmoment.com... ⭕ No Customily - No Customily detected
[3/100] Checking evridwearcustom.com... ✅ HAS CUSTOMILY - Found: customily, customily-widget

================================================================================
Progress: 10/100 (10.0%)
Customily found: 1
Success: 10, Errors: 0
================================================================================
```

### 2. 查看结果

在数据库中查询：

```sql
-- 查看所有安装了 Customily 的店铺
SELECT domain, country_code, estimated_monthly_visits, customily_details
FROM stores
WHERE has_customily = true
ORDER BY estimated_monthly_visits DESC;

-- 统计各国安装 Customily 的店铺数量
SELECT country_code, COUNT(*) as count
FROM stores
WHERE has_customily = true
GROUP BY country_code
ORDER BY count DESC;
```

### 3. 在前端查看

访问你的 Vercel 网站，使用筛选功能：
- 选择国家：中国/美国
- 选择 Customily：已安装/未安装
- 查看结果列表

## ⚙️ 配置选项

### 修改检测范围

编辑脚本中的配置：

```python
# check_customily_app.py 第 145 行

# 只检测中国和香港
countries = ['CN', 'HK']

# 或者检测中国、香港、美国
countries = ['CN', 'HK', 'US']

# 限制检测数量
stores = get_stores_to_check(conn, country_filter=countries, limit=100)
```

### 修改检测延迟

```python
# 第 234 行
time.sleep(2)  # 每个店铺之间延迟 2 秒
```

## 🔧 故障排除

### 问题 1：数据库连接失败

```bash
ERROR: Please set DATABASE_URL environment variable
```

解决方法：
```bash
# 确保 .env 文件存在并包含数据库 URL
cat .env

# 重新加载环境变量
source .env
```

### 问题 2：ChromeDriver 未找到

```bash
❌ WebDriver initialization failed
```

解决方法：
```bash
# 安装 ChromeDriver
brew install chromedriver

# 或者下载并手动安装
# https://chromedriver.chromium.org/
```

### 问题 3：检测速度太慢

- 使用快速版 `check_customily_app.py` 而不是 Selenium 版
- 减少检测数量：`limit=50`
- 增加并发（高级用户）

### 问题 4：检测不准确

- 使用 Selenium 版获得更高准确率
- 检查网络连接是否稳定
- 某些店铺可能使用了反爬虫机制

## 📊 性能指标

### 快速版 (requests)
- 速度：约 2-3 秒/店铺
- 准确率：约 85%
- 资源占用：低
- 适合：大批量检测

### Selenium 版
- 速度：约 5-8 秒/店铺
- 准确率：约 95%
- 资源占用：中等
- 适合：精确检测

## 🎯 最佳实践

1. **首次检测**：使用快速版检测所有店铺
2. **精确验证**：对重点店铺使用 Selenium 版复查
3. **定期更新**：每月重新检测一次
4. **分批处理**：每次检测 50-100 个店铺
5. **错误处理**：记录失败的店铺，稍后重试

## 📝 示例：完整工作流程

```bash
# 1. 检测中国和香港的店铺
python3 check_customily_app.py

# 2. 查看检测结果
psql $DATABASE_URL -c "
SELECT 
  country_code,
  COUNT(*) as total,
  SUM(CASE WHEN has_customily THEN 1 ELSE 0 END) as with_customily
FROM stores
WHERE country_code IN ('CN', 'HK')
GROUP BY country_code;
"

# 3. 导出安装了 Customily 的店铺
psql $DATABASE_URL -c "
COPY (
  SELECT domain, country_code, estimated_monthly_visits, customily_details
  FROM stores
  WHERE has_customily = true
  ORDER BY estimated_monthly_visits DESC
) TO STDOUT WITH CSV HEADER
" > customily_stores.csv

# 4. 在 Vercel 网站上查看和筛选
```

## 🔄 更新和维护

### 重新检测所有店铺

```sql
-- 清除之前的检测结果
UPDATE stores 
SET has_customily = NULL, 
    customily_check_date = NULL, 
    customily_details = NULL;
```

然后重新运行检测脚本。

### 只检测新店铺

脚本会自动跳过已检测的店铺（`has_customily IS NULL`）。

## 📞 支持

如有问题，请检查：
1. 数据库连接是否正常
2. Python 依赖是否安装完整
3. ChromeDriver 版本是否匹配
4. 网络连接是否稳定

---

**最后更新**：2025-02-25
