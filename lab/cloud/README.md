# Cloud Infrastructure Import Order

## Prerequisites
The cloud sites must exist in NetBox before importing circuit terminations.

## Import Order

### 1. Import Sites First
Import the main sites file which includes cloud sites:
```bash
# This file contains both on-prem and cloud sites
lab/sites/netbox_dc_sites.csv
```

Sites included:
- EMEA-DC-CLOUD (Equinix AM5, Amsterdam)
- APAC-DC-CLOUD (Equinix SG3, Singapore)
- AMER-DC-CLOUD (Equinix DC6, Ashburn)
- EMEA-DC-ONPREM (Interxion PAR7, Paris)
- APAC-DC-ONPREM (Equinix TY4, Tokyo)
- AMER-DC-ONPREM (CyrusOne, Dallas)

### 2. Get Site IDs from NetBox

After importing sites, retrieve their NetBox IDs:

```bash
# Via NetBox API
curl -H "Authorization: Token YOUR_TOKEN" \
     "https://netbox.example.com/api/dcim/sites/?name=EMEA-DC-CLOUD"

curl -H "Authorization: Token YOUR_TOKEN" \
     "https://netbox.example.com/api/dcim/sites/?name=AMER-DC-CLOUD"
```

Or via NetBox UI:
- Go to Organization → Sites
- Find each cloud site and note its ID

### 3. Update Circuit Terminations

Edit `netbox_cloud_circuit_terminations.csv` with actual site IDs:

Current (estimated IDs):
```csv
EXPRESSROUTE-EMEA-001,A,dcim.site,388,1000,1000,,,
EXPRESSROUTE-EMEA-001,Z,dcim.site,389,1000,1000,,,  # ← Update this
DIRECTCONNECT-AMER-001,A,dcim.site,392,10000,10000,,,
DIRECTCONNECT-AMER-001,Z,dcim.site,393,10000,10000,,,  # ← Update this
```

Replace IDs:
- Line 3: Replace 389 with actual EMEA-DC-CLOUD ID
- Line 5: Replace 393 with actual AMER-DC-CLOUD ID

### 4. Import Remaining Cloud Files

Import in this order:
1. `netbox_cloud_providers.csv` - Cloud providers (Microsoft, AWS, Google)
2. `netbox_cloud_gateway_device_types.csv` - Gateway device types
3. `netbox_cloud_gateways.csv` - Gateway devices
4. `netbox_cloud_gateway_interfaces.csv` - Gateway interfaces
5. `netbox_cloud_circuits.csv` - ExpressRoute and Direct Connect circuits
6. `netbox_cloud_circuit_terminations.csv` - Circuit terminations (after updating IDs)
7. `netbox_cloud_vrfs.csv` - VRFs for cloud VPCs/VNets
8. `netbox_cloud_prefixes.csv` - IP prefixes in cloud VRFs
9. `netbox_cloud_vpn_tunnels.csv` - VPN tunnels to GCP

## Known Site IDs (from existing terminations)

From `lab/circuits/netbox_dc_circuits_terminations.csv`:
- EMEA-DC-ONPREM = 388
- APAC-DC-ONPREM = 390
- AMER-DC-ONPREM = 392

Cloud site IDs need to be determined after import.

## IP Address Allocation

### On-Premise (10.100-102.x.x)
- 10.100.0.0/16 - EMEA-DC-ONPREM
- 10.101.0.0/16 - APAC-DC-ONPREM
- 10.102.0.0/16 - AMER-DC-ONPREM

### Cloud (10.200-221.x.x)
- 10.200.0.0/16 - EMEA Azure Production VNet
- 10.201.0.0/24 - EMEA Azure Management VNet
- 10.210.0.0/16 - APAC GCP Production VPC
- 10.211.0.0/24 - APAC GCP Management VPC
- 10.220.0.0/16 - AMER AWS Production VPC
- 10.221.0.0/24 - AMER AWS Management VPC
