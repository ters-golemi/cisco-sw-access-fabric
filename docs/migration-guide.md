# SD-Access Migration Guide

## Overview

This guide provides a comprehensive, step-by-step approach to migrate from a traditional enterprise network to an SD-Access fabric. The migration follows a phased approach to minimize disruption and allow for rollback at each stage.

## Current Network Overview

- **WAN Routers**: 2 units
- **Core Switches**: 2 units
- **Aggregation Switches**: 2 units
- **Access Switches**: 4 units
- **VLANs**: 10 VLANs routed through WAN routers
- **Routing**: Traditional VLAN-based routing

## Migration Strategy

The migration follows a **phased approach** with the following stages:

1. **Preparation Phase** - Assessment and planning
2. **Infrastructure Phase** - Deploy DNA Center and ISE
3. **Underlay Phase** - Configure underlay network
4. **Overlay Phase** - Build SD-Access fabric
5. **Migration Phase** - Migrate endpoints
6. **Optimization Phase** - Fine-tune and optimize

## Phase 1: Preparation (Week 1-2)

### 1.1 Network Assessment

**Objective**: Document current network state

Tasks:
- [ ] Document all device configurations
- [ ] Map all VLANs and IP subnets
- [ ] Identify all endpoints and their connectivity
- [ ] Document current routing protocols (OSPF, EIGRP, BGP, static)
- [ ] Document QoS policies
- [ ] Document security policies and ACLs
- [ ] Perform network discovery using DNA Center

**Commands to collect information**:
```bash
# On each device
show running-config
show vlan brief
show ip interface brief
show ip route
show spanning-tree
show cdp neighbors
show mac address-table
```

### 1.2 Design Planning

**Objective**: Design the SD-Access fabric

Tasks:
- [ ] Design underlay IP addressing scheme
- [ ] Design overlay virtual networks (VNs)
- [ ] Map existing VLANs to virtual networks
- [ ] Plan fabric site boundaries
- [ ] Design security group tags (SGTs)
- [ ] Plan LISP instance IDs
- [ ] Design anycast gateway addressing
- [ ] Plan border handoff connections

**Key Design Decisions**:

| Component | Design Choice | Notes |
|-----------|--------------|-------|
| Underlay Routing | IS-IS or OSPF | IS-IS recommended for scale |
| Underlay Addressing | /31 point-to-point links | Efficient IP usage |
| Overlay VNs | Map 10 VLANs to VNs | 1:1 or consolidate |
| SGT Strategy | Role-based or Zone-based | Depends on security policy |
| Control Plane | Both Core Switches | High availability |
| Border Nodes | Both WAN Routers | Dual-homing |

### 1.3 Hardware and Software Preparation

**Objective**: Prepare infrastructure components

Tasks:
- [ ] Install DNA Center appliance(s)
- [ ] Install ISE appliance(s)
- [ ] Upgrade all network devices to compatible IOS-XE versions
- [ ] Apply necessary licenses (DNA, ISE)
- [ ] Configure NTP on all devices
- [ ] Configure DNS for all management interfaces
- [ ] Set up backup systems

### 1.4 Lab Testing

**Objective**: Validate design in a test environment

Tasks:
- [ ] Build small-scale test fabric
- [ ] Test endpoint connectivity
- [ ] Validate policy enforcement
- [ ] Test failover scenarios
- [ ] Document rollback procedures

## Phase 2: Infrastructure Deployment (Week 3-4)

### 2.1 Cisco Catalyst Center Setup

**Objective**: Install and configure 3-node Catalyst Center cluster for high availability

Tasks:
- [ ] Rack and cable 3 Catalyst Center appliances
- [ ] Perform initial 3-node cluster setup for high availability
- [ ] Configure cluster networking and inter-node connectivity
- [ ] Configure system settings (NTP, DNS, certificates) on all nodes
- [ ] Configure backup schedule with cluster-aware backups
- [ ] Integrate with ISE using pxGrid
- [ ] Add network devices to inventory
- [ ] Configure device credentials
- [ ] Set up site hierarchy

**High Availability Configuration**:
- **Node 1**: Primary cluster member (active)
- **Node 2**: Secondary cluster member (active) 
- **Node 3**: Tertiary cluster member (active)
- **Load Distribution**: Automatic across all three nodes
- **Failover**: Automatic with zero downtime

**DNA Center Initial Configuration**:
```bash
# Access DNA Center CLI
maglev-config update

# Configure via GUI:
# 1. System Settings > Settings > System Configuration
#    - NTP Server: <ntp-server-ip>
#    - DNS Server: <dns-server-ip>
#    - Domain Name: example.com
#
# 2. System Settings > Settings > Device Credentials
#    - CLI Credentials: username/password
#    - SNMP v2c: community string
#    - HTTPS: username/password
#
# 3. Design > Network Hierarchy
#    - Create Sites (Building, Floor)
#    - Assign IP pools
```

### 2.2 ISE Setup

**Objective**: Install and configure 3-node ISE deployment for high availability

Tasks:
- [ ] Rack and cable 3 ISE appliances
- [ ] Perform initial setup on all three nodes
- [ ] Configure ISE cluster with high availability personas
- [ ] Configure NTP, DNS, certificates on all nodes
- [ ] Enable pxGrid services with redundancy
- [ ] Configure network device authentication (RADIUS) with load balancing
- [ ] Set up basic authentication policies
- [ ] Configure security group tags (SGTs)
- [ ] Create TrustSec policy matrix

**ISE High Availability Configuration**:
```
1. ISE 3-Node Deployment:
   - Primary Administration Node (PAN): ise-pan.example.com
   - Policy Service Node 1 (PSN): ise-psn1.example.com  
   - Policy Service Node 2 (PSN): ise-psn2.example.com
   - Automatic failover between PSN nodes
   - Geographic distribution recommended

2. Node Personas and Roles:
   - PAN: Administration, Monitoring, pxGrid publisher
   - PSN1: Policy Service, pxGrid client, RADIUS/TACACS+
   - PSN2: Policy Service, pxGrid client, RADIUS/TACACS+

3. pxGrid High Availability:
   - Administration > System > Deployment
   - Enable pxGrid on PAN with automatic failover
   - Configure pxGrid clients on both PSN nodes
   - Generate pxGrid certificates for secure communication

4. Network Device Load Balancing:
   - Administration > Network Resources > Network Devices
   - Add all fabric devices with both PSN nodes as RADIUS servers
   - Configure RADIUS shared secret (same on both PSNs)
   - Enable load balancing and failover

5. Security Groups:
   - Work Centers > TrustSec > Components > Security Groups
   - Create SGTs for each user/device role:
     * Employees (SGT 10)
     * Guests (SGT 20)
     * Contractors (SGT 30)
     * IoT Devices (SGT 40)
     * Servers (SGT 50)

5. TrustSec Policy Matrix:
   - Work Centers > TrustSec > TrustSec Policy
   - Define source-destination SGT policies
```

### 2.3 Integration

**Objective**: Integrate DNA Center with ISE

Tasks:
- [ ] Configure pxGrid on DNA Center
- [ ] Test DNA-ISE communication
- [ ] Verify device synchronization
- [ ] Test policy download

## Phase 3: Underlay Network Configuration (Week 5-6)

### 3.1 Underlay Design

**Objective**: Build robust underlay network for VXLAN fabric

**Underlay Requirements**:
- Layer 3 routed access (no spanning-tree in underlay)
- IGP routing protocol (IS-IS or OSPF)
- High bandwidth links (10G+ recommended)
- Low latency (<50ms fabric-wide)
- MTU 9100+ for VXLAN overhead

### 3.2 Configure Routing Protocol

**Objective**: Establish underlay reachability

**Option A: IS-IS Configuration** (Recommended):

```
# On all fabric devices
!
router isis UNDERLAY
 net 49.0001.0000.0000.000X.00
 is-type level-2-only
 metric-style wide
 log-adjacency-changes
 passive-interface default
 no passive-interface GigabitEthernet1/0/1
 no passive-interface GigabitEthernet1/0/2
!
interface Loopback0
 description Underlay Router ID
 ip address 10.255.255.X 255.255.255.255
 ip router isis UNDERLAY
!
interface GigabitEthernet1/0/1
 description Uplink to Core
 no switchport
 ip address 10.254.1.X 255.255.255.254
 ip router isis UNDERLAY
 isis network point-to-point
!
```

**Option B: OSPF Configuration**:

```
# On all fabric devices
!
router ospf 100
 router-id 10.255.255.X
 passive-interface default
 no passive-interface GigabitEthernet1/0/1
 no passive-interface GigabitEthernet1/0/2
!
interface Loopback0
 description Underlay Router ID
 ip address 10.255.255.X 255.255.255.255
 ip ospf 100 area 0
!
interface GigabitEthernet1/0/1
 description Uplink to Core
 no switchport
 ip address 10.254.1.X 255.255.255.254
 ip ospf network point-to-point
 ip ospf 100 area 0
!
```

### 3.3 Verify Underlay

**Objective**: Ensure underlay connectivity

Verification Commands:
```bash
# Verify routing protocol adjacencies
show isis neighbors
show ip ospf neighbor

# Verify routing table
show ip route

# Verify reachability to all loopbacks
ping 10.255.255.1 source loopback 0
ping 10.255.255.2 source loopback 0

# Test MTU
ping 10.255.255.X size 9000 df-bit

# Verify multicast (if using for underlay)
show ip mroute
show ip pim neighbor
```

## Phase 4: SD-Access Fabric Build (Week 7-8)

### 4.1 Create Fabric in DNA Center

**Objective**: Define fabric sites and roles

**Steps**:

1. **Create Fabric Site**:
   - Navigate to: Provision > Fabrics
   - Click "Add Fabric"
   - Select site from hierarchy
   - Name: "Campus-Fabric-Site1"

2. **Add Fabric Devices and Assign Roles**:

   | Device | Role | Purpose |
   |--------|------|---------|
   | Core-Switch-1 | Control Plane + Border | LISP MS/MR + External connectivity |
   | Core-Switch-2 | Control Plane + Border | LISP MS/MR + External connectivity |
   | WAN-Router-1 | Border | External connectivity |
   | WAN-Router-2 | Border | External connectivity |
   | Aggr-Switch-1 | Edge | Endpoint connectivity |
   | Aggr-Switch-2 | Edge | Endpoint connectivity |
   | Access-Switch-1 | Edge | Endpoint connectivity |
   | Access-Switch-2 | Edge | Endpoint connectivity |
   | Access-Switch-3 | Edge | Endpoint connectivity |
   | Access-Switch-4 | Edge | Endpoint connectivity |

3. **Configure Fabric Settings**:
   - Underlay: IS-IS or OSPF
   - Overlay: LISP + VXLAN
   - Authentication: 802.1X with ISE

### 4.2 Configure Virtual Networks

**Objective**: Create overlay virtual networks for segmentation

**Steps**:

1. **Create Virtual Networks** (Map existing VLANs):
   - Navigate to: Policy > Virtual Networks
   - Create VNs for each VLAN:
     * VN-Data (VLAN 10)
     * VN-Voice (VLAN 20)
     * VN-Guest (VLAN 30)
     * VN-Management (VLAN 40)
     * VN-Security (VLAN 50)
     * VN-IoT (VLAN 60)
     * VN-Servers (VLAN 70)
     * VN-Storage (VLAN 80)
     * VN-DMZ (VLAN 90)
     * VN-Partner (VLAN 100)

2. **Configure IP Pools**:
   - Assign IP address pools to each VN
   - Configure anycast gateway addresses

3. **Associate VNs to Fabric**:
   - Map each VN to the fabric site
   - Configure Layer 2 flooding

### 4.3 Configure Border Handoffs

**Objective**: Connect fabric to external networks

**Border Types**:
- **Internal Border**: Connect to legacy campus networks
- **External Border**: Connect to WAN, Internet, Data Center

**Configuration**:

```
# On Border Nodes (DNA Center automates this)
!
# Border handoff for external connectivity
interface GigabitEthernet1/0/10
 description Border Handoff to WAN
 no switchport
 ip address 192.168.100.2 255.255.255.252
 ip nat outside
!
# VRF for virtual network
vrf definition VN-Data
 rd 1:1
 address-family ipv4
  route-target export 1:1
  route-target import 1:1
 exit-address-family
!
interface Vlan 10
 description VN-Data Anycast Gateway
 vrf forwarding VN-Data
 ip address 10.10.10.1 255.255.255.0
 ip helper-address 10.20.20.10
 lisp mobility VN-Data
!
```

### 4.4 Provision Fabric Devices

**Objective**: Push fabric configuration to all devices

**Steps**:
1. Navigate to: Provision > Fabric
2. Select devices to provision
3. Review configuration preview
4. Deploy configuration
5. Monitor deployment status

**DNA Center will automatically configure**:
- LISP control plane
- VXLAN data plane
- TrustSec CTS
- Anycast gateways
- Multicast distribution trees
- Fabric-enabled interfaces

## Phase 5: Policy Configuration (Week 9)

### 5.1 Configure Scalable Groups

**Objective**: Define security group tags for policy enforcement

**In ISE**:
```
Security Groups (SGTs):
- Employees (10)
- Guests (20)
- Contractors (30)
- IoT-Devices (40)
- Corporate-Servers (50)
- Voice-Devices (60)
- Video-Devices (70)
- Printers (80)
- Unknown (100)
```

### 5.2 Configure Group Policies

**Objective**: Define access policies between security groups

**TrustSec Policy Matrix Examples**:

| Source SGT | Destination SGT | Action | Contracts |
|------------|-----------------|--------|-----------|
| Employees | Corporate-Servers | Permit | HTTP, HTTPS, SSH |
| Guests | Corporate-Servers | Deny | All |
| Guests | Internet | Permit | HTTP, HTTPS |
| IoT-Devices | Corporate-Servers | Deny | All |
| IoT-Devices | IoT-Devices | Permit | Specific ports |

### 5.3 Configure Contracts (Access Policies)

**Objective**: Define granular access control

**Example Contract**:
```
# In ISE Policy > Policy Elements > Results > TrustSec > Security Group ACLs

Name: Permit-Web-Services
ACL Content:
  permit tcp any any eq 80
  permit tcp any any eq 443
  deny ip any any

Name: Permit-Voice
ACL Content:
  permit udp any any range 16384 32767
  permit tcp any any eq 2000
  permit tcp any any eq 5060
  deny ip any any
```

### 5.4 Authentication and Authorization Policies

**Objective**: Classify endpoints into security groups

**Configure in ISE**:

1. **Authentication Policies**:
   - 802.1X for corporate devices
   - MAB (MAC Authentication Bypass) for IoT
   - Guest portal for visitors

2. **Authorization Policies**:
   ```
   Rule: Corporate-Wired-Devices
   Conditions: Wired_802.1X AND AD-Group = "Employees"
   Results: 
     - Security Group = Employees
     - VLAN = VN-Data
     - Access = Full-Access

   Rule: Corporate-Wireless-Devices
   Conditions: Wireless_802.1X AND AD-Group = "Employees"
   Results:
     - Security Group = Employees
     - VLAN = VN-Data
     - Access = Full-Access

   Rule: Guest-Devices
   Conditions: MAB AND Guest-Portal-Authenticated
   Results:
     - Security Group = Guests
     - VLAN = VN-Guest
     - Access = Internet-Only

   Rule: IoT-Devices
   Conditions: MAB AND Device-Type = "IP-Camera"
   Results:
     - Security Group = IoT-Devices
     - VLAN = VN-IoT
     - Access = IoT-Access
   ```

## Phase 6: Endpoint Migration (Week 10-12)

### 6.1 Migration Strategy

**Approach**: Phased migration by access switch

**Order**:
1. Start with non-critical access switch
2. Migrate one switch at a time
3. Validate connectivity before moving to next
4. Keep border handoffs active during migration

### 6.2 Pre-Migration Tasks

**Before each switch migration**:
- [ ] Document connected endpoints
- [ ] Schedule maintenance window
- [ ] Notify users
- [ ] Back up switch configuration
- [ ] Verify rollback procedure
- [ ] Prepare monitoring

### 6.3 Access Switch Migration Procedure

**For each access switch**:

1. **Enable fabric on access switch ports**:
   ```
   # In DNA Center: Provision > Fabric
   # Select access switch
   # Configure fabric edge ports
   
   # Alternatively via CLI (after fabric provisioning):
   interface GigabitEthernet1/0/5
    description User Port - Fabric Enabled
    switchport mode access
    switchport access vlan 10
    authentication port-control auto
    mab
    dot1x pae authenticator
    spanning-tree portfast
   ```

2. **Migrate endpoints**:
   - Move endpoints to fabric-enabled ports
   - Or enable fabric on ports with connected endpoints
   - Monitor endpoint authentication in ISE

3. **Verify connectivity**:
   ```bash
   # On DNA Center
   # Navigate to: Assurance > Health > Client Health
   # Verify endpoint connectivity and policy

   # On fabric edge switch
   show lisp session
   show vxlan vtep
   show cts role-based permissions
   ```

4. **Validate policy enforcement**:
   - Test inter-SGT communication
   - Verify blocked traffic
   - Check QoS markings

### 6.4 Aggregation Switch Migration

**For aggregation switches**:

1. **Configure as edge nodes**: Already done in Phase 4
2. **Migrate downstream access switches**: Follow access switch procedure
3. **Verify redundancy**: Test failover scenarios

### 6.5 Monitor Migration

**Continuous monitoring during migration**:
- DNA Center Assurance dashboards
- ISE Live Logs
- Syslog monitoring
- Network performance metrics

**Key Metrics**:
- Endpoint authentication success rate (>95%)
- LISP registration success
- Policy application success
- Network latency and throughput
- Control plane stability

## Phase 7: Border and External Connectivity (Week 13)

### 7.1 Configure Border Handoffs

**Objective**: Enable external connectivity through borders

**Types of handoffs**:
1. **IP Transit**: Route external prefixes via border
2. **SDA Transit**: Connect multiple fabric sites
3. **Fusion**: Connect to non-fabric networks

### 7.2 WAN Integration

**Configure WAN routers as borders**:

1. **External handoff** (to WAN):
   ```
   interface GigabitEthernet0/0/1
    description WAN Handoff
    ip address 192.168.1.2 255.255.255.252
    ip nat outside
   !
   ip route 0.0.0.0 0.0.0.0 192.168.1.1
   ```

2. **VRF-aware routing**:
   - Configure BGP or static routes per VRF
   - Implement route leaking if needed

### 7.3 Legacy Network Integration

**For legacy campus networks**:

1. **Configure fusion router** (if needed)
2. **Set up routing between fabric and legacy**
3. **Gradually migrate legacy segments**

## Phase 8: Optimization and Validation (Week 14-16)

### 8.1 Performance Optimization

Tasks:
- [ ] Tune QoS policies
- [ ] Optimize control plane timers
- [ ] Adjust multicast settings
- [ ] Fine-tune security policies
- [ ] Optimize LISP registrations

### 8.2 Security Hardening

Tasks:
- [ ] Review and refine SGT assignments
- [ ] Audit TrustSec policy matrix
- [ ] Implement additional security contracts
- [ ] Enable additional security features (MACsec, Encrypted VXLAN)
- [ ] Configure threat defense policies

### 8.3 Comprehensive Testing

Test scenarios:
- [ ] End-to-end connectivity
- [ ] Failover scenarios (control plane, border, edge)
- [ ] Policy enforcement validation
- [ ] QoS validation
- [ ] Multicast functionality
- [ ] Guest access workflows
- [ ] Application performance

### 8.4 Documentation

Deliverables:
- [ ] As-built network diagrams
- [ ] Configuration backups
- [ ] Operational runbooks
- [ ] Troubleshooting guides
- [ ] Policy documentation
- [ ] Change management procedures

### 8.5 Training

**Staff training topics**:
- DNA Center operations
- ISE policy management
- Fabric troubleshooting
- Day-2 operations
- Incident response

## Rollback Procedures

### Emergency Rollback

**If critical issues occur**:

1. **Disable fabric on affected switch**:
   ```
   # In DNA Center: Remove device from fabric
   # Or via CLI:
   no lisp
   no vxlan
   no cts role-based enforcement
   ```

2. **Restore traditional configuration**:
   ```
   # Restore from backup
   configure replace flash:backup-config.cfg
   ```

3. **Move endpoints back to traditional network**

### Planned Rollback

**If migration needs to be reversed**:

1. Document lessons learned
2. Remove devices from fabric in DNA Center
3. Restore traditional configurations
4. Re-enable traditional routing
5. Migrate endpoints back

## Post-Migration Activities

### Day-2 Operations

**Ongoing tasks**:
- Monitor DNA Center assurance dashboards
- Review ISE authentication logs
- Adjust policies based on usage patterns
- Add new endpoints and users
- Manage software updates
- Capacity planning

### Maintenance Windows

**Regular maintenance**:
- Software updates (quarterly)
- Policy reviews (monthly)
- Performance tuning (as needed)
- Security audits (quarterly)
- Disaster recovery testing (semi-annually)

## Success Criteria

**Migration is successful when**:
- [ ] All endpoints connected to fabric
- [ ] 100% of endpoints authenticating successfully
- [ ] All policies enforced correctly
- [ ] No increase in trouble tickets
- [ ] Network performance meets or exceeds baseline
- [ ] Failover scenarios tested and working
- [ ] Documentation completed
- [ ] Staff trained
- [ ] Management approval received

## Troubleshooting Common Issues

### Issue: Endpoints not authenticating

**Symptoms**: Endpoints unable to access network

**Resolution**:
1. Check ISE logs for authentication failures
2. Verify RADIUS configuration on switch
3. Check endpoint credentials
4. Review authorization policies

### Issue: No connectivity after fabric enablement

**Symptoms**: Endpoints authenticate but cannot communicate

**Resolution**:
1. Verify LISP registration: `show lisp session`
2. Check VXLAN tunnels: `show vxlan vtep`
3. Verify virtual network mapping
4. Check border routing

### Issue: Policy not enforcing

**Symptoms**: SGT-based policies not working

**Resolution**:
1. Verify SGT assignment in ISE
2. Check CTS configuration: `show cts role-based permissions`
3. Verify TrustSec policy download
4. Check contracts in policy matrix

### Issue: Control plane instability

**Symptoms**: Frequent LISP re-registrations

**Resolution**:
1. Check underlay stability
2. Verify NTP synchronization
3. Check control plane CPU and memory
4. Review LISP timers

## Appendix: Reference Commands

### Verification Commands

```bash
# Fabric Verification
show fabric summary
show lisp session
show lisp service ipv4
show vxlan vtep

# Policy Verification
show cts role-based permissions
show cts environment-data

# Endpoint Verification
show authentication sessions
show device-tracking database

# Underlay Verification
show isis neighbors
show ip ospf neighbor
show ip route
```

### DNA Center Automation

```python
# Example: Add device to fabric via API
import requests

url = "https://dnac-ip/dna/intent/api/v1/business/sda/fabric-site"
headers = {"Content-Type": "application/json", "X-Auth-Token": token}
payload = {
    "fabricName": "Campus-Fabric-Site1",
    "siteNameHierarchy": "Global/USA/Campus1"
}
response = requests.post(url, json=payload, headers=headers, verify=False)
```

## Timeline Summary

| Phase | Duration | Description |
|-------|----------|-------------|
| 1. Preparation | 2 weeks | Assessment and planning |
| 2. Infrastructure | 2 weeks | DNA Center and ISE setup |
| 3. Underlay | 2 weeks | Configure underlay network |
| 4. Fabric Build | 2 weeks | Create SD-Access fabric |
| 5. Policy Config | 1 week | Configure security policies |
| 6. Endpoint Migration | 3 weeks | Migrate endpoints to fabric |
| 7. Border Config | 1 week | Configure external connectivity |
| 8. Optimization | 3 weeks | Test, optimize, and validate |
| **Total** | **16 weeks** | **Complete migration** |

## Contact and Support

- Cisco TAC: https://www.cisco.com/c/en/us/support/web/tsd-cisco-worldwide-contacts.html
- DNA Center Community: https://community.cisco.com/t5/dna-center/bd-p/disc-dna-center
- SD-Access Resources: https://www.cisco.com/c/en/us/solutions/enterprise-networks/sd-access/index.html
