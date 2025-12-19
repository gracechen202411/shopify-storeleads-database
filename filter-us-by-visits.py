#!/usr/bin/env python3
"""
Filter US stores by monthly visits:
- Premium stores (monthly visits >= 1000)
- Regular stores (monthly visits < 1000 or no data)
"""

import csv
import os
from collections import defaultdict

# Input file
INPUT_FILE = 'storeleads/us-stores.csv'

# Output files
OUTPUT_PREMIUM = 'storeleads/us-stores-premium-1000plus.csv'
OUTPUT_REGULAR = 'storeleads/us-stores-regular.csv'

# Threshold
VISIT_THRESHOLD = 1000

def filter_by_visits():
    """Filter US stores by monthly visit threshold"""

    print(f"Reading from: {INPUT_FILE}")
    print(f"Filtering by monthly visits >= {VISIT_THRESHOLD:,}\n")

    # Statistics
    stats = defaultdict(int)

    # Open all files
    with open(INPUT_FILE, 'r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        # Get header
        fieldnames = reader.fieldnames

        # Open output files
        premium_file = open(OUTPUT_PREMIUM, 'w', encoding='utf-8', newline='')
        regular_file = open(OUTPUT_REGULAR, 'w', encoding='utf-8', newline='')

        # Create writers
        premium_writer = csv.DictWriter(premium_file, fieldnames=fieldnames)
        regular_writer = csv.DictWriter(regular_file, fieldnames=fieldnames)

        # Write headers
        premium_writer.writeheader()
        regular_writer.writeheader()

        # Process each row
        row_count = 0
        for row in reader:
            row_count += 1

            # Show progress every 50k rows
            if row_count % 50000 == 0:
                print(f"Processed {row_count:,} rows...")

            # Get monthly visits
            visits_str = row.get('estimated_monthly_visits', '').strip()

            try:
                if visits_str:
                    visits = int(visits_str)
                    if visits >= VISIT_THRESHOLD:
                        premium_writer.writerow(row)
                        stats['premium'] += 1
                    else:
                        regular_writer.writerow(row)
                        stats['regular'] += 1
                else:
                    # No visit data - goes to regular
                    regular_writer.writerow(row)
                    stats['regular'] += 1
                    stats['no_data'] += 1
            except ValueError:
                # Invalid visit data - goes to regular
                regular_writer.writerow(row)
                stats['regular'] += 1
                stats['invalid_data'] += 1

        # Close files
        premium_file.close()
        regular_file.close()

    # Print statistics
    print(f"\n{'='*60}")
    print(f"Filtering completed!")
    print(f"{'='*60}")
    print(f"Total rows processed: {row_count:,}")
    print(f"\nBreakdown:")
    print(f"  Premium stores (≥{VISIT_THRESHOLD:,} visits): {stats['premium']:,} ({stats['premium']/row_count*100:.1f}%)")
    print(f"  Regular stores: {stats['regular']:,} ({stats['regular']/row_count*100:.1f}%)")
    print(f"    - No visit data: {stats['no_data']:,}")
    print(f"    - Invalid data: {stats['invalid_data']:,}")

    print(f"\nOutput files:")
    print(f"  {OUTPUT_PREMIUM}")
    print(f"  {OUTPUT_REGULAR}")

    # Show file sizes
    print(f"\nFile sizes:")
    for filepath in [OUTPUT_PREMIUM, OUTPUT_REGULAR]:
        if os.path.exists(filepath):
            size_mb = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  {os.path.basename(filepath)}: {size_mb:.1f} MB")

    print(f"\n✅ Premium file is {'UNDER' if size_mb < 500 else 'OVER'} 500MB limit for Neon free tier!")

if __name__ == '__main__':
    try:
        filter_by_visits()
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user!")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
