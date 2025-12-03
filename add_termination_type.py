#!/usr/bin/env python3
"""
Add termination_type field to circuit terminations
A-side terminations connecting to sites need termination_type = dcim.site
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
            # Add termination_type field
            new_row = {
                'circuit': row['circuit'],
                'term_side': row['term_side'],
                'termination_type': 'dcim.site' if row['term_side'] == 'A' and row.get('site') else '',
                'site': row.get('site', ''),
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': row['description']
            }
            terminations.append(new_row)

    # Write with termination_type field
    fieldnames = ['circuit', 'term_side', 'termination_type', 'site', 'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    a_side_count = len([t for t in terminations if t['term_side'] == 'A'])
    print(f"  ✅ Updated {len(terminations)} terminations")
    print(f"     {a_side_count} A-side with termination_type=dcim.site")

print("\n✅ All termination files updated with termination_type field")
