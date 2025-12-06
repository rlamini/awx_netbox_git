#!/usr/bin/env python3
"""
Generate Meraki devices for all agency branches.
Reads agency sites from existing site files and creates:
- 2× Meraki MX68 (HA pair: MX-01 primary, MX-02 secondary)
- 2× Meraki MS120-8 switches
- 4× Meraki MR36 access points
"""

import csv

devices = []

print("Generating Meraki devices for all agency branches...")

# Read agencies from site files
agencies = []

# EMEA agencies
print("\nReading EMEA agencies...")
with open('lab/sites/netbox_sites_emea.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'slug': row['slug'],
                'region': 'EMEA'
            })

# APAC agencies
print("Reading APAC agencies...")
with open('lab/sites/netbox_sites_apac.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'slug': row['slug'],
                'region': 'APAC'
            })

# AMER agencies
print("Reading AMER agencies...")
with open('lab/sites/netbox_sites_amer.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'slug': row['slug'],
                'region': 'AMER'
            })

print(f"Found {len(agencies)} agencies total")
print(f"  - EMEA: {len([a for a in agencies if a['region'] == 'EMEA'])} agencies")
print(f"  - APAC: {len([a for a in agencies if a['region'] == 'APAC'])} agencies")
print(f"  - AMER: {len([a for a in agencies if a['region'] == 'AMER'])} agencies")

# Generate devices for each agency
print("\nGenerating Meraki devices...")

for agency in agencies:
    site_name = agency['name']

    # 2× Meraki MX68 (HA pair)
    devices.append({
        'name': f'{site_name}-MX-01',
        'manufacturer': 'Cisco Meraki',
        'device_type': 'MX68',
        'role': 'Firewall',
        'site': site_name,
        'location': '',
        'rack': '',
        'position': '',
        'face': '',
        'status': 'active',
        'description': f'Meraki MX68 SD-WAN Appliance - Primary (HA pair)',
        'comments': f'Primary MX in HA pair. VPN to {agency["region"]}-DC-ONPREM hub.'
    })

    devices.append({
        'name': f'{site_name}-MX-02',
        'manufacturer': 'Cisco Meraki',
        'device_type': 'MX68',
        'role': 'Firewall',
        'site': site_name,
        'location': '',
        'rack': '',
        'position': '',
        'face': '',
        'status': 'active',
        'description': f'Meraki MX68 SD-WAN Appliance - Secondary (HA pair)',
        'comments': f'Secondary MX in HA pair. Failover for MX-01.'
    })

    # 2× Meraki MS120-8 switches
    for sw_num in range(1, 3):
        devices.append({
            'name': f'{site_name}-SW-0{sw_num}',
            'manufacturer': 'Cisco Meraki',
            'device_type': 'MS120-8',
            'role': 'Access Switch',
            'site': site_name,
            'location': '',
            'rack': '',
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'Meraki MS120-8 Access Switch {sw_num}',
            'comments': f'8-port cloud-managed switch. Uplinks to both MX-01 and MX-02.'
        })

    # 4× Meraki MR36 WiFi 6 APs
    for ap_num in range(1, 5):
        devices.append({
            'name': f'{site_name}-AP-0{ap_num}',
            'manufacturer': 'Cisco Meraki',
            'device_type': 'MR36',
            'role': 'Wireless AP',
            'site': site_name,
            'location': '',
            'rack': '',
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'Meraki MR36 WiFi 6 Access Point {ap_num}',
            'comments': f'WiFi 6 AP (2×2:2 MU-MIMO). PoE powered from switch.'
        })

print(f"\n✅ Generated {len(devices)} Meraki devices")
print(f"   - {len(agencies)} agencies × 8 devices = {len(agencies) * 8} devices")
print(f"   - Per agency: 2 MX + 2 Switches + 4 APs")

# Write devices CSV
devices_file = 'lab/agencies/netbox_agency_meraki_devices.csv'
with open(devices_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"✅ Meraki devices written to {devices_file}")
