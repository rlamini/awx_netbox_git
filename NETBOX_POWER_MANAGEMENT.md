# NetBox Power Management - Conceptual Guide

## Table of Contents
1. [Introduction to NetBox Power Management](#introduction-to-netbox-power-management)
2. [NetBox Power Philosophy](#netbox-power-philosophy)
3. [Power Component Types](#power-component-types)
4. [Power Relationships](#power-relationships)
5. [Power Tracing](#power-tracing)
6. [Power Capacity Planning](#power-capacity-planning)
7. [Best Practices](#best-practices)

---

## Introduction to NetBox Power Management

NetBox provides comprehensive **power infrastructure modeling** to track electrical distribution from utility service to individual equipment. Unlike network ports that pass data, power components track electrical connectivity and power consumption.

### What NetBox Power Management Provides

✅ **Complete Power Chain Visibility**
- Track power from utility entrance to device PSU
- Model redundant power paths (A-feed, B-feed)
- Visualize power distribution hierarchy

✅ **Capacity Planning**
- Track power draw at device level
- Calculate rack/location power usage
- Identify available capacity

✅ **Redundancy Validation**
- Ensure dual power feeds exist
- Verify A/B feed separation
- Simulate failure scenarios

✅ **Operational Documentation**
- Document which outlet powers which device
- Track circuit breaker assignments
- Map PDU locations and connections

---

## NetBox Power Philosophy

### How NetBox Models Power

NetBox treats power infrastructure as a **hierarchy of connected components**, similar to how it models network connectivity. However, power has unique characteristics:

```
Network Cabling:          Power Distribution:
Interface ↔ Interface     Power Outlet → Power Port
(bidirectional)           (unidirectional)

Data flow both ways       Power flows one way:
                          Source → Consumer
```

### Key Concepts

1. **Power Outlets** = Power **sources** (provide power)
2. **Power Ports** = Power **consumers** (receive power)
3. **Power Cables** = Connect outlets to ports (one direction)
4. **Power Feeds** = Utility connections (top of hierarchy)

### The Power Chain

```
Utility/Generator
    ↓ (provides power)
Power Panel Outlet
    ↓ (cable)
PDU Power Port (inlet)
    ↓ (internal)
PDU Power Outlet
    ↓ (cable)
Device Power Port (PSU)
    ↓ (internal)
Device operates
```

---

## Power Component Types

NetBox has several component types for modeling power infrastructure. Each serves a specific purpose in the power chain.

### 1. Power Panels

**What they are in NetBox:**
Power panels are **devices** (like switches or servers) but represent electrical distribution equipment rather than IT equipment.

**NetBox Implementation:**
- **Object Type**: Device
- **Device Type**: User-defined (e.g., "480V/208V 3-Phase Panel")
- **Location**: Can be assigned to a location but not a rack
- **U-Height**: 0 (zero-U device, doesn't occupy rack space)

**Purpose:**
Power panels represent main electrical distribution panels (breaker panels) that receive utility power and distribute it to PDUs through individual circuit breakers.

**NetBox Fields:**
```
Device:
  - name: "SITE-LOCATION-PANEL-A"
  - device_type: "480V/208V 3-Phase Panel"
  - role: "PDU" or "Power Distribution"
  - site: The datacenter site
  - location: The physical location
  - rack: (empty - not rack-mounted)
  - position: (empty - zero-U)
```

**Key Features:**
- Can have power outlets (circuit breakers)
- Can have power ports (utility input)
- May have associated power feeds
- Tracks incoming utility service

---

### 2. Power Outlets

**What they are in NetBox:**
Power outlets are **components of devices** that **provide power**. They represent physical outlets, receptacles, or circuit breakers.

**NetBox Implementation:**
- **Object Type**: PowerOutlet (device component)
- **Parent**: Must belong to a device (power panel, PDU, UPS)
- **Direction**: Provides power (source)

**Purpose:**
Power outlets represent:
- Circuit breakers on power panels
- Receptacles on PDUs
- Output ports on UPS units
- Any connector that provides power

**NetBox Fields:**
```
PowerOutlet:
  - device: Parent device (e.g., PDU-A)
  - name: "Outlet-01" or "Circuit-01"
  - type: Connector type (e.g., "iec-60320-c13", "nema-l6-30r")
  - power_port: (optional) Input feeding this outlet
  - feed_leg: A, B, or C (for 3-phase distribution)
  - allocated_draw: Watts allocated to this outlet
  - description: Human-readable description
```

**Connector Types:**
NetBox supports standard connector types:
- **IEC 60320**: C13 (common PDU outlet), C19 (high-current)
- **NEMA**: 5-15R (standard US), L6-30R (twist-lock 30A)
- **IEC 60309**: P+N+E variants (international)
- **Hardwired**: Direct connection

**Feed Leg Concept:**
```
3-Phase Distribution:
Panel has 3 power phases: A, B, C

Outlets distributed across phases for load balancing:
  Outlet-01 → Phase A
  Outlet-02 → Phase B
  Outlet-03 → Phase C
  Outlet-04 → Phase A (cycle repeats)
  ...

This prevents overloading a single phase.
```

---

### 3. Power Ports

**What they are in NetBox:**
Power ports are **components of devices** that **consume power**. They represent physical power inlets or PSUs (Power Supply Units).

**NetBox Implementation:**
- **Object Type**: PowerPort (device component)
- **Parent**: Must belong to a device (server, switch, PDU)
- **Direction**: Consumes power (receiver)

**Purpose:**
Power ports represent:
- PSUs on servers and network equipment
- Power inlets on PDUs (where they receive utility power)
- Input ports on UPS units
- Any connector that receives power

**NetBox Fields:**
```
PowerPort:
  - device: Parent device (e.g., "CORE-SW01")
  - name: "PSU1" or "Power-In"
  - type: Connector type (e.g., "iec-60320-c14", "nema-l6-30p")
  - maximum_draw: Maximum watts this port can draw
  - allocated_draw: Actual allocated watts (capacity planning)
  - description: Human-readable description
```

**Connector Types:**
- **IEC 60320**: C14 (common server inlet), C20 (high-current)
- **NEMA**: 5-15P (standard US plug), L6-30P (twist-lock 30A)
- **IEC 60309**: P+N+E variants
- **Hardwired**: Direct connection

**Maximum vs. Allocated Draw:**

```
Maximum Draw:
  - Rated PSU capacity
  - Worst-case power consumption
  - Used for circuit breaker sizing
  - Example: 1400W PSU rating

Allocated Draw:
  - Expected actual usage
  - Based on workload/utilization
  - Typically 60-80% of maximum
  - Example: 980W (70% of 1400W)

Why both?
  - Maximum: Prevents circuit overload
  - Allocated: Realistic capacity planning
```

**Example - Dual PSU Server:**
```
Device: ESX-Server-01

PowerPort 1:
  - name: "PSU1"
  - type: iec-60320-c14
  - maximum_draw: 1400W
  - allocated_draw: 980W
  - Connects to: PDU-A Outlet-05

PowerPort 2:
  - name: "PSU2"
  - type: iec-60320-c14
  - maximum_draw: 1400W
  - allocated_draw: 980W
  - Connects to: PDU-B Outlet-05

Total server power:
  - Maximum: 2800W (both PSUs)
  - Allocated: 1960W (realistic usage)
  - Redundancy: N+1 (can lose one PSU)
```

---

### 4. Power Cables

**What they are in NetBox:**
Power cables are **cable objects** that connect power outlets to power ports. They represent physical power cords or permanent wiring.

**NetBox Implementation:**
- **Object Type**: Cable
- **Type**: Power (distinguishes from network/console cables)
- **Direction**: Outlet (source) → Port (destination)

**Purpose:**
Power cables document the physical electrical connections between power-providing and power-consuming components.

**NetBox Fields:**
```
Cable:
  - label: "RACK-01-PC-0001" (unique identifier)
  - type: "power"
  - status: "connected", "planned", "decommissioned"
  - side_a_device: Device with power outlet
  - side_a_type: "dcim.poweroutlet"
  - side_a_name: "Outlet-01"
  - side_b_device: Device with power port
  - side_b_type: "dcim.powerport"
  - side_b_name: "PSU1"
  - length: Cable length (optional)
  - length_unit: "m" or "ft"
  - color: Cable color (optional, for identification)
```

**Important Rules:**
1. ✅ Can connect: PowerOutlet → PowerPort
2. ❌ Cannot connect: PowerPort → PowerPort (no port-to-port)
3. ❌ Cannot connect: PowerOutlet → PowerOutlet (no outlet-to-outlet)
4. ✅ One direction: Power flows from outlet to port

**Cable Types in Practice:**

```
Feed Cable (Panel → PDU):
  Side A: Power Panel Circuit-05 (PowerOutlet)
  Side B: PDU-A Power-In (PowerPort)
  Purpose: Utility distribution

Equipment Cable (PDU → Device):
  Side A: PDU-A Outlet-03 (PowerOutlet)
  Side B: Server-01 PSU1 (PowerPort)
  Purpose: Device power connection
```

---

### 5. Power Feeds

**What they are in NetBox:**
Power feeds are **special objects** that represent utility power connections. They model the connection between external power sources and power panels.

**NetBox Implementation:**
- **Object Type**: PowerFeed
- **Parent**: Power panel (device)
- **Purpose**: Track utility/generator connections

**Purpose:**
Power feeds represent the entry point of electrical service:
- Utility company service entrance
- Generator outputs
- UPS outputs feeding power panels
- Top of the power hierarchy

**NetBox Fields:**
```
PowerFeed:
  - power_panel: The panel receiving power
  - name: "Utility-A" or "Generator-1"
  - status: "active", "failed", "offline"
  - type: "primary", "redundant"
  - supply: "ac" or "dc"
  - phase: "single-phase" or "three-phase"
  - voltage: Nominal voltage (e.g., 480)
  - amperage: Service amperage (e.g., 400A)
  - max_utilization: Maximum load percentage (e.g., 80%)
  - available_power: Calculated available watts
```

**How Power Feeds Work:**

```
┌──────────────────┐
│  Utility Service │
│   (External)     │
└────────┬─────────┘
         │
    PowerFeed
  ┌──────┴──────┐
  │   Name: "A" │
  │   480V 400A │
  │   192kW     │
  └──────┬──────┘
         ↓
┌────────────────┐
│  Power Panel-A │
│  (NetBox Device)│
└────────────────┘
```

**Power Calculation:**
```
Available Power = Voltage × Amperage × Phases × Max Utilization

Example:
  480V × 400A × √3 × 80% = 265kW available

NetBox automatically calculates:
  - Total available power
  - Allocated power (sum of outlets)
  - Remaining capacity
```

---

## Power Relationships

### How Components Connect

NetBox models power as a **directed acyclic graph** (DAG), meaning:
- Power flows in one direction (source → consumer)
- No circular dependencies (can't power itself)
- Forms a tree structure (hierarchical)

### The Complete Power Hierarchy

```
┌─────────────────────────────────────────────┐
│              Power Feed                     │
│          (Utility/Generator)                │
│         Voltage: 480V, 400A                 │
│         Available: 265kW                    │
└──────────────────┬──────────────────────────┘
                   │ (provides power to)
                   ↓
┌─────────────────────────────────────────────┐
│           Power Panel (Device)              │
│        Type: 480V/208V 3-Phase              │
│        Location: Network Core               │
└──────────────────┬──────────────────────────┘
                   │ (has components)
                   ↓
        ┌──────────┴──────────┐
        ↓                     ↓
┌───────────────┐    ┌───────────────┐
│ Circuit-01    │    │ Circuit-02    │
│ (PowerOutlet) │    │ (PowerOutlet) │
│ 30A, 7.2kW    │    │ 30A, 7.2kW    │
└───────┬───────┘    └───────┬───────┘
        │ (Cable)            │ (Cable)
        ↓                    ↓
┌───────────────┐    ┌───────────────┐
│ PDU-A         │    │ PDU-B         │
│ Power-In      │    │ Power-In      │
│ (PowerPort)   │    │ (PowerPort)   │
│ 7.2kW max     │    │ 7.2kW max     │
└───────┬───────┘    └───────┬───────┘
        │                    │
        ↓                    ↓
┌───────────────┐    ┌───────────────┐
│ PDU-A         │    │ PDU-B         │
│ (Device)      │    │ (Device)      │
│ 24 outlets    │    │ 24 outlets    │
└───────┬───────┘    └───────┬───────┘
        │ (has components)   │
        ↓                    ↓
┌───────────────┐    ┌───────────────┐
│ Outlet-01     │    │ Outlet-01     │
│ (PowerOutlet) │    │ (PowerOutlet) │
│ C13, 300W     │    │ C13, 300W     │
└───────┬───────┘    └───────┬───────┘
        │ (Cable)            │ (Cable)
        ↓                    ↓
┌───────────────┐    ┌───────────────┐
│ Server-01     │    │ Server-01     │
│ PSU1          │    │ PSU2          │
│ (PowerPort)   │    │ (PowerPort)   │
│ 1400W max     │    │ 1400W max     │
└───────────────┘    └───────────────┘
```

### Parent-Child Relationships

**Devices contain components:**
```
Power Panel (Device)
  ├── Circuit-01 (PowerOutlet)
  ├── Circuit-02 (PowerOutlet)
  └── Utility-Feed (PowerPort - if fed by upstream)

PDU (Device)
  ├── Power-In (PowerPort - receives from panel)
  ├── Outlet-01 (PowerOutlet - provides to devices)
  ├── Outlet-02 (PowerOutlet)
  └── ... (24 outlets total)

Server (Device)
  ├── PSU1 (PowerPort - receives from PDU-A)
  └── PSU2 (PowerPort - receives from PDU-B)
```

**Cables connect components:**
```
Cable connects:
  PowerOutlet (Circuit-01 on Panel)
      →
  PowerPort (Power-In on PDU-A)

Cable connects:
  PowerOutlet (Outlet-01 on PDU-A)
      →
  PowerPort (PSU1 on Server-01)
```

### Linked Power Ports and Outlets

Some devices have **both** power ports (input) and power outlets (output):

```
PDU Example:
  ┌─────────────────────┐
  │       PDU-A         │
  │                     │
  │  Power-In ← (Input) │ PowerPort: receives from panel
  │                     │
  │  Outlet-01 → (Out)  │ PowerOutlet: provides to device 1
  │  Outlet-02 → (Out)  │ PowerOutlet: provides to device 2
  │  ...                │
  └─────────────────────┘

UPS Example:
  ┌─────────────────────┐
  │       UPS-1         │
  │                     │
  │  Input-A ← (Input)  │ PowerPort: utility feed A
  │  Input-B ← (Input)  │ PowerPort: utility feed B
  │                     │
  │  Output-1 → (Out)   │ PowerOutlet: to panel 1
  │  Output-2 → (Out)   │ PowerOutlet: to panel 2
  └─────────────────────┘
```

NetBox allows you to **link** PowerPort to PowerOutlet on the same device:

```
PowerOutlet:
  - device: PDU-A
  - name: Outlet-01
  - power_port: Power-In (links to PowerPort on same device)

This tells NetBox:
  "Outlet-01's power comes from Power-In on this PDU"

NetBox can then trace:
  Panel → PDU Power-In → (internal link) → PDU Outlet-01 → Server PSU1
```

---

## Power Tracing

One of NetBox's most powerful features is **power path tracing** - the ability to visualize the complete power chain from utility to device.

### How Power Tracing Works

NetBox follows the cable connections between power outlets and power ports to build a complete power path.

**Simple Trace Example:**
```
Start: Server-01 PSU1
  ↓
Trace upstream (where does power come from?):

  Server-01 PSU1 (PowerPort)
      ↑ (connected via Cable-001)
  PDU-A Outlet-01 (PowerOutlet)
      ↑ (internal link via power_port)
  PDU-A Power-In (PowerPort)
      ↑ (connected via Cable-Feed-A)
  Panel-A Circuit-05 (PowerOutlet)
      ↑ (connected via PowerFeed)
  Utility Service A
```

### Using NetBox Power Trace

**In the NetBox UI:**

1. Navigate to a device (e.g., Server-01)
2. Click "Power" tab
3. Click on a power port (e.g., PSU1)
4. Click "Trace" button

**What you see:**
```
Power Path for Server-01 PSU1:

[Utility Feed A]
    ↓ (Power Feed)
[Panel-A]
    ↓ Cable: Panel-Circuit-05
[PDU-A] Power-In
    ↓ (Internal)
[PDU-A] Outlet-01
    ↓ Cable: PC-0001
[Server-01] PSU1 ← YOU ARE HERE
```

### Redundancy Visualization

For devices with dual PSUs, trace both paths:

```
Server-01 Power Redundancy:

Path A (PSU1):                Path B (PSU2):
Utility Feed A                Utility Feed B
    ↓                             ↓
Panel-A                       Panel-B
    ↓                             ↓
PDU-A                         PDU-B
    ↓                             ↓
Server-01 PSU1               Server-01 PSU2
         ╲                   ╱
          ╲                 ╱
           ╲               ╱
            ╲             ╱
             ┌───────────┐
             │ Server-01 │ ← Powered by BOTH
             │  ONLINE   │
             └───────────┘

If Path A fails → Server stays online via Path B
If Path B fails → Server stays online via Path A
```

### Power Trace API

NetBox provides API endpoints for programmatic power tracing:

```bash
# Trace power for a specific power port
GET /api/dcim/power-ports/{id}/trace/

Response:
[
  {
    "url": "/api/dcim/power-feeds/1/",
    "name": "Utility Feed A",
    "type": "powerfeed"
  },
  {
    "url": "/api/dcim/power-outlets/42/",
    "name": "Circuit-05",
    "device": "Panel-A"
  },
  {
    "url": "/api/dcim/power-ports/100/",
    "name": "Power-In",
    "device": "PDU-A"
  },
  ...
]
```

---

## Power Capacity Planning

NetBox excels at power capacity planning by aggregating power data at multiple levels.

### Device Level

**Power consumption per device:**

```
Device: CORE-SW01

PowerPort: PSU1
  - Maximum Draw: 3000W
  - Allocated Draw: 2100W

PowerPort: PSU2
  - Maximum Draw: 3000W
  - Allocated Draw: 2100W

Total Device Power:
  - Maximum: 6000W (both PSUs)
  - Allocated: 4200W (realistic usage)
  - Redundant: 3000W (single PSU capacity)
```

**Why dual PSU doesn't double power:**

In N+1 redundancy, one PSU can fail without affecting the device. The device draws power from BOTH PSUs simultaneously, splitting the load:

```
Normal Operation:
  PSU1: 2100W (50% of load)
  PSU2: 2100W (50% of load)
  Total: 4200W

PSU1 Fails:
  PSU1: 0W (failed)
  PSU2: 4200W (100% of load, but within 6000W capacity)
  Total: 4200W (no change in power draw)
```

### Rack Level

**Power consumption per rack:**

NetBox can calculate total rack power by summing all devices in the rack:

```
Rack: NET-R01

Devices:
  - CORE-SW01: 4200W allocated
  - FW-01: 3500W allocated
  - RTR-01: 2100W allocated

Total Rack Power:
  - Allocated: 9800W (9.8kW)

PDU Capacity:
  - PDU-A: 7200W capacity
  - PDU-B: 7200W capacity
  - Total: 14400W (14.4kW)

Utilization:
  - Per PDU: 4900W / 7200W = 68%
  - Total: 9800W / 14400W = 68%

Available Capacity:
  - Per PDU: 2300W available
  - Can add: ~2 more 1kW devices
```

### Location Level

**Power consumption by datacenter location:**

```
Location: Network Core

All devices in this location:
  - 8 Core Switches: 33,600W
  - 8 Firewalls: 28,000W
  - 4 Load Balancers: 11,200W
  - 4 Routers: 8,400W

Total: 81,200W (81.2kW allocated)

Power Panels:
  - Panel-A capacity: 302kW (42 circuits × 7.2kW)
  - Panel-B capacity: 302kW
  - Total capacity: 604kW

Utilization: 81.2kW / 604kW = 13%
Available: 522.8kW for growth
```

### Site Level

**Total datacenter power:**

```
Site: EMEA-DC-CLOUD

Total Allocated Power:
  - Network Core: 81.2kW
  - Server Hall A: 102.4kW
  - Server Hall B: 98.6kW
  - Storage: 45.8kW
  - MMR: 14.2kW

Total: 342.2kW allocated

Total Capacity: 1,814kW (60 panels × 30.2kW)
Utilization: 18.9%
Available Growth: 1,471.8kW (430% expansion possible)
```

### NetBox Reports

NetBox can generate power reports:

**1. Power Utilization Report**
```
Shows per-rack power usage:
  Rack          Allocated    Capacity    Utilization
  ────────────────────────────────────────────────────
  NET-R01       9.8kW        14.4kW      68%
  NET-R02       8.2kW        14.4kW      57%
  SRV-A-R01     5.6kW        14.4kW      39%
  ...
```

**2. Power by Location**
```
Shows power by datacenter area:
  Location        Allocated    Capacity    Utilization
  ─────────────────────────────────────────────────────
  Network Core    81.2kW       604kW       13%
  Server Hall A   102.4kW      604kW       17%
  Storage         45.8kW       302kW       15%
  ...
```

**3. Stranded Capacity**
```
Identifies underutilized power resources:
  Resource         Available    Reason
  ──────────────────────────────────────────────────
  Panel-A Circ-20  7.2kW        No PDU connected
  Panel-B Circ-15  7.2kW        No PDU connected
  PDU-A Outlet-18  300W         Empty outlet
  ...
```

**4. Over-Provisioned**
```
Identifies potential issues:
  Device          Allocated    Available   Status
  ───────────────────────────────────────────────────
  PDU-STG-R01-A   6.8kW        7.2kW       ⚠️ 94%
  Panel-B Circ-05 7.1kW        7.2kW       ⚠️ 99%
  ...
```

### Custom Power Queries

Using NetBox API or GraphQL:

```python
# Get total allocated power for a site
from dcim.models import PowerPort

site_power = PowerPort.objects.filter(
    device__site__slug='emea-dc-cloud'
).aggregate(
    total_allocated=Sum('allocated_draw'),
    total_maximum=Sum('maximum_draw')
)

print(f"Site allocated power: {site_power['total_allocated']/1000}kW")
print(f"Site maximum power: {site_power['total_maximum']/1000}kW")
```

---

## Best Practices

### 1. Naming Conventions

**Be Consistent:**

```
✅ Good naming:
  - Power Panels: {SITE}-{LOCATION}-PANEL-{A/B}
  - PDUs: {RACK}-PDU-{A/B}
  - Circuits: Circuit-{01-42}
  - Outlets: Outlet-{01-24}
  - PSUs: PSU{1-2}

❌ Bad naming:
  - Power Panels: Panel 1, PP-A, Main Panel
  - PDUs: PDU_1, pdu-a, P1
  - Mixed numbering: Outlet-1, Outlet-02, Outlet-3
```

### 2. A-Feed / B-Feed Separation

**Always maintain feed separation:**

```
✅ Correct:
  Device PSU1 → PDU-A → Panel-A → Utility A
  Device PSU2 → PDU-B → Panel-B → Utility B

❌ Wrong:
  Device PSU1 → PDU-A → Panel-A → Utility A
  Device PSU2 → PDU-A → Panel-A → Utility A
  (Both PSUs on same feed - no redundancy!)
```

### 3. Power Allocation

**Use realistic allocated values:**

```
✅ Good practice:
  Maximum Draw: 1400W (PSU rating)
  Allocated Draw: 980W (70% typical utilization)

❌ Bad practice:
  Maximum Draw: 1400W
  Allocated Draw: 1400W (assumes 100% - unrealistic)

  or

  Maximum Draw: 1400W
  Allocated Draw: 0W (empty - can't plan capacity)
```

### 4. Load Balancing

**Distribute load across phases:**

```
✅ Good:
  PDU Phase A: 2400W
  PDU Phase B: 2300W
  PDU Phase C: 2400W
  (Balanced load)

❌ Bad:
  PDU Phase A: 5000W
  PDU Phase B: 1000W
  PDU Phase C: 1100W
  (Phase A overloaded)
```

Track this using the `feed_leg` field on PowerOutlets.

### 5. Documentation

**Always document:**

```
PowerOutlet:
  description: "Powers CORE-SW01 PSU1 (primary feed)"

PowerPort:
  description: "Primary PSU - connected to PDU-A"

PowerFeed:
  comments: "Main utility service - 400A breaker in MER"
```

### 6. Power Port Linking

**Link PDU power ports to outlets:**

```
PDU-A:
  PowerPort: Power-In (receives from panel)
  PowerOutlet: Outlet-01
    - power_port: Power-In (links to input)
  PowerOutlet: Outlet-02
    - power_port: Power-In
  ...

This enables complete power tracing.
```

### 7. Regular Audits

**Periodically verify:**

1. All devices have power ports configured
2. All power ports have allocated_draw values
3. Dual-PSU devices connect to different PDUs
4. PDUs connect to different panels
5. Panels connect to different utility feeds
6. No circular power dependencies
7. Power cables have correct terminations

### 8. Change Management

**When adding devices:**

1. ✅ Check rack power capacity first
2. ✅ Verify PDU has available outlets
3. ✅ Ensure both PDUs have capacity (dual PSU)
4. ✅ Update allocated_draw values
5. ✅ Create power cables in NetBox
6. ✅ Verify power path traces correctly

**When removing devices:**

1. ✅ Delete power cables
2. ✅ Mark power ports as available
3. ✅ Update capacity calculations
4. ✅ Document decommission date

---

## Summary

### NetBox Power Components Quick Reference

| Component | Type | Purpose | Direction | Example |
|-----------|------|---------|-----------|---------|
| **PowerFeed** | Object | Utility connection | Provides | "Utility-A 480V 400A" |
| **Power Panel** | Device | Electrical distribution | Provides | "SITE-PANEL-A" |
| **PowerOutlet** | Component | Power source | Provides | "Circuit-01", "Outlet-05" |
| **PowerPort** | Component | Power consumer | Consumes | "PSU1", "Power-In" |
| **Cable** | Object | Connection | One-way | Outlet → Port |

### Power Flow Direction

```
Always one direction:

PowerFeed
    ↓ provides power to
PowerPanel (Device)
    ↓ has
PowerOutlet (Circuit)
    ↓ connected via Cable to
PowerPort (PDU Input)
    ↓ internal link to
PowerOutlet (PDU Outlet)
    ↓ connected via Cable to
PowerPort (Device PSU)
    ↓ powers
Device operates
```

### Key Takeaways

1. **Power flows one way**: From outlets (sources) to ports (consumers)
2. **Components have parents**: Outlets and ports belong to devices
3. **Cables connect components**: Not devices directly
4. **Dual values matter**: Maximum for safety, allocated for planning
5. **Redundancy requires separation**: A-feed and B-feed must be independent
6. **Tracing is powerful**: NetBox can visualize entire power paths
7. **Capacity planning is built-in**: Aggregate power at any level
8. **Documentation is critical**: Use descriptions and comments

---

## Additional Resources

### NetBox Documentation

- **Power Management**: https://docs.netbox.dev/en/stable/models/dcim/power/
- **Power Feeds**: https://docs.netbox.dev/en/stable/models/dcim/powerfeed/
- **Power Panels**: https://docs.netbox.dev/en/stable/models/dcim/powerpanel/
- **REST API**: https://docs.netbox.dev/en/stable/rest-api/overview/

### Industry Standards

- **TIA-942**: Telecommunications Infrastructure Standard for Data Centers
- **ANSI/BICSI 002**: Data Center Design and Implementation Best Practices
- **IEC 60320**: Power connector standards (C13, C14, C19, C20)
- **NEMA**: National Electrical Manufacturers Association standards

### Related NetBox Features

- **Cable Tracing**: Trace network and power connections
- **Custom Fields**: Add facility-specific power tracking
- **Reports**: Generate power utilization reports
- **Webhooks**: Trigger alerts for power threshold violations
- **API**: Automate power capacity checks

---

**Document Version**: 1.0
**Last Updated**: 2024-12-05
**For**: NetBox DCIM Implementation
