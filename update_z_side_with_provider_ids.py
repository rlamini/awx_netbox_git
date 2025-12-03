#!/usr/bin/env python3
"""
Update Z-side terminations to use provider network numeric IDs
"""
import csv
from pathlib import Path

# Provider network name to ID mapping from NetBox export
provider_to_id = {
    'GTT Communications': '1',
    'Zayo Group': '2',
    'Telia Carrier': '3',
    'Telstra Global': '4',
    'Singtel': '5',
    'China Telecom Global': '6',
    'Crown Castle Fiber': '7',
    'Orange Business Services': '8',
    'Colt Technology': '9',
    'NTT Communications': '10',
    'PCCW Global': '11',
    'Lumen Technologies': '12',
    'Cogent Communications': '13'
}

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
            # Update Z-side terminations with numeric provider network IDs
            if row['term_side'] == 'Z':
                # termination_id should already have the provider name
                provider_name = row['termination_id']
                if provider_name in provider_to_id:
                    row['termination_id'] = provider_to_id[provider_name]
                    z_side_updated += 1
                else:
                    print(f"  ⚠️  Warning: Provider '{provider_name}' not found in mapping")

            terminations.append(row)

    # Write updated terminations
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Updated {z_side_updated} Z-side terminations with numeric provider network IDs")

print("\n✅ All Z-side terminations now use numeric provider network IDs")
