# Hop Skip Media Google Ads Blog 订阅指南

## 📡 RSS订阅地址

### 主博客RSS
```
https://hopskipmedia.com/feed/
```

### Google AdWords分类RSS
```
https://hopskipmedia.com/category/google-adwords/feed/
```

### Digital Marketing分类RSS
```
https://hopskipmedia.com/category/digital-marketing/feed/
```

---

## 🤖 如何将博客文章发送到Discord进行解读

### 方案1：使用Discord Webhook + RSS Bot

#### 步骤1：创建Discord Webhook
```
1. 进入你的Discord服务器
2. 右键点击目标频道 → 编辑频道
3. 集成 → Webhooks → 新建Webhook
4. 复制Webhook URL（格式类似：https://discord.com/api/webhooks/xxx/yyy）
```

#### 步骤2：使用RSS-to-Discord服务

**推荐服务**：
- **MonitoRSS** (https://monitorss.xyz/)
  - 免费
  - 支持自定义消息格式
  - 可以过滤关键词（如"Google Ads"）

- **Zapier** (https://zapier.com/)
  - RSS Feed → Discord
  - 可以添加中间处理步骤

- **IFTTT** (https://ifttt.com/)
  - RSS to Discord applet

**配置示例（MonitoRSS）**：
```
RSS Feed URL: https://hopskipmedia.com/category/google-adwords/feed/
Discord Channel: #google-ads-articles
Message Format:
📰 新文章发布！
**{title}**
{description}
🔗 {link}
发布时间：{date}
```

---

### 方案2：使用Python脚本自动化（推荐）

#### 安装依赖
```bash
pip install feedparser requests beautifulsoup4
```

#### 脚本：`rss_to_discord.py`
```python
#!/usr/bin/env python3
"""
RSS to Discord Bot
自动抓取Hop Skip Media博客并发送到Discord
"""

import feedparser
import requests
import time
from datetime import datetime
import json
from bs4 import BeautifulSoup

# Discord Webhook URL（需要替换成你的）
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/YOUR_WEBHOOK_TOKEN"

# RSS Feed URL
RSS_FEED_URL = "https://hopskipmedia.com/category/google-adwords/feed/"

# 已发送文章缓存文件
SENT_CACHE_FILE = "sent_articles.json"

def load_sent_articles():
    """加载已发送的文章列表"""
    try:
        with open(SENT_CACHE_FILE, 'r') as f:
            return set(json.load(f))
    except FileNotFoundError:
        return set()

def save_sent_articles(articles):
    """保存已发送的文章列表"""
    with open(SENT_CACHE_FILE, 'w') as f:
        json.dump(list(articles), f)

def fetch_article_content(url):
    """抓取文章完整内容（可选）"""
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取文章主要内容（根据Hop Skip Media的HTML结构）
        article = soup.find('article')
        if article:
            # 提取前300个字符作为摘要
            paragraphs = article.find_all('p')
            content = ' '.join([p.get_text() for p in paragraphs[:3]])
            return content[:300] + "..."
        return None
    except Exception as e:
        print(f"❌ 抓取文章内容失败: {e}")
        return None

def send_to_discord(article):
    """发送文章到Discord"""
    title = article.get('title', 'No Title')
    link = article.get('link', '')
    published = article.get('published', 'Unknown')
    summary = article.get('summary', '')

    # 清理HTML标签
    soup = BeautifulSoup(summary, 'html.parser')
    clean_summary = soup.get_text()[:200] + "..."

    # 构建Discord Embed消息
    embed = {
        "title": title,
        "description": clean_summary,
        "url": link,
        "color": 5814783,  # 橙色（Hop Skip Media品牌色）
        "footer": {
            "text": "Hop Skip Media Blog"
        },
        "timestamp": published,
        "fields": [
            {
                "name": "📅 发布时间",
                "value": published,
                "inline": True
            }
        ]
    }

    payload = {
        "content": "🔔 **新的Google Ads文章发布了！**",
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
        if response.status_code == 204:
            print(f"✅ 已发送到Discord: {title}")
            return True
        else:
            print(f"❌ 发送失败 (HTTP {response.status_code}): {title}")
            return False
    except Exception as e:
        print(f"❌ 发送到Discord失败: {e}")
        return False

def main():
    """主函数：定期检查RSS并发送新文章"""
    print("🚀 启动RSS to Discord Bot...")
    print(f"📡 监控RSS: {RSS_FEED_URL}")
    print(f"🎯 目标Discord Webhook: {DISCORD_WEBHOOK_URL[:50]}...")

    sent_articles = load_sent_articles()

    # 解析RSS Feed
    feed = feedparser.parse(RSS_FEED_URL)

    if not feed.entries:
        print("⚠️ 未找到RSS条目")
        return

    print(f"📰 找到 {len(feed.entries)} 篇文章")

    new_count = 0
    for entry in feed.entries:
        article_id = entry.get('id', entry.get('link'))

        if article_id not in sent_articles:
            print(f"\n📤 发现新文章: {entry.get('title')}")

            if send_to_discord(entry):
                sent_articles.add(article_id)
                save_sent_articles(sent_articles)
                new_count += 1

                # 避免发送太快被Discord限速
                time.sleep(2)

    print(f"\n✅ 完成！发送了 {new_count} 篇新文章")

if __name__ == '__main__':
    main()
```

#### 运行脚本
```bash
# 测试运行
python3 rss_to_discord.py

# 定时运行（每小时检查一次）
# macOS/Linux - 添加到crontab
0 * * * * cd /path/to/Storeleads && python3 rss_to_discord.py

# 或者使用后台运行
nohup python3 rss_to_discord.py &
```

---

### 方案3：使用GitHub Actions自动化（最佳）

创建 `.github/workflows/rss-to-discord.yml`:

```yaml
name: RSS to Discord

on:
  schedule:
    # 每小时运行一次
    - cron: '0 * * * *'
  workflow_dispatch:  # 允许手动触发

jobs:
  fetch-and-send:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.x'

    - name: Install dependencies
      run: |
        pip install feedparser requests beautifulsoup4

    - name: Run RSS to Discord script
      env:
        DISCORD_WEBHOOK_URL: ${{ secrets.DISCORD_WEBHOOK_URL }}
      run: |
        python3 rss_to_discord.py

    - name: Commit updated cache
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add sent_articles.json
        git diff --quiet && git diff --staged --quiet || git commit -m "Update sent articles cache"
        git push
```

---

## 🗄️ 如何将博客内容保存到数据库

### 数据库设计

#### 表结构：`hopskip_articles`

```sql
CREATE TABLE hopskip_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id TEXT UNIQUE NOT NULL,           -- RSS条目ID或URL
    title TEXT NOT NULL,                        -- 文章标题
    url TEXT NOT NULL,                          -- 文章URL
    summary TEXT,                               -- 摘要
    content TEXT,                               -- 完整内容（可选）
    author TEXT,                                -- 作者
    published_date DATETIME,                    -- 发布日期
    categories TEXT,                            -- 分类（JSON数组）
    tags TEXT,                                  -- 标签（JSON数组）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,  -- 入库时间
    discord_sent BOOLEAN DEFAULT FALSE,         -- 是否已发送到Discord
    discord_sent_at DATETIME                    -- 发送到Discord的时间
);

CREATE INDEX idx_article_id ON hopskip_articles(article_id);
CREATE INDEX idx_published_date ON hopskip_articles(published_date);
CREATE INDEX idx_discord_sent ON hopskip_articles(discord_sent);
```

---

### Python脚本：`rss_to_database.py`

```python
#!/usr/bin/env python3
"""
RSS to Database
将Hop Skip Media博客保存到SQLite数据库
"""

import feedparser
import requests
import sqlite3
import json
from datetime import datetime
from bs4 import BeautifulSoup

# 数据库文件
DB_FILE = "hopskip_blog.db"

# RSS Feed URL
RSS_FEED_URL = "https://hopskipmedia.com/category/google-adwords/feed/"

def init_database():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS hopskip_articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        article_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        url TEXT NOT NULL,
        summary TEXT,
        content TEXT,
        author TEXT,
        published_date DATETIME,
        categories TEXT,
        tags TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        discord_sent BOOLEAN DEFAULT FALSE,
        discord_sent_at DATETIME
    )
    ''')

    cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_id ON hopskip_articles(article_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_published_date ON hopskip_articles(published_date)')

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")

def fetch_full_article(url):
    """抓取文章完整内容"""
    try:
        response = requests.get(url, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取文章内容
        article = soup.find('article')
        if article:
            # 移除不需要的元素
            for elem in article.find_all(['script', 'style', 'nav']):
                elem.decompose()

            return article.get_text(separator='\n', strip=True)
        return None
    except Exception as e:
        print(f"❌ 抓取文章失败 {url}: {e}")
        return None

def save_article(article):
    """保存文章到数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    article_id = article.get('id', article.get('link'))
    title = article.get('title', 'No Title')
    url = article.get('link', '')
    summary = BeautifulSoup(article.get('summary', ''), 'html.parser').get_text()
    author = article.get('author', 'Unknown')
    published = article.get('published', '')

    # 解析发布日期
    try:
        published_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
    except:
        published_date = datetime.now()

    # 提取分类
    categories = [tag['term'] for tag in article.get('tags', []) if tag.get('term')]

    try:
        # 抓取完整内容（可选）
        print(f"📄 抓取完整内容: {title}")
        content = fetch_full_article(url)

        cursor.execute('''
        INSERT INTO hopskip_articles
        (article_id, title, url, summary, content, author, published_date, categories)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id,
            title,
            url,
            summary,
            content,
            author,
            published_date,
            json.dumps(categories)
        ))

        conn.commit()
        print(f"✅ 已保存: {title}")
        return True

    except sqlite3.IntegrityError:
        print(f"⏭️  已存在: {title}")
        return False
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        return False
    finally:
        conn.close()

def main():
    """主函数"""
    print("🚀 启动RSS to Database...")

    # 初始化数据库
    init_database()

    # 解析RSS Feed
    print(f"📡 正在抓取RSS: {RSS_FEED_URL}")
    feed = feedparser.parse(RSS_FEED_URL)

    if not feed.entries:
        print("⚠️ 未找到RSS条目")
        return

    print(f"📰 找到 {len(feed.entries)} 篇文章")

    new_count = 0
    for entry in feed.entries:
        if save_article(entry):
            new_count += 1

    print(f"\n✅ 完成！新增 {new_count} 篇文章到数据库")

if __name__ == '__main__':
    main()
```

---

### 查询数据库

```python
#!/usr/bin/env python3
"""查询数据库示例"""

import sqlite3
import json

DB_FILE = "hopskip_blog.db"

def query_articles():
    """查询所有文章"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id, title, url, author, published_date, categories
    FROM hopskip_articles
    ORDER BY published_date DESC
    LIMIT 10
    ''')

    print("📚 最近10篇文章：\n")
    for row in cursor.fetchall():
        id, title, url, author, published, categories = row
        cats = json.loads(categories) if categories else []
        print(f"[{id}] {title}")
        print(f"    作者: {author}")
        print(f"    发布: {published}")
        print(f"    分类: {', '.join(cats)}")
        print(f"    链接: {url}")
        print()

    conn.close()

if __name__ == '__main__':
    query_articles()
```

---

## 📊 日志记录

### 日志脚本：`rss_with_logging.py`

```python
#!/usr/bin/env python3
"""
带日志记录的RSS处理脚本
"""

import logging
from datetime import datetime

# 配置日志
LOG_FILE = f"rss_processor_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    logger.info("=" * 80)
    logger.info("RSS处理器启动")
    logger.info(f"RSS Feed: {RSS_FEED_URL}")
    logger.info(f"数据库: {DB_FILE}")
    logger.info(f"Discord Webhook: {DISCORD_WEBHOOK_URL[:50]}...")
    logger.info("=" * 80)

    try:
        # 初始化数据库
        logger.info("初始化数据库...")
        init_database()

        # 抓取RSS
        logger.info("正在抓取RSS Feed...")
        feed = feedparser.parse(RSS_FEED_URL)
        logger.info(f"找到 {len(feed.entries)} 篇文章")

        # 处理每篇文章
        new_articles = 0
        sent_articles = 0

        for idx, entry in enumerate(feed.entries, 1):
            title = entry.get('title', 'No Title')
            logger.info(f"[{idx}/{len(feed.entries)}] 处理文章: {title}")

            # 保存到数据库
            if save_article(entry):
                logger.info(f"  ✅ 已保存到数据库")
                new_articles += 1

                # 发送到Discord
                if send_to_discord(entry):
                    logger.info(f"  ✅ 已发送到Discord")
                    sent_articles += 1
                else:
                    logger.warning(f"  ⚠️  发送到Discord失败")
            else:
                logger.info(f"  ⏭️  文章已存在，跳过")

        logger.info("=" * 80)
        logger.info(f"✅ 处理完成！")
        logger.info(f"   新增文章: {new_articles}")
        logger.info(f"   发送到Discord: {sent_articles}")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"❌ 处理失败: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()
```

---

## 🎯 完整工作流程

```
1. RSS Feed (Hop Skip Media)
   ↓
2. Python脚本定期抓取
   ↓
3. 解析文章内容
   ↓
4. 保存到SQLite数据库
   ↓
5. 发送到Discord频道
   ↓
6. 记录日志
   ↓
7. 定期运行（cron/GitHub Actions）
```

---

## 📝 运行清单

### 首次设置
```bash
# 1. 创建Discord Webhook
# 2. 安装Python依赖
pip install feedparser requests beautifulsoup4

# 3. 配置脚本（修改DISCORD_WEBHOOK_URL）
vim rss_to_discord.py

# 4. 初始化数据库
python3 rss_to_database.py

# 5. 测试运行
python3 rss_with_logging.py

# 6. 查看日志
cat rss_processor_*.log

# 7. 查询数据库
python3 query_database.py
```

### 日常使用
```bash
# 手动运行一次
python3 rss_with_logging.py

# 查看最新日志
tail -f rss_processor_$(date +%Y%m%d).log

# 查看数据库统计
sqlite3 hopskip_blog.db "SELECT COUNT(*) FROM hopskip_articles;"
```

---

## 🔍 监控和调试

### 检查数据库
```bash
sqlite3 hopskip_blog.db

# 查看总文章数
SELECT COUNT(*) FROM hopskip_articles;

# 查看今天新增的文章
SELECT title, published_date FROM hopskip_articles
WHERE DATE(created_at) = DATE('now')
ORDER BY created_at DESC;

# 查看未发送到Discord的文章
SELECT id, title, url FROM hopskip_articles
WHERE discord_sent = FALSE;
```

### 查看日志
```bash
# 查看所有日志
ls -lh rss_processor_*.log

# 查看今天的日志
cat rss_processor_$(date +%Y%m%d).log

# 搜索错误
grep "ERROR" rss_processor_*.log

# 实时监控
tail -f rss_processor_$(date +%Y%m%d).log
```

---

## 🚀 下一步优化

1. ✅ 添加文章内容摘要生成（AI总结）
2. ✅ 添加关键词提取
3. ✅ 添加文章分类和标签
4. ✅ 添加重复检测（相似文章）
5. ✅ 添加Webhook失败重试机制
6. ✅ 添加定时任务监控告警

---

**创建时间**: 2025-12-17
**适用于**: Hop Skip Media Google Ads Blog
**工具栈**: Python + SQLite + Discord Webhooks + RSS
