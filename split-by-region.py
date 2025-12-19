#!/usr/bin/env python3
"""
Split Shopify store leads CSV by region:
- China + Hong Kong (CN, HK)
- United States (US)
- Other countries
"""

import csv
import os
from collections import defaultdict

# Input file
INPUT_FILE = 'storeleads/shopify-storeleads.csv'

# Output files
OUTPUT_CHINA_HK = 'storeleads/china-hongkong-stores.csv'
OUTPUT_US = 'storeleads/us-stores.csv'
OUTPUT_OTHER = 'storeleads/other-countries-stores.csv'

# Region definitions
CHINA_HK_CODES = {'CN', 'HK'}
US_CODE = 'US'

def split_csv_by_region():
    """Split CSV file into three regional files"""

    print(f"Reading from: {INPUT_FILE}")
    print(f"Splitting into 3 regions...\n")

    # Statistics
    stats = defaultdict(int)

    # Open all output files
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Get header
        fieldnames = reader.fieldnames

        # Open output files
        china_hk_file = open(OUTPUT_CHINA_HK, 'w', encoding='utf-8', newline='')
        us_file = open(OUTPUT_US, 'w', encoding='utf-8', newline='')
        other_file = open(OUTPUT_OTHER, 'w', encoding='utf-8', newline='')

        # Create writers
        china_hk_writer = csv.DictWriter(china_hk_file, fieldnames=fieldnames)
        us_writer = csv.DictWriter(us_file, fieldnames=fieldnames)
        other_writer = csv.DictWriter(other_file, fieldnames=fieldnames)

        # Write headers
        china_hk_writer.writeheader()
        us_writer.writeheader()
        other_writer.writeheader()

        # Process each row
        row_count = 0
        for row in reader:
            row_count += 1

            # Show progress every 100k rows
            if row_count % 100000 == 0:
                print(f"Processed {row_count:,} rows...")

            country_code = row.get('country_code', '').strip().upper()

            # Route to appropriate file
            if country_code in CHINA_HK_CODES:
                china_hk_writer.writerow(row)
                stats['china_hk'] += 1
            elif country_code == US_CODE:
                us_writer.writerow(row)
                stats['us'] += 1
            else:
                other_writer.writerow(row)
                stats['other'] += 1

        # Close files
        china_hk_file.close()
        us_file.close()
        other_file.close()

    # Print statistics
    print(f"\n{'='*60}")
    print(f"Splitting completed!")
    print(f"{'='*60}")
    print(f"Total rows processed: {row_count:,}")
    print(f"\nRegion breakdown:")
    print(f"  China + Hong Kong: {stats['china_hk']:,} rows")
    print(f"  United States:     {stats['us']:,} rows")
    print(f"  Other countries:   {stats['other']:,} rows")
    print(f"\nOutput files:")
    print(f"  {OUTPUT_CHINA_HK}")
    print(f"  {OUTPUT_US}")
    print(f"  {OUTPUT_OTHER}")

    # Show file sizes
    print(f"\nFile sizes:")
    for filepath in [OUTPUT_CHINA_HK, OUTPUT_US, OUTPUT_OTHER]:
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  {os.path.basename(filepath)}: {size_mb:.1f} MB")

if __name__ == '__main__':
    try:
        split_csv_by_region()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
