#!/usr/bin/env python3
"""
Generate power ports on PDUs (input power).
Each PDU needs 1 power port to receive power from the panel.
"""

import csv

# Read PDUs
pdus = []
with open('lab/netbox_dc_pdus.csv', 'r') as f:
    reader = csv.DictReader(f)
    pdus = [row for row in reader]

pdu_power_ports = []

print(f"Generating power ports for {len(pdus)} PDUs...")

for pdu in pdus:
    pdu_name = pdu['name']

    # Each PDU has 1 input power port
    pdu_power_ports.append({
        'device': pdu_name,
        'name': 'Power-In',
        'type': 'nema-l6-30p',  # 30A 250V twist-lock plug (matches panel outlet)
        'maximum_draw': 7200,  # 30A × 240V = 7200W (7.2kW)
        'allocated_draw': '',
        'description': 'Input power from electrical panel'
    })

print(f"✅ Generated {len(pdu_power_ports)} PDU power ports")

# Write PDU power ports CSV
ports_file = 'lab/netbox_dc_pdu_power_ports.csv'
with open(ports_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'maximum_draw', 'allocated_draw', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(pdu_power_ports)

print(f"✅ PDU power ports written to {ports_file}")
