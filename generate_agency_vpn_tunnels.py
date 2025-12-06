#!/usr/bin/env python3
"""
Generate VPN tunnel documentation for agency branches.
Each agency has Meraki Auto VPN (SD-WAN) tunnels to regional DC hubs:
- EMEA agencies → EMEA-DC-ONPREM
- APAC agencies → APAC-DC-ONPREM
- AMER agencies → AMER-DC-ONPREM

Tunnels are established over both ADSL (primary) and 5G (backup) circuits.
"""

import csv
import json

vpn_tunnels = []

print("Generating Meraki Auto VPN tunnel documentation...")

# Read agencies from site files
agencies = []

# EMEA agencies
with open('lab/sites/netbox_sites_emea.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'region': 'EMEA',
                'hub': 'EMEA-DC-ONPREM'
            })

# APAC agencies
with open('lab/sites/netbox_sites_apac.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'region': 'APAC',
                'hub': 'APAC-DC-ONPREM'
            })

# AMER agencies
with open('lab/sites/netbox_sites_amer.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if 'agency' in row['tags'].lower():
            agencies.append({
                'name': row['name'],
                'region': 'AMER',
                'hub': 'AMER-DC-ONPREM'
            })

print(f"Found {len(agencies)} agencies")

# Generate VPN tunnel documentation
print("\nGenerating VPN tunnel configuration...")

for agency in agencies:
    site_name = agency['name']
    hub = agency['hub']

    # Meraki Auto VPN tunnel (automatically configured)
    vpn_tunnels.append({
        'name': f'{site_name}-VPN-TO-{hub}',
        'type': 'Meraki Auto VPN',
        'spoke_site': site_name,
        'spoke_device': f'{site_name}-MX-01',  # Primary MX
        'hub_site': hub,
        'hub_device': f'{hub}-MERAKI-HUB-MX',  # Hub MX at datacenter
        'primary_wan': 'ADSL',
        'backup_wan': '5G',
        'encryption': 'AES-256',
        'status': 'active',
        'failover': 'automatic',
        'description': f'Meraki SD-WAN tunnel from {site_name} to {hub}',
        'comments': 'Auto VPN with automatic failover between ADSL and 5G. Managed via Meraki Dashboard.'
    })

print(f"\n✅ Generated {len(vpn_tunnels)} VPN tunnel configurations")
print(f"   - EMEA agencies → EMEA-DC-ONPREM: {len([t for t in vpn_tunnels if 'EMEA' in t['hub_site']])} tunnels")
print(f"   - APAC agencies → APAC-DC-ONPREM: {len([t for t in vpn_tunnels if 'APAC' in t['hub_site']])} tunnels")
print(f"   - AMER agencies → AMER-DC-ONPREM: {len([t for t in vpn_tunnels if 'AMER' in t['hub_site']])} tunnels")

# Write VPN tunnels CSV
vpn_file = 'lab/agencies/netbox_agency_vpn_tunnels.csv'
with open(vpn_file, 'w', newline='') as f:
    fieldnames = ['name', 'type', 'spoke_site', 'spoke_device', 'hub_site', 'hub_device',
                  'primary_wan', 'backup_wan', 'encryption', 'status', 'failover',
                  'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(vpn_tunnels)

print(f"✅ VPN tunnels written to {vpn_file}")

# Also create JSON format
vpn_json_file = 'lab/agencies/netbox_agency_vpn_tunnels.json'
with open(vpn_json_file, 'w') as f:
    json.dump(vpn_tunnels, f, indent=2)

print(f"✅ VPN tunnels JSON written to {vpn_json_file}")

print("\nNote: Meraki Auto VPN tunnels are automatically managed.")
print("Track in NetBox via:")
print("  - Config contexts on MX devices")
print("  - Journal entries")
print("  - Custom fields")
print("  - Or import as documentation")
