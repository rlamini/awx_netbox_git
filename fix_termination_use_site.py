#!/usr/bin/env python3
"""
Fix circuit terminations to use site field instead of termination_id
NetBox should resolve site names to IDs automatically
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
            # Use site field instead of termination_id
            new_row = {
                'circuit': row['circuit'],
                'term_side': row['term_side'],
                'site': row.get('termination_id', row.get('site', '')),
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': row['description']
            }
            terminations.append(new_row)

    # Write simplified format with site field
    fieldnames = ['circuit', 'term_side', 'site', 'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {len(terminations)} terminations")
    print(f"     Using 'site' field with site name (NetBox resolves to ID)")

print("\n✅ All termination files updated to use 'site' field")
print("   NetBox should automatically resolve site names to IDs during import")
