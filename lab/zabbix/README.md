# NetBox to Zabbix Integration

This directory contains configuration files for synchronizing NetBox devices to Zabbix monitoring.

## Files

- **zabbix_mapping.yaml** - Template and host group mapping configuration
- **../../sync_netbox_to_zabbix.py** - Main synchronization script
- **../../config.yaml.example** - Example configuration file

## Quick Start

### 1. Install Dependencies

```bash
pip3 install pynetbox pyzabbix pyyaml requests
```

### 2. Configure Credentials

Create `config.yaml` from example:

```bash
cp config.yaml.example config.yaml
```

Edit `config.yaml` and add your NetBox and Zabbix credentials.

### 3. Customize Mapping

Edit `lab/zabbix/zabbix_mapping.yaml` to match your Zabbix templates.

**Important**: Ensure the templates referenced in the mapping file exist in your Zabbix instance!

### 4. Test Connection

```bash
python3 sync_netbox_to_zabbix.py --test-connection
```

### 5. Dry Run

```bash
python3 sync_netbox_to_zabbix.py --dry-run
```

### 6. Sync Devices

```bash
# Sync all devices
python3 sync_netbox_to_zabbix.py --mode full

# Sync specific site
python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"
```

## Template Mapping

The mapping file defines how NetBox devices map to Zabbix templates.

### Priority Order (Highest to Lowest)

1. **Device Type** - Most specific (e.g., "Nexus 9508")
2. **Platform + Role** - Combination (e.g., "NX-OS+Core Switch")
3. **Platform** - Platform only (e.g., "NX-OS")
4. **Role** - Role only (e.g., "Core Switch")
5. **Manufacturer** - Vendor default (e.g., "Cisco Systems")
6. **Default Template** - Fallback (e.g., "Template Net Device SNMP")

### Example Mappings

**Device Type Mapping:**
```yaml
device_type_mapping:
  "Nexus 9508": "Template Cisco Nexus 9000"
  "Catalyst 9300-48P": "Template Cisco Catalyst IOS-XE"
  "ASR 9001": "Template Cisco IOS-XR"
```

**Platform Mapping:**
```yaml
platform_mapping:
  "NX-OS": "Template Cisco NX-OS"
  "IOS-XE": "Template Cisco IOS-XE"
  "IOS-XR": "Template Cisco IOS-XR"
```

**Role Mapping:**
```yaml
role_mapping:
  "Core Switch": "Template Network Core Switch"
  "Access Switch": "Template Network Access Switch"
  "Router": "Template Network Router"
```

## Host Groups

Devices are automatically organized into host groups:

- **All Devices** - Global group containing all devices
- **Site: {site_name}** - Devices per site (e.g., "Site: EMEA-DC-ONPREM")
- **Role: {role_name}** - Devices per role (e.g., "Role: Core Switch")
- **Platform: {platform_name}** - Devices per platform (e.g., "Platform: Cisco NX-OS")
- **Tag: {tag_name}** - Devices per tag (e.g., "Tag: production")

Host groups are created automatically if they don't exist.

## Required Zabbix Templates

Before running sync, ensure these templates exist in Zabbix:

### Cisco Templates

- **Template Cisco Nexus 9000** - For Nexus switches (NX-OS)
- **Template Cisco Catalyst IOS-XE** - For Catalyst switches (IOS-XE)
- **Template Cisco IOS-XR** - For ASR routers (IOS-XR)
- **Template Cisco IOS** - For ISR routers (IOS)

### Generic Templates

- **Template Net Device SNMP** - Fallback for any SNMP device

You can download official Zabbix templates from:
https://git.zabbix.com/projects/ZBX/repos/zabbix/browse/templates

Or create custom templates for your environment.

## Configuration Options

### Filters

Control which devices are synced:

```yaml
sync:
  filters:
    # Only sync active devices
    allowed_statuses:
      - active

    # Custom field filter - IMPORTANT!
    # Sync devices where custom field cf_monitoring = Yes or No
    # - cf_monitoring = "Yes" → Host enabled in Zabbix (active monitoring)
    # - cf_monitoring = "No" → Host disabled in Zabbix (no monitoring, but synced)
    # - cf_monitoring not set → Device NOT synced
    custom_field_monitoring:
      field_name: "cf_monitoring"
      field_values: ["Yes", "No"]

    # Exclude devices with these tags
    excluded_tags:
      - no-monitoring
      - decommissioned

    # Exclude specific sites
    excluded_sites:
      - TEST-SITE
```

**Custom Field Requirement:**

The `cf_monitoring` custom field controls device synchronization and monitoring status:

| cf_monitoring | Behavior |
|---------------|----------|
| **Yes** | ✅ Device synced to Zabbix and **enabled** (actively monitored) |
| **No** | ⚠️ Device synced to Zabbix but **disabled** (not monitored, but tracked) |
| **Not set** | ❌ Device NOT synced to Zabbix |

**Requirements to sync a device:**
1. Device status must be **active**
2. Custom field **cf_monitoring** must be set to **Yes** or **No**

To disable the custom field filter and sync all devices, set it to null in `zabbix_mapping.yaml`:
```yaml
custom_field_monitoring: null
```

### Update Behavior

Control what gets updated on existing hosts:

```yaml
sync:
  update:
    # Update existing hosts
    update_existing: true

    # Update host groups
    update_groups: true

    # Update templates
    update_templates: true

    # Update IP addresses
    update_ip: true

    # Remove hosts deleted in NetBox
    remove_deleted: false
```

### Platform-Specific Settings

Override SNMP community per platform:

```yaml
platform_overrides:
  "NX-OS":
    snmp:
      community: "nxos_community"
    macros:
      "{$SNMP_COMMUNITY}": "nxos_community"

  "IOS-XR":
    snmp:
      community: "iosxr_community"
    macros:
      "{$SNMP_COMMUNITY}": "iosxr_community"
```

## Zabbix Macros

The script sets these macros on each host:

| Macro | Purpose | Example |
|-------|---------|---------|
| {$SNMP_COMMUNITY} | SNMP community string | "public" |
| {$NETBOX_SITE} | Reference to NetBox site | "EMEA-DC-ONPREM" |
| {$NETBOX_ROLE} | Reference to NetBox role | "Core Switch" |
| {$NETBOX_DEVICE_ID} | Link back to NetBox device | "42" |

These macros can be used in Zabbix items and triggers.

## Scheduled Sync

### Option 1: Cron Job

```bash
# Edit crontab
crontab -e

# Add sync every 6 hours
0 */6 * * * /usr/bin/python3 /path/to/sync_netbox_to_zabbix.py --mode incremental >> /var/log/netbox_zabbix_sync.log 2>&1
```

### Option 2: Systemd Timer

See main documentation (NETBOX_ZABBIX_SYNC.md) for systemd timer setup.

### Option 3: AWX/Ansible Tower

Create AWX job template to run sync on schedule.

## Troubleshooting

### Connection Failed

**NetBox:**
```bash
# Test NetBox API
curl -H "Authorization: Token YOUR-TOKEN" https://netbox.acme.com/api/dcim/devices/ | jq
```

**Zabbix:**
```bash
# Test Zabbix API
curl -X POST -H "Content-Type: application/json-rpc" \
  -d '{"jsonrpc":"2.0","method":"apiinfo.version","params":{},"id":1}' \
  https://zabbix.acme.com/api_jsonrpc.php
```

### Template Not Found

Error: `Template 'Template Cisco Nexus 9000' not found`

**Solutions:**
1. Import template to Zabbix
2. Update mapping file to use existing template
3. Use default template (fallback)

### Device Has No Primary IP

Warning: `Device has no primary IP, skipping`

**Solution:**
Assign primary IPv4 address in NetBox to the device.

### SNMP Monitoring Not Working

**Checks:**
1. SNMP enabled on device?
2. SNMP community correct?
3. Firewall allows SNMP (UDP 161)?
4. Zabbix can reach device IP?

**Test from Zabbix server:**
```bash
snmpwalk -v2c -c public DEVICE-IP sysDescr
```

## Examples

### Example 1: Sync All Devices

```bash
python3 sync_netbox_to_zabbix.py --mode full
```

Output:
```
======================================================================
Starting NetBox to Zabbix Synchronization
======================================================================
Connecting to NetBox: https://netbox.acme.com
✅ Connected to NetBox (236 devices total)
Connecting to Zabbix: https://zabbix.acme.com
✅ Connected to Zabbix (version 6.0.0)
Found 40 devices to sync
Syncing 40 devices...
✅ Created host: EMEA-DC-ONPREM-CORE-SW01
✅ Created host: EMEA-DC-ONPREM-CORE-SW02
...
======================================================================
Synchronization Complete
======================================================================
Devices found:   40
Devices created: 35
Devices updated: 5
Devices skipped: 0
Errors:          0
======================================================================
```

### Example 2: Sync Specific Site

```bash
python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"
```

### Example 3: Dry Run

```bash
python3 sync_netbox_to_zabbix.py --dry-run
```

Output:
```
======================================================================
DRY RUN MODE - No changes will be made to Zabbix
======================================================================
...
[DRY-RUN] Would CREATE host: EMEA-DC-ONPREM-CORE-SW01 (IP: 10.10.100.1, Template: Template Cisco Nexus 9000, Groups: 4)
[DRY-RUN] Would CREATE host: EMEA-DC-ONPREM-CORE-SW02 (IP: 10.10.100.2, Template: Template Cisco Nexus 9000, Groups: 4)
...
```

## Documentation

For complete documentation, see:
- **NETBOX_ZABBIX_SYNC.md** - Full integration guide
- **zabbix_mapping.yaml** - Mapping configuration with comments
- **config.yaml.example** - Configuration example

## Support

For issues or questions:
1. Check troubleshooting section in this README
2. Check main documentation (NETBOX_ZABBIX_SYNC.md)
3. Review logs: `/var/log/netbox_zabbix_sync.log`
4. Contact NetOps team

---

**Version**: 1.0
**Last Updated**: 2025-12-06
