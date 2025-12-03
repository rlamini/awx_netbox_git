#!/usr/bin/env python3
"""
Generate structured cabling through patch panels for all 6 datacenters
Implements proper cable management with:
- Equipment cables (device to patch panel)
- Horizontal cables (rack to rack within same room)
- Vertical/Backbone cables (between floors/areas)
- Patch cords (front port to front port for cross-connects)
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

print("Generating structured cabling for all 6 datacenters...")

for site in sites:
    print(f"\n{site}:")
    site_cable_start = len(cables)

    # Device naming
    core_sw01 = f'{site}-CORE-SW01'
    core_sw02 = f'{site}-CORE-SW02'
    dist_sw01 = f'{site}-DIST-SW01'
    dist_sw02 = f'{site}-DIST-SW02'
    fw_ext_01 = f'{site}-FW-EXT-01'
    fw_ext_02 = f'{site}-FW-EXT-02'
    fw_int_01 = f'{site}-FW-INT-01'
    fw_int_02 = f'{site}-FW-INT-02'
    rtr_edge_01 = f'{site}-RTR-EDGE-01'
    rtr_edge_02 = f'{site}-RTR-EDGE-02'
    lb_01 = f'{site}-LB-01'

    # ============================================
    # NETWORK CORE - Equipment to Patch Panel
    # ============================================
    print("  - Network Core: Equipment cables")

    # CORE-SW01 to its patch panel (NET-R01)
    pp_core01 = f'{site}-NET-R01-FPP01'
    for port in range(1, 49):
        add_cable(
            f'{site}-EC-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{core_sw01}:Ethernet1/{port}',
            'dcim.interface',
            f'{pp_core01}:Port-{port}',
            f'Equipment cable: {core_sw01} to patch panel'
        )

    # CORE-SW02 to its patch panel (NET-R02)
    pp_core02 = f'{site}-NET-R02-FPP01'
    for port in range(1, 49):
        add_cable(
            f'{site}-EC-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{core_sw02}:Ethernet1/{port}',
            'dcim.interface',
            f'{pp_core02}:Port-{port}',
            f'Equipment cable: {core_sw02} to patch panel'
        )

    # DIST-SW01 to its patch panel (NET-R03)
    pp_dist01 = f'{site}-NET-R03-FPP01'
    for port in range(1, 49):
        add_cable(
            f'{site}-EC-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{dist_sw01}:Ethernet1/{port}',
            'dcim.interface',
            f'{pp_dist01}:Port-{port}',
            f'Equipment cable: {dist_sw01} to patch panel'
        )

    # DIST-SW02 to its patch panel (NET-R04)
    pp_dist02 = f'{site}-NET-R04-FPP01'
    for port in range(1, 49):
        add_cable(
            f'{site}-EC-{cable_id:05d}',
            'smf',
            'connected',
            'dcim.interface',
            f'{dist_sw02}:Ethernet1/{port}',
            'dcim.interface',
            f'{pp_dist02}:Port-{port}',
            f'Equipment cable: {dist_sw02} to patch panel'
        )

    # ============================================
    # NETWORK CORE - Patch Panel Cross-Connects
    # ============================================
    print("  - Network Core: Horizontal backbone cables")

    # Core VPC peer-link via patch panels
    # CORE-SW01 Port 49 (2/1 mapped) → PP Port 25 → Horizontal → PP Port 25 → CORE-SW02 Port 49
    add_cable(
        f'{site}-HC-{cable_id:05d}',
        'dac-active',
        'connected',
        'dcim.interface',
        f'{pp_core01}:Port-25',
        'dcim.interface',
        f'{pp_core02}:Port-25',
        'Horizontal cable: Core VPC peer-link (40G)'
    )
    add_cable(
        f'{site}-HC-{cable_id:05d}',
        'dac-active',
        'connected',
        'dcim.interface',
        f'{pp_core01}:Port-26',
        'dcim.interface',
        f'{pp_core02}:Port-26',
        'Horizontal cable: Core VPC peer-link (40G)'
    )

    # Core to Distribution horizontal cables
    # CORE-SW01 E1/1 → PP1 Port-1 → Horizontal → PP3 Port-1 → DIST-SW01 E1/1
    for i in range(1, 5):  # 4 links Core01 to Dist01
        add_cable(
            f'{site}-HC-{cable_id:05d}',
            'dac-active',
            'connected',
            'dcim.interface',
            f'{pp_core01}:Port-{i}',
            'dcim.interface',
            f'{pp_dist01}:Port-{i}',
            f'Horizontal cable: Core01 to Dist01 link {i}'
        )

    for i in range(1, 5):  # 4 links Core02 to Dist01
        add_cable(
            f'{site}-HC-{cable_id:05d}',
            'dac-active',
            'connected',
            'dcim.interface',
            f'{pp_core02}:Port-{i}',
            'dcim.interface',
            f'{pp_dist01}:Port-{i+4}',
            f'Horizontal cable: Core02 to Dist01 link {i}'
        )

    for i in range(1, 5):  # 4 links to Dist02
        add_cable(
            f'{site}-HC-{cable_id:05d}',
            'dac-active',
            'connected',
            'dcim.interface',
            f'{pp_core01}:Port-{i+4}',
            'dcim.interface',
            f'{pp_dist02}:Port-{i}',
            f'Horizontal cable: Core01 to Dist02 link {i}'
        )

    for i in range(1, 5):
        add_cable(
            f'{site}-HC-{cable_id:05d}',
            'dac-active',
            'connected',
            'dcim.interface',
            f'{pp_core02}:Port-{i+4}',
            'dcim.interface',
            f'{pp_dist02}:Port-{i+4}',
            f'Horizontal cable: Core02 to Dist02 link {i}'
        )

    # Distribution to Firewalls (using patch panel ports 10-13)
    add_cable(f'{site}-HC-{cable_id:05d}', 'dac-active', 'connected',
             'dcim.interface', f'{pp_dist01}:Port-10', 'dcim.interface', f'{pp_core01}:Port-10',
             'Horizontal cable: Dist01 to FW-EXT-01 via Core rack')

    # ============================================
    # SERVER HALLS - Spine/Leaf Fabric
    # ============================================
    for hall in ['A', 'B']:
        print(f"  - Server Hall {hall}: Spine-Leaf fabric cabling")

        spine_01 = f'{site}-SPINE-{hall}01'
        spine_02 = f'{site}-SPINE-{hall}02'
        leaf_01 = f'{site}-LEAF-{hall}01'
        leaf_02 = f'{site}-LEAF-{hall}02'

        pp_spine01 = f'{site}-SRV-{hall}-R01-FPP01'
        pp_spine02 = f'{site}-SRV-{hall}-R02-FPP01'
        pp_leaf01 = f'{site}-SRV-{hall}-R03-FPP01'
        pp_leaf02 = f'{site}-SRV-{hall}-R04-FPP01'

        # Spine01 equipment cables (48 ports)
        for port in range(1, 49):
            add_cable(
                f'{site}-EC-{cable_id:05d}',
                'smf',
                'connected',
                'dcim.interface',
                f'{spine_01}:Ethernet{port}',
                'dcim.interface',
                f'{pp_spine01}:Port-{port}',
                f'Equipment cable: {spine_01} to patch panel'
            )

        # Spine02 equipment cables
        for port in range(1, 49):
            add_cable(
                f'{site}-EC-{cable_id:05d}',
                'smf',
                'connected',
                'dcim.interface',
                f'{spine_02}:Ethernet{port}',
                'dcim.interface',
                f'{pp_spine02}:Port-{port}',
                f'Equipment cable: {spine_02} to patch panel'
            )

        # Leaf01 equipment cables (uplinks only, ports 49-60)
        for port in range(49, 61):
            pp_port = port - 48  # Map Ethernet49 → Port-1
            add_cable(
                f'{site}-EC-{cable_id:05d}',
                'smf',
                'connected',
                'dcim.interface',
                f'{leaf_01}:Ethernet{port}',
                'dcim.interface',
                f'{pp_leaf01}:Port-{pp_port}',
                f'Equipment cable: {leaf_01} uplink to patch panel'
            )

        # Leaf02 equipment cables (uplinks only)
        for port in range(49, 61):
            pp_port = port - 48
            add_cable(
                f'{site}-EC-{cable_id:05d}',
                'smf',
                'connected',
                'dcim.interface',
                f'{leaf_02}:Ethernet{port}',
                'dcim.interface',
                f'{pp_leaf02}:Port-{pp_port}',
                f'Equipment cable: {leaf_02} uplink to patch panel'
            )

        # Horizontal cables: Leaf to Spine mesh
        # Leaf01 to Spine01 (4 links)
        for i in range(1, 5):
            add_cable(
                f'{site}-HC-{cable_id:05d}',
                'dac-active',
                'connected',
                'dcim.interface',
                f'{pp_leaf01}:Port-{i}',
                'dcim.interface',
                f'{pp_spine01}:Port-{i}',
                f'Horizontal cable: Leaf01 to Spine01 link {i}'
            )

        # Leaf01 to Spine02 (4 links)
        for i in range(1, 5):
            add_cable(
                f'{site}-HC-{cable_id:05d}',
                'dac-active',
                'connected',
                'dcim.interface',
                f'{pp_leaf01}:Port-{i+4}',
                'dcim.interface',
                f'{pp_spine02}:Port-{i}',
                f'Horizontal cable: Leaf01 to Spine02 link {i}'
            )

        # Leaf02 to Spine01 (4 links)
        for i in range(1, 5):
            add_cable(
                f'{site}-HC-{cable_id:05d}',
                'dac-active',
                'connected',
                'dcim.interface',
                f'{pp_leaf02}:Port-{i}',
                'dcim.interface',
                f'{pp_spine01}:Port-{i+4}',
                f'Horizontal cable: Leaf02 to Spine01 link {i}'
            )

        # Leaf02 to Spine02 (4 links)
        for i in range(1, 5):
            add_cable(
                f'{site}-HC-{cable_id:05d}',
                'dac-active',
                'connected',
                'dcim.interface',
                f'{pp_leaf02}:Port-{i+4}',
                'dcim.interface',
                f'{pp_spine02}:Port-{i+4}',
                f'Horizontal cable: Leaf02 to Spine02 link {i}'
            )

        # Spine to Distribution (100G uplinks) - Vertical cables
        add_cable(f'{site}-VC-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.interface', f'{pp_spine01}:Port-45', 'dcim.interface', f'{pp_dist01}:Port-40',
                 f'Vertical cable: Spine{hall}01 to Dist01 100G')
        add_cable(f'{site}-VC-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.interface', f'{pp_spine01}:Port-46', 'dcim.interface', f'{pp_dist02}:Port-40',
                 f'Vertical cable: Spine{hall}01 to Dist02 100G')
        add_cable(f'{site}-VC-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.interface', f'{pp_spine02}:Port-45', 'dcim.interface', f'{pp_dist01}:Port-41',
                 f'Vertical cable: Spine{hall}02 to Dist01 100G')
        add_cable(f'{site}-VC-{cable_id:05d}', 'aoc', 'connected',
                 'dcim.interface', f'{pp_spine02}:Port-46', 'dcim.interface', f'{pp_dist02}:Port-41',
                 f'Vertical cable: Spine{hall}02 to Dist02 100G')

        # ============================================
        # SERVERS - Equipment to Patch Panel
        # ============================================
        print(f"  - Server Hall {hall}: Server equipment cables")

        servers = []
        for i in range(1, 7):
            if i <= 4:
                servers.append(f'{site}-ESX-{hall}0{i}')
            elif i == 5:
                servers.append(f'{site}-ESX-{hall}05')
            elif i == 6:
                servers.append(f'{site}-ESX-{hall}06')

        if hall == 'B':
            servers.append(f'{site}-PHYS-DB01')
            servers.append(f'{site}-PHYS-DB02')

        # Connect each server to patch panels in its rack
        for idx, server in enumerate(servers):
            # Determine which rack the server is in
            if idx < 2:  # Servers 1-2 in racks 5-6
                rack_num = idx + 5
            elif idx < 4:  # Servers 3-4 in racks 1-2
                rack_num = idx - 1
            else:  # Servers 5-6 (or DB servers) in racks 3-4
                rack_num = idx - 3

            # Patch panel name based on rack
            if rack_num <= 4:
                pp_server = f'{site}-SRV-{hall}-R0{rack_num}-FPP02'  # Mid-rack PP for servers
            else:
                pp_server = f'{site}-SRV-{hall}-R0{rack_num}-FPP01'  # ToR PP

            # Server NICs to patch panel (4 ports per server)
            for nic in range(1, 5):
                pp_port = (idx % 2) * 4 + nic  # 2 servers per rack, 4 ports each
                add_cable(
                    f'{site}-EC-{cable_id:05d}',
                    'smf',
                    'connected',
                    'dcim.interface',
                    f'{server}:eno{nic}',
                    'dcim.interface',
                    f'{pp_server}:Port-{pp_port}',
                    f'Equipment cable: {server} to patch panel'
                )

            # Horizontal cables from server rack PP to leaf PP
            # eno1/eno2 → Leaf01, eno3/eno4 → Leaf02
            for nic in range(1, 5):
                pp_port_src = (idx % 2) * 4 + nic
                leaf_port = idx * 2 + ((nic - 1) % 2) + 1

                if nic <= 2:
                    pp_leaf_dst = pp_leaf01
                else:
                    pp_leaf_dst = pp_leaf02

                add_cable(
                    f'{site}-HC-{cable_id:05d}',
                    'dac-active',
                    'connected',
                    'dcim.interface',
                    f'{pp_server}:Port-{pp_port_src}',
                    'dcim.interface',
                    f'{pp_leaf_dst}:Port-{leaf_port+12}',  # Offset for downlink ports
                    f'Horizontal cable: Server rack to Leaf switch'
                )

    # ============================================
    # STORAGE ROOM
    # ============================================
    print("  - Storage Room: Equipment and horizontal cables")

    acc_stg_01 = f'{site}-ACC-STG-01'
    acc_stg_02 = f'{site}-ACC-STG-02'
    san_01 = f'{site}-SAN-01'
    san_02 = f'{site}-SAN-02'
    nas_01 = f'{site}-NAS-01'
    nas_02 = f'{site}-NAS-02'

    pp_stg01 = f'{site}-STG-R01-FPP01'
    pp_stg02 = f'{site}-STG-R02-FPP01'
    pp_stg03 = f'{site}-STG-R03-FPP01'

    # Access switch equipment cables (uplinks only)
    for port in [47, 48]:
        pp_port = port - 46
        add_cable(f'{site}-EC-{cable_id:05d}', 'smf', 'connected',
                 'dcim.interface', f'{acc_stg_01}:GigabitEthernet1/0/{port}',
                 'dcim.interface', f'{pp_stg01}:Port-{pp_port}',
                 f'Equipment cable: {acc_stg_01} uplink to PP')

    for port in [47, 48]:
        pp_port = port - 46
        add_cable(f'{site}-EC-{cable_id:05d}', 'smf', 'connected',
                 'dcim.interface', f'{acc_stg_02}:GigabitEthernet1/0/{port}',
                 'dcim.interface', f'{pp_stg02}:Port-{pp_port}',
                 f'Equipment cable: {acc_stg_02} uplink to PP')

    # Storage device equipment cables
    for eth in range(1, 5):
        add_cable(f'{site}-EC-{cable_id:05d}', 'smf', 'connected',
                 'dcim.interface', f'{san_01}:eth{eth}',
                 'dcim.interface', f'{pp_stg03}:Port-{eth}',
                 f'Equipment cable: {san_01} to PP')
        add_cable(f'{site}-EC-{cable_id:05d}', 'smf', 'connected',
                 'dcim.interface', f'{san_02}:eth{eth}',
                 'dcim.interface', f'{pp_stg01}:Port-{eth+4}',
                 f'Equipment cable: {san_02} to PP')
        add_cable(f'{site}-EC-{cable_id:05d}', 'smf', 'connected',
                 'dcim.interface', f'{nas_01}:ext-{eth}',
                 'dcim.interface', f'{pp_stg02}:Port-{eth+4}',
                 f'Equipment cable: {nas_01} to PP')
        add_cable(f'{site}-EC-{cable_id:05d}', 'smf', 'connected',
                 'dcim.interface', f'{nas_02}:ext-{eth}',
                 'dcim.interface', f'{pp_stg03}:Port-{eth+4}',
                 f'Equipment cable: {nas_02} to PP')

    # Horizontal cables: Storage to access switches
    add_cable(f'{site}-HC-{cable_id:05d}', 'dac-active', 'connected',
             'dcim.interface', f'{pp_stg03}:Port-1', 'dcim.interface', f'{pp_stg01}:Port-10',
             'Horizontal cable: SAN-01 to ACC-STG-01')

    # ============================================
    # MEET-ME ROOM
    # ============================================
    print("  - Meet-Me Room: Management cables")

    mmr_sw01 = f'{site}-MMR-SW01'
    oob_rtr01 = f'{site}-OOB-RTR01'
    pp_mmr = f'{site}-MMR-R01-CPP01'

    # Equipment cables
    for port in [47, 48]:
        pp_port = port - 46
        add_cable(f'{site}-EC-{cable_id:05d}', 'cat6', 'connected',
                 'dcim.interface', f'{mmr_sw01}:GigabitEthernet1/0/{port}',
                 'dcim.interface', f'{pp_mmr}:Port-{pp_port}',
                 f'Equipment cable: {mmr_sw01} to copper PP')

    add_cable(f'{site}-EC-{cable_id:05d}', 'cat6', 'connected',
             'dcim.interface', f'{oob_rtr01}:GigabitEthernet0/1',
             'dcim.interface', f'{pp_mmr}:Port-10',
             f'Equipment cable: {oob_rtr01} to copper PP')

    site_cable_count = len(cables) - site_cable_start
    print(f"  Total cables for {site}: {site_cable_count}")

print(f"\n✅ Generated {len(cables)} structured cables across all 6 datacenters")

# Write cables CSV
cables_file = 'lab/netbox_dc_structured_cables.csv'
with open(cables_file, 'w', newline='') as f:
    fieldnames = ['label', 'type', 'status', 'a_termination_type', 'a_termination',
                  'b_termination_type', 'b_termination', 'length', 'length_unit', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cables)

print(f"✅ Structured cables written to {cables_file}")

# Summary
print("\n📊 Cable Types Summary:")
print("  EC = Equipment Cable (device to patch panel)")
print("  HC = Horizontal Cable (patch panel to patch panel, same floor)")
print("  VC = Vertical Cable (patch panel to patch panel, different floors/areas)")
print(f"\nTotal equipment cables: {len([c for c in cables if '-EC-' in c['label']])}")
print(f"Total horizontal cables: {len([c for c in cables if '-HC-' in c['label']])}")
print(f"Total vertical cables: {len([c for c in cables if '-VC-' in c['label']])}")
