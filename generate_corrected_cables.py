#!/usr/bin/env python3
"""
Generate corrected cables using patch panel front/rear ports
"""
import csv
from pathlib import Path

sites = [
    'EMEA-DC-CLOUD',
    'EMEA-DC-ONPREM',
    'APAC-DC-CLOUD',
    'APAC-DC-ONPREM',
    'AMER-DC-CLOUD',
    'AMER-DC-ONPREM'
]

cables = []
cable_id = 1

def add_cable(label, cable_type, status, a_device, a_type, a_name, b_device, b_type, b_name, desc):
    global cable_id
    cables.append({
        'label': label,
        'type': cable_type,
        'status': status,
        'side_a_device': a_device,
        'side_a_type': a_type,
        'side_a_name': a_name,
        'side_b_device': b_device,
        'side_b_type': b_type,
        'side_b_name': b_name,
        'length': '',
        'length_unit': '',
        'description': desc
    })
    cable_id += 1

print("Generating corrected cables with front/rear ports...")

for site in sites:
    print(f"\n{site}:")

    # Core switches to patch panels (equipment cables to rear ports)
    core_sw01 = f'{site}-CORE-SW01'
    core_sw02 = f'{site}-CORE-SW02'
    pp_core01 = f'{site}-NET-R01-FPP01'
    pp_core02 = f'{site}-NET-R02-FPP01'

    print("  - Core switches to patch panels")
    # Core-SW01 to patch panel front ports
    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            core_sw01,
            'dcim.interface',
            f'Ethernet1/{port}',
            pp_core01,
            'dcim.frontport',
            f'Front-{port}',
            f'Equipment cable: {core_sw01} to front port'
        )

    # Core-SW02 to patch panel front ports
    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            core_sw02,
            'dcim.interface',
            f'Ethernet1/{port}',
            pp_core02,
            'dcim.frontport',
            f'Front-{port}',
            f'Equipment cable: {core_sw02} to front port'
        )

    # Distribution switches to patch panels
    dist_sw01 = f'{site}-DIST-SW01'
    dist_sw02 = f'{site}-DIST-SW02'
    pp_dist01 = f'{site}-NET-R03-FPP01'
    pp_dist02 = f'{site}-NET-R04-FPP01'

    print("  - Distribution switches to patch panels")
    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            dist_sw01,
            'dcim.interface',
            f'Ethernet1/{port}',
            pp_dist01,
            'dcim.frontport',
            f'Front-{port}',
            f'Equipment cable: {dist_sw01} to front port'
        )

    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            dist_sw02,
            'dcim.interface',
            f'Ethernet1/{port}',
            pp_dist02,
            'dcim.frontport',
            f'Front-{port}',
            f'Equipment cable: {dist_sw02} to front port'
        )

    # Horizontal cables: Core to Distribution via rear ports (permanent cabling)
    print("  - Horizontal cables between patch panels")

    # Core VPC peer-link
    add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
             pp_core01, 'dcim.rearport', 'Rear-25',
             pp_core02, 'dcim.rearport', 'Rear-25',
             'Horizontal cable: Core VPC peer-link')
    add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
             pp_core01, 'dcim.rearport', 'Rear-26',
             pp_core02, 'dcim.rearport', 'Rear-26',
             'Horizontal cable: Core VPC peer-link')

    # Core01 to Dist01
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 pp_core01, 'dcim.rearport', f'Rear-{i}',
                 pp_dist01, 'dcim.rearport', f'Rear-{i}',
                 f'Horizontal cable: Core01 to Dist01 link {i}')

    # Core02 to Dist01
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 pp_core02, 'dcim.rearport', f'Rear-{i}',
                 pp_dist01, 'dcim.rearport', f'Rear-{i+4}',
                 f'Horizontal cable: Core02 to Dist01 link {i}')

    # Core01 to Dist02
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 pp_core01, 'dcim.rearport', f'Rear-{i+4}',
                 pp_dist02, 'dcim.rearport', f'Rear-{i}',
                 f'Horizontal cable: Core01 to Dist02 link {i}')

    # Core02 to Dist02
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 pp_core02, 'dcim.rearport', f'Rear-{i+4}',
                 pp_dist02, 'dcim.rearport', f'Rear-{i+4}',
                 f'Horizontal cable: Core02 to Dist02 link {i}')

    # Server Halls - Spine/Leaf fabric
    for hall in ['A', 'B']:
        print(f"  - Server Hall {hall}")

        spine_01 = f'{site}-SPINE-{hall}01'
        spine_02 = f'{site}-SPINE-{hall}02'
        leaf_01 = f'{site}-LEAF-{hall}01'
        leaf_02 = f'{site}-LEAF-{hall}02'

        pp_spine01 = f'{site}-SRV-{hall}-R01-FPP01'
        pp_spine02 = f'{site}-SRV-{hall}-R02-FPP01'
        pp_leaf01 = f'{site}-SRV-{hall}-R03-FPP01'
        pp_leaf02 = f'{site}-SRV-{hall}-R04-FPP01'

        # Spine switches to front ports
        for port in range(1, 49):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     spine_01, 'dcim.interface', f'Ethernet{port}',
                     pp_spine01, 'dcim.frontport', f'Front-{port}',
                     f'Equipment cable: {spine_01} to front port')

        for port in range(1, 49):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     spine_02, 'dcim.interface', f'Ethernet{port}',
                     pp_spine02, 'dcim.frontport', f'Front-{port}',
                     f'Equipment cable: {spine_02} to front port')

        # Leaf switches uplinks to front ports
        for port in range(49, 61):
            pp_port = port - 48
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     leaf_01, 'dcim.interface', f'Ethernet{port}',
                     pp_leaf01, 'dcim.frontport', f'Front-{pp_port}',
                     f'Equipment cable: {leaf_01} uplink to front port')

        for port in range(49, 61):
            pp_port = port - 48
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     leaf_02, 'dcim.interface', f'Ethernet{port}',
                     pp_leaf02, 'dcim.frontport', f'Front-{pp_port}',
                     f'Equipment cable: {leaf_02} uplink to front port')

        # Horizontal cables: Leaf to Spine mesh via rear ports
        # Leaf01 to Spine01
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     pp_leaf01, 'dcim.rearport', f'Rear-{i}',
                     pp_spine01, 'dcim.rearport', f'Rear-{i}',
                     f'Horizontal cable: Leaf01 to Spine01 link {i}')

        # Leaf01 to Spine02
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     pp_leaf01, 'dcim.rearport', f'Rear-{i+4}',
                     pp_spine02, 'dcim.rearport', f'Rear-{i}',
                     f'Horizontal cable: Leaf01 to Spine02 link {i}')

        # Leaf02 to Spine01
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     pp_leaf02, 'dcim.rearport', f'Rear-{i}',
                     pp_spine01, 'dcim.rearport', f'Rear-{i+4}',
                     f'Horizontal cable: Leaf02 to Spine01 link {i}')

        # Leaf02 to Spine02
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     pp_leaf02, 'dcim.rearport', f'Rear-{i+4}',
                     pp_spine02, 'dcim.rearport', f'Rear-{i+4}',
                     f'Horizontal cable: Leaf02 to Spine02 link {i}')

        # Spine to Distribution 100G uplinks via rear ports
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 pp_spine01, 'dcim.rearport', 'Rear-45',
                 pp_dist01, 'dcim.rearport', 'Rear-40',
                 f'Vertical backbone: Spine{hall}01 to Dist01 100G')
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 pp_spine01, 'dcim.rearport', 'Rear-46',
                 pp_dist02, 'dcim.rearport', 'Rear-40',
                 f'Vertical backbone: Spine{hall}01 to Dist02 100G')
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 pp_spine02, 'dcim.rearport', 'Rear-45',
                 pp_dist01, 'dcim.rearport', 'Rear-41',
                 f'Vertical backbone: Spine{hall}02 to Dist01 100G')
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 pp_spine02, 'dcim.rearport', 'Rear-46',
                 pp_dist02, 'dcim.rearport', 'Rear-41',
                 f'Vertical backbone: Spine{hall}02 to Dist02 100G')

        # Servers to patch panels (simplified - key servers only)
        print(f"    - Sample server connections")
        for srv_num in [1, 2]:  # ESX-A01, ESX-A02
            server = f'{site}-ESX-{hall}0{srv_num}'
            rack_num = 5 if srv_num == 1 else 6
            pp_server = f'{site}-SRV-{hall}-R0{rack_num}-FPP01'

            # Server NICs to patch panel front ports
            for nic in range(1, 5):
                add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                         server, 'dcim.interface', f'eno{nic}',
                         pp_server, 'dcim.frontport', f'Front-{nic}',
                         f'Equipment cable: {server} to front port')

print(f"\n✅ Generated {len(cables)} cables with proper front/rear port terminations")

# Write cables CSV
cables_file = 'lab/netbox_dc_cables.csv'
with open(cables_file, 'w', newline='') as f:
    fieldnames = ['label', 'type', 'status', 'side_a_device', 'side_a_type', 'side_a_name',
                  'side_b_device', 'side_b_type', 'side_b_name', 'length', 'length_unit', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cables)

print(f"✅ Cables written to {cables_file}")
print("\n📊 Cable termination types:")
print(f"  Equipment cables (interface → frontport): {len([c for c in cables if c['side_a_type'] == 'dcim.interface' and c['side_b_type'] == 'dcim.frontport'])}")
print(f"  Horizontal cables (rearport → rearport): {len([c for c in cables if c['side_a_type'] == 'dcim.rearport' and c['side_b_type'] == 'dcim.rearport'])}")
