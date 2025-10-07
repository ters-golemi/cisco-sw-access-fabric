# Example Configurations for SD-Access Deployment

This document provides example configurations for various components in the SD-Access fabric.

## DNA Center Configuration Example

### Site Hierarchy

```
Global/
└── USA/
    └── Campus1/
        ├── Building1/
        │   ├── Floor1
        │   └── Floor2
        └── Building2/
            ├── Floor1
            └── Floor2
```

### IP Pool Assignments

| Virtual Network | IP Pool | Gateway | DHCP Server |
|----------------|---------|---------|-------------|
| VN-Data | 10.10.0.0/16 | 10.10.10.1 | 10.20.20.10 |
| VN-Voice | 10.20.0.0/16 | 10.20.20.1 | 10.20.20.10 |
| VN-Guest | 10.30.0.0/16 | 10.30.30.1 | 10.20.20.10 |
| VN-Management | 10.40.0.0/16 | 10.40.40.1 | 10.20.20.10 |
| VN-Security | 10.50.0.0/16 | 10.50.50.1 | 10.20.20.10 |
| VN-IoT | 10.60.0.0/16 | 10.60.60.1 | 10.20.20.10 |
| VN-Servers | 10.70.0.0/16 | 10.70.70.1 | 10.20.20.10 |
| VN-Storage | 10.80.0.0/16 | 10.80.80.1 | 10.20.20.10 |
| VN-DMZ | 10.90.0.0/16 | 10.90.90.1 | 10.20.20.10 |
| VN-Partner | 10.100.0.0/16 | 10.100.100.1 | 10.20.20.10 |

## Underlay Network Configuration

### IP Addressing Scheme

#### Loopback Addresses (Router IDs)

| Device | Loopback0 |
|--------|-----------|
| core-switch-1 | 10.255.255.1/32 |
| core-switch-2 | 10.255.255.2/32 |
| wan-router-1 | 10.255.255.11/32 |
| wan-router-2 | 10.255.255.12/32 |
| aggr-switch-1 | 10.255.255.21/32 |
| aggr-switch-2 | 10.255.255.22/32 |
| access-switch-1 | 10.255.255.31/32 |
| access-switch-2 | 10.255.255.32/32 |
| access-switch-3 | 10.255.255.33/32 |
| access-switch-4 | 10.255.255.34/32 |

#### Point-to-Point Links

| Link | Device A | Interface A | IP A | Device B | Interface B | IP B |
|------|----------|-------------|------|----------|-------------|------|
| Link1 | core-switch-1 | Gi1/0/1 | 10.254.1.0/31 | aggr-switch-1 | Gi1/0/47 | 10.254.1.1/31 |
| Link2 | core-switch-1 | Gi1/0/2 | 10.254.1.2/31 | aggr-switch-2 | Gi1/0/47 | 10.254.1.3/31 |
| Link3 | core-switch-2 | Gi1/0/1 | 10.254.1.4/31 | aggr-switch-1 | Gi1/0/48 | 10.254.1.5/31 |
| Link4 | core-switch-2 | Gi1/0/2 | 10.254.1.6/31 | aggr-switch-2 | Gi1/0/48 | 10.254.1.7/31 |

### IS-IS Configuration Example

#### Core Switch Configuration

```
hostname core-switch-1
!
interface Loopback0
 description Underlay Router ID
 ip address 10.255.255.1 255.255.255.255
 ip router isis UNDERLAY
!
interface GigabitEthernet1/0/1
 description Link to aggr-switch-1
 no switchport
 ip address 10.254.1.0 255.255.255.254
 ip router isis UNDERLAY
 isis network point-to-point
 mtu 9100
 no shutdown
!
interface GigabitEthernet1/0/2
 description Link to aggr-switch-2
 no switchport
 ip address 10.254.1.2 255.255.255.254
 ip router isis UNDERLAY
 isis network point-to-point
 mtu 9100
 no shutdown
!
router isis UNDERLAY
 net 49.0001.0000.0000.0001.00
 is-type level-2-only
 metric-style wide
 log-adjacency-changes
 passive-interface default
 no passive-interface GigabitEthernet1/0/1
 no passive-interface GigabitEthernet1/0/2
!
```

#### Edge Switch Configuration

```
hostname access-switch-1
!
interface Loopback0
 description Underlay Router ID
 ip address 10.255.255.31 255.255.255.255
 ip router isis UNDERLAY
!
interface GigabitEthernet1/0/25
 description Uplink to aggr-switch-1
 no switchport
 ip address 10.254.2.0 255.255.255.254
 ip router isis UNDERLAY
 isis network point-to-point
 mtu 9100
 no shutdown
!
interface GigabitEthernet1/0/26
 description Uplink to aggr-switch-2
 no switchport
 ip address 10.254.2.2 255.255.255.254
 ip router isis UNDERLAY
 isis network point-to-point
 mtu 9100
 no shutdown
!
router isis UNDERLAY
 net 49.0001.0000.0000.0031.00
 is-type level-2-only
 metric-style wide
 log-adjacency-changes
 passive-interface default
 no passive-interface GigabitEthernet1/0/25
 no passive-interface GigabitEthernet1/0/26
!
```

## Authentication Configuration

### AAA and RADIUS Configuration

```
!
! AAA Configuration
aaa new-model
!
aaa authentication login default group ISE-GROUP local
aaa authentication dot1x default group ISE-GROUP
aaa authorization network default group ISE-GROUP
aaa authorization exec default group ISE-GROUP local
aaa accounting update newinfo
aaa accounting dot1x default start-stop group ISE-GROUP
aaa accounting network default start-stop group ISE-GROUP
!
! RADIUS Servers
radius server ISE-1
 address ipv4 10.1.1.20 auth-port 1812 acct-port 1813
 key cisco123
!
radius server ISE-2
 address ipv4 10.1.1.21 auth-port 1812 acct-port 1813
 key cisco123
!
! RADIUS Server Group
aaa group server radius ISE-GROUP
 server name ISE-1
 server name ISE-2
!
! Device Tracking
device-tracking tracking
device-tracking policy IPDT_POLICY
 tracking enable
!
! 802.1X
dot1x system-auth-control
dot1x critical eapol
!
! TrustSec (CTS)
cts authorization list ISE-GROUP
cts role-based enforcement
!
```

### Edge Port Configuration

```
!
! Fabric Edge Port for Endpoints
interface GigabitEthernet1/0/5
 description User Port - Employee
 switchport mode access
 switchport access vlan 10
 !
 ! Authentication
 authentication host-mode multi-auth
 authentication port-control auto
 authentication periodic
 authentication timer reauthenticate server
 !
 ! MAB Configuration
 mab
 !
 ! 802.1X Configuration
 dot1x pae authenticator
 dot1x timeout tx-period 5
 !
 ! Device Tracking
 device-tracking attach-policy IPDT_POLICY
 !
 ! Spanning Tree
 spanning-tree portfast
 spanning-tree bpduguard enable
 !
 no shutdown
!
```

## ISE Configuration

### Security Groups (SGTs)

```
Security Group Tags:
- Employees (SGT 10)
- Guests (SGT 20)
- Contractors (SGT 30)
- IoT-Devices (SGT 40)
- Corporate-Servers (SGT 50)
- Voice-Devices (SGT 60)
- Video-Devices (SGT 70)
- Printers (SGT 80)
- Unknown (SGT 100)
```

### Security Group ACLs (SGACLs)

#### Permit-Web-Services

```
permit tcp any any eq 80
permit tcp any any eq 443
deny ip any any log
```

#### Permit-Voice

```
permit udp any any range 16384 32767
permit tcp any any eq 2000
permit tcp any any eq 5060
permit tcp any any eq 5061
deny ip any any log
```

#### Permit-All

```
permit ip any any
```

#### Deny-All

```
deny ip any any log
```

### TrustSec Policy Matrix

| Source SGT | Destination SGT | Policy | SGACL |
|------------|-----------------|--------|-------|
| Employees | Corporate-Servers | PERMIT | Permit-All |
| Employees | Voice-Devices | PERMIT | Permit-Voice |
| Employees | Printers | PERMIT | Permit-Web-Services |
| Guests | Corporate-Servers | DENY | Deny-All |
| Guests | Internet | PERMIT | Permit-Web-Services |
| Contractors | Corporate-Servers | PERMIT | Permit-Web-Services |
| IoT-Devices | Corporate-Servers | DENY | Deny-All |
| IoT-Devices | IoT-Devices | PERMIT | Permit-All |
| Voice-Devices | Corporate-Servers | PERMIT | Permit-Voice |

### Authorization Policies

#### Employee Wired Access

```
Rule Name: Employee-Wired-Access
Conditions:
  - Wired_802.1X
  - AD:ExternalGroups EQUALS "Domain Users"
Results:
  - Authorization Profile: Employee-Access
  - VLAN: 10 (VN-Data)
  - SGT: 10 (Employees)
  - DACL: None
```

#### Guest Access

```
Rule Name: Guest-Access
Conditions:
  - Wireless_MAB OR Wired_MAB
  - GuestType EQUALS "Guest"
Results:
  - Authorization Profile: Guest-Access
  - VLAN: 30 (VN-Guest)
  - SGT: 20 (Guests)
  - DACL: Permit-Internet-Only
```

#### IoT Devices

```
Rule Name: IoT-Devices
Conditions:
  - Wired_MAB
  - EndpointProfile EQUALS "IP-Camera" OR "IoT-Sensor"
Results:
  - Authorization Profile: IoT-Access
  - VLAN: 60 (VN-IoT)
  - SGT: 40 (IoT-Devices)
  - DACL: None
```

#### Voice Devices

```
Rule Name: Voice-Access
Conditions:
  - Wired_MAB
  - Device-Type EQUALS "IP-Phone"
Results:
  - Authorization Profile: Voice-Access
  - VLAN: 20 (VN-Voice)
  - SGT: 60 (Voice-Devices)
  - DACL: None
```

## Border Configuration

### External Border Handoff

```
hostname wan-router-1
!
! Loopback Interface
interface Loopback0
 description Underlay Router ID
 ip address 10.255.255.11 255.255.255.255
!
! External WAN Interface
interface GigabitEthernet0/0/0
 description WAN Handoff to ISP
 ip address 192.168.100.1 255.255.255.252
 ip nat outside
 no shutdown
!
! VRF Definition for VN-Data
vrf definition VN-Data
 rd 1:1
 address-family ipv4
  route-target export 1:1
  route-target import 1:1
 exit-address-family
!
! VRF Interface (managed by DNA Center)
interface Vlan 1001
 description Border for VN-Data
 vrf forwarding VN-Data
 ip address 10.10.255.1 255.255.255.0
 no shutdown
!
! BGP Configuration for External Connectivity
router bgp 65001
 bgp log-neighbor-changes
 !
 ! Default VRF
 neighbor 192.168.100.2 remote-as 65000
 neighbor 192.168.100.2 description ISP
 !
 address-family ipv4
  network 10.0.0.0 mask 255.0.0.0
  neighbor 192.168.100.2 activate
 exit-address-family
 !
 ! VN-Data VRF
 address-family ipv4 vrf VN-Data
  redistribute lisp
  neighbor 192.168.100.2 remote-as 65000
  neighbor 192.168.100.2 activate
 exit-address-family
!
! NAT Configuration
ip nat inside source list NAT_ACL interface GigabitEthernet0/0/0 overload
!
ip access-list standard NAT_ACL
 permit 10.0.0.0 0.255.255.255
!
```

## Virtual Network Configuration

### VRF Configuration (Automated by DNA Center)

```
!
! VRF for VN-Data
vrf definition VN-Data
 rd 1:1
 address-family ipv4
  route-target export 1:1
  route-target import 1:1
 exit-address-family
!
! Anycast Gateway for VN-Data
interface Vlan 10
 description VN-Data Anycast Gateway
 vrf forwarding VN-Data
 ip address 10.10.10.1 255.255.255.0
 ip helper-address 10.20.20.10
 lisp mobility VN-Data
 no shutdown
!
```

## Verification Commands

### Underlay Verification

```bash
# IS-IS Neighbors
show isis neighbors

# IS-IS Database
show isis database

# IP Routes
show ip route isis

# Interface Status
show ip interface brief

# MTU Verification
show interfaces | include MTU

# Ping Test
ping 10.255.255.X source loopback 0
```

### Fabric Verification

```bash
# Fabric Summary
show fabric summary

# LISP Sessions
show lisp session

# LISP EID Table
show lisp service ipv4

# VXLAN VTEPs
show vxlan vtep

# Fabric Site Details
show fabric site detail

# Fabric VN Details
show fabric vn name VN-Data
```

### Authentication Verification

```bash
# Authentication Sessions
show authentication sessions

# 802.1X Status
show dot1x all

# MAB Sessions
show mab all

# Device Tracking
show device-tracking database

# RADIUS Statistics
show radius statistics
```

### Policy Verification

```bash
# TrustSec Configuration
show cts environment-data

# SGT Assignments
show cts role-based permissions

# SGT to IP Bindings
show cts role-based sgt-map all

# Policy Download Status
show cts policy-server status
```

## Troubleshooting Commands

```bash
# Debug Authentication
debug authentication all
debug radius authentication
debug dot1x all

# Debug LISP
debug lisp control-plane all
debug lisp data-plane all

# Debug VXLAN
debug vxlan packet
debug vxlan error

# Debug TrustSec
debug cts all

# Show Tech Support
show tech-support

# Show Logging
show logging
```

## DNA Center API Examples

### Get Authentication Token

```bash
curl -X POST \
  https://10.1.1.10/dna/system/api/v1/auth/token \
  -H 'Content-Type: application/json' \
  -u 'admin:password' \
  --insecure
```

### Get Fabric Sites

```bash
curl -X GET \
  https://10.1.1.10/dna/intent/api/v1/business/sda/fabric-site \
  -H 'X-Auth-Token: TOKEN' \
  --insecure
```

### Add Device to Fabric

```bash
curl -X POST \
  https://10.1.1.10/dna/intent/api/v1/business/sda/edge-device \
  -H 'X-Auth-Token: TOKEN' \
  -H 'Content-Type: application/json' \
  -d '{
    "deviceManagementIpAddress": "10.2.4.1",
    "siteNameHierarchy": "Global/USA/Campus1"
  }' \
  --insecure
```

## ISE API Examples

### Get Security Groups

```bash
curl -X GET \
  https://10.1.1.20/ers/config/sgt \
  -H 'Accept: application/json' \
  -u 'admin:password' \
  --insecure
```

### Create Security Group

```bash
curl -X POST \
  https://10.1.1.20/ers/config/sgt \
  -H 'Content-Type: application/json' \
  -u 'admin:password' \
  -d '{
    "Sgt": {
      "name": "Employees",
      "value": 10,
      "description": "Corporate employees"
    }
  }' \
  --insecure
```

## Best Practices Summary

1. Always configure underlay before overlay
2. Verify underlay connectivity before fabric deployment
3. Use consistent naming conventions
4. Document all IP address assignments
5. Test authentication before enabling on all ports
6. Implement policies gradually
7. Monitor fabric health continuously
8. Maintain configuration backups
9. Use automation for consistency
10. Follow change management procedures
