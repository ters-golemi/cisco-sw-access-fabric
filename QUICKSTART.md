# Quick Start Guide

Get started with SD-Access migration automation in minutes.

## Prerequisites

- macOS 10.15 or later
- Python 3.8+
- Network access to DNA Center and ISE
- Administrator credentials

## 5-Minute Setup

### 1. Clone and Install

```bash
# Clone repository
git clone https://github.com/ters-golemi/cisco-sw-access-fabric.git
cd cisco-sw-access-fabric

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Inventory

Edit `ansible/inventory/hosts.yml` with your device IPs:

```yaml
dnac-primary:
  ansible_host: YOUR_DNAC_IP

ise-primary:
  ansible_host: YOUR_ISE_IP

core-switch-1:
  ansible_host: YOUR_CORE1_IP
  loopback0: 10.255.255.1
```

### 3. Set Credentials

```bash
# Create vault file
ansible-vault create ansible/group_vars/vault.yml

# Add your credentials:
vault_device_password: "your_password"
vault_enable_password: "your_enable"
vault_radius_key: "your_radius_key"
vault_dnac_password: "your_dnac_password"
vault_ise_password: "your_ise_password"
```

### 4. Run Automation

#### Option A: Ansible

```bash
# Configure underlay
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/01-prepare-underlay.yml

# Configure authentication
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/02-configure-authentication.yml

# Deploy fabric
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/03-deploy-fabric.yml
```

#### Option B: Python

```bash
# Deploy fabric
python3 python_scripts/dnac_fabric_manager.py \
  --host YOUR_DNAC_IP \
  --username admin \
  --password YOUR_PASSWORD \
  --config config/fabric-config.json

# Configure ISE
python3 python_scripts/ise_policy_manager.py \
  --host YOUR_ISE_IP \
  --username admin \
  --password YOUR_PASSWORD \
  --config config/ise-config.json
```

## What's Included

### Documentation
- Hardware requirements list
- 16-week migration guide
- Mac setup instructions
- Example configurations

### Automation
- 3 Ansible playbooks
- 2 Python scripts
- Pre-configured templates
- Example configurations

### Configuration Files
- Device inventory
- Variable definitions
- Fabric configuration
- ISE policy configuration

## Next Steps

1. Review [docs/hardware-requirements.md](docs/hardware-requirements.md)
2. Read [docs/migration-guide.md](docs/migration-guide.md)
3. Customize `ansible/group_vars/all.yml`
4. Test in lab environment
5. Follow migration phases

## Common Commands

### Verify Setup
```bash
# Check Python
python3 --version

# Check Ansible
ansible --version

# Test inventory
ansible-inventory -i ansible/inventory/hosts.yml --list

# Test connectivity
ansible -i ansible/inventory/hosts.yml all -m ping
```

### Backup Configs
```bash
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/01-prepare-underlay.yml \
  --tags backup
```

### Verify Deployment
```bash
# Check fabric devices
ansible -i ansible/inventory/hosts.yml fabric_devices \
  -m ios_command \
  -a "commands='show fabric summary'"
```

## Troubleshooting

### Can't connect to devices
- Verify IP addresses in inventory
- Check network connectivity
- Verify credentials in vault

### Python errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

### Ansible errors
- Check vault password
- Verify device credentials
- Review ansible.cfg settings

## Getting Help

- Full documentation: [docs/](docs/)
- Mac setup guide: [docs/mac-setup-guide.md](docs/mac-setup-guide.md)
- Examples: [docs/example-configurations.md](docs/example-configurations.md)
- GitHub Issues: https://github.com/ters-golemi/cisco-sw-access-fabric/issues

## Security Notes

- Store credentials in Ansible Vault
- Add `.env` and `.vault_pass` to `.gitignore`
- Use read-only accounts where possible
- Enable audit logging
- Review security policies regularly

## Quick Reference

| Task | Command |
|------|---------|
| Activate venv | `source venv/bin/activate` |
| Edit inventory | `nano ansible/inventory/hosts.yml` |
| Edit variables | `nano ansible/group_vars/all.yml` |
| Edit vault | `ansible-vault edit ansible/group_vars/vault.yml` |
| Run playbook | `ansible-playbook -i inventory playbook.yml` |
| Python script | `python3 python_scripts/script.py --help` |

## Support Matrix

| Component | Version | Required |
|-----------|---------|----------|
| Python | 3.8+ | Yes |
| Ansible | 2.14+ | Yes |
| DNA Center | 2.2.3+ | Yes |
| ISE | 3.0+ | Yes |
| IOS-XE | 16.12.1+ | Yes |

## Success Checklist

- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Inventory updated
- [ ] Credentials configured
- [ ] Network connectivity verified
- [ ] Lab environment tested
- [ ] Documentation reviewed
- [ ] Backup procedures established
- [ ] Rollback plan documented

Ready to deploy? Start with the migration guide!
