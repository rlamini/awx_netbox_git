# NetBox Config Contexts

This directory contains hierarchical config contexts for network devices.

## Context Hierarchy (by weight/priority)

1. **Global Context** (weight: 1000) - Applied to all devices
2. **Platform Contexts** (weight: 2000) - Applied by platform (NX-OS, IOS-XE, IOS-XR, IOS)
3. **Site Context** (weight: 3000) - Applied by site (EMEA-DC-ONPREM)
4. **Role Contexts** (weight: 4000) - Applied by device role

## Files

### JSON Context Files
- `global_context.json` - Global configuration (logging, AAA, etc.)
- `emea_dc_onprem_context.json` - EMEA DC ONPREM site configuration
- `platform_nxos_context.json` - Cisco NX-OS platform defaults
- `platform_iosxe_context.json` - Cisco IOS-XE platform defaults
- `platform_iosxr_context.json` - Cisco IOS-XR platform defaults
- `platform_ios_context.json` - Cisco IOS platform defaults
- `role_core_switch_context.json` - Core switch role configuration
- `role_distribution_switch_context.json` - Distribution switch configuration
- `role_access_switch_context.json` - Access switch configuration
- `role_router_context.json` - Router configuration
- `role_oob_router_context.json` - OOB router configuration

### Generated Files
- `netbox_config_contexts.csv` - CSV export for NetBox import

## Import to NetBox

### Method 1: CSV Import (UI)
1. Navigate to **Customization → Config Contexts**
2. Click **Import**
3. Upload `netbox_config_contexts.csv`
4. Map fields and import

### Method 2: Manual Creation (UI)
1. Navigate to **Customization → Config Contexts**
2. Click **Add**
3. Copy JSON from files above
4. Set weight and assignments
5. Save

### Method 3: API (Recommended for automation)
See parent directory's `generate_config_contexts.py` script

## Testing Context Merge

To test how contexts merge for a specific device:

1. Go to device page (e.g., EMEA-DC-ONPREM-CORE-SW01)
2. Click **Config Context** tab
3. View merged JSON data

Example merged context for **EMEA-DC-ONPREM-CORE-SW01**:
- Global context (base settings)
- + NX-OS platform context (features, VTP, spanning-tree)
- + EMEA-DC-ONPREM site context (NTP, DNS, SNMP)
- + Core Switch role context (HSRP, routing, VLANs)
- = Final merged context

## Modifying Contexts

1. Edit the JSON files in this directory
2. Regenerate CSV: `python3 ../generate_config_contexts.py`
3. Re-import to NetBox or update via API

## Version Control

All context files are tracked in Git. When making changes:
1. Edit JSON files
2. Test in NetBox
3. Commit changes with descriptive message
