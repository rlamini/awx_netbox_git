#!/usr/bin/env python3
"""
Fix netbox_dc_devices.csv to use slugs instead of display names
for device_type and site fields
"""
import csv

# Build mapping of model -> slug from device_types.csv
device_type_map = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        device_type_map[row['model']] = row['slug']

# Build mapping of site name -> slug from dc_sites.csv
site_map = {}
with open('lab/netbox_dc_sites.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        site_map[row['name']] = row['slug']

print(f"Loaded {len(device_type_map)} device type mappings")
print(f"Loaded {len(site_map)} site mappings")

# Read and fix devices.csv
devices = []
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        # Convert device_type from model to slug
        if row['device_type'] in device_type_map:
            old_type = row['device_type']
            row['device_type'] = device_type_map[old_type]
            print(f"  Device: {row['name']}: '{old_type}' -> '{row['device_type']}'")
        else:
            print(f"  WARNING: Device {row['name']}: device_type '{row['device_type']}' not found in mapping")

        # Convert site from name to slug
        if row['site'] in site_map:
            old_site = row['site']
            row['site'] = site_map[old_site]
        else:
            print(f"  WARNING: Device {row['name']}: site '{row['site']}' not found in mapping")

        devices.append(row)

# Write corrected file
with open('lab/netbox_dc_devices.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"\n✅ Fixed {len(devices)} device records")
print(f"✅ Updated: lab/netbox_dc_devices.csv")
