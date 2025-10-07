# Hardware Requirements for SD-Access Deployment

## Current Network Infrastructure

- **WAN Routers**: 2 units (SD-Access compatible)
- **Core Switches**: 2 units (SD-Access compatible)
- **Aggregation Switches**: 2 units (SD-Access compatible)
- **Access Switches**: 4 units (SD-Access compatible)
- **VLANs**: 10 VLANs routed through WAN routers

## Required Hardware for SD-Access Deployment

### 1. Cisco Catalyst Center Appliance

**Required**: 3 Catalyst Center appliances (for high availability deployment)

- **Model Options**:
  - Catalyst Center DN2-HW-APL (Physical Appliance)
  - Catalyst Center DN2-HW-APL-L (Large deployment)
  - Catalyst Center Virtual Appliance (for smaller deployments/testing)

- **High Availability Configuration**:
  - 3-node cluster for maximum uptime and fault tolerance
  - Active-Active-Active cluster configuration
  - Load distribution across all three nodes
  - Automatic failover with zero downtime

- **Minimum Specifications per Node** (Physical):
  - 44 vCPUs
  - 256 GB RAM
  - 3 TB storage (RAID 10)
  - 4x 10GbE network interfaces

- **Purpose**: Centralized management, automation, and policy control for the SD-Access fabric

### 2. Identity Services Engine (ISE)

**Required**: 3 ISE appliances (for high availability deployment)

- **Model Options**:
  - ISE-3595-K9 (Large deployment)
  - ISE-3515-K9 (Medium deployment)
  - ISE-3495-K9 (Small deployment)
  - ISE Virtual Appliance

- **High Availability Configuration**:
  - 3-node deployment: 2 Policy Service Nodes (PSN) + 1 Policy Administration Node (PAN)
  - Automatic failover between PSN nodes
  - Geographic distribution recommended for disaster recovery
  - Load balancing across PSN nodes for optimal performance

- **Minimum Specifications per Node** (ISE-3515):
  - 24 vCPUs
  - 64 GB RAM
  - 600 GB storage
  - 4x 1GbE network interfaces

- **Purpose**: Network access control, policy enforcement, and segmentation (TrustSec)

### 3. Fabric Control Plane Nodes

**Leverage Existing**: Use existing Core Switches as Control Plane nodes

- **Requirements**:
  - Minimum 2 switches for redundancy
  - Must support Catalyst 9000 series or compatible hardware
  - Must run IOS-XE 16.12.1 or later
  - Recommended: Catalyst 9400 or 9500 series

- **Purpose**: LISP Map Server/Map Resolver for fabric endpoint location tracking

### 4. Fabric Border Nodes

**Leverage Existing**: Use existing WAN Routers or Core Switches as Border nodes

- **Requirements**:
  - Minimum 2 border nodes for redundancy
  - Must support VRF-Lite or full VRF
  - Must support LISP, VXLAN, and TrustSec
  - Recommended: Catalyst 9500 series or ASR 1000 series

- **Purpose**: Gateway between SD-Access fabric and external networks (WAN, Internet, legacy networks)

### 5. Fabric Edge Nodes

**Leverage Existing**: Use existing Aggregation and Access Switches as Edge nodes

- **Current Infrastructure**:
  - 2 Aggregation Switches
  - 4 Access Switches
  
- **Requirements**:
  - Must support VXLAN encapsulation
  - Must support TrustSec (SGT)
  - Must support LISP data plane
  - Recommended: Catalyst 9300 or 9400 series
  - IOS-XE 16.12.1 or later

- **Purpose**: Endpoint connectivity and policy enforcement at the edge

### 6. Wireless LAN Controller (WLC) - Optional

**If wireless is required**: 1-2 WLC appliances or embedded wireless controller

- **Model Options**:
  - Cisco 9800 Series Wireless Controllers
  - Embedded Wireless Controller on Catalyst 9000 switches

- **Purpose**: Wireless endpoint integration with SD-Access fabric

### 7. Network Time Protocol (NTP) Server

**Recommended**: Dedicated NTP server or external NTP source

- **Purpose**: Time synchronization across all fabric devices

### 8. DNS and DHCP Servers

**Required**: Ensure existing DNS and DHCP infrastructure is available

- **Purpose**: Name resolution and IP address management for endpoints

## Summary of Additional Hardware Needed

Based on the current infrastructure being SD-Access compatible, the following NEW hardware is required:

1. **DNA Center Appliance**: 1-2 units (PRIMARY REQUIREMENT)
   - Estimated Cost: $100,000 - $200,000 per appliance
   
2. **Identity Services Engine (ISE)**: 2 units (PRIMARY REQUIREMENT)
   - Estimated Cost: $30,000 - $75,000 per appliance depending on model
   
3. **Optional - Wireless LAN Controller**: 1-2 units (if wireless support needed)
   - Estimated Cost: $15,000 - $50,000 per controller

4. **Licenses**:
   - DNA Advantage or Premier licenses for all switches
   - ISE Advantage or Premier licenses
   - Estimated: $1,000 - $3,000 per switch depending on license tier

## Existing Hardware Repurposing

The following existing hardware can be repurposed for SD-Access roles:

- **WAN Routers (2)**: Configure as Fabric Border Nodes
- **Core Switches (2)**: Configure as Fabric Control Plane Nodes
- **Aggregation Switches (2)**: Configure as Fabric Edge Nodes
- **Access Switches (4)**: Configure as Fabric Edge Nodes

## Network Design Roles

```
SD-Access Fabric Architecture:

┌─────────────────────────────────────────────────────────┐
│                     DNA Center                          │
│              (Management & Automation)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           │ Management
                           │
┌──────────────────────────┴───────────────────────────────┐
│                                                           │
│  ┌────────────────┐         ┌────────────────┐          │
│  │   ISE Node 1   │         │   ISE Node 2   │          │
│  │ (Policy/AuthN) │         │ (Policy/AuthN) │          │
│  └────────────────┘         └────────────────┘          │
│                                                           │
└───────────────────────────────────────────────────────────┘
                           │
            ┌──────────────┴──────────────┐
            │                             │
    ┌───────▼─────────┐         ┌────────▼────────┐
    │  Core Switch 1  │         │  Core Switch 2  │
    │ (Control Plane) │◄───────►│ (Control Plane) │
    │  LISP MS/MR     │         │  LISP MS/MR     │
    └────────┬────────┘         └────────┬────────┘
             │                           │
             └───────────┬───────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
    ┌───────▼──────┐          ┌──────▼───────┐
    │ WAN Router 1 │          │ WAN Router 2 │
    │   (Border)   │          │   (Border)   │
    └───────┬──────┘          └──────┬───────┘
            │                        │
            └──────────┬─────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    ┌────▼────┐   ┌────▼────┐  ┌────▼────┐
    │  Aggr   │   │  Aggr   │  │         │
    │Switch 1 │   │Switch 2 │  │         │
    │ (Edge)  │   │ (Edge)  │  │         │
    └────┬────┘   └────┬────┘  │         │
         │             │        │         │
    ┌────┴──┬──────────┴───┬────────┐   │
    │       │              │        │   │
┌───▼──┐ ┌──▼──┐      ┌───▼──┐ ┌───▼──┐│
│Access│ │Access│      │Access│ │Access││
│Sw 1  │ │Sw 2 │      │Sw 3  │ │Sw 4  ││
│(Edge)│ │(Edge)│      │(Edge)│ │(Edge)││
└──────┘ └─────┘      └──────┘ └──────┘│
                                        │
                                        │
                                   Endpoints
```

## Pre-Deployment Checklist

- [ ] Verify all existing hardware is running compatible IOS-XE versions
- [ ] Procure DNA Center appliance(s)
- [ ] Procure ISE appliance(s)
- [ ] Obtain necessary software licenses (DNA, ISE)
- [ ] Plan IP addressing for underlay and overlay networks
- [ ] Document current VLAN and routing configuration
- [ ] Plan maintenance windows for migration
- [ ] Set up backup and recovery procedures
- [ ] Establish rollback procedures
- [ ] Configure management network access to DNA Center
- [ ] Install and configure NTP server
- [ ] Verify DNS and DHCP services are operational

## Minimum Software Versions

- **IOS-XE**: 16.12.1 or later (17.3.x recommended)
- **DNA Center**: 2.2.3.4 or later (2.3.x recommended)
- **ISE**: 3.0 or later (3.1 recommended)
- **Wireless Controller (if applicable)**: IOS-XE 17.6.x or later

## References

- Cisco SD-Access Design Guide
- Cisco DNA Center Installation Guide
- Cisco ISE Installation Guide
- Cisco SD-Access CVD (Validated Design)
