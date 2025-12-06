#!/usr/bin/env python3
"""
Generate ESXi host devices for virtualization clusters.
Places ESXi hosts in server hall racks across all datacenters.
"""

import csv

# Sites - Only ONPREM sites have physical ESXi hosts
# CLOUD sites use managed cloud services (Azure, GCP, AWS)
sites = ['EMEA-DC-ONPREM', 'APAC-DC-ONPREM', 'AMER-DC-ONPREM']

esxi_hosts = []

print("Generating ESXi hosts for datacenter server halls...")

for site in sites:
    print(f"\n{site}:")

    # Server Hall A - Compute Cluster (6 hosts using Dell R750)
    print("  - Server Hall A (Compute Cluster)")
    for host_num in range(1, 7):
        rack_num = ((host_num - 1) // 2) + 1  # 2 hosts per rack (R01-R03)
        rack = f'{site}-SRV-A-R0{rack_num}'

        # Position in rack (starting at U39 for first host, U37 for second)
        position = 39 - ((host_num - 1) % 2) * 2  # 39, 37 (2U spacing)

        esxi_hosts.append({
            'name': f'{site}-ESX-A{host_num:02d}',
            'manufacturer': 'Dell',
            'device_type': 'PowerEdge R750',
            'role': 'Server',
            'site': site,
            'location': f'{site}-Server Hall A',
            'rack': rack,
            'position': position,
            'face': 'front',
            'status': 'active',
            'description': f'VMware ESXi host - Compute cluster (Server Hall A)'
        })

    # Server Hall B - Storage Cluster (4 hosts using Dell R750)
    print("  - Server Hall B (Storage Cluster)")
    for host_num in range(1, 5):
        rack_num = ((host_num - 1) // 2) + 1  # 2 hosts per rack (R01-R02)
        rack = f'{site}-SRV-B-R0{rack_num}'

        position = 39 - ((host_num - 1) % 2) * 2

        esxi_hosts.append({
            'name': f'{site}-ESX-B{host_num:02d}',
            'manufacturer': 'Dell',
            'device_type': 'PowerEdge R750',
            'role': 'Server',
            'site': site,
            'location': f'{site}-Server Hall B',
            'rack': rack,
            'position': position,
            'face': 'front',
            'status': 'active',
            'description': f'VMware ESXi host - Storage/vSAN cluster (Server Hall B)'
        })

    # Management Cluster (3 hosts using Cisco UCS in Server Hall A racks R04-R06)
    print("  - Server Hall A (Management Cluster)")
    for host_num in range(1, 4):
        rack_num = host_num + 3  # R04, R05, R06
        rack = f'{site}-SRV-A-R0{rack_num}'

        esxi_hosts.append({
            'name': f'{site}-ESX-MGT{host_num:02d}',
            'manufacturer': 'Cisco',
            'device_type': 'UCS C240 M6',
            'role': 'Server',
            'site': site,
            'location': f'{site}-Server Hall A',
            'rack': rack,
            'position': 39,
            'face': 'front',
            'status': 'active',
            'description': f'VMware ESXi host - Management cluster (vCenter, NSX, etc.)'
        })

print(f"\n✅ Generated {len(esxi_hosts)} ESXi hosts")
print(f"   - 3 ONPREM sites × 13 hosts = 39 ESXi hosts total")
print(f"   - Per site: 6 Compute + 4 Storage + 3 Management")
print(f"   - CLOUD sites (EMEA-Azure, APAC-GCP, AMER-AWS) use managed cloud services")

# Write ESXi hosts CSV
esxi_file = 'lab/virtualization/netbox_dc_esxi_hosts.csv'
with open(esxi_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(esxi_hosts)

print(f"✅ ESXi hosts written to {esxi_file}")
