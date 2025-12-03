#!/usr/bin/env python3
"""
Replace all Egypt (EG) references with Algeria (DZ) references
in circuit termination files
"""
import csv
from pathlib import Path

# Algeria site IDs from the export
algeria_sites = {
    'DZ-Agency1': '189',
    'DZ-Agency2': '190'
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
    replaced_count = 0

    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Replace EG with DZ in circuit name
            circuit = row['circuit']
            if 'EG-Agency' in circuit:
                old_circuit = circuit
                circuit = circuit.replace('EG-Agency', 'DZ-Agency')
                replaced_count += 1
                print(f"  Circuit: {old_circuit} → {circuit}")

            # Replace EG with DZ in description
            description = row['description']
            if 'EG-Agency' in description:
                description = description.replace('EG-Agency', 'DZ-Agency')

            # Update termination_id if it was empty and now we have DZ site
            termination_id = row.get('termination_id', '')
            if not termination_id:
                # Extract site name from description
                if 'at DZ-Agency1' in description:
                    termination_id = algeria_sites['DZ-Agency1']
                    print(f"  Added site ID {termination_id} for DZ-Agency1")
                elif 'at DZ-Agency2' in description:
                    termination_id = algeria_sites['DZ-Agency2']
                    print(f"  Added site ID {termination_id} for DZ-Agency2")

            new_row = {
                'circuit': circuit,
                'term_side': row['term_side'],
                'termination_type': row['termination_type'],
                'termination_id': termination_id,
                'port_speed': row['port_speed'],
                'upstream_speed': row['upstream_speed'],
                'description': description
            }
            terminations.append(new_row)

    # Write updated terminations
    fieldnames = ['circuit', 'term_side', 'termination_type', 'termination_id',
                  'port_speed', 'upstream_speed', 'description']
    with open(term_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(terminations)

    if replaced_count > 0:
        print(f"  ✅ Replaced {replaced_count} Egypt references with Algeria")
    else:
        print(f"  ℹ️  No Egypt references found")

print("\n✅ All files processed - Egypt (EG) replaced with Algeria (DZ)")
