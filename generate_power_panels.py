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
    'Storage Room',
    'Meet Me Room'
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
            'site': site,
            'location': location_full,
            'description': f'Primary power panel A-feed for {location}'
        })

        # Panel-B (Secondary feed)
        power_panels.append({
            'name': f'{site}-{location_slug}-PANEL-B',
            'site': site,
            'location': location_full,
            'description': f'Secondary power panel B-feed for {location}'
        })

print(f"\n✅ Generated {len(power_panels)} power panels")
print(f"   - {len(sites)} sites × {len(locations)} locations × 2 panels = {len(power_panels)} panels")

# Write power panels CSV
panels_file = 'lab/power/netbox_dc_power_panels.csv'
with open(panels_file, 'w', newline='') as f:
    fieldnames = ['name', 'site', 'location', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_panels)

print(f"✅ Power panels written to {panels_file}")
