#!/usr/bin/env python3
"""
Import CSV data to Neon PostgreSQL database
Usage: python import-to-neon.py <csv_file_path>
"""
import os
import sys
import csv
import psycopg2
from psycopg2.extras import execute_batch
from datetime import datetime

# Database connection - Set these environment variables
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    print("ERROR: Please set DATABASE_URL environment variable")
    print("Example: export DATABASE_URL='postgresql://user:password@host/dbname'")
    sys.exit(1)

def parse_date(date_str):
    """Parse date string from CSV"""
    if not date_str or date_str.strip() == '':
        return None
    try:
        return datetime.strptime(date_str, '%Y/%m/%d').date()
    except:
        return None

def parse_int(value):
    """Parse integer value"""
    if not value or value.strip() == '':
        return None
    try:
        return int(value)
    except:
        return None

def import_csv_to_database(csv_file_path, batch_size=1000):
    """Import CSV file to PostgreSQL database"""
    print(f"Connecting to database...")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # SQL insert statement
    insert_sql = """
        INSERT INTO stores (
            domain, about_us_url, aliases, categories, city, company_location,
            contact_page_url, country_code, created, description, domain_url,
            emails, employee_count, estimated_monthly_visits, estimated_yearly_sales,
            facebook, facebook_url, instagram, instagram_url, language_code,
            linkedin_account, linkedin_url, merchant_name, meta_description, phones,
            pinterest, pinterest_url, plan, platform, platform_rank, rank, region,
            state, status, street_address, tiktok, tiktok_url, title, twitter,
            twitter_url, whatsapp_url, youtube, youtube_url, zip
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (domain) DO NOTHING;
    """

    try:
        print(f"Opening CSV file: {csv_file_path}")
        with open(csv_file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            batch = []
            total_processed = 0
            total_inserted = 0

            for row in reader:
                # Prepare data tuple
                data = (
                    row.get('domain'),
                    row.get('about_us_url'),
                    row.get('aliases'),
                    row.get('categories'),
                    row.get('city'),
                    row.get('company_location'),
                    row.get('contact_page_url'),
                    row.get('country_code'),
                    parse_date(row.get('created')),
                    row.get('description'),
                    row.get('domain_url'),
                    row.get('emails'),
                    parse_int(row.get('employee_count')),
                    parse_int(row.get('estimated_monthly_visits')),
                    row.get('estimated_yearly_sales'),
                    row.get('facebook'),
                    row.get('facebook_url'),
                    row.get('instagram'),
                    row.get('instagram_url'),
                    row.get('language_code'),
                    row.get('linkedin_account'),
                    row.get('linkedin_url'),
                    row.get('merchant_name'),
                    row.get('meta_description'),
                    row.get('phones'),
                    row.get('pinterest'),
                    row.get('pinterest_url'),
                    row.get('plan'),
                    row.get('platform'),
                    parse_int(row.get('platform_rank')),
                    parse_int(row.get('rank')),
                    row.get('region'),
                    row.get('state'),
                    row.get('status'),
                    row.get('street_address'),
                    row.get('tiktok'),
                    row.get('tiktok_url'),
                    row.get('title'),
                    row.get('twitter'),
                    row.get('twitter_url'),
                    row.get('whatsapp_url'),
                    row.get('youtube'),
                    row.get('youtube_url'),
                    row.get('zip')
                )

                batch.append(data)
                total_processed += 1

                # Execute batch insert
                if len(batch) >= batch_size:
                    execute_batch(cur, insert_sql, batch)
                    conn.commit()
                    total_inserted += len(batch)
                    print(f"  Processed {total_processed:,} rows, inserted {total_inserted:,} rows...")
                    batch = []

            # Insert remaining rows
            if batch:
                execute_batch(cur, insert_sql, batch)
                conn.commit()
                total_inserted += len(batch)

            print(f"\n✓ Import complete!")
            print(f"  Total rows processed: {total_processed:,}")
            print(f"  Total rows inserted: {total_inserted:,}")

    except Exception as e:
        print(f"ERROR: {e}")
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import-to-neon.py <csv_file_path>")
        print("\nTo import all chunks:")
        print("  for file in chunks/*.csv; do python import-to-neon.py \"$file\"; done")
        sys.exit(1)

    csv_file = sys.argv[1]
    if not os.path.exists(csv_file):
        print(f"ERROR: File not found: {csv_file}")
        sys.exit(1)

    import_csv_to_database(csv_file)
