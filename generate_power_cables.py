#!/usr/bin/env python3
"""
Generate power cables connecting devices to PDU outlets.
PSU1 → PDU-A, PSU2 → PDU-B for redundancy.
"""

import csv
from collections import defaultdict

# Read devices list
devices = []
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    devices = [row for row in reader if row['role'] != 'Patch Panel']  # Skip patch panels

# Track outlet usage per PDU
pdu_outlet_usage = defaultdict(int)

power_cables = []
cable_id = 1

print(f"Generating power cables for {len(devices)} devices...")

for device in devices:
    device_name = device['name']
    rack = device['rack']

    # Determine PDU names for this rack
    pdu_a = f"{rack}-PDU-A"
    pdu_b = f"{rack}-PDU-B"

    # Get next available outlet on each PDU
    pdu_a_outlet = pdu_outlet_usage[pdu_a] + 1
    pdu_b_outlet = pdu_outlet_usage[pdu_b] + 1

    # Check if we have enough outlets (24 per PDU)
    if pdu_a_outlet > 24 or pdu_b_outlet > 24:
        print(f"WARNING: {rack} has more than 24 devices! Outlets exhausted.")
        continue

    # PSU1 to PDU-A
    power_cables.append({
        'label': f'{rack}-PC-{cable_id:04d}',
        'type': 'power',
        'status': 'connected',
        'side_a_device': device_name,
        'side_a_type': 'dcim.powerport',
        'side_a_name': 'PSU1',
        'side_b_device': pdu_a,
        'side_b_type': 'dcim.poweroutlet',
        'side_b_name': f'Outlet-{pdu_a_outlet:02d}',
        'length': '',
        'length_unit': '',
        'description': f'Power cable: {device_name} PSU1 to {pdu_a}'
    })
    cable_id += 1
    pdu_outlet_usage[pdu_a] += 1

    # PSU2 to PDU-B
    power_cables.append({
        'label': f'{rack}-PC-{cable_id:04d}',
        'type': 'power',
        'status': 'connected',
        'side_a_device': device_name,
        'side_a_type': 'dcim.powerport',
        'side_a_name': 'PSU2',
        'side_b_device': pdu_b,
        'side_b_type': 'dcim.poweroutlet',
        'side_b_name': f'Outlet-{pdu_b_outlet:02d}',
        'length': '',
        'length_unit': '',
        'description': f'Power cable: {device_name} PSU2 to {pdu_b}'
    })
    cable_id += 1
    pdu_outlet_usage[pdu_b] += 1

print(f"\n✅ Generated {len(power_cables)} power cables")
print(f"   - {len(devices)} devices × 2 power supplies each")

# Check outlet utilization
max_outlets_used = max(pdu_outlet_usage.values()) if pdu_outlet_usage else 0
print(f"   - Maximum outlets used per PDU: {max_outlets_used}/24")

# Write power cables CSV
cables_file = 'lab/netbox_dc_power_cables.csv'
with open(cables_file, 'w', newline='') as f:
    fieldnames = ['label', 'type', 'status', 'side_a_device', 'side_a_type', 'side_a_name',
                  'side_b_device', 'side_b_type', 'side_b_name', 'length', 'length_unit', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_cables)

print(f"✅ Power cables written to {cables_file}")
