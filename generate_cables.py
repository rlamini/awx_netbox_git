#!/usr/bin/env python3
"""
Generate comprehensive cable connections for all 6 datacenters
"""
import csv
from pathlib import Path

# Cable types
CABLE_TYPE_DAC_10G = 'dac-active'
CABLE_TYPE_DAC_25G = 'dac-active'
CABLE_TYPE_DAC_40G = 'dac-active'
CABLE_TYPE_AOC_100G = 'aoc'
CABLE_TYPE_CAT6 = 'cat6'

cables = []
cable_id = 1

def add_cable(site, device_a, interface_a, device_b, interface_b, cable_type, label_suffix=""):
    global cable_id
    label = f"{site}-CABLE-{cable_id:04d}"
    if label_suffix:
        label += f"-{label_suffix}"

    cables.append({
        'label': label,
        'type': cable_type,
        'status': 'connected',
        'a_termination_type': 'dcim.interface',
        'a_termination': f'{device_a}:{interface_a}',
        'b_termination_type': 'dcim.interface',
        'b_termination': f'{device_b}:{interface_b}',
        'length': '',
        'length_unit': '',
        'description': f'Connection {device_a} to {device_b}'
    })
    cable_id += 1

# Site prefixes for the 6 DCs
sites = [
    'EMEA-DC-CLOUD',
    'EMEA-DC-ONPREM',
    'APAC-DC-CLOUD',
    'APAC-DC-ONPREM',
    'AMER-DC-CLOUD',
    'AMER-DC-ONPREM'
]

print("Generating cables for all 6 datacenters...")

for site in sites:
    print(f"\n{site}:")

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

    # Core Layer Connections
    print("  - Core layer connections")
    # Core-SW01 to Core-SW02 VPC Peer Link (40G)
    add_cable(site, core_sw01, 'Ethernet2/1', core_sw02, 'Ethernet2/1', CABLE_TYPE_DAC_40G, 'CORE-VPC')
    add_cable(site, core_sw01, 'Ethernet2/2', core_sw02, 'Ethernet2/2', CABLE_TYPE_DAC_40G, 'CORE-VPC')

    # Core to Distribution (10G links)
    add_cable(site, core_sw01, 'Ethernet1/1', dist_sw01, 'Ethernet1/1', CABLE_TYPE_DAC_10G, 'C01-D01')
    add_cable(site, core_sw01, 'Ethernet1/2', dist_sw01, 'Ethernet1/2', CABLE_TYPE_DAC_10G, 'C01-D01')
    add_cable(site, core_sw01, 'Ethernet1/3', dist_sw02, 'Ethernet1/1', CABLE_TYPE_DAC_10G, 'C01-D02')
    add_cable(site, core_sw01, 'Ethernet1/4', dist_sw02, 'Ethernet1/2', CABLE_TYPE_DAC_10G, 'C01-D02')

    add_cable(site, core_sw02, 'Ethernet1/1', dist_sw01, 'Ethernet1/3', CABLE_TYPE_DAC_10G, 'C02-D01')
    add_cable(site, core_sw02, 'Ethernet1/2', dist_sw01, 'Ethernet1/4', CABLE_TYPE_DAC_10G, 'C02-D01')
    add_cable(site, core_sw02, 'Ethernet1/3', dist_sw02, 'Ethernet1/3', CABLE_TYPE_DAC_10G, 'C02-D02')
    add_cable(site, core_sw02, 'Ethernet1/4', dist_sw02, 'Ethernet1/4', CABLE_TYPE_DAC_10G, 'C02-D02')

    # Distribution to Firewalls
    print("  - Distribution to Firewalls")
    add_cable(site, dist_sw01, 'Ethernet1/10', fw_ext_01, 'ethernet1/1', CABLE_TYPE_DAC_10G, 'D01-FWEXT01')
    add_cable(site, dist_sw01, 'Ethernet1/11', fw_ext_01, 'ethernet1/2', CABLE_TYPE_DAC_10G, 'D01-FWEXT01')
    add_cable(site, dist_sw02, 'Ethernet1/10', fw_ext_02, 'ethernet1/1', CABLE_TYPE_DAC_10G, 'D02-FWEXT02')
    add_cable(site, dist_sw02, 'Ethernet1/11', fw_ext_02, 'ethernet1/2', CABLE_TYPE_DAC_10G, 'D02-FWEXT02')

    add_cable(site, dist_sw01, 'Ethernet1/12', fw_int_01, 'ethernet1/1', CABLE_TYPE_DAC_10G, 'D01-FWINT01')
    add_cable(site, dist_sw01, 'Ethernet1/13', fw_int_01, 'ethernet1/2', CABLE_TYPE_DAC_10G, 'D01-FWINT01')
    add_cable(site, dist_sw02, 'Ethernet1/12', fw_int_02, 'ethernet1/1', CABLE_TYPE_DAC_10G, 'D02-FWINT02')
    add_cable(site, dist_sw02, 'Ethernet1/13', fw_int_02, 'ethernet1/2', CABLE_TYPE_DAC_10G, 'D02-FWINT02')

    # Distribution to Edge Routers
    print("  - Distribution to Edge Routers")
    add_cable(site, dist_sw01, 'Ethernet1/20', rtr_edge_01, 'TenGigE0/0/0/1', CABLE_TYPE_DAC_10G, 'D01-RTR01')
    add_cable(site, dist_sw01, 'Ethernet1/21', rtr_edge_01, 'TenGigE0/0/0/2', CABLE_TYPE_DAC_10G, 'D01-RTR01')
    add_cable(site, dist_sw02, 'Ethernet1/20', rtr_edge_02, 'TenGigE0/0/0/1', CABLE_TYPE_DAC_10G, 'D02-RTR02')
    add_cable(site, dist_sw02, 'Ethernet1/21', rtr_edge_02, 'TenGigE0/0/0/2', CABLE_TYPE_DAC_10G, 'D02-RTR02')

    # Distribution to Load Balancer (dual-homed)
    print("  - Distribution to Load Balancer")
    add_cable(site, dist_sw01, 'Ethernet1/30', lb_01, '1.1', CABLE_TYPE_DAC_10G, 'D01-LB01')
    add_cable(site, dist_sw01, 'Ethernet1/31', lb_01, '1.2', CABLE_TYPE_DAC_10G, 'D01-LB01')
    add_cable(site, dist_sw02, 'Ethernet1/30', lb_01, '1.3', CABLE_TYPE_DAC_10G, 'D02-LB01')
    add_cable(site, dist_sw02, 'Ethernet1/31', lb_01, '1.4', CABLE_TYPE_DAC_10G, 'D02-LB01')

    # Server Halls A and B
    for hall in ['A', 'B']:
        print(f"  - Server Hall {hall} - Spine-Leaf fabric")
        spine_01 = f'{site}-SPINE-{hall}01'
        spine_02 = f'{site}-SPINE-{hall}02'
        leaf_01 = f'{site}-LEAF-{hall}01'
        leaf_02 = f'{site}-LEAF-{hall}02'

        # Spine to Distribution (100G uplinks)
        add_cable(site, spine_01, 'Ethernet49', dist_sw01, 'Ethernet1/40', CABLE_TYPE_AOC_100G, f'SPINE{hall}01-D01')
        add_cable(site, spine_01, 'Ethernet50', dist_sw02, 'Ethernet1/40', CABLE_TYPE_AOC_100G, f'SPINE{hall}01-D02')
        add_cable(site, spine_02, 'Ethernet49', dist_sw01, 'Ethernet1/41', CABLE_TYPE_AOC_100G, f'SPINE{hall}02-D01')
        add_cable(site, spine_02, 'Ethernet50', dist_sw02, 'Ethernet1/41', CABLE_TYPE_AOC_100G, f'SPINE{hall}02-D02')

        # Full mesh: Each Leaf to Each Spine (4x 10G per leaf-spine pair)
        # LEAF-01 to SPINE-01
        add_cable(site, leaf_01, 'Ethernet49', spine_01, 'Ethernet1', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}01')
        add_cable(site, leaf_01, 'Ethernet50', spine_01, 'Ethernet2', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}01')
        add_cable(site, leaf_01, 'Ethernet51', spine_01, 'Ethernet3', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}01')
        add_cable(site, leaf_01, 'Ethernet52', spine_01, 'Ethernet4', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}01')

        # LEAF-01 to SPINE-02
        add_cable(site, leaf_01, 'Ethernet53', spine_02, 'Ethernet1', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}02')
        add_cable(site, leaf_01, 'Ethernet54', spine_02, 'Ethernet2', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}02')
        add_cable(site, leaf_01, 'Ethernet55', spine_02, 'Ethernet3', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}02')
        add_cable(site, leaf_01, 'Ethernet56', spine_02, 'Ethernet4', CABLE_TYPE_DAC_10G, f'LEAF{hall}01-SPINE{hall}02')

        # LEAF-02 to SPINE-01
        add_cable(site, leaf_02, 'Ethernet49', spine_01, 'Ethernet5', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}01')
        add_cable(site, leaf_02, 'Ethernet50', spine_01, 'Ethernet6', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}01')
        add_cable(site, leaf_02, 'Ethernet51', spine_01, 'Ethernet7', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}01')
        add_cable(site, leaf_02, 'Ethernet52', spine_01, 'Ethernet8', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}01')

        # LEAF-02 to SPINE-02
        add_cable(site, leaf_02, 'Ethernet53', spine_02, 'Ethernet5', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}02')
        add_cable(site, leaf_02, 'Ethernet54', spine_02, 'Ethernet6', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}02')
        add_cable(site, leaf_02, 'Ethernet55', spine_02, 'Ethernet7', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}02')
        add_cable(site, leaf_02, 'Ethernet56', spine_02, 'Ethernet8', CABLE_TYPE_DAC_10G, f'LEAF{hall}02-SPINE{hall}02')

        # Server connections (dual-homed to both leaf switches)
        print(f"  - Server Hall {hall} - Server connections")
        servers = []
        for i in range(1, 7):  # ESX-A01 through ESX-A06 (or B01-B06)
            if i <= 4:
                servers.append(f'{site}-ESX-{hall}0{i}')
            elif i == 5:
                servers.append(f'{site}-ESX-{hall}05')
            elif i == 6:
                servers.append(f'{site}-ESX-{hall}06')

        # Add physical DB servers for Hall B only
        if hall == 'B':
            servers.append(f'{site}-PHYS-DB01')
            servers.append(f'{site}-PHYS-DB02')

        # Connect each server: eno1,eno2 to LEAF-01 and eno3,eno4 to LEAF-02
        for idx, server in enumerate(servers):
            leaf_port_01 = idx * 2 + 1  # Ports 1,3,5,7,9,11,13,15 on LEAF-01
            leaf_port_02 = idx * 2 + 1  # Ports 1,3,5,7,9,11,13,15 on LEAF-02

            add_cable(site, server, 'eno1', leaf_01, f'Ethernet{leaf_port_01}', CABLE_TYPE_DAC_25G, f'{server}-LEAF01')
            add_cable(site, server, 'eno2', leaf_01, f'Ethernet{leaf_port_01 + 1}', CABLE_TYPE_DAC_25G, f'{server}-LEAF01')
            add_cable(site, server, 'eno3', leaf_02, f'Ethernet{leaf_port_02}', CABLE_TYPE_DAC_25G, f'{server}-LEAF02')
            add_cable(site, server, 'eno4', leaf_02, f'Ethernet{leaf_port_02 + 1}', CABLE_TYPE_DAC_25G, f'{server}-LEAF02')

    # Storage Room connections
    print("  - Storage Room connections")
    acc_stg_01 = f'{site}-ACC-STG-01'
    acc_stg_02 = f'{site}-ACC-STG-02'
    san_01 = f'{site}-SAN-01'
    san_02 = f'{site}-SAN-02'
    nas_01 = f'{site}-NAS-01'
    nas_02 = f'{site}-NAS-02'

    # Access switches to Distribution
    add_cable(site, acc_stg_01, 'GigabitEthernet1/0/47', dist_sw01, 'Ethernet1/45', CABLE_TYPE_DAC_10G, 'ACCSTG01-D01')
    add_cable(site, acc_stg_01, 'GigabitEthernet1/0/48', dist_sw02, 'Ethernet1/45', CABLE_TYPE_DAC_10G, 'ACCSTG01-D02')
    add_cable(site, acc_stg_02, 'GigabitEthernet1/0/47', dist_sw01, 'Ethernet1/46', CABLE_TYPE_DAC_10G, 'ACCSTG02-D01')
    add_cable(site, acc_stg_02, 'GigabitEthernet1/0/48', dist_sw02, 'Ethernet1/46', CABLE_TYPE_DAC_10G, 'ACCSTG02-D02')

    # Storage devices dual-homed to access switches (25G)
    add_cable(site, san_01, 'eth1', acc_stg_01, 'GigabitEthernet1/0/1', CABLE_TYPE_DAC_25G, 'SAN01-ACCSTG01')
    add_cable(site, san_01, 'eth2', acc_stg_01, 'GigabitEthernet1/0/2', CABLE_TYPE_DAC_25G, 'SAN01-ACCSTG01')
    add_cable(site, san_01, 'eth3', acc_stg_02, 'GigabitEthernet1/0/1', CABLE_TYPE_DAC_25G, 'SAN01-ACCSTG02')
    add_cable(site, san_01, 'eth4', acc_stg_02, 'GigabitEthernet1/0/2', CABLE_TYPE_DAC_25G, 'SAN01-ACCSTG02')

    add_cable(site, san_02, 'eth1', acc_stg_01, 'GigabitEthernet1/0/3', CABLE_TYPE_DAC_25G, 'SAN02-ACCSTG01')
    add_cable(site, san_02, 'eth2', acc_stg_01, 'GigabitEthernet1/0/4', CABLE_TYPE_DAC_25G, 'SAN02-ACCSTG01')
    add_cable(site, san_02, 'eth3', acc_stg_02, 'GigabitEthernet1/0/3', CABLE_TYPE_DAC_25G, 'SAN02-ACCSTG02')
    add_cable(site, san_02, 'eth4', acc_stg_02, 'GigabitEthernet1/0/4', CABLE_TYPE_DAC_25G, 'SAN02-ACCSTG02')

    add_cable(site, nas_01, 'ext-1', acc_stg_01, 'GigabitEthernet1/0/5', CABLE_TYPE_DAC_25G, 'NAS01-ACCSTG01')
    add_cable(site, nas_01, 'ext-2', acc_stg_01, 'GigabitEthernet1/0/6', CABLE_TYPE_DAC_25G, 'NAS01-ACCSTG01')
    add_cable(site, nas_01, 'ext-3', acc_stg_02, 'GigabitEthernet1/0/5', CABLE_TYPE_DAC_25G, 'NAS01-ACCSTG02')
    add_cable(site, nas_01, 'ext-4', acc_stg_02, 'GigabitEthernet1/0/6', CABLE_TYPE_DAC_25G, 'NAS01-ACCSTG02')

    add_cable(site, nas_02, 'ext-1', acc_stg_01, 'GigabitEthernet1/0/7', CABLE_TYPE_DAC_25G, 'NAS02-ACCSTG01')
    add_cable(site, nas_02, 'ext-2', acc_stg_01, 'GigabitEthernet1/0/8', CABLE_TYPE_DAC_25G, 'NAS02-ACCSTG01')
    add_cable(site, nas_02, 'ext-3', acc_stg_02, 'GigabitEthernet1/0/7', CABLE_TYPE_DAC_25G, 'NAS02-ACCSTG02')
    add_cable(site, nas_02, 'ext-4', acc_stg_02, 'GigabitEthernet1/0/8', CABLE_TYPE_DAC_25G, 'NAS02-ACCSTG02')

    # Meet-Me Room connections
    print("  - Meet-Me Room connections")
    mmr_sw01 = f'{site}-MMR-SW01'
    oob_rtr01 = f'{site}-OOB-RTR01'

    # MMR switch to Core
    add_cable(site, mmr_sw01, 'GigabitEthernet1/0/47', core_sw01, 'Ethernet1/48', CABLE_TYPE_DAC_10G, 'MMR-CORE01')
    add_cable(site, mmr_sw01, 'GigabitEthernet1/0/48', core_sw02, 'Ethernet1/48', CABLE_TYPE_DAC_10G, 'MMR-CORE02')

    # OOB router to MMR switch
    add_cable(site, oob_rtr01, 'GigabitEthernet0/1', mmr_sw01, 'GigabitEthernet1/0/1', CABLE_TYPE_CAT6, 'OOB-MMR')

    print(f"  Total cables for {site}: {len([c for c in cables if site in c['label']])}")

print(f"\n✅ Generated {len(cables)} cables across all 6 datacenters")

# Write cables CSV
cables_file = 'lab/cables/netbox_dc_cables.csv'
with open(cables_file, 'w', newline='') as f:
    fieldnames = ['label', 'type', 'status', 'a_termination_type', 'a_termination',
                  'b_termination_type', 'b_termination', 'length', 'length_unit', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cables)

print(f"✅ Cables written to {cables_file}")
