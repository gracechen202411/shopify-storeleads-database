#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSS to Database
将Hop Skip Media博客保存到SQLite数据库，并记录详细日志
"""

import feedparser
import requests
import sqlite3
import json
from datetime import datetime
from bs4 import BeautifulSoup
import logging
import time

# ==================== 配置区 ====================

# 数据库文件
DB_FILE = "hopskip_blog.db"

# RSS Feed URL
RSS_FEED_URL = "https://hopskipmedia.com/category/google-adwords/feed/"

# 日志文件
LOG_FILE = f"rss_database_{datetime.now().strftime('%Y%m%d')}.log"

# 是否抓取完整文章内容（可能比较慢）
FETCH_FULL_CONTENT = True

# ==================== 日志配置 ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# ==================== 数据库函数 ====================

def init_database():
    """初始化数据库"""
    logger.info("🗄️ 初始化数据库...")

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
        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        discord_sent BOOLEAN DEFAULT FALSE,
        discord_sent_at DATETIME
    )
    ''')

    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_article_id ON hopskip_articles(article_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_published_date ON hopskip_articles(published_date)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_discord_sent ON hopskip_articles(discord_sent)')

    conn.commit()

    # 统计信息
    cursor.execute('SELECT COUNT(*) FROM hopskip_articles')
    count = cursor.fetchone()[0]
    logger.info(f"✅ 数据库已就绪，当前有 {count} 篇文章")

    conn.close()


def fetch_full_article(url):
    """抓取文章完整内容"""
    try:
        logger.info(f"  📥 抓取完整内容: {url}")
        response = requests.get(url, timeout=15)

        if response.status_code != 200:
            logger.warning(f"  ⚠️ HTTP {response.status_code}")
            return None

        soup = BeautifulSoup(response.content, 'html.parser')

        # 提取文章内容
        article = soup.find('article')
        if article:
            # 移除不需要的元素
            for elem in article.find_all(['script', 'style', 'nav', 'footer', 'header']):
                elem.decompose()

            content = article.get_text(separator='\n', strip=True)
            logger.info(f"  ✅ 抓取成功，长度: {len(content)} 字符")
            return content
        else:
            logger.warning(f"  ⚠️ 未找到article标签")
            return None

    except requests.Timeout:
        logger.error(f"  ❌ 请求超时")
        return None
    except Exception as e:
        logger.error(f"  ❌ 抓取失败: {e}")
        return None


def save_article(article):
    """保存文章到数据库"""
    article_id = article.get('id', article.get('link'))
    title = article.get('title', 'No Title')
    url = article.get('link', '')
    summary = BeautifulSoup(article.get('summary', ''), 'html.parser').get_text().strip()
    author = article.get('author', 'Unknown')
    published = article.get('published', '')

    logger.info(f"💾 保存文章: {title}")
    logger.info(f"  📎 URL: {url}")
    logger.info(f"  ✍️ 作者: {author}")

    # 解析发布日期
    try:
        # RSS日期格式：Mon, 13 Jan 2025 12:00:00 +0000
        published_date = datetime.strptime(published, '%a, %d %b %Y %H:%M:%S %z')
        logger.info(f"  📅 发布: {published_date.strftime('%Y-%m-%d %H:%M:%S')}")
    except:
        published_date = datetime.now()
        logger.warning(f"  ⚠️ 日期解析失败，使用当前时间")

    # 提取分类和标签
    categories = []
    tags = []
    for tag in article.get('tags', []):
        term = tag.get('term', '')
        scheme = tag.get('scheme', '')

        if 'category' in scheme.lower():
            categories.append(term)
        else:
            tags.append(term)

    logger.info(f"  📂 分类: {', '.join(categories) if categories else '无'}")
    logger.info(f"  🏷️ 标签: {', '.join(tags) if tags else '无'}")

    # 抓取完整内容
    content = None
    if FETCH_FULL_CONTENT:
        content = fetch_full_article(url)
        time.sleep(1)  # 避免请求太频繁

    # 保存到数据库
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        cursor.execute('''
        INSERT INTO hopskip_articles
        (article_id, title, url, summary, content, author, published_date, categories, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            article_id,
            title,
            url,
            summary,
            content,
            author,
            published_date,
            json.dumps(categories, ensure_ascii=False),
            json.dumps(tags, ensure_ascii=False)
        ))

        conn.commit()
        logger.info(f"✅ 保存成功 (ID: {cursor.lastrowid})")
        return True

    except sqlite3.IntegrityError:
        logger.info(f"⏭️  文章已存在，跳过")
        return False

    except Exception as e:
        logger.error(f"❌ 保存失败: {e}")
        conn.rollback()
        return False

    finally:
        conn.close()


def get_database_stats():
    """获取数据库统计信息"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    stats = {}

    # 总文章数
    cursor.execute('SELECT COUNT(*) FROM hopskip_articles')
    stats['total'] = cursor.fetchone()[0]

    # 今天新增
    cursor.execute('''
    SELECT COUNT(*) FROM hopskip_articles
    WHERE DATE(created_at) = DATE('now')
    ''')
    stats['today'] = cursor.fetchone()[0]

    # 已发送到Discord
    cursor.execute('SELECT COUNT(*) FROM hopskip_articles WHERE discord_sent = TRUE')
    stats['discord_sent'] = cursor.fetchone()[0]

    # 最新文章
    cursor.execute('''
    SELECT title, published_date FROM hopskip_articles
    ORDER BY published_date DESC
    LIMIT 1
    ''')
    row = cursor.fetchone()
    if row:
        stats['latest_title'] = row[0]
        stats['latest_date'] = row[1]
    else:
        stats['latest_title'] = 'N/A'
        stats['latest_date'] = 'N/A'

    conn.close()
    return stats


def main():
    """主函数"""
    logger.info("=" * 100)
    logger.info("🚀 RSS to Database 启动")
    logger.info(f"📡 RSS Feed: {RSS_FEED_URL}")
    logger.info(f"🗄️ 数据库: {DB_FILE}")
    logger.info(f"📝 日志文件: {LOG_FILE}")
    logger.info(f"📄 抓取完整内容: {'是' if FETCH_FULL_CONTENT else '否'}")
    logger.info("=" * 100)

    # 初始化数据库
    init_database()

    # 解析RSS Feed
    logger.info("\n📡 正在抓取RSS Feed...")
    try:
        feed = feedparser.parse(RSS_FEED_URL)
    except Exception as e:
        logger.error(f"❌ RSS解析失败: {e}")
        return

    if not feed.entries:
        logger.warning("⚠️ 未找到RSS条目")
        return

    logger.info(f"📰 找到 {len(feed.entries)} 篇文章\n")

    # 处理每篇文章
    new_count = 0
    for idx, entry in enumerate(feed.entries, 1):
        logger.info(f"\n{'=' * 80}")
        logger.info(f"[{idx}/{len(feed.entries)}] 处理文章")
        logger.info(f"{'=' * 80}")

        if save_article(entry):
            new_count += 1

    # 显示统计信息
    logger.info("\n" + "=" * 100)
    logger.info("📊 数据库统计")
    logger.info("=" * 100)

    stats = get_database_stats()
    logger.info(f"总文章数: {stats['total']}")
    logger.info(f"今日新增: {stats['today']}")
    logger.info(f"已发送Discord: {stats['discord_sent']}")
    logger.info(f"最新文章: {stats['latest_title']}")
    logger.info(f"发布日期: {stats['latest_date']}")

    logger.info("\n" + "=" * 100)
    logger.info(f"✅ 处理完成！")
    logger.info(f"   新增文章: {new_count}")
    logger.info(f"   跳过重复: {len(feed.entries) - new_count}")
    logger.info("=" * 100)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}", exc_info=True)
