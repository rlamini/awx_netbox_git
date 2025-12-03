#!/usr/bin/env python3
"""
Fix circuit terminations to match NetBox CSV import format exactly
Remove Z-side terminations (they don't connect to any object)
Keep only A-side with proper termination_type and site reference
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

    # Read terminations and keep only A-side
    terminations = []
    a_count = 0
    z_count = 0

    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['term_side'] == 'A':
                # Keep A-side terminations with site reference
                new_row = {
                    'circuit': row['circuit'],
                    'term_side': row['term_side'],
                    'site': row.get('site', ''),
                    'port_speed': row['port_speed'],
                    'upstream_speed': row['upstream_speed'],
                    'description': row['description']
                }
                terminations.append(new_row)
                a_count += 1
            else:
                z_count += 1

    # Write simplified format without Z-side
    fieldnames = ['circuit', 'term_side', 'site', 'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Kept {a_count} A-side terminations (removed {z_count} Z-side)")
    print(f"     A-side terminations reference sites directly")

print("\n✅ All termination files updated:")
print("   - Only A-side terminations (with site references)")
print("   - Removed Z-side terminations (no terminating object)")
print("   - Z-side can be added later via NetBox UI if needed")
