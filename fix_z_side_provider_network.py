#!/usr/bin/env python3
"""
Update Z-side terminations to use provider networks
Z-side should connect to circuits.providernetwork objects
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
    z_side_updated = 0

    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Update Z-side terminations to use provider network
            if row['term_side'] == 'Z':
                row['termination_type'] = 'circuits.providernetwork'
                # termination_id will be the provider network name (NetBox resolves to ID)
                # Extract provider from description
                desc = row['description']
                if 'at ' in desc:
                    provider = desc.split('at ')[-1]
                    row['termination_id'] = provider
                z_side_updated += 1

            terminations.append(row)

    # Write updated terminations
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {z_side_updated} Z-side terminations")
    print(f"     termination_type: circuits.providernetwork")
    print(f"     termination_id: provider network name")

print("\n✅ All Z-side terminations now connect to provider networks")
