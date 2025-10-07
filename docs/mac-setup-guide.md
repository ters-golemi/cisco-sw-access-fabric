# Mac Setup Guide for SD-Access Automation

This guide provides step-by-step instructions to set up the SD-Access automation tools on macOS.

## Prerequisites

- macOS 10.15 (Catalina) or later
- Administrator access
- Internet connection
- Network access to DNA Center and ISE

## Installation Steps

### 1. Install Homebrew

Homebrew is a package manager for macOS that simplifies software installation.

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Verify installation
brew --version
```

### 2. Install Python 3

```bash
# Install Python 3 via Homebrew
brew install python3

# Verify installation
python3 --version

# Should show Python 3.8 or later
```

### 3. Install Git

```bash
# Install Git
brew install git

# Verify installation
git --version

# Configure Git (optional)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 4. Clone the Repository

```bash
# Create a workspace directory
mkdir -p ~/workspace
cd ~/workspace

# Clone the repository
git clone https://github.com/ters-golemi/cisco-sw-access-fabric.git

# Navigate to the repository
cd cisco-sw-access-fabric
```

### 5. Set Up Python Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Your prompt should now show (venv) at the beginning
```

### 6. Install Python Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install required packages
pip install -r requirements.txt
```

### 7. Install Ansible

```bash
# Install Ansible via pip
pip install ansible

# Install Ansible collections for network automation
ansible-galaxy collection install cisco.ios
ansible-galaxy collection install cisco.dnac
ansible-galaxy collection install community.general

# Verify installation
ansible --version
```

### 8. Configure Environment Variables

```bash
# Create environment file
cat > .env << 'EOF'
# DNA Center Configuration
DNAC_HOST=10.1.1.10
DNAC_USERNAME=admin
DNAC_PASSWORD=your_password_here

# ISE Configuration
ISE_HOST=10.1.1.20
ISE_USERNAME=admin
ISE_PASSWORD=your_password_here

# Network Device Credentials
DEVICE_USERNAME=admin
DEVICE_PASSWORD=your_password_here
DEVICE_ENABLE_PASSWORD=your_enable_password_here

# RADIUS Shared Secret
RADIUS_KEY=your_radius_key_here
EOF

# Make sure to edit the file with your actual credentials
nano .env
```

### 9. Configure Ansible Vault for Secrets

```bash
# Create Ansible vault password file
echo "your_vault_password" > .vault_pass

# Secure the file
chmod 600 .vault_pass

# Create encrypted vault file for sensitive data
ansible-vault create ansible/group_vars/vault.yml --vault-password-file .vault_pass
```

Add the following content to the vault file:

```yaml
---
vault_device_password: "your_device_password"
vault_enable_password: "your_enable_password"
vault_radius_key: "your_radius_key"
vault_dnac_password: "your_dnac_password"
vault_ise_password: "your_ise_password"
```

### 10. Install Additional Tools (Optional)

```bash
# Install jq for JSON processing
brew install jq

# Install yq for YAML processing
brew install yq

# Install network utilities
brew install nmap telnet

# Install text editor (if needed)
brew install vim
# or
brew install nano
```

### 11. Test Network Connectivity

```bash
# Test connectivity to DNA Center
ping -c 4 10.1.1.10

# Test connectivity to ISE
ping -c 4 10.1.1.20

# Test HTTPS connectivity
curl -k https://10.1.1.10
```

### 12. Verify Setup

```bash
# Verify Python installation
python3 --version

# Verify Ansible installation
ansible --version

# Verify Ansible collections
ansible-galaxy collection list | grep cisco

# Test Ansible inventory
ansible-inventory -i ansible/inventory/hosts.yml --list

# Run a simple Ansible ping (requires devices to be accessible)
ansible -i ansible/inventory/hosts.yml all -m ping --ask-pass
```

## Configuration Files

### Update Inventory File

Edit `ansible/inventory/hosts.yml` with your actual device IP addresses:

```bash
nano ansible/inventory/hosts.yml
```

Update the following:
- DNA Center IP addresses
- ISE IP addresses
- Network device IP addresses
- Loopback addresses
- Interface names

### Update Variables

Edit `ansible/group_vars/all.yml` with your network specifics:

```bash
nano ansible/group_vars/all.yml
```

Update the following:
- NTP servers
- DNS servers
- VLAN to VN mappings
- IP addressing schemes
- Security group definitions

## Running the Automation

### Option 1: Using Ansible Playbooks

```bash
# Activate virtual environment
source venv/bin/activate

# Run underlay configuration
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/01-prepare-underlay.yml \
  --vault-password-file .vault_pass

# Run authentication configuration
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/02-configure-authentication.yml \
  --vault-password-file .vault_pass

# Run fabric deployment
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/03-deploy-fabric.yml \
  --vault-password-file .vault_pass
```

### Option 2: Using Python Scripts

```bash
# Activate virtual environment
source venv/bin/activate

# Load environment variables
source .env

# Run DNA Center fabric manager
python3 python_scripts/dnac_fabric_manager.py \
  --host $DNAC_HOST \
  --username $DNAC_USERNAME \
  --password $DNAC_PASSWORD \
  --config config/fabric-config.json

# Run ISE policy manager
python3 python_scripts/ise_policy_manager.py \
  --host $ISE_HOST \
  --username $ISE_USERNAME \
  --password $ISE_PASSWORD \
  --config config/ise-config.json
```

## Troubleshooting

### Issue: Python not found

```bash
# Install Python via Homebrew
brew install python3

# Add to PATH if needed
echo 'export PATH="/usr/local/opt/python/libexec/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Issue: Ansible command not found

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall Ansible
pip install --upgrade ansible
```

### Issue: Connection timeout to devices

```bash
# Check network connectivity
ping 10.1.1.10

# Check firewall settings
# System Preferences > Security & Privacy > Firewall

# Test SSH connectivity
ssh admin@10.1.1.10
```

### Issue: SSL certificate verification failed

```bash
# For testing only, you can disable SSL verification
# Add --verify-ssl=false flag to Python scripts
# Or set ANSIBLE_HOST_KEY_CHECKING=False in ansible.cfg
```

### Issue: Permission denied errors

```bash
# Fix file permissions
chmod 600 .vault_pass
chmod 755 python_scripts/*.py

# Run with sudo if needed (generally not recommended)
sudo pip install -r requirements.txt
```

## Directory Structure

After setup, your directory structure should look like this:

```
cisco-sw-access-fabric/
├── .env                          # Environment variables (not committed)
├── .vault_pass                   # Vault password (not committed)
├── venv/                         # Python virtual environment (not committed)
├── README.md                     # Project overview
├── requirements.txt              # Python dependencies
├── ansible/
│   ├── ansible.cfg              # Ansible configuration
│   ├── inventory/
│   │   └── hosts.yml            # Device inventory
│   ├── group_vars/
│   │   ├── all.yml              # Global variables
│   │   └── vault.yml            # Encrypted secrets
│   ├── playbooks/
│   │   ├── 01-prepare-underlay.yml
│   │   ├── 02-configure-authentication.yml
│   │   └── 03-deploy-fabric.yml
│   └── templates/               # Configuration templates
├── python_scripts/
│   ├── dnac_fabric_manager.py   # DNA Center automation
│   └── ise_policy_manager.py    # ISE automation
├── docs/
│   ├── hardware-requirements.md
│   ├── migration-guide.md
│   └── mac-setup-guide.md
└── config/                       # Configuration files
    ├── fabric-config.json
    └── ise-config.json
```

## Best Practices

### Security

1. **Never commit sensitive data**:
   - Add `.env`, `.vault_pass`, `*.pem` to `.gitignore`
   - Use Ansible Vault for secrets
   - Use environment variables for credentials

2. **Use SSH keys**:
   ```bash
   # Generate SSH key
   ssh-keygen -t rsa -b 4096 -C "automation@example.com"
   
   # Copy to devices (if supported)
   ssh-copy-id admin@10.1.1.10
   ```

3. **Limit access**:
   - Use read-only accounts where possible
   - Create dedicated automation accounts
   - Enable audit logging

### Version Control

```bash
# Create .gitignore
cat > .gitignore << 'EOF'
# Environment files
.env
.vault_pass

# Virtual environment
venv/
*.pyc
__pycache__/

# Backups
backups/
*.cfg.bak

# Logs
*.log

# IDE
.vscode/
.idea/

# macOS
.DS_Store
EOF

# Commit changes
git add .
git commit -m "Initial setup"
git push
```

### Backup

```bash
# Create backup directory
mkdir -p backups

# Backup device configurations regularly
ansible-playbook -i ansible/inventory/hosts.yml \
  ansible/playbooks/backup-configs.yml

# Backup DNA Center
# (Use DNA Center's built-in backup feature)

# Backup ISE
# (Use ISE's built-in backup feature)
```

## Updates and Maintenance

### Update Python Packages

```bash
# Activate virtual environment
source venv/bin/activate

# Update all packages
pip list --outdated
pip install --upgrade -r requirements.txt

# Update specific package
pip install --upgrade ansible
```

### Update Ansible Collections

```bash
ansible-galaxy collection install cisco.ios --force
ansible-galaxy collection install cisco.dnac --force
```

### Update Repository

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt
ansible-galaxy collection install -r requirements.yml
```

## Getting Help

### Resources

- **Cisco SD-Access Documentation**: https://www.cisco.com/c/en/us/solutions/enterprise-networks/sd-access/
- **DNA Center API Documentation**: https://developer.cisco.com/docs/dna-center/
- **ISE API Documentation**: https://developer.cisco.com/docs/identity-services-engine/
- **Ansible Network Automation**: https://docs.ansible.com/ansible/latest/network/index.html

### Community

- Cisco DevNet Community: https://community.cisco.com/t5/devnet/ct-p/devnet
- Ansible Network Automation: https://www.ansible.com/products/network-automation

### Support

- Cisco TAC: https://www.cisco.com/c/en/us/support/index.html
- GitHub Issues: https://github.com/ters-golemi/cisco-sw-access-fabric/issues

## Next Steps

After completing the setup:

1. Review and customize the configuration files
2. Test in a lab environment first
3. Follow the migration guide for production deployment
4. Monitor the deployment using DNA Center Assurance
5. Document any customizations or issues

## Maintenance Schedule

Recommended maintenance tasks:

- **Weekly**: Review logs and monitor fabric health
- **Monthly**: Update Python packages and Ansible collections
- **Quarterly**: Review and update security policies
- **Annually**: Review hardware and software lifecycle

## Uninstall

If you need to remove the setup:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv

# Remove cloned repository
cd ..
rm -rf cisco-sw-access-fabric

# Uninstall Homebrew packages (optional)
brew uninstall python3 ansible git
```
