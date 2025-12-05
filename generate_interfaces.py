#!/usr/bin/env python3
"""
Generate interfaces CSV for all devices based on device type
"""
import csv
from pathlib import Path

# Interface templates by device type
# Format: device_type -> [(interface_name_template, count, type, speed_kbps)]
interface_templates = {
    'Nexus 9508': [
        ('Ethernet1/{port}', 48, '10gbase-x-sfpp', 10000000),
        ('Ethernet2/{port}', 6, '40gbase-x-qsfpp', 40000000),
    ],
    'Nexus 93180YC-FX': [
        ('Ethernet1/{port}', 48, '25gbase-x-sfp28', 25000000),
    ],
    'PA-5450': [
        ('ethernet1/{port}', 16, '10gbase-x-sfpp', 10000000),
    ],
    'PA-3260': [
        ('ethernet1/{port}', 12, '10gbase-x-sfpp', 10000000),
    ],
    'ASR 9001': [
        ('TenGigE0/0/0/{port}', 10, '10gbase-x-sfpp', 10000000),
    ],
    'BIG-IP i10800': [
        ('1.{port}', 8, '10gbase-x-sfpp', 10000000),
    ],
    'DCS-7280SR-48C6': [
        ('Ethernet{port}', 48, '10gbase-x-sfpp', 10000000),
        ('Ethernet{port}', 6, '100gbase-x-qsfp28', 100000000),
    ],
    'DCS-7050SX3-48YC12': [
        ('Ethernet{port}', 48, '10gbase-x-sfpp', 10000000),
        ('Ethernet{port}', 12, '25gbase-x-sfp28', 25000000),
    ],
    'PowerEdge R750': [
        ('eno{port}', 4, '25gbase-x-sfp28', 25000000),
    ],
    'ProLiant DL380 Gen10': [
        ('eno{port}', 4, '25gbase-x-sfp28', 25000000),
    ],
    'Catalyst 9300-48P': [
        ('GigabitEthernet1/0/{port}', 48, '1000base-t', 1000000),
    ],
    'PowerStore 9200T': [
        ('eth{port}', 4, '25gbase-x-sfp28', 25000000),
    ],
    'PowerScale F600': [
        ('ext-{port}', 4, '25gbase-x-sfp28', 25000000),
    ],
    'ISR 4431': [
        ('GigabitEthernet0/{port}', 4, '1000base-t', 1000000),
    ],
}

# Read devices
devices_file = 'lab/devices/netbox_dc_devices.csv'
interfaces_file = 'lab/netbox_dc_interfaces.csv'

interfaces = []

print("Generating interfaces for all devices...")

with open(devices_file, 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        device_name = row['name']
        device_type = row['device_type']

        if device_type not in interface_templates:
            print(f"  ⚠️  Warning: No interface template for device type '{device_type}'")
            continue

        # Generate interfaces for this device
        for template_name, count, iface_type, speed in interface_templates[device_type]:
            # Handle different port numbering
            if 'DCS-7280SR' in device_type:
                # Arista DCS-7280SR: Ethernet1-48 (10G), Ethernet49-54 (100G)
                if 'Ethernet{port}' in template_name and '10gbase' in iface_type:
                    start_port = 1
                else:  # 100G ports
                    start_port = 49
            elif 'DCS-7050SX3' in device_type:
                # Arista DCS-7050SX3: Ethernet1-48 (10G), Ethernet49-60 (25G)
                if 'Ethernet{port}' in template_name and '10gbase' in iface_type:
                    start_port = 1
                else:  # 25G uplink ports
                    start_port = 49
            else:
                start_port = 1

            for port_num in range(count):
                port = start_port + port_num
                iface_name = template_name.format(port=port)

                interfaces.append({
                    'device': device_name,
                    'name': iface_name,
                    'type': iface_type,
                    'speed': speed,
                    'enabled': 'true',
                    'description': f'{iface_type.upper()} Interface'
                })

print(f"Generated {len(interfaces)} interfaces for {len(set([i['device'] for i in interfaces]))} devices")

# Write interfaces CSV
with open(interfaces_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'speed', 'enabled', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(interfaces)

print(f"✅ Interfaces written to {interfaces_file}")
