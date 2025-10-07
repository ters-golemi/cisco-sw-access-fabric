# SD-Access Fabric Migration Project

Comprehensive automation and documentation for migrating from a traditional enterprise network to an SD-Access Fabric.

## Overview

This repository provides a complete solution for migrating a traditional enterprise network to Cisco SD-Access, including hardware requirements documentation, migration guides, Ansible playbooks, and Python automation scripts.

## Current Network

- 2 WAN Routers
- 2 Core Switches  
- 2 Aggregation Switches
- 4 Access Switches
- 10 VLANs routed through WAN routers
- All hardware is SD-Access compatible

## Solution Components

### Documentation

- **Hardware Requirements**: Complete list of hardware needed for SD-Access deployment
- **Migration Guide**: Step-by-step migration process with detailed phases
- **Mac Setup Guide**: Instructions for setting up automation tools on macOS

### Automation Scripts

- **Ansible Playbooks**: Automated configuration deployment
  - Underlay network preparation
  - Authentication and ISE integration
  - Fabric deployment via DNA Center
  
- **Python Scripts**: API-based automation
  - DNA Center fabric manager
  - ISE policy manager

### Configuration Files

- Pre-configured inventory files
- Variable definitions for all network components
- Example configuration templates

## Quick Start

### Prerequisites

- macOS 10.15 or later
- Python 3.8 or later
- Network access to DNA Center and ISE
- Valid credentials for all systems

### Installation

```bash
# Clone the repository
git clone https://github.com/ters-golemi/cisco-sw-access-fabric.git
cd cisco-sw-access-fabric

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install Ansible collections
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install cisco.dnac
```

### Configuration

1. Update inventory file: `ansible/inventory/hosts.yml`
2. Update variables: `ansible/group_vars/all.yml`
3. Create vault for secrets: `ansible-vault create ansible/group_vars/vault.yml`
4. Update configuration files in `config/` directory

### Usage

#### Using Ansible

```bash
# Configure underlay network
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/01-prepare-underlay.yml

# Configure authentication
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/02-configure-authentication.yml

# Deploy fabric
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/03-deploy-fabric.yml
```

#### Using Python Scripts

```bash
# Deploy fabric via DNA Center
python3 python_scripts/dnac_fabric_manager.py \
  --host 10.1.1.10 \
  --username admin \
  --password <password> \
  --config config/fabric-config.json

# Configure ISE policies
python3 python_scripts/ise_policy_manager.py \
  --host 10.1.1.20 \
  --username admin \
  --password <password> \
  --config config/ise-config.json
```

## Documentation

### Hardware Requirements

See [docs/hardware-requirements.md](docs/hardware-requirements.md) for:
- Required new hardware (DNA Center, ISE)
- Existing hardware repurposing
- Software version requirements
- Licensing requirements

### Migration Guide

See [docs/migration-guide.md](docs/migration-guide.md) for:
- Phased migration approach
- Pre-migration assessment
- Step-by-step procedures
- Verification steps
- Rollback procedures

### Mac Setup Guide

See [docs/mac-setup-guide.md](docs/mac-setup-guide.md) for:
- Complete setup instructions for macOS
- Environment configuration
- Tool installation
- Troubleshooting

## Repository Structure

```
cisco-sw-access-fabric/
├── README.md                     # This file
├── requirements.txt              # Python dependencies
├── ansible/
│   ├── ansible.cfg              # Ansible configuration
│   ├── inventory/
│   │   └── hosts.yml            # Device inventory
│   ├── group_vars/
│   │   └── all.yml              # Global variables
│   ├── playbooks/
│   │   ├── 01-prepare-underlay.yml
│   │   ├── 02-configure-authentication.yml
│   │   └── 03-deploy-fabric.yml
│   └── templates/               # Configuration templates
├── python_scripts/
│   ├── dnac_fabric_manager.py   # DNA Center automation
│   └── ise_policy_manager.py    # ISE automation
├── docs/
│   ├── hardware-requirements.md # Hardware requirements
│   ├── migration-guide.md       # Migration procedures
│   └── mac-setup-guide.md       # macOS setup guide
└── config/
    ├── fabric-config.json       # Fabric configuration
    └── ise-config.json          # ISE configuration
```

## Features

- Automated underlay network configuration (IS-IS or OSPF)
- ISE integration with RADIUS and TrustSec
- Fabric site creation and device role assignment
- Virtual network creation and IP pool assignment
- Security group tag (SGT) configuration
- Authorization policy automation
- Comprehensive error handling and logging
- Support for both Ansible and Python workflows

## Hardware Required for SD-Access

### New Hardware Needed

1. **DNA Center Appliance** (1-2 units)
   - Primary requirement for fabric management
   - Cisco DN2-HW-APL or Virtual Appliance

2. **Identity Services Engine** (2 units minimum)
   - Required for policy and authentication
   - Cisco ISE-3595-K9, ISE-3515-K9, or Virtual

3. **Licenses**
   - DNA Advantage or Premier licenses
   - ISE Advantage or Premier licenses

### Existing Hardware Repurposing

- WAN Routers: Configure as Border Nodes
- Core Switches: Configure as Control Plane Nodes
- Aggregation Switches: Configure as Edge Nodes
- Access Switches: Configure as Edge Nodes

## Migration Timeline

Estimated timeline: 16 weeks

1. Preparation: 2 weeks
2. Infrastructure Deployment: 2 weeks
3. Underlay Configuration: 2 weeks
4. Fabric Build: 2 weeks
5. Policy Configuration: 1 week
6. Endpoint Migration: 3 weeks
7. Border Configuration: 1 week
8. Optimization: 3 weeks

## Best Practices

- Always test in a lab environment first
- Back up all configurations before making changes
- Use Ansible Vault for sensitive data
- Follow the phased migration approach
- Maintain rollback procedures
- Monitor fabric health continuously
- Document all customizations

## Security Considerations

- Store credentials in Ansible Vault or environment variables
- Use separate accounts for automation
- Enable audit logging on all devices
- Implement least-privilege access
- Regularly review security policies
- Keep software updated

## Troubleshooting

Common issues and solutions are documented in:
- [Migration Guide - Troubleshooting Section](docs/migration-guide.md#troubleshooting-common-issues)
- [Mac Setup Guide - Troubleshooting Section](docs/mac-setup-guide.md#troubleshooting)

## Support and Resources

### Documentation

- Cisco SD-Access: https://www.cisco.com/c/en/us/solutions/enterprise-networks/sd-access/
- DNA Center: https://developer.cisco.com/docs/dna-center/
- ISE: https://developer.cisco.com/docs/identity-services-engine/

### Community

- Cisco DevNet: https://community.cisco.com/t5/devnet/ct-p/devnet
- Ansible Network: https://www.ansible.com/products/network-automation

### Professional Support

- Cisco TAC: https://www.cisco.com/c/en/us/support/
- GitHub Issues: https://github.com/ters-golemi/cisco-sw-access-fabric/issues

## Contributing

Contributions are welcome. Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is provided as-is for educational and operational purposes.

## Disclaimer

This solution is provided as a reference implementation. Always test thoroughly in a non-production environment before deploying to production. Cisco product names and trademarks are property of Cisco Systems, Inc.
