#!/usr/bin/env python3
"""
Generate circuits for all agency branches.
Each agency has:
- 1× ADSL circuit (primary connectivity)
- 1× 5G circuit (backup connectivity)
Both connect to regional DC hubs via VPN.
"""

import csv

circuits = []
circuit_terminations = []

print("Generating circuits for all agency branches...")

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
                'adsl_provider': 'Orange Business Services',
                '5g_provider': 'Vodafone Business',
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
                'adsl_provider': 'Singtel',
                '5g_provider': '3 Business',
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
                'adsl_provider': 'Verizon Business',
                '5g_provider': 'T-Mobile Business',
                'hub': 'AMER-DC-ONPREM'
            })

print(f"Found {len(agencies)} agencies")
print(f"  - EMEA: {len([a for a in agencies if a['region'] == 'EMEA'])} agencies")
print(f"  - APAC: {len([a for a in agencies if a['region'] == 'APAC'])} agencies")
print(f"  - AMER: {len([a for a in agencies if a['region'] == 'AMER'])} agencies")

# Generate circuits for each agency
print("\nGenerating circuits...")

for idx, agency in enumerate(agencies, start=1):
    site_name = agency['name']

    # ADSL Circuit (Primary)
    adsl_cid = f'ADSL-{agency["region"]}-{idx:04d}'
    circuits.append({
        'cid': adsl_cid,
        'provider': agency['adsl_provider'],
        'type': 'ADSL',
        'status': 'active',
        'install_date': '2024-01-01',
        'commit_rate': '50',  # 50 Mbps
        'description': f'ADSL circuit for {site_name}',
        'comments': f'Primary internet connectivity. VPN to {agency["hub"]}.'
    })

    # ADSL Termination (A-side: Agency, Z-side: Provider)
    circuit_terminations.append({
        'circuit': adsl_cid,
        'term_side': 'A',
        'site': site_name,
        'port_speed': '50',
        'upstream_speed': '50',
        'description': f'{site_name} ADSL endpoint'
    })

    # 5G Circuit (Backup)
    fiveg_cid = f'5G-{agency["region"]}-{idx:04d}'
    circuits.append({
        'cid': fiveg_cid,
        'provider': agency['5g_provider'],
        'type': '5G',
        'status': 'active',
        'install_date': '2024-01-01',
        'commit_rate': '100',  # 100 Mbps (5G)
        'description': f'5G backup circuit for {site_name}',
        'comments': f'Backup connectivity (failover). VPN to {agency["hub"]}.'
    })

    # 5G Termination (A-side: Agency)
    circuit_terminations.append({
        'circuit': fiveg_cid,
        'term_side': 'A',
        'site': site_name,
        'port_speed': '100',
        'upstream_speed': '100',
        'description': f'{site_name} 5G endpoint'
    })

print(f"\n✅ Generated {len(circuits)} circuits")
print(f"   - ADSL circuits: {len(agencies)} (50 Mbps each)")
print(f"   - 5G circuits: {len(agencies)} (100 Mbps each, backup)")
print(f"   - Total: {len(agencies)} agencies × 2 circuits = {len(circuits)} circuits")

# Write circuits CSV
circuits_file = 'lab/agencies/netbox_agency_circuits.csv'
with open(circuits_file, 'w', newline='') as f:
    fieldnames = ['cid', 'provider', 'type', 'status', 'install_date',
                  'commit_rate', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(circuits)

print(f"✅ Circuits written to {circuits_file}")

# Write circuit terminations CSV
terminations_file = 'lab/agencies/netbox_agency_circuit_terminations.csv'
with open(terminations_file, 'w', newline='') as f:
    fieldnames = ['circuit', 'term_side', 'site', 'port_speed',
                  'upstream_speed', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(circuit_terminations)

print(f"✅ Circuit terminations written to {terminations_file}")
