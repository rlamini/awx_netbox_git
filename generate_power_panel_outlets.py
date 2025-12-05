#!/usr/bin/env python3
"""
Generate power outlets on power panels.
Each panel has 42 circuits (3-phase distribution panel).
"""

import csv

# Read power panels
power_panels = []
with open('lab/power/netbox_dc_power_panels.csv', 'r') as f:
    reader = csv.DictReader(f)
    power_panels = [row for row in reader]

power_panel_outlets = []

print(f"Generating power outlets for {len(power_panels)} power panels...")

for panel in power_panels:
    panel_name = panel['name']

    # Each panel has 42 circuits (standard 3-phase panel)
    for circuit_num in range(1, 43):
        power_panel_outlets.append({
            'power_panel': panel_name,
            'name': f'Circuit-{circuit_num:02d}',
            'type': 'nema-l6-30r',  # 30A 250V twist-lock (common for PDU feeds)
            'feed_leg': 'A' if circuit_num % 3 == 1 else ('B' if circuit_num % 3 == 2 else 'C'),  # 3-phase distribution
            'description': f'Circuit {circuit_num}'
        })

print(f"✅ Generated {len(power_panel_outlets)} power panel outlets")
print(f"   - {len(power_panels)} panels × 42 circuits each")

# Write power panel outlets CSV
outlets_file = 'lab/power/netbox_dc_power_panel_outlets.csv'
with open(outlets_file, 'w', newline='') as f:
    fieldnames = ['power_panel', 'name', 'type', 'feed_leg', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_panel_outlets)

print(f"✅ Power panel outlets written to {outlets_file}")
