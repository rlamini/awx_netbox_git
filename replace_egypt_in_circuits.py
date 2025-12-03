#!/usr/bin/env python3
"""
Replace Egypt (EG) with Algeria (DZ) in circuits CSV files
"""
import csv
from pathlib import Path

circuit_files = [
    'lab/netbox_dc_circuits.csv',
    'lab/netbox_circuits_emea.csv',
    'lab/dc/netbox_circuits_amer.csv',
    'lab/netbox_circuits_apac.csv'
]

for circuit_file in circuit_files:
    if not Path(circuit_file).exists():
        continue

    print(f"\nProcessing {circuit_file}...")

    # Read circuits
    circuits = []
    replaced_count = 0

    with open(circuit_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Replace EG with DZ in cid
            cid = row['cid']
            if 'EG-Agency' in cid:
                old_cid = cid
                cid = cid.replace('EG-Agency', 'DZ-Agency')
                replaced_count += 1
                print(f"  Circuit: {old_cid} → {cid}")
                row['cid'] = cid

            # Replace EG with DZ in site
            if 'site' in row and 'EG-Agency' in row['site']:
                old_site = row['site']
                row['site'] = row['site'].replace('EG-Agency', 'DZ-Agency')
                print(f"  Site: {old_site} → {row['site']}")

            # Replace EG with DZ in description
            if 'description' in row and 'EG-Agency' in row['description']:
                row['description'] = row['description'].replace('EG-Agency', 'DZ-Agency')

            circuits.append(row)

    # Write updated circuits
    with open(circuit_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(circuits)

    if replaced_count > 0:
        print(f"  ✅ Replaced {replaced_count} Egypt references with Algeria")
    else:
        print(f"  ℹ️  No Egypt references found")

print("\n✅ All circuit files processed - Egypt (EG) replaced with Algeria (DZ)")
