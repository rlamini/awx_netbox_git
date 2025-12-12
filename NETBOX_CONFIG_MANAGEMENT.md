# NetBox Configuration Management Design
## EMEA-DC-ONPREM Cisco Devices - Config Contexts & Templates

---

## Table of Contents

1. [Overview](#overview)
2. [Config Contexts](#config-contexts)
3. [Config Templates](#config-templates)
4. [Architecture](#architecture)
5. [Implementation for EMEA-DC-ONPREM](#implementation-for-emea-dc-onprem)
6. [Examples](#examples)
7. [Import Process](#import-process)

---

## Overview

### What is Configuration Management in NetBox?

NetBox provides two powerful features for network device configuration management:

1. **Config Contexts**: Hierarchical JSON data that stores configuration variables
2. **Config Templates**: Jinja2 templates that render actual device configurations using context data

### Why Use Config Contexts and Templates?

- **Centralized Data Source**: Single source of truth for configuration variables
- **Hierarchical Inheritance**: Data cascades from global → site → role → platform → device
- **Template Reusability**: One template can serve multiple devices with different contexts
- **Version Control**: Track configuration changes over time
- **Automation Ready**: Export rendered configs for Ansible, Terraform, or direct deployment

---

## Config Contexts

### What are Config Contexts?

Config contexts are **JSON data structures** that store configuration variables. They can be assigned to devices based on multiple criteria:

- **Sites**: All devices at a specific location
- **Roles**: All devices with a specific role (Core Switch, Distribution Switch, etc.)
- **Device Types**: All devices of a specific model (Nexus 9508, Catalyst 9300-48P, etc.)
- **Platforms**: All devices running specific OS (NX-OS, IOS-XE, IOS-XR, IOS)
- **Manufacturers**: All devices from a specific vendor
- **Tags**: Custom groupings
- **Individual Devices**: Device-specific overrides

### Context Hierarchy and Priority

Config contexts are **merged** in order of specificity (higher numbers = higher priority):

```
Priority Order (1 = Lowest, 8 = Highest):
1. Global contexts (no assignment)
2. Manufacturer-specific
3. Platform-specific
4. Site-specific
5. Role-specific
6. Device Type-specific
7. Tag-specific
8. Device-specific (highest priority, overrides all)
```

**Important**: When contexts merge:
- Nested keys are **deep-merged** (combined)
- Duplicate keys at the same level: **higher priority wins**
- Arrays are **replaced**, not merged

### Config Context Assignment (Affectation)

Config contexts can be assigned to devices using multiple criteria. Each context can have one or more assignment rules:

#### Assignment Methods

| Assignment Type | Field Name | Description | Example | When to Use |
|----------------|------------|-------------|---------|-------------|
| **Global** | (none) | Applied to ALL devices | Logging, AAA servers | Universal settings for entire infrastructure |
| **Site** | `sites` | All devices in specific site(s) | EMEA-DC-ONPREM | Site-specific NTP, DNS, timezone |
| **Role** | `roles` | All devices with specific role(s) | Core Switch, Access Switch | Role-specific VLANs, routing, features |
| **Platform** | `platforms` | All devices running specific OS | NX-OS, IOS-XE, IOS-XR | Platform-specific commands, features |
| **Device Type** | `device_types` | All devices of specific model(s) | Nexus 9508, Catalyst 9300-48P | Model-specific settings, interfaces |
| **Manufacturer** | `manufacturers` | All devices from vendor | Cisco Systems, Arista | Vendor-specific defaults |
| **Tag** | `tags` | All devices with specific tag(s) | production, dmz | Custom groupings |
| **Device** | `devices` | Specific individual device(s) | EMEA-DC-ONPREM-CORE-SW01 | Device-specific overrides |

#### Assignment Rules and Logic

**Multiple Assignments (OR logic):**
- A context can be assigned to multiple sites, roles, platforms, etc.
- Example: `sites: ["EMEA-DC-ONPREM", "APAC-DC-ONPREM"]` applies to devices in EITHER site

**Multiple Criteria (AND logic):**
- A context can have multiple assignment types
- Example: A context with `sites: ["EMEA-DC-ONPREM"]` AND `roles: ["Core Switch"]` applies ONLY to Core Switches in EMEA-DC-ONPREM

**No Assignment (Global):**
- A context with NO assignments applies to ALL devices

#### Assignment Examples

**Example 1: Global Context (No Assignment)**
```json
{
  "name": "Global Configuration",
  "weight": 1000,
  "sites": [],
  "roles": [],
  "platforms": [],
  "device_types": [],
  "devices": []
}
```
→ **Applies to**: ALL devices in NetBox

**Example 2: Site-Specific Context**
```json
{
  "name": "EMEA-DC-ONPREM Site",
  "weight": 3000,
  "sites": ["EMEA-DC-ONPREM"],
  "roles": [],
  "platforms": [],
  "device_types": [],
  "devices": []
}
```
→ **Applies to**: All devices in site "EMEA-DC-ONPREM" only

**Example 3: Platform-Specific Context**
```json
{
  "name": "Cisco NX-OS Platform",
  "weight": 2000,
  "sites": [],
  "roles": [],
  "platforms": ["NX-OS"],
  "device_types": [],
  "devices": []
}
```
→ **Applies to**: All devices with platform "NX-OS" (regardless of site)

**Example 4: Role-Specific Context**
```json
{
  "name": "Core Switch Role",
  "weight": 4000,
  "sites": [],
  "roles": ["Core Switch"],
  "platforms": [],
  "device_types": [],
  "devices": []
}
```
→ **Applies to**: All devices with role "Core Switch" (regardless of site or platform)

**Example 5: Multiple Sites (OR Logic)**
```json
{
  "name": "ONPREM Sites Configuration",
  "weight": 3000,
  "sites": ["EMEA-DC-ONPREM", "APAC-DC-ONPREM", "AMER-DC-ONPREM"],
  "roles": [],
  "platforms": [],
  "device_types": [],
  "devices": []
}
```
→ **Applies to**: Devices in EMEA-DC-ONPREM OR APAC-DC-ONPREM OR AMER-DC-ONPREM

**Example 6: Combined Assignment (AND Logic)**
```json
{
  "name": "EMEA Core Switches",
  "weight": 5000,
  "sites": ["EMEA-DC-ONPREM"],
  "roles": ["Core Switch"],
  "platforms": ["NX-OS"],
  "device_types": [],
  "devices": []
}
```
→ **Applies to**: Devices that are:
- IN site "EMEA-DC-ONPREM" **AND**
- WITH role "Core Switch" **AND**
- RUNNING platform "NX-OS"

(This would match: EMEA-DC-ONPREM-CORE-SW01 and EMEA-DC-ONPREM-CORE-SW02)

**Example 7: Device-Specific Override**
```json
{
  "name": "CORE-SW01 Custom Config",
  "weight": 8000,
  "sites": [],
  "roles": [],
  "platforms": [],
  "device_types": [],
  "devices": ["EMEA-DC-ONPREM-CORE-SW01"]
}
```
→ **Applies to**: Only device "EMEA-DC-ONPREM-CORE-SW01"

**Example 8: Device Type Specific**
```json
{
  "name": "Nexus 9508 Configuration",
  "weight": 4500,
  "sites": [],
  "roles": [],
  "platforms": [],
  "device_types": ["nexus-9508"],
  "devices": []
}
```
→ **Applies to**: All devices with device_type "Nexus 9508" (slug: nexus-9508)

#### Assignment Matrix for EMEA-DC-ONPREM

Here's how our 11 contexts are assigned:

| Context Name | Weight | Site | Role | Platform | Device Type | Device | Applies To |
|--------------|--------|------|------|----------|-------------|--------|------------|
| Global Configuration | 1000 | - | - | - | - | - | ALL devices |
| Cisco NX-OS Platform | 2000 | - | - | NX-OS | - | - | All NX-OS devices |
| Cisco IOS-XE Platform | 2000 | - | - | IOS-XE | - | - | All IOS-XE devices |
| Cisco IOS-XR Platform | 2000 | - | - | IOS-XR | - | - | All IOS-XR devices |
| Cisco IOS Platform | 2000 | - | - | IOS | - | - | All IOS devices |
| EMEA-DC-ONPREM Site | 3000 | EMEA-DC-ONPREM | - | - | - | - | All EMEA-DC-ONPREM devices |
| Core Switch Role | 4000 | - | Core Switch | - | - | - | All Core Switches |
| Distribution Switch Role | 4000 | - | Distribution Switch | - | - | - | All Distribution Switches |
| Access Switch Role | 4000 | - | Access Switch | - | - | - | All Access Switches |
| Router Role | 4000 | - | Router | - | - | - | All Routers |
| OOB Router Role | 4000 | - | OOB Router | - | - | - | All OOB Routers |

#### Context Resolution for Specific Devices

**Device: EMEA-DC-ONPREM-CORE-SW01** (Nexus 9508, Core Switch, NX-OS)

Contexts applied (in merge order):
1. ✅ Global Configuration (weight 1000) - No assignment = ALL devices
2. ✅ Cisco NX-OS Platform (weight 2000) - Platform = NX-OS
3. ✅ EMEA-DC-ONPREM Site (weight 3000) - Site = EMEA-DC-ONPREM
4. ✅ Core Switch Role (weight 4000) - Role = Core Switch

**Device: EMEA-DC-ONPREM-ACC-STG-01** (Catalyst 9300-48P, Access Switch, IOS-XE)

Contexts applied (in merge order):
1. ✅ Global Configuration (weight 1000) - No assignment = ALL devices
2. ✅ Cisco IOS-XE Platform (weight 2000) - Platform = IOS-XE
3. ✅ EMEA-DC-ONPREM Site (weight 3000) - Site = EMEA-DC-ONPREM
4. ✅ Access Switch Role (weight 4000) - Role = Access Switch

**Device: EMEA-DC-ONPREM-RTR-EDGE-01** (ASR 9001, Router, IOS-XR)

Contexts applied (in merge order):
1. ✅ Global Configuration (weight 1000) - No assignment = ALL devices
2. ✅ Cisco IOS-XR Platform (weight 2000) - Platform = IOS-XR
3. ✅ EMEA-DC-ONPREM Site (weight 3000) - Site = EMEA-DC-ONPREM
4. ✅ Router Role (weight 4000) - Role = Router

**Device: EMEA-DC-ONPREM-OOB-RTR01** (ISR 4431, OOB Router, IOS)

Contexts applied (in merge order):
1. ✅ Global Configuration (weight 1000) - No assignment = ALL devices
2. ✅ Cisco IOS Platform (weight 2000) - Platform = IOS
3. ✅ EMEA-DC-ONPREM Site (weight 3000) - Site = EMEA-DC-ONPREM
4. ✅ OOB Router Role (weight 4000) - Role = OOB Router

#### How to Assign Contexts in NetBox

**Method 1: NetBox UI**

1. Navigate to **Customization → Config Contexts**
2. Click **Add** or edit existing context
3. Fill in **Assignment** section:
   - **Sites**: Select one or more sites (dropdown)
   - **Roles**: Select one or more roles (dropdown)
   - **Platforms**: Select one or more platforms (dropdown)
   - **Device Types**: Select one or more device types (dropdown)
   - **Devices**: Select specific devices (dropdown)
   - **Tags**: Select tags (dropdown)
4. Set **Weight** (priority)
5. Paste JSON data
6. Save

**Method 2: NetBox API**

```python
import requests
import json

NETBOX_URL = "https://netbox.example.com"
TOKEN = "your-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get IDs for assignments
site_response = requests.get(
    f"{NETBOX_URL}/api/dcim/sites/?name=EMEA-DC-ONPREM",
    headers=headers
)
site_id = site_response.json()['results'][0]['id']

# Load context data
with open('lab/config-contexts/emea_dc_onprem_context.json') as f:
    context_data = json.load(f)

# Create context with site assignment
data = {
    "name": "EMEA-DC-ONPREM Site",
    "weight": 3000,
    "description": "EMEA DC ONPREM site-specific configuration",
    "is_active": True,
    "data": context_data,
    "sites": [site_id],  # Assignment to site
    "roles": [],
    "platforms": [],
    "device_types": [],
    "tags": []
}

response = requests.post(
    f"{NETBOX_URL}/api/extras/config-contexts/",
    headers=headers,
    json=data
)

print(f"Created context: {response.json()['name']}")
```

**Method 3: CSV Import**

CSV format with assignment columns:

```csv
name,weight,description,is_active,data,sites,roles,platforms,device_types
Global Configuration,1000,Global settings,True,"{...}","","","",""
EMEA-DC-ONPREM Site,3000,Site config,True,"{...}","EMEA-DC-ONPREM","","",""
Core Switch Role,4000,Core role,True,"{...}","","Core Switch","",""
Cisco NX-OS Platform,2000,NX-OS defaults,True,"{...}","","","NX-OS",""
```

**Important Notes:**
- Multiple values in CSV: Use comma-separated list in quotes: `"site1,site2,site3"`
- Empty assignment = Global context
- IDs vs Names: API requires IDs, CSV import can use names

### Config Context Structure

Config contexts use **JSON format**:

```json
{
  "hostname": "DEVICE-NAME",
  "management": {
    "vlan": 100,
    "ip": "10.0.0.1/24",
    "gateway": "10.0.0.254"
  },
  "dns": {
    "servers": ["8.8.8.8", "8.8.4.4"],
    "domain": "example.com"
  },
  "ntp": {
    "servers": ["ntp1.example.com", "ntp2.example.com"],
    "timezone": "Europe/Paris"
  },
  "snmp": {
    "community": "public",
    "location": "Datacenter",
    "contact": "netops@example.com"
  }
}
```

---

## Config Templates

### What are Config Templates?

Config templates are **Jinja2 templates** that generate actual device configurations by combining:
- Template logic (loops, conditionals, filters)
- Config context data (variables)

### Template Assignment

Templates are assigned to devices based on:
- **Platform**: Cisco NX-OS, IOS-XE, IOS-XR, IOS, etc.
- **Device Type**: Specific models
- **Role**: Device function

### Jinja2 Syntax Basics

```jinja2
{# Comments #}

{# Variables #}
hostname {{ hostname }}

{# Conditionals #}
{% if management.vlan %}
interface Vlan{{ management.vlan }}
  ip address {{ management.ip }}
{% endif %}

{# Loops #}
{% for server in ntp.servers %}
ntp server {{ server }}
{% endfor %}

{# Filters #}
{{ device.name | upper }}
{{ ip_address | ipaddr('address') }}
```

### Template Data Sources

Templates can access multiple data sources:

1. **Config Context** (`context`): Merged JSON data
2. **Device Object** (`device`): NetBox device attributes
   - `device.name`
   - `device.site.name`
   - `device.role.name`
   - `device.device_type.model`
3. **Request Object** (`request`): Current user, timestamp, etc.

---

## Architecture

### Configuration Management Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    NetBox Database                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │ Config Contexts  │        │ Config Templates │          │
│  │   (JSON Data)    │        │  (Jinja2 Files)  │          │
│  └────────┬─────────┘        └─────────┬────────┘          │
│           │                            │                    │
│           │        ┌───────────────────┘                    │
│           │        │                                        │
│           ▼        ▼                                        │
│    ┌─────────────────────┐                                 │
│    │  Rendering Engine   │                                 │
│    │  (Jinja2 + Context) │                                 │
│    └──────────┬──────────┘                                 │
│               │                                             │
└───────────────┼─────────────────────────────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │ Rendered Configuration│
    │   (Device Config)     │
    └───────────────────────┘
                │
                ▼
    ┌───────────────────────┐
    │ Export / Deploy       │
    │ - API Export          │
    │ - Ansible Playbook    │
    │ - Direct Push (NAPALM)│
    └───────────────────────┘
```

### Data Flow Example

```
Device: EMEA-DC-ONPREM-CORE-SW01 (Cisco Nexus 9508, Core Switch, NX-OS)

Step 1: Collect Config Contexts
├── Global Context          (priority 1)
├── Cisco Systems Context   (priority 2)
├── NX-OS Platform Context  (priority 3)
├── EMEA-DC-ONPREM Context  (priority 4)
├── Core Switch Role        (priority 5)
└── Nexus 9508 Type        (priority 6)

Step 2: Merge Contexts (JSON Deep Merge)
{
  "hostname": "EMEA-DC-ONPREM-CORE-SW01",  # From global
  "domain": "emea.datacenter.local",       # From site
  "ntp_servers": ["10.10.1.1", "10.10.1.2"], # From site
  "snmp_location": "EMEA DC ONPREM - Network Core", # From role
  "mgmt_vlan": 100,                        # From platform
  "features": ["vpc", "lacp", "lldp"]      # From device type
}

Step 3: Select Template
Platform: NX-OS → Template: cisco_nxos_base.j2

Step 4: Render Configuration
Template + Merged Context → Full Device Configuration

Step 5: Export
- View in NetBox UI
- Export via API
- Push via Ansible/AWX
```

---

## Implementation for EMEA-DC-ONPREM

### Target Devices (10 Cisco Devices)

| Device Name | Device Type | Platform | Role |
|-------------|-------------|----------|------|
| EMEA-DC-ONPREM-CORE-SW01 | Nexus 9508 | NX-OS | Core Switch |
| EMEA-DC-ONPREM-CORE-SW02 | Nexus 9508 | NX-OS | Core Switch |
| EMEA-DC-ONPREM-DIST-SW01 | Nexus 93180YC-FX | NX-OS | Distribution Switch |
| EMEA-DC-ONPREM-DIST-SW02 | Nexus 93180YC-FX | NX-OS | Distribution Switch |
| EMEA-DC-ONPREM-ACC-STG-01 | Catalyst 9300-48P | IOS-XE | Access Switch |
| EMEA-DC-ONPREM-ACC-STG-02 | Catalyst 9300-48P | IOS-XE | Access Switch |
| EMEA-DC-ONPREM-MMR-SW01 | Catalyst 9300-48P | IOS-XE | Access Switch |
| EMEA-DC-ONPREM-RTR-EDGE-01 | ASR 9001 | IOS-XR | Router |
| EMEA-DC-ONPREM-RTR-EDGE-02 | ASR 9001 | IOS-XR | Router |
| EMEA-DC-ONPREM-OOB-RTR01 | ISR 4431 | IOS | OOB Router |

### Config Context Hierarchy Design

#### Base Config Contexts (Weights 1000-4000)

The following contexts provide foundational configuration applicable to all or specific groups of devices.

#### 1. Global Context (All Devices)

**File**: `global_context.json`
**Priority**: 1 (Lowest)
**Applies To**: All devices

```json
{
  "global": {
    "organization": "ACME Corporation",
    "managed_by": "NetOps Team",
    "contact_email": "netops@acme.com"
  },
  "logging": {
    "syslog_servers": [
      "10.255.1.10",
      "10.255.1.11"
    ],
    "severity": "informational",
    "facility": "local7"
  },
  "aaa": {
    "tacacs_servers": [
      "10.255.1.20",
      "10.255.1.21"
    ],
    "tacacs_key": "TACACS_SECRET_KEY"
  }
}
```

#### 2. Site Context (EMEA-DC-ONPREM)

**File**: `emea_dc_onprem_context.json`
**Priority**: 4
**Applies To**: All devices at site EMEA-DC-ONPREM

```json
{
  "site": {
    "name": "EMEA-DC-ONPREM",
    "region": "EMEA",
    "location": "Paris, France",
    "timezone": "Europe/Paris",
    "domain": "emea.onprem.acme.com"
  },
  "ntp": {
    "servers": [
      "10.10.1.1",
      "10.10.1.2"
    ],
    "source_interface": "Loopback0"
  },
  "dns": {
    "servers": [
      "10.10.2.1",
      "10.10.2.2"
    ],
    "domain": "emea.onprem.acme.com"
  },
  "snmp": {
    "community_ro": "SNMP_RO_COMMUNITY",
    "community_rw": "SNMP_RW_COMMUNITY",
    "location": "EMEA DC ONPREM - Paris FR",
    "contact": "netops-emea@acme.com",
    "trap_servers": [
      "10.10.3.1",
      "10.10.3.2"
    ]
  },
  "management": {
    "vlan": 100,
    "subnet": "10.10.100.0/24",
    "gateway": "10.10.100.254"
  }
}
```

#### 3. Platform Context (NX-OS)

**File**: `platform_nxos_context.json`
**Priority**: 3
**Applies To**: All Cisco NX-OS devices

```json
{
  "platform": {
    "os": "NX-OS",
    "vendor": "Cisco Systems"
  },
  "features": {
    "required": [
      "interface-vlan",
      "lacp",
      "lldp",
      "ssh"
    ]
  },
  "spanning_tree": {
    "mode": "rapid-pvst",
    "priority": 4096
  },
  "vtp": {
    "mode": "transparent"
  },
  "management": {
    "ssh_version": 2,
    "enable_scp": true
  }
}
```

#### 4. Platform Context (IOS-XE)

**File**: `platform_iosxe_context.json`
**Priority**: 3
**Applies To**: All Cisco IOS-XE devices (Catalyst)

```json
{
  "platform": {
    "os": "IOS-XE",
    "vendor": "Cisco Systems"
  },
  "spanning_tree": {
    "mode": "rapid-pvst",
    "portfast_default": true
  },
  "management": {
    "ssh_version": 2,
    "enable_secret_level": 15
  },
  "security": {
    "service_password_encryption": true,
    "tcp_keepalives": true
  }
}
```

#### 5. Platform Context (IOS-XR)

**File**: `platform_iosxr_context.json`
**Priority**: 3
**Applies To**: All Cisco IOS-XR devices (ASR)

```json
{
  "platform": {
    "os": "IOS-XR",
    "vendor": "Cisco Systems"
  },
  "management": {
    "ssh_version": "v2",
    "netconf": {
      "enabled": true,
      "port": 830
    }
  },
  "routing": {
    "protocols": ["ospf", "bgp"],
    "mpls_enabled": false
  }
}
```

#### 6. Role Context (Core Switch)

**File**: `role_core_switch_context.json`
**Priority**: 5
**Applies To**: All Core Switch devices

```json
{
  "role": {
    "name": "Core Switch",
    "tier": "core",
    "redundancy": "hsrp"
  },
  "hsrp": {
    "version": 2,
    "group_id": 1,
    "priority_primary": 110,
    "priority_secondary": 100,
    "preempt": true
  },
  "vlans": {
    "management": 100,
    "native": 1,
    "allowed": "1,100,200-299"
  },
  "routing": {
    "ospf": {
      "process_id": 1,
      "area": "0.0.0.0"
    }
  },
  "interfaces": {
    "mtu": 9216
  }
}
```

#### 7. Role Context (Distribution Switch)

**File**: `role_distribution_switch_context.json`
**Priority**: 5
**Applies To**: All Distribution Switch devices

```json
{
  "role": {
    "name": "Distribution Switch",
    "tier": "distribution"
  },
  "vlans": {
    "management": 100,
    "native": 1,
    "server_vlans": "200-299",
    "storage_vlans": "300-349"
  },
  "spanning_tree": {
    "priority": 8192,
    "root_guard": true
  },
  "interfaces": {
    "mtu": 9216
  }
}
```

#### 8. Role Context (Access Switch)

**File**: `role_access_switch_context.json`
**Priority**: 5
**Applies To**: All Access Switch devices

```json
{
  "role": {
    "name": "Access Switch",
    "tier": "access"
  },
  "vlans": {
    "management": 100,
    "native": 1,
    "data_vlan": 200,
    "voice_vlan": 210
  },
  "spanning_tree": {
    "portfast": true,
    "bpduguard": true
  },
  "poe": {
    "enabled": true,
    "power_budget": "740W"
  },
  "port_security": {
    "enabled": false,
    "max_mac": 2
  }
}
```

#### 9. Role Context (Router)

**File**: `role_router_context.json`
**Priority**: 5
**Applies To**: All Router devices

```json
{
  "role": {
    "name": "Router",
    "tier": "edge"
  },
  "routing": {
    "protocols": ["ospf", "bgp"],
    "ospf": {
      "process_id": 1,
      "area": "0.0.0.0",
      "network_type": "point-to-point"
    },
    "bgp": {
      "as_number": 65001,
      "router_id": "auto"
    }
  },
  "security": {
    "acls_enabled": true,
    "zone_firewall": false
  }
}
```

---

#### Advanced Config Contexts (Weights 5000-5500) ⭐ NEW

These contexts provide **enterprise-grade Layer 2 security features** with comprehensive configuration for advanced security controls. They work in conjunction with the **advanced configuration templates** (`cisco_iosxe_advanced.j2` and `cisco_nxos_advanced.j2`).

#### 10. Advanced Security - Access Switch

**File**: `netbox_config_contexts_advanced.csv` (row 2)
**Weight**: 5000
**Applies To**: All Access Switch devices
**Purpose**: Complete Layer 2 security stack for access layer

**Features Included**:

1. **DHCP Snooping**: Prevents rogue DHCP servers
   - VLAN-based protection (200-299)
   - Rate limiting (15 packets/sec)
   - MAC address verification
   - Database persistence to flash
   - Trust ports: uplinks and trunks

2. **Dynamic ARP Inspection (DAI)**: Prevents ARP spoofing
   - VLAN-based protection (200-299)
   - Triple validation (src-mac, dst-mac, IP)
   - Log buffer (1024 entries, 10s interval)
   - Trust ports: uplinks and trunks

3. **Port Security**: Prevents MAC flooding and CAM table attacks
   - Maximum 3 MAC addresses per port
   - Sticky MAC learning
   - Violation mode: restrict (drops packets, logs)
   - Aging: 120 minutes (inactivity-based)
   - Auto-recovery: 600 seconds

4. **802.1X Network Access Control**: Enterprise authentication
   - RADIUS integration (10.100.50.100-101 for EMEA)
   - Multi-auth and multi-domain modes
   - Guest VLAN (220), Auth-fail VLAN (221), Critical VLAN (222)
   - Timeout configuration (quiet 60s, tx 30s, server 30s)
   - Re-authentication every 3600s (1 hour)

5. **Interface Profiles**: Pre-configured port templates
   - `access_data`: User access (data only, VLAN 200)
   - `access_voice`: User access with voice (data VLAN 200, voice VLAN 210)
   - `trunk_uplink`: Uplink to distribution/core (trusted, root guard)
   - `trunk_server`: Server/ESXi trunk (untrusted, ESXi VLANs)

**Example JSON Structure**:

```json
{
  "security": {
    "dhcp_snooping": {
      "enabled": true,
      "vlan_list": "200-299",
      "information_option": true,
      "rate_limit": 15,
      "verify_mac": true,
      "database": {
        "agent": "flash:/dhcp_snooping.db",
        "write_delay": 60
      },
      "trust_ports": ["uplink", "trunk"]
    },
    "arp_inspection": {
      "enabled": true,
      "vlan_list": "200-299",
      "validate": {
        "src_mac": true,
        "dst_mac": true,
        "ip": true
      },
      "log_buffer": {
        "entries": 1024,
        "interval": 10
      },
      "trust_ports": ["uplink", "trunk"]
    },
    "port_security": {
      "enabled": true,
      "default": {
        "maximum": 3,
        "violation": "restrict",
        "aging_time": 120,
        "aging_type": "inactivity"
      },
      "sticky_mac": true,
      "recovery": {
        "interval": 600,
        "cause": "psecure-violation"
      }
    },
    "dot1x": {
      "enabled": true,
      "system_auth_control": true,
      "radius": {
        "servers": ["10.100.50.100", "10.100.50.101"],
        "timeout": 5,
        "retransmit": 3,
        "key": "DOT1X_RADIUS_KEY"
      },
      "default_port_config": {
        "pae": "authenticator",
        "host_mode": "multi-auth",
        "violation_mode": "restrict",
        "max_reauth_req": 2,
        "timeout": {
          "quiet_period": 60,
          "tx_period": 30,
          "supp_timeout": 30,
          "server_timeout": 30
        },
        "reauthentication": true,
        "reauth_period": 3600
      },
      "guest_vlan": 220,
      "auth_fail_vlan": 221,
      "critical_vlan": 222
    }
  },
  "interface_profiles": {
    "access_data": {
      "description": "User access port - data only",
      "switchport_mode": "access",
      "access_vlan": 200,
      "voice_vlan": null,
      "spanning_tree": {
        "portfast": true,
        "bpduguard": true
      },
      "storm_control": {
        "broadcast": 10,
        "multicast": 10,
        "unicast": 10
      },
      "dhcp_snooping_trust": false,
      "arp_inspection_trust": false,
      "port_security": {
        "enabled": true,
        "maximum": 2
      },
      "dot1x": {
        "enabled": true,
        "host_mode": "multi-auth"
      }
    },
    "access_voice": {
      "description": "User access port - data + voice",
      "switchport_mode": "access",
      "access_vlan": 200,
      "voice_vlan": 210,
      "spanning_tree": {
        "portfast": true,
        "bpduguard": true
      },
      "storm_control": {
        "broadcast": 10,
        "multicast": 10,
        "unicast": 10
      },
      "dhcp_snooping_trust": false,
      "arp_inspection_trust": false,
      "port_security": {
        "enabled": true,
        "maximum": 3
      },
      "dot1x": {
        "enabled": true,
        "host_mode": "multi-domain"
      }
    },
    "trunk_uplink": {
      "description": "Trunk to distribution/core",
      "switchport_mode": "trunk",
      "native_vlan": 1,
      "allowed_vlans": "1,100,200-299",
      "spanning_tree": {
        "portfast": false,
        "bpduguard": false,
        "guard": "root"
      },
      "storm_control": {
        "broadcast": 20,
        "multicast": 20
      },
      "dhcp_snooping_trust": true,
      "arp_inspection_trust": true,
      "port_security": {
        "enabled": false
      }
    },
    "trunk_server": {
      "description": "Trunk to ESXi host",
      "switchport_mode": "trunk",
      "native_vlan": 1,
      "allowed_vlans": "1,10,20,30,40,50,60,70,80",
      "spanning_tree": {
        "portfast": "trunk",
        "bpduguard": false
      },
      "storm_control": {
        "broadcast": 20,
        "multicast": 20
      },
      "dhcp_snooping_trust": false,
      "arp_inspection_trust": false,
      "port_security": {
        "enabled": false
      }
    }
  }
}
```

#### 11. Advanced Security - Distribution Switch

**File**: `netbox_config_contexts_advanced.csv` (row 3)
**Weight**: 5000
**Applies To**: All Distribution Switch devices
**Purpose**: Layer 2 security for distribution layer with SVI gateway support

**Features Included**:

1. **DHCP Snooping**: Distribution layer protection
   - Same as access layer
   - Database persistence
   - Trust configuration for core uplinks

2. **Dynamic ARP Inspection**: Distribution layer ARP protection
   - Same validation as access layer
   - Larger log buffer (2048 entries)
   - Trust configuration for core uplinks

3. **IP Source Guard**: Additional IP spoofing protection
   - VLAN-based (200-299)
   - Binds IP to MAC and port
   - Works with DHCP snooping database

4. **Interface Profiles**: Distribution-specific templates
   - `trunk_access_downlink`: Trunk to access switches (untrusted)
   - `trunk_core_uplink`: Trunk to core switches (trusted, root guard)
   - `svi_gateway`: VLAN gateway interfaces with DHCP relay

**Example JSON Structure**:

```json
{
  "security": {
    "dhcp_snooping": {
      "enabled": true,
      "vlan_list": "200-299",
      "information_option": true,
      "verify_mac": true,
      "database": {
        "agent": "flash:/dhcp_snooping.db",
        "write_delay": 60
      }
    },
    "arp_inspection": {
      "enabled": true,
      "vlan_list": "200-299",
      "validate": {
        "src_mac": true,
        "dst_mac": true,
        "ip": true
      },
      "log_buffer": {
        "entries": 2048,
        "interval": 10
      }
    },
    "ip_source_guard": {
      "enabled": true,
      "vlan_list": "200-299"
    }
  },
  "interface_profiles": {
    "trunk_access_downlink": {
      "description": "Trunk to access switch",
      "switchport_mode": "trunk",
      "native_vlan": 1,
      "allowed_vlans": "1,100,200-299",
      "spanning_tree": {
        "portfast": false,
        "bpduguard": false
      },
      "dhcp_snooping_trust": false,
      "arp_inspection_trust": false
    },
    "trunk_core_uplink": {
      "description": "Trunk to core switch",
      "switchport_mode": "trunk",
      "native_vlan": 1,
      "allowed_vlans": "all",
      "spanning_tree": {
        "portfast": false,
        "bpduguard": false,
        "guard": "root"
      },
      "dhcp_snooping_trust": true,
      "arp_inspection_trust": true
    },
    "svi_gateway": {
      "description": "SVI gateway for VLAN",
      "dhcp_relay": {
        "enabled": true,
        "servers": ["10.100.50.200", "10.101.50.200"]
      },
      "ip_helper": true
    }
  }
}
```

#### 12. DHCP and DNS Servers (Regional)

**File**: `netbox_config_contexts_advanced.csv` (row 4)
**Weight**: 5500
**Applies To**: All devices (global)
**Purpose**: Region-specific DHCP and DNS server addresses

**Regional Server Allocation**:

| Region | DHCP Servers | DNS Servers |
|--------|-------------|-------------|
| EMEA   | 10.100.50.200, 10.100.50.201 | 10.100.50.210, 10.100.50.211 |
| APAC   | 10.101.50.200, 10.101.50.201 | 10.101.50.210, 10.101.50.211 |
| AMER   | 10.102.50.200, 10.102.50.201 | 10.102.50.210, 10.102.50.211 |

**Example JSON Structure**:

```json
{
  "services": {
    "dhcp_servers": {
      "emea": ["10.100.50.200", "10.100.50.201"],
      "apac": ["10.101.50.200", "10.101.50.201"],
      "amer": ["10.102.50.200", "10.102.50.201"]
    },
    "dns_servers": {
      "emea": ["10.100.50.210", "10.100.50.211"],
      "apac": ["10.101.50.210", "10.101.50.211"],
      "amer": ["10.102.50.210", "10.102.50.211"]
    }
  }
}
```

**Usage in Templates**:

Templates use region detection to select appropriate servers:

```jinja2
{% set region = device.site.name.split('-')[0] | lower %}
{% set dhcp_servers = config_context.services.dhcp_servers.get(region, []) %}
{% for server in dhcp_servers %}
 ip helper-address {{ server }}
{% endfor %}
```

#### 13. RADIUS and AAA Servers (Regional)

**File**: `netbox_config_contexts_advanced.csv` (row 5)
**Weight**: 5500
**Applies To**: All devices (global)
**Purpose**: Region-specific RADIUS and TACACS+ authentication servers

**Regional Server Allocation**:

| Region | 802.1X RADIUS | Management RADIUS | TACACS+ |
|--------|---------------|-------------------|---------|
| EMEA   | 10.100.50.100, 10.100.50.101 | 10.100.50.110, 10.100.50.111 | 10.100.50.120, 10.100.50.121 |
| APAC   | 10.101.50.100, 10.101.50.101 | 10.101.50.110, 10.101.50.111 | 10.101.50.120, 10.101.50.121 |
| AMER   | 10.102.50.100, 10.102.50.101 | 10.102.50.110, 10.102.50.111 | 10.102.50.120, 10.102.50.121 |

**Server Purposes**:
- **802.1X RADIUS (.100-.101)**: Network Access Control (NAC) authentication for end devices
- **Management RADIUS (.110-.111)**: Wireless/VPN authentication (future use)
- **TACACS+ (.120-.121)**: Network device management authentication

**Example JSON Structure**:

```json
{
  "aaa": {
    "radius": {
      "dot1x": {
        "emea": ["10.100.50.100", "10.100.50.101"],
        "apac": ["10.101.50.100", "10.101.50.101"],
        "amer": ["10.102.50.100", "10.102.50.101"]
      },
      "management": {
        "emea": ["10.100.50.110", "10.100.50.111"],
        "apac": ["10.101.50.110", "10.101.50.111"],
        "amer": ["10.102.50.110", "10.102.50.111"]
      },
      "timeout": 5,
      "retransmit": 3
    },
    "tacacs": {
      "servers": {
        "emea": ["10.100.50.120", "10.100.50.121"],
        "apac": ["10.101.50.120", "10.101.50.121"],
        "amer": ["10.102.50.120", "10.102.50.121"]
      },
      "timeout": 5,
      "key": "TACACS_SECRET_KEY"
    }
  }
}
```

**Usage in Templates**:

```jinja2
{% set region = device.site.name.split('-')[0] | lower %}
{% set radius_servers = config_context.aaa.radius.dot1x.get(region, []) %}
{% for server in radius_servers %}
radius server DOT1X-{{ loop.index }}
 address ipv4 {{ server }} auth-port 1812 acct-port 1813
 key {{ config_context.security.dot1x.radius.key }}
{% endfor %}
```

---

### Advanced Config Context Assignment Matrix

| Context Name | Weight | Site | Role | Platform | Applies To |
|--------------|--------|------|------|----------|------------|
| **Base Contexts** |
| Global Configuration | 1000 | - | - | - | ALL devices |
| Cisco NX-OS Platform | 2000 | - | - | NX-OS | All NX-OS devices |
| Cisco IOS-XE Platform | 2000 | - | - | IOS-XE | All IOS-XE devices |
| Cisco IOS-XR Platform | 2000 | - | - | IOS-XR | All IOS-XR devices |
| Cisco IOS Platform | 2000 | - | - | IOS | All IOS devices |
| EMEA-DC-ONPREM Site | 3000 | EMEA-DC-ONPREM | - | - | All EMEA-DC-ONPREM devices |
| Core Switch Role | 4000 | - | Core Switch | - | All Core Switches |
| Distribution Switch Role | 4000 | - | Distribution Switch | - | All Distribution Switches |
| Access Switch Role | 4000 | - | Access Switch | - | All Access Switches |
| Router Role | 4000 | - | Router | - | All Routers |
| OOB Router Role | 4000 | - | OOB Router | - | All OOB Routers |
| **Advanced Contexts** ⭐ |
| Advanced Security - Access Switch | 5000 | - | Access Switch | - | All Access Switches |
| Advanced Security - Distribution Switch | 5000 | - | Distribution Switch | - | All Distribution Switches |
| DHCP and DNS Servers | 5500 | - | - | - | ALL devices |
| RADIUS and AAA Servers | 5500 | - | - | - | ALL devices |

**Context Merge Order** (for an Access Switch in EMEA-DC-ONPREM):

1. ✅ Global Configuration (1000)
2. ✅ Cisco IOS-XE Platform (2000) *or* Cisco NX-OS Platform
3. ✅ EMEA-DC-ONPREM Site (3000)
4. ✅ Access Switch Role (4000)
5. ✅ Advanced Security - Access Switch (5000) ⭐ **NEW**
6. ✅ DHCP and DNS Servers (5500) ⭐ **NEW**
7. ✅ RADIUS and AAA Servers (5500) ⭐ **NEW**

---

## Examples

### Example 1: Merged Context for EMEA-DC-ONPREM-CORE-SW01

**Device Attributes:**
- Name: EMEA-DC-ONPREM-CORE-SW01
- Device Type: Nexus 9508
- Platform: NX-OS
- Role: Core Switch
- Site: EMEA-DC-ONPREM

**Merged Context (JSON):**

```json
{
  "global": {
    "organization": "ACME Corporation",
    "managed_by": "NetOps Team",
    "contact_email": "netops@acme.com"
  },
  "logging": {
    "syslog_servers": ["10.255.1.10", "10.255.1.11"],
    "severity": "informational",
    "facility": "local7"
  },
  "aaa": {
    "tacacs_servers": ["10.255.1.20", "10.255.1.21"],
    "tacacs_key": "TACACS_SECRET_KEY"
  },
  "platform": {
    "os": "NX-OS",
    "vendor": "Cisco Systems"
  },
  "features": {
    "required": ["interface-vlan", "lacp", "lldp", "ssh"]
  },
  "site": {
    "name": "EMEA-DC-ONPREM",
    "region": "EMEA",
    "location": "Paris, France",
    "timezone": "Europe/Paris",
    "domain": "emea.onprem.acme.com"
  },
  "ntp": {
    "servers": ["10.10.1.1", "10.10.1.2"],
    "source_interface": "Loopback0"
  },
  "dns": {
    "servers": ["10.10.2.1", "10.10.2.2"],
    "domain": "emea.onprem.acme.com"
  },
  "snmp": {
    "community_ro": "SNMP_RO_COMMUNITY",
    "community_rw": "SNMP_RW_COMMUNITY",
    "location": "EMEA DC ONPREM - Paris FR",
    "contact": "netops-emea@acme.com",
    "trap_servers": ["10.10.3.1", "10.10.3.2"]
  },
  "role": {
    "name": "Core Switch",
    "tier": "core",
    "redundancy": "hsrp"
  },
  "hsrp": {
    "version": 2,
    "group_id": 1,
    "priority_primary": 110,
    "priority_secondary": 100,
    "preempt": true
  },
  "vlans": {
    "management": 100,
    "native": 1,
    "allowed": "1,100,200-299"
  },
  "routing": {
    "ospf": {
      "process_id": 1,
      "area": "0.0.0.0"
    }
  },
  "spanning_tree": {
    "mode": "rapid-pvst",
    "priority": 4096
  },
  "management": {
    "vlan": 100,
    "subnet": "10.10.100.0/24",
    "gateway": "10.10.100.254",
    "ssh_version": 2,
    "enable_scp": true
  },
  "interfaces": {
    "mtu": 9216
  },
  "vtp": {
    "mode": "transparent"
  }
}
```

### Example 2: Config Template for NX-OS (Nexus)

**Template File**: `cisco_nxos_base.j2`

```jinja2
{# Cisco NX-OS Base Configuration Template #}
!
! Device: {{ device.name }}
! Model: {{ device.device_type.model }}
! Site: {{ device.site.name }}
! Role: {{ device.role.name }}
! Generated: {{ request.timestamp|default('Manual') }}
!
! ========================================
! GLOBAL CONFIGURATION
! ========================================
!
hostname {{ device.name }}
!
clock timezone {{ site.timezone|default('UTC') }} 0 0
!
{% if features.required is defined %}
! Enable required features
{% for feature in features.required %}
feature {{ feature }}
{% endfor %}
!
{% endif %}
! ========================================
! VTP CONFIGURATION
! ========================================
!
{% if vtp is defined %}
vtp mode {{ vtp.mode|default('transparent') }}
{% endif %}
!
! ========================================
! SPANNING TREE CONFIGURATION
! ========================================
!
{% if spanning_tree is defined %}
spanning-tree mode {{ spanning_tree.mode|default('rapid-pvst') }}
spanning-tree vlan 1-4094 priority {{ spanning_tree.priority|default(32768) }}
{% endif %}
!
! ========================================
! VLAN CONFIGURATION
! ========================================
!
{% if vlans is defined %}
vlan {{ vlans.management|default(100) }}
  name MANAGEMENT
!
vlan 1
  name DEFAULT
!
{% endif %}
! ========================================
! INTERFACE CONFIGURATION
! ========================================
!
interface mgmt0
  description MANAGEMENT INTERFACE
  vrf member management
  no shutdown
!
interface loopback0
  description LOOPBACK - ROUTER ID
  no shutdown
!
! ========================================
! NTP CONFIGURATION
! ========================================
!
{% if ntp is defined %}
{% for server in ntp.servers %}
ntp server {{ server }} use-vrf management
{% endfor %}
{% if ntp.source_interface is defined %}
ntp source-interface {{ ntp.source_interface }}
{% endif %}
!
{% endif %}
! ========================================
! DNS CONFIGURATION
! ========================================
!
{% if dns is defined %}
ip domain-name {{ dns.domain|default('local') }}
{% for server in dns.servers %}
ip name-server {{ server }} use-vrf management
{% endfor %}
!
{% endif %}
! ========================================
! SNMP CONFIGURATION
! ========================================
!
{% if snmp is defined %}
snmp-server contact {{ snmp.contact|default('netops@acme.com') }}
snmp-server location {{ snmp.location|default(device.site.name) }}
snmp-server community {{ snmp.community_ro|default('public') }} ro
{% if snmp.trap_servers is defined %}
{% for trap_server in snmp.trap_servers %}
snmp-server host {{ trap_server }} traps version 2c {{ snmp.community_rw|default('private') }}
{% endfor %}
{% endif %}
!
{% endif %}
! ========================================
! LOGGING CONFIGURATION
! ========================================
!
{% if logging is defined %}
logging timestamp milliseconds
logging monitor {{ logging.severity|default('informational') }}
logging logfile messages {{ logging.severity|default('informational') }}
{% for syslog_server in logging.syslog_servers %}
logging server {{ syslog_server }} {{ logging.severity|default('informational') }} use-vrf management
{% endfor %}
!
{% endif %}
! ========================================
! AAA CONFIGURATION
! ========================================
!
{% if aaa is defined %}
feature tacacs+
!
{% for tacacs_server in aaa.tacacs_servers %}
tacacs-server host {{ tacacs_server }} key 7 {{ aaa.tacacs_key|default('SECRET') }}
{% endfor %}
!
aaa group server tacacs+ TACACS-GROUP
{% for tacacs_server in aaa.tacacs_servers %}
  server {{ tacacs_server }}
{% endfor %}
  use-vrf management
!
aaa authentication login default group TACACS-GROUP local
aaa authorization config-commands default group TACACS-GROUP local
aaa authorization commands default group TACACS-GROUP local
aaa accounting default group TACACS-GROUP
!
{% endif %}
! ========================================
! ROUTING CONFIGURATION
! ========================================
!
{% if routing is defined %}
{% if routing.ospf is defined %}
router ospf {{ routing.ospf.process_id|default(1) }}
  router-id {{ device.primary_ip4.address.ip|default('1.1.1.1') }}
!
{% endif %}
{% endif %}
! ========================================
! SSH & MANAGEMENT ACCESS
! ========================================
!
{% if management is defined %}
ssh key rsa 2048 force
ip ssh version {{ management.ssh_version|default(2) }}
{% if management.enable_scp %}
feature scp-server
{% endif %}
!
line vty
  exec-timeout 30
  session-limit 5
!
{% endif %}
! ========================================
! BANNER
! ========================================
!
banner motd ^
******************************************
* {{ device.name }}
* {{ device.site.name }} - {{ device.role.name }}
*
* UNAUTHORIZED ACCESS PROHIBITED
* All access is logged and monitored
******************************************
^
!
end
```

### Example 3: Rendered Configuration Output

**Device**: EMEA-DC-ONPREM-CORE-SW01
**Template**: cisco_nxos_base.j2
**Context**: Merged from global + site + platform + role

**Rendered Output**:

```
!
! Device: EMEA-DC-ONPREM-CORE-SW01
! Model: Nexus 9508
! Site: EMEA-DC-ONPREM
! Role: Core Switch
! Generated: 2025-12-06 15:30:00
!
! ========================================
! GLOBAL CONFIGURATION
! ========================================
!
hostname EMEA-DC-ONPREM-CORE-SW01
!
clock timezone Europe/Paris 0 0
!
! Enable required features
feature interface-vlan
feature lacp
feature lldp
feature ssh
!
! ========================================
! VTP CONFIGURATION
! ========================================
!
vtp mode transparent
!
! ========================================
! SPANNING TREE CONFIGURATION
! ========================================
!
spanning-tree mode rapid-pvst
spanning-tree vlan 1-4094 priority 4096
!
! ========================================
! VLAN CONFIGURATION
! ========================================
!
vlan 100
  name MANAGEMENT
!
vlan 1
  name DEFAULT
!
! ========================================
! INTERFACE CONFIGURATION
! ========================================
!
interface mgmt0
  description MANAGEMENT INTERFACE
  vrf member management
  no shutdown
!
interface loopback0
  description LOOPBACK - ROUTER ID
  no shutdown
!
! ========================================
! NTP CONFIGURATION
! ========================================
!
ntp server 10.10.1.1 use-vrf management
ntp server 10.10.1.2 use-vrf management
ntp source-interface Loopback0
!
! ========================================
! DNS CONFIGURATION
! ========================================
!
ip domain-name emea.onprem.acme.com
ip name-server 10.10.2.1 use-vrf management
ip name-server 10.10.2.2 use-vrf management
!
! ========================================
! SNMP CONFIGURATION
! ========================================
!
snmp-server contact netops-emea@acme.com
snmp-server location EMEA DC ONPREM - Paris FR
snmp-server community SNMP_RO_COMMUNITY ro
snmp-server host 10.10.3.1 traps version 2c SNMP_RW_COMMUNITY
snmp-server host 10.10.3.2 traps version 2c SNMP_RW_COMMUNITY
!
! ========================================
! LOGGING CONFIGURATION
! ========================================
!
logging timestamp milliseconds
logging monitor informational
logging logfile messages informational
logging server 10.255.1.10 informational use-vrf management
logging server 10.255.1.11 informational use-vrf management
!
! ========================================
! AAA CONFIGURATION
! ========================================
!
feature tacacs+
!
tacacs-server host 10.255.1.20 key 7 TACACS_SECRET_KEY
tacacs-server host 10.255.1.21 key 7 TACACS_SECRET_KEY
!
aaa group server tacacs+ TACACS-GROUP
  server 10.255.1.20
  server 10.255.1.21
  use-vrf management
!
aaa authentication login default group TACACS-GROUP local
aaa authorization config-commands default group TACACS-GROUP local
aaa authorization commands default group TACACS-GROUP local
aaa accounting default group TACACS-GROUP
!
! ========================================
! ROUTING CONFIGURATION
! ========================================
!
router ospf 1
  router-id 10.10.100.1
!
! ========================================
! SSH & MANAGEMENT ACCESS
! ========================================
!
ssh key rsa 2048 force
ip ssh version 2
feature scp-server
!
line vty
  exec-timeout 30
  session-limit 5
!
! ========================================
! BANNER
! ========================================
!
banner motd ^
******************************************
* EMEA-DC-ONPREM-CORE-SW01
* EMEA-DC-ONPREM - Core Switch
*
* UNAUTHORIZED ACCESS PROHIBITED
* All access is logged and monitored
******************************************
^
!
end
```

---

## Import Process

### Step 1: Prepare CSV Files

NetBox supports importing config contexts via the API or UI. For bulk import, we'll use Python scripts to create contexts via API or export to CSV format.

**Config Context CSV Format:**

```csv
name,weight,description,data,is_active,sites,roles,platforms,device_types
Global Context,1000,"Global settings for all devices","{...JSON...}",True,,,,
EMEA-DC-ONPREM Context,2000,"EMEA DC ONPREM site context","{...JSON...}",True,EMEA-DC-ONPREM,,,
NX-OS Platform Context,3000,"Cisco NX-OS platform defaults","{...JSON...}",True,,,NX-OS,
```

**Config Template Import:**

Templates are typically created via NetBox UI or API (not CSV):
- Navigate to **Customization → Config Templates**
- Create new template
- Assign platform/device type
- Paste Jinja2 template content

### Step 2: Import Config Contexts

```bash
# Using Python script (preferred)
python3 generate_config_contexts.py

# Or using NetBox UI:
# 1. Navigate to Customization → Config Contexts
# 2. Click "Add" for each context
# 3. Paste JSON data
# 4. Set weight and assignments (site, role, platform, etc.)
```

### Step 3: Import Config Templates

```bash
# Using Python script
python3 generate_config_templates.py

# Or using NetBox UI:
# 1. Navigate to Customization → Config Templates
# 2. Click "Add"
# 3. Set name, platform, and template content
# 4. Save
```

### Step 4: Render Configurations

**Via NetBox UI:**
1. Navigate to device (e.g., EMEA-DC-ONPREM-CORE-SW01)
2. Click "Config Context" tab to view merged JSON
3. Click "Render Config" to generate full configuration

**Via API:**

```python
import requests

NETBOX_URL = "https://netbox.example.com"
TOKEN = "your-api-token"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}

# Get rendered config for device
device_id = 1
response = requests.get(
    f"{NETBOX_URL}/api/dcim/devices/{device_id}/render-config/",
    headers=headers
)

config = response.json()
print(config['content'])
```

---

## Files Generated

### Config Context CSV Files

Located in: `lab/config-contexts/`

**Base Config Contexts** (`netbox_config_contexts.csv`):
1. Global Configuration - Universal settings
2. Cisco NX-OS Platform - NX-OS defaults
3. Cisco IOS-XE Platform - IOS-XE defaults
4. Cisco IOS-XR Platform - IOS-XR defaults
5. Cisco IOS Platform - IOS defaults
6. EMEA-DC-ONPREM Site - Site-specific settings
7. Core Switch Role - Core layer configuration
8. Distribution Switch Role - Distribution layer configuration
9. Access Switch Role - Access layer configuration
10. Router Role - Router configuration
11. OOB Router Role - Out-of-band management

**Advanced Config Contexts** ⭐ (`netbox_config_contexts_advanced.csv`):
12. Advanced Security - Access Switch - Layer 2 security for access layer
13. Advanced Security - Distribution Switch - Layer 2 security for distribution layer
14. DHCP and DNS Servers - Regional server addresses
15. RADIUS and AAA Servers - Regional authentication servers

### Config Template Files

Located in: `lab/config-templates/`

**Base Templates**:
1. `cisco_nxos_base.j2` - Nexus NX-OS base template
2. `cisco_iosxe_base.j2` - Catalyst IOS-XE base template
3. `cisco_iosxr_base.j2` - ASR IOS-XR base template
4. `cisco_ios_base.j2` - ISR IOS base template

**Advanced Templates** ⭐:
5. `cisco_iosxe_advanced.j2` - **Complete** IOS-XE template (base + advanced security) - 444 lines
6. `cisco_nxos_advanced.j2` - **Complete** NX-OS template (base + advanced security) - 414 lines

**Template Metadata**:
7. `template_inventory.csv` - Template descriptions and feature lists
8. `README.md` - Template documentation and usage guide

### Python Generation Scripts

Located in root directory:

1. `generate_config_contexts.py` - Creates config contexts via API
2. `generate_config_templates.py` - Creates config templates via API

---

## Next Steps

1. **Customize Context Data**: Update JSON files with actual environment values (IPs, passwords, etc.)
2. **Enhance Templates**: Add interface configs, VLANs, routing protocols
3. **Test Rendering**: Verify rendered configs in NetBox UI
4. **Export Configurations**: Use API to export rendered configs
5. **Integrate with Automation**:
   - Ansible playbooks to deploy configs
   - AWX jobs for scheduled config updates
   - Git version control for templates and contexts
6. **Expand Coverage**: Add contexts and templates for other vendors (Arista, Palo Alto, F5)

---

## Benefits Summary

✅ **Single Source of Truth**: All config data in NetBox
✅ **Consistency**: Same template ensures uniform configs across all devices
✅ **Scalability**: Add new devices automatically inherit contexts based on role/site/platform
✅ **Version Control**: Track changes to contexts and templates over time
✅ **Automation Ready**: Export configs to Ansible/Terraform/AWX for deployment
✅ **Role-Based**: Different configs for different device roles (Core, Distribution, Access)
✅ **Multi-Platform**: Support NX-OS, IOS-XE, IOS-XR, IOS, Arista, and more
✅ **Enterprise Security** ⭐: Advanced L2 security (DHCP snooping, ARP inspection, port security, 802.1X)
✅ **Regional Awareness**: Automatic server selection based on region (EMEA/APAC/AMER)
✅ **Complete Templates**: Standalone templates with base config + security (no separate files needed)
✅ **Interface Intelligence**: Auto-detection of trunk vs access, trusted vs untrusted ports
✅ **Production-Ready**: Templates include all necessary features for enterprise deployment

---

**Document Version**: 2.0
**Last Updated**: 2025-12-12
**Author**: NetOps Team
**Changelog**:
- v2.0 (2025-12-12): Added Advanced Config Contexts (DHCP snooping, ARP inspection, port security, 802.1X) and Advanced Templates
- v1.0 (2025-12-06): Initial release with base config contexts and templates
