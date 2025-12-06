# NetBox to Zabbix Synchronization
## Automated Device Monitoring Integration

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Device Mapping](#device-mapping)
4. [Zabbix Configuration](#zabbix-configuration)
5. [Synchronization Process](#synchronization-process)
6. [Templates and Host Groups](#templates-and-host-groups)
7. [Installation and Setup](#installation-and-setup)
8. [Usage](#usage)
9. [Troubleshooting](#troubleshooting)

---

## Overview

### What is NetBox to Zabbix Sync?

This integration automatically synchronizes network devices from NetBox (Source of Truth) to Zabbix (Monitoring System).

**Benefits:**
- ✅ **Single Source of Truth**: NetBox is the authoritative source for device inventory
- ✅ **Automated Monitoring**: New devices in NetBox are automatically added to Zabbix
- ✅ **Consistent Naming**: Device names, IPs, and metadata stay synchronized
- ✅ **Template Mapping**: Devices get appropriate Zabbix templates based on role/platform
- ✅ **Host Groups**: Devices are organized by site, role, and platform
- ✅ **Reduced Manual Work**: No more manual host creation in Zabbix

### How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                         NetBox (Source)                          │
│  - Device inventory (name, IP, site, role, platform)            │
│  - Primary IP addresses                                          │
│  - Custom fields and tags                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ API Query
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Sync Script (Python)                          │
│  - Fetch devices from NetBox API                                │
│  - Map devices to Zabbix templates                              │
│  - Create/update hosts in Zabbix                                │
│  - Assign host groups and templates                             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ API Create/Update
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Zabbix (Target)                             │
│  - Hosts (monitored devices)                                     │
│  - Host groups (organization)                                    │
│  - Templates (monitoring configuration)                          │
│  - Items, Triggers, Graphs                                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## Architecture

### Components

1. **NetBox API**
   - Provides device inventory via REST API
   - Includes: name, primary IP, site, role, platform, device type, tags, status

2. **Sync Script** (`sync_netbox_to_zabbix.py`)
   - Python script using `pynetbox` and `pyzabbix` libraries
   - Fetches devices from NetBox
   - Creates/updates hosts in Zabbix
   - Handles mapping and error handling

3. **Mapping Configuration** (`zabbix_mapping.yaml`)
   - Maps NetBox roles → Zabbix templates
   - Maps NetBox platforms → Zabbix templates
   - Maps NetBox sites → Zabbix host groups
   - Customizable per environment

4. **Zabbix API**
   - Receives host creation/update requests
   - Manages hosts, host groups, and template assignments

### Data Flow

```
Step 1: Fetch Devices from NetBox
┌────────────────────────────────────────┐
│ NetBox API Query                       │
│ GET /api/dcim/devices/                 │
│   ?status=active                       │
│   &site=EMEA-DC-ONPREM                 │
└────────────────┬───────────────────────┘
                 │
                 ▼
Step 2: Transform Data
┌────────────────────────────────────────┐
│ Device Transformation                  │
│ - Extract: name, IP, site, role        │
│ - Map role → template                  │
│ - Map site → host group                │
│ - Prepare Zabbix host object           │
└────────────────┬───────────────────────┘
                 │
                 ▼
Step 3: Check if Host Exists in Zabbix
┌────────────────────────────────────────┐
│ Zabbix API Query                       │
│ host.get(filter={host: device_name})   │
└────────────────┬───────────────────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
     Exists          Not Exists
         │                │
         │                ▼
         │      ┌─────────────────────┐
         │      │ Create New Host     │
         │      │ host.create()       │
         │      └─────────┬───────────┘
         │                │
         ▼                ▼
┌────────────────────────────────────────┐
│ Update Host                            │
│ - Update IP address                    │
│ - Update host groups                   │
│ - Update templates                     │
│ - Update macros                        │
└────────────────────────────────────────┘
```

---

## Device Mapping

### NetBox Device Attributes

Each device in NetBox has:

| Attribute | Example | Use in Zabbix |
|-----------|---------|---------------|
| **name** | EMEA-DC-ONPREM-CORE-SW01 | Zabbix hostname |
| **primary_ip4** | 10.10.100.1/24 | Zabbix host IP (interface) |
| **site.name** | EMEA-DC-ONPREM | Zabbix host group |
| **role.name** | Core Switch | Template selection |
| **platform.name** | NX-OS | Template selection |
| **device_type.model** | Nexus 9508 | Host inventory field |
| **status** | active | Only sync active devices |
| **tags** | production, critical | Additional host groups |

### Mapping Rules

#### 1. Hostname Mapping

**NetBox** → **Zabbix**
```
EMEA-DC-ONPREM-CORE-SW01 → EMEA-DC-ONPREM-CORE-SW01
```

**Rules:**
- Use exact device name from NetBox
- No modifications or transformations
- Zabbix hostname = NetBox device name

#### 2. IP Address Mapping

**NetBox** → **Zabbix**
```
Primary IP: 10.10.100.1/24 → Zabbix Interface IP: 10.10.100.1
```

**Rules:**
- Use NetBox primary_ip4 (strip CIDR mask)
- If no primary IP: skip device (log warning)
- Interface type: Agent (Zabbix agent) or SNMP (based on monitoring method)

#### 3. Host Group Mapping (Hierarchical)

**Structure:**
```
All Devices
├── Site: EMEA-DC-ONPREM
│   ├── Role: Core Switch
│   ├── Role: Distribution Switch
│   ├── Role: Access Switch
│   └── Role: Router
├── Site: APAC-DC-ONPREM
│   └── ...
├── Platform: Cisco NX-OS
├── Platform: Cisco IOS-XE
└── Tags
    ├── production
    └── critical
```

**Host Group Assignment:**

Each device gets assigned to multiple host groups:

1. **"All Devices"** - Global group
2. **"Site: {site_name}"** - Site-based group
3. **"Role: {role_name}"** - Role-based group
4. **"Platform: {platform_name}"** - Platform-based group
5. **"Tag: {tag_name}"** - Tag-based groups (if tagged)

**Example for EMEA-DC-ONPREM-CORE-SW01**:
```
Host Groups:
- All Devices
- Site: EMEA-DC-ONPREM
- Role: Core Switch
- Platform: Cisco NX-OS
```

#### 4. Template Mapping (Priority Order)

**Mapping Priority (highest to lowest):**

1. **Device Type Specific** (most specific)
   - `Nexus 9508` → Template: "Template Cisco Nexus 9508"

2. **Platform + Role Combination**
   - `NX-OS` + `Core Switch` → Template: "Template Cisco NX-OS Core Switch"

3. **Platform Specific**
   - `NX-OS` → Template: "Template Cisco NX-OS"

4. **Role Specific**
   - `Core Switch` → Template: "Template Network Core Switch"

5. **Manufacturer Default**
   - `Cisco Systems` → Template: "Template Cisco Generic"

6. **Generic Fallback** (least specific)
   - Default → Template: "Template Network Device"

**Mapping Table for EMEA-DC-ONPREM Devices:**

| Device Name | Device Type | Platform | Role | Zabbix Template |
|-------------|-------------|----------|------|-----------------|
| EMEA-DC-ONPREM-CORE-SW01 | Nexus 9508 | NX-OS | Core Switch | Template Cisco Nexus 9000 |
| EMEA-DC-ONPREM-CORE-SW02 | Nexus 9508 | NX-OS | Core Switch | Template Cisco Nexus 9000 |
| EMEA-DC-ONPREM-DIST-SW01 | Nexus 93180YC-FX | NX-OS | Distribution Switch | Template Cisco Nexus 9000 |
| EMEA-DC-ONPREM-DIST-SW02 | Nexus 93180YC-FX | NX-OS | Distribution Switch | Template Cisco Nexus 9000 |
| EMEA-DC-ONPREM-ACC-STG-01 | Catalyst 9300-48P | IOS-XE | Access Switch | Template Cisco Catalyst IOS-XE |
| EMEA-DC-ONPREM-ACC-STG-02 | Catalyst 9300-48P | IOS-XE | Access Switch | Template Cisco Catalyst IOS-XE |
| EMEA-DC-ONPREM-MMR-SW01 | Catalyst 9300-48P | IOS-XE | Access Switch | Template Cisco Catalyst IOS-XE |
| EMEA-DC-ONPREM-RTR-EDGE-01 | ASR 9001 | IOS-XR | Router | Template Cisco IOS-XR |
| EMEA-DC-ONPREM-RTR-EDGE-02 | ASR 9001 | IOS-XR | Router | Template Cisco IOS-XR |
| EMEA-DC-ONPREM-OOB-RTR01 | ISR 4431 | IOS | OOB Router | Template Cisco IOS |

---

## Zabbix Configuration

### Required Zabbix Templates

Before running sync, ensure these templates exist in Zabbix:

#### Cisco Templates

1. **Template Cisco Nexus 9000** (for NX-OS devices)
   - SNMP monitoring
   - CPU, Memory, Temperature
   - Interface statistics (counters, errors, utilization)
   - BGP, OSPF neighbor monitoring
   - Fan status, power supply status

2. **Template Cisco Catalyst IOS-XE** (for Catalyst switches)
   - SNMP monitoring
   - CPU, Memory
   - Interface statistics
   - PoE monitoring
   - Stack member status

3. **Template Cisco IOS-XR** (for ASR routers)
   - SNMP monitoring
   - CPU, Memory per route processor
   - Interface statistics
   - BGP, OSPF, ISIS monitoring
   - MPLS monitoring

4. **Template Cisco IOS** (for ISR routers)
   - SNMP monitoring
   - CPU, Memory
   - Interface statistics
   - IPSec VPN tunnels

#### Generic Templates

5. **Template Network Device** (fallback)
   - Basic ICMP ping
   - SNMP availability
   - Basic interface monitoring

### Zabbix Host Groups

Create these host groups manually or let the script auto-create:

```
Host Groups:
├── All Devices
├── Site: EMEA-DC-ONPREM
├── Site: EMEA-DC-CLOUD
├── Site: APAC-DC-ONPREM
├── Site: APAC-DC-CLOUD
├── Site: AMER-DC-ONPREM
├── Site: AMER-DC-CLOUD
├── Role: Core Switch
├── Role: Distribution Switch
├── Role: Access Switch
├── Role: Router
├── Role: Firewall
├── Role: Load Balancer
├── Platform: Cisco NX-OS
├── Platform: Cisco IOS-XE
├── Platform: Cisco IOS-XR
├── Platform: Cisco IOS
├── Platform: Arista EOS
├── Platform: Palo Alto PAN-OS
└── Platform: F5 TMOS
```

### Zabbix Macros

The script sets these host-level macros:

| Macro | Source | Example | Purpose |
|-------|--------|---------|---------|
| {$SNMP_COMMUNITY} | Config | "public" | SNMP v2c community string |
| {$NETBOX_SITE} | NetBox site.name | "EMEA-DC-ONPREM" | Reference to NetBox site |
| {$NETBOX_ROLE} | NetBox role.name | "Core Switch" | Reference to NetBox role |
| {$NETBOX_DEVICE_ID} | NetBox device.id | "42" | Link back to NetBox |
| {$NETBOX_URL} | Config | "https://netbox..." | NetBox instance URL |

---

## Synchronization Process

### Sync Modes

#### 1. Full Sync (Default)

Synchronizes ALL active devices from NetBox to Zabbix.

```bash
python3 sync_netbox_to_zabbix.py --mode full
```

**Process:**
1. Fetch all active devices from NetBox
2. For each device:
   - Check if exists in Zabbix
   - Create if new, update if exists
   - Assign templates and host groups
3. Report: X devices created, Y devices updated, Z errors

#### 2. Site-Specific Sync

Synchronizes devices from a specific site only.

```bash
python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"
```

**Process:**
1. Fetch devices from specified site
2. Sync only those devices
3. Useful for testing or incremental rollout

#### 3. Dry Run (Test Mode)

Shows what WOULD happen without making changes.

```bash
python3 sync_netbox_to_zabbix.py --dry-run
```

**Process:**
1. Fetch devices from NetBox
2. Display planned actions (create/update)
3. NO actual changes to Zabbix
4. Useful for validation before actual sync

#### 4. Incremental Sync

Only syncs devices added/modified since last sync.

```bash
python3 sync_netbox_to_zabbix.py --mode incremental
```

**Process:**
1. Check last sync timestamp (stored in file)
2. Fetch only devices modified after last sync
3. Sync those devices
4. Update timestamp

### Sync Workflow

```
START
  │
  ├─→ Load Configuration (zabbix_mapping.yaml)
  │
  ├─→ Connect to NetBox API
  │
  ├─→ Connect to Zabbix API
  │
  ├─→ Fetch Devices from NetBox
  │     └─→ Filter: status=active
  │
  ├─→ For Each Device:
  │     │
  │     ├─→ Validate (has primary IP?)
  │     │     └─→ NO: Skip device, log warning
  │     │     └─→ YES: Continue
  │     │
  │     ├─→ Map to Zabbix Template (mapping rules)
  │     │
  │     ├─→ Check if Host Exists in Zabbix
  │     │     ├─→ EXISTS: Update host
  │     │     └─→ NOT EXISTS: Create host
  │     │
  │     ├─→ Assign Host Groups
  │     │     ├─→ Create host groups if missing
  │     │     └─→ Link host to groups
  │     │
  │     ├─→ Assign Templates
  │     │     └─→ Link templates to host
  │     │
  │     ├─→ Set Host Macros
  │     │     └─→ {$NETBOX_SITE}, {$NETBOX_ROLE}, etc.
  │     │
  │     └─→ Create/Update Zabbix Interface
  │           └─→ Type: SNMP, IP: primary_ip4, Port: 161
  │
  ├─→ Generate Sync Report
  │     ├─→ Devices created: X
  │     ├─→ Devices updated: Y
  │     ├─→ Devices skipped: Z
  │     └─→ Errors: N
  │
  └─→ END
```

---

## Templates and Host Groups

### Template Assignment Logic

**Example: EMEA-DC-ONPREM-CORE-SW01**

```python
Device attributes:
- name: "EMEA-DC-ONPREM-CORE-SW01"
- device_type: "Nexus 9508"
- platform: "NX-OS"
- role: "Core Switch"
- manufacturer: "Cisco Systems"

Template selection process:
1. Check mapping.yaml for device_type "Nexus 9508"
   → Found: "Template Cisco Nexus 9000" ✅ USE THIS

If not found:
2. Check mapping.yaml for platform "NX-OS" + role "Core Switch"
   → Would use combination template if exists

If not found:
3. Check mapping.yaml for platform "NX-OS"
   → Would use: "Template Cisco NX-OS"

If not found:
4. Check mapping.yaml for role "Core Switch"
   → Would use: "Template Network Core Switch"

If not found:
5. Use manufacturer default "Cisco Systems"
   → Would use: "Template Cisco Generic"

If not found:
6. Use global default
   → Would use: "Template Network Device"
```

**Result:** Template "Template Cisco Nexus 9000" assigned

### Host Group Auto-Creation

If a host group doesn't exist in Zabbix, the script will:

1. Create the host group
2. Add it to the host
3. Log the creation

**Example:**
```
[INFO] Host group 'Site: EMEA-DC-ONPREM' not found
[INFO] Creating host group 'Site: EMEA-DC-ONPREM'
[INFO] Host group created successfully (ID: 42)
```

---

## Installation and Setup

### Prerequisites

1. **Python 3.8+**
2. **Python Libraries:**
   ```bash
   pip3 install pynetbox pyzabbix pyyaml requests
   ```

3. **NetBox Access:**
   - NetBox URL
   - API Token (read-only sufficient)

4. **Zabbix Access:**
   - Zabbix URL
   - Admin user credentials (need host creation permissions)

5. **Network Connectivity:**
   - Script can reach NetBox API (HTTPS)
   - Script can reach Zabbix API (HTTPS)
   - Zabbix can reach monitored devices (SNMP)

### Step 1: Install Dependencies

```bash
# Install Python libraries
pip3 install pynetbox pyzabbix pyyaml requests

# Verify installation
python3 -c "import pynetbox, pyzabbix, yaml; print('OK')"
```

### Step 2: Configure Credentials

Create `.env` file or export environment variables:

```bash
# NetBox Configuration
export NETBOX_URL="https://netbox.acme.com"
export NETBOX_TOKEN="your-netbox-api-token-here"

# Zabbix Configuration
export ZABBIX_URL="https://zabbix.acme.com"
export ZABBIX_USER="admin"
export ZABBIX_PASSWORD="zabbix"

# SNMP Community (for SNMP monitoring)
export SNMP_COMMUNITY="public"
```

Or create `config.yaml`:

```yaml
netbox:
  url: "https://netbox.acme.com"
  token: "your-netbox-api-token"
  verify_ssl: true

zabbix:
  url: "https://zabbix.acme.com"
  user: "admin"
  password: "zabbix"
  verify_ssl: true

monitoring:
  snmp_community: "public"
  snmp_port: 161
  default_interface_type: "snmp"  # snmp or agent
```

### Step 3: Configure Template Mapping

Edit `lab/zabbix/zabbix_mapping.yaml` (created by script):

```yaml
# See next section for full example
```

### Step 4: Test Connection

```bash
# Test NetBox connection
python3 -c "import pynetbox; nb = pynetbox.api('https://netbox.acme.com', token='your-token'); print(len(list(nb.dcim.devices.all())))"

# Test Zabbix connection
python3 sync_netbox_to_zabbix.py --test-connection
```

### Step 5: Dry Run

```bash
# See what would happen without making changes
python3 sync_netbox_to_zabbix.py --dry-run --site "EMEA-DC-ONPREM"
```

### Step 6: First Sync

```bash
# Sync devices from one site
python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"

# Review results in Zabbix UI

# If good, sync all sites
python3 sync_netbox_to_zabbix.py --mode full
```

---

## Usage

### Command Line Options

```bash
python3 sync_netbox_to_zabbix.py [OPTIONS]

Options:
  --mode MODE          Sync mode: full, site, incremental (default: full)
  --site SITE          Site name for site-specific sync
  --dry-run            Show planned changes without executing
  --verbose, -v        Verbose output
  --config FILE        Config file path (default: config.yaml)
  --mapping FILE       Mapping file path (default: zabbix_mapping.yaml)
  --test-connection    Test API connections and exit
  --help, -h           Show help message
```

### Usage Examples

**Example 1: Full sync with verbose output**
```bash
python3 sync_netbox_to_zabbix.py --mode full --verbose
```

**Example 2: Sync specific site**
```bash
python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"
```

**Example 3: Dry run to preview changes**
```bash
python3 sync_netbox_to_zabbix.py --dry-run
```

**Example 4: Incremental sync (only changed devices)**
```bash
python3 sync_netbox_to_zabbix.py --mode incremental
```

**Example 5: Test connections**
```bash
python3 sync_netbox_to_zabbix.py --test-connection
```

### Scheduled Synchronization

**Option 1: Cron Job (Linux)**

```bash
# Edit crontab
crontab -e

# Add sync every 6 hours
0 */6 * * * /usr/bin/python3 /path/to/sync_netbox_to_zabbix.py --mode incremental >> /var/log/netbox_zabbix_sync.log 2>&1
```

**Option 2: Systemd Timer (Linux)**

Create `/etc/systemd/system/netbox-zabbix-sync.service`:
```ini
[Unit]
Description=NetBox to Zabbix Sync
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 /opt/netbox-zabbix-sync/sync_netbox_to_zabbix.py --mode incremental
User=zabbix
Group=zabbix
```

Create `/etc/systemd/system/netbox-zabbix-sync.timer`:
```ini
[Unit]
Description=Run NetBox to Zabbix sync every 6 hours

[Timer]
OnBootSec=15min
OnUnitActiveSec=6h

[Install]
WantedBy=timers.target
```

Enable timer:
```bash
systemctl enable netbox-zabbix-sync.timer
systemctl start netbox-zabbix-sync.timer
```

**Option 3: AWX/Ansible Tower**

Create AWX job template that runs the sync script on schedule.

---

## Troubleshooting

### Problem 1: Connection to NetBox Fails

**Symptom:**
```
Error: Failed to connect to NetBox API
```

**Checks:**
1. ✅ NetBox URL correct? (include https://)
2. ✅ API token valid?
3. ✅ Network connectivity? `curl https://netbox.acme.com/api/`
4. ✅ SSL certificate valid? (or set verify_ssl: false for testing)

**Solution:**
```bash
# Test manually
curl -H "Authorization: Token your-token" https://netbox.acme.com/api/dcim/devices/
```

### Problem 2: Connection to Zabbix Fails

**Symptom:**
```
Error: Zabbix API authentication failed
```

**Checks:**
1. ✅ Zabbix URL correct? (include /api_jsonrpc.php)
2. ✅ Username/password correct?
3. ✅ User has API access enabled?
4. ✅ User has permissions to create hosts?

**Solution:**
```bash
# Test API access
curl -X POST -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"user.login","params":{"user":"admin","password":"zabbix"},"id":1}' \
  https://zabbix.acme.com/api_jsonrpc.php
```

### Problem 3: Template Not Found

**Symptom:**
```
Warning: Template 'Template Cisco Nexus 9000' not found in Zabbix
```

**Solution:**
1. Import template to Zabbix
2. Or update mapping.yaml to use existing template
3. Or remove template requirement (fallback to default)

### Problem 4: Device Has No Primary IP

**Symptom:**
```
Warning: Device EMEA-DC-ONPREM-CORE-SW01 has no primary IP, skipping
```

**Solution:**
1. Assign primary IPv4 address in NetBox
2. Re-run sync

### Problem 5: Duplicate Hosts

**Symptom:**
Multiple hosts with same name in Zabbix

**Cause:**
Script ran multiple times before completion

**Solution:**
```bash
# Delete duplicates in Zabbix UI
# Or use Zabbix API to find and delete:
python3 sync_netbox_to_zabbix.py --cleanup-duplicates
```

### Problem 6: SNMP Monitoring Not Working

**Symptom:**
Zabbix shows "SNMP agent unreachable"

**Checks:**
1. ✅ Device has SNMP enabled?
2. ✅ SNMP community correct?
3. ✅ Firewall allows SNMP (UDP 161) from Zabbix?
4. ✅ Zabbix can reach device IP?

**Solution:**
```bash
# Test SNMP from Zabbix server
snmpwalk -v2c -c public 10.10.100.1 sysDescr
```

---

## Benefits Summary

✅ **Automation**: No manual host creation in Zabbix
✅ **Consistency**: NetBox is single source of truth
✅ **Scalability**: Easily add hundreds of devices
✅ **Accuracy**: No typos or manual errors
✅ **Flexibility**: Customizable mapping rules
✅ **Integration**: Works with existing NetBox and Zabbix setups
✅ **Monitoring**: Automatic template assignment based on device type
✅ **Organization**: Auto-created host groups by site/role/platform

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure credentials
3. ✅ Import Zabbix templates
4. ✅ Customize mapping.yaml
5. ✅ Run dry-run test
6. ✅ Sync first site
7. ✅ Verify in Zabbix UI
8. ✅ Sync all sites
9. ✅ Schedule automated syncs
10. ✅ Monitor and maintain

---

**Document Version**: 1.0
**Last Updated**: 2025-12-06
**Author**: NetOps Team
