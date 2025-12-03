#!/usr/bin/env python3
"""
Fix devices that exceed rack height by adjusting positions
"""
import csv

# Load device types to get u_height
device_types = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        device_types[row['model']] = int(row['u_height'])

RACK_HEIGHT = 42  # Standard rack height

print("Fixing device positions that exceed rack height...\n")

devices = []
fixed_count = 0

with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for idx, row in enumerate(reader, start=1):
        device_type = row['device_type']
        position = int(row['position'])
        u_height = device_types.get(device_type, 1)

        # Calculate max allowed position for this device
        max_position = RACK_HEIGHT - u_height + 1

        # Check if position exceeds rack height
        top_position = position + u_height - 1

        if top_position > RACK_HEIGHT:
            old_position = position
            # Adjust to maximum allowed position
            row['position'] = str(max_position)
            print(f"Record {idx}: {row['name']}")
            print(f"  Rack: {row['rack']}")
            print(f"  Device: {device_type} ({u_height}U)")
            print(f"  Fixed: U{old_position} → U{max_position}")
            fixed_count += 1

        devices.append(row)

# Write corrected file
with open('lab/netbox_dc_devices.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"\n✅ Fixed {fixed_count} device positions")
print(f"✅ Updated: lab/netbox_dc_devices.csv")
print(f"\nAll devices now fit within 42U rack height")
