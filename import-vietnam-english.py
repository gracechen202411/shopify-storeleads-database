import os
import psycopg2
from io import StringIO
import csv
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read database URL from .env
DATABASE_URL = os.getenv('POSTGRES_URL_NON_POOLING')
if not DATABASE_URL:
    print("Error: POSTGRES_URL_NON_POOLING not found in environment")
    print("Trying POSTGRES_URL instead...")
    DATABASE_URL = os.getenv('POSTGRES_URL')
    if not DATABASE_URL:
        print("Error: No database URL found")
        exit(1)

print("Connecting to database...")
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

print("Connected successfully!")

# Read and prepare CSV data
csv_file = 'storeleads/vietnam-english-stores.csv'
print(f"\nReading {csv_file}...")

with open(csv_file, 'r', encoding='utf-8') as f:
    # Skip header
    header = f.readline()

    # Count total lines
    content = f.read()
    total_lines = content.count('\n') + 1

print(f"Found {total_lines:,} stores to import")
print("\nStarting fast import using PostgreSQL COPY...")

try:
    with open(csv_file, 'r', encoding='utf-8') as f:
        # Skip the header line
        next(f)

        # Use COPY command for ultra-fast import
        cur.copy_expert("""
            COPY stores (
                domain, about_us_url, aliases, categories, city, company_location,
                contact_page_url, country_code, created, description, domain_url,
                emails, employee_count, estimated_monthly_visits, estimated_yearly_sales,
                facebook, facebook_url, instagram, instagram_url, language_code,
                linkedin_account, linkedin_url, merchant_name, meta_description,
                phones, pinterest, pinterest_url, plan, platform, platform_rank,
                rank, region, state, status, street_address, tiktok, tiktok_url,
                title, twitter, twitter_url, whatsapp_url, youtube, youtube_url, zip
            )
            FROM STDIN
            WITH (FORMAT CSV, DELIMITER ',', NULL '', QUOTE '"', ESCAPE '"')
        """, f)

    conn.commit()

    # Get final count
    cur.execute("SELECT COUNT(*) FROM stores WHERE country_code = 'VN' AND language_code = 'en'")
    vietnam_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM stores")
    total_count = cur.fetchone()[0]

    print("\n" + "="*60)
    print("✅ Import completed successfully!")
    print(f"Vietnam English stores in database: {vietnam_count:,}")
    print(f"Total stores in database: {total_count:,}")
    print("="*60)

except Exception as e:
    conn.rollback()
    print(f"\n❌ Error during import: {e}")
    raise
finally:
    cur.close()
    conn.close()
