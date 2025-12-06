#!/usr/bin/env python3
"""
Generate ISP providers for agency circuits.
Each agency has:
- 1× ADSL circuit (primary)
- 1× 5G circuit (backup)
"""

import csv

providers = []

print("Generating ISP providers for agencies...")

# EMEA ISP Providers
providers.extend([
    {
        'name': 'Orange Business Services',
        'slug': 'orange-business',
        'asn': '5511',
        'description': 'Orange Business Services - EMEA ADSL/Fiber provider'
    },
    {
        'name': 'BT Business',
        'slug': 'bt-business',
        'asn': '2856',
        'description': 'BT Business - UK/EMEA ADSL/Fiber provider'
    },
    {
        'name': 'Deutsche Telekom',
        'slug': 'deutsche-telekom',
        'asn': '3320',
        'description': 'Deutsche Telekom - Germany ADSL/Fiber provider'
    },
    {
        'name': 'Vodafone Business',
        'slug': 'vodafone-business',
        'asn': '1273',
        'description': 'Vodafone Business - EMEA 5G backup provider'
    }
])

# APAC ISP Providers
providers.extend([
    {
        'name': 'Singtel',
        'slug': 'singtel',
        'asn': '7473',
        'description': 'Singapore Telecommunications - APAC ADSL/Fiber provider'
    },
    {
        'name': 'Telstra Business',
        'slug': 'telstra-business',
        'asn': '1221',
        'description': 'Telstra Business - Australia/APAC ADSL/Fiber provider'
    },
    {
        'name': 'NTT Communications',
        'slug': 'ntt-communications',
        'asn': '2914',
        'description': 'NTT Communications - Japan/APAC provider'
    },
    {
        'name': '3 Business',
        'slug': '3-business',
        'asn': '25135',
        'description': '3 Business - APAC 5G backup provider'
    }
])

# AMER ISP Providers
providers.extend([
    {
        'name': 'Verizon Business',
        'slug': 'verizon-business',
        'asn': '701',
        'description': 'Verizon Business - AMER ADSL/Fiber provider'
    },
    {
        'name': 'AT&T Business',
        'slug': 'att-business',
        'asn': '7018',
        'description': 'AT&T Business - AMER ADSL/Fiber provider'
    },
    {
        'name': 'CenturyLink',
        'slug': 'centurylink',
        'asn': '209',
        'description': 'CenturyLink/Lumen - AMER DSL/Fiber provider'
    },
    {
        'name': 'T-Mobile Business',
        'slug': 't-mobile-business',
        'asn': '21928',
        'description': 'T-Mobile Business - AMER 5G backup provider'
    }
])

print(f"✅ Generated {len(providers)} ISP providers")
print(f"   - EMEA: 4 providers (Orange, BT, Deutsche Telekom, Vodafone)")
print(f"   - APAC: 4 providers (Singtel, Telstra, NTT, 3)")
print(f"   - AMER: 4 providers (Verizon, AT&T, CenturyLink, T-Mobile)")

# Write providers CSV
providers_file = 'lab/agencies/netbox_agency_isp_providers.csv'
with open(providers_file, 'w', newline='') as f:
    fieldnames = ['name', 'slug', 'asn', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(providers)

print(f"✅ ISP providers written to {providers_file}")
