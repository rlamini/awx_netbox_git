#!/usr/bin/env python3
"""
Find devices that exceed rack height (42U standard)
"""
import csv

# Load device types to get u_height
device_types = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        device_types[row['model']] = int(row['u_height'])

print("Finding devices that exceed rack height...\n")

RACK_HEIGHT = 42  # Standard rack height

problems = []
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader, start=1):
        device_type = row['device_type']
        position = int(row['position'])
        u_height = device_types.get(device_type, 1)

        # Top position the device reaches
        top_position = position + u_height - 1

        if top_position > RACK_HEIGHT:
            problems.append({
                'record': idx,
                'name': row['name'],
                'rack': row['rack'],
                'device_type': device_type,
                'u_height': u_height,
                'position': position,
                'top_position': top_position,
                'overflow': top_position - RACK_HEIGHT
            })

if problems:
    print(f"❌ Found {len(problems)} devices exceeding rack height:\n")
    for p in problems:
        print(f"Record {p['record']}: {p['name']}")
        print(f"  Rack: {p['rack']}")
        print(f"  Device: {p['device_type']} ({p['u_height']}U)")
        print(f"  Position: U{p['position']} (reaches U{p['top_position']}, exceeds by {p['overflow']}U)")
        print(f"  → Should be at U{RACK_HEIGHT - p['u_height'] + 1} or lower")
        print()
else:
    print("✅ All devices fit within rack height!")
