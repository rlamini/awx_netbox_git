#!/usr/bin/env python3
"""
Add manufacturer column to netbox_dc_devices.csv
NetBox requires both manufacturer and device_type (model) for device import
"""
import csv

# Build mapping of model -> manufacturer from device_types.csv
model_to_manufacturer = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        model_to_manufacturer[row['model']] = row['manufacturer']

print(f"Loaded {len(model_to_manufacturer)} device type mappings")
print()

# Read devices CSV and add manufacturer column
devices = []
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        device_type_model = row['device_type']

        # Look up manufacturer for this device type
        if device_type_model in model_to_manufacturer:
            manufacturer = model_to_manufacturer[device_type_model]
            print(f"Device {row['name']}: adding manufacturer '{manufacturer}' for device_type '{device_type_model}'")
        else:
            manufacturer = "UNKNOWN"
            print(f"WARNING: Device {row['name']}: could not find manufacturer for device_type '{device_type_model}'")

        # Create new row with manufacturer field added after device_type
        new_row = {
            'name': row['name'],
            'manufacturer': manufacturer,
            'device_type': row['device_type'],
            'role': row['role'],
            'site': row['site'],
            'location': row['location'],
            'rack': row['rack'],
            'position': row['position'],
            'face': row['face'],
            'status': row['status'],
            'description': row['description']
        }
        devices.append(new_row)

# Write updated file with new field order
fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location', 'rack', 'position', 'face', 'status', 'description']
with open('lab/netbox_dc_devices.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"\n✅ Added manufacturer field to {len(devices)} device records")
print(f"✅ Updated: lab/netbox_dc_devices.csv")
