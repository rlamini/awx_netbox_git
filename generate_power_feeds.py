#!/usr/bin/env python3
"""
Generate power feed cables from power panels to PDUs.
Maps PDUs to their location's panels and creates feed cables.
"""

import csv
from collections import defaultdict

# Read PDUs
pdus = []
with open('lab/power/netbox_dc_pdus.csv', 'r') as f:
    reader = csv.DictReader(f)
    pdus = [row for row in reader]

# Track circuit usage per panel
panel_circuit_usage = defaultdict(int)

power_feeds = []
cable_id = 1

print(f"Generating power feed cables for {len(pdus)} PDUs...")

# Group PDUs by location
pdus_by_location = defaultdict(list)
for pdu in pdus:
    location = pdu['location']
    pdus_by_location[location].append(pdu)

print(f"Distributing {len(pdus)} PDUs across {len(pdus_by_location)} locations")

for location, location_pdus in pdus_by_location.items():
    site = location_pdus[0]['site']
    location_name = location.replace(f'{site}-', '')
    location_slug = location_name.replace(' ', '-')

    panel_a = f'{site}-{location_slug}-PANEL-A'
    panel_b = f'{site}-{location_slug}-PANEL-B'

    print(f"\n{location}: {len(location_pdus)} PDUs")

    for pdu in location_pdus:
        pdu_name = pdu['name']
        rack = pdu['rack']

        # Determine which panel this PDU connects to
        if pdu_name.endswith('-PDU-A'):
            panel = panel_a
            panel_type = 'A'
        else:  # PDU-B
            panel = panel_b
            panel_type = 'B'

        # Get next available circuit
        circuit_num = panel_circuit_usage[panel] + 1

        if circuit_num > 42:
            print(f"WARNING: {panel} has more than 42 PDUs! Circuit exhausted.")
            continue

        # Create power feed cable
        power_feeds.append({
            'label': f'{rack}-PF-{cable_id:04d}',
            'type': 'power',
            'status': 'connected',
            'side_a_device': panel,
            'side_a_type': 'dcim.poweroutlet',
            'side_a_name': f'Circuit-{circuit_num:02d}',
            'side_b_device': pdu_name,
            'side_b_type': 'dcim.powerport',
            'side_b_name': 'Power-In',
            'length': '',
            'length_unit': '',
            'description': f'Power feed: {panel} to {pdu_name}'
        })

        cable_id += 1
        panel_circuit_usage[panel] += 1

print(f"\n✅ Generated {len(power_feeds)} power feed cables")
print(f"   - Connects electrical panels to PDUs")

# Check circuit utilization
max_circuits = max(panel_circuit_usage.values()) if panel_circuit_usage else 0
print(f"   - Maximum circuits used per panel: {max_circuits}/42")

# Write power feeds CSV
feeds_file = 'lab/power/netbox_dc_power_feeds.csv'
with open(feeds_file, 'w', newline='') as f:
    fieldnames = ['label', 'type', 'status', 'side_a_device', 'side_a_type', 'side_a_name',
                  'side_b_device', 'side_b_type', 'side_b_name', 'length', 'length_unit', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_feeds)

print(f"✅ Power feeds written to {feeds_file}")
