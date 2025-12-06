# VMware vSphere Virtualization Infrastructure

## Overview

This document describes the VMware vSphere virtualization infrastructure for the multi-datacenter environment. The infrastructure consists of ESXi hosts, vSphere clusters, and the necessary NetBox configuration to track virtualization resources.

---

## Infrastructure Summary

### ESXi Hosts Distribution

**Total: 78 ESXi hosts across 6 datacenters**

Per datacenter:
- **6 Compute hosts** (Server Hall A) - Dell PowerEdge R750
- **4 Storage hosts** (Server Hall B) - Dell PowerEdge R750 with vSAN
- **3 Management hosts** (Server Hall A) - Cisco UCS C240 M6

### Cluster Types

**3 cluster types per datacenter = 18 total clusters**

1. **Compute Cluster** (Production)
   - 6 ESXi hosts per cluster
   - Dell PowerEdge R750 (2U, dual CPU)
   - Located in Server Hall A (racks R01-R03)
   - Purpose: Production workloads, VMs

2. **Storage Cluster** (Production)
   - 4 ESXi hosts per cluster
   - Dell PowerEdge R750 (2U, dual CPU)
   - Located in Server Hall B (racks R01-R02)
   - Purpose: vSAN storage, storage-intensive workloads

3. **Management Cluster** (Management)
   - 3 ESXi hosts per cluster
   - Cisco UCS C240 M6 (2U)
   - Located in Server Hall A (racks R04-R06)
   - Purpose: vCenter Server, NSX Manager, vRealize Operations

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Datacenter Site                          │
│                (e.g., EMEA-DC-CLOUD)                        │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Compute    │ │   Storage    │ │  Management  │
│   Cluster    │ │   Cluster    │ │   Cluster    │
└──────────────┘ └──────────────┘ └──────────────┘
│                │                │
│ 6 ESXi Hosts │ │ 4 ESXi Hosts │ │ 3 ESXi Hosts │
│ Dell R750    │ │ Dell R750    │ │ Cisco UCS    │
│ Server Hall A│ │ Server Hall B│ │ Server Hall A│
│ Racks R01-R03│ │ Racks R01-R02│ │ Racks R04-R06│
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## Hardware Specifications

### Dell PowerEdge R750 (Compute & Storage)

**Form Factor:**
- 2U rack server
- Dual CPU support
- Up to 4TB RAM

**Use Cases:**
- Compute clusters: General VM workloads
- Storage clusters: vSAN ready with NVMe drives

**Placement:**
- Position U39 and U37 in racks (2U per host)
- 2 hosts per rack

### Cisco UCS C240 M6 (Management)

**Form Factor:**
- 2U rack server
- Dual CPU support
- Up to 3TB RAM

**Use Cases:**
- vCenter Server
- NSX Manager
- vRealize Operations
- Other management infrastructure VMs

**Placement:**
- Position U39 in racks
- 1 host per rack (R04, R05, R06)

---

## Cluster Configuration

### Naming Convention

```
{SITE}-{TYPE}-CLUSTER

Examples:
- EMEA-DC-CLOUD-COMPUTE-CLUSTER
- EMEA-DC-CLOUD-STORAGE-CLUSTER
- EMEA-DC-CLOUD-MGMT-CLUSTER
```

### ESXi Host Naming Convention

```
{SITE}-ESX-{LOCATION}{NUMBER}

Where:
- LOCATION: A (Server Hall A), B (Server Hall B), MGT (Management)
- NUMBER: 01-06 for compute, 01-04 for storage, 01-03 for management

Examples:
- EMEA-DC-CLOUD-ESX-A01 (Compute host 1)
- EMEA-DC-CLOUD-ESX-B01 (Storage host 1)
- EMEA-DC-CLOUD-ESX-MGT01 (Management host 1)
```

---

## Cluster Details by Type

### 1. Compute Cluster

**Purpose:** Production application workloads

**Configuration:**
- **Hosts:** 6 × Dell PowerEdge R750
- **Location:** Server Hall A, racks R01-R03
- **vSphere HA:** Enabled (N+1 redundancy)
- **vSphere DRS:** Enabled (automatic load balancing)
- **Resource Pools:** Dev, Test, Prod

**Host List:**
```
{SITE}-ESX-A01 (Rack R01, U39)
{SITE}-ESX-A02 (Rack R01, U37)
{SITE}-ESX-A03 (Rack R02, U39)
{SITE}-ESX-A04 (Rack R02, U37)
{SITE}-ESX-A05 (Rack R03, U39)
{SITE}-ESX-A06 (Rack R03, U37)
```

### 2. Storage Cluster (vSAN)

**Purpose:** Software-defined storage with vSAN

**Configuration:**
- **Hosts:** 4 × Dell PowerEdge R750
- **Location:** Server Hall B, racks R01-R02
- **vSAN:** Enabled (hybrid or all-flash)
- **Fault Domains:** 2 (2 hosts per fault domain)
- **Storage Policy:** RAID-1 mirroring

**Host List:**
```
{SITE}-ESX-B01 (Rack R01, U39)
{SITE}-ESX-B02 (Rack R01, U37)
{SITE}-ESX-B03 (Rack R02, U39)
{SITE}-ESX-B04 (Rack R02, U37)
```

### 3. Management Cluster

**Purpose:** VMware infrastructure management components

**Configuration:**
- **Hosts:** 3 × Cisco UCS C240 M6
- **Location:** Server Hall A, racks R04-R06
- **vSphere HA:** Enabled (N+1 redundancy)
- **Key VMs:** vCenter, NSX Manager, vROps, vRLI

**Host List:**
```
{SITE}-ESX-MGT01 (Rack R04, U39)
{SITE}-ESX-MGT02 (Rack R05, U39)
{SITE}-ESX-MGT03 (Rack R06, U39)
```

**Management VMs (per site):**
- vCenter Server Appliance
- NSX Manager (3-node cluster)
- vRealize Operations Manager
- vRealize Log Insight
- vRealize Automation (if needed)

---

## NetBox Import Sequence

### Import Order

The virtualization components must be imported in this specific order:

```
1. ESXi Device Types
   ↓
2. ESXi Host Devices
   ↓
3. Cluster Types
   ↓
4. Cluster Groups
   ↓
5. vSphere Clusters
```

### Step-by-Step Import

#### 1. ESXi Device Types
```
DCIM → Device Types → Import
File: lab/virtualization/netbox_esxi_device_types.csv
Records: 3 device types
```

**Device Types:**
- Dell PowerEdge R750 (2U)
- Dell PowerEdge R650 (1U)
- Cisco UCS C240 M6 (2U)

#### 2. ESXi Host Devices
```
DCIM → Devices → Import
File: lab/virtualization/netbox_dc_esxi_hosts.csv
Records: 78 ESXi hosts
```

**Prerequisites:**
- Sites must exist
- Locations must exist (Server Hall A, Server Hall B)
- Racks must exist
- Device types must be imported (step 1)

#### 3. Cluster Types
```
Virtualization → Cluster Types → Import
File: lab/virtualization/netbox_cluster_types.csv
Records: 1 cluster type (VMware vSphere)
```

#### 4. Cluster Groups
```
Virtualization → Cluster Groups → Import
File: lab/virtualization/netbox_cluster_groups.csv
Records: 2 groups (Production, Management)
```

#### 5. vSphere Clusters
```
Virtualization → Clusters → Import
File: lab/virtualization/netbox_vmware_clusters.csv
Records: 18 clusters (3 per datacenter)
```

**Prerequisites:**
- Sites must exist
- Cluster types must be imported (step 3)
- Cluster groups must be imported (step 4)

---

## Post-Import Configuration

### 1. Assign Devices to Clusters

After importing clusters, you need to manually assign ESXi hosts to their respective clusters in NetBox:

**Compute Cluster Hosts:**
```
SITE-ESX-A01 through SITE-ESX-A06 → SITE-COMPUTE-CLUSTER
```

**Storage Cluster Hosts:**
```
SITE-ESX-B01 through SITE-ESX-B04 → SITE-STORAGE-CLUSTER
```

**Management Cluster Hosts:**
```
SITE-ESX-MGT01 through SITE-ESX-MGT03 → SITE-MGMT-CLUSTER
```

### 2. Add Network Interfaces (Optional)

ESXi hosts typically have:
- **Management interfaces:** 2× 1GbE (vMotion, Management)
- **VM Network interfaces:** 2-4× 10GbE or 25GbE
- **vSAN interfaces:** 2× 10GbE or 25GbE (for storage cluster)

### 3. Add Power Connections (Optional)

Each ESXi host has dual power supplies:
- **PSU1** → PDU-A
- **PSU2** → PDU-B

---

## Verification

### Check ESXi Hosts

```sql
-- Verify all ESXi hosts are imported
SELECT site, device_type, COUNT(*)
FROM dcim_device
WHERE role = 'Server' AND device_type LIKE '%R750%' OR device_type LIKE '%UCS%'
GROUP BY site, device_type;

Expected results:
- Each site: 10× Dell PowerEdge R750, 3× Cisco UCS C240 M6
```

### Check Clusters

```sql
-- Verify all clusters are created
SELECT site, name, type, group
FROM virtualization_cluster
ORDER BY site, name;

Expected results:
- 18 clusters total (3 per site)
- Types: VMware vSphere
- Groups: Production (12), Management (6)
```

---

## Capacity Planning

### Per Datacenter Capacity

**Compute Resources:**
- 13 ESXi hosts per site
- Total CPU cores: ~520 cores (assuming 2× 20-core CPUs per host)
- Total RAM: ~6.5TB (assuming 500GB average per host)

**Storage Capacity (vSAN):**
- 4 hosts per storage cluster
- Assuming 8× 1.92TB SSDs per host
- Raw capacity: ~60TB per site
- Usable (with RAID-1): ~30TB per site

**VM Density:**
- Compute cluster: ~150-200 VMs per cluster
- Management cluster: ~20-30 management VMs per cluster

### Total Infrastructure Capacity

**Across 6 datacenters:**
- **Total ESXi hosts:** 78
- **Total clusters:** 18
- **Total CPU cores:** ~3,120 cores
- **Total RAM:** ~39TB
- **Total storage (usable):** ~180TB

---

## High Availability

### vSphere HA Configuration

**Compute Clusters (6 hosts):**
- Admission control: 20% reserved (N+1 failure tolerance)
- Host failures tolerated: 1
- VM restart priority: High/Medium/Low

**Storage Clusters (4 hosts):**
- Admission control: 25% reserved
- Host failures tolerated: 1
- vSAN failures to tolerate (FTT): 1

**Management Clusters (3 hosts):**
- Admission control: 33% reserved
- Host failures tolerated: 1
- All VMs set to highest restart priority

### Network Redundancy

Each ESXi host has:
- Dual management interfaces (vSwitch redundancy)
- Dual VM network interfaces (distributed vSwitch)
- Dual vSAN network interfaces (vSAN traffic isolation)

### Power Redundancy

Each ESXi host has:
- Dual power supplies
- Connected to separate PDUs (PDU-A and PDU-B)
- Each PDU on separate power feed

---

## Best Practices

### 1. Cluster Sizing
- Keep compute clusters at 6-8 hosts for optimal DRS
- Storage clusters at 4-6 hosts for vSAN efficiency
- Management clusters at 3 hosts minimum for HA

### 2. Resource Allocation
- Reserve 20-25% capacity for HA failover
- Use resource pools to organize workloads
- Set memory/CPU reservations for critical VMs

### 3. Maintenance
- Use maintenance mode for ESXi updates
- Schedule vMotion migrations during low-usage windows
- Test failover scenarios regularly

### 4. Monitoring
- Monitor host CPU/memory utilization
- Track vSAN capacity and performance
- Set alerts for HA admission control violations

---

## Summary

### Quick Stats

| Component | Count | Notes |
|-----------|-------|-------|
| **Datacenters** | 6 | EMEA, APAC, AMER (Cloud + OnPrem) |
| **ESXi Hosts** | 78 | 13 per datacenter |
| **vSphere Clusters** | 18 | 3 per datacenter |
| **Compute Hosts** | 36 | Dell PowerEdge R750 |
| **Storage Hosts** | 24 | Dell PowerEdge R750 (vSAN) |
| **Management Hosts** | 18 | Cisco UCS C240 M6 |

### Files Generated

| File | Records | Purpose |
|------|---------|---------|
| netbox_esxi_device_types.csv | 3 | ESXi server device types |
| netbox_dc_esxi_hosts.csv | 78 | Physical ESXi host devices |
| netbox_cluster_types.csv | 1 | VMware vSphere cluster type |
| netbox_cluster_groups.csv | 2 | Production and Management groups |
| netbox_vmware_clusters.csv | 18 | vSphere clusters configuration |

---

## Next Steps

1. **Import into NetBox** (follow import sequence above)
2. **Assign hosts to clusters** (manual step in NetBox UI)
3. **Configure network interfaces** (generate interface CSVs if needed)
4. **Add power connections** (link to existing power infrastructure)
5. **Create virtual machines** (optional - can track VMs in NetBox)
6. **Document vCenter servers** (add as virtual appliances)
7. **Track NSX components** (NSX Managers, Controllers, Edges)

---

## Additional Resources

- VMware vSphere Documentation: https://docs.vmware.com/en/VMware-vSphere/
- NetBox Virtualization: https://docs.netbox.dev/en/stable/models/virtualization/
- vSAN Design Guide: https://core.vmware.com/resource/vmware-vsan-design-guide
