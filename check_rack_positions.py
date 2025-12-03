#!/usr/bin/env python3
"""
Find overlapping rack positions in devices CSV
"""
import csv
from collections import defaultdict

# Load device types to get u_height
device_types = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        device_types[row['model']] = int(row['u_height'])

print("Loading devices and checking for overlaps...\n")

# Load devices and track positions by rack
devices = []
rack_positions = defaultdict(list)  # rack_name -> [(device, start_pos, end_pos), ...]

with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        devices.append(row)

        rack = row['rack']
        position = int(row['position'])
        device_type = row['device_type']
        u_height = device_types.get(device_type, 1)

        # Calculate the range of positions this device occupies
        # Position is the bottom U, so a 2U device at position 42 occupies U42 and U43
        start_pos = position
        end_pos = position + u_height - 1

        rack_positions[rack].append({
            'record': idx,
            'name': row['name'],
            'device_type': device_type,
            'u_height': u_height,
            'start': start_pos,
            'end': end_pos,
            'site': row['site']
        })

# Check for overlaps
print("Checking for position conflicts...\n")
conflicts = []

for rack, devices_in_rack in rack_positions.items():
    # Sort by start position
    devices_in_rack.sort(key=lambda x: x['start'])

    for i in range(len(devices_in_rack)):
        for j in range(i + 1, len(devices_in_rack)):
            dev1 = devices_in_rack[i]
            dev2 = devices_in_rack[j]

            # Check if ranges overlap
            if not (dev1['end'] < dev2['start'] or dev2['end'] < dev1['start']):
                conflicts.append({
                    'rack': rack,
                    'site': dev1['site'],
                    'device1': dev1,
                    'device2': dev2
                })

if conflicts:
    print(f"❌ Found {len(conflicts)} position conflicts:\n")
    for conflict in conflicts:
        dev1 = conflict['device1']
        dev2 = conflict['device2']
        print(f"Rack: {conflict['rack']} at {conflict['site']}")
        print(f"  Conflict between:")
        print(f"    Record {dev1['record']}: {dev1['name']} ({dev1['device_type']}, {dev1['u_height']}U) at U{dev1['start']}-U{dev1['end']}")
        print(f"    Record {dev2['record']}: {dev2['name']} ({dev2['device_type']}, {dev2['u_height']}U) at U{dev2['start']}-U{dev2['end']}")
        print()
else:
    print("✅ No position conflicts found!")

# Show rack utilization
print("\nRack utilization summary:")
for rack in sorted(rack_positions.keys())[:10]:
    devices_in_rack = rack_positions[rack]
    site = devices_in_rack[0]['site'] if devices_in_rack else ''
    total_u = sum(d['u_height'] for d in devices_in_rack)
    print(f"  {rack} ({site}): {len(devices_in_rack)} devices, {total_u}U used")
