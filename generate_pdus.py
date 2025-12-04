#!/usr/bin/env python3
"""
Generate PDU devices for all datacenter racks.
Each rack gets 2 PDUs (A and B feeds for redundancy).
"""

import csv

# Sites
sites = ['EMEA-DC-CLOUD', 'EMEA-DC-ONPREM', 'APAC-DC-CLOUD', 'APAC-DC-ONPREM', 'AMER-DC-CLOUD', 'AMER-DC-ONPREM']

pdus = []

print("Generating PDUs for datacenter racks...")

for site in sites:
    print(f"\n{site}:")

    # Network Core racks (4 racks)
    print("  - Network Core racks")
    for rack_num in range(1, 5):
        rack = f'{site}-NET-R0{rack_num}'

        # PDU-A (Metered)
        pdus.append({
            'name': f'{rack}-PDU-A',
            'manufacturer': 'APC by Schneider Electric',
            'device_type': 'AP8959EU3',
            'role': 'PDU',
            'site': site,
            'location': f'{site}-Network Core',
            'rack': rack,
            'position': '',  # Zero-U device
            'face': '',
            'status': 'active',
            'description': f'PDU A-feed for {rack}'
        })

        # PDU-B (Switched)
        pdus.append({
            'name': f'{rack}-PDU-B',
            'manufacturer': 'APC by Schneider Electric',
            'device_type': 'AP8981',
            'role': 'PDU',
            'site': site,
            'location': f'{site}-Network Core',
            'rack': rack,
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'PDU B-feed for {rack}'
        })

    # Server Halls (2 halls: A and B)
    for hall in ['A', 'B']:
        print(f"  - Server Hall {hall}")

        # Spine/Leaf racks (4 racks per hall)
        for rack_num in range(1, 5):
            rack = f'{site}-SRV-{hall}-R0{rack_num}'

            pdus.append({
                'name': f'{rack}-PDU-A',
                'manufacturer': 'APC by Schneider Electric',
                'device_type': 'AP8959EU3',
                'role': 'PDU',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': '',
                'face': '',
                'status': 'active',
                'description': f'PDU A-feed for {rack}'
            })

            pdus.append({
                'name': f'{rack}-PDU-B',
                'manufacturer': 'APC by Schneider Electric',
                'device_type': 'AP8981',
                'role': 'PDU',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': '',
                'face': '',
                'status': 'active',
                'description': f'PDU B-feed for {rack}'
            })

        # Additional server racks (R05, R06)
        for rack_num in [5, 6]:
            rack = f'{site}-SRV-{hall}-R0{rack_num}'

            pdus.append({
                'name': f'{rack}-PDU-A',
                'manufacturer': 'APC by Schneider Electric',
                'device_type': 'AP8959EU3',
                'role': 'PDU',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': '',
                'face': '',
                'status': 'active',
                'description': f'PDU A-feed for {rack}'
            })

            pdus.append({
                'name': f'{rack}-PDU-B',
                'manufacturer': 'APC by Schneider Electric',
                'device_type': 'AP8981',
                'role': 'PDU',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': '',
                'face': '',
                'status': 'active',
                'description': f'PDU B-feed for {rack}'
            })

    # Storage racks
    print("  - Storage racks")
    for rack_num in range(1, 4):
        rack = f'{site}-STG-R0{rack_num}'

        pdus.append({
            'name': f'{rack}-PDU-A',
            'manufacturer': 'APC by Schneider Electric',
            'device_type': 'AP8959EU3',
            'role': 'PDU',
            'site': site,
            'location': f'{site}-Storage',
            'rack': rack,
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'PDU A-feed for {rack}'
        })

        pdus.append({
            'name': f'{rack}-PDU-B',
            'manufacturer': 'APC by Schneider Electric',
            'device_type': 'AP8981',
            'role': 'PDU',
            'site': site,
            'location': f'{site}-Storage',
            'rack': rack,
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'PDU B-feed for {rack}'
        })

    # MMR (Meet Me Room) racks
    print("  - MMR racks")
    for rack_num in range(1, 3):
        rack = f'{site}-MMR-R0{rack_num}'

        pdus.append({
            'name': f'{rack}-PDU-A',
            'manufacturer': 'APC by Schneider Electric',
            'device_type': 'AP8959EU3',
            'role': 'PDU',
            'site': site,
            'location': f'{site}-MMR',
            'rack': rack,
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'PDU A-feed for {rack}'
        })

        pdus.append({
            'name': f'{rack}-PDU-B',
            'manufacturer': 'APC by Schneider Electric',
            'device_type': 'AP8981',
            'role': 'PDU',
            'site': site,
            'location': f'{site}-MMR',
            'rack': rack,
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'PDU B-feed for {rack}'
        })

print(f"\n✅ Generated {len(pdus)} PDUs (2 per rack for redundancy)")

# Write PDUs CSV
pdus_file = 'lab/netbox_dc_pdus.csv'
with open(pdus_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(pdus)

print(f"✅ PDUs written to {pdus_file}")
