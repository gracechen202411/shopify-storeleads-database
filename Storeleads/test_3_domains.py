#!/usr/bin/env python3
"""
测试：检查 3 个域名能检测到什么信息
"""

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
print('🧪 测试：检查 3 个域名能检测到什么信息')
print('='*100)
print()

# 获取 3 个测试域名
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()
cur.execute("""
    SELECT domain, estimated_monthly_visits, country_code
    FROM stores
    WHERE country_code IN ('CN', 'HK')
      AND estimated_monthly_visits >= 100000
    ORDER BY estimated_monthly_visits DESC
    LIMIT 3
""")
test_domains = cur.fetchall()
cur.close()
conn.close()

print('📊 测试域名：')
for i, (domain, visits, country) in enumerate(test_domains, 1):
    flag = '🇨🇳' if country == 'CN' else '🇭🇰'
    print(f'  {i}. {domain} - {visits:,} 访问/月 {flag}')
print()

# 启动浏览器
print('🌐 启动浏览器...')
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
print('✅ 浏览器启动成功')
print()

print('='*100)
print('🔍 开始检查...')
print('='*100)
print()

for i, (domain, visits, country) in enumerate(test_domains, 1):
    print(f'[{i}/3] 检查 {domain}...')

    check_domain = domain.replace('www.', '')
    url = f'https://adstransparency.google.com/?region=anywhere&domain={check_domain}'

    try:
        driver.get(url)

        try:
            wait = WebDriverWait(driver, 10)
            wait.until(lambda d: '个广告' in d.find_element(By.TAG_NAME, 'body').text)
            time.sleep(2)
        except:
            pass

        page_text = driver.find_element(By.TAG_NAME, 'body').text

        # 检查广告数量
        match = re.search(r'~?(\d+)\+?\s*个广告', page_text)

        if match:
            ads_count = int(match.group(1))
            has_ads = ads_count > 0

            print(f'  ✅ 广告数量: {ads_count}')

            if has_ads:
                # 尝试查找日期信息
                if '最近展示' in page_text or '上次展示' in page_text or '天前' in page_text:
                    print(f'  📅 页面包含日期信息')
                    # 尝试提取日期
                    date_matches = re.findall(r'(\d+)\s*天前', page_text)
                    if date_matches:
                        days_ago = min(int(d) for d in date_matches)
                        print(f'  📅 最近广告: {days_ago} 天前')
                        if days_ago <= 30:
                            print(f'  🔥 可能是 30 天内新客户！')
                else:
                    print(f'  ⚠️  首页没有显示广告日期')

                # 检查是否需要点击才能看到日期
                print(f'  💡 需要点击广告才能查看详细投放日期')
            else:
                print(f'  ⭕ 无广告 (never_advertised)')

        elif '未找到任何广告' in page_text:
            print(f'  ⭕ 无广告 (never_advertised)')
        else:
            print(f'  ❓ 无法判断')

    except Exception as e:
        print(f'  ❌ 错误: {e}')

    print()
    time.sleep(1)

driver.quit()

print('='*100)
print('⚠️  重要发现：')
print('='*100)
print()
print('当前脚本能检测到：')
print('  ✅ 1. 是否有投放 Google 广告')
print('  ✅ 2. 广告总数量')
print('  ⚠️  3. 部分广告可能显示"X天前"')
print()
print('当前脚本无法准确检测到：')
print('  ❌ 1. 广告的首次投放日期')
print('  ❌ 2. 是否是 30 天内的新客户')
print()
print('💡 要准确检测 30 天新客户，需要：')
print('  1. 点击进入广告详情页')
print('  2. 查看广告的"首次展示"和"最后展示"日期')
print('  3. 判断是否在 30 天内开始投放')
print()
print('='*100)
