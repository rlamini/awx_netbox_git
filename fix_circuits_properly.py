#!/usr/bin/env python3
"""
Properly fix circuits and terminations:
1. Simplify terminations to only necessary fields (no optional fields)
2. Extract site from terminations and add to circuits CSV
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

    print(f"\n{'='*60}")
    print(f"Processing {Path(circuit_file).name}")
    print(f"{'='*60}")

    # Step 1: Extract site info from A-side terminations
    circuit_to_site = {}
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['term_side'] == 'A':
                # Extract site from description (e.g., "A-side termination at EMEA-DC-CLOUD")
                desc = row['description']
                if 'at ' in desc:
                    site = desc.split('at ')[-1].strip()
                    circuit_to_site[row['cid']] = site

    print(f"  Found {len(circuit_to_site)} circuits with site info")

    # Step 2: Update circuits file to add site field
    circuits = []
    with open(circuit_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        # Add 'site' field if not present
        if 'site' not in fieldnames:
            fieldnames = list(fieldnames)
            # Insert site after status
            status_idx = fieldnames.index('status') if 'status' in fieldnames else 3
            fieldnames.insert(status_idx + 1, 'site')

        for row in reader:
            # Add site if we have it
            row['site'] = circuit_to_site.get(row['cid'], '')
            circuits.append(row)

    # Write updated circuits file
    with open(circuit_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(circuits)

    print(f"  ✅ Updated {len(circuits)} circuits with site field")

    # Step 3: Simplify terminations - only necessary fields, no optional
    terminations = []
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            simple_row = {
                'cid': row['cid'],
                'term_side': row['term_side'],
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': row['description']
            }
            terminations.append(simple_row)

    # Write simplified terminations
    simple_fieldnames = ['cid', 'term_side', 'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=simple_fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {len(terminations)} terminations (only necessary fields)")

print("\n" + "="*60)
print("✅ All files updated:")
print("   - Circuits now have 'site' field")
print("   - Terminations simplified (no optional fields)")
print("="*60)
