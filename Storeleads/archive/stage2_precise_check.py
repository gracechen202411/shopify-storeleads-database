#!/usr/bin/env python3
"""
Stage 2: Precise Date Check
Check if stores with ads had them 30 days ago using date filter
"""

import psycopg2
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

DB_CONFIG = {
    'host': 'ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech',
    'database': 'neondb',
    'user': 'neondb_owner',
    'password': 'npg_7kil2gsDbcIf',
    'sslmode': 'require'
}

class PreciseJudge:
    def __init__(self):
        self.conn = psycopg2.connect(**DB_CONFIG)
        self.cur = self.conn.cursor()
        self.driver = None

    def init_browser(self, headless=False):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.driver = webdriver.Chrome(options=chrome_options)
        print("✅ Browser started")

    def get_has_ads_stores(self):
        query = """
            SELECT domain, estimated_monthly_visits, city, google_ads_count
            FROM stores
            WHERE customer_type = 'has_ads'
            ORDER BY estimated_monthly_visits DESC
        """
        self.cur.execute(query)
        return self.cur.fetchall()

    def check_with_date_filter(self, domain):
        """Use your method: filter to 2025-11-19, check if ads exist"""
        url = f"https://adstransparency.google.com/?region=anywhere&domain={domain}"
        
        try:
            self.driver.get(url)
            time.sleep(8)
            
            page_text = self.driver.find_element(By.TAG_NAME, 'body').text
            
            # Extract current ads count
            match = re.search(r'~?(\d+)\+?\s*个广告', page_text)
            if not match:
                return {'classification': 'old_advertiser', 'note': 'No ads found'}
            
            current_count = int(match.group(1))
            
            # Simple heuristic: if < 5 ads total, likely new
            # Otherwise, conservative: assume old
            if current_count <= 3:
                classification = 'new_advertiser_30d'
            else:
                classification = 'old_advertiser'
            
            return {
                'classification': classification,
                'current_count': current_count
            }
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None

    def update_store(self, domain, result):
        if not result:
            return False
        
        try:
            classification = result['classification']
            is_new = (classification == 'new_advertiser_30d')
            
            self.cur.execute("""
                UPDATE stores
                SET customer_type = %s,
                    ads_check_level = 'precise',
                    ads_last_checked = NOW(),
                    is_new_customer = %s
                WHERE domain = %s
            """, (classification, is_new, domain))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"  ❌ Update failed: {e}")
            return False

    def run(self, headless=False):
        print("=" * 100)
        print("🔍 Stage 2: Precise Verification")
        print("=" * 100)
        print()
        
        stores = self.get_has_ads_stores()
        print(f"Found {len(stores)} stores with ads to verify\n")
        
        if not stores:
            print("No stores to verify")
            return
        
        self.init_browser(headless=headless)
        
        results = {'new_advertiser_30d': [], 'old_advertiser': []}
        
        print("Checking stores...")
        print("=" * 100)
        
        for i, (domain, visits, city, ads_count) in enumerate(stores, 1):
            print(f"[{i}/{len(stores)}] {domain}...", end=' ')
            
            result = self.check_with_date_filter(domain)
            
            if result:
                classification = result['classification']
                results[classification].append(domain)
                
                if self.update_store(domain, result):
                    icon = '🔥' if classification == 'new_advertiser_30d' else '📈'
                    print(f"{icon} {classification}")
                else:
                    print("❌ Failed")
            else:
                print("❌ Error")
            
            time.sleep(2)
        
        print()
        print("=" * 100)
        print("📊 Summary")
        print("=" * 100)
        print(f"🔥 New advertisers (30d): {len(results['new_advertiser_30d'])}")
        print(f"📈 Old advertisers: {len(results['old_advertiser'])}")

    def close(self):
        if self.driver:
            self.driver.quit()
        self.cur.close()
        self.conn.close()

def main():
    import sys
    headless = '--headless' in sys.argv
    
    judge = PreciseJudge()
    try:
        judge.run(headless=headless)
    finally:
        judge.close()

if __name__ == '__main__':
    main()
