# NetBox Custom Field Setup for Zabbix Monitoring

This guide explains how to create the `cf_monitoring` custom field in NetBox for Zabbix sync filtering.

---

## Overview

The NetBox to Zabbix sync script uses a custom field called `cf_monitoring` to determine which devices should be monitored in Zabbix.

**Requirement**: Only devices with `cf_monitoring = "Yes"` are synchronized to Zabbix.

---

## Step 1: Create Custom Field in NetBox

### Via NetBox UI

1. **Navigate to Customization**
   - Go to **Customization → Custom Fields**
   - Click **+ Add**

2. **Configure Custom Field**

   **Basic Settings:**
   - **Name**: `cf_monitoring`
   - **Label**: `Monitoring Enabled`
   - **Object Type**: `dcim > device`
   - **Type**: `Selection`
   - **Required**: `☐` (optional - unchecked)
   - **Description**: `Enable Zabbix monitoring for this device`

   **Choices:**
   ```
   Yes
   No
   ```

   **Default Value**: `No`

   **Weight**: `100`

   **Validation:**
   - Min/Max: (leave empty)
   - Regex: (leave empty)

3. **Save** the custom field

### Via NetBox API

```python
import requests

NETBOX_URL = "https://netbox.acme.com"
TOKEN = "your-netbox-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

data = {
    "name": "cf_monitoring",
    "label": "Monitoring Enabled",
    "type": "select",
    "content_types": ["dcim.device"],
    "required": False,
    "description": "Enable Zabbix monitoring for this device",
    "choices": ["Yes", "No"],
    "default": "No",
    "weight": 100
}

response = requests.post(
    f"{NETBOX_URL}/api/extras/custom-fields/",
    headers=headers,
    json=data
)

print(f"Custom field created: {response.json()}")
```

---

## Step 2: Set Custom Field on Devices

### Method 1: Via NetBox UI (Single Device)

1. Navigate to the device (e.g., **EMEA-DC-ONPREM-CORE-SW01**)
2. Click **Edit**
3. Scroll to **Custom Fields** section
4. Set **Monitoring Enabled**: `Yes`
5. Click **Save**

### Method 2: Via NetBox UI (Bulk Edit)

1. Go to **Devices → Devices**
2. Filter devices you want to monitor (e.g., by site)
3. Select devices (checkboxes)
4. Click **Edit Selected**
5. Set **cf_monitoring**: `Yes`
6. Click **Apply**

### Method 3: Via NetBox API (Script)

```python
import requests

NETBOX_URL = "https://netbox.acme.com"
TOKEN = "your-netbox-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get devices from a specific site
devices_response = requests.get(
    f"{NETBOX_URL}/api/dcim/devices/?site=EMEA-DC-ONPREM&status=active",
    headers=headers
)

devices = devices_response.json()['results']

# Update each device
for device in devices:
    device_id = device['id']

    # Update custom field
    update_data = {
        "custom_fields": {
            "cf_monitoring": "Yes"
        }
    }

    response = requests.patch(
        f"{NETBOX_URL}/api/dcim/devices/{device_id}/",
        headers=headers,
        json=update_data
    )

    if response.status_code == 200:
        print(f"✅ Updated {device['name']}")
    else:
        print(f"❌ Failed to update {device['name']}: {response.text}")
```

### Method 4: Python Script (Bulk Update)

Create `enable_monitoring.py`:

```python
#!/usr/bin/env python3
"""
Enable monitoring for all active devices in a site

Usage:
    python3 enable_monitoring.py --site "EMEA-DC-ONPREM"
"""

import argparse
import pynetbox

NETBOX_URL = "https://netbox.acme.com"
TOKEN = "your-netbox-api-token"

def enable_monitoring(site_name: str):
    """Enable monitoring for all active devices in a site"""

    # Connect to NetBox
    nb = pynetbox.api(NETBOX_URL, token=TOKEN)

    # Get devices
    devices = nb.dcim.devices.filter(site=site_name, status='active')

    updated_count = 0

    for device in devices:
        # Set custom field
        device.custom_fields['cf_monitoring'] = 'Yes'
        device.save()

        print(f"✅ Enabled monitoring for {device.name}")
        updated_count += 1

    print(f"\nTotal devices updated: {updated_count}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Enable monitoring for devices')
    parser.add_argument('--site', required=True, help='Site name')

    args = parser.parse_args()
    enable_monitoring(args.site)
```

Run:
```bash
pip3 install pynetbox
python3 enable_monitoring.py --site "EMEA-DC-ONPREM"
```

---

## Step 3: Verify Custom Field

### Via NetBox UI

1. Go to **Devices → Devices**
2. Add column **Monitoring Enabled** to the table
3. Filter: **Monitoring Enabled** = `Yes`
4. Verify the list shows only devices you want to monitor

### Via NetBox API

```python
import requests

NETBOX_URL = "https://netbox.acme.com"
TOKEN = "your-netbox-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get devices with cf_monitoring = Yes
response = requests.get(
    f"{NETBOX_URL}/api/dcim/devices/?cf_monitoring=Yes",
    headers=headers
)

devices = response.json()['results']
print(f"Devices with monitoring enabled: {len(devices)}")

for device in devices:
    print(f"  - {device['name']} (Site: {device['site']['name']})")
```

---

## Step 4: Test Zabbix Sync

Once the custom field is set:

```bash
# Test with dry-run
python3 sync_netbox_to_zabbix.py --dry-run --site "EMEA-DC-ONPREM"

# Expected output:
# Filtering by custom field: cf_monitoring = Yes
# Found 10 devices to sync
# [DRY-RUN] Would CREATE host: EMEA-DC-ONPREM-CORE-SW01 ...
```

---

## Troubleshooting

### Problem: Custom field not appearing in device form

**Solution**: Make sure object type is set to `dcim > device`

### Problem: Devices not being synced despite cf_monitoring = Yes

**Checks**:
1. Device status is `active`?
2. Device has primary IPv4 address?
3. Custom field name is exactly `cf_monitoring`?
4. Custom field value is exactly `Yes` (case-sensitive)?

**Debug**:
```bash
# Check what NetBox API returns
curl -H "Authorization: Token YOUR-TOKEN" \
  "https://netbox.acme.com/api/dcim/devices/?cf_monitoring=Yes" | jq
```

### Problem: Sync finds 0 devices

**Check filters in `zabbix_mapping.yaml`:**
```yaml
sync:
  filters:
    custom_field_monitoring:
      field_name: "cf_monitoring"  # Must match custom field name
      field_value: "Yes"            # Must match exact value
```

---

## Best Practices

### 1. Default Value

Set default to `No` to prevent accidental monitoring of new devices.

### 2. Required Field

Make the field **optional** (not required) so existing devices without the field can still be managed.

### 3. Gradual Rollout

Enable monitoring site by site:
```bash
# Week 1: EMEA
python3 enable_monitoring.py --site "EMEA-DC-ONPREM"
python3 sync_netbox_to_zabbix.py --mode site --site "EMEA-DC-ONPREM"

# Week 2: APAC
python3 enable_monitoring.py --site "APAC-DC-ONPREM"
python3 sync_netbox_to_zabbix.py --mode site --site "APAC-DC-ONPREM"

# Week 3: AMER
python3 enable_monitoring.py --site "AMER-DC-ONPREM"
python3 sync_netbox_to_zabbix.py --mode site --site "AMER-DC-ONPREM"
```

### 4. Automation

Create a workflow:
1. Device added to NetBox
2. Set `cf_monitoring = No` by default
3. After validation, set `cf_monitoring = Yes`
4. Automated sync adds device to Zabbix

### 5. Documentation

Add description to custom field explaining its purpose:
```
Enable Zabbix monitoring for this device.
Set to 'Yes' to sync this device to Zabbix for monitoring.
Set to 'No' to exclude from monitoring.
```

---

## Summary

✅ Create custom field `cf_monitoring` with choices: Yes, No
✅ Set field on devices that should be monitored
✅ Sync script automatically filters by this field
✅ Only devices with `cf_monitoring = Yes` are synced to Zabbix

This provides fine-grained control over which devices are monitored!

---

**Last Updated**: 2025-12-06
**Version**: 1.0
