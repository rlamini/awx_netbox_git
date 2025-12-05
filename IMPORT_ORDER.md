# NetBox Import Order - Complete Guide

## Prerequisites (Must be imported first)

These provide the foundation data that patch panels depend on:

### 1. **Manufacturers**
```
Organization → Manufacturers → Import
File: lab/netbox_manufacturers.csv
```
**Why**: Patch panels use manufacturer "Generic"

### 2. **Device Roles**
```
Devices → Device Roles → Import
File: lab/netbox_device_roles.csv
```
**Why**: Patch panels use role "Patch Panel"

### 3. **Sites** (if not already imported)
```
Organization → Sites → Import
File: lab/netbox_sites.csv
```
**Why**: Patch panels are assigned to sites

### 4. **Locations** (if not already imported)
```
DCIM → Locations → Import
File: lab/netbox_locations.csv
```
**Why**: Patch panels are assigned to locations

### 5. **Racks** (if not already imported)
```
DCIM → Racks → Import
File: lab/netbox_racks.csv
```
**Why**: Patch panels are mounted in racks

---

## Patch Panel Import Sequence

### 6. **Patch Panel Device Types**
```
Devices → Device Types → Import
File: lab/netbox_patchpanel_device_types.csv
```
**Contains**:
- Fiber Patch Panel 24-Port (1U)
- Fiber Patch Panel 48-Port (2U)
- Copper Patch Panel 24-Port (1U)
- Copper Patch Panel 48-Port (1U)

### 7. **Patch Panel Devices**
```
Devices → Devices → Import
File: lab/netbox_dc_patch_panels.csv
```
**Contains**: 168 patch panel devices across 6 DCs

### 8. **Rear Ports** (BEFORE Front Ports!)
```
Devices → Rear Ports → Import
File: lab/netbox_dc_patch_panel_rear_ports.csv
```
**Contains**: 5,904 rear ports (permanent cabling side)

### 9. **Front Ports** (AFTER Rear Ports!)
```
Devices → Front Ports → Import
File: lab/netbox_dc_patch_panel_front_ports.csv
```
**Contains**: 5,904 front ports (patch cord side)
**Note**: Front ports reference rear ports, so rear ports must exist first

### 10. **Cables** (AFTER all devices and ports!)
```
DCIM → Cables → Import
File: lab/netbox_dc_cables.csv
```
**Contains**: 3,036 cables with proper terminations
- 2,688 equipment cables (interface → frontport) - Equipment connections
- 348 horizontal cables (rearport → rearport) - Permanent backbone cabling
**Note**: All devices and ports must exist before importing cables

**Cabling Model**:
- **Front Ports**: Equipment connections (switches, servers) via patch cords
- **Rear Ports**: Permanent horizontal/backbone cables between patch panels

---

## Power Infrastructure Import Sequence

### 11. **PDU Device Types**
```
Devices → Device Types → Import
File: lab/power/netbox_pdu_device_types.csv
```
**Contains**: 2 PDU device types
- APC AP8959EU3: Metered Plus ZeroU 32A (24x C13 outlets)
- APC AP8981: Switched Plus ZeroU 32A (24x C13 outlets)

### 12. **PDU Devices**
```
Devices → Devices → Import
File: lab/power/netbox_dc_pdus.csv
```
**Contains**: 252 PDUs (2 per rack: PDU-A and PDU-B)
**Note**: Provides redundant power feeds for all devices

### 13. **Power Outlets**
```
Devices → Power Outlets → Import
File: lab/power/netbox_dc_power_outlets.csv
```
**Contains**: 6,048 power outlets (24 C13 outlets per PDU)
**Note**: PDU devices must exist before importing outlets

### 14. **Power Ports**
```
Devices → Power Ports → Import
File: lab/power/netbox_dc_power_ports.csv
```
**Contains**: 468 power ports on devices (PSU1 and PSU2)
**Note**: All devices have dual power supplies for redundancy

### 15. **Power Cables** (AFTER all power ports and outlets!)
```
DCIM → Cables → Import
File: lab/power/netbox_dc_power_cables.csv
```
**Contains**: 468 power cables
- PSU1 connects to PDU-A for each device
- PSU2 connects to PDU-B for each device
**Note**: Provides redundant power - if one PDU/feed fails, device stays online

**Power Redundancy Model**:
- **PDU-A**: Primary power feed (Metered for monitoring)
- **PDU-B**: Secondary power feed (Switched for remote control)
- **Each Device**: Dual PSUs for N+1 redundancy

---

## Verification Checklist

After importing, verify in NetBox:

### Network/Cabling Verification
✅ **Manufacturers**: "Generic" and "APC by Schneider Electric" exist
✅ **Device Roles**: "Patch Panel" and "PDU" exist
✅ **Device Types**: 4 patch panel types + 2 PDU types exist
✅ **Devices**: 168 patch panels + 252 PDUs visible in device list
✅ **Rear Ports**: Each patch panel has rear ports (check any patch panel)
✅ **Front Ports**: Each patch panel has front ports mapped to rear ports
✅ **Cables**: 3,036 network cables connecting devices through patch panels

### Power Infrastructure Verification
✅ **PDUs**: Each rack has 2 PDUs (PDU-A and PDU-B)
✅ **Power Outlets**: Each PDU has 24 outlets (C13 type)
✅ **Power Ports**: Each device has 2 power ports (PSU1 and PSU2)
✅ **Power Cables**: 468 power cables (redundant connections)
✅ **Redundancy**: Check any device - PSU1→PDU-A, PSU2→PDU-B

---

## Common Import Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "manufacturer: Object not found: Generic" | Generic manufacturer missing | Import netbox_manufacturers.csv first |
| "role: Object not found: Patch Panel" | Role missing | Import netbox_device_roles.csv first |
| "device_type: Object not found" | Device type missing | Import netbox_patchpanel_device_types.csv first |
| "position: U## is already occupied" | Rack position conflict | Already fixed - reimport netbox_dc_patch_panels.csv |
| "rear_port: Object not found" | Front ports before rear | Import rear ports before front ports |

---

## File Summary

### Network/Cabling Files
| File | Records | Purpose |
|------|---------|---------|
| netbox_manufacturers.csv | 2 new | "Generic" + "APC by Schneider Electric" |
| netbox_device_roles.csv | 2 new | "Patch Panel" + "PDU" roles |
| netbox_patchpanel_device_types.csv | 4 | Patch panel device types |
| netbox_dc_patch_panels.csv | 168 | Patch panel devices |
| netbox_dc_patch_panel_rear_ports.csv | 5,904 | Rear ports (permanent cabling) |
| netbox_dc_patch_panel_front_ports.csv | 5,904 | Front ports (patch cords) |
| netbox_dc_cables.csv | 3,036 | Network cables |

### Power Infrastructure Files
| File | Records | Purpose |
|------|---------|---------|
| netbox_pdu_device_types.csv | 2 | PDU device types (Metered/Switched) |
| netbox_dc_pdus.csv | 252 | PDU devices (2 per rack) |
| netbox_dc_power_outlets.csv | 6,048 | Power outlets (24 per PDU) |
| netbox_dc_power_ports.csv | 468 | Power ports (dual PSU per device) |
| netbox_dc_power_cables.csv | 468 | Power cables (redundant connections) |

**Total**: 22,254 objects for complete datacenter DCIM infrastructure
- Network/Cabling: 15,016 objects
- Power Infrastructure: 7,238 objects
