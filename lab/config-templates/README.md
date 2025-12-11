# NetBox Configuration Templates

This directory contains Jinja2 configuration templates for network devices, organized by complexity and security level.

## Template Categories

### Base Configuration Templates
Basic device configuration with standard management features.

| Template | Platform | Description |
|----------|----------|-------------|
| `cisco_nxos_base.j2` | NX-OS | Nexus switches - basic config |
| `cisco_iosxe_base.j2` | IOS-XE | Catalyst switches - basic config |
| `cisco_iosxr_base.j2` | IOS-XR | ASR routers - basic config |
| `cisco_ios_base.j2` | IOS | ISR routers - basic config |

### Advanced Security Templates ⭐ NEW
**Complete** configuration templates with base features + enterprise security.

| Template | Platform | Description |
|----------|----------|-------------|
| `cisco_iosxe_advanced.j2` | IOS-XE | Catalyst switches - complete config with advanced security |
| `cisco_nxos_advanced.j2` | NX-OS | Nexus switches - complete config with advanced security |

**Note**: Advanced templates are standalone and include ALL base configuration sections (services, management, protocols) PLUS advanced Layer 2 security features. You do not need to use base templates when using advanced templates.

## Advanced Security Features

The advanced templates include comprehensive Layer 2 security features in addition to all base configuration:

### 1. DHCP Snooping
- **Purpose**: Prevents rogue DHCP servers
- **Features**: VLAN-based, trust ports, rate-limiting, MAC verification

### 2. Dynamic ARP Inspection (DAI)
- **Purpose**: Prevents ARP spoofing
- **Features**: Source/Dest MAC + IP validation, trust ports, logging

### 3. Port Security
- **Purpose**: Prevents MAC flooding
- **Features**: Sticky MAC, violation modes, auto-recovery

### 4. 802.1X Network Access Control
- **Purpose**: Device/user authentication
- **Features**: RADIUS, multi-auth, guest/fail/critical VLANs

### 5. Storm Control
- **Purpose**: Prevents broadcast storms
- **Features**: Broadcast/multicast/unicast thresholds

See full documentation in README sections below.
