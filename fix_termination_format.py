#!/usr/bin/env python3
"""
Fix circuit termination CSV files to match NetBox expected format

Current format:
  circuit,term_side,site,port_speed,upstream_speed,description

NetBox expected format:
  cid,term_side,termination_type,termination_id,port_speed,upstream_speed,xconnect_id,pp_info,description,tags
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

    # Read existing terminations
    terminations = []
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert to new format
            new_row = {
                'cid': row['circuit'],  # Rename circuit to cid
                'term_side': row['term_side'],
                'termination_type': '',  # Leave empty for now
                'termination_id': '',    # Leave empty for now
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'xconnect_id': '',       # Optional field
                'pp_info': '',           # Optional field
                'description': row['description'],
                'tags': ''               # Optional field
            }
            terminations.append(new_row)

    # Write with new format
    new_fieldnames = ['cid', 'term_side', 'termination_type', 'termination_id',
                      'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
                      'description', 'tags']

    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {len(terminations)} terminations")
    print(f"  Changed headers: circuit→cid, removed site, added termination_type, termination_id, xconnect_id, pp_info, tags")

print("\n✅ All circuit termination files updated to NetBox format")
