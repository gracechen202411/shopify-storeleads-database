import csv
import sys

input_file = 'storeleads/other-countries-stores.csv'
output_file = 'storeleads/vietnam-english-stores.csv'

print(f"Reading from: {input_file}")
print(f"Filtering for: Country=VN, Language=en")
print("Starting filtering process...")

vietnam_english_count = 0
total_rows = 0

with open(input_file, 'r', encoding='utf-8') as infile, \
     open(output_file, 'w', encoding='utf-8', newline='') as outfile:

    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    writer.writeheader()

    for row in reader:
        total_rows += 1

        # Filter: country_code = VN and language_code = en
        if row.get('country_code', '').upper() == 'VN' and row.get('language_code', '').lower() == 'en':
            writer.writerow(row)
            vietnam_english_count += 1

        # Progress update every 100k rows
        if total_rows % 100000 == 0:
            print(f"Processed {total_rows:,} rows, found {vietnam_english_count:,} Vietnam English stores")

print("\n" + "="*60)
print(f"Filtering complete!")
print(f"Total rows processed: {total_rows:,}")
print(f"Vietnam English stores found: {vietnam_english_count:,}")
print(f"Output file: {output_file}")
print("="*60)
