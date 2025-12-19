#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import logging

# ==================== 配置区 ====================

# Discord Webhook URL（需要替换成你的）
DISCORD_WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL_HERE"

# RSS Feed URL
RSS_FEED_URL = "https://hopskipmedia.com/category/google-adwords/feed/"

# 已发送文章缓存文件
SENT_CACHE_FILE = "sent_articles.json"

# 日志文件
LOG_FILE = f"rss_discord_{datetime.now().strftime('%Y%m%d')}.log"

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

# ==================== 核心函数 ====================

def load_sent_articles():
    """加载已发送的文章列表"""
    try:
        with open(SENT_CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"📂 已加载缓存: {len(data)} 篇文章")
            return set(data)
    except FileNotFoundError:
        logger.info("📂 缓存文件不存在，创建新缓存")
        return set()
    except Exception as e:
        logger.error(f"❌ 加载缓存失败: {e}")
        return set()


def save_sent_articles(articles):
    """保存已发送的文章列表"""
    try:
        with open(SENT_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(list(articles), f, ensure_ascii=False, indent=2)
        logger.info(f"💾 已保存缓存: {len(articles)} 篇文章")
    except Exception as e:
        logger.error(f"❌ 保存缓存失败: {e}")


def clean_html(html_text):
    """清理HTML标签"""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    return soup.get_text().strip()


def send_to_discord(article):
    """发送文章到Discord"""
    title = article.get('title', 'No Title')
    link = article.get('link', '')
    published = article.get('published', 'Unknown')
    summary = article.get('summary', '')
    author = article.get('author', 'Unknown')

    # 清理HTML标签
    clean_summary = clean_html(summary)
    if len(clean_summary) > 300:
        clean_summary = clean_summary[:300] + "..."

    # 解析分类
    categories = [tag['term'] for tag in article.get('tags', []) if tag.get('term')]
    category_text = ", ".join(categories[:3]) if categories else "Uncategorized"

    # 构建Discord Embed消息
    embed = {
        "title": title,
        "description": clean_summary,
        "url": link,
        "color": 16744448,  # 橙色 (0xFF8000)
        "footer": {
            "text": "Hop Skip Media Blog"
        },
        "timestamp": datetime.now().isoformat(),
        "fields": [
            {
                "name": "✍️ 作者",
                "value": author,
                "inline": True
            },
            {
                "name": "📂 分类",
                "value": category_text,
                "inline": True
            },
            {
                "name": "📅 发布时间",
                "value": published,
                "inline": False
            }
        ],
        "thumbnail": {
            "url": "https://hopskipmedia.com/wp-content/uploads/2021/03/cropped-hop-skip-media-logo-512x512-1-270x270.png"
        }
    }

    payload = {
        "content": "🔔 **新的Google Ads文章发布了！**",
        "embeds": [embed]
    }

    try:
        logger.info(f"📤 正在发送到Discord: {title}")
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)

        if response.status_code == 204:
            logger.info(f"✅ 发送成功")
            return True
        else:
            logger.error(f"❌ 发送失败 (HTTP {response.status_code}): {response.text}")
            return False

    except Exception as e:
        logger.error(f"❌ 发送到Discord异常: {e}")
        return False


def main():
    """主函数：定期检查RSS并发送新文章"""
    logger.info("=" * 100)
    logger.info("🚀 RSS to Discord Bot 启动")
    logger.info(f"📡 RSS Feed: {RSS_FEED_URL}")
    logger.info(f"🎯 Discord Webhook: {DISCORD_WEBHOOK_URL[:50]}...")
    logger.info(f"📁 缓存文件: {SENT_CACHE_FILE}")
    logger.info(f"📝 日志文件: {LOG_FILE}")
    logger.info("=" * 100)

    # 检查Webhook配置
    if DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE":
        logger.error("❌ 请先配置DISCORD_WEBHOOK_URL！")
        logger.error("   在脚本顶部修改 DISCORD_WEBHOOK_URL 变量")
        return

    # 加载已发送文章
    sent_articles = load_sent_articles()

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

    new_count = 0
    for idx, entry in enumerate(feed.entries, 1):
        article_id = entry.get('id', entry.get('link'))
        title = entry.get('title', 'No Title')

        logger.info(f"[{idx}/{len(feed.entries)}] 检查文章: {title}")

        if article_id in sent_articles:
            logger.info(f"  ⏭️  已发送过，跳过")
            continue

        logger.info(f"  📬 发现新文章！")

        if send_to_discord(entry):
            sent_articles.add(article_id)
            save_sent_articles(sent_articles)
            new_count += 1

            # 避免发送太快被Discord限速
            time.sleep(2)
        else:
            logger.warning(f"  ⚠️  发送失败，下次重试")

        print()  # 空行分隔

    logger.info("=" * 100)
    logger.info(f"✅ 处理完成！")
    logger.info(f"   总文章数: {len(feed.entries)}")
    logger.info(f"   新增发送: {new_count}")
    logger.info(f"   已发送总数: {len(sent_articles)}")
    logger.info("=" * 100)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\n⚠️ 用户中断")
    except Exception as e:
        logger.error(f"❌ 程序异常: {e}", exc_info=True)
