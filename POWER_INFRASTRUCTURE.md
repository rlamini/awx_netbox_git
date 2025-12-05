# NetBox Power Infrastructure - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [Power Flow Diagram](#power-flow-diagram)
3. [Component Hierarchy](#component-hierarchy)
4. [Power Components Explained](#power-components-explained)
5. [Redundancy Model](#redundancy-model)
6. [Power Capacity Planning](#power-capacity-planning)
7. [Import Sequence](#import-sequence)

---

## Overview

The NetBox power infrastructure provides **complete electrical visibility** from utility service entrance to individual device power supplies. This implementation follows datacenter best practices with **N+1 redundancy** at every level.

**Total Infrastructure:**
- 60 Power Panels (electrical distribution)
- 252 PDUs (rack power distribution)
- 2,520 Panel Circuits
- 6,048 PDU Outlets
- 720 Power Ports (252 PDU inputs + 468 device inputs)
- 720 Power Cables (252 feeds + 468 device cables)

---

## Power Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         UTILITY POWER                                │
│                    (480V/208V 3-Phase Service)                       │
└─────────────────────────────┬───────────────────────────────────────┘
                              │
              ┌───────────────┴────────────────┐
              │                                │
         ┌────▼────┐                      ┌────▼────┐
         │ PANEL-A │                      │ PANEL-B │
         │ Primary │                      │Secondary│
         │ 42 Ckt  │                      │ 42 Ckt  │
         └────┬────┘                      └────┬────┘
              │                                │
    ┌─────────┴─────┐                ┌────────┴──────┐
    │ Power Feed    │                │ Power Feed    │
    │ 30A 250V      │                │ 30A 250V      │
    │ (7.2kW max)   │                │ (7.2kW max)   │
    └─────────┬─────┘                └────────┬──────┘
              │                                │
         ┌────▼────┐                      ┌────▼────┐
         │  PDU-A  │                      │  PDU-B  │
         │ Metered │                      │Switched │
         │24 Outlet│                      │24 Outlet│
         └────┬────┘                      └────┬────┘
              │                                │
    ┌─────────┴─────────┐          ┌──────────┴─────────┐
    │                   │          │                    │
┌───▼───┐          ┌───▼───┐  ┌───▼───┐          ┌───▼───┐
│ C13-1 │   ...    │C13-24 │  │ C13-1 │   ...    │C13-24 │
└───┬───┘          └───┬───┘  └───┬───┘          └───┬───┘
    │                  │          │                  │
┌───▼───┐          ┌───▼───┐  ┌───▼───┐          ┌───▼───┐
│ PSU1  │          │ PSU1  │  │ PSU2  │          │ PSU2  │
│Device1│          │Device2│  │Device1│          │Device2│
└───────┘          └───────┘  └───────┘          └───────┘
```

---

## Component Hierarchy

```
Datacenter Site
└── Location (Network Core, Server Hall A/B, Storage, MMR)
    ├── Power Panel-A (Primary Feed)
    │   ├── Circuit-01 (Power Outlet)
    │   ├── Circuit-02 (Power Outlet)
    │   └── ... (42 circuits total)
    │
    ├── Power Panel-B (Secondary Feed)
    │   ├── Circuit-01 (Power Outlet)
    │   ├── Circuit-02 (Power Outlet)
    │   └── ... (42 circuits total)
    │
    └── Racks (in this location)
        ├── Rack-01
        │   ├── PDU-A (connected to Panel-A)
        │   │   ├── Power-In (Power Port from Panel)
        │   │   ├── Outlet-01 → Device PSU1
        │   │   ├── Outlet-02 → Device PSU1
        │   │   └── ... (24 outlets)
        │   │
        │   └── PDU-B (connected to Panel-B)
        │       ├── Power-In (Power Port from Panel)
        │       ├── Outlet-01 → Device PSU2
        │       ├── Outlet-02 → Device PSU2
        │       └── ... (24 outlets)
        │
        └── Devices (in this rack)
            ├── Device-01
            │   ├── PSU1 → PDU-A Outlet-01
            │   └── PSU2 → PDU-B Outlet-01
            └── Device-02
                ├── PSU1 → PDU-A Outlet-02
                └── PSU2 → PDU-B Outlet-02
```

---

## Power Components Explained

### 1. Power Panels (Electrical Distribution)

**What they are:**
- Main electrical distribution panels (breaker panels)
- Located in each datacenter location
- Receive utility power and distribute to PDUs

**NetBox Implementation:**
- **Device Type**: `480V/208V 3-Phase Panel` or `400V/230V 3-Phase Panel`
- **Manufacturer**: Generic
- **Role**: PDU (power infrastructure)
- **Rack Mounted**: No (Zero-U, facility equipment)
- **Count**: 60 panels (2 per location × 30 locations)

**Power Outlets on Panels:**
- **42 circuits per panel** (3-phase distribution)
- **Outlet Type**: `nema-l6-30r` (30A 250V twist-lock receptacle)
- **Feed Legs**: A, B, C (3-phase balanced load)
- **Purpose**: Provides power feeds to PDUs

**Example:**
```
EMEA-DC-CLOUD-Network-Core-PANEL-A
├── Circuit-01 (Feed Leg A) → PDU #1
├── Circuit-02 (Feed Leg B) → PDU #2
├── Circuit-03 (Feed Leg C) → PDU #3
└── ... (42 circuits, 14% utilized)
```

---

### 2. Power Feeds (Panel → PDU Connections)

**What they are:**
- Heavy-duty power cables from panel to PDU
- Permanent installation (conduit/cable tray)
- Provides utility power to rack PDUs

**NetBox Implementation:**
- **Cable Type**: Power
- **Label**: `{rack}-PF-{id}` (e.g., EMEA-DC-CLOUD-NET-R01-PF-0001)
- **Count**: 252 cables (1 per PDU)

**Connection Pattern:**
```
Side A: Power Panel Circuit
  - Device: EMEA-DC-CLOUD-Network-Core-PANEL-A
  - Type: dcim.poweroutlet
  - Name: Circuit-05

Side B: PDU Power Input
  - Device: EMEA-DC-CLOUD-NET-R01-PDU-A
  - Type: dcim.powerport
  - Name: Power-In
```

**Circuit Utilization:**
- **Maximum circuits per panel**: 42
- **Actual usage**: 6 circuits average (14%)
- **Available capacity**: 36 circuits per panel

---

### 3. PDUs (Rack Power Distribution Units)

**What they are:**
- Rack-mounted power strips with monitoring/switching
- Distribute power to devices in the rack
- Dual PDUs per rack for redundancy

**NetBox Implementation:**
- **Device Types**:
  - `AP8959EU3`: APC Metered Plus (monitoring only)
  - `AP8981`: APC Switched Plus (remote power control)
- **Manufacturer**: APC by Schneider Electric
- **Role**: PDU
- **Position**: Zero-U (vertical mount, no rack space)
- **Count**: 252 PDUs (126 racks × 2 PDUs)

**PDU Types:**
- **PDU-A**: Metered Plus - monitors power consumption
- **PDU-B**: Switched Plus - allows remote on/off control

**Power Capacity per PDU:**
- **Input**: 30A @ 240V = 7,200W (7.2kW)
- **Outlets**: 24× C13 outlets
- **Max per outlet**: ~300W average

**PDU Components:**

#### a) PDU Power Port (Input)
```
Device: EMEA-DC-CLOUD-NET-R01-PDU-A
Name: Power-In
Type: nema-l6-30p (30A plug)
Maximum Draw: 7200W
Receives power from: Panel Circuit
```

#### b) PDU Power Outlets (24 per PDU)
```
Device: EMEA-DC-CLOUD-NET-R01-PDU-A
Outlets:
  - Outlet-01 (Feed Leg A) → Device 1 PSU1
  - Outlet-02 (Feed Leg A) → Device 2 PSU1
  - Outlet-03 (Feed Leg A) → Device 3 PSU1
  ...
  - Outlet-13 (Feed Leg B) → Device 1 PSU1
  ...
  - Outlet-24 (Feed Leg B) → Device 12 PSU1
```

**Feed Leg Distribution:**
- **Outlets 1-12**: Feed Leg A
- **Outlets 13-24**: Feed Leg B
- **Purpose**: Load balancing across 2 phases

---

### 4. Device Power Ports (Equipment PSUs)

**What they are:**
- Power supply units (PSUs) on network/server equipment
- Accept power from PDU outlets
- Dual PSUs for redundancy

**NetBox Implementation:**
- **Count**: 468 power ports (234 devices × 2 PSUs)
- **Port Names**: PSU1, PSU2
- **Type**: `iec-60320-c14` (standard server power inlet)

**Power Draw by Device Type:**

| Device Type | Max Draw/PSU | Allocated/PSU | Total (Dual PSU) |
|-------------|--------------|---------------|------------------|
| **Network Equipment** |
| Nexus 9508 (Chassis) | 3,000W | 2,100W | 4,200W |
| PA-5450 (Firewall) | 2,500W | 1,750W | 3,500W |
| BIG-IP i10800 (LB) | 2,000W | 1,400W | 2,800W |
| ASR 9001 (Router) | 1,500W | 1,050W | 2,100W |
| PA-3260 (Firewall) | 1,200W | 840W | 1,680W |
| DCS-7280SR (Spine) | 800W | 560W | 1,120W |
| Nexus 93180YC (ToR) | 750W | 525W | 1,050W |
| DCS-7050SX3 (Leaf) | 600W | 420W | 840W |
| **Servers** |
| ProLiant DL380 Gen10 | 1,600W | 1,120W | 2,240W |
| PowerEdge R750 | 1,400W | 980W | 1,960W |
| PowerEdge R740 | 1,100W | 770W | 1,540W |
| ProLiant DL360 Gen10 | 800W | 560W | 1,120W |
| **Storage** |
| Pure FlashArray X70 | 2,000W | 1,400W | 2,800W |
| NetApp AFF A400 | 1,800W | 1,260W | 2,520W |
| **Access/Edge** |
| ICX7150-48P | 370W | 259W | 370W (single PSU) |
| ISR 4331 | 250W | 175W | 250W (single PSU) |

**Power Calculation:**
- **Maximum Draw**: Rated PSU capacity (worst case)
- **Allocated Draw**: 70% of maximum (typical datacenter utilization)

**Total Datacenter Power:**
- **Maximum**: 613,200W (613.2 kW)
- **Allocated**: 429,144W (429.1 kW)
- **Per Site**: ~102 kW allocated (6 sites)

---

### 5. Power Cables (Device Connections)

**What they are:**
- Power cords connecting devices to PDU outlets
- IEC C13/C14 standard cables
- Dual cables per device (one to each PDU)

**NetBox Implementation:**
- **Cable Type**: Power
- **Label**: `{rack}-PC-{id}` (e.g., EMEA-DC-CLOUD-NET-R01-PC-0001)
- **Count**: 468 cables (234 devices × 2 PSUs)

**Connection Pattern:**
```
Cable 1 (Primary):
  Side A: Device PSU1
    - Device: EMEA-DC-CLOUD-CORE-SW01
    - Type: dcim.powerport
    - Name: PSU1
  Side B: PDU-A Outlet
    - Device: EMEA-DC-CLOUD-NET-R01-PDU-A
    - Type: dcim.poweroutlet
    - Name: Outlet-01

Cable 2 (Secondary):
  Side A: Device PSU2
    - Device: EMEA-DC-CLOUD-CORE-SW01
    - Type: dcim.powerport
    - Name: PSU2
  Side B: PDU-B Outlet
    - Device: EMEA-DC-CLOUD-NET-R01-PDU-B
    - Type: dcim.poweroutlet
    - Name: Outlet-01
```

---

## Redundancy Model

### A-Feed and B-Feed Separation

```
┌─────────────────────────────────────────────────────────────┐
│                     DATACENTER REDUNDANCY                    │
└─────────────────────────────────────────────────────────────┘

              UTILITY A              UTILITY B
                  │                      │
            ┌─────▼─────┐          ┌─────▼─────┐
            │  PANEL-A  │          │  PANEL-B  │
            │ (Primary) │          │(Secondary)│
            └─────┬─────┘          └─────┬─────┘
                  │                      │
         ┌────────┴────────┐    ┌────────┴────────┐
         │                 │    │                 │
    ┌────▼────┐       ┌────▼────▼────┐       ┌────▼────┐
    │ PDU-A   │       │   PDU-A      │       │ PDU-B   │
    │ Rack 1  │       │   Rack 2     │       │ Rack 1  │
    └────┬────┘       └────┬────┬────┘       └────┬────┘
         │                 │    │                 │
    ┌────▼────┐       ┌────▼────▼────┐       ┌────▼────┐
    │ Device  │       │   Device     │       │ Device  │
    │  PSU1   │       │    PSU1      │       │  PSU2   │
    └─────────┘       └──────────────┘       └─────────┘

    ✓ Active          ✓ Active               ✓ Standby
```

### Failure Scenarios

#### Scenario 1: Single PSU Failure
```
Device: EMEA-DC-CLOUD-CORE-SW01
  ├── PSU1 → PDU-A → Panel-A [FAILED ❌]
  └── PSU2 → PDU-B → Panel-B [ACTIVE ✓]

Result: Device stays ONLINE (N+1 redundancy)
```

#### Scenario 2: PDU Failure
```
Rack: EMEA-DC-CLOUD-NET-R01
  ├── PDU-A → Panel-A [FAILED ❌]
  │   └── All devices lose PSU1
  └── PDU-B → Panel-B [ACTIVE ✓]
      └── All devices on PSU2

Result: All devices stay ONLINE (automatic failover)
```

#### Scenario 3: Power Panel Failure
```
Location: Network Core
  ├── Panel-A [FAILED ❌]
  │   └── All PDU-A offline
  └── Panel-B [ACTIVE ✓]
      └── All PDU-B active

Result: All devices stay ONLINE (location-wide failover)
```

#### Scenario 4: Utility Feed Failure
```
Utility:
  ├── Feed A [FAILED ❌]
  │   └── Panel-A offline → All PDU-A offline
  └── Feed B [ACTIVE ✓]
      └── Panel-B active → All PDU-B active

Result: All devices stay ONLINE (site-wide failover)
```

---

## Power Capacity Planning

### Per-Location Power Summary

Each location (e.g., Network Core, Server Hall A) has:

```
Power Panels: 2 (A and B)
  ├── Capacity: 42 circuits × 7.2kW = 302kW per panel
  └── Utilized: ~6 circuits × 7.2kW = 43kW per panel (14%)

PDUs: 4-12 (depends on location)
  ├── Capacity: 7.2kW per PDU
  └── Devices: 1-3 devices per PDU average

Devices: Varies by location
  └── Total Power: 70-120kW per location
```

### Rack-Level Power

**Typical Network Rack:**
```
Rack: NET-R01
├── PDU-A: 7.2kW capacity
│   ├── Core Switch PSU1: 3.0kW
│   ├── Firewall PSU1: 2.5kW
│   └── Available: 1.7kW (24%)
└── PDU-B: 7.2kW capacity
    ├── Core Switch PSU2: 3.0kW
    ├── Firewall PSU2: 2.5kW
    └── Available: 1.7kW (24%)

Total Rack Power: 11.0kW (dual PSU)
Redundancy: 5.5kW per feed (N+1)
```

**Typical Server Rack:**
```
Rack: SRV-A-R05
├── PDU-A: 7.2kW capacity
│   ├── Server 1 PSU1: 1.4kW
│   ├── Server 2 PSU1: 1.4kW
│   └── Available: 4.4kW (61%)
└── PDU-B: 7.2kW capacity
    ├── Server 1 PSU2: 1.4kW
    ├── Server 2 PSU2: 1.4kW
    └── Available: 4.4kW (61%)

Total Rack Power: 5.6kW (dual PSU)
Redundancy: 2.8kW per feed (N+1)
```

### Growth Capacity

**Panel Capacity:**
- **Available circuits**: 36 per panel (86% free)
- **Max growth**: 36 × 7.2kW = 259kW per panel
- **Can support**: ~150 additional PDUs per location

**PDU Capacity:**
- **Average utilization**: 3 outlets per PDU (12.5%)
- **Available outlets**: 21 per PDU (87.5% free)
- **Max growth**: 7× current device count per rack

**Power Headroom:**
- **Total allocated**: 429 kW
- **Total capacity**: 1,814 kW (60 panels × 30.2kW)
- **Available growth**: 1,385 kW (323% expansion possible)

---

## Import Sequence

### Power Infrastructure Import Order

```
┌─────────────────────────────────────────────────┐
│  Step 1: Power Panel Device Types              │
│  File: netbox_power_panel_device_types.csv     │
│  Records: 2                                      │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 2: Power Panel Devices                   │
│  File: netbox_dc_power_panels.csv              │
│  Records: 60                                     │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 3: Power Panel Outlets (Circuits)        │
│  File: netbox_dc_power_panel_outlets.csv       │
│  Records: 2,520                                  │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 4: PDU Device Types                      │
│  File: netbox_pdu_device_types.csv             │
│  Records: 2                                      │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 5: PDU Devices                           │
│  File: netbox_dc_pdus.csv                      │
│  Records: 252                                    │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 6: PDU Power Ports (Input)               │
│  File: netbox_dc_pdu_power_ports.csv           │
│  Records: 252                                    │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 7: PDU Power Outlets                     │
│  File: netbox_dc_power_outlets.csv             │
│  Records: 6,048                                  │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 8: Device Power Ports (PSUs)             │
│  File: netbox_dc_power_ports.csv               │
│  Records: 468                                    │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 9: Power Feed Cables (Panel→PDU)         │
│  File: netbox_dc_power_feeds.csv               │
│  Records: 252                                    │
└─────────────────────────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│  Step 10: Power Cables (PDU→Device)            │
│  File: netbox_dc_power_cables.csv              │
│  Records: 468                                    │
└─────────────────────────────────────────────────┘
```

### Import Commands

1. **Power Panel Types**
   ```
   DCIM → Device Types → Import
   File: lab/power/netbox_power_panel_device_types.csv
   ```

2. **Power Panels**
   ```
   DCIM → Devices → Import
   File: lab/power/netbox_dc_power_panels.csv
   ```

3. **Panel Circuits**
   ```
   DCIM → Power Outlets → Import
   File: lab/power/netbox_dc_power_panel_outlets.csv
   ```

4. **PDU Types**
   ```
   DCIM → Device Types → Import
   File: lab/power/netbox_pdu_device_types.csv
   ```

5. **PDUs**
   ```
   DCIM → Devices → Import
   File: lab/power/netbox_dc_pdus.csv
   ```

6. **PDU Input Ports**
   ```
   DCIM → Power Ports → Import
   File: lab/power/netbox_dc_pdu_power_ports.csv
   ```

7. **PDU Outlets**
   ```
   DCIM → Power Outlets → Import
   File: lab/power/netbox_dc_power_outlets.csv
   ```

8. **Device PSUs**
   ```
   DCIM → Power Ports → Import
   File: lab/power/netbox_dc_power_ports.csv
   ```

9. **Power Feeds**
   ```
   DCIM → Cables → Import
   File: lab/power/netbox_dc_power_feeds.csv
   ```

10. **Device Power Cables**
    ```
    DCIM → Cables → Import
    File: lab/power/netbox_dc_power_cables.csv
    ```

---

## Verification & Testing

### Post-Import Checks

1. **Power Panels**
   ```
   Navigate: DCIM → Devices → Filter by Role "PDU"
   Expected: 60 power panels visible
   Verify: Each location has PANEL-A and PANEL-B
   ```

2. **Panel Circuits**
   ```
   Navigate: Device detail → Power Outlets
   Expected: 42 circuits per panel
   Verify: Feed legs A, B, C distributed evenly
   ```

3. **Power Feeds**
   ```
   Navigate: DCIM → Cables → Filter by Type "Power"
   Expected: 252 power feed cables
   Verify: Panel Circuit → PDU Power-In connections
   ```

4. **PDUs**
   ```
   Navigate: DCIM → Devices → Filter by Device Type "AP89*"
   Expected: 252 PDUs total
   Verify: Each rack has PDU-A and PDU-B
   ```

5. **PDU Outlets**
   ```
   Navigate: Device detail → Power Outlets
   Expected: 24 outlets per PDU
   Verify: Feed legs A and B (12 each)
   ```

6. **Device Power**
   ```
   Navigate: Device detail → Power Ports
   Expected: PSU1 and PSU2 on each device
   Verify: Wattage values populated
   ```

7. **Power Cables**
   ```
   Navigate: Device detail → Power → Trace
   Expected: PSU1 → PDU-A, PSU2 → PDU-B
   Verify: Complete path visible
   ```

8. **Power Tracing**
   ```
   Test: Trace power from device to panel
   Expected path:
     Device PSU → Power Cable → PDU Outlet →
     PDU Power-In → Feed Cable → Panel Circuit
   ```

### Power Reports in NetBox

After import, you can generate these reports:

1. **Power Utilization by Rack**
   - Shows allocated vs. capacity per PDU
   - Identifies over-provisioned racks

2. **Power Utilization by Location**
   - Shows total power by datacenter area
   - Useful for cooling requirements

3. **Redundancy Status**
   - Lists devices with single PSU (no redundancy)
   - Verifies A/B feed separation

4. **Circuit Loading**
   - Shows panel circuit utilization
   - Identifies available capacity

5. **Power Chain Visualization**
   - Graphical trace from utility to device
   - Validates redundancy paths

---

## Summary Statistics

### Power Infrastructure Total

| Component | Count | Details |
|-----------|-------|---------|
| Power Panels | 60 | 2 per location (A/B) |
| Panel Circuits | 2,520 | 42 per panel |
| PDUs | 252 | 2 per rack (A/B) |
| PDU Input Ports | 252 | 1 per PDU (7.2kW each) |
| PDU Outlets | 6,048 | 24 per PDU (C13 type) |
| Device PSUs | 468 | 2 per device (dual redundancy) |
| Power Feed Cables | 252 | Panel to PDU |
| Device Power Cables | 468 | PDU to device |
| **Total Power Objects** | **9,870** | Complete power chain |

### Power Capacity

| Metric | Value |
|--------|-------|
| Total Panel Capacity | 1,814 kW |
| Total PDU Capacity | 1,814 kW |
| Total Device Maximum | 613 kW |
| Total Device Allocated | 429 kW |
| Average Utilization | 24% |
| Growth Headroom | 323% |

### Redundancy Coverage

| Level | Redundancy | Failover |
|-------|------------|----------|
| Utility Feeds | A + B | Automatic |
| Power Panels | A + B | Automatic |
| PDUs | A + B | Automatic |
| Device PSUs | PSU1 + PSU2 | Automatic |
| **Total Redundancy** | **N+1 at all levels** | **Zero downtime** |

---

## Conclusion

This power infrastructure implementation provides:

✅ **Complete visibility** from utility to device
✅ **Full redundancy** at every level (N+1)
✅ **Accurate power monitoring** with real wattage values
✅ **Capacity planning** with growth headroom tracking
✅ **Failure simulation** to verify redundancy paths
✅ **Standards-compliant** datacenter electrical design

The NetBox database now contains a **complete digital twin** of the electrical infrastructure, enabling:
- Power capacity planning
- Redundancy validation
- Circuit tracing
- Load balancing
- Cost analysis
- Maintenance scheduling
- Regulatory compliance

**Total Objects**: 9,870 power-related components across 6 datacenters.
