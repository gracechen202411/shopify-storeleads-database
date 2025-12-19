#!/usr/bin/env python3
"""
Fast import using PostgreSQL COPY command
Import stores data 10-20x faster than INSERT
"""

import psycopg2
import os
import sys
from datetime import datetime

DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: Please set DATABASE_URL environment variable")
    print("Run: source .env")
    sys.exit(1)

FILES_TO_IMPORT = [
    ('storeleads/china-hongkong-stores.csv', 'China + Hong Kong'),
    ('storeleads/us-stores-premium-1000plus.csv', 'US Premium (≥1000 visits)'),
]

def fast_import_csv(csv_file, description):
    """Fast import using COPY command"""
    print(f"\n{'='*60}")
    print(f"Fast importing: {description}")
    print(f"File: {csv_file}")
    print(f"{'='*60}")

    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        return 0

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    try:
        start_time = datetime.now()

        # Use COPY command for super fast import
        with open(csv_file, 'r', encoding='utf-8') as f:
            # Skip header
            next(f)

            # COPY command - this is MUCH faster than INSERT
            cur.copy_expert(
                """
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
                """,
                f
            )

        conn.commit()

        # Get count
        cur.execute("SELECT COUNT(*) FROM stores WHERE country_code IN (SELECT DISTINCT country_code FROM (VALUES %s) AS t(code))",
                   (('CN',), ('HK',), ('US',)))
        count = cur.fetchone()[0] if 'china-hongkong' in csv_file else None

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✅ Import completed in {duration:.2f} seconds!")

        cur.close()
        conn.close()

        return 1

    except Exception as e:
        print(f"\n❌ Error during import: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        cur.close()
        conn.close()
        return 0

def main():
    """Main import function"""
    print("\n" + "="*60)
    print("FAST Import Using PostgreSQL COPY Command")
    print("="*60)
    print(f"Target Database: Neon PostgreSQL")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    overall_start = datetime.now()

    for csv_file, description in FILES_TO_IMPORT:
        fast_import_csv(csv_file, description)

    overall_end = datetime.now()
    total_duration = (overall_end - overall_start).total_seconds()

    # Final statistics
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Total time: {total_duration:.2f} seconds ({total_duration/60:.1f} minutes)")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM stores")
        total_count = cur.fetchone()[0]

        cur.execute("SELECT country_code, COUNT(*) FROM stores GROUP BY country_code ORDER BY COUNT(*) DESC")
        countries = cur.fetchall()

        print(f"\nDatabase Statistics:")
        print(f"  Total stores: {total_count:,}")
        print(f"\n  By country:")
        for country, count in countries:
            print(f"    {country}: {count:,}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠ Error getting stats: {e}")

    print("\n✅ Fast import completed successfully!")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Import interrupted by user!")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
