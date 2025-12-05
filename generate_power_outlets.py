#!/usr/bin/env python3
"""
Generate power outlets for all PDUs.
Each PDU has 24 outlets (C13 type).
"""

import csv

# Read PDU list
pdus = []
with open('lab/power/netbox_dc_pdus.csv', 'r') as f:
    reader = csv.DictReader(f)
    pdus = [row for row in reader]

power_outlets = []

print(f"Generating power outlets for {len(pdus)} PDUs...")

for pdu in pdus:
    pdu_name = pdu['name']

    # Each PDU has 24 outlets (C13 type)
    for outlet_num in range(1, 25):
        power_outlets.append({
            'device': pdu_name,
            'name': f'Outlet-{outlet_num:02d}',
            'type': 'iec-60320-c13',  # Standard C13 outlet
            'power_port': '',  # Empty for now
            'feed_leg': 'A' if outlet_num <= 12 else 'B',  # Split across two legs
            'description': f'Power outlet {outlet_num}'
        })

print(f"✅ Generated {len(power_outlets)} power outlets")
print(f"   - {len(pdus)} PDUs × 24 outlets each")

# Write power outlets CSV
outlets_file = 'lab/power/netbox_dc_power_outlets.csv'
with open(outlets_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'power_port', 'feed_leg', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_outlets)

print(f"✅ Power outlets written to {outlets_file}")
