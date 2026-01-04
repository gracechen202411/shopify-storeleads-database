# SerpApi 集成指南

## 📌 什么是 SerpApi？

SerpApi 是一个专业的搜索引擎 API 服务，提供 Google Ads Transparency Center 的数据访问接口。

**优势：**
- ✅ **速度快** - 纯 API 调用，无需浏览器
- ✅ **稳定** - 99.998% 正常运行时间
- ✅ **简单** - 无需处理浏览器自动化、验证码等问题
- ✅ **结构化数据** - 返回 JSON 格式，易于解析
- ✅ **免费套餐** - 每月 100 次免费查询

## 🚀 快速开始

### 1. 注册账号

访问：https://serpapi.com/

1. 点击 "Sign Up" 注册
2. 填写邮箱和密码
3. 验证邮箱

### 2. 获取 API Key

1. 登录后访问：https://serpapi.com/manage-api-key
2. 复制 "Your Private API Key"
3. 保存到安全的地方

### 3. 配置项目

编辑 `serpapi_ads_checker.py`：

```python
# 替换这一行
SERPAPI_KEY = "YOUR_SERPAPI_KEY_HERE"

# 改为你的实际 API Key
SERPAPI_KEY = "your_actual_api_key_here"
```

### 4. 安装依赖

```bash
pip3 install requests
```

### 5. 测试

```bash
cd Storeleads
python3 serpapi_ads_checker.py
```

## 📊 定价

### Free Plan（免费）
- ✅ 100 searches/month
- ✅ 所有 API 功能
- ✅ 适合小规模测试

### Starter Plan（$75/月）
- ✅ 5,000 searches/month
- ✅ 适合中等规模批量检查

### Production Plan（$225/月）
- ✅ 15,000 searches/month
- ✅ 适合大规模生产环境

详细定价：https://serpapi.com/pricing

## 💡 使用建议

1. **缓存结果** - 避免重复查询同一个域名
2. **批量处理** - 合理安排批量任务
3. **监控配额** - 在控制台查看已使用的查询次数
4. **错误处理** - 处理 API 错误和限流

## 📈 性能预估

基于 SerpApi 的官方性能数据：

| 方法 | 速度（秒/域名） | 并发 | 稳定性 |
|------|----------------|------|--------|
| Selenium | ~20-25 秒 | 单线程 | 中等 |
| Playwright | ~5-10 秒 | 5-10 并发 | 良好 |
| **SerpApi** | **~1-2 秒** | **无限制** | **优秀** |

**速度提升：**
- 比 Selenium 快 **10-20 倍**
- 比 Playwright 快 **3-5 倍**

## 🔧 API 使用示例

### 查询单个域名

```python
from serpapi_ads_checker import SerpApiAdsChecker

checker = SerpApiAdsChecker(api_key="your_key")
result = checker.check_domain_ads("keychron.com")

print(result)
# {
#   'domain': 'keychron.com',
#   'has_ads': True,
#   'ad_count': 42,
#   'first_shown': 1234567890,
#   'last_shown': 1234567890,
#   ...
# }
```

### 批量查询

```python
domains = ['keychron.com', 'nothing.tech', 'aelfriceden.com']
results = checker.batch_check_domains(domains)

for r in results:
    print(f"{r['domain']}: {r['ad_count']} ads")
```

## 🛡️ 安全建议

1. **不要提交 API Key 到 Git**
   - 将 API Key 存储在环境变量或 `.env` 文件
   - 添加 `.env` 到 `.gitignore`

2. **使用环境变量**

```python
import os

SERPAPI_KEY = os.getenv('SERPAPI_KEY', 'YOUR_SERPAPI_KEY_HERE')
```

```bash
export SERPAPI_KEY="your_actual_api_key"
python3 serpapi_ads_checker.py
```

## 📚 参考文档

- [SerpApi 官网](https://serpapi.com/)
- [Google Ads Transparency Center API 文档](https://serpapi.com/google-ads-transparency-center-api)
- [API Playground](https://serpapi.com/playground)

## ❓ 常见问题

### Q: 免费套餐够用吗？
A: 适合测试和小规模使用。如果每天检查 10 个域名，免费套餐可以用 10 天。

### Q: 如何监控使用量？
A: 访问 https://serpapi.com/dashboard 查看实时使用统计。

### Q: API 有速率限制吗？
A: 免费套餐约 1 请求/秒，付费套餐可以更快。

### Q: 数据准确吗？
A: SerpApi 直接从 Google Ads Transparency Center 获取数据，和手动查询完全一致。

## 🎯 下一步

1. ✅ 获取 API Key
2. ✅ 配置 `serpapi_ads_checker.py`
3. ✅ 运行测试
4. ✅ 查看性能对比报告
5. ✅ 决定是否升级到付费套餐
