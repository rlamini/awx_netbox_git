#!/usr/bin/env python3
"""
Generate VPN IPSec tunnel information for APAC (GCP).
Since NetBox doesn't have native VPN tunnel objects, we'll document them
in a structured format for import as custom fields or documentation.
"""

import csv
import json

vpn_tunnels = []

print("Generating VPN IPSec tunnels for APAC (GCP)...")

# APAC - GCP Cloud VPN
print("\nAPAC: Site-to-Site VPN between OnPrem and GCP")

# Tunnel 1
vpn_tunnels.append({
    'name': 'APAC-GCP-VPN-TUNNEL-1',
    'site_a': 'APAC-DC-ONPREM',
    'site_z': 'APAC-DC-CLOUD',
    'status': 'active',
    'type': 'IPSec',
    'encryption': 'AES-256-GCM',
    'authentication': 'SHA256',
    'ike_version': 'IKEv2',
    'pfs_group': 'DH Group 14',
    'peer_a_ip': '203.0.113.10',  # OnPrem public IP (example)
    'peer_z_ip': '198.51.100.20',  # GCP Cloud VPN Gateway IP (example)
    'local_subnet': '10.50.0.0/16',  # APAC OnPrem network
    'remote_subnet': '10.200.0.0/16',  # GCP PROD VPC
    'description': 'Primary IPSec tunnel - APAC OnPrem to GCP',
    'comments': 'HA VPN tunnel 1. Routes traffic between APAC-DC-ONPREM and GCP VPC.'
})

# Tunnel 2 (redundant)
vpn_tunnels.append({
    'name': 'APAC-GCP-VPN-TUNNEL-2',
    'site_a': 'APAC-DC-ONPREM',
    'site_z': 'APAC-DC-CLOUD',
    'status': 'active',
    'type': 'IPSec',
    'encryption': 'AES-256-GCM',
    'authentication': 'SHA256',
    'ike_version': 'IKEv2',
    'pfs_group': 'DH Group 14',
    'peer_a_ip': '203.0.113.11',  # OnPrem public IP 2 (example)
    'peer_z_ip': '198.51.100.21',  # GCP Cloud VPN Gateway IP 2 (example)
    'local_subnet': '10.50.0.0/16',  # APAC OnPrem network
    'remote_subnet': '10.200.0.0/16',  # GCP PROD VPC
    'description': 'Secondary IPSec tunnel - APAC OnPrem to GCP (redundant)',
    'comments': 'HA VPN tunnel 2. Provides redundancy for tunnel 1.'
})

print(f"  - Tunnel 1: APAC-GCP-VPN-TUNNEL-1")
print(f"    OnPrem: 203.0.113.10 → GCP: 198.51.100.20")
print(f"    10.50.0.0/16 ↔ 10.200.0.0/16")
print(f"  - Tunnel 2: APAC-GCP-VPN-TUNNEL-2 (redundant)")
print(f"    OnPrem: 203.0.113.11 → GCP: 198.51.100.21")
print(f"    10.50.0.0/16 ↔ 10.200.0.0/16")

print(f"\n✅ Generated {len(vpn_tunnels)} VPN IPSec tunnels")
print(f"   - High Availability: 2 tunnels for redundancy")
print(f"   - Encryption: AES-256-GCM")
print(f"   - IKE: IKEv2 with SHA256")

# Write VPN tunnels CSV
vpn_file = 'lab/circuits/netbox_cloud_vpn_tunnels.csv'
with open(vpn_file, 'w', newline='') as f:
    fieldnames = ['name', 'site_a', 'site_z', 'status', 'type', 'encryption',
                  'authentication', 'ike_version', 'pfs_group', 'peer_a_ip',
                  'peer_z_ip', 'local_subnet', 'remote_subnet', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(vpn_tunnels)

print(f"✅ VPN tunnels written to {vpn_file}")

# Also create a JSON file for detailed configuration
vpn_json_file = 'lab/circuits/netbox_cloud_vpn_tunnels.json'
with open(vpn_json_file, 'w') as f:
    json.dump(vpn_tunnels, f, indent=2)

print(f"✅ VPN tunnels JSON written to {vpn_json_file}")
print(f"\nNote: Import VPN tunnels as custom configuration or documentation in NetBox.")
print(f"NetBox doesn't have native VPN tunnel objects, but you can track them via:")
print(f"  - Custom fields on circuits")
print(f"  - Config contexts on devices")
print(f"  - Journal entries")
