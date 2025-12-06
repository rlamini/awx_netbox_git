#!/usr/bin/env python3
"""
Generate Config Templates for NetBox
Creates configuration templates for Cisco platforms

This script documents the config templates available for NetBox.
Templates are stored as .j2 (Jinja2) files and must be imported via NetBox UI or API.

Usage:
    python3 generate_config_templates.py
"""

import os
import csv


def generate_template_inventory():
    """
    Generate inventory of config templates with metadata

    Config Template fields (for reference):
    - name: Template name
    - description: Template description
    - platform: Platform slug (nxos, ios-xe, ios-xr, ios)
    - template_code: Jinja2 template content
    """

    templates = []
    base_path = 'lab/config-templates'

    # ========================================
    # CISCO TEMPLATES
    # ========================================
    cisco_templates = [
        {
            'name': 'Cisco NX-OS Base Configuration',
            'file': 'cisco_nxos_base.j2',
            'platform': 'NX-OS',
            'description': 'Base configuration template for Cisco Nexus switches (NX-OS)',
            'compatible_devices': 'Nexus 9508, Nexus 93180YC-FX, Nexus 9000 series',
            'features': [
                'Global settings (hostname, timezone)',
                'Feature activation',
                'VTP configuration',
                'Spanning tree (rapid-pvst)',
                'VLAN configuration',
                'Management interface',
                'NTP, DNS, SNMP',
                'Syslog logging',
                'TACACS+ AAA',
                'OSPF/BGP routing',
                'HSRP (for core/distribution)',
                'SSH management access',
                'Banner'
            ]
        },
        {
            'name': 'Cisco IOS-XE Base Configuration',
            'file': 'cisco_iosxe_base.j2',
            'platform': 'IOS-XE',
            'description': 'Base configuration template for Cisco Catalyst switches (IOS-XE)',
            'compatible_devices': 'Catalyst 9300-48P, Catalyst 9000, 3850, 3650 series',
            'features': [
                'Service timestamps and encryption',
                'Global settings',
                'VTP transparent mode',
                'Spanning tree (rapid-pvst, portfast, bpduguard)',
                'VLAN configuration (management, data, voice)',
                'Interface templates',
                'NTP, DNS, SNMP',
                'Syslog logging',
                'TACACS+ AAA',
                'SSH management access',
                'PoE configuration (access switches)',
                'Banner'
            ]
        },
        {
            'name': 'Cisco IOS-XR Base Configuration',
            'file': 'cisco_iosxr_base.j2',
            'platform': 'IOS-XR',
            'description': 'Base configuration template for Cisco ASR routers (IOS-XR)',
            'compatible_devices': 'ASR 9001, ASR 9000, NCS series',
            'features': [
                'Global settings (hostname, timezone)',
                'Management and loopback interfaces',
                'NTP, DNS, SNMP',
                'Syslog logging',
                'TACACS+ AAA',
                'OSPF/BGP routing',
                'NETCONF (optional)',
                'SSH management access',
                'Banner'
            ]
        },
        {
            'name': 'Cisco IOS Base Configuration',
            'file': 'cisco_ios_base.j2',
            'platform': 'IOS',
            'description': 'Base configuration template for Cisco ISR routers (IOS)',
            'compatible_devices': 'ISR 4431, ISR 4000, 2900, 1900 series',
            'features': [
                'Service timestamps and encryption',
                'Global settings',
                'Management and loopback interfaces',
                'NTP, DNS, SNMP',
                'Syslog logging',
                'TACACS+ AAA',
                'SSH management access',
                'Console and VTY line configuration',
                'Banner'
            ]
        }
    ]

    for template in cisco_templates:
        templates.append(template)

    # ========================================
    # WRITE TEMPLATE INVENTORY CSV
    # ========================================
    output_file = 'lab/config-templates/template_inventory.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['name', 'file', 'platform', 'description', 'compatible_devices', 'features']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for template in templates:
            writer.writerow({
                'name': template['name'],
                'file': template['file'],
                'platform': template['platform'],
                'description': template['description'],
                'compatible_devices': template['compatible_devices'],
                'features': '; '.join(template['features'])
            })

    print(f'✅ Generated template inventory for {len(templates)} templates')
    print(f'📄 Output file: {output_file}')
    print()
    print('Config Templates Summary:')
    print('-' * 60)
    for template in templates:
        print(f'  {template["name"]:45} ({template["file"]})')
        print(f'    Platform: {template["platform"]}')
        print(f'    Devices: {template["compatible_devices"]}')
        print()

    return templates


def generate_readme(templates):
    """Generate README for config templates"""
    readme_content = """# NetBox Config Templates

This directory contains Jinja2 configuration templates for network devices.

## Templates Overview

"""

    for template in templates:
        readme_content += f"""### {template['name']}

**File**: `{template['file']}`
**Platform**: {template['platform']}
**Description**: {template['description']}

**Compatible Devices**: {template['compatible_devices']}

**Features**:
"""
        for feature in template['features']:
            readme_content += f"- {feature}\n"
        readme_content += "\n"

    readme_content += """## Import to NetBox

Config templates cannot be imported via CSV. Use one of these methods:

### Method 1: NetBox UI (Manual)

1. Navigate to **Customization → Config Templates**
2. Click **Add**
3. Fill in the form:
   - **Name**: Template name (e.g., "Cisco NX-OS Base Configuration")
   - **Description**: Template description
   - **Platform**: Select platform (NX-OS, IOS-XE, IOS-XR, IOS)
4. Copy template content from `.j2` file
5. Paste into **Template Code** field
6. Save

### Method 2: NetBox API (Recommended for automation)

```python
import requests

NETBOX_URL = "https://netbox.example.com"
TOKEN = "your-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Read template file
with open('lab/config-templates/cisco_nxos_base.j2', 'r') as f:
    template_code = f.read()

# Get platform ID
platform_response = requests.get(
    f"{NETBOX_URL}/api/dcim/platforms/?slug=nxos",
    headers=headers
)
platform_id = platform_response.json()['results'][0]['id']

# Create config template
data = {
    "name": "Cisco NX-OS Base Configuration",
    "description": "Base configuration for Nexus switches",
    "platform": platform_id,
    "template_code": template_code
}

response = requests.post(
    f"{NETBOX_URL}/api/extras/config-templates/",
    headers=headers,
    json=data
)

print(response.json())
```

## Using Templates

### Render Configuration for a Device

**Via NetBox UI**:
1. Go to device page (e.g., EMEA-DC-ONPREM-CORE-SW01)
2. Click **Config** tab
3. Select template from dropdown
4. Click **Render**
5. View rendered configuration

**Via API**:
```python
import requests

NETBOX_URL = "https://netbox.example.com"
TOKEN = "your-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get device ID
device_response = requests.get(
    f"{NETBOX_URL}/api/dcim/devices/?name=EMEA-DC-ONPREM-CORE-SW01",
    headers=headers
)
device_id = device_response.json()['results'][0]['id']

# Render configuration
response = requests.get(
    f"{NETBOX_URL}/api/dcim/devices/{device_id}/render-config/",
    headers=headers
)

config = response.json()
print(config['content'])
```

## Template Variables

Templates use variables from **Config Contexts** and **Device Attributes**.

### Config Context Variables

Access merged config context data:
```jinja2
{{ site.timezone }}          {# From site context #}
{{ ntp.servers }}            {# From site/global context #}
{{ platform.os }}            {# From platform context #}
{{ role.tier }}              {# From role context #}
{{ vlans.management }}       {# From role/site context #}
```

### Device Attribute Variables

Access NetBox device object:
```jinja2
{{ device.name }}                    {# Device hostname #}
{{ device.site.name }}               {# Site name #}
{{ device.role.name }}               {# Device role #}
{{ device.device_type.model }}       {# Device model #}
{{ device.primary_ip4.address }}     {# Management IP #}
{{ device.primary_ip4.address.ip }}  {# IP without mask #}
```

### Conditional Logic

```jinja2
{% if role.tier == 'core' %}
spanning-tree pathcost method long
{% endif %}

{% if features.required is defined %}
{% for feature in features.required %}
feature {{ feature }}
{% endfor %}
{% endif %}
```

### Loops

```jinja2
{% for server in ntp.servers %}
ntp server {{ server }}
{% endfor %}

{% for vlan_id in vlans.server_vlans %}
vlan {{ vlan_id }}
  name SERVER-VLAN-{{ vlan_id }}
{% endfor %}
```

## Testing Templates

### Test Locally with Jinja2

```python
from jinja2 import Template

# Load template
with open('lab/config-templates/cisco_nxos_base.j2', 'r') as f:
    template = Template(f.read())

# Load context
context = {
    'device': {
        'name': 'EMEA-DC-ONPREM-CORE-SW01',
        'site': {'name': 'EMEA-DC-ONPREM'},
        'role': {'name': 'Core Switch'}
    },
    'site': {'timezone': 'Europe/Paris'},
    'ntp': {'servers': ['10.10.1.1', '10.10.1.2']},
    # ... more context data
}

# Render
rendered = template.render(**context)
print(rendered)
```

## Modifying Templates

1. Edit `.j2` files in this directory
2. Test rendering locally or in NetBox
3. Update in NetBox via UI or API
4. Commit changes to Git

## Best Practices

1. **Keep templates modular**: Use includes/macros for reusable blocks
2. **Use comments**: Document complex logic with `{# comments #}`
3. **Validate syntax**: Test with sample data before deploying
4. **Version control**: Track all changes in Git
5. **Test rendering**: Always test on non-production devices first
6. **Document variables**: List all required context variables
7. **Handle missing data**: Use defaults and conditionals

Example:
```jinja2
{# Use default if variable is missing #}
spanning-tree priority {{ spanning_tree.priority|default(32768) }}

{# Check if variable exists before using #}
{% if hsrp is defined %}
feature hsrp
{% endif %}
```

## File Structure

```
lab/config-templates/
├── README.md                    # This file
├── template_inventory.csv       # Template metadata
├── cisco_nxos_base.j2          # Cisco NX-OS template
├── cisco_iosxe_base.j2         # Cisco IOS-XE template
├── cisco_iosxr_base.j2         # Cisco IOS-XR template
└── cisco_ios_base.j2           # Cisco IOS template
```

## Next Steps

1. Import templates to NetBox (UI or API)
2. Create platforms in NetBox if they don't exist:
   - NX-OS (slug: nxos)
   - IOS-XE (slug: ios-xe)
   - IOS-XR (slug: ios-xr)
   - IOS (slug: ios)
3. Assign platforms to device types
4. Assign templates to platforms
5. Test rendering on sample devices
6. Deploy to production devices via automation (Ansible/AWX)
"""

    with open('lab/config-templates/README.md', 'w') as f:
        f.write(readme_content)

    print('✅ Generated README.md for config templates')


def verify_template_files():
    """Verify all template files exist"""
    base_path = 'lab/config-templates'
    template_files = [
        'cisco_nxos_base.j2',
        'cisco_iosxe_base.j2',
        'cisco_iosxr_base.j2',
        'cisco_ios_base.j2'
    ]

    print()
    print('Template Files Verification:')
    print('-' * 60)

    all_exist = True
    for template_file in template_files:
        filepath = f'{base_path}/{template_file}'
        exists = os.path.exists(filepath)
        status = '✅' if exists else '❌'
        print(f'{status} {template_file:30} {"EXISTS" if exists else "MISSING"}')
        if not exists:
            all_exist = False

    print()
    if all_exist:
        print('✅ All template files verified')
    else:
        print('❌ Some template files are missing')

    return all_exist


if __name__ == '__main__':
    print('=' * 60)
    print('NetBox Config Template Generator')
    print('=' * 60)
    print()

    # Verify template files exist
    verify_template_files()

    # Generate inventory
    templates = generate_template_inventory()

    # Generate README
    generate_readme(templates)

    print()
    print('Next Steps:')
    print('1. Review template files in lab/config-templates/')
    print('2. Import templates to NetBox via UI or API')
    print('3. Ensure platforms exist in NetBox (NX-OS, IOS-XE, IOS-XR, IOS)')
    print('4. Assign templates to platforms')
    print('5. Test rendering on devices')
    print()
    print('Done! ✨')
