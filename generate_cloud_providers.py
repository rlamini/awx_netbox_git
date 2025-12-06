#!/usr/bin/env python3
"""
Generate circuit providers for cloud interconnection.
"""

import csv

providers = []

print("Generating circuit providers for cloud interconnection...")

# Cloud providers
providers.append({
    'name': 'Microsoft Azure',
    'slug': 'microsoft-azure',
    'asn': '12076',
    'description': 'Microsoft Azure ExpressRoute'
})

providers.append({
    'name': 'Google Cloud Platform',
    'slug': 'google-cloud-platform',
    'asn': '15169',
    'description': 'Google Cloud Platform'
})

providers.append({
    'name': 'Amazon Web Services',
    'slug': 'amazon-web-services',
    'asn': '16509',
    'description': 'Amazon Web Services Direct Connect'
})

# Interconnection providers
providers.append({
    'name': 'Equinix',
    'slug': 'equinix',
    'asn': '24115',
    'description': 'Equinix - Global Interconnection Platform'
})

providers.append({
    'name': 'Megaport',
    'slug': 'megaport',
    'asn': '133937',
    'description': 'Megaport - Network as a Service'
})

print(f"✅ Generated {len(providers)} circuit providers")
print(f"   - Cloud Providers: Microsoft Azure, Google Cloud, AWS")
print(f"   - Interconnection: Equinix, Megaport")

# Write providers CSV
providers_file = 'lab/circuits/netbox_cloud_providers.csv'
with open(providers_file, 'w', newline='') as f:
    fieldnames = ['name', 'slug', 'asn', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(providers)

print(f"✅ Providers written to {providers_file}")
