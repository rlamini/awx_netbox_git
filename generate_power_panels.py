#!/usr/bin/env python3
"""
Generate power panels (electrical distribution panels) for datacenters.
Each location gets 2 power panels (Panel-A and Panel-B) for redundancy.
"""

import csv

# Sites
sites = ['EMEA-DC-CLOUD', 'EMEA-DC-ONPREM', 'APAC-DC-CLOUD', 'APAC-DC-ONPREM', 'AMER-DC-CLOUD', 'AMER-DC-ONPREM']

# Locations in each site
locations = [
    'Network Core',
    'Server Hall A',
    'Server Hall B',
    'Storage',
    'MMR'
]

power_panels = []

print("Generating power panels for datacenter locations...")

for site in sites:
    print(f"\n{site}:")

    for location in locations:
        location_full = f'{site}-{location}'
        location_slug = location.replace(' ', '-')

        # Panel-A (Primary feed)
        power_panels.append({
            'name': f'{site}-{location_slug}-PANEL-A',
            'manufacturer': 'Generic',
            'device_type': '480V/208V 3-Phase Panel',
            'role': 'PDU',  # Use PDU role for power infrastructure
            'site': site,
            'location': location_full,
            'rack': '',  # Not rack-mounted
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'Primary power panel A-feed for {location}'
        })

        # Panel-B (Secondary feed)
        power_panels.append({
            'name': f'{site}-{location_slug}-PANEL-B',
            'manufacturer': 'Generic',
            'device_type': '480V/208V 3-Phase Panel',
            'role': 'PDU',
            'site': site,
            'location': location_full,
            'rack': '',
            'position': '',
            'face': '',
            'status': 'active',
            'description': f'Secondary power panel B-feed for {location}'
        })

print(f"\n✅ Generated {len(power_panels)} power panels")
print(f"   - {len(sites)} sites × {len(locations)} locations × 2 panels = {len(power_panels)} panels")

# Write power panels CSV
panels_file = 'lab/netbox_dc_power_panels.csv'
with open(panels_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_panels)

print(f"✅ Power panels written to {panels_file}")
