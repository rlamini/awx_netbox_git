#!/usr/bin/env python3
"""
Generate Meraki Hub MX appliances in ONPREM datacenters.
Each ONPREM DC gets 2× Meraki MX250 in HA configuration to terminate
agency VPN tunnels.
"""

import csv

device_types = []
devices = []

print("Generating Meraki Hub devices for ONPREM datacenters...")

# Device Type - Meraki MX250 (larger appliance for hub)
device_types.append({
    'manufacturer': 'Cisco Meraki',
    'model': 'MX250',
    'slug': 'meraki-mx250',
    'u_height': 1,
    'is_full_depth': True,
    'description': 'Meraki MX250 SD-WAN Concentrator (2 Gbps)'
})

print("  - Created Meraki MX250 device type (hub concentrator)")

# ONPREM Sites
onprem_sites = ['EMEA-DC-ONPREM', 'APAC-DC-ONPREM', 'AMER-DC-ONPREM']

# Generate 2× MX250 per ONPREM site (HA pair)
for site in onprem_sites:
    # Primary MX250
    devices.append({
        'name': f'{site}-MERAKI-HUB-MX-01',
        'manufacturer': 'Cisco Meraki',
        'device_type': 'MX250',
        'role': 'Firewall',
        'site': site,
        'location': f'{site}-Network Core',
        'rack': f'{site}-NET-R04',
        'position': '10',
        'face': 'front',
        'status': 'active',
        'description': f'Meraki MX250 SD-WAN Hub - Primary',
        'comments': f'VPN hub for all {site.split("-")[0]} agencies. Primary in HA pair.'
    })

    # Secondary MX250
    devices.append({
        'name': f'{site}-MERAKI-HUB-MX-02',
        'manufacturer': 'Cisco Meraki',
        'device_type': 'MX250',
        'role': 'Firewall',
        'site': site,
        'location': f'{site}-Network Core',
        'rack': f'{site}-NET-R04',
        'position': '9',
        'face': 'front',
        'status': 'active',
        'description': f'Meraki MX250 SD-WAN Hub - Secondary',
        'comments': f'VPN hub failover for {site.split("-")[0]} agencies. Secondary in HA pair.'
    })

print(f"\n✅ Generated {len(device_types)} device type")
print(f"✅ Generated {len(devices)} Meraki Hub devices")
print(f"   - {len(onprem_sites)} sites × 2 MX250 = 6 hub devices")
print(f"   - EMEA-DC-ONPREM: 2× MX250 (hub for EMEA agencies)")
print(f"   - APAC-DC-ONPREM: 2× MX250 (hub for APAC agencies)")
print(f"   - AMER-DC-ONPREM: 2× MX250 (hub for AMER agencies)")

# Write device type CSV
device_types_file = 'lab/agencies/netbox_meraki_hub_device_types.csv'
with open(device_types_file, 'w', newline='') as f:
    fieldnames = ['manufacturer', 'model', 'slug', 'u_height', 'is_full_depth', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(device_types)

print(f"✅ Hub device types written to {device_types_file}")

# Write devices CSV
devices_file = 'lab/agencies/netbox_dc_meraki_hubs.csv'
with open(devices_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"✅ Hub devices written to {devices_file}")
