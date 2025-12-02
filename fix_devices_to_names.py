#!/usr/bin/env python3
"""
Fix netbox_dc_devices.csv to use display names instead of slugs
for device_type, site, and location fields (NetBox CSV import expects names)
"""
import csv

# Build mapping of slug -> model (display name) from device_types.csv
device_type_map = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        device_type_map[row['slug']] = row['model']

# Build mapping of slug -> name (display name) from dc_sites.csv
site_map = {}
with open('lab/netbox_dc_sites.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        site_map[row['slug']] = row['name']

# Build mapping of slug -> name (display name) from dc_locations.csv
location_map = {}
with open('lab/netbox_dc_locations.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        location_map[row['slug']] = row['name']

print(f"Loaded {len(device_type_map)} device type mappings")
print(f"Loaded {len(site_map)} site mappings")
print(f"Loaded {len(location_map)} location mappings")
print()

# Read and fix devices.csv
devices = []
fixed_count = 0
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames

    for row in reader:
        changes = []

        # Convert device_type from slug to model (display name)
        if row['device_type'] in device_type_map:
            old_type = row['device_type']
            row['device_type'] = device_type_map[old_type]
            changes.append(f"device_type: '{old_type}' -> '{row['device_type']}'")

        # Convert site from slug to name (display name)
        if row['site'] in site_map:
            old_site = row['site']
            row['site'] = site_map[old_site]
            changes.append(f"site: '{old_site}' -> '{row['site']}'")

        # Convert location from slug to name (display name)
        if row['location'] in location_map:
            old_location = row['location']
            row['location'] = location_map[old_location]
            changes.append(f"location: '{old_location}' -> '{row['location']}'")

        if changes:
            fixed_count += 1
            print(f"Device {row['name']}: {', '.join(changes)}")

        devices.append(row)

# Write corrected file
with open('lab/netbox_dc_devices.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"\n✅ Fixed {fixed_count} device records")
print(f"✅ Updated: lab/netbox_dc_devices.csv")
print(f"\nConverted slugs to display names for NetBox CSV import")
