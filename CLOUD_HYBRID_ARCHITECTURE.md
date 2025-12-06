# Multi-Cloud Hybrid Architecture

## Overview

This document describes the hybrid cloud architecture connecting on-premises datacenters with multiple cloud providers:

- **EMEA**: On-premises datacenter connected to **Microsoft Azure** via ExpressRoute
- **APAC**: On-premises datacenter connected to **Google Cloud Platform** via VPN IPSec
- **AMER**: On-premises datacenter connected to **Amazon Web Services** via Direct Connect

---

## Architecture Summary

### Regional Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMEA Region                                  │
├─────────────────────────────────────────────────────────────────┤
│  EMEA-DC-ONPREM         ═══ExpressRoute═══►      EMEA-DC-CLOUD │
│  (Physical DC)          1 Gbps                   (Azure)        │
│  - VMware vSphere       via Equinix              - VNets        │
│  - 39 ESXi hosts                                 - VMs/Services │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    APAC Region                                  │
├─────────────────────────────────────────────────────────────────┤
│  APAC-DC-ONPREM         ═══VPN IPSec═══►         APAC-DC-CLOUD │
│  (Physical DC)          2 Tunnels (HA)           (GCP)          │
│  - VMware vSphere       Over Internet            - VPCs         │
│  - 39 ESXi hosts                                 - Compute Eng. │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    AMER Region                                  │
├─────────────────────────────────────────────────────────────────┤
│  AMER-DC-ONPREM         ═══Direct Connect═══►    AMER-DC-CLOUD │
│  (Physical DC)          10 Gbps                  (AWS)          │
│  - VMware vSphere       via Equinix              - VPCs         │
│  - 39 ESXi hosts                                 - EC2/RDS/S3   │
└─────────────────────────────────────────────────────────────────┘
```

---

## On-Premises Infrastructure

### Physical Datacenters (ONPREM Sites)

Each ONPREM datacenter has:
- **Physical racks and servers**
- **VMware vSphere clusters**: 3 clusters (Compute, Storage, Management)
- **ESXi hosts**: 13 hosts per site (39 total)
- **Power infrastructure**: PDUs, power feeds, redundant power
- **Network infrastructure**: Switches, patch panels, structured cabling

**ONPREM Sites:**
1. **EMEA-DC-ONPREM** - Europe on-premises datacenter
2. **APAC-DC-ONPREM** - Asia Pacific on-premises datacenter
3. **AMER-DC-ONPREM** - Americas on-premises datacenter

---

## Cloud Infrastructure

### Cloud Providers by Region

| Region | Cloud Provider | Regions | Connectivity | Bandwidth |
|--------|---------------|---------|--------------|-----------|
| **EMEA** | Microsoft Azure | eu-west-1 (Ireland) | ExpressRoute | 1 Gbps |
| **APAC** | Google Cloud Platform | asia-southeast1 (Singapore) | VPN IPSec | Over Internet |
| **AMER** | Amazon Web Services | us-east-1 (N. Virginia) | Direct Connect | 10 Gbps |

### Cloud Sites (CLOUD Sites)

Cloud sites contain **NO physical infrastructure** (no racks, servers, power). They only contain:
- **VRFs** representing cloud VPCs/VNets
- **IP Prefixes** for cloud subnets
- **Virtual gateway devices** for connectivity
- **Circuit information** for interconnection

**CLOUD Sites:**
1. **EMEA-DC-CLOUD** - Azure eu-west-1
2. **APAC-DC-CLOUD** - GCP asia-southeast1
3. **AMER-DC-CLOUD** - AWS us-east-1

---

## Network Architecture

### EMEA - Azure ExpressRoute

**Topology:**
```
EMEA-DC-ONPREM
      │
      │ (Private Fiber)
      ▼
  Equinix Amsterdam
      │
      │ ExpressRoute
      ▼
Azure ExpressRoute Gateway
      │
      ├─── EMEA-AZURE-PROD-VNET (10.100.0.0/16)
      └─── EMEA-AZURE-MGMT-VNET (10.101.0.0/16)
```

**Circuit Details:**
- **Circuit ID**: EXPRESSROUTE-EMEA-001
- **Provider**: Microsoft Azure (via Equinix)
- **Bandwidth**: 1 Gbps
- **Type**: ExpressRoute Standard
- **BGP Peering**: Private peering enabled
- **Status**: Active

**Azure VNets:**
1. **EMEA-AZURE-PROD-VNET** (10.100.0.0/16)
   - Public subnets: 10.100.1.0/24, 10.100.2.0/24
   - Private subnets: 10.100.10.0/24, 10.100.11.0/24

2. **EMEA-AZURE-MGMT-VNET** (10.101.0.0/16)
   - Management subnet: 10.101.1.0/24
   - GatewaySubnet: 10.101.254.0/24 (ExpressRoute Gateway)

**Gateway:**
- **Device**: EMEA-AZURE-ER-GW-01
- **Type**: Azure ExpressRoute Gateway (Virtual)
- **SKU**: Standard or HighPerformance

---

### APAC - GCP Cloud VPN (IPSec)

**Topology:**
```
APAC-DC-ONPREM
      │
      │ Firewall: APAC-ONPREM-VPN-FW-01
      │ (Palo Alto PA-5220)
      │
      │ (Internet)
      │ IPSec Tunnel 1: 203.0.113.10 → 198.51.100.20
      │ IPSec Tunnel 2: 203.0.113.11 → 198.51.100.21
      ▼
GCP Cloud VPN Gateway (HA)
      │
      ├─── APAC-GCP-PROD-VPC (10.200.0.0/16)
      └─── APAC-GCP-MGMT-VPC (10.201.0.0/16)
```

**VPN Details:**
- **Tunnel 1**: APAC-GCP-VPN-TUNNEL-1
  - OnPrem IP: 203.0.113.10
  - GCP IP: 198.51.100.20
  - Networks: 10.50.0.0/16 ↔ 10.200.0.0/16

- **Tunnel 2**: APAC-GCP-VPN-TUNNEL-2 (Redundant)
  - OnPrem IP: 203.0.113.11
  - GCP IP: 198.51.100.21
  - Networks: 10.50.0.0/16 ↔ 10.200.0.0/16

**Encryption:**
- **Type**: IPSec (Site-to-Site)
- **IKE Version**: IKEv2
- **Encryption**: AES-256-GCM
- **Authentication**: SHA256
- **PFS**: Diffie-Hellman Group 14
- **Rekey Time**: 8 hours

**GCP VPCs:**
1. **APAC-GCP-PROD-VPC** (10.200.0.0/16)
   - Subnets: 10.200.1.0/24, 10.200.2.0/24, 10.200.10.0/24

2. **APAC-GCP-MGMT-VPC** (10.201.0.0/16)
   - Management subnet: 10.201.1.0/24

**Gateways:**
- **GCP Side**:
  - APAC-GCP-VPN-GW-01 (HA VPN interface 1)
  - APAC-GCP-VPN-GW-02 (HA VPN interface 2)
- **OnPrem Side**:
  - APAC-ONPREM-VPN-FW-01 (Palo Alto PA-5220 firewall)

---

### AMER - AWS Direct Connect

**Topology:**
```
AMER-DC-ONPREM
      │
      │ (Dedicated Fiber)
      ▼
  Equinix Ashburn
      │
      │ Direct Connect
      ▼
AWS Direct Connect Gateway
      │
      ├─── AMER-AWS-PROD-VPC (10.300.0.0/16)
      └─── AMER-AWS-MGMT-VPC (10.301.0.0/16)
```

**Circuit Details:**
- **Circuit ID**: DIRECTCONNECT-AMER-001
- **Provider**: Amazon Web Services (via Equinix)
- **Bandwidth**: 10 Gbps
- **Type**: Dedicated Connection
- **Location**: Equinix AS1 (Ashburn, VA)
- **BGP ASN**: OnPrem: 65000, AWS: 65003
- **Status**: Active

**AWS VPCs:**
1. **AMER-AWS-PROD-VPC** (10.300.0.0/16)
   - Public subnets: 10.300.1.0/24, 10.300.2.0/24
   - Private subnets: 10.300.10.0/24, 10.300.11.0/24

2. **AMER-AWS-MGMT-VPC** (10.301.0.0/16)
   - Management subnet: 10.301.1.0/24

**Gateway:**
- **Device**: AMER-AWS-DX-GW-01
- **Type**: AWS Direct Connect Gateway (Virtual)
- **BGP**: Enabled for route propagation

---

## IP Address Management (IPAM)

### VRF Strategy

Each cloud VPC/VNet is represented as a **VRF** in NetBox for routing isolation:

| VRF Name | Route Distinguisher | Cloud Provider | CIDR | Purpose |
|----------|-------------------|----------------|------|---------|
| EMEA-AZURE-PROD-VNET | 65001:100 | Azure | 10.100.0.0/16 | Production workloads |
| EMEA-AZURE-MGMT-VNET | 65001:200 | Azure | 10.101.0.0/16 | Management services |
| APAC-GCP-PROD-VPC | 65002:100 | GCP | 10.200.0.0/16 | Production workloads |
| APAC-GCP-MGMT-VPC | 65002:200 | GCP | 10.201.0.0/16 | Management services |
| AMER-AWS-PROD-VPC | 65003:100 | AWS | 10.300.0.0/16 | Production workloads |
| AMER-AWS-MGMT-VPC | 65003:200 | AWS | 10.301.0.0/16 | Management services |

### IP Allocation Strategy

**Cloud IP Ranges:**
- **10.100.0.0/16** - Azure EMEA Production
- **10.101.0.0/16** - Azure EMEA Management
- **10.200.0.0/16** - GCP APAC Production
- **10.201.0.0/16** - GCP APAC Management
- **10.300.0.0/16** - AWS AMER Production
- **10.301.0.0/16** - AWS AMER Management

**OnPrem IP Ranges** (assumed):
- **10.10.0.0/16** - EMEA-DC-ONPREM
- **10.50.0.0/16** - APAC-DC-ONPREM
- **10.60.0.0/16** - AMER-DC-ONPREM

---

## Connectivity Summary

### Circuit Providers

| Provider | ASN | Service Type | Usage |
|----------|-----|--------------|-------|
| Microsoft Azure | 12076 | ExpressRoute | EMEA connectivity |
| Google Cloud Platform | 15169 | Cloud VPN | APAC connectivity |
| Amazon Web Services | 16509 | Direct Connect | AMER connectivity |
| Equinix | 24115 | Interconnection | ExpressRoute, Direct Connect |
| Megaport | 133937 | Network as a Service | Alternative/backup |

### Active Circuits

| Circuit ID | Type | Provider | Bandwidth | A-Side | Z-Side |
|------------|------|----------|-----------|--------|--------|
| EXPRESSROUTE-EMEA-001 | ExpressRoute | Azure | 1 Gbps | EMEA-DC-ONPREM | EMEA-DC-CLOUD |
| DIRECTCONNECT-AMER-001 | Direct Connect | AWS | 10 Gbps | AMER-DC-ONPREM | AMER-DC-CLOUD |
| APAC-GCP-VPN-TUNNEL-1 | VPN IPSec | GCP | Internet | APAC-DC-ONPREM | APAC-DC-CLOUD |
| APAC-GCP-VPN-TUNNEL-2 | VPN IPSec | GCP | Internet | APAC-DC-ONPREM | APAC-DC-CLOUD |

---

## NetBox Import Sequence

### Prerequisites

Before importing cloud connectivity:
1. All sites must exist (EMEA/APAC/AMER CLOUD and ONPREM)
2. Base infrastructure imported (for ONPREM sites only)

### Import Order for Cloud Infrastructure

```
Step 1: Circuit Providers
   File: lab/circuits/netbox_cloud_providers.csv
   Records: 5 providers
   Menu: Circuits → Providers → Import

Step 2: Cloud VRFs
   File: lab/circuits/netbox_cloud_vrfs.csv
   Records: 6 VRFs (2 per cloud provider)
   Menu: IPAM → VRFs → Import

Step 3: Cloud IP Prefixes
   File: lab/circuits/netbox_cloud_prefixes.csv
   Records: 21 prefixes (subnets)
   Menu: IPAM → Prefixes → Import

Step 4: Cloud Gateway Device Types
   File: lab/virtualization/netbox_cloud_gateway_device_types.csv
   Records: 3 device types
   Menu: Devices → Device Types → Import

Step 5: Cloud Gateway Devices
   File: lab/virtualization/netbox_cloud_gateways.csv
   Records: 5 gateway devices
   Menu: Devices → Devices → Import

Step 6: Cloud Circuits
   File: lab/circuits/netbox_cloud_circuits.csv
   Records: 2 circuits (ExpressRoute, Direct Connect)
   Menu: Circuits → Circuits → Import

Step 7: Circuit Terminations
   File: lab/circuits/netbox_cloud_circuit_terminations.csv
   Records: 4 terminations (A-side, Z-side for each circuit)
   Menu: Circuits → Circuit Terminations → Import

Step 8: VPN Tunnel Documentation (Manual)
   File: lab/circuits/netbox_cloud_vpn_tunnels.csv
   Records: 2 VPN tunnels (APAC)
   Note: Add as config context or journal entries
```

---

## High Availability & Redundancy

### EMEA (Azure ExpressRoute)
- **Circuit Redundancy**: Single 1 Gbps circuit
- **Recommendation**: Add secondary ExpressRoute circuit for HA
- **Failover**: Manual failover to VPN backup (if configured)

### APAC (GCP Cloud VPN)
- **Tunnel Redundancy**: 2 IPSec tunnels (HA VPN)
- **Automatic Failover**: GCP manages tunnel failover
- **Encryption**: Fully redundant with separate endpoints

### AMER (AWS Direct Connect)
- **Circuit Redundancy**: Single 10 Gbps circuit
- **Recommendation**: Add secondary Direct Connect for HA
- **Backup**: VPN over internet as backup path

---

## Monitoring & Operations

### Key Metrics to Monitor

**ExpressRoute (EMEA):**
- Circuit availability
- BGP session status
- Throughput (Gbps)
- Latency to Azure regions

**VPN IPSec (APAC):**
- Tunnel status (both tunnels)
- Encryption key lifetime
- Packet loss and latency
- Firewall connection count

**Direct Connect (AMER):**
- Port status (up/down)
- BGP route advertisements
- Data transfer (GB/month)
- Virtual interface health

### Troubleshooting

**ExpressRoute Issues:**
1. Check circuit provisioning in Azure Portal
2. Verify BGP peering status
3. Check route table propagation
4. Contact Equinix if physical circuit down

**VPN IPSec Issues:**
1. Check Phase 1 (IKE) negotiation
2. Verify Phase 2 (IPSec) SA establishment
3. Check firewall logs for drops
4. Verify PSK (pre-shared key) matches
5. Check NAT-T if behind NAT

**Direct Connect Issues:**
1. Verify LOA-CFA (Letter of Authorization)
2. Check BGP neighbor state
3. Verify Virtual Private Gateway attachment
4. Check route propagation in VPC route tables

---

## Cost Optimization

### EMEA (Azure ExpressRoute)
- **Circuit Cost**: ~$1,000/month (1 Gbps)
- **Data Transfer**: Inbound free, Outbound charged
- **Optimization**: Use VNet peering to avoid extra ExpressRoute costs

### APAC (GCP Cloud VPN)
- **VPN Gateway**: ~$50/month per tunnel
- **Data Transfer**: $0.12/GB egress
- **Optimization**: Lowest cost option, but internet-dependent

### AMER (AWS Direct Connect)
- **Port Cost**: ~$2,000/month (10 Gbps)
- **Data Transfer**: $0.02/GB (data out to DX)
- **Optimization**: High bandwidth = lower per-GB cost

---

## Security Considerations

### ExpressRoute (EMEA)
- **Private Connection**: Traffic does not traverse internet
- **Encryption**: Optional (use MACsec for Layer 2 encryption)
- **NSG**: Azure Network Security Groups on subnets
- **ExpressRoute Microsoft Peering**: Separate from private peering

### VPN IPSec (APAC)
- **Encryption**: AES-256-GCM (strong encryption)
- **Authentication**: SHA256 + PSK
- **Perfect Forward Secrecy**: DH Group 14
- **Firewall**: Palo Alto PA-5220 for threat prevention

### Direct Connect (AMER)
- **Private Connection**: Dedicated fiber, not internet
- **Encryption**: Not encrypted by default (use VPN over DX if needed)
- **Security Groups**: AWS VPC security groups
- **BGP MD5**: Authentication for BGP sessions

---

## Future Enhancements

### Planned Improvements

1. **ExpressRoute HA (EMEA)**
   - Add second ExpressRoute circuit
   - Configure dual BGP sessions

2. **Direct Connect HA (AMER)**
   - Add second Direct Connect port
   - Implement LAG (Link Aggregation Group)

3. **Multi-Cloud Connectivity**
   - Add Azure-to-AWS connectivity
   - Implement GCP-to-Azure peering
   - Use cloud-native transit solutions

4. **SD-WAN Overlay**
   - Deploy SD-WAN for intelligent routing
   - Automatic failover between circuits
   - Application-aware routing

---

## Files Generated

### Cloud Connectivity Files

| File | Records | Purpose |
|------|---------|---------|
| netbox_cloud_providers.csv | 5 | Circuit providers (Azure, GCP, AWS, Equinix, Megaport) |
| netbox_cloud_vrfs.csv | 6 | VRFs for cloud VPCs/VNets |
| netbox_cloud_prefixes.csv | 21 | IP prefixes (subnets) in cloud VPCs |
| netbox_cloud_circuits.csv | 2 | ExpressRoute and Direct Connect circuits |
| netbox_cloud_circuit_terminations.csv | 4 | Circuit endpoints (A-side, Z-side) |
| netbox_cloud_vpn_tunnels.csv | 2 | VPN IPSec tunnel configurations |
| netbox_cloud_vpn_tunnels.json | 2 | VPN tunnel details (JSON format) |
| netbox_cloud_gateway_device_types.csv | 3 | Gateway device types |
| netbox_cloud_gateways.csv | 5 | Virtual gateway devices |

**Total Objects:** 48 cloud connectivity objects

---

## Summary

This hybrid architecture provides:
- ✅ **Multi-cloud presence** across Azure, GCP, and AWS
- ✅ **Dedicated connectivity** for EMEA (ExpressRoute) and AMER (Direct Connect)
- ✅ **Cost-effective VPN** for APAC
- ✅ **IP segregation** using VRFs
- ✅ **Detailed tracking** in NetBox for all cloud resources

**Total Infrastructure:**
- **3 OnPrem Sites** with physical infrastructure
- **3 Cloud Sites** with virtual resources
- **2 Dedicated Circuits** (ExpressRoute + Direct Connect)
- **2 VPN Tunnels** (HA VPN for APAC)
- **6 Cloud VRFs** for network isolation
- **21 Cloud Subnets** across all cloud providers
