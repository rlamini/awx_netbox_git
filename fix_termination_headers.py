#!/usr/bin/env python3
"""
Fix circuit terminations CSV headers to match NetBox import format
Change 'cid' to 'circuit' as required by NetBox
"""
import csv
from pathlib import Path

term_files = [
    'lab/netbox_dc_circuits_terminations.csv',
    'lab/netbox_circuits_terminations_emea.csv',
    'lab/netbox_circuits_terminations_amer.csv',
    'lab/netbox_circuits_terminations_apac.csv'
]

for term_file in term_files:
    if not Path(term_file).exists():
        continue

    print(f"\nProcessing {term_file}...")

    # Read terminations
    terminations = []
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Rename cid to circuit
            new_row = {
                'circuit': row.get('cid', row.get('circuit', '')),
                'term_side': row['term_side'],
                'site': row['site'],
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': row['description']
            }
            terminations.append(new_row)

    # Write with correct header
    fieldnames = ['circuit', 'term_side', 'site', 'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {len(terminations)} terminations (cid → circuit)")

print("\n✅ All termination files updated with correct header 'circuit'")
