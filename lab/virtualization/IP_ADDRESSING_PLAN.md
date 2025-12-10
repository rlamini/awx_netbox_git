# Virtualization Platform IP Addressing Plan

## Network Architecture Overview

The virtualization platform uses a regional IP addressing scheme with dedicated subnets for each network segment.

## Regional IP Ranges

### EMEA Region: 10.100.0.0/16
### APAC Region: 10.101.0.0/16
### AMER Region: 10.102.0.0/16

## Subnet Allocation per Region

| Subnet | EMEA | APAC | AMER | Purpose | VLAN |
|--------|------|------|------|---------|------|
| Out-of-Band Management | 10.100.10.0/24 | 10.101.10.0/24 | 10.102.10.0/24 | ESXi iDRAC/iLO/CIMC interfaces | 10 |
| ESXi Management | 10.100.20.0/24 | 10.101.20.0/24 | 10.102.20.0/24 | ESXi vmk0 management | 20 |
| vMotion Network | 10.100.30.0/24 | 10.101.30.0/24 | 10.102.30.0/24 | ESXi vmk1 vMotion | 30 |
| vSAN Network | 10.100.40.0/24 | 10.101.40.0/24 | 10.102.40.0/24 | ESXi vmk2 vSAN storage | 40 |
| Infrastructure VMs | 10.100.50.0/24 | 10.101.50.0/24 | 10.102.50.0/24 | vCenter, NSX, vROps, vRLI | 50 |
| Application VMs | 10.100.60.0/24 | 10.101.60.0/24 | 10.102.60.0/24 | Web, App, DB, Cache servers | 60 |
| Backend/Data Network | 10.100.70.0/24 | 10.101.70.0/24 | 10.102.70.0/24 | Backend, Cluster, Replication | 70 |
| Storage Network | 10.100.80.0/24 | 10.101.80.0/24 | 10.102.80.0/24 | NFS, File Server storage | 80 |

## EMEA Region (10.100.0.0/16)

### 10.100.10.0/24 - Out-of-Band Management Network
**Purpose:** Physical server management interfaces (iDRAC, iLO, CIMC)
**Gateway:** 10.100.10.1
**DNS:** 10.100.10.2-3
**DHCP Range:** 10.100.10.100-200

| Host | IP Address | Interface | Description |
|------|------------|-----------|-------------|
| ESX-A01 | 10.100.10.11 | iDRAC | Dell iDRAC interface |
| ESX-A02 | 10.100.10.12 | iDRAC | Dell iDRAC interface |
| ESX-A03 | 10.100.10.13 | iDRAC | Dell iDRAC interface |
| ESX-A04 | 10.100.10.14 | iDRAC | Dell iDRAC interface |
| ESX-A05 | 10.100.10.15 | iLO | HPE iLO interface |
| ESX-A06 | 10.100.10.16 | iLO | HPE iLO interface |
| ESX-B01 | 10.100.10.17 | iDRAC | Dell iDRAC interface |
| ESX-B02 | 10.100.10.18 | iDRAC | Dell iDRAC interface |
| ESX-B03 | 10.100.10.19 | iDRAC | Dell iDRAC interface |
| ESX-B04 | 10.100.10.20 | iDRAC | Dell iDRAC interface |
| ESX-MGT01 | 10.100.10.21 | CIMC | Cisco CIMC interface |
| ESX-MGT02 | 10.100.10.22 | CIMC | Cisco CIMC interface |
| ESX-MGT03 | 10.100.10.23 | CIMC | Cisco CIMC interface |

### 10.100.20.0/24 - ESXi Management Network (Reserved)
**Purpose:** ESXi vmk0 management interfaces
**Gateway:** 10.100.20.1
**Note:** ESXi management IPs will be assigned during host configuration

### 10.100.30.0/24 - vMotion Network (Reserved)
**Purpose:** ESXi vmk1 vMotion traffic
**Gateway:** 10.100.30.1
**Note:** Dedicated high-speed network for live VM migration

### 10.100.40.0/24 - vSAN Network (Reserved)
**Purpose:** ESXi vmk2 vSAN storage traffic
**Gateway:** 10.100.40.1
**Note:** Dedicated network for vSAN cluster communication

### 10.100.50.0/24 - Infrastructure VMs Network
**Purpose:** VMware infrastructure and management VMs
**Gateway:** 10.100.50.1
**DNS:** 10.100.50.2-3

| VM | IP Address | DNS Name | Description |
|----|------------|----------|-------------|
| vCenter-01 | 10.100.50.10 | emea-vcenter-01.lab.local | vCenter Server |
| NSX-Manager-01 | 10.100.50.11 | emea-nsx-mgr-01.lab.local | NSX Manager Node 1 |
| NSX-Manager-02 | 10.100.50.12 | emea-nsx-mgr-02.lab.local | NSX Manager Node 2 |
| NSX-Manager-03 | 10.100.50.13 | emea-nsx-mgr-03.lab.local | NSX Manager Node 3 |
| vROps-01 | 10.100.50.20 | emea-vrops-01.lab.local | vRealize Operations |
| vRLI-01 | 10.100.50.21 | emea-vrli-01.lab.local | vRealize Log Insight |
| Backup-Server-01 | 10.100.50.30 | emea-backup-01.lab.local | Veeam Backup Server |
| Jump-Host-01 | 10.100.50.40 | emea-jumphost-01.lab.local | Administrative Jump Host |
| Ansible-Tower-01 | 10.100.50.50 | emea-ansible-01.lab.local | Ansible Automation Platform |
| vSAN-Witness | 10.100.50.80 | emea-vsan-witness.lab.local | vSAN Witness Appliance |
| File-Server-01 | 10.100.50.90 | emea-fileserver-01.lab.local | Windows File Server |
| NFS-Server-01 | 10.100.50.91 | emea-nfs-01.lab.local | NFS Server |

### 10.100.60.0/24 - Application VMs Network
**Purpose:** Production workload VMs (management interface)
**Gateway:** 10.100.60.1
**DNS:** 10.100.60.2-3

| VM | IP Address | DNS Name | Description |
|----|------------|----------|-------------|
| Web-App-01 | 10.100.60.10 | emea-web-01.lab.local | NGINX Web Server 1 |
| Web-App-02 | 10.100.60.11 | emea-web-02.lab.local | NGINX Web Server 2 |
| Web-App-03 | 10.100.60.12 | emea-web-03.lab.local | NGINX Web Server 3 |
| App-Server-01 | 10.100.60.20 | emea-app-01.lab.local | Java App Server 1 |
| App-Server-02 | 10.100.60.21 | emea-app-02.lab.local | Java App Server 2 |
| App-Server-03 | 10.100.60.22 | emea-app-03.lab.local | Java App Server 3 |
| DB-Server-01 | 10.100.60.30 | emea-db-01.lab.local | PostgreSQL Database 1 |
| DB-Server-02 | 10.100.60.31 | emea-db-02.lab.local | PostgreSQL Database 2 |
| DB-Server-03 | 10.100.60.32 | emea-db-03.lab.local | PostgreSQL Database 3 |
| Cache-Server-01 | 10.100.60.40 | emea-cache-01.lab.local | Redis Cache Node 1 |
| Cache-Server-02 | 10.100.60.41 | emea-cache-02.lab.local | Redis Cache Node 2 |
| Cache-Server-03 | 10.100.60.42 | emea-cache-03.lab.local | Redis Cache Node 3 |
| Kafka-Broker-01 | 10.100.60.50 | emea-kafka-01.lab.local | Kafka Broker Node 1 |
| Kafka-Broker-02 | 10.100.60.51 | emea-kafka-02.lab.local | Kafka Broker Node 2 |
| Kafka-Broker-03 | 10.100.60.52 | emea-kafka-03.lab.local | Kafka Broker Node 3 |
| Elasticsearch-01 | 10.100.60.60 | emea-elastic-01.lab.local | Elasticsearch Node 1 |
| Elasticsearch-02 | 10.100.60.61 | emea-elastic-02.lab.local | Elasticsearch Node 2 |
| Elasticsearch-03 | 10.100.60.62 | emea-elastic-03.lab.local | Elasticsearch Node 3 |
| Docker-Host-01 | 10.100.60.70 | emea-docker-01.lab.local | Docker Host 1 |
| Docker-Host-02 | 10.100.60.71 | emea-docker-02.lab.local | Docker Host 2 |
| Docker-Host-03 | 10.100.60.72 | emea-docker-03.lab.local | Docker Host 3 |

### 10.100.70.0/24 - Backend/Data Network
**Purpose:** Backend application traffic, database replication, cluster communication
**Gateway:** 10.100.70.1
**Note:** No DNS names assigned (backend interfaces)

| VM | IP Address | Description |
|----|------------|-------------|
| App-Server-01 (eth1) | 10.100.70.20 | Backend traffic |
| App-Server-02 (eth1) | 10.100.70.21 | Backend traffic |
| App-Server-03 (eth1) | 10.100.70.22 | Backend traffic |
| Backup-Server-01 (eth1) | 10.100.70.30 | Backup data network |
| DB-Server-01 (eth1) | 10.100.70.31 | DB replication |
| DB-Server-02 (eth1) | 10.100.70.32 | DB replication |
| DB-Server-03 (eth1) | 10.100.70.33 | DB replication |
| Cache-Server-01 (eth1) | 10.100.70.40 | Redis cluster |
| Cache-Server-02 (eth1) | 10.100.70.41 | Redis cluster |
| Cache-Server-03 (eth1) | 10.100.70.42 | Redis cluster |
| Kafka-Broker-01 (eth1) | 10.100.70.50 | Kafka data |
| Kafka-Broker-02 (eth1) | 10.100.70.51 | Kafka data |
| Kafka-Broker-03 (eth1) | 10.100.70.52 | Kafka data |
| Elasticsearch-01 (eth1) | 10.100.70.60 | ES cluster |
| Elasticsearch-02 (eth1) | 10.100.70.61 | ES cluster |
| Elasticsearch-03 (eth1) | 10.100.70.62 | ES cluster |
| Docker-Host-01 (eth1) | 10.100.70.70 | Container network |
| Docker-Host-02 (eth1) | 10.100.70.71 | Container network |
| Docker-Host-03 (eth1) | 10.100.70.72 | Container network |

### 10.100.80.0/24 - Storage Network
**Purpose:** NFS/CIFS file access for VMs
**Gateway:** 10.100.80.1

| VM | IP Address | Description |
|----|------------|-------------|
| File-Server-01 (eth1) | 10.100.80.90 | File server storage |
| NFS-Server-01 (eth1) | 10.100.80.91 | NFS storage |

## APAC Region (10.101.0.0/16)

Identical structure to EMEA, with 10.101.x.x addressing scheme.

### Key Networks:
- **10.101.10.0/24** - OOB Management
- **10.101.20.0/24** - ESXi Management
- **10.101.30.0/24** - vMotion
- **10.101.40.0/24** - vSAN
- **10.101.50.0/24** - Infrastructure VMs
- **10.101.60.0/24** - Application VMs
- **10.101.70.0/24** - Backend/Data
- **10.101.80.0/24** - Storage

## AMER Region (10.102.0.0/16)

Identical structure to EMEA and APAC, with 10.102.x.x addressing scheme.

### Key Networks:
- **10.102.10.0/24** - OOB Management
- **10.102.20.0/24** - ESXi Management
- **10.102.30.0/24** - vMotion
- **10.102.40.0/24** - vSAN
- **10.102.50.0/24** - Infrastructure VMs
- **10.102.60.0/24** - Application VMs
- **10.102.70.0/24** - Backend/Data
- **10.102.80.0/24** - Storage

## DNS Configuration

### Primary DNS Servers:
- **EMEA:** 10.100.50.2, 10.100.50.3
- **APAC:** 10.101.50.2, 10.101.50.3
- **AMER:** 10.102.50.2, 10.102.50.3

### DNS Domain:
- **lab.local** - Internal lab domain

### DNS Zones:
- **Forward Zone:** lab.local
- **Reverse Zones:**
  - 10.100.in-addr.arpa (EMEA)
  - 10.101.in-addr.arpa (APAC)
  - 10.102.in-addr.arpa (AMER)

## Network Services

### Gateway Addresses (.1 in each subnet):
- OOB Management: x.x.10.1
- ESXi Management: x.x.20.1
- vMotion: x.x.30.1
- vSAN: x.x.40.1
- Infrastructure VMs: x.x.50.1
- Application VMs: x.x.60.1
- Backend/Data: x.x.70.1
- Storage: x.x.80.1

### DHCP Ranges (Reserved):
- Each network reserves .100-.200 for DHCP
- Static assignments use .10-.99 range

## MTU Configuration

| Network | MTU | Notes |
|---------|-----|-------|
| OOB Management | 1500 | Standard Ethernet |
| ESXi Management | 1500 | Standard Ethernet |
| vMotion | 9000 | Jumbo frames enabled |
| vSAN | 9000 | Jumbo frames enabled |
| Infrastructure VMs | 1500 | Standard Ethernet |
| Application VMs | 1500 | Standard Ethernet |
| Backend/Data | 9000 | Jumbo frames for performance |
| Storage | 9000 | Jumbo frames for NFS/CIFS |

## VLAN Configuration

All networks are configured with corresponding VLANs matching the third octet:
- VLAN 10: OOB Management
- VLAN 20: ESXi Management
- VLAN 30: vMotion
- VLAN 40: vSAN
- VLAN 50: Infrastructure VMs
- VLAN 60: Application VMs
- VLAN 70: Backend/Data
- VLAN 80: Storage

## Security Zones

| Zone | Networks | Trust Level | Description |
|------|----------|-------------|-------------|
| Management | 10.x.10.0/24, 10.x.20.0/24 | High | Physical and ESXi management |
| Infrastructure | 10.x.50.0/24 | High | VMware infrastructure components |
| Production | 10.x.60.0/24 | Medium | Application workloads |
| Backend | 10.x.70.0/24 | Medium-High | Backend application traffic |
| Storage | 10.x.30.0/24, 10.x.40.0/24, 10.x.80.0/24 | High | Storage and vMotion traffic |

## IP Address Usage Summary

### Per Region:
- **ESXi OOB Management:** 13 IPs
- **Infrastructure VMs:** 14 IPs
- **Application VMs:** 28 IPs (42 total with backend interfaces)
- **Total Assigned per Region:** ~55 IPs
- **Available per Region:** ~1,980 IPs (plenty of growth capacity)

### Total Across All Regions:
- **Total IPs Assigned:** ~165 IPs
- **Total IP Space:** 196,608 IPs (3 x /16 networks)
- **Utilization:** <0.1% (excellent room for expansion)
