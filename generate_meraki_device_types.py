#!/usr/bin/env python3
"""
Generate Meraki device types for agency branches.
Each agency has:
- 2× Meraki MX68 (SD-WAN appliance, HA pair)
- 2× Meraki MS120-8 (8-port switch)
- 4× Meraki MR36 (WiFi 6 access point)
"""

import csv

device_types = []

print("Generating Meraki device types for agencies...")

# Meraki MX68 - SD-WAN Security Appliance
device_types.append({
    'manufacturer': 'Cisco Meraki',
    'model': 'MX68',
    'slug': 'meraki-mx68',
    'u_height': 1,
    'is_full_depth': False,
    'description': 'Meraki MX68 SD-WAN Security Appliance (450 Mbps)'
})

# Meraki MS120-8 - Access Switch
device_types.append({
    'manufacturer': 'Cisco Meraki',
    'model': 'MS120-8',
    'slug': 'meraki-ms120-8',
    'u_height': 1,
    'is_full_depth': False,
    'description': 'Meraki MS120-8 Cloud Managed Switch (8× 1GbE ports)'
})

# Meraki MR36 - WiFi 6 Access Point
device_types.append({
    'manufacturer': 'Cisco Meraki',
    'model': 'MR36',
    'slug': 'meraki-mr36',
    'u_height': 0,
    'is_full_depth': False,
    'description': 'Meraki MR36 WiFi 6 Access Point (2×2:2 MU-MIMO)'
})

print(f"✅ Generated {len(device_types)} Meraki device types")
print(f"   - Meraki MX68 (SD-WAN appliance)")
print(f"   - Meraki MS120-8 (8-port switch)")
print(f"   - Meraki MR36 (WiFi 6 AP)")

# Write device types CSV
device_types_file = 'lab/agencies/netbox_meraki_device_types.csv'
with open(device_types_file, 'w', newline='') as f:
    fieldnames = ['manufacturer', 'model', 'slug', 'u_height', 'is_full_depth', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(device_types)

print(f"✅ Meraki device types written to {device_types_file}")
