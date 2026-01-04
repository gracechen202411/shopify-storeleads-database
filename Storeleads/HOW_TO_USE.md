# 完整版使用说明

## 🎯 文件说明

您现在有 3 个文件：

1. **`test_selenium_batch.py`** - 测试版（已验证，10 个域名，50 秒）
2. **`reliable_selenium_full.py`** - 完整版（基于测试版，6251 个域名，8-10 小时）✅
3. **`VERSION_COMPARISON.md`** - 详细对比说明

---

## 🚀 快速开始

### 方案 A：立即运行完整版（推荐）

```bash
cd /Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads

# 运行完整版
python3 reliable_selenium_full.py
```

**会做什么：**
1. 显示进度统计（已处理/待处理）
2. 询问是否开始（按 Enter 确认）
3. 开始检查 6251 个域名
4. 每 20 个自动保存到数据库
5. 每 100 个显示进度报告
6. 完成后显示详细统计

**预计时间：8-10 小时**

---

### 方案 B：后台运行（睡觉时跑）

```bash
cd /Users/hangzhouweineng/Desktop/shopify-storeleads-database/Storeleads

# 后台运行，输出到日志文件
nohup python3 reliable_selenium_full.py > check.log 2>&1 &

# 查看实时进度
tail -f check.log

# 或者在另一个终端查看进度文件
watch -n 10 'cat selenium_progress.json | python3 -m json.tool'
```

**好处：**
- ✅ 不用一直盯着
- ✅ 睡觉时也在跑
- ✅ 关闭终端也不影响

---

### 方案 C：分批运行（每天跑一点）

```bash
# 第一天：运行 2 小时
python3 reliable_selenium_full.py
# 2 小时后按 Ctrl+C 中断

# 第二天：继续运行
python3 reliable_selenium_full.py
# ✅ 自动从上次继续！

# 第三天、第四天...
# 一直到全部完成
```

**好处：**
- ✅ 随时可以中断
- ✅ 进度不会丢失
- ✅ 灵活安排时间

---

## 📊 运行中会看到什么

### 启动时：

```
====================================================================================================
🚀 完整版可靠批量检查器（Selenium）
====================================================================================================

✅ 数据库连接成功

🌐 启动 Chrome 浏览器...
✅ 浏览器启动成功

📊 数据库中共有 6251 个域名
✅ 已处理: 0 个
⏳ 待处理: 6251 个

====================================================================================================
🚀 开始检查 6251 个域名...
⚙️  批量大小: 20 (每次 commit)
🔄 重试次数: 2
====================================================================================================
```

### 运行中：

```
[1/6251] 检查 keychron.com (815,670 访问/月 🇭🇰)... ✅ 400 个广告
[2/6251] 检查 nothing.tech (1,508,985 访问/月 🇭🇰)... ⭕ 0 个广告
[3/6251] 检查 aelfriceden.com (681,352 访问/月 🇨🇳)... ✅ 300 个广告
...
[20/6251] 检查 test.com (10,000 访问/月 🇨🇳)... ✅ 50 个广告
  💾 批量更新 20 个域名到数据库

[100/6251] 检查 another.com...
📊 进度统计:
   已完成: 100/6251 (1.6%)
   平均速度: 5.2 秒/域名
   预计剩余: 8.9 小时
   成功率: 98.0%
```

### 完成时：

```
====================================================================================================
📊 检查完成！
====================================================================================================

⏱️  总耗时: 32451.23 秒 (9.01 小时)
✅ 成功处理: 6180 个域名
❌ 失败: 71 个域名
📈 平均速度: 5.19 秒/域名
📊 成功率: 98.9%

✅ 进度已保存到: selenium_progress.json
✅ 数据已更新到 Neon 数据库
====================================================================================================
```

---

## 💾 进度文件说明

### `selenium_progress.json` 内容：

```json
{
  "processed": [
    "keychron.com",
    "nothing.tech",
    "aelfriceden.com",
    ...
  ],
  "failed": [
    "error-domain.com"
  ],
  "total_checked": 1234,
  "updated_at": "2025-01-04T12:00:00"
}
```

**作用：**
- ✅ 记录已处理的域名
- ✅ 记录失败的域名
- ✅ 中断后继续时自动跳过已处理的

---

## 🔧 常见操作

### 1. 中断运行

```bash
# 按 Ctrl+C
^C

⚠️  用户中断！
💾 正在保存进度...
✅ 进度已保存，下次运行会继续
```

### 2. 继续运行

```bash
# 直接再运行
python3 reliable_selenium_full.py

📦 加载进度: 已处理 1234 个域名
...
⏳ 待处理: 5017 个
# ✅ 自动继续！
```

### 3. 重新开始

```bash
# 删除进度文件
rm selenium_progress.json

# 再运行
python3 reliable_selenium_full.py
# ✅ 从头开始
```

### 4. 只重试失败的

```bash
# 编辑进度文件，只保留 failed 列表
# 删除 processed 列表

# 或者用命令：
python3 -c "
import json
with open('selenium_progress.json', 'r') as f:
    data = json.load(f)

# 只重试失败的
data['processed'] = []

with open('selenium_progress.json', 'w') as f:
    json.dump(data, f)
"

# 再运行
python3 reliable_selenium_full.py
```

---

## 📈 查看数据库结果

```bash
# 查看已更新的数据
python3 -c "
import psycopg2

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 统计
cur.execute('''
    SELECT
        COUNT(*) as total,
        SUM(CASE WHEN google_ads_count > 0 THEN 1 ELSE 0 END) as has_ads,
        SUM(CASE WHEN google_ads_count = 0 THEN 1 ELSE 0 END) as no_ads
    FROM stores
    WHERE ads_check_level = '"'reliable_selenium_full'"'
''')

total, has_ads, no_ads = cur.fetchone()
print(f'总计: {total}')
print(f'有广告: {has_ads} ({has_ads/total*100:.1f}%)')
print(f'无广告: {no_ads} ({no_ads/total*100:.1f}%)')

cur.close()
conn.close()
"
```

---

## ⚠️ 注意事项

### 1. 网络问题

如果网络不稳定：
- ✅ 自动重试 2 次
- ✅ 失败的会记录下来
- ✅ 可以单独重试失败的

### 2. 内存问题

如果内存不足：
- 减小批量大小（改 `BATCH_SIZE = 10`）
- 每次更新更频繁，但更稳定

### 3. 速度太慢

如果觉得慢：
- 增加批量大小（改 `BATCH_SIZE = 50`）
- 或考虑使用 SerpApi（付费，1-2 秒/个）

---

## 🎯 推荐流程

### 今天：

```bash
# 1. 测试 3 个域名（确保能正常运行）
# 编辑 reliable_selenium_full.py 第 237 行
# 改为：LIMIT 3

python3 reliable_selenium_full.py

# 2. 确认数据库更新成功

# 3. 改回 LIMIT 去掉（运行全部）

# 4. 后台运行
nohup python3 reliable_selenium_full.py > check.log 2>&1 &

# 5. 睡觉去 😴
```

### 明天：

```bash
# 查看进度
tail check.log

# 或查看进度文件
cat selenium_progress.json

# 如果完成了，查看结果
# 如果还在跑，继续等待
```

---

## 💰 成本

**完全免费！**
- ✅ 使用您的电脑
- ✅ 使用您的网络
- ✅ 不消耗 Claude token
- ✅ 不花一分钱

---

## 📞 遇到问题？

### 常见错误：

1. **`ChromeDriver not found`**
   ```bash
   # 安装 ChromeDriver
   brew install chromedriver
   ```

2. **数据库连接失败**
   - 检查网络
   - 确认数据库密码正确

3. **Chrome 启动失败**
   ```bash
   # 使用有界面模式
   # 删除 --headless 参数
   ```

---

## 🎉 完成后

### 数据会在：
1. ✅ Neon 数据库（`stores` 表）
2. ✅ Vercel 前端可以立即查看
3. ✅ 可以导出 CSV

### 您可以：
1. 在 Vercel 网站上搜索店铺
2. 筛选有广告/无广告的店铺
3. 导出目标客户列表
4. 给朋友使用

---

**准备好了吗？现在就运行吧！** 🚀
