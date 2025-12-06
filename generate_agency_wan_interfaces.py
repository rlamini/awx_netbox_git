#!/usr/bin/env python3
"""
Generate WAN interfaces for all agency Meraki MX devices.
Each MX has:
- WAN1 (Internet 1) - for ADSL circuit
- WAN2 (Internet 2) - for 5G circuit
"""

import csv

interfaces = []

print("Generating WAN interfaces for agency Meraki MX devices...")

# Read agencies from site files
agencies = []

# EMEA agencies
with open('lab/sites/netbox_sites_emea.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'region': 'EMEA'
            })

# APAC agencies
with open('lab/sites/netbox_sites_apac.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'region': 'APAC'
            })

# AMER agencies
with open('lab/sites/netbox_sites_amer.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'region': 'AMER'
            })

print(f"Found {len(agencies)} agencies")

# Generate WAN interfaces for each MX
print("\nGenerating WAN interfaces...")

for agency in agencies:
    site_name = agency['name']

    # MX-01 WAN interfaces
    # WAN1 (Internet 1) - ADSL
    interfaces.append({
        'device': f'{site_name}-MX-01',
        'name': 'WAN1',
        'type': '1000base-t',
        'enabled': True,
        'description': 'WAN1 (Internet 1) - ADSL circuit',
        'mode': '',
        'mtu': '1500'
    })

    # WAN2 (Internet 2) - 5G
    interfaces.append({
        'device': f'{site_name}-MX-01',
        'name': 'WAN2',
        'type': '1000base-t',
        'enabled': True,
        'description': 'WAN2 (Internet 2) - 5G backup circuit',
        'mode': '',
        'mtu': '1500'
    })

    # MX-02 WAN interfaces (secondary MX in HA pair)
    # WAN1 (Internet 1) - ADSL
    interfaces.append({
        'device': f'{site_name}-MX-02',
        'name': 'WAN1',
        'type': '1000base-t',
        'enabled': True,
        'description': 'WAN1 (Internet 1) - ADSL circuit',
        'mode': '',
        'mtu': '1500'
    })

    # WAN2 (Internet 2) - 5G
    interfaces.append({
        'device': f'{site_name}-MX-02',
        'name': 'WAN2',
        'type': '1000base-t',
        'enabled': True,
        'description': 'WAN2 (Internet 2) - 5G backup circuit',
        'mode': '',
        'mtu': '1500'
    })

print(f"\n✅ Generated {len(interfaces)} WAN interfaces")
print(f"   - {len(agencies)} agencies × 2 MX × 2 WAN = {len(interfaces)} interfaces")
print(f"   - Per MX: WAN1 (ADSL), WAN2 (5G)")

# Write interfaces CSV
interfaces_file = 'lab/agencies/netbox_agency_wan_interfaces.csv'
with open(interfaces_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'enabled', 'description', 'mode', 'mtu']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(interfaces)

print(f"✅ WAN interfaces written to {interfaces_file}")
