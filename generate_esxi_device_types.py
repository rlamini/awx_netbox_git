#!/usr/bin/env python3
"""
Generate ESXi host device types for virtualization infrastructure.
"""

import csv

device_types = []

# ESXi Host Device Types
# Dell PowerEdge R750 - High-performance compute host
device_types.append({
    'manufacturer': 'Dell',
    'model': 'PowerEdge R750',
    'slug': 'dell-poweredge-r750',
    'u_height': 2,
    'is_full_depth': True,
    'description': 'Dell PowerEdge R750 - 2U Rack Server for ESXi (Dual CPU, up to 4TB RAM)'
})

# Dell PowerEdge R650 - Standard compute host
device_types.append({
    'manufacturer': 'Dell',
    'model': 'PowerEdge R650',
    'slug': 'dell-poweredge-r650',
    'u_height': 1,
    'is_full_depth': True,
    'description': 'Dell PowerEdge R650 - 1U Rack Server for ESXi (Dual CPU, up to 2TB RAM)'
})

# Cisco UCS C240 M6 - Management cluster
device_types.append({
    'manufacturer': 'Cisco',
    'model': 'UCS C240 M6',
    'slug': 'cisco-ucs-c240-m6',
    'u_height': 2,
    'is_full_depth': True,
    'description': 'Cisco UCS C240 M6 - 2U Rack Server for ESXi Management'
})

print(f"✅ Generated {len(device_types)} ESXi host device types")

# Write device types CSV
device_types_file = 'lab/virtualization/netbox_esxi_device_types.csv'
with open(device_types_file, 'w', newline='') as f:
    fieldnames = ['manufacturer', 'model', 'slug', 'u_height', 'is_full_depth', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(device_types)

print(f"✅ ESXi device types written to {device_types_file}")
