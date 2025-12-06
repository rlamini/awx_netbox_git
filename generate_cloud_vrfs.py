#!/usr/bin/env python3
"""
Generate VRFs for cloud VPCs/VNets.
- EMEA uses Azure (VNets)
- APAC uses GCP (VPCs)
- AMER uses AWS (VPCs)
"""

import csv

vrfs = []

# EMEA - Azure VNets
print("Generating Azure VNets (EMEA)...")
vrfs.append({
    'name': 'EMEA-AZURE-PROD-VNET',
    'rd': '65001:100',
    'description': 'Azure Production VNet - EMEA (eu-west-1)',
    'tenant': '',
    'enforce_unique': True
})

vrfs.append({
    'name': 'EMEA-AZURE-MGMT-VNET',
    'rd': '65001:200',
    'description': 'Azure Management VNet - EMEA (eu-west-1)',
    'tenant': '',
    'enforce_unique': True
})

# APAC - GCP VPCs
print("Generating GCP VPCs (APAC)...")
vrfs.append({
    'name': 'APAC-GCP-PROD-VPC',
    'rd': '65002:100',
    'description': 'GCP Production VPC - APAC (asia-southeast1)',
    'tenant': '',
    'enforce_unique': True
})

vrfs.append({
    'name': 'APAC-GCP-MGMT-VPC',
    'rd': '65002:200',
    'description': 'GCP Management VPC - APAC (asia-southeast1)',
    'tenant': '',
    'enforce_unique': True
})

# AMER - AWS VPCs
print("Generating AWS VPCs (AMER)...")
vrfs.append({
    'name': 'AMER-AWS-PROD-VPC',
    'rd': '65003:100',
    'description': 'AWS Production VPC - AMER (us-east-1)',
    'tenant': '',
    'enforce_unique': True
})

vrfs.append({
    'name': 'AMER-AWS-MGMT-VPC',
    'rd': '65003:200',
    'description': 'AWS Management VPC - AMER (us-east-1)',
    'tenant': '',
    'enforce_unique': True
})

print(f"\n✅ Generated {len(vrfs)} cloud VRFs")
print(f"   - 2 Azure VNets (EMEA)")
print(f"   - 2 GCP VPCs (APAC)")
print(f"   - 2 AWS VPCs (AMER)")

# Write VRFs CSV
vrfs_file = 'lab/circuits/netbox_cloud_vrfs.csv'
with open(vrfs_file, 'w', newline='') as f:
    fieldnames = ['name', 'rd', 'description', 'tenant', 'enforce_unique']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(vrfs)

print(f"✅ Cloud VRFs written to {vrfs_file}")
