#!/usr/bin/env python3
"""
Remove 'site' column from circuit CSV files
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
    with open(circuit_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        # Check if 'site' column exists
        if 'site' not in fieldnames:
            print(f"  ℹ️  No 'site' column found")
            continue

        # Create new fieldnames without 'site'
        new_fieldnames = [f for f in fieldnames if f != 'site']

        for row in reader:
            # Remove site field
            if 'site' in row:
                del row['site']
            circuits.append(row)

    # Write without site column
    with open(circuit_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(circuits)

    print(f"  ✅ Removed 'site' column from {len(circuits)} circuits")
    print(f"  New columns: {', '.join(new_fieldnames)}")

print("\n✅ All circuit files updated - 'site' column removed")
