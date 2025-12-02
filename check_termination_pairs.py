#!/usr/bin/env python3
"""
Check if circuit terminations have proper A/Z side pairing
"""
import csv
from pathlib import Path
from collections import defaultdict

term_files = [
    'lab/netbox_dc_circuits_terminations.csv',
    'lab/netbox_circuits_terminations_emea.csv',
    'lab/netbox_circuits_terminations_amer.csv',
    'lab/netbox_circuits_terminations_apac.csv'
]

circuit_terms = defaultdict(lambda: {'A': [], 'Z': []})

print("Analyzing circuit terminations...\n")

for term_file in term_files:
    if not Path(term_file).exists():
        continue

    with open(term_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            circuit = row['circuit']
            term_side = row['term_side']
            site = row['site']
            circuit_terms[circuit][term_side].append(site)

# Report findings
print(f"Total circuits: {len(circuit_terms)}\n")

a_only = []
z_only = []
both = []
multiple_a = []
multiple_z = []

for circuit, sides in circuit_terms.items():
    has_a = len(sides['A']) > 0
    has_z = len(sides['Z']) > 0

    if sides['A'] and len(sides['A']) > 1:
        multiple_a.append(circuit)
    if sides['Z'] and len(sides['Z']) > 1:
        multiple_z.append(circuit)

    if has_a and has_z:
        both.append(circuit)
    elif has_a:
        a_only.append(circuit)
    elif has_z:
        z_only.append(circuit)

print(f"✅ Circuits with both A and Z terminations: {len(both)}")
print(f"⚠️  Circuits with only A-side termination: {len(a_only)}")
print(f"⚠️  Circuits with only Z-side termination: {len(z_only)}")

if multiple_a:
    print(f"⚠️  Circuits with multiple A-side terminations: {len(multiple_a)}")
    for cid in multiple_a[:5]:
        print(f"     - {cid}: {circuit_terms[cid]['A']}")

if multiple_z:
    print(f"⚠️  Circuits with multiple Z-side terminations: {len(multiple_z)}")
    for cid in multiple_z[:5]:
        print(f"     - {cid}: {circuit_terms[cid]['Z']}")

if a_only:
    print(f"\nFirst 10 circuits with only A-side:")
    for cid in a_only[:10]:
        print(f"  - {cid} at {circuit_terms[cid]['A'][0]}")
