#!/usr/bin/env python3
"""
Import selected store data to Neon PostgreSQL:
1. China + Hong Kong stores (59,739)
2. US Premium stores (143,360)
"""

import csv
import psycopg2
import os
import sys
from datetime import datetime

# Database connection
DATABASE_URL = os.environ.get('DATABASE_URL',
    'postgresql://neondb_owner:npg_7kil2gsDbcIf@ep-misty-star-ahewx63v-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require')

# Files to import
FILES_TO_IMPORT = [
    ('storeleads/china-hongkong-stores.csv', 'China + Hong Kong'),
    ('storeleads/us-stores-premium-1000plus.csv', 'US Premium (≥1000 visits)'),
]

def clean_value(value):
    """Clean and prepare value for database insertion"""
    if value is None or value == '':
        return None
    # Remove extra whitespace
    value = value.strip()
    if value == '':
        return None
    return value

def parse_int(value):
    """Parse integer value"""
    if not value:
        return None
    try:
        return int(value)
    except (ValueError, TypeError):
        return None

def import_csv_to_db(csv_file, description):
    """Import CSV file to database"""
    print(f"\n{'='*60}")
    print(f"Importing: {description}")
    print(f"File: {csv_file}")
    print(f"{'='*60}\n")

    if not os.path.exists(csv_file):
        print(f"❌ Error: File not found: {csv_file}")
        return 0

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Prepare INSERT statement
    insert_sql = """
        INSERT INTO stores (
            domain, about_us_url, aliases, categories, city, company_location,
            contact_page_url, country_code, created, description, domain_url,
            emails, employee_count, estimated_monthly_visits, estimated_yearly_sales,
            facebook, facebook_url, instagram, instagram_url, language_code,
            linkedin_account, linkedin_url, merchant_name, meta_description,
            phones, pinterest, pinterest_url, plan, platform, platform_rank,
            rank, region, state, status, street_address, tiktok, tiktok_url,
            title, twitter, twitter_url, whatsapp_url, youtube, youtube_url, zip
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s
        )
        ON CONFLICT (domain) DO NOTHING
    """

    imported_count = 0
    skipped_count = 0
    error_count = 0

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        batch = []
        batch_size = 1000

        for row_num, row in enumerate(reader, start=1):
            try:
                # Prepare values
                values = (
                    clean_value(row.get('domain')),
                    clean_value(row.get('about_us_url')),
                    clean_value(row.get('aliases')),
                    clean_value(row.get('categories')),
                    clean_value(row.get('city')),
                    clean_value(row.get('company_location')),
                    clean_value(row.get('contact_page_url')),
                    clean_value(row.get('country_code')),
                    clean_value(row.get('created')),
                    clean_value(row.get('description')),
                    clean_value(row.get('domain_url')),
                    clean_value(row.get('emails')),
                    parse_int(row.get('employee_count')),
                    parse_int(row.get('estimated_monthly_visits')),
                    clean_value(row.get('estimated_yearly_sales')),
                    clean_value(row.get('facebook')),
                    clean_value(row.get('facebook_url')),
                    clean_value(row.get('instagram')),
                    clean_value(row.get('instagram_url')),
                    clean_value(row.get('language_code')),
                    clean_value(row.get('linkedin_account')),
                    clean_value(row.get('linkedin_url')),
                    clean_value(row.get('merchant_name')),
                    clean_value(row.get('meta_description')),
                    clean_value(row.get('phones')),
                    clean_value(row.get('pinterest')),
                    clean_value(row.get('pinterest_url')),
                    clean_value(row.get('plan')),
                    clean_value(row.get('platform')),
                    parse_int(row.get('platform_rank')),
                    parse_int(row.get('rank')),
                    clean_value(row.get('region')),
                    clean_value(row.get('state')),
                    clean_value(row.get('status')),
                    clean_value(row.get('street_address')),
                    clean_value(row.get('tiktok')),
                    clean_value(row.get('tiktok_url')),
                    clean_value(row.get('title')),
                    clean_value(row.get('twitter')),
                    clean_value(row.get('twitter_url')),
                    clean_value(row.get('whatsapp_url')),
                    clean_value(row.get('youtube')),
                    clean_value(row.get('youtube_url')),
                    clean_value(row.get('zip')),
                )

                batch.append(values)

                # Execute batch
                if len(batch) >= batch_size:
                    try:
                        cur.executemany(insert_sql, batch)
                        conn.commit()
                        imported_count += len(batch)
                        batch = []

                        if imported_count % 10000 == 0:
                            print(f"  ✓ Imported {imported_count:,} rows...")
                    except Exception as e:
                        print(f"  ⚠ Batch error at row {row_num}: {e}")
                        conn.rollback()
                        error_count += len(batch)
                        batch = []

            except Exception as e:
                print(f"  ⚠ Row {row_num} error: {e}")
                error_count += 1

        # Insert remaining batch
        if batch:
            try:
                cur.executemany(insert_sql, batch)
                conn.commit()
                imported_count += len(batch)
            except Exception as e:
                print(f"  ⚠ Final batch error: {e}")
                conn.rollback()
                error_count += len(batch)

    cur.close()
    conn.close()

    print(f"\n{'='*60}")
    print(f"Import completed for: {description}")
    print(f"  ✓ Successfully imported: {imported_count:,} rows")
    if error_count > 0:
        print(f"  ⚠ Errors: {error_count:,} rows")
    print(f"{'='*60}\n")

    return imported_count

def main():
    """Main import function"""
    print("\n" + "="*60)
    print("Starting Shopify Store Data Import")
    print("="*60)
    print(f"Target Database: Neon PostgreSQL")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    total_imported = 0

    for csv_file, description in FILES_TO_IMPORT:
        imported = import_csv_to_db(csv_file, description)
        total_imported += imported

    # Final statistics
    print("\n" + "="*60)
    print("FINAL SUMMARY")
    print("="*60)
    print(f"Total records imported: {total_imported:,}")
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Query database for stats
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM stores")
        total_count = cur.fetchone()[0]

        cur.execute("SELECT COUNT(DISTINCT country_code) FROM stores")
        country_count = cur.fetchone()[0]

        cur.execute("SELECT country_code, COUNT(*) FROM stores GROUP BY country_code ORDER BY COUNT(*) DESC LIMIT 5")
        top_countries = cur.fetchall()

        print(f"\nDatabase Statistics:")
        print(f"  Total stores in database: {total_count:,}")
        print(f"  Unique countries: {country_count}")
        print(f"\n  Top 5 countries:")
        for country, count in top_countries:
            print(f"    {country or '(empty)'}: {count:,}")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠ Error getting database stats: {e}")

    print("\n✅ Import process completed successfully!")
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
