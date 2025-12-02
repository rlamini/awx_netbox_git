#!/usr/bin/env python3
"""
Comprehensive fix for all NetBox CSV files to use slugs instead of display names
for all foreign key references (site, location, device_type)
"""
import csv

# Build mappings
device_type_map = {}
with open('lab/netbox_device_types.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        device_type_map[row['model']] = row['slug']

site_map = {}
with open('lab/netbox_dc_sites.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        site_map[row['name']] = row['slug']

location_map = {}
with open('lab/netbox_dc_locations.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        location_map[row['name']] = row['slug']

print(f"Loaded mappings:")
print(f"  - {len(device_type_map)} device types")
print(f"  - {len(site_map)} sites")
print(f"  - {len(location_map)} locations")
print()

# Fix 1: netbox_dc_locations.csv - Convert site names to slugs
print("=" * 60)
print("Fixing netbox_dc_locations.csv")
print("=" * 60)
locations = []
with open('lab/netbox_dc_locations.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        if row['site'] in site_map:
            old_site = row['site']
            row['site'] = site_map[old_site]
            print(f"  Location '{row['name']}': site '{old_site}' -> '{row['site']}'")
        locations.append(row)

with open('lab/netbox_dc_locations.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(locations)
print(f"✅ Fixed {len(locations)} location records\n")

# Fix 2: netbox_dc_racks.csv - Convert site and location names to slugs
print("=" * 60)
print("Fixing netbox_dc_racks.csv")
print("=" * 60)
racks = []
with open('lab/netbox_dc_racks.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        # Fix site field
        if row['site'] in site_map:
            old_site = row['site']
            row['site'] = site_map[old_site]

        # Fix location field
        if row['location'] in location_map:
            old_location = row['location']
            row['location'] = location_map[old_location]
            print(f"  Rack '{row['name']}': location '{old_location}' -> '{row['location']}'")

        racks.append(row)

with open('lab/netbox_dc_racks.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(racks)
print(f"✅ Fixed {len(racks)} rack records\n")

# Fix 3: netbox_dc_devices.csv - Convert location names to slugs
# (site and device_type already fixed in previous script)
print("=" * 60)
print("Fixing netbox_dc_devices.csv")
print("=" * 60)
devices = []
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        # Fix location field
        if row['location'] in location_map:
            old_location = row['location']
            row['location'] = location_map[old_location]
            print(f"  Device '{row['name']}': location '{old_location}' -> '{row['location']}'")

        devices.append(row)

with open('lab/netbox_dc_devices.csv', 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)
print(f"✅ Fixed {len(devices)} device records\n")

print("=" * 60)
print("✅ ALL FIXES COMPLETED!")
print("=" * 60)
print("\nImport order for NetBox:")
print("  1. Tags (netbox_dc_tags.csv)")
print("  2. Manufacturers (netbox_manufacturers.csv)")
print("  3. Device Types (netbox_device_types.csv)")
print("  4. Device Roles (netbox_device_roles.csv)")
print("  5. Sites (netbox_dc_sites.csv)")
print("  6. Locations (netbox_dc_locations.csv)")
print("  7. Racks (netbox_dc_racks.csv)")
print("  8. Devices (netbox_dc_devices.csv)")
print("  9. Interfaces (netbox_dc_interfaces.csv)")
