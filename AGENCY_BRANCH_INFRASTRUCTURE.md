# Agency Branch Infrastructure - Meraki SD-WAN

## Overview

This document describes the branch office infrastructure using Cisco Meraki SD-WAN technology. The infrastructure connects **292 agency branches** across EMEA, APAC, and AMER regions to their respective regional datacenter hubs.

---

## Infrastructure Summary

### Agency Distribution

| Region | Agencies | Hub Datacenter | VPN Tunnels |
|--------|----------|----------------|-------------|
| **EMEA** | 112 | EMEA-DC-ONPREM | 112 |
| **APAC** | 96 | APAC-DC-ONPREM | 96 |
| **AMER** | 84 | AMER-DC-ONPREM | 84 |
| **Total** | **292** | 3 hubs | 292 |

### Equipment per Agency

Each agency branch has standardized Meraki equipment:
- **2× Meraki MX68** - SD-WAN appliances (HA pair)
- **2× Meraki MS120-8** - 8-port cloud-managed switches
- **4× Meraki MR36** - WiFi 6 access points

**Total Agency Equipment:**
- 584 Meraki MX68 (292 HA pairs)
- 584 Meraki MS120-8 switches
- 1,168 Meraki MR36 access points
- **2,336 total Meraki devices**

### Datacenter Hubs

Each ONPREM datacenter has Meraki MX250 hub concentrators:
- **2× Meraki MX250 per DC** (HA pair)
- **6 total hub devices** (3 regions × 2 devices)

---

## Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                        Regional Hub                               │
│              (EMEA/APAC/AMER-DC-ONPREM)                          │
│                                                                   │
│  ┌────────────────────────────────────────┐                     │
│  │  Meraki MX250 Hub (HA Pair)            │                     │
│  │  - MX-01 (Primary)                     │                     │
│  │  - MX-02 (Secondary)                   │                     │
│  │  Terminates VPN from all agencies      │                     │
│  └────────────────┬───────────────────────┘                     │
│                   │                                              │
└───────────────────┼──────────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┬─────────────┬──────────────┐
        │                       │             │              │
        ▼                       ▼             ▼              ▼
   ┌─────────┐            ┌─────────┐   ┌─────────┐    ┌─────────┐
   │Agency 1 │            │Agency 2 │   │Agency 3 │... │Agency N │
   └─────────┘            └─────────┘   └─────────┘    └─────────┘

Each Agency:
┌────────────────────────────────────────────────────────────────┐
│  Agency Branch (e.g., FR-Agency1)                              │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Internet Connectivity:                                         │
│  ┌────────────┐              ┌────────────┐                   │
│  │  ADSL ISP  │ (Primary)    │  5G ISP    │ (Backup)          │
│  │  50 Mbps   │              │  100 Mbps  │                   │
│  └──────┬─────┘              └──────┬─────┘                   │
│         │                            │                         │
│         └────────────┬───────────────┘                         │
│                      ▼                                          │
│         ┌────────────────────────┐                             │
│         │  Meraki MX68 (HA Pair) │                             │
│         │  - MX-01 (Primary)     │                             │
│         │  - MX-02 (Secondary)   │                             │
│         │  Auto VPN to Hub       │                             │
│         └──────────┬─────────────┘                             │
│                    │                                            │
│         ┌──────────┴──────────┐                                │
│         │                     │                                │
│    ┌────▼────┐          ┌────▼────┐                           │
│    │ MS120-8 │          │ MS120-8 │                           │
│    │ SW-01   │          │ SW-02   │                           │
│    └────┬────┘          └────┬────┘                           │
│         │                    │                                 │
│    ┌────┴────────────────────┴────┐                           │
│    │                               │                           │
│  ┌─▼──┐ ┌─▼──┐ ┌─▼──┐ ┌─▼──┐    │                           │
│  │AP01│ │AP02│ │AP03│ │AP04│    │                           │
│  │MR36│ │MR36│ │MR36│ │MR36│    │                           │
│  └────┘ └────┘ └────┘ └────┘    │                           │
│                                   │                           │
│  WiFi Network + Wired Devices     │                           │
└───────────────────────────────────────────────────────────────┘
```

---

## Equipment Details

### Meraki MX68 - SD-WAN Security Appliance

**Specifications:**
- **Throughput**: 450 Mbps firewall, 200 Mbps VPN
- **WAN Interfaces**: 2× (ADSL + 5G)
- **LAN Ports**: 8× 1GbE
- **PoE+**: Optional (not used in this deployment)
- **High Availability**: Active/Standby

**Deployment:**
- **Quantity**: 2 per agency (584 total)
- **Primary (MX-01)**: Active device handling traffic
- **Secondary (MX-02)**: Standby for failover
- **Virtual IP**: Shared between HA pair

**Functions:**
- SD-WAN routing and load balancing
- Stateful firewall
- Auto VPN to regional hub
- Application-aware QoS
- Content filtering
- Intrusion prevention (optional)

### Meraki MS120-8 - Cloud Managed Switch

**Specifications:**
- **Ports**: 8× 1GbE (RJ-45)
- **PoE**: None (use PoE injectors for APs)
- **Uplink**: 2× SFP (for redundant uplinks to MX)
- **Cloud Management**: Meraki Dashboard

**Deployment:**
- **Quantity**: 2 per agency (584 total)
- **SW-01**: Primary switch
- **SW-02**: Secondary switch for redundancy
- **Uplinks**: Dual uplinks to both MX-01 and MX-02

**Functions:**
- Layer 2 switching
- VLAN support
- Port security
- QoS/CoS
- RSTP for loop prevention

### Meraki MR36 - WiFi 6 Access Point

**Specifications:**
- **WiFi Standard**: 802.11ax (WiFi 6)
- **Radios**: 2×2:2 MU-MIMO
- **Maximum Data Rate**: 1.8 Gbps
- **Power**: 802.3at PoE+
- **Antennas**: Internal omnidirectional

**Deployment:**
- **Quantity**: 4 per agency (1,168 total)
- **Typical Coverage**: 1,500-2,000 sq ft per AP
- **SSIDs**: Corporate, Guest (segregated)
- **Power**: PoE injectors or PoE+ switch

**Functions:**
- Dual-band WiFi (2.4 GHz + 5 GHz)
- WPA3 security
- Client load balancing
- Band steering
- Airtime fairness

### Meraki MX250 - Hub Concentrator

**Specifications:**
- **Throughput**: 2 Gbps firewall, 1.5 Gbps VPN
- **VPN Tunnels**: 1,000+ concurrent
- **WAN Interfaces**: 2× 10GbE SFP+
- **LAN Ports**: 8× 1GbE + 2× 10GbE SFP+

**Deployment:**
- **Quantity**: 2 per datacenter hub (6 total)
- **Location**: Network Core rack in each ONPREM DC
- **Role**: VPN concentrator for all regional agencies

**Functions:**
- Hub for Meraki Auto VPN
- Terminates 100+ agency VPN tunnels
- High-capacity SD-WAN routing
- Centralized policy enforcement

---

## Connectivity

### Internet Circuits per Agency

Each agency has **dual internet circuits** for redundancy:

#### 1. ADSL Circuit (Primary)

| Region | Provider | Bandwidth | Backup | Cost/Month (est) |
|--------|----------|-----------|--------|------------------|
| EMEA | Orange Business Services | 50 Mbps | 5G | €80-120 |
| APAC | Singtel | 50 Mbps | 5G | $100-150 |
| AMER | Verizon Business | 50 Mbps | 5G | $100-150 |

**Circuit Type**: ADSL/VDSL or Fiber (depending on availability)
**SLA**: 99.5% uptime
**Failover**: Automatic to 5G backup

#### 2. 5G Circuit (Backup)

| Region | Provider | Bandwidth | Type | Cost/Month (est) |
|--------|----------|-----------|------|------------------|
| EMEA | Vodafone Business | 100 Mbps | 5G cellular | €50-80 |
| APAC | 3 Business | 100 Mbps | 5G cellular | $60-90 |
| AMER | T-Mobile Business | 100 Mbps | 5G cellular | $70-100 |

**Circuit Type**: 5G cellular with static IP (optional)
**SLA**: 99% uptime
**Failover**: Automatic activation when ADSL fails

### Total Circuits

- **ADSL Circuits**: 292 (50 Mbps each)
- **5G Circuits**: 292 (100 Mbps each)
- **Total**: 584 circuits

### Circuit to Device Connections

Each circuit is connected to a specific WAN interface on the primary Meraki MX (MX-01):

**ADSL Circuit → MX-01 WAN1**
```
Circuit: ADSL-{REGION}-{NUMBER}
   ↓ (Circuit Termination)
Device: {AGENCY}-MX-01
Interface: WAN1 (1000base-t)
```

**5G Circuit → MX-01 WAN2**
```
Circuit: 5G-{REGION}-{NUMBER}
   ↓ (Circuit Termination)
Device: {AGENCY}-MX-01
Interface: WAN2 (1000base-t)
```

**WAN Interfaces per MX:**
Each Meraki MX device has 2 WAN interfaces:
- **WAN1** (Internet 1): Connected to ADSL circuit (primary)
- **WAN2** (Internet 2): Connected to 5G circuit (backup)

**Total WAN Interfaces:**
- 292 agencies × 2 MX × 2 WAN = **1,168 WAN interfaces**
- ADSL connections: 292 (to MX-01 WAN1)
- 5G connections: 292 (to MX-01 WAN2)

**Note:** MX-02 (secondary in HA pair) also has WAN1/WAN2 interfaces but shares the same circuits through HA synchronization. Only MX-01 circuit terminations are tracked in NetBox to avoid duplication.

---

## Meraki Auto VPN

### How It Works

Meraki Auto VPN is a **zero-touch VPN** solution that automatically establishes and maintains IPSec tunnels between spoke (agency) MX devices and hub (datacenter) MX concentrators.

**Key Features:**
- **Automatic Configuration**: No manual IPSec configuration needed
- **Dynamic Tunnels**: Tunnels established automatically when devices come online
- **Multi-Path**: Traffic can use both ADSL and 5G paths simultaneously
- **Active-Active**: Load balancing across multiple WAN links
- **Zero-Touch**: Devices configured via Meraki Dashboard

### VPN Topology

**Hub-and-Spoke:**
- **Hubs**: 3× MX250 pairs (EMEA, APAC, AMER datacenters)
- **Spokes**: 292 agencies (each with MX68 pair)
- **Tunnels**: 292 total (one per agency to regional hub)

**Traffic Flow:**
```
Agency → MX68 → Auto VPN Tunnel → MX250 Hub → Datacenter Resources
```

### Encryption

- **Protocol**: IPSec (IKEv2)
- **Encryption**: AES-256
- **Authentication**: Pre-shared key (PSK) managed by Meraki Dashboard
- **Perfect Forward Secrecy**: Yes (DH Group 14+)

### Failover Behavior

**ADSL Primary Failure:**
1. MX detects ADSL link down
2. Automatic failover to 5G backup (typically < 1 second)
3. VPN tunnel re-established over 5G
4. Traffic continues with no user intervention

**MX Device Failure (Primary to Secondary):**
1. MX-02 (secondary) detects MX-01 (primary) failure
2. MX-02 assumes Virtual IP and becomes active
3. VPN tunnels re-established to MX-02
4. Failover time: ~30 seconds

---

## Regional Hub Configuration

### EMEA-DC-ONPREM Hub

**Devices:**
- EMEA-DC-ONPREM-MERAKI-HUB-MX-01 (Primary)
- EMEA-DC-ONPREM-MERAKI-HUB-MX-02 (Secondary)

**Location:** Network Core, Rack NET-R04

**Terminates VPN for:**
- 112 EMEA agencies (FR, DE, GB, NL, BE, LU, CH, AT, IE, MC, ES, PT, IT, GR, MT, etc.)

**Estimated Traffic:**
- Aggregate bandwidth: ~5.6 Gbps (112 × 50 Mbps)
- Actual usage: ~1-2 Gbps (typical oversubscription)

### APAC-DC-ONPREM Hub

**Devices:**
- APAC-DC-ONPREM-MERAKI-HUB-MX-01 (Primary)
- APAC-DC-ONPREM-MERAKI-HUB-MX-02 (Secondary)

**Location:** Network Core, Rack NET-R04

**Terminates VPN for:**
- 96 APAC agencies

**Estimated Traffic:**
- Aggregate bandwidth: ~4.8 Gbps (96 × 50 Mbps)
- Actual usage: ~1-1.5 Gbps

### AMER-DC-ONPREM Hub

**Devices:**
- AMER-DC-ONPREM-MERAKI-HUB-MX-01 (Primary)
- AMER-DC-ONPREM-MERAKI-HUB-MX-02 (Secondary)

**Location:** Network Core, Rack NET-R04

**Terminates VPN for:**
- 84 AMER agencies

**Estimated Traffic:**
- Aggregate bandwidth: ~4.2 Gbps (84 × 50 Mbps)
- Actual usage: ~1-1.2 Gbps

---

## NetBox Import Sequence

### Import Order

```
Step 1: ISP Providers
   File: lab/agencies/netbox_agency_isp_providers.csv
   Records: 12 ISP providers
   Menu: Circuits → Providers → Import

Step 2: Meraki Device Types (Agency)
   File: lab/agencies/netbox_meraki_device_types.csv
   Records: 3 device types (MX68, MS120-8, MR36)
   Menu: Devices → Device Types → Import

Step 3: Meraki Hub Device Types
   File: lab/agencies/netbox_meraki_hub_device_types.csv
   Records: 1 device type (MX250)
   Menu: Devices → Device Types → Import

Step 4: Agency Meraki Devices
   File: lab/agencies/netbox_agency_meraki_devices.csv
   Records: 2,336 devices (292 agencies × 8)
   Menu: Devices → Devices → Import
   Note: May need to import in batches due to size

Step 5: Datacenter Hub Devices
   File: lab/agencies/netbox_dc_meraki_hubs.csv
   Records: 6 hub devices (3 DCs × 2)
   Menu: Devices → Devices → Import

Step 6: Agency Circuits
   File: lab/agencies/netbox_agency_circuits.csv
   Records: 584 circuits (292 ADSL + 292 5G)
   Menu: Circuits → Circuits → Import
   Note: May need to import in batches

Step 7: Circuit Terminations
   File: lab/agencies/netbox_agency_circuit_terminations.csv
   Records: 584 terminations (A-side only)
   Menu: Circuits → Circuit Terminations → Import

Step 8: Agency Cables
   File: lab/agencies/netbox_agency_cables.csv
   Records: 2,628 cables (292 agencies × 9 cables)
   Menu: DCIM → Cables → Import
   Note: May need to import in batches

Step 9: VPN Tunnel Documentation (Optional)
   File: lab/agencies/netbox_agency_vpn_tunnels.csv
   Records: 292 VPN tunnel configurations
   Note: Import as config context or journal entries
```

---

## Cabling Infrastructure

### Standard Cabling per Agency

Each agency has **9 standardized cables**:

#### 1. HA Cable (1× per agency)
```
MX-01 Port 8 ↔ MX-02 Port 8
- Type: Cat6
- Color: Red
- Length: 1m
- Purpose: HA heartbeat/synchronization
```

#### 2. Uplink Cables (4× per agency)
Full mesh between MX appliances and switches for maximum redundancy:

```
MX-01 Port 1 → SW-01 Port 7
MX-01 Port 2 → SW-02 Port 7
MX-02 Port 1 → SW-01 Port 8
MX-02 Port 2 → SW-02 Port 8
- Type: Cat6
- Color: Blue
- Length: 3m
- Purpose: LAN connectivity
```

**Redundancy Benefits:**
- Each MX connects to both switches
- Each switch has uplinks to both MX devices
- Loss of 1 MX or 1 switch: no impact
- Traffic can path through any combination

#### 3. Access Point Cables (4× per agency)
Switches distribute power and connectivity to WiFi APs:

```
SW-01 Port 1 → AP-01 Port 1
SW-01 Port 2 → AP-02 Port 1
SW-02 Port 1 → AP-03 Port 1
SW-02 Port 2 → AP-04 Port 1
- Type: Cat6
- Color: Green
- Length: 30m (typical ceiling run)
- Purpose: AP connectivity + PoE power
```

**Note:** APs are powered via PoE (Power over Ethernet). No separate power cables needed.

### Cabling Diagram

```
Agency Branch Cabling:

     [WAN]              [WAN]
       │                  │
    ┌──▼───┐  HA Cable ┌──▼───┐
    │MX-01 │◄─────────►│MX-02 │
    │      │   (Red)    │      │
    └──┬┬──┘            └──┬┬──┘
       ││                  ││
    ┌──┘│                  │└──┐
    │   └──────┐    ┌──────┘   │
    │   ┌──────┘    └──────┐   │
    │   │  (Blue uplinks)  │   │
    │   │                  │   │
  ┌─▼───▼─┐              ┌─▼───▼─┐
  │ SW-01 │              │ SW-02 │
  │ MS120 │              │ MS120 │
  └─┬──┬──┘              └─┬──┬──┘
    │  │                   │  │
    │  │   (Green PoE)     │  │
    │  │                   │  │
  ┌─▼┐ └──┐             ┌─▼┐ └──┐
  │AP│    │             │AP│    │
  │01│  ┌─▼┐            │03│  ┌─▼┐
  └──┘  │AP│            └──┘  │AP│
        │02│                  │04│
        └──┘                  └──┘
```

### Cable Color Coding

| Color | Purpose | Devices |
|-------|---------|---------|
| **Red** | HA heartbeat | MX ↔ MX |
| **Blue** | Uplinks | MX → Switches |
| **Green** | Access/PoE | Switches → APs |

### Total Cabling

**Per Agency:**
- 1 HA cable (red)
- 4 uplink cables (blue)
- 4 AP cables (green)
- **Total: 9 cables**

**All Agencies:**
- 292 agencies × 9 cables = **2,628 cables**
- HA cables: 292
- Uplink cables: 1,168
- AP cables: 1,168

---

## Management & Monitoring

### Meraki Dashboard

All devices are managed through the **Meraki Dashboard** (cloud-based):
- **URL**: https://dashboard.meraki.com
- **Organization**: Single organization for all regions
- **Networks**: Separate network per agency + hub networks
- **Templates**: Standard configuration templates for agencies

**Key Dashboard Features:**
- Real-time device status
- VPN tunnel health monitoring
- Traffic analytics
- Client usage statistics
- Automatic firmware updates
- Remote troubleshooting

### Monitoring Metrics

**Per Agency:**
- WAN uptime (ADSL + 5G)
- VPN tunnel status
- Device online/offline status
- Client count (wireless + wired)
- Bandwidth utilization
- Top applications

**Per Hub:**
- VPN tunnel count
- Aggregate bandwidth
- CPU/memory utilization
- Tunnel failure rate

### Alerts

**Critical Alerts:**
- MX device offline > 5 minutes
- Both WAN links down
- VPN tunnel down > 5 minutes
- Switch offline
- 3+ APs offline in same agency

**Warning Alerts:**
- Single WAN link down
- High bandwidth utilization (> 80%)
- Single AP offline
- Firmware update available

---

## High Availability

### Agency Level HA

**MX HA Pair:**
- Active/Standby configuration
- Virtual IP shared between MX-01 and MX-02
- Heartbeat over dedicated link
- Failover time: ~30 seconds

**Dual WAN:**
- ADSL primary, 5G backup
- Automatic failover
- Load balancing (optional)
- Failover time: <1 second

**Switch Redundancy:**
- 2 switches with redundant uplinks to both MX devices
- RSTP for loop prevention
- No switch stacking (independent devices)

**WiFi Redundancy:**
- 4 APs provide overlapping coverage
- Client auto-roaming between APs
- Single AP failure: minimal impact

### Hub Level HA

**MX250 HA Pair:**
- Active/Standby
- Failover: ~30 seconds
- All VPN tunnels fail over automatically

**Datacenter Redundancy:**
- No cross-region failover (regional hubs only)
- Future enhancement: Multi-hub VPN mesh

---

## Security

### Perimeter Security

**MX Firewall Features:**
- Stateful packet inspection
- Layer 7 application control
- Content filtering
- IDS/IPS (optional license)
- Malware protection
- Advanced malware protection (AMP)

**Default Rules:**
- Deny all inbound (from internet)
- Allow outbound with inspection
- Allow VPN traffic to hub
- Allow Meraki cloud management

### WiFi Security

**Corporate SSID:**
- WPA3-Enterprise (802.1X)
- RADIUS authentication to Active Directory
- VLAN: Corporate (isolated from guest)

**Guest SSID:**
- WPA2-PSK or splash page
- Internet-only access (walled garden)
- VLAN: Guest (isolated from corporate)

### Network Segmentation

**VLANs per Agency:**
- VLAN 10: Management (MX, switches, APs)
- VLAN 20: Corporate (employee devices)
- VLAN 30: Guest WiFi
- VLAN 40: Printers/IoT (optional)

---

## Cost Summary

### Equipment Costs (One-time)

| Item | Quantity | Unit Price (est) | Total (est) |
|------|----------|------------------|-------------|
| Meraki MX68 | 584 | $1,500 | $876,000 |
| Meraki MS120-8 | 584 | $500 | $292,000 |
| Meraki MR36 | 1,168 | $800 | $934,400 |
| Meraki MX250 | 6 | $8,000 | $48,000 |
| **Total Equipment** | | | **$2,150,400** |

### Licensing Costs (Annual)

| License | Quantity | Unit Price/Year (est) | Total/Year (est) |
|---------|----------|-----------------------|------------------|
| MX68 Enterprise | 584 | $400 | $233,600 |
| MS120-8 Enterprise | 584 | $150 | $87,600 |
| MR36 Enterprise | 1,168 | $200 | $233,600 |
| MX250 Enterprise | 6 | $2,500 | $15,000 |
| **Total Licensing** | | | **$569,800/year** |

### Circuit Costs (Monthly)

| Circuit Type | Quantity | Unit Price/Month (est) | Total/Month (est) |
|--------------|----------|------------------------|-------------------|
| ADSL 50Mbps | 292 | $100 | $29,200 |
| 5G 100Mbps | 292 | $70 | $20,440 |
| **Total Circuits** | | | **$49,640/month** |
| **Total Circuits/Year** | | | **$595,680/year** |

### Total Cost of Ownership (3 Years)

- **Equipment**: $2,150,400 (one-time)
- **Licensing**: $1,709,400 (3 years)
- **Circuits**: $1,787,040 (3 years)
- **Total**: **$5,646,840** (3 years)

---

## Files Generated

| File | Records | Purpose |
|------|---------|---------|
| netbox_meraki_device_types.csv | 3 | Agency Meraki device types |
| netbox_meraki_hub_device_types.csv | 1 | Hub MX250 device type |
| netbox_agency_meraki_devices.csv | 2,336 | All agency Meraki devices |
| netbox_dc_meraki_hubs.csv | 6 | Datacenter hub MX250 devices |
| netbox_agency_isp_providers.csv | 12 | ISP providers (ADSL + 5G) |
| netbox_agency_circuits.csv | 584 | Agency internet circuits |
| netbox_agency_circuit_terminations.csv | 584 | Circuit terminations |
| netbox_agency_cables.csv | 2,628 | Agency cabling (HA, uplinks, APs) |
| netbox_agency_vpn_tunnels.csv | 292 | VPN tunnel documentation |
| netbox_agency_vpn_tunnels.json | 292 | VPN tunnel details (JSON) |

**Total Objects:** 7,448 agency infrastructure objects (includes 2,628 cables)

---

## Summary

This Meraki SD-WAN infrastructure provides:
- ✅ **292 connected agencies** across 3 global regions
- ✅ **Zero-touch VPN** with Meraki Auto VPN
- ✅ **Dual WAN redundancy** (ADSL + 5G)
- ✅ **Device-level HA** (MX, switches, WiFi)
- ✅ **Fully redundant cabling** (HA, uplinks, APs)
- ✅ **Cloud management** via Meraki Dashboard
- ✅ **Scalable architecture** for future growth

**Total Infrastructure:**
- 2,336 agency devices (MX + switches + APs)
- 6 datacenter hub devices (MX250 concentrators)
- 584 internet circuits (ADSL + 5G)
- 2,628 cables (HA, uplinks, AP connections)
- 292 Auto VPN tunnels to regional hubs
