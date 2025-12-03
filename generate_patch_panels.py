#!/usr/bin/env python3
"""
Generate patch panels for all datacenter racks with structured cabling
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

patch_panels = []
patch_panel_interfaces = []

print("Generating patch panels for all datacenters...")

for site in sites:
    print(f"\n{site}:")

    # Network Core Racks - Fiber Patch Panels for interconnects
    print("  - Network Core racks: Fiber patch panels")
    # NET-R01: CORE-SW01 at 1-13, FW at 30-33, RTR at 41-42 → Place PP at 20
    # NET-R02: CORE-SW02 at 14-26, FW at 34-37, RTR at 41-42 → Place PP at 5
    # NET-R03: DIST-SW01 at 27, FW at 38-39, LB at 41 → Place PP at 15
    # NET-R04: DIST-SW02 at 28, FW at 40-41 → Place PP at 15
    rack_positions = {'1': '20', '2': '5', '3': '15', '4': '15'}

    for rack_num in range(1, 5):  # NET-R01 through NET-R04
        rack = f'{site}-NET-R0{rack_num}'
        pp_name = f'{site}-NET-R0{rack_num}-FPP01'

        patch_panels.append({
            'name': pp_name,
            'manufacturer': 'Generic',
            'device_type': 'Fiber Patch Panel 48-Port',
            'role': 'Patch Panel',
            'site': site,
            'location': f'{site}-Network Core',
            'rack': rack,
            'position': rack_positions[str(rack_num)],  # Safe positions avoiding conflicts
            'face': 'front',
            'status': 'active',
            'description': 'Fiber patch panel for network interconnects'
        })

        # Generate 48 ports for this patch panel
        for port in range(1, 49):
            patch_panel_interfaces.append({
                'device': pp_name,
                'name': f'Port-{port}',
                'type': 'other',  # Generic type for patch panel ports
                'enabled': 'true',
                'description': f'Fiber port {port}'
            })

    # Server Hall A & B - Fiber Patch Panels in each rack
    for hall in ['A', 'B']:
        print(f"  - Server Hall {hall}: Fiber patch panels for ToR")
        # Spine racks: Spine switch at 42 (1U), servers below → Place PP at 39 (2U, occupies 39-40)
        for spine_num in range(1, 3):  # SPINE-A01, SPINE-A02
            rack = f'{site}-SRV-{hall}-R0{spine_num}'
            pp_name = f'{site}-SRV-{hall}-R0{spine_num}-FPP01'

            patch_panels.append({
                'name': pp_name,
                'manufacturer': 'Generic',
                'device_type': 'Fiber Patch Panel 48-Port',
                'role': 'Patch Panel',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': '39',  # Below spine switch (avoids conflict with switch at 42)
                'face': 'front',
                'status': 'active',
                'description': 'Fiber patch panel for spine switch'
            })

            for port in range(1, 49):
                patch_panel_interfaces.append({
                    'device': pp_name,
                    'name': f'Port-{port}',
                    'type': 'other',
                    'enabled': 'true',
                    'description': f'Fiber port {port}'
                })

        # Leaf racks: Leaf switch at 42 (1U) → Place PP at 39 (2U, occupies 39-40)
        for leaf_num in range(3, 5):  # Racks 3-4 have leaf switches
            rack = f'{site}-SRV-{hall}-R0{leaf_num}'
            pp_name = f'{site}-SRV-{hall}-R0{leaf_num}-FPP01'

            patch_panels.append({
                'name': pp_name,
                'manufacturer': 'Generic',
                'device_type': 'Fiber Patch Panel 48-Port',
                'role': 'Patch Panel',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': '39',  # Below leaf switch (avoids conflict with switch at 42)
                'face': 'front',
                'status': 'active',
                'description': 'Fiber patch panel for leaf switch'
            })

            for port in range(1, 49):
                patch_panel_interfaces.append({
                    'device': pp_name,
                    'name': f'Port-{port}',
                    'type': 'other',
                    'enabled': 'true',
                    'description': f'Fiber port {port}'
                })

        # Server racks - Fiber patch panels for 25G server connections
        # Racks 1-4 have spine/leaf switches at top, servers below (use FPP02 for servers)
        # Racks 5-6 only have servers (use FPP01)
        for srv_rack in range(1, 7):  # SRV-A-R01 through SRV-A-R06
            rack = f'{site}-SRV-{hall}-R0{srv_rack}'

            # Racks 1-4 already have FPP01 for spine/leaf, use FPP02 for servers
            # Racks 5-6 only have servers, use FPP01
            if srv_rack <= 4:
                pp_name = f'{site}-SRV-{hall}-R0{srv_rack}-FPP02'
                position = '25'  # Mid-rack for server connections
            else:
                pp_name = f'{site}-SRV-{hall}-R0{srv_rack}-FPP01'
                position = '40'  # Top of rack

            # Use 24-port for server racks (sufficient for 1-2 servers per rack)
            patch_panels.append({
                'name': pp_name,
                'manufacturer': 'Generic',
                'device_type': 'Fiber Patch Panel 24-Port',
                'role': 'Patch Panel',
                'site': site,
                'location': f'{site}-Server Hall {hall}',
                'rack': rack,
                'position': position,
                'face': 'front',
                'status': 'active',
                'description': 'Fiber patch panel for server connections'
            })

            for port in range(1, 25):
                patch_panel_interfaces.append({
                    'device': pp_name,
                    'name': f'Port-{port}',
                    'type': 'other',
                    'enabled': 'true',
                    'description': f'Fiber port {port}'
                })

    # Storage Room - Fiber patch panels
    # STG-R01/R02: Access switch at 42, storage devices low → Place PP at 39
    # STG-R03: Storage devices at 1-12 → Place PP at 39
    print("  - Storage Room: Fiber patch panels")
    for stg_rack in range(1, 4):  # STG-R01, STG-R02, STG-R03
        rack = f'{site}-STG-R0{stg_rack}'
        pp_name = f'{site}-STG-R0{stg_rack}-FPP01'

        patch_panels.append({
            'name': pp_name,
            'manufacturer': 'Generic',
            'device_type': 'Fiber Patch Panel 24-Port',
            'role': 'Patch Panel',
            'site': site,
            'location': f'{site}-Storage Room',
            'rack': rack,
            'position': '39',  # Below access switches (avoids conflict with switch at 42)
            'face': 'front',
            'status': 'active',
            'description': 'Fiber patch panel for storage connections'
        })

        for port in range(1, 25):
            patch_panel_interfaces.append({
                'device': pp_name,
                'name': f'Port-{port}',
                'type': 'lc',
                'enabled': 'true',
                'description': f'Fiber port {port}'
            })

    # MMR - Copper patch panel for management
    # MMR-R01: MMR-SW01 at 1 (1U) → Place PP at 10 (well clear of switch)
    print("  - Meet-Me Room: Copper patch panel")
    rack = f'{site}-MMR-R01'
    pp_name = f'{site}-MMR-R01-CPP01'

    patch_panels.append({
        'name': pp_name,
        'manufacturer': 'Generic',
        'device_type': 'Copper Patch Panel 48-Port',
        'role': 'Patch Panel',
        'site': site,
        'location': f'{site}-Meet-Me Room',
        'rack': rack,
        'position': '10',  # Safe position well clear of switch at U1
        'face': 'front',
        'status': 'active',
        'description': 'Copper patch panel for management'
    })

    for port in range(1, 49):
        patch_panel_interfaces.append({
            'device': pp_name,
            'name': f'Port-{port}',
            'type': 'other',
            'enabled': 'true',
            'description': f'Copper port {port}'
        })

print(f"\n✅ Generated {len(patch_panels)} patch panels")
print(f"✅ Generated {len(patch_panel_interfaces)} patch panel interfaces")

# Write patch panels CSV
pp_file = 'lab/netbox_dc_patch_panels.csv'
with open(pp_file, 'w', newline='') as f:
    fieldnames = ['name', 'manufacturer', 'device_type', 'role', 'site', 'location',
                  'rack', 'position', 'face', 'status', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(patch_panels)

print(f"✅ Patch panels written to {pp_file}")

# Write patch panel interfaces CSV
ppi_file = 'lab/netbox_dc_patch_panel_interfaces.csv'
with open(ppi_file, 'w', newline='') as f:
    fieldnames = ['device', 'name', 'type', 'enabled', 'description']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(patch_panel_interfaces)

print(f"✅ Patch panel interfaces written to {ppi_file}")

# Summary
print("\n📊 Summary:")
print(f"  Network Core racks: 4 × 48-port fiber PP per DC = 24 total")
print(f"  Spine racks: 4 × 48-port fiber PP per DC = 24 total")
print(f"  Leaf racks: 4 × 48-port fiber PP per DC = 24 total")
print(f"  Server racks: 12 × 24-port fiber PP per DC = 72 total")
print(f"  Storage racks: 3 × 24-port fiber PP per DC = 18 total")
print(f"  MMR racks: 1 × 48-port copper PP per DC = 6 total")
print(f"  Grand Total: {len(patch_panels)} patch panels across 6 DCs")
