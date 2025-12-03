#!/usr/bin/env python3
"""
Fix circuit terminations to properly reference sites
NetBox requires termination_type and site name for A-side terminations
"""
import csv
from pathlib import Path

circuit_files = [
    ('lab/netbox_dc_circuits.csv', 'lab/netbox_dc_circuits_terminations.csv'),
    ('lab/netbox_circuits_emea.csv', 'lab/netbox_circuits_terminations_emea.csv'),
    ('lab/dc/netbox_circuits_amer.csv', 'lab/netbox_circuits_terminations_amer.csv'),
    ('lab/netbox_circuits_apac.csv', 'lab/netbox_circuits_terminations_apac.csv'),
]

for circuit_file, term_file in circuit_files:
    if not Path(circuit_file).exists() or not Path(term_file).exists():
        continue

    print(f"\nProcessing {term_file}...")

    # Read circuits to get site associations
    circuit_to_site = {}
    with open(circuit_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if 'site' in row and row['site']:
                circuit_to_site[row['cid']] = row['site']

    # Update terminations with site references
    terminations = []
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # For A-side terminations, add site reference
            if row['term_side'] == 'A':
                site = circuit_to_site.get(row['cid'], '')
                new_row = {
                    'cid': row['cid'],
                    'term_side': row['term_side'],
                    'site': site,  # Site name for A-side
                    'port_speed': row['port_speed'],
                    'upstream_speed': row['upstream_speed'],
                    'description': row['description']
                }
            else:
                # Z-side has no site
                new_row = {
                    'cid': row['cid'],
                    'term_side': row['term_side'],
                    'site': '',
                    'port_speed': row['port_speed'],
                    'upstream_speed': row['upstream_speed'],
                    'description': row['description']
                }
            terminations.append(new_row)

    # Write with site field
    fieldnames = ['cid', 'term_side', 'site', 'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {len(terminations)} terminations with site references")

print("\n✅ All termination files updated with site field for A-side terminations")
