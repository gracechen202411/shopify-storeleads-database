#!/usr/bin/env python3
"""
使用 Selenium 检测 Shopify 店铺是否安装了 Customily 应用
支持检测动态加载的内容
"""

import os
import sys
import psycopg2
import time
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 数据库连接
DATABASE_URL = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL_NON_POOLING')

if not DATABASE_URL:
    print("ERROR: Please set DATABASE_URL or POSTGRES_URL_NON_POOLING environment variable")
    sys.exit(1)

def create_driver():
    """创建 Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

def check_customily_with_selenium(driver, domain):
    """
    使用 Selenium 检测 Customily 应用
    
    返回: (has_customily: bool, details: str)
    """
    try:
        # 确保域名格式正确
        if not domain.startswith('http'):
            url = f'https://{domain}'
        else:
            url = domain
        
        # 访问页面
        driver.get(url)
        
        # 等待页面加载
        time.sleep(3)
        
        # 获取页面源代码
        page_source = driver.page_source.lower()
        
        # 检测 Customily 特征
        customily_indicators = {
            'script_tag': 'customily' in page_source and '<script' in page_source,
            'cdn_url': 'cdn.shopify.com' in page_source and 'customily' in page_source,
            'app_url': 'app.customily.com' in page_source,
            'widget': 'customily-widget' in page_source or 'customily_widget' in page_source,
            'js_file': 'customily.js' in page_source,
            'data_attribute': 'data-customily' in page_source
        }
        
        # 检查是否有 Customily 元素
        try:
            customily_elements = driver.find_elements(By.XPATH, "//*[contains(@class, 'customily') or contains(@id, 'customily')]")
            if customily_elements:
                customily_indicators['dom_element'] = True
        except:
            pass
        
        # 检查网络请求（通过 performance logs）
        try:
            logs = driver.get_log('performance')
            for log in logs:
                if 'customily' in str(log).lower():
                    customily_indicators['network_request'] = True
                    break
        except:
            pass
        
        # 判断是否安装了 Customily
        found_indicators = [k for k, v in customily_indicators.items() if v]
        
        if found_indicators:
            details = f"Indicators: {', '.join(found_indicators)}"
            return True, details
        
        return False, "No Customily detected"
        
    except Exception as e:
        return False, f"Error: {str(e)[:100]}"

def update_store_customily_status(conn, domain, has_customily, details):
    """更新店铺的 Customily 状态到数据库"""
    cur = conn.cursor()
    
    try:
        # 检查并创建列
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='stores' AND column_name='has_customily'
        """)
        
        if not cur.fetchone():
            print("Creating has_customily columns...")
            cur.execute("""
                ALTER TABLE stores 
                ADD COLUMN IF NOT EXISTS has_customily BOOLEAN DEFAULT FALSE,
                ADD COLUMN IF NOT EXISTS customily_check_date TIMESTAMP,
                ADD COLUMN IF NOT EXISTS customily_details TEXT
            """)
            conn.commit()
        
        # 更新记录
        cur.execute("""
            UPDATE stores 
            SET has_customily = %s,
                customily_check_date = %s,
                customily_details = %s
            WHERE domain = %s
        """, (has_customily, datetime.now(), details, domain))
        
        conn.commit()
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Database error: {e}")
        return False
    finally:
        cur.close()

def get_stores_to_check(conn, countries=None, limit=None):
    """获取需要检查的店铺"""
    cur = conn.cursor()
    
    query = """
        SELECT domain, country_code, estimated_monthly_visits, city, state
        FROM stores
        WHERE domain IS NOT NULL 
        AND domain != ''
        AND (has_customily IS NULL OR customily_check_date IS NULL)
    """
    
    params = []
    
    if countries:
        placeholders = ','.join(['%s'] * len(countries))
        query += f" AND country_code IN ({placeholders})"
        params.extend(countries)
    
    query += " ORDER BY estimated_monthly_visits DESC NULLS LAST"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cur.execute(query, params)
    stores = cur.fetchall()
    cur.close()
    
    return stores

def main():
    print("=" * 80)
    print("Customily App Detector (Selenium Version)")
    print("=" * 80)
    
    # 连接数据库
    print("\nConnecting to database...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        sys.exit(1)
    
    # 创建 WebDriver
    print("\nInitializing Chrome WebDriver...")
    try:
        driver = create_driver()
        print("✅ WebDriver ready")
    except Exception as e:
        print(f"❌ WebDriver initialization failed: {e}")
        print("\nPlease install ChromeDriver:")
        print("  brew install chromedriver")
        conn.close()
        sys.exit(1)
    
    # 获取店铺列表
    print("\nFetching stores...")
    countries = ['CN', 'HK', 'US']  # 中国、香港、美国
    stores = get_stores_to_check(conn, countries=countries, limit=50)
    
    print(f"Found {len(stores)} stores to check")
    
    if not stores:
        print("No stores to check.")
        driver.quit()
        conn.close()
        return
    
    # 显示示例
    print("\nFirst 5 stores:")
    for i, store in enumerate(stores[:5], 1):
        domain, country, visits, city, state = store
        location = f"{city}, {state}" if city and state else country
        print(f"  {i}. {domain} ({location}) - {visits:,} visits/month")
    
    # 确认
    print("\n" + "=" * 80)
    response = input("Start checking? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        driver.quit()
        conn.close()
        return
    
    # 开始检测
    print("\n" + "=" * 80)
    print("Starting detection...")
    print("=" * 80)
    
    success_count = 0
    customily_found = 0
    
    for i, store in enumerate(stores, 1):
        domain, country, visits, city, state = store
        
        print(f"\n[{i}/{len(stores)}] {domain}...", end=" ")
        
        # 检测
        has_customily, details = check_customily_with_selenium(driver, domain)
        
        if has_customily:
            print(f"✅ CUSTOMILY FOUND!")
            print(f"    Details: {details}")
            customily_found += 1
        else:
            print(f"⭕ No Customily")
        
        # 更新数据库
        if update_store_customily_status(conn, domain, has_customily, details):
            success_count += 1
        
        # 进度报告
        if i % 10 == 0:
            print(f"\n{'='*80}")
            print(f"Progress: {i}/{len(stores)} ({i/len(stores)*100:.1f}%)")
            print(f"Customily found: {customily_found}")
            print(f"{'='*80}")
        
        time.sleep(2)
    
    # 完成
    print("\n" + "=" * 80)
    print("✅ Detection Complete!")
    print("=" * 80)
    print(f"Total: {len(stores)}")
    print(f"Customily found: {customily_found} ({customily_found/len(stores)*100:.1f}%)")
    print(f"Database updates: {success_count}")
    print("=" * 80)
    
    driver.quit()
    conn.close()

if __name__ == "__main__":
    main()
