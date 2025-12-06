#!/usr/bin/env python3
"""
Generate Config Contexts for NetBox
Creates hierarchical config contexts for EMEA-DC-ONPREM Cisco devices

This script creates config contexts with proper weight and assignments:
- Global contexts (weight 1000)
- Platform contexts (weight 2000)
- Site contexts (weight 3000)
- Role contexts (weight 4000)

Usage:
    python3 generate_config_contexts.py
"""

import json
import os
import csv


def load_json_file(filepath):
    """Load JSON data from file"""
    with open(filepath, 'r') as f:
        return json.load(f)


def generate_config_contexts():
    """
    Generate config contexts CSV file for NetBox import

    Config Context fields:
    - name: Context name
    - weight: Priority (higher = more specific)
    - description: Context description
    - is_active: Boolean (True/False)
    - data: JSON data (escaped)
    - sites: Comma-separated site names (optional)
    - roles: Comma-separated role names (optional)
    - platforms: Comma-separated platform names (optional)
    - device_types: Comma-separated device type slugs (optional)
    """

    contexts = []
    base_path = 'lab/config-contexts'

    # ========================================
    # 1. GLOBAL CONTEXT (Weight: 1000)
    # ========================================
    global_data = load_json_file(f'{base_path}/global_context.json')
    contexts.append({
        'name': 'Global Configuration',
        'weight': 1000,
        'description': 'Global settings applied to all devices',
        'is_active': True,
        'data': json.dumps(global_data),
        'sites': '',
        'roles': '',
        'platforms': '',
        'device_types': ''
    })

    # ========================================
    # 2. PLATFORM CONTEXTS (Weight: 2000)
    # ========================================
    platform_contexts = [
        {
            'file': 'platform_nxos_context.json',
            'name': 'Cisco NX-OS Platform',
            'platform': 'NX-OS',
            'description': 'Cisco NX-OS platform defaults (Nexus switches)'
        },
        {
            'file': 'platform_iosxe_context.json',
            'name': 'Cisco IOS-XE Platform',
            'platform': 'IOS-XE',
            'description': 'Cisco IOS-XE platform defaults (Catalyst switches)'
        },
        {
            'file': 'platform_iosxr_context.json',
            'name': 'Cisco IOS-XR Platform',
            'platform': 'IOS-XR',
            'description': 'Cisco IOS-XR platform defaults (ASR routers)'
        },
        {
            'file': 'platform_ios_context.json',
            'name': 'Cisco IOS Platform',
            'platform': 'IOS',
            'description': 'Cisco IOS platform defaults (ISR routers)'
        }
    ]

    for platform_ctx in platform_contexts:
        platform_data = load_json_file(f'{base_path}/{platform_ctx["file"]}')
        contexts.append({
            'name': platform_ctx['name'],
            'weight': 2000,
            'description': platform_ctx['description'],
            'is_active': True,
            'data': json.dumps(platform_data),
            'sites': '',
            'roles': '',
            'platforms': platform_ctx['platform'],
            'device_types': ''
        })

    # ========================================
    # 3. SITE CONTEXT (Weight: 3000)
    # ========================================
    site_data = load_json_file(f'{base_path}/emea_dc_onprem_context.json')
    contexts.append({
        'name': 'EMEA-DC-ONPREM Site',
        'weight': 3000,
        'description': 'EMEA DC ONPREM site-specific configuration',
        'is_active': True,
        'data': json.dumps(site_data),
        'sites': 'EMEA-DC-ONPREM',
        'roles': '',
        'platforms': '',
        'device_types': ''
    })

    # ========================================
    # 4. ROLE CONTEXTS (Weight: 4000)
    # ========================================
    role_contexts = [
        {
            'file': 'role_core_switch_context.json',
            'name': 'Core Switch Role',
            'role': 'Core Switch',
            'description': 'Core switch role configuration'
        },
        {
            'file': 'role_distribution_switch_context.json',
            'name': 'Distribution Switch Role',
            'role': 'Distribution Switch',
            'description': 'Distribution switch role configuration'
        },
        {
            'file': 'role_access_switch_context.json',
            'name': 'Access Switch Role',
            'role': 'Access Switch',
            'description': 'Access switch role configuration'
        },
        {
            'file': 'role_router_context.json',
            'name': 'Router Role',
            'role': 'Router',
            'description': 'Router role configuration (edge routers)'
        },
        {
            'file': 'role_oob_router_context.json',
            'name': 'OOB Router Role',
            'role': 'OOB Router',
            'description': 'Out-of-band management router configuration'
        }
    ]

    for role_ctx in role_contexts:
        role_data = load_json_file(f'{base_path}/{role_ctx["file"]}')
        contexts.append({
            'name': role_ctx['name'],
            'weight': 4000,
            'description': role_ctx['description'],
            'is_active': True,
            'data': json.dumps(role_data),
            'sites': '',
            'roles': role_ctx['role'],
            'platforms': '',
            'device_types': ''
        })

    # ========================================
    # WRITE CSV FILE
    # ========================================
    output_file = 'lab/config-contexts/netbox_config_contexts.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'weight', 'description', 'is_active', 'data',
                      'sites', 'roles', 'platforms', 'device_types']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(contexts)

    print(f'✅ Generated {len(contexts)} config contexts')
    print(f'📄 Output file: {output_file}')
    print()
    print('Config Contexts Summary:')
    print('-' * 60)
    for ctx in contexts:
        print(f'  {ctx["name"]:40} (weight: {ctx["weight"]})')
    print()
    print('Next Steps:')
    print('1. Review the generated CSV file')
    print('2. Import to NetBox via UI: Customization → Config Contexts → Import')
    print('3. Or use NetBox API to create contexts programmatically')
    print()


def generate_readme():
    """Generate README for config contexts"""
    readme_content = """# NetBox Config Contexts

This directory contains hierarchical config contexts for network devices.

## Context Hierarchy (by weight/priority)

1. **Global Context** (weight: 1000) - Applied to all devices
2. **Platform Contexts** (weight: 2000) - Applied by platform (NX-OS, IOS-XE, IOS-XR, IOS)
3. **Site Context** (weight: 3000) - Applied by site (EMEA-DC-ONPREM)
4. **Role Contexts** (weight: 4000) - Applied by device role

## Files

### JSON Context Files
- `global_context.json` - Global configuration (logging, AAA, etc.)
- `emea_dc_onprem_context.json` - EMEA DC ONPREM site configuration
- `platform_nxos_context.json` - Cisco NX-OS platform defaults
- `platform_iosxe_context.json` - Cisco IOS-XE platform defaults
- `platform_iosxr_context.json` - Cisco IOS-XR platform defaults
- `platform_ios_context.json` - Cisco IOS platform defaults
- `role_core_switch_context.json` - Core switch role configuration
- `role_distribution_switch_context.json` - Distribution switch configuration
- `role_access_switch_context.json` - Access switch configuration
- `role_router_context.json` - Router configuration
- `role_oob_router_context.json` - OOB router configuration

### Generated Files
- `netbox_config_contexts.csv` - CSV export for NetBox import

## Import to NetBox

### Method 1: CSV Import (UI)
1. Navigate to **Customization → Config Contexts**
2. Click **Import**
3. Upload `netbox_config_contexts.csv`
4. Map fields and import

### Method 2: Manual Creation (UI)
1. Navigate to **Customization → Config Contexts**
2. Click **Add**
3. Copy JSON from files above
4. Set weight and assignments
5. Save

### Method 3: API (Recommended for automation)
See parent directory's `generate_config_contexts.py` script

## Testing Context Merge

To test how contexts merge for a specific device:

1. Go to device page (e.g., EMEA-DC-ONPREM-CORE-SW01)
2. Click **Config Context** tab
3. View merged JSON data

Example merged context for **EMEA-DC-ONPREM-CORE-SW01**:
- Global context (base settings)
- + NX-OS platform context (features, VTP, spanning-tree)
- + EMEA-DC-ONPREM site context (NTP, DNS, SNMP)
- + Core Switch role context (HSRP, routing, VLANs)
- = Final merged context

## Modifying Contexts

1. Edit the JSON files in this directory
2. Regenerate CSV: `python3 ../generate_config_contexts.py`
3. Re-import to NetBox or update via API

## Version Control

All context files are tracked in Git. When making changes:
1. Edit JSON files
2. Test in NetBox
3. Commit changes with descriptive message
"""

    with open('lab/config-contexts/README.md', 'w') as f:
        f.write(readme_content)

    print('✅ Generated README.md for config contexts')


if __name__ == '__main__':
    print('=' * 60)
    print('NetBox Config Context Generator')
    print('=' * 60)
    print()

    generate_config_contexts()
    generate_readme()

    print('Done! ✨')
