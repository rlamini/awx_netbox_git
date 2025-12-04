#!/usr/bin/env python3
"""
Generate power ports for all datacenter devices.
Most devices have dual power supplies (PSU1, PSU2).
"""

import csv

# Read devices list
devices = []
with open('lab/netbox_dc_devices.csv', 'r') as f:
    reader = csv.DictReader(f)
    devices = [row for row in reader]

power_ports = []

print(f"Generating power ports for {len(devices)} devices...")

# Device types and their power port configurations
device_power_config = {
    # Network devices (dual PSU)
    'Nexus 9508': 2,
    'Nexus 93180YC-FX': 2,
    'DCS-7280SR-48C6': 2,
    'DCS-7050SX3-48YC12': 2,
    'ASR 9001': 2,
    'PA-5450': 2,
    'PA-3260': 2,
    'BIG-IP i10800': 2,

    # Servers (dual PSU)
    'PowerEdge R750': 2,
    'PowerEdge R740': 2,
    'ProLiant DL380 Gen10': 2,
    'ProLiant DL360 Gen10': 2,

    # Storage (dual PSU)
    'Pure FlashArray X70': 2,
    'NetApp AFF A400': 2,

    # Small devices (single PSU)
    'ICX7150-48P': 1,
    'ISR 4331': 1,
}

for device in devices:
    device_name = device['name']
    device_type = device['device_type']

    # Determine number of power supplies (default to 2 for enterprise equipment)
    num_psus = device_power_config.get(device_type, 2)

    # Skip patch panels (they don't have power)
    if 'Patch Panel' in device_type or device['role'] == 'Patch Panel':
        continue

    for psu_num in range(1, num_psus + 1):
        power_ports.append({
            'device': device_name,
            'name': f'PSU{psu_num}',
            'type': 'iec-60320-c14',  # Standard C14 power inlet
            'maximum_draw': '',  # Leave empty for now
            'allocated_draw': '',
            'description': f'Power supply {psu_num}'
        })

print(f"✅ Generated {len(power_ports)} power ports")
print(f"   - Dual PSU devices: {len([d for d in devices if device_power_config.get(d['device_type'], 2) == 2])}")
print(f"   - Single PSU devices: {len([d for d in devices if device_power_config.get(d['device_type'], 2) == 1])}")

# Write power ports CSV
ports_file = 'lab/netbox_dc_power_ports.csv'
with open(ports_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'maximum_draw', 'allocated_draw', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_ports)

print(f"✅ Power ports written to {ports_file}")
