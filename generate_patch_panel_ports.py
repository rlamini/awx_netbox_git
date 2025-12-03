#!/usr/bin/env python3
"""
Generate front ports and rear ports for patch panels (proper NetBox structured cabling)
"""
import csv
from pathlib import Path

# Site prefixes for the 6 DCs
sites = [
    'EMEA-DC-CLOUD',
    'EMEA-DC-ONPREM',
    'APAC-DC-CLOUD',
    'APAC-DC-ONPREM',
    'AMER-DC-CLOUD',
    'AMER-DC-ONPREM'
]

rear_ports = []
front_ports = []

print("Generating front and rear ports for all patch panels...")

for site in sites:
    print(f"\n{site}:")

    # Network Core Racks - 48-port Fiber Patch Panels
    print("  - Network Core racks: 48-port fiber patch panels")
    for rack_num in range(1, 5):
        pp_name = f'{site}-NET-R0{rack_num}-FPP01'

        for port in range(1, 49):
            # Rear port (permanent cabling side)
            rear_ports.append({
                'device': pp_name,
                'name': f'Rear-{port}',
                'type': 'lc',
                'positions': '1',
                'description': f'Rear port {port}'
            })

            # Front port (patch cord side)
            front_ports.append({
                'device': pp_name,
                'name': f'Front-{port}',
                'type': 'lc',
                'rear_port': f'Rear-{port}',
                'rear_port_position': '1',
                'description': f'Front port {port}'
            })

    # Server Halls - Spine/Leaf 48-port and Server 24-port Patch Panels
    for hall in ['A', 'B']:
        print(f"  - Server Hall {hall}: Fiber patch panels")

        # Spine racks (48-port)
        for spine_num in range(1, 3):
            pp_name = f'{site}-SRV-{hall}-R0{spine_num}-FPP01'
            for port in range(1, 49):
                rear_ports.append({
                    'device': pp_name,
                    'name': f'Rear-{port}',
                    'type': 'lc',
                    'positions': '1',
                    'description': f'Rear port {port}'
                })
                front_ports.append({
                    'device': pp_name,
                    'name': f'Front-{port}',
                    'type': 'lc',
                    'rear_port': f'Rear-{port}',
                    'rear_port_position': '1',
                    'description': f'Front port {port}'
                })

        # Leaf racks (48-port)
        for leaf_num in range(3, 5):
            pp_name = f'{site}-SRV-{hall}-R0{leaf_num}-FPP01'
            for port in range(1, 49):
                rear_ports.append({
                    'device': pp_name,
                    'name': f'Rear-{port}',
                    'type': 'lc',
                    'positions': '1',
                    'description': f'Rear port {port}'
                })
                front_ports.append({
                    'device': pp_name,
                    'name': f'Front-{port}',
                    'type': 'lc',
                    'rear_port': f'Rear-{port}',
                    'rear_port_position': '1',
                    'description': f'Front port {port}'
                })

        # Server racks (24-port)
        for srv_rack in range(1, 7):
            if srv_rack <= 4:
                pp_name = f'{site}-SRV-{hall}-R0{srv_rack}-FPP02'
            else:
                pp_name = f'{site}-SRV-{hall}-R0{srv_rack}-FPP01'

            for port in range(1, 25):
                rear_ports.append({
                    'device': pp_name,
                    'name': f'Rear-{port}',
                    'type': 'lc',
                    'positions': '1',
                    'description': f'Rear port {port}'
                })
                front_ports.append({
                    'device': pp_name,
                    'name': f'Front-{port}',
                    'type': 'lc',
                    'rear_port': f'Rear-{port}',
                    'rear_port_position': '1',
                    'description': f'Front port {port}'
                })

    # Storage Room - 24-port Fiber Patch Panels
    print("  - Storage Room: 24-port fiber patch panels")
    for stg_rack in range(1, 4):
        pp_name = f'{site}-STG-R0{stg_rack}-FPP01'
        for port in range(1, 25):
            rear_ports.append({
                'device': pp_name,
                'name': f'Rear-{port}',
                'type': 'lc',
                'positions': '1',
                'description': f'Rear port {port}'
            })
            front_ports.append({
                'device': pp_name,
                'name': f'Front-{port}',
                'type': 'lc',
                'rear_port': f'Rear-{port}',
                'rear_port_position': '1',
                'description': f'Front port {port}'
            })

    # MMR - 48-port Copper Patch Panel
    print("  - Meet-Me Room: 48-port copper patch panel")
    pp_name = f'{site}-MMR-R01-CPP01'
    for port in range(1, 49):
        rear_ports.append({
            'device': pp_name,
            'name': f'Rear-{port}',
            'type': '8p8c',  # RJ45
            'positions': '1',
            'description': f'Rear port {port}'
        })
        front_ports.append({
            'device': pp_name,
            'name': f'Front-{port}',
            'type': '8p8c',  # RJ45
            'rear_port': f'Rear-{port}',
            'rear_port_position': '1',
            'description': f'Front port {port}'
        })

print(f"\n✅ Generated {len(rear_ports)} rear ports")
print(f"✅ Generated {len(front_ports)} front ports")

# Write rear ports CSV
rear_file = 'lab/netbox_dc_patch_panel_rear_ports.csv'
with open(rear_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'positions', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rear_ports)

print(f"✅ Rear ports written to {rear_file}")

# Write front ports CSV
front_file = 'lab/netbox_dc_patch_panel_front_ports.csv'
with open(front_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'rear_port', 'rear_port_position', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(front_ports)

print(f"✅ Front ports written to {front_file}")

print("\n📊 Summary:")
print(f"  Total patch panels: 168")
print(f"  Total rear ports: {len(rear_ports)}")
print(f"  Total front ports: {len(front_ports)}")
print(f"\nEach patch panel port has:")
print(f"  - 1 Rear Port (permanent cabling)")
print(f"  - 1 Front Port (patch cords)")
