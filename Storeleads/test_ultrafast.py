#!/usr/bin/env python3
"""测试超快速版本 - 10个域名"""

import psycopg2
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

print('='*100)
print('⚡ 测试超快速版本（10个域名）')
print('='*100)
print()

# 获取测试域名
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("""
    SELECT domain FROM stores
    WHERE country_code IN ('CN', 'HK')
      AND estimated_monthly_visits >= 100000
    ORDER BY estimated_monthly_visits DESC
    LIMIT 10
""")
domains = [row[0] for row in cur.fetchall()]
cur.close()
conn.close()

# 启动浏览器 - 超快速配置
print('🌐 启动浏览器（超快速配置）...')
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')

# 超快速优化
chrome_options.add_argument('--disable-images')
chrome_options.add_argument('--blink-settings=imagesEnabled=false')
chrome_options.page_load_strategy = 'eager'  # 不等待完全加载

driver = webdriver.Chrome(options=chrome_options)
driver.set_page_load_timeout(5)  # 5秒超时
print('✅ 浏览器启动成功\n')

print('='*100)
print('⚡ 开始检查...')
print('='*100)
print()

start_time = time.time()

for i, domain in enumerate(domains, 1):
    check_domain = domain.replace('www.', '')
    url = f'https://adstransparency.google.com/?region=anywhere&domain={check_domain}'

    item_start = time.time()

    try:
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 2)
            wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text)
        except:
            pass

        page_text = driver.find_element(By.TAG_NAME, 'body').text
        match = re.search(r'~?(\d+)\+?\s*个广告', page_text)

        if match:
            ads_count = int(match.group(1))
            status = '✅' if ads_count > 0 else '⭕'
        elif '未找到任何广告' in page_text:
            ads_count = 0
            status = '⭕'
        else:
            ads_count = -1
            status = '❓'

        item_time = time.time() - item_start
        print(f'[{i}/10] {domain}: {status} {ads_count} 个广告 ({item_time:.2f}秒)')

    except Exception as e:
        print(f'[{i}/10] {domain}: ❌ 错误')

elapsed = time.time() - start_time

driver.quit()

print()
print('='*100)
print('📊 测试结果')
print('='*100)
print(f'⏱️  总耗时: {elapsed:.2f} 秒')
print(f'📈 平均速度: {elapsed/10:.2f} 秒/个')
print()

if elapsed/10 < 2:
    print('🎉 速度非常快！可以用这个版本！')
elif elapsed/10 < 3:
    print('✅ 速度不错！比之前快了！')
else:
    print('⚠️  速度改进有限')

print('='*100)
