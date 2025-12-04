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
- 2,688 equipment cables (interface → rearport)
- 348 patch cords (frontport → frontport)
**Note**: All devices and ports must exist before importing cables

---

## Verification Checklist

After importing, verify in NetBox:

✅ **Manufacturers**: "Generic" exists
✅ **Device Roles**: "Patch Panel" exists
✅ **Device Types**: 4 patch panel types exist under Generic manufacturer
✅ **Devices**: 168 patch panels visible in device list
✅ **Rear Ports**: Each patch panel has rear ports (check any patch panel)
✅ **Front Ports**: Each patch panel has front ports mapped to rear ports

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

| File | Records | Purpose |
|------|---------|---------|
| netbox_manufacturers.csv | 1 new | Adds "Generic" manufacturer |
| netbox_device_roles.csv | 1 new | Adds "Patch Panel" role |
| netbox_patchpanel_device_types.csv | 4 | Patch panel device types |
| netbox_dc_patch_panels.csv | 168 | Patch panel devices |
| netbox_dc_patch_panel_rear_ports.csv | 5,904 | Rear ports (permanent) |
| netbox_dc_patch_panel_front_ports.csv | 5,904 | Front ports (patch cords) |

**Total**: 11,981 objects to import for complete patch panel infrastructure
