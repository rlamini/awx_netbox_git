#!/usr/bin/env python3
"""
Generate VMware cluster types and clusters for virtualization infrastructure.
Creates Compute, Storage, and Management clusters for each datacenter.
"""

import csv

# Sites - Only ONPREM sites have VMware vSphere clusters
# CLOUD sites use managed cloud services (Azure, GCP, AWS)
sites = ['EMEA-DC-ONPREM', 'APAC-DC-ONPREM', 'AMER-DC-ONPREM']

# Cluster Types
cluster_types = [
    {
        'name': 'VMware vSphere',
        'slug': 'vmware-vsphere',
        'description': 'VMware vSphere virtualization cluster'
    }
]

# Cluster Groups (for organizing clusters)
cluster_groups = [
    {
        'name': 'Production',
        'slug': 'production',
        'description': 'Production virtualization clusters'
    },
    {
        'name': 'Management',
        'slug': 'management',
        'description': 'Management and infrastructure clusters'
    }
]

clusters = []

print("Generating VMware vSphere clusters...")

for site in sites:
    print(f"\n{site}:")

    # Compute Cluster (Server Hall A)
    print("  - Compute Cluster")
    clusters.append({
        'name': f'{site}-COMPUTE-CLUSTER',
        'type': 'VMware vSphere',
        'group': 'Production',
        'site': site,
        'description': f'Production compute cluster - Server Hall A (6 ESXi hosts)',
        'comments': f'Hosts: {site}-ESX-A01 through {site}-ESX-A06'
    })

    # Storage/vSAN Cluster (Server Hall B)
    print("  - Storage Cluster")
    clusters.append({
        'name': f'{site}-STORAGE-CLUSTER',
        'type': 'VMware vSphere',
        'group': 'Production',
        'site': site,
        'description': f'vSAN storage cluster - Server Hall B (4 ESXi hosts)',
        'comments': f'Hosts: {site}-ESX-B01 through {site}-ESX-B04. vSAN enabled for storage.'
    })

    # Management Cluster (Server Hall A)
    print("  - Management Cluster")
    clusters.append({
        'name': f'{site}-MGMT-CLUSTER',
        'type': 'VMware vSphere',
        'group': 'Management',
        'site': site,
        'description': f'Management cluster - vCenter, NSX, monitoring (3 ESXi hosts)',
        'comments': f'Hosts: {site}-ESX-MGT01 through {site}-ESX-MGT03. Runs vCenter, NSX Manager, vROps.'
    })

print(f"\n✅ Generated {len(cluster_types)} cluster type")
print(f"✅ Generated {len(cluster_groups)} cluster groups")
print(f"✅ Generated {len(clusters)} clusters")
print(f"   - 3 ONPREM sites × 3 clusters = 9 clusters total")
print(f"   - Per site: 1 Compute + 1 Storage + 1 Management")
print(f"   - CLOUD sites use managed cloud services (no vSphere clusters)")

# Write cluster types CSV
cluster_types_file = 'lab/virtualization/netbox_cluster_types.csv'
with open(cluster_types_file, 'w', newline='') as f:
    fieldnames = ['name', 'slug', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cluster_types)

print(f"✅ Cluster types written to {cluster_types_file}")

# Write cluster groups CSV
cluster_groups_file = 'lab/virtualization/netbox_cluster_groups.csv'
with open(cluster_groups_file, 'w', newline='') as f:
    fieldnames = ['name', 'slug', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cluster_groups)

print(f"✅ Cluster groups written to {cluster_groups_file}")

# Write clusters CSV
clusters_file = 'lab/virtualization/netbox_vmware_clusters.csv'
with open(clusters_file, 'w', newline='') as f:
    fieldnames = ['name', 'type', 'group', 'site', 'description', 'comments']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(clusters)

print(f"✅ Clusters written to {clusters_file}")
