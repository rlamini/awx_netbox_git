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

# Device types with PSU count and power draw (watts)
device_power_config = {
    # Network devices (dual PSU) - device_type: (psu_count, max_watts_per_psu)
    'Nexus 9508': (2, 3000),  # Chassis switch, high power
    'Nexus 93180YC-FX': (2, 750),  # ToR switch
    'DCS-7280SR-48C6': (2, 800),  # Spine switch
    'DCS-7050SX3-48YC12': (2, 600),  # Leaf switch
    'ASR 9001': (2, 1500),  # Edge router
    'PA-5450': (2, 2500),  # High-end firewall
    'PA-3260': (2, 1200),  # Mid-range firewall
    'BIG-IP i10800': (2, 2000),  # Load balancer

    # Servers (dual PSU)
    'PowerEdge R750': (2, 1400),  # 2U server
    'PowerEdge R740': (2, 1100),  # 2U server
    'ProLiant DL380 Gen10': (2, 1600),  # 2U server
    'ProLiant DL360 Gen10': (2, 800),  # 1U server

    # Storage (dual PSU)
    'Pure FlashArray X70': (2, 2000),  # Storage array
    'NetApp AFF A400': (2, 1800),  # Storage array

    # Small devices (single PSU)
    'ICX7150-48P': (1, 370),  # Access switch
    'ISR 4331': (1, 250),  # Small router
}

for device in devices:
    device_name = device['name']
    device_type = device['device_type']

    # Skip patch panels (they don't have power)
    if 'Patch Panel' in device_type or device['role'] == 'Patch Panel':
        continue

    # Get power configuration (default to dual PSU, 1000W)
    num_psus, max_watts = device_power_config.get(device_type, (2, 1000))

    for psu_num in range(1, num_psus + 1):
        power_ports.append({
            'device': device_name,
            'name': f'PSU{psu_num}',
            'type': 'iec-60320-c14',  # Standard C14 power inlet
            'maximum_draw': max_watts,  # Maximum power draw in watts
            'allocated_draw': int(max_watts * 0.7),  # Allocated = 70% of max (typical usage)
            'description': f'Power supply {psu_num}'
        })

print(f"✅ Generated {len(power_ports)} power ports with power draw values")

# Calculate total power
total_max_power = sum([p['maximum_draw'] for p in power_ports])
total_allocated_power = sum([p['allocated_draw'] for p in power_ports])

print(f"   - Total maximum power draw: {total_max_power:,}W ({total_max_power/1000:.1f}kW)")
print(f"   - Total allocated power draw: {total_allocated_power:,}W ({total_allocated_power/1000:.1f}kW)")

# Write power ports CSV
ports_file = 'lab/netbox_dc_power_ports.csv'
with open(ports_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'maximum_draw', 'allocated_draw', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(power_ports)

print(f"✅ Power ports written to {ports_file}")
