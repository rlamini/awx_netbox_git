#!/usr/bin/env python3
"""
Generate virtual gateway devices for cloud connectivity:
- Azure ExpressRoute Gateway (EMEA)
- AWS Direct Connect Gateway (AMER)
- GCP Cloud VPN Gateway (APAC)
"""

import csv

device_types = []
devices = []

print("Generating cloud gateway device types and devices...")

# Device Types
print("\nCreating virtual gateway device types...")

device_types.append({
    'manufacturer': 'Microsoft',
    'model': 'Azure ExpressRoute Gateway',
    'slug': 'azure-expressroute-gateway',
    'u_height': 0,
    'is_full_depth': False,
    'description': 'Azure ExpressRoute Virtual Network Gateway'
})

device_types.append({
    'manufacturer': 'Amazon',
    'model': 'AWS Direct Connect Gateway',
    'slug': 'aws-directconnect-gateway',
    'u_height': 0,
    'is_full_depth': False,
    'description': 'AWS Direct Connect Gateway (Virtual)'
})

device_types.append({
    'manufacturer': 'Google',
    'model': 'GCP Cloud VPN Gateway',
    'slug': 'gcp-cloud-vpn-gateway',
    'u_height': 0,
    'is_full_depth': False,
    'description': 'GCP Cloud VPN Gateway (HA VPN)'
})

print(f"  - Azure ExpressRoute Gateway")
print(f"  - AWS Direct Connect Gateway")
print(f"  - GCP Cloud VPN Gateway")

# Devices
print("\nCreating virtual gateway devices...")

# EMEA - Azure ExpressRoute Gateway
devices.append({
    'name': 'EMEA-AZURE-ER-GW-01',
    'manufacturer': 'Microsoft',
    'device_type': 'Azure ExpressRoute Gateway',
    'role': 'Cloud Gateway',
    'site': 'EMEA-DC-CLOUD',
    'location': '',
    'rack': '',
    'position': '',
    'face': '',
    'status': 'active',
    'description': 'Azure ExpressRoute Gateway - eu-west-1',
    'comments': 'Virtual gateway for ExpressRoute connectivity. Connects EMEA-DC-ONPREM to Azure VNets.'
})

print(f"  - EMEA-AZURE-ER-GW-01 (ExpressRoute Gateway)")

# AMER - AWS Direct Connect Gateway
devices.append({
    'name': 'AMER-AWS-DX-GW-01',
    'manufacturer': 'Amazon',
    'device_type': 'AWS Direct Connect Gateway',
    'role': 'Cloud Gateway',
    'site': 'AMER-DC-CLOUD',
    'location': '',
    'rack': '',
    'position': '',
    'face': '',
    'status': 'active',
    'description': 'AWS Direct Connect Gateway - us-east-1',
    'comments': 'Virtual gateway for Direct Connect. Connects AMER-DC-ONPREM to AWS VPCs.'
})

print(f"  - AMER-AWS-DX-GW-01 (Direct Connect Gateway)")

# APAC - GCP Cloud VPN Gateway (HA VPN - 2 instances)
devices.append({
    'name': 'APAC-GCP-VPN-GW-01',
    'manufacturer': 'Google',
    'device_type': 'GCP Cloud VPN Gateway',
    'role': 'Cloud Gateway',
    'site': 'APAC-DC-CLOUD',
    'location': '',
    'rack': '',
    'position': '',
    'face': '',
    'status': 'active',
    'description': 'GCP Cloud VPN Gateway 1 - asia-southeast1',
    'comments': 'HA VPN Gateway interface 1. Terminates IPSec tunnel 1 from APAC-DC-ONPREM.'
})

devices.append({
    'name': 'APAC-GCP-VPN-GW-02',
    'manufacturer': 'Google',
    'device_type': 'GCP Cloud VPN Gateway',
    'role': 'Cloud Gateway',
    'site': 'APAC-DC-CLOUD',
    'location': '',
    'rack': '',
    'position': '',
    'face': '',
    'status': 'active',
    'description': 'GCP Cloud VPN Gateway 2 - asia-southeast1',
    'comments': 'HA VPN Gateway interface 2. Terminates IPSec tunnel 2 from APAC-DC-ONPREM (redundant).'
})

print(f"  - APAC-GCP-VPN-GW-01 (Cloud VPN Gateway 1)")
print(f"  - APAC-GCP-VPN-GW-02 (Cloud VPN Gateway 2 - HA)")

# OnPrem VPN endpoints for APAC
devices.append({
    'name': 'APAC-ONPREM-VPN-FW-01',
    'manufacturer': 'Palo Alto Networks',
    'device_type': 'PA-5220',
    'role': 'Firewall',
    'site': 'APAC-DC-ONPREM',
    'location': 'APAC-DC-ONPREM-Network Core',
    'rack': 'APAC-DC-ONPREM-NET-R01',
    'position': '35',
    'face': 'front',
    'status': 'active',
    'description': 'VPN Firewall - IPSec endpoint for GCP',
    'comments': 'Terminates IPSec VPN tunnels to GCP Cloud VPN Gateway.'
})

print(f"  - APAC-ONPREM-VPN-FW-01 (OnPrem VPN endpoint)")

print(f"\n✅ Generated {len(device_types)} gateway device types")
print(f"✅ Generated {len(devices)} gateway devices")
print(f"   - Azure: 1 ExpressRoute Gateway")
print(f"   - AWS: 1 Direct Connect Gateway")
print(f"   - GCP: 2 Cloud VPN Gateways (HA)")
print(f"   - OnPrem: 1 VPN Firewall")

# Write device types CSV
device_types_file = 'lab/virtualization/netbox_cloud_gateway_device_types.csv'
with open(device_types_file, 'w', newline='') as f:
    fieldnames = ['manufacturer', 'model', 'slug', 'u_height', 'is_full_depth', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(device_types)

print(f"✅ Gateway device types written to {device_types_file}")

# Write devices CSV
devices_file = 'lab/virtualization/netbox_cloud_gateways.csv'
with open(devices_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(devices)

print(f"✅ Gateway devices written to {devices_file}")
