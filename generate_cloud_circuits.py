#!/usr/bin/env python3
"""
Generate circuits for cloud interconnection:
- EMEA: Azure ExpressRoute (via Equinix)
- AMER: AWS Direct Connect (via Equinix)
- APAC: VPN IPSec (no dedicated circuit, over internet)
"""

import csv

circuits = []
circuit_terminations = []

print("Generating cloud interconnection circuits...")

# EMEA - Azure ExpressRoute
print("\nEMEA: Azure ExpressRoute")
circuits.append({
    'cid': 'EXPRESSROUTE-EMEA-001',
    'provider': 'Microsoft Azure',
    'type': 'ExpressRoute',
    'status': 'active',
    'install_date': '2024-01-15',
    'commit_rate': '1000',  # 1 Gbps
    'description': 'Azure ExpressRoute - EMEA OnPrem to Azure eu-west-1',
    'comments': 'ExpressRoute circuit via Equinix Amsterdam. Primary connection for EMEA-DC-ONPREM to Azure.'
})

# ExpressRoute terminations (A-side: OnPrem, Z-side: Azure)
circuit_terminations.extend([
    {
        'circuit': 'EXPRESSROUTE-EMEA-001',
        'term_side': 'A',
        'site': 'EMEA-DC-ONPREM',
        'port_speed': '1000',
        'upstream_speed': '1000',
        'description': 'EMEA OnPrem ExpressRoute endpoint'
    },
    {
        'circuit': 'EXPRESSROUTE-EMEA-001',
        'term_side': 'Z',
        'site': 'EMEA-DC-CLOUD',
        'port_speed': '1000',
        'upstream_speed': '1000',
        'description': 'Azure ExpressRoute Gateway (eu-west-1)'
    }
])

print(f"  - Circuit: EXPRESSROUTE-EMEA-001 (1 Gbps)")
print(f"  - A-side: EMEA-DC-ONPREM")
print(f"  - Z-side: EMEA-DC-CLOUD (Azure)")
print(f"  - Provider: Microsoft Azure (via Equinix)")

# AMER - AWS Direct Connect
print("\nAMER: AWS Direct Connect")
circuits.append({
    'cid': 'DIRECTCONNECT-AMER-001',
    'provider': 'Amazon Web Services',
    'type': 'Direct Connect',
    'status': 'active',
    'install_date': '2024-02-01',
    'commit_rate': '10000',  # 10 Gbps
    'description': 'AWS Direct Connect - AMER OnPrem to AWS us-east-1',
    'comments': 'Direct Connect via Equinix Ashburn. Primary connection for AMER-DC-ONPREM to AWS.'
})

# Direct Connect terminations
circuit_terminations.extend([
    {
        'circuit': 'DIRECTCONNECT-AMER-001',
        'term_side': 'A',
        'site': 'AMER-DC-ONPREM',
        'port_speed': '10000',
        'upstream_speed': '10000',
        'description': 'AMER OnPrem Direct Connect endpoint'
    },
    {
        'circuit': 'DIRECTCONNECT-AMER-001',
        'term_side': 'Z',
        'site': 'AMER-DC-CLOUD',
        'port_speed': '10000',
        'upstream_speed': '10000',
        'description': 'AWS Direct Connect Gateway (us-east-1)'
    }
])

print(f"  - Circuit: DIRECTCONNECT-AMER-001 (10 Gbps)")
print(f"  - A-side: AMER-DC-ONPREM")
print(f"  - Z-side: AMER-DC-CLOUD (AWS)")
print(f"  - Provider: Amazon Web Services (via Equinix)")

# APAC - No dedicated circuit (VPN over Internet)
print("\nAPAC: VPN IPSec (no dedicated circuit)")
print(f"  - Site-to-Site VPN over internet")
print(f"  - APAC-DC-ONPREM ↔ APAC-DC-CLOUD (GCP)")
print(f"  - 2 IPSec tunnels for redundancy")
print(f"  - See separate VPN tunnel configuration file")

print(f"\n✅ Generated {len(circuits)} circuits")
print(f"   - ExpressRoute: 1 circuit (EMEA)")
print(f"   - Direct Connect: 1 circuit (AMER)")
print(f"   - VPN IPSec: Configured separately (APAC)")

# Write circuits CSV
circuits_file = 'lab/circuits/netbox_cloud_circuits.csv'
with open(circuits_file, 'w', newline='') as f:
    fieldnames = ['cid', 'provider', 'type', 'status', 'install_date',
                  'commit_rate', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(circuits)

print(f"✅ Circuits written to {circuits_file}")

# Write circuit terminations CSV
terminations_file = 'lab/circuits/netbox_cloud_circuit_terminations.csv'
with open(terminations_file, 'w', newline='') as f:
    fieldnames = ['circuit', 'term_side', 'site', 'port_speed',
                  'upstream_speed', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(circuit_terminations)

print(f"✅ Circuit terminations written to {terminations_file}")
