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

def add_cable(label, cable_type, status, a_term_type, a_term, b_term_type, b_term, desc):
    global cable_id
    cables.append({
        'label': label,
        'type': cable_type,
        'status': status,
        'a_termination_type': a_term_type,
        'a_termination': a_term,
        'b_termination_type': b_term_type,
        'b_termination': b_term,
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
    # Core-SW01 to patch panel rear ports
    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{core_sw01}:Ethernet1/{port}',
            'dcim.rearport',
            f'{pp_core01}:Rear-{port}',
            f'Equipment cable: {core_sw01} to rear port'
        )

    # Core-SW02 to patch panel rear ports
    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{core_sw02}:Ethernet1/{port}',
            'dcim.rearport',
            f'{pp_core02}:Rear-{port}',
            f'Equipment cable: {core_sw02} to rear port'
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
            'dcim.interface',
            f'{dist_sw01}:Ethernet1/{port}',
            'dcim.rearport',
            f'{pp_dist01}:Rear-{port}',
            f'Equipment cable: {dist_sw01} to rear port'
        )

    for port in range(1, 49):
        add_cable(
            f'{site}-CABLE-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{dist_sw02}:Ethernet1/{port}',
            'dcim.rearport',
            f'{pp_dist02}:Rear-{port}',
            f'Equipment cable: {dist_sw02} to rear port'
        )

    # Horizontal cables: Core to Distribution via front ports (patch cords)
    print("  - Horizontal cables between patch panels")

    # Core VPC peer-link
    add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
             'dcim.frontport', f'{pp_core01}:Front-25',
             'dcim.frontport', f'{pp_core02}:Front-25',
             'Patch cord: Core VPC peer-link')
    add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
             'dcim.frontport', f'{pp_core01}:Front-26',
             'dcim.frontport', f'{pp_core02}:Front-26',
             'Patch cord: Core VPC peer-link')

    # Core01 to Dist01
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 'dcim.frontport', f'{pp_core01}:Front-{i}',
                 'dcim.frontport', f'{pp_dist01}:Front-{i}',
                 f'Patch cord: Core01 to Dist01 link {i}')

    # Core02 to Dist01
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 'dcim.frontport', f'{pp_core02}:Front-{i}',
                 'dcim.frontport', f'{pp_dist01}:Front-{i+4}',
                 f'Patch cord: Core02 to Dist01 link {i}')

    # Core01 to Dist02
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 'dcim.frontport', f'{pp_core01}:Front-{i+4}',
                 'dcim.frontport', f'{pp_dist02}:Front-{i}',
                 f'Patch cord: Core01 to Dist02 link {i}')

    # Core02 to Dist02
    for i in range(1, 5):
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                 'dcim.frontport', f'{pp_core02}:Front-{i+4}',
                 'dcim.frontport', f'{pp_dist02}:Front-{i+4}',
                 f'Patch cord: Core02 to Dist02 link {i}')

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

        # Spine switches to rear ports
        for port in range(1, 49):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     'dcim.interface', f'{spine_01}:Ethernet{port}',
                     'dcim.rearport', f'{pp_spine01}:Rear-{port}',
                     f'Equipment cable: {spine_01} to rear port')

        for port in range(1, 49):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     'dcim.interface', f'{spine_02}:Ethernet{port}',
                     'dcim.rearport', f'{pp_spine02}:Rear-{port}',
                     f'Equipment cable: {spine_02} to rear port')

        # Leaf switches uplinks to rear ports
        for port in range(49, 61):
            pp_port = port - 48
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     'dcim.interface', f'{leaf_01}:Ethernet{port}',
                     'dcim.rearport', f'{pp_leaf01}:Rear-{pp_port}',
                     f'Equipment cable: {leaf_01} uplink to rear port')

        for port in range(49, 61):
            pp_port = port - 48
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                     'dcim.interface', f'{leaf_02}:Ethernet{port}',
                     'dcim.rearport', f'{pp_leaf02}:Rear-{pp_port}',
                     f'Equipment cable: {leaf_02} uplink to rear port')

        # Patch cords: Leaf to Spine mesh via front ports
        # Leaf01 to Spine01
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     'dcim.frontport', f'{pp_leaf01}:Front-{i}',
                     'dcim.frontport', f'{pp_spine01}:Front-{i}',
                     f'Patch cord: Leaf01 to Spine01 link {i}')

        # Leaf01 to Spine02
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     'dcim.frontport', f'{pp_leaf01}:Front-{i+4}',
                     'dcim.frontport', f'{pp_spine02}:Front-{i}',
                     f'Patch cord: Leaf01 to Spine02 link {i}')

        # Leaf02 to Spine01
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     'dcim.frontport', f'{pp_leaf02}:Front-{i}',
                     'dcim.frontport', f'{pp_spine01}:Front-{i+4}',
                     f'Patch cord: Leaf02 to Spine01 link {i}')

        # Leaf02 to Spine02
        for i in range(1, 5):
            add_cable(f'{site}-CABLE-{cable_id:05d}', 'dac-active', 'connected',
                     'dcim.frontport', f'{pp_leaf02}:Front-{i+4}',
                     'dcim.frontport', f'{pp_spine02}:Front-{i+4}',
                     f'Patch cord: Leaf02 to Spine02 link {i}')

        # Spine to Distribution 100G uplinks via front ports
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.frontport', f'{pp_spine01}:Front-45',
                 'dcim.frontport', f'{pp_dist01}:Front-40',
                 f'Vertical backbone: Spine{hall}01 to Dist01 100G')
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.frontport', f'{pp_spine01}:Front-46',
                 'dcim.frontport', f'{pp_dist02}:Front-40',
                 f'Vertical backbone: Spine{hall}01 to Dist02 100G')
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.frontport', f'{pp_spine02}:Front-45',
                 'dcim.frontport', f'{pp_dist01}:Front-41',
                 f'Vertical backbone: Spine{hall}02 to Dist01 100G')
        add_cable(f'{site}-CABLE-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.frontport', f'{pp_spine02}:Front-46',
                 'dcim.frontport', f'{pp_dist02}:Front-41',
                 f'Vertical backbone: Spine{hall}02 to Dist02 100G')

        # Servers to patch panels (simplified - key servers only)
        print(f"    - Sample server connections")
        for srv_num in [1, 2]:  # ESX-A01, ESX-A02
            server = f'{site}-ESX-{hall}0{srv_num}'
            rack_num = 5 if srv_num == 1 else 6
            pp_server = f'{site}-SRV-{hall}-R0{rack_num}-FPP01'

            # Server NICs to patch panel rear ports
            for nic in range(1, 5):
                add_cable(f'{site}-CABLE-{cable_id:05d}', 'smf', 'connected',
                         'dcim.interface', f'{server}:eno{nic}',
                         'dcim.rearport', f'{pp_server}:Rear-{nic}',
                         f'Equipment cable: {server} to rear port')

print(f"\n✅ Generated {len(cables)} cables with proper front/rear port terminations")

# Write cables CSV
cables_file = 'lab/netbox_dc_cables.csv'
with open(cables_file, 'w', newline='') as f:
    fieldnames = ['label', 'type', 'status', 'a_termination_type', 'a_termination',
                  'b_termination_type', 'b_termination', 'length', 'length_unit', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cables)

print(f"✅ Cables written to {cables_file}")
print("\n📊 Cable termination types:")
print(f"  Equipment cables (interface → rearport): {len([c for c in cables if 'rearport' in c['b_termination_type']])}")
print(f"  Patch cords (frontport → frontport): {len([c for c in cables if 'frontport' in c['a_termination_type']])}")
