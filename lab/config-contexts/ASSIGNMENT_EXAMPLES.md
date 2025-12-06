# Config Context Assignment Examples

This document provides practical examples of config context assignments for various use cases.

## Table of Contents

1. [Basic Assignments](#basic-assignments)
2. [Advanced Assignments](#advanced-assignments)
3. [Real-World Scenarios](#real-world-scenarios)
4. [Troubleshooting](#troubleshooting)

---

## Basic Assignments

### Example 1: Global Context (All Devices)

**Use Case**: AAA servers, syslog servers, contact information that applies to ALL devices

**Assignment**:
- Sites: (empty)
- Roles: (empty)
- Platforms: (empty)
- Device Types: (empty)
- Devices: (empty)
- Tags: (empty)

**Context Data** (`global_context.json`):
```json
{
  "global": {
    "organization": "ACME Corporation",
    "contact_email": "netops@acme.com"
  },
  "logging": {
    "syslog_servers": ["10.255.1.10", "10.255.1.11"]
  },
  "aaa": {
    "tacacs_servers": ["10.255.1.20", "10.255.1.21"]
  }
}
```

**Applies To**: ALL devices in NetBox (no restrictions)

---

### Example 2: Site-Specific Context

**Use Case**: NTP servers, DNS servers, timezone for a specific datacenter

**Assignment**:
- Sites: `EMEA-DC-ONPREM`
- Roles: (empty)
- Platforms: (empty)
- Device Types: (empty)

**Context Data** (`emea_dc_onprem_context.json`):
```json
{
  "site": {
    "name": "EMEA-DC-ONPREM",
    "timezone": "Europe/Paris"
  },
  "ntp": {
    "servers": ["10.10.1.1", "10.10.1.2"]
  },
  "dns": {
    "servers": ["10.10.2.1", "10.10.2.2"],
    "domain": "emea.onprem.acme.com"
  }
}
```

**Applies To**: All devices in site EMEA-DC-ONPREM only

---

### Example 3: Platform-Specific Context

**Use Case**: Platform-specific features, commands, defaults for Cisco NX-OS

**Assignment**:
- Sites: (empty)
- Roles: (empty)
- Platforms: `NX-OS`
- Device Types: (empty)

**Context Data** (`platform_nxos_context.json`):
```json
{
  "platform": {
    "os": "NX-OS",
    "vendor": "Cisco Systems"
  },
  "features": {
    "required": ["interface-vlan", "lacp", "lldp", "ssh"]
  },
  "spanning_tree": {
    "mode": "rapid-pvst",
    "priority": 4096
  }
}
```

**Applies To**: All devices with platform = NX-OS (across all sites)

---

### Example 4: Role-Specific Context

**Use Case**: Role-specific VLANs, routing protocols, redundancy settings

**Assignment**:
- Sites: (empty)
- Roles: `Core Switch`
- Platforms: (empty)
- Device Types: (empty)

**Context Data** (`role_core_switch_context.json`):
```json
{
  "role": {
    "name": "Core Switch",
    "tier": "core"
  },
  "hsrp": {
    "version": 2,
    "priority_primary": 110
  },
  "routing": {
    "ospf": {
      "process_id": 1,
      "area": "0.0.0.0"
    }
  }
}
```

**Applies To**: All devices with role = Core Switch (across all sites and platforms)

---

## Advanced Assignments

### Example 5: Multi-Site Context (OR Logic)

**Use Case**: Common settings for all ONPREM sites (not CLOUD sites)

**Assignment**:
- Sites: `EMEA-DC-ONPREM`, `APAC-DC-ONPREM`, `AMER-DC-ONPREM`
- Roles: (empty)
- Platforms: (empty)
- Device Types: (empty)

**Context Data**:
```json
{
  "datacenter_type": "on-premise",
  "backup": {
    "servers": ["backup1.onprem.acme.com", "backup2.onprem.acme.com"]
  },
  "monitoring": {
    "prometheus": "prometheus.onprem.acme.com:9090"
  }
}
```

**Applies To**: Devices in EMEA-DC-ONPREM **OR** APAC-DC-ONPREM **OR** AMER-DC-ONPREM

**Logic**: OR logic - device needs to be in ANY of these sites

---

### Example 6: Site + Role Combination (AND Logic)

**Use Case**: Specific settings for Core Switches in EMEA only

**Assignment**:
- Sites: `EMEA-DC-ONPREM`
- Roles: `Core Switch`
- Platforms: (empty)
- Device Types: (empty)

**Context Data**:
```json
{
  "emea_core": {
    "hsrp_group_base": 100,
    "vrrp_enabled": false,
    "bgp_asn": 65100
  }
}
```

**Applies To**: Devices that are:
- In site EMEA-DC-ONPREM **AND**
- Have role Core Switch

**Matches**:
- ✅ EMEA-DC-ONPREM-CORE-SW01 (EMEA + Core Switch)
- ✅ EMEA-DC-ONPREM-CORE-SW02 (EMEA + Core Switch)
- ❌ APAC-DC-ONPREM-CORE-SW01 (Different site)
- ❌ EMEA-DC-ONPREM-DIST-SW01 (Different role)

**Logic**: AND logic - device must match ALL criteria

---

### Example 7: Site + Role + Platform (Triple AND)

**Use Case**: Specific optimizations for Nexus switches in EMEA core

**Assignment**:
- Sites: `EMEA-DC-ONPREM`
- Roles: `Core Switch`
- Platforms: `NX-OS`
- Device Types: (empty)

**Context Data**:
```json
{
  "emea_nexus_core": {
    "vpc_domain": 100,
    "vpc_priority": 100,
    "features": ["vpc", "lacp", "interface-vlan"]
  }
}
```

**Applies To**: Devices that are:
- In site EMEA-DC-ONPREM **AND**
- Have role Core Switch **AND**
- Run platform NX-OS

**Matches**:
- ✅ EMEA-DC-ONPREM-CORE-SW01 (Nexus 9508, NX-OS)
- ✅ EMEA-DC-ONPREM-CORE-SW02 (Nexus 9508, NX-OS)
- ❌ EMEA-DC-ONPREM-ACC-STG-01 (IOS-XE, not NX-OS)

---

### Example 8: Device Type Specific

**Use Case**: Model-specific interface configurations for Nexus 9508

**Assignment**:
- Sites: (empty)
- Roles: (empty)
- Platforms: (empty)
- Device Types: `nexus-9508` (slug)

**Context Data**:
```json
{
  "device_type": {
    "model": "Nexus 9508",
    "chassis_slots": 8,
    "supervisor_slots": 2
  },
  "interfaces": {
    "mgmt0": "10G",
    "max_port_channels": 511
  }
}
```

**Applies To**: All devices with device_type = Nexus 9508 (slug: nexus-9508)

**Matches**:
- ✅ EMEA-DC-ONPREM-CORE-SW01 (Nexus 9508)
- ✅ EMEA-DC-ONPREM-CORE-SW02 (Nexus 9508)
- ✅ APAC-DC-ONPREM-CORE-SW01 (Nexus 9508)
- ❌ EMEA-DC-ONPREM-DIST-SW01 (Nexus 93180YC-FX, different model)

---

### Example 9: Device-Specific Override

**Use Case**: Custom configuration for a specific device (highest priority)

**Assignment**:
- Sites: (empty)
- Roles: (empty)
- Platforms: (empty)
- Device Types: (empty)
- Devices: `EMEA-DC-ONPREM-CORE-SW01`

**Context Data**:
```json
{
  "device_override": {
    "custom_vlan": 999,
    "special_feature": true,
    "note": "This device has custom configuration"
  }
}
```

**Applies To**: Only device EMEA-DC-ONPREM-CORE-SW01

**Use Case**: Override specific settings for one device without affecting others

**Weight**: Usually set to 8000+ (highest priority) to override all other contexts

---

### Example 10: Tag-Based Assignment

**Use Case**: Apply context to devices tagged as "production"

**Assignment**:
- Sites: (empty)
- Roles: (empty)
- Platforms: (empty)
- Device Types: (empty)
- Tags: `production`

**Context Data**:
```json
{
  "environment": "production",
  "monitoring": {
    "critical_alerts": true,
    "pagerduty_enabled": true
  },
  "backup": {
    "frequency": "hourly",
    "retention_days": 30
  }
}
```

**Applies To**: All devices tagged with "production"

**Matches**: Any device with tag "production", regardless of site, role, or platform

---

## Real-World Scenarios

### Scenario 1: Multi-Region Deployment

**Challenge**: 3 regions (EMEA, APAC, AMER), each with different NTP/DNS servers

**Solution**: Create 3 site-specific contexts

**Context 1: EMEA-DC-ONPREM**
```json
{
  "site": {"region": "EMEA", "timezone": "Europe/Paris"},
  "ntp": {"servers": ["10.10.1.1", "10.10.1.2"]},
  "dns": {"servers": ["10.10.2.1", "10.10.2.2"]}
}
```
Assignment: Sites = `EMEA-DC-ONPREM`

**Context 2: APAC-DC-ONPREM**
```json
{
  "site": {"region": "APAC", "timezone": "Asia/Singapore"},
  "ntp": {"servers": ["10.20.1.1", "10.20.1.2"]},
  "dns": {"servers": ["10.20.2.1", "10.20.2.2"]}
}
```
Assignment: Sites = `APAC-DC-ONPREM`

**Context 3: AMER-DC-ONPREM**
```json
{
  "site": {"region": "AMER", "timezone": "America/New_York"},
  "ntp": {"servers": ["10.30.1.1", "10.30.1.2"]},
  "dns": {"servers": ["10.30.2.1", "10.30.2.2"]}
}
```
Assignment: Sites = `AMER-DC-ONPREM`

**Result**: Each region's devices get their local NTP/DNS servers automatically

---

### Scenario 2: Platform-Based Feature Activation

**Challenge**: Different platforms require different features enabled

**Solution**: Create platform-specific contexts

**NX-OS Context**:
```json
{
  "features": {
    "required": ["interface-vlan", "lacp", "lldp", "ssh", "vpc"]
  }
}
```
Assignment: Platforms = `NX-OS`

**IOS-XE Context**:
```json
{
  "services": {
    "required": ["ip routing", "ip multicast-routing"]
  }
}
```
Assignment: Platforms = `IOS-XE`

**Result**: Each platform gets appropriate feature/service activation commands

---

### Scenario 3: Tier-Based VLAN Assignment

**Challenge**: Different device roles need different VLANs

**Solution**: Create role-specific contexts

**Core Switch Context**:
```json
{
  "vlans": {
    "management": 100,
    "native": 1,
    "allowed": "1,100,200-299,300-349"
  }
}
```
Assignment: Roles = `Core Switch`

**Access Switch Context**:
```json
{
  "vlans": {
    "management": 100,
    "data": 200,
    "voice": 210,
    "guest": 220
  }
}
```
Assignment: Roles = `Access Switch`

**Result**: Each tier gets appropriate VLAN configuration

---

### Scenario 4: Emergency Device Override

**Challenge**: Need to temporarily change settings on one device during maintenance

**Solution**: Create high-weight device-specific context

**Device Override Context**:
```json
{
  "maintenance_mode": true,
  "snmp": {
    "location": "MAINTENANCE - DO NOT ALERT"
  },
  "logging": {
    "severity": "debugging"
  }
}
```
Assignment:
- Weight: 9000 (very high)
- Devices = `EMEA-DC-ONPREM-CORE-SW01`

**Result**: This one device gets maintenance settings, overriding all other contexts

**After Maintenance**: Simply deactivate or delete this context

---

## Troubleshooting

### Problem 1: Context Not Applying

**Symptom**: Device doesn't receive expected context data

**Checklist**:
1. ✅ Is context active? (`is_active = True`)
2. ✅ Does device match assignment criteria?
   - Check site name (exact match)
   - Check role name (exact match)
   - Check platform slug (not display name!)
   - Check device type slug (not model name!)
3. ✅ Is device assigned to site/role/platform?
4. ✅ Check weight - is another context overriding?

**Debug in NetBox UI**:
1. Go to device page
2. Click "Config Context" tab
3. View "Applicable Contexts" section
4. See which contexts are applied and merged result

---

### Problem 2: Wrong Values in Merged Context

**Symptom**: Device has unexpected values in config context

**Cause**: Higher-weight context is overriding

**Solution**:
1. Check weights of all applicable contexts
2. Remember: Higher weight = higher priority
3. Verify merge order:
   - Global (1000) → Platform (2000) → Site (3000) → Role (4000) → Device Type (4500) → Device (8000)
4. Adjust weights if needed

**Example**:
- Site context (weight 3000): `{"vlan": 100}`
- Role context (weight 4000): `{"vlan": 200}`
- **Result**: `{"vlan": 200}` (role wins, higher weight)

---

### Problem 3: Platform Assignment Not Working

**Symptom**: Platform-specific context not applying

**Common Mistake**: Using platform display name instead of slug

**Wrong**:
```csv
platforms,Cisco NX-OS
```

**Correct**:
```csv
platforms,NX-OS
```

**Or in API**:
```python
# Get platform ID first
platform_response = requests.get(
    f"{NETBOX_URL}/api/dcim/platforms/?slug=nxos",
    headers=headers
)
```

**Note**: Platform slug is usually lowercase with hyphens, not spaces

---

### Problem 4: CSV Import Fails

**Symptom**: CSV import fails with validation error

**Common Issues**:

1. **JSON Escaping in CSV**:
   - Wrong: `data,{...}`
   - Correct: `data,"{...}"`  (quoted)

2. **Multiple Values**:
   - Wrong: `sites,["EMEA-DC-ONPREM","APAC-DC-ONPREM"]`
   - Correct: `sites,"EMEA-DC-ONPREM,APAC-DC-ONPREM"` (comma-separated string)

3. **Empty Fields**:
   - Wrong: Leave blank
   - Correct: `sites,""` (empty string in quotes)

---

### Problem 5: Device-Specific Override Not Working

**Symptom**: Device context not overriding other contexts

**Solution**: Ensure device-specific context has highest weight

**Example**:
```json
{
  "name": "Device Override",
  "weight": 9000,  // Very high weight
  "devices": ["EMEA-DC-ONPREM-CORE-SW01"]
}
```

**Weight Guidelines**:
- Global: 1000
- Platform: 2000-2999
- Site: 3000-3999
- Role: 4000-4999
- Device Type: 4500-4999
- Device Override: 8000+

---

## Best Practices

### 1. Use Consistent Weight Ranges

- Global: 1000-1999
- Platform: 2000-2999
- Site: 3000-3999
- Role: 4000-4999
- Device Type: 4500-4999
- Tag: 5000-5999
- Device-specific: 8000+

### 2. Avoid Too Many Assignments

**Bad**: Context with sites + roles + platforms + device_types all filled
→ Very restrictive, hard to match

**Good**: One or two assignment types
→ Clear, predictable

### 3. Use Descriptive Names

**Bad**: "Context 1", "Config A"
**Good**: "EMEA-DC-ONPREM Site", "Core Switch Role"

### 4. Test Before Production

1. Create context with `is_active = False`
2. Verify assignment and data
3. Test on one device
4. Activate (`is_active = True`)

### 5. Document Custom Contexts

Add clear descriptions to each context explaining purpose and assignment logic

---

**Last Updated**: 2025-12-06
**Version**: 1.0
