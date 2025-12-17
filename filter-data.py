#!/usr/bin/env python3
"""
Filter and merge CSV data to fit within 500MB for Neon free tier
Keeps only the most valuable stores based on:
- Active status
- Has monthly visits data
- Has employee count
- Sorts by monthly visits (top stores first)
"""
import csv
import os
from pathlib import Path

# Configuration
CHUNKS_DIR = "/Users/grace/Downloads/ALL/下载ALLLL/chunks"
OUTPUT_FILE = "/Users/grace/Downloads/ALL/下载ALLLL/shopify-storeleads-filtered.csv"
TARGET_SIZE_MB = 450  # Leave some buffer for the 500MB limit
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024

def get_sort_key(row):
    """Get sort key for prioritizing stores"""
    try:
        visits = int(row.get('estimated_monthly_visits', 0) or 0)
    except:
        visits = 0

    try:
        employees = int(row.get('employee_count', 0) or 0)
    except:
        employees = 0

    # Prioritize: active, has visits, has employees
    is_active = 1 if row.get('status') == 'Active' else 0
    has_visits = 1 if visits > 0 else 0
    has_employees = 1 if employees > 0 else 0

    # Sort key: (active, has_visits, has_employees, visits, employees)
    return (is_active, has_visits, has_employees, visits, employees)

def filter_and_merge():
    """Filter and merge CSV files"""
    print(f"Reading all CSV chunks from {CHUNKS_DIR}...")
    print(f"Target size: {TARGET_SIZE_MB}MB")

    all_rows = []
    header = None

    # Read all CSV files
    csv_files = sorted(Path(CHUNKS_DIR).glob("shopify-storeleads-part*.csv"))

    if not csv_files:
        print(f"ERROR: No CSV files found in {CHUNKS_DIR}")
        return

    print(f"Found {len(csv_files)} CSV files")

    for csv_file in csv_files:
        print(f"  Reading {csv_file.name}...")
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if header is None:
                header = reader.fieldnames

            for row in reader:
                # Basic filtering - skip obviously low-value stores
                status = row.get('status', '')
                visits = row.get('estimated_monthly_visits', '')

                # Keep if active OR has significant visits
                if status == 'Active' or (visits and visits.isdigit() and int(visits) > 1000):
                    all_rows.append(row)

    print(f"\nTotal rows after basic filtering: {len(all_rows):,}")

    # Sort by value (most valuable stores first)
    print("Sorting by value (monthly visits, employee count, etc.)...")
    all_rows.sort(key=get_sort_key, reverse=True)

    # Write filtered data until we reach target size
    print(f"Writing filtered data to {OUTPUT_FILE}...")

    current_size = 0
    rows_written = 0

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)

        # Write header
        writer.writeheader()
        header_size = f.tell()
        current_size = header_size

        for row in all_rows:
            # Estimate row size
            row_str = ','.join(str(v) for v in row.values()) + '\n'
            row_size = len(row_str.encode('utf-8'))

            # Check if we would exceed target size
            if current_size + row_size > TARGET_SIZE_BYTES:
                break

            writer.writerow(row)
            current_size += row_size
            rows_written += 1

            if rows_written % 10000 == 0:
                print(f"  Written {rows_written:,} rows ({current_size/1024/1024:.1f}MB)...")

    print(f"\n✓ Filtering complete!")
    print(f"  Total rows written: {rows_written:,}")
    print(f"  File size: {current_size/1024/1024:.1f}MB")
    print(f"  Output file: {OUTPUT_FILE}")
    print(f"\nThis file can be imported to Neon free tier (500MB limit)")

    # Show some statistics
    print(f"\n📊 Statistics:")
    active_count = sum(1 for row in all_rows[:rows_written] if row.get('status') == 'Active')
    with_visits = sum(1 for row in all_rows[:rows_written]
                     if row.get('estimated_monthly_visits', '').isdigit()
                     and int(row.get('estimated_monthly_visits', 0)) > 0)

    print(f"  Active stores: {active_count:,} ({active_count/rows_written*100:.1f}%)")
    print(f"  Stores with visit data: {with_visits:,} ({with_visits/rows_written*100:.1f}%)")

    if rows_written > 0:
        # Get top store info
        top_store = all_rows[0]
        print(f"\n🏆 Top store:")
        print(f"  Name: {top_store.get('merchant_name', 'N/A')}")
        print(f"  Domain: {top_store.get('domain', 'N/A')}")
        print(f"  Monthly visits: {top_store.get('estimated_monthly_visits', 'N/A')}")
        print(f"  Employees: {top_store.get('employee_count', 'N/A')}")

if __name__ == "__main__":
    filter_and_merge()
