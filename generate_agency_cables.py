#!/usr/bin/env python3
"""
Generate cables for all agency branches.
Each agency has standard cabling:
- 1× HA cable (MX-01 ↔ MX-02)
- 4× Uplink cables (both MX to both switches)
- 4× AP cables (switches to APs)
Total: 9 cables per agency
"""

import csv

cables = []

print("Generating cables for all agency branches...")

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

# Generate cables for each agency
print("\nGenerating cables...")

for agency in agencies:
    site_name = agency['name']

    # 1. HA Cable: MX-01 ↔ MX-02 (dedicated link for HA heartbeat)
    cables.append({
        'side_a_device': f'{site_name}-MX-01',
        'side_a_type': 'interface',
        'side_a_name': 'Port 8',
        'side_b_device': f'{site_name}-MX-02',
        'side_b_type': 'interface',
        'side_b_name': 'Port 8',
        'type': 'cat6',
        'status': 'connected',
        'color': 'red',
        'length': '1',
        'length_unit': 'm',
        'label': f'{site_name}-HA-CABLE',
        'description': 'MX HA heartbeat link'
    })

    # 2. Uplink cables: MX → Switches (4 cables for redundancy)
    # MX-01 → SW-01
    cables.append({
        'side_a_device': f'{site_name}-MX-01',
        'side_a_type': 'interface',
        'side_a_name': 'Port 1',
        'side_b_device': f'{site_name}-SW-01',
        'side_b_type': 'interface',
        'side_b_name': 'Port 7',
        'type': 'cat6',
        'status': 'connected',
        'color': 'blue',
        'length': '3',
        'length_unit': 'm',
        'label': f'{site_name}-MX01-SW01',
        'description': 'Uplink MX-01 to SW-01'
    })

    # MX-01 → SW-02
    cables.append({
        'side_a_device': f'{site_name}-MX-01',
        'side_a_type': 'interface',
        'side_a_name': 'Port 2',
        'side_b_device': f'{site_name}-SW-02',
        'side_b_type': 'interface',
        'side_b_name': 'Port 7',
        'type': 'cat6',
        'status': 'connected',
        'color': 'blue',
        'length': '3',
        'length_unit': 'm',
        'label': f'{site_name}-MX01-SW02',
        'description': 'Uplink MX-01 to SW-02'
    })

    # MX-02 → SW-01
    cables.append({
        'side_a_device': f'{site_name}-MX-02',
        'side_a_type': 'interface',
        'side_a_name': 'Port 1',
        'side_b_device': f'{site_name}-SW-01',
        'side_b_type': 'interface',
        'side_b_name': 'Port 8',
        'type': 'cat6',
        'status': 'connected',
        'color': 'blue',
        'length': '3',
        'length_unit': 'm',
        'label': f'{site_name}-MX02-SW01',
        'description': 'Uplink MX-02 to SW-01'
    })

    # MX-02 → SW-02
    cables.append({
        'side_a_device': f'{site_name}-MX-02',
        'side_a_type': 'interface',
        'side_a_name': 'Port 2',
        'side_b_device': f'{site_name}-SW-02',
        'side_b_type': 'interface',
        'side_b_name': 'Port 8',
        'type': 'cat6',
        'status': 'connected',
        'color': 'blue',
        'length': '3',
        'length_unit': 'm',
        'label': f'{site_name}-MX02-SW02',
        'description': 'Uplink MX-02 to SW-02'
    })

    # 3. AP cables: Switches → APs (4 cables)
    # SW-01 → AP-01
    cables.append({
        'side_a_device': f'{site_name}-SW-01',
        'side_a_type': 'interface',
        'side_a_name': 'Port 1',
        'side_b_device': f'{site_name}-AP-01',
        'side_b_type': 'interface',
        'side_b_name': 'Port 1',
        'type': 'cat6',
        'status': 'connected',
        'color': 'green',
        'length': '30',
        'length_unit': 'm',
        'label': f'{site_name}-SW01-AP01',
        'description': 'SW-01 to AP-01 (PoE)'
    })

    # SW-01 → AP-02
    cables.append({
        'side_a_device': f'{site_name}-SW-01',
        'side_a_type': 'interface',
        'side_a_name': 'Port 2',
        'side_b_device': f'{site_name}-AP-02',
        'side_b_type': 'interface',
        'side_b_name': 'Port 1',
        'type': 'cat6',
        'status': 'connected',
        'color': 'green',
        'length': '30',
        'length_unit': 'm',
        'label': f'{site_name}-SW01-AP02',
        'description': 'SW-01 to AP-02 (PoE)'
    })

    # SW-02 → AP-03
    cables.append({
        'side_a_device': f'{site_name}-SW-02',
        'side_a_type': 'interface',
        'side_a_name': 'Port 1',
        'side_b_device': f'{site_name}-AP-03',
        'side_b_type': 'interface',
        'side_b_name': 'Port 1',
        'type': 'cat6',
        'status': 'connected',
        'color': 'green',
        'length': '30',
        'length_unit': 'm',
        'label': f'{site_name}-SW02-AP03',
        'description': 'SW-02 to AP-03 (PoE)'
    })

    # SW-02 → AP-04
    cables.append({
        'side_a_device': f'{site_name}-SW-02',
        'side_a_type': 'interface',
        'side_a_name': 'Port 2',
        'side_b_device': f'{site_name}-AP-04',
        'side_b_type': 'interface',
        'side_b_name': 'Port 1',
        'type': 'cat6',
        'status': 'connected',
        'color': 'green',
        'length': '30',
        'length_unit': 'm',
        'label': f'{site_name}-SW02-AP04',
        'description': 'SW-02 to AP-04 (PoE)'
    })

print(f"\n✅ Generated {len(cables)} cables")
print(f"   - {len(agencies)} agencies × 9 cables = {len(cables)} cables")
print(f"   - Per agency:")
print(f"     • 1 HA cable (MX-01 ↔ MX-02)")
print(f"     • 4 uplink cables (MX → Switches)")
print(f"     • 4 AP cables (Switches → APs)")

# Write cables CSV
cables_file = 'lab/agencies/netbox_agency_cables.csv'
with open(cables_file, 'w', newline='') as f:
    fieldnames = ['side_a_device', 'side_a_type', 'side_a_name',
                  'side_b_device', 'side_b_type', 'side_b_name',
                  'type', 'status', 'color', 'length', 'length_unit',
                  'label', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cables)

print(f"✅ Agency cables written to {cables_file}")
