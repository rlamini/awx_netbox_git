#!/usr/bin/env python3
"""
Add termination_type and termination_id to circuit terminations
termination_type = dcim.site
termination_id = site name (NetBox will resolve to ID during import)
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
            # Add termination_type and termination_id
            site = row.get('site', '')
            new_row = {
                'circuit': row['circuit'],
                'term_side': row['term_side'],
                'termination_type': 'dcim.site',
                'termination_id': site,  # Site name - NetBox resolves to ID during import
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': row['description']
            }
            terminations.append(new_row)

    # Write with termination_type and termination_id
    fieldnames = ['circuit', 'term_side', 'termination_type', 'termination_id',
                  'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {len(terminations)} terminations")
    print(f"     termination_type: dcim.site")
    print(f"     termination_id: site name")

print("\n✅ All termination files updated with termination_type and termination_id")
