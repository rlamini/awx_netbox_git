#!/usr/bin/env python3
"""
Add Z-side terminations for all circuits
Z-side represents the provider/remote endpoint of the circuit
"""
import csv
from pathlib import Path

term_files = [
    'lab/netbox_dc_circuits_terminations.csv',
    'lab/netbox_circuits_terminations_emea.csv',
    'lab/netbox_circuits_terminations_amer.csv',
    'lab/netbox_circuits_terminations_apac.csv'
]

# Load circuit information to get provider details
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

    # Load circuit details (to get provider info)
    circuits = {}
    with open(circuit_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            circuits[row['cid']] = {
                'provider': row.get('provider', ''),
                'type': row.get('type', ''),
                'description': row.get('description', '')
            }

    # Read existing terminations
    terminations = []
    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            terminations.append(row)

    # Count A-side only
    a_side_count = len([t for t in terminations if t['term_side'] == 'A'])
    z_side_count = len([t for t in terminations if t['term_side'] == 'Z'])

    print(f"  Current: {a_side_count} A-side, {z_side_count} Z-side terminations")

    # Add Z-side terminations for circuits that only have A-side
    circuits_with_a = {}
    circuits_with_z = set()

    for term in terminations:
        if term['term_side'] == 'A':
            circuits_with_a[term['circuit']] = term
        elif term['term_side'] == 'Z':
            circuits_with_z.add(term['circuit'])

    added = 0
    for circuit_id, a_term in circuits_with_a.items():
        if circuit_id not in circuits_with_z:
            # Add Z-side termination (provider endpoint)
            circuit_info = circuits.get(circuit_id, {})
            provider = circuit_info.get('provider', 'Provider')

            z_term = {
                'circuit': circuit_id,
                'term_side': 'Z',
                'site': '',  # Z-side doesn't need a site (provider endpoint)
                'port_speed': a_term['port_speed'],
                'upstream_speed': a_term['upstream_speed'],
                'description': f"Z-side termination at {provider}"
            }
            terminations.append(z_term)
            added += 1

    # Write updated terminations
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    print(f"  ✅ Added {added} Z-side terminations")
    print(f"  New total: {len(terminations)} terminations")

print("\n✅ All circuit termination files updated with Z-side terminations")
