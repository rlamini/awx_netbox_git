#!/usr/bin/env python3
"""
Generate IP prefixes (subnets) for cloud VPCs/VNets.
"""

import csv

prefixes = []

print("Generating cloud IP prefixes...")

# EMEA - Azure VNets
print("\nEMEA-AZURE-PROD-VNET (10.100.0.0/16):")
prefixes.extend([
    {
        'prefix': '10.100.0.0/16',
        'vrf': 'EMEA-AZURE-PROD-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Azure Production VNet - EMEA'
    },
    {
        'prefix': '10.100.1.0/24',
        'vrf': 'EMEA-AZURE-PROD-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Public subnet - AZ 1'
    },
    {
        'prefix': '10.100.2.0/24',
        'vrf': 'EMEA-AZURE-PROD-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Public subnet - AZ 2'
    },
    {
        'prefix': '10.100.10.0/24',
        'vrf': 'EMEA-AZURE-PROD-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Private subnet - AZ 1'
    },
    {
        'prefix': '10.100.11.0/24',
        'vrf': 'EMEA-AZURE-PROD-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Private subnet - AZ 2'
    }
])

print("  - 10.100.0.0/16 (VNet)")
print("  - 10.100.1.0/24 (Public AZ1)")
print("  - 10.100.2.0/24 (Public AZ2)")
print("  - 10.100.10.0/24 (Private AZ1)")
print("  - 10.100.11.0/24 (Private AZ2)")

print("\nEMEA-AZURE-MGMT-VNET (10.101.0.0/16):")
prefixes.extend([
    {
        'prefix': '10.101.0.0/16',
        'vrf': 'EMEA-AZURE-MGMT-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Azure Management VNet - EMEA'
    },
    {
        'prefix': '10.101.1.0/24',
        'vrf': 'EMEA-AZURE-MGMT-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Management subnet'
    },
    {
        'prefix': '10.101.254.0/24',
        'vrf': 'EMEA-AZURE-MGMT-VNET',
        'site': 'EMEA-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'GatewaySubnet (ExpressRoute)'
    }
])

print("  - 10.101.0.0/16 (VNet)")
print("  - 10.101.1.0/24 (Management)")
print("  - 10.101.254.0/24 (GatewaySubnet)")

# APAC - GCP VPCs
print("\nAPAC-GCP-PROD-VPC (10.200.0.0/16):")
prefixes.extend([
    {
        'prefix': '10.200.0.0/16',
        'vrf': 'APAC-GCP-PROD-VPC',
        'site': 'APAC-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'GCP Production VPC - APAC'
    },
    {
        'prefix': '10.200.1.0/24',
        'vrf': 'APAC-GCP-PROD-VPC',
        'site': 'APAC-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Subnet - asia-southeast1-a'
    },
    {
        'prefix': '10.200.2.0/24',
        'vrf': 'APAC-GCP-PROD-VPC',
        'site': 'APAC-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Subnet - asia-southeast1-b'
    },
    {
        'prefix': '10.200.10.0/24',
        'vrf': 'APAC-GCP-PROD-VPC',
        'site': 'APAC-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Private subnet - asia-southeast1-a'
    }
])

print("  - 10.200.0.0/16 (VPC)")
print("  - 10.200.1.0/24 (Subnet AZ-a)")
print("  - 10.200.2.0/24 (Subnet AZ-b)")
print("  - 10.200.10.0/24 (Private AZ-a)")

print("\nAPAC-GCP-MGMT-VPC (10.201.0.0/16):")
prefixes.extend([
    {
        'prefix': '10.201.0.0/16',
        'vrf': 'APAC-GCP-MGMT-VPC',
        'site': 'APAC-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'GCP Management VPC - APAC'
    },
    {
        'prefix': '10.201.1.0/24',
        'vrf': 'APAC-GCP-MGMT-VPC',
        'site': 'APAC-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Management subnet'
    }
])

print("  - 10.201.0.0/16 (VPC)")
print("  - 10.201.1.0/24 (Management)")

# AMER - AWS VPCs
print("\nAMER-AWS-PROD-VPC (10.300.0.0/16):")
prefixes.extend([
    {
        'prefix': '10.300.0.0/16',
        'vrf': 'AMER-AWS-PROD-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'AWS Production VPC - AMER'
    },
    {
        'prefix': '10.300.1.0/24',
        'vrf': 'AMER-AWS-PROD-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Public subnet - us-east-1a'
    },
    {
        'prefix': '10.300.2.0/24',
        'vrf': 'AMER-AWS-PROD-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Public subnet - us-east-1b'
    },
    {
        'prefix': '10.300.10.0/24',
        'vrf': 'AMER-AWS-PROD-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Private subnet - us-east-1a'
    },
    {
        'prefix': '10.300.11.0/24',
        'vrf': 'AMER-AWS-PROD-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Private subnet - us-east-1b'
    }
])

print("  - 10.300.0.0/16 (VPC)")
print("  - 10.300.1.0/24 (Public us-east-1a)")
print("  - 10.300.2.0/24 (Public us-east-1b)")
print("  - 10.300.10.0/24 (Private us-east-1a)")
print("  - 10.300.11.0/24 (Private us-east-1b)")

print("\nAMER-AWS-MGMT-VPC (10.301.0.0/16):")
prefixes.extend([
    {
        'prefix': '10.301.0.0/16',
        'vrf': 'AMER-AWS-MGMT-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'AWS Management VPC - AMER'
    },
    {
        'prefix': '10.301.1.0/24',
        'vrf': 'AMER-AWS-MGMT-VPC',
        'site': 'AMER-DC-CLOUD',
        'status': 'active',
        'role': '',
        'description': 'Management subnet'
    }
])

print("  - 10.301.0.0/16 (VPC)")
print("  - 10.301.1.0/24 (Management)")

print(f"\n✅ Generated {len(prefixes)} IP prefixes")
print(f"   - Azure: 8 prefixes")
print(f"   - GCP: 6 prefixes")
print(f"   - AWS: 8 prefixes")

# Write prefixes CSV
prefixes_file = 'lab/circuits/netbox_cloud_prefixes.csv'
with open(prefixes_file, 'w', newline='') as f:
    fieldnames = ['prefix', 'vrf', 'site', 'status', 'role', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(prefixes)

print(f"✅ Cloud prefixes written to {prefixes_file}")
