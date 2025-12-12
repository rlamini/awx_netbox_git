# NetBox Advanced Config Contexts - Import Instructions

This directory contains individual JSON files for each advanced config context that can be imported into NetBox one by one.

## Overview

These config contexts provide advanced enterprise features for network device configurations:

1. **Layer 2 Security Features** - DHCP Snooping, ARP Inspection, Port Security, 802.1X
2. **AAA Services** - TACACS+ and RADIUS with regional server allocation
3. **Regional Services** - NTP, DNS, DHCP, SNMP, Syslog, NetFlow with regional routing
4. **VLAN Configuration** - Default VLAN definitions (optional)

## Files and Import Order

Import these config contexts in NetBox in the following order:

### 1. Layer 2 Security Features
**File:** `1_advanced_layer2_security.json`
**Weight:** `5000`
**Name:** `Advanced Layer 2 Security Features`
**Description:** `Enterprise Layer 2 security features including DHCP Snooping, Dynamic ARP Inspection, Port Security, and 802.1X NAC`

**Features:**
- DHCP Snooping for VLAN protection
- Dynamic ARP Inspection (DAI) for ARP spoofing prevention
- Port Security with MAC address limits
- 802.1X Network Access Control with guest/critical VLANs

**Assignment:** Assign to device roles: `access-switch`, `distribution-switch`

---

### 2. AAA Services
**File:** `2_advanced_aaa_services.json`
**Weight:** `5100`
**Name:** `Advanced AAA Services (TACACS+/RADIUS)`
**Description:** `Regional TACACS+ and RADIUS server configuration for authentication and 802.1X`

**Features:**
- TACACS+ servers for management access (per region)
- RADIUS servers for 802.1X authentication (per region)
- Automatic regional server selection based on site name

**Regional Servers:**
- **EMEA:** 10.10.100.x
- **APAC:** 10.20.100.x
- **AMER:** 10.30.100.x

**Assignment:** Assign to all device roles that need AAA

---

### 3. Regional Services
**File:** `3_advanced_regional_services.json`
**Weight:** `5200`
**Name:** `Advanced Regional Infrastructure Services`
**Description:** `Regional infrastructure services (NTP, DNS, DHCP, SNMP, Syslog, NetFlow) with automatic server selection`

**Features:**
- NTP servers (per region)
- DNS servers (per region)
- DHCP relay/helper servers (per region)
- Syslog servers (per region)
- SNMP trap collectors (per region)
- NetFlow collectors (per region)

**Regional Servers:**
- **EMEA:** 10.10.100.x
- **APAC:** 10.20.100.x
- **AMER:** 10.30.100.x

**Assignment:** Assign to all device roles

---

### 4. VLAN Configuration (Optional)
**File:** `4_advanced_vlan_config.json`
**Weight:** `5500`
**Name:** `Advanced VLAN Configuration`
**Description:** `Default VLAN definitions for voice, management, and 802.1X special VLANs`

**Features:**
- Voice VLAN (210)
- Management VLAN (100)
- 802.1X special VLANs (997, 998, 999)
- Standard VLANs (USERS, SERVERS, GUEST, etc.)

**Assignment:** Assign to access switches or specific sites (optional)

---

## How to Import in NetBox

### Step 1: Access Config Contexts
1. Navigate to: **Organization → Config Contexts**
2. Click: **+ Add**

### Step 2: Create Each Config Context
For each file, follow these steps:

#### Basic Information
- **Name:** Use the name specified above
- **Weight:** Use the weight specified above (5000, 5100, 5200, 5500)
- **Description:** Use the description specified above
- **Is Active:** ✅ Check this box

#### Assignment
Assign the config context to appropriate:
- **Regions:** Select EMEA, APAC, AMER (or specific regions)
- **Site Groups:** Select your site groups if needed
- **Sites:** Or select specific sites
- **Device Roles:** Select appropriate roles:
  - Layer 2 Security: `access-switch`, `distribution-switch`
  - AAA Services: All network device roles
  - Regional Services: All network device roles
  - VLAN Config: `access-switch` or specific sites

#### Data
- Copy the entire contents of the JSON file
- Paste into the **Data** field
- Ensure valid JSON format

#### Save
- Click **Create** to save the config context

### Step 3: Verify
After importing all contexts:
1. Go to a device (e.g., an access switch)
2. Navigate to the device's detail page
3. Click the **Config Context** tab
4. Verify that the contexts are merged correctly
5. Check that regional variables are properly set based on site name

---

## Regional Server Allocation

The config contexts use automatic regional server selection based on the **site name prefix**:

| Region | Site Prefix | Example Sites | Server Base |
|--------|-------------|---------------|-------------|
| **EMEA** | `emea-*` | emea-london-dc1, emea-paris-dc1 | 10.10.100.x |
| **APAC** | `apac-*` | apac-singapore-dc1, apac-tokyo-dc1 | 10.20.100.x |
| **AMER** | `amer-*` | amer-newyork-dc1, amer-miami-dc1 | 10.30.100.x |

### Server IP Allocation by Service

| Service | EMEA | APAC | AMER |
|---------|------|------|------|
| **TACACS+** | 10.10.100.10-11 | 10.20.100.10-11 | 10.30.100.10-11 |
| **RADIUS (802.1X)** | 10.10.100.20-21 | 10.20.100.20-21 | 10.30.100.20-21 |
| **NTP** | 10.10.100.30-31 | 10.20.100.30-31 | 10.30.100.30-31 |
| **DNS** | 10.10.100.40-41 | 10.20.100.40-41 | 10.30.100.40-41 |
| **DHCP** | 10.10.100.50-51 | 10.20.100.50-51 | 10.30.100.50-51 |
| **Syslog** | 10.10.100.60-61 | 10.20.100.60-61 | 10.30.100.60-61 |
| **SNMP** | 10.10.100.70-71 | 10.20.100.70-71 | 10.30.100.70-71 |
| **NetFlow** | 10.10.100.80 | 10.20.100.80 | 10.30.100.80 |

---

## Customization

### Updating Server IPs
To customize server IPs for your environment:
1. Edit the JSON files with your actual server addresses
2. Maintain the regional structure (emea, apac, amer)
3. Re-import or update the config contexts in NetBox

### Updating Security Settings
To modify security settings (e.g., 802.1X timers, port security limits):
1. Edit `1_advanced_layer2_security.json`
2. Modify the relevant parameters
3. Update the config context in NetBox

### Adding New Regions
To add a new region (e.g., "cala" for Caribbean/Latin America):
1. Add the region key to each services section
2. Define server IPs for the new region
3. Update device site names to use the new prefix (e.g., `cala-bogota-dc1`)

---

## Config Context Weights

The weight system determines merge priority (higher weight = higher priority):

| Weight | Config Context | Priority |
|--------|----------------|----------|
| **1000** | Base Network Settings | Low (base defaults) |
| **2000** | Base Infrastructure Services | Medium-Low |
| **3000** | Site-Specific Settings | Medium |
| **5000** | Advanced Layer 2 Security | High |
| **5100** | Advanced AAA Services | High |
| **5200** | Advanced Regional Services | High |
| **5500** | Advanced VLAN Configuration | Highest |

Advanced contexts (5000+) override base contexts (1000-3000) when both exist.

---

## Testing

After importing all config contexts:

1. **View Merged Context:**
   - Go to a device detail page
   - Click **Config Context** tab
   - Verify all expected variables are present

2. **Render Configuration:**
   - Go to **Config Templates** (if AWX/Ansible Tower configured)
   - Select a device
   - Render the configuration
   - Verify that regional servers are correctly selected
   - Check that security features are properly configured

3. **Test Regional Selection:**
   - Create test devices in different regions
   - Verify each device gets region-appropriate servers
   - Site name pattern: `{region}-{location}-{datacenter}`

---

## Troubleshooting

### Config Context Not Appearing
- **Check Weight:** Ensure weight is set correctly
- **Check Assignment:** Verify device matches assignment criteria (region, site, role)
- **Check Active:** Ensure "Is Active" is checked
- **Check JSON:** Validate JSON syntax is correct

### Wrong Regional Servers
- **Check Site Name:** Site name must start with region prefix (emea-, apac-, amer-)
- **Check Template:** Verify template uses `{% set region = device.site.name.split('-')[0] | lower %}`
- **Check Fallback:** Templates should have fallback to EMEA if region not found

### Template Rendering Errors
- **Check Defensive Coding:** Templates must check if variables exist before using them
- **Check Nested Access:** Always verify parent exists before accessing child (e.g., `aaa.tacacs.servers`)
- **Use Fallbacks:** Use `| default()` filters for optional values

---

## Support

For issues or questions:
- Review the main documentation: `NETBOX_CONFIG_MANAGEMENT.md`
- Check template files in: `lab/config-templates/`
- Verify config context assignment and merge order in NetBox

---

## Summary

✅ **4 config context files ready to import**
✅ **Regional server allocation (EMEA/APAC/AMER)**
✅ **Enterprise security features (802.1X, DHCP Snooping, Port Security, DAI)**
✅ **Compatible with all advanced templates (IOS-XE, NX-OS, IOS, IOS-XR)**
✅ **Defensive programming for error-free rendering**

Import order: **1 → 2 → 3 → 4** with weights **5000 → 5100 → 5200 → 5500**
