#!/usr/bin/env python3
"""
Setup Validation Script
Validates that the SD-Access automation environment is properly configured
"""

import sys
import os
import subprocess
from pathlib import Path


class Colors:
    """ANSI color codes"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def check_command(command, name):
    """Check if a command is available"""
    try:
        result = subprocess.run(
            [command, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.decode().split('\n')[0]
            print_success(f"{name} is installed: {version}")
            return True
        else:
            print_error(f"{name} is not installed")
            return False
    except FileNotFoundError:
        print_error(f"{name} is not installed")
        return False
    except Exception as e:
        print_warning(f"Could not check {name}: {e}")
        return False


def check_python_package(package_name):
    """Check if a Python package is installed"""
    try:
        __import__(package_name)
        print_success(f"Python package '{package_name}' is installed")
        return True
    except ImportError:
        print_error(f"Python package '{package_name}' is not installed")
        return False


def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print_success(f"{description} exists: {file_path}")
        return True
    else:
        print_error(f"{description} not found: {file_path}")
        return False


def check_directory_structure():
    """Verify directory structure"""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        ('ansible', 'Ansible directory'),
        ('ansible/inventory', 'Ansible inventory directory'),
        ('ansible/playbooks', 'Ansible playbooks directory'),
        ('ansible/group_vars', 'Ansible group variables directory'),
        ('ansible/templates', 'Ansible templates directory'),
        ('python_scripts', 'Python scripts directory'),
        ('config', 'Configuration directory'),
        ('docs', 'Documentation directory')
    ]
    
    all_exist = True
    for dir_path, description in required_dirs:
        if os.path.isdir(dir_path):
            print_success(f"{description}: {dir_path}")
        else:
            print_error(f"{description} missing: {dir_path}")
            all_exist = False
    
    return all_exist


def check_required_files():
    """Check for required files"""
    print_header("Checking Required Files")
    
    required_files = [
        ('README.md', 'README file'),
        ('requirements.txt', 'Python requirements file'),
        ('ansible/ansible.cfg', 'Ansible configuration'),
        ('ansible/inventory/hosts.yml', 'Ansible inventory'),
        ('ansible/group_vars/all.yml', 'Ansible variables'),
        ('ansible/playbooks/01-prepare-underlay.yml', 'Underlay playbook'),
        ('ansible/playbooks/02-configure-authentication.yml', 'Authentication playbook'),
        ('ansible/playbooks/03-deploy-fabric.yml', 'Fabric deployment playbook'),
        ('python_scripts/dnac_fabric_manager.py', 'DNA Center manager script'),
        ('python_scripts/ise_policy_manager.py', 'ISE manager script'),
        ('config/fabric-config.json', 'Fabric configuration'),
        ('config/ise-config.json', 'ISE configuration'),
        ('docs/hardware-requirements.md', 'Hardware requirements'),
        ('docs/migration-guide.md', 'Migration guide'),
        ('docs/mac-setup-guide.md', 'Mac setup guide')
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist


def check_python_environment():
    """Check Python environment"""
    print_header("Checking Python Environment")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major >= 3 and python_version.minor >= 8:
        print_success(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print_error(f"Python version too old: {python_version.major}.{python_version.minor}.{python_version.micro}")
        print_error("Python 3.8 or later is required")
        return False
    
    # Check if in virtual environment
    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    
    if in_venv:
        print_success("Running in virtual environment")
    else:
        print_warning("Not running in virtual environment")
        print_warning("Consider creating one with: python3 -m venv venv")
    
    # Check required Python packages
    packages = ['requests', 'ansible']
    all_installed = True
    for package in packages:
        if not check_python_package(package):
            all_installed = False
    
    return all_installed


def check_system_tools():
    """Check system tools"""
    print_header("Checking System Tools")
    
    tools = [
        ('python3', 'Python 3'),
        ('pip3', 'Pip'),
        ('ansible', 'Ansible'),
        ('ansible-playbook', 'Ansible Playbook'),
        ('git', 'Git')
    ]
    
    all_installed = True
    for command, name in tools:
        if not check_command(command, name):
            all_installed = False
    
    return all_installed


def check_ansible_collections():
    """Check Ansible collections"""
    print_header("Checking Ansible Collections")
    
    try:
        result = subprocess.run(
            ['ansible-galaxy', 'collection', 'list'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10
        )
        
        output = result.stdout.decode()
        
        collections = ['cisco.ios', 'cisco.dnac', 'community.general']
        all_installed = True
        
        for collection in collections:
            if collection in output:
                print_success(f"Ansible collection '{collection}' is installed")
            else:
                print_warning(f"Ansible collection '{collection}' not found")
                print_warning(f"Install with: ansible-galaxy collection install {collection}")
                all_installed = False
        
        return all_installed
        
    except Exception as e:
        print_warning(f"Could not check Ansible collections: {e}")
        return False


def check_configuration():
    """Check configuration files for placeholders"""
    print_header("Checking Configuration")
    
    # Check if inventory has been customized
    inventory_path = 'ansible/inventory/hosts.yml'
    if os.path.exists(inventory_path):
        with open(inventory_path, 'r') as f:
            content = f.read()
            if '10.1.1.10' in content or '10.2.1.1' in content:
                print_warning("Inventory file contains default IP addresses")
                print_warning("Update ansible/inventory/hosts.yml with your actual device IPs")
            else:
                print_success("Inventory file appears to be customized")
    
    # Check for vault file
    vault_path = 'ansible/group_vars/vault.yml'
    if os.path.exists(vault_path):
        print_success("Vault file exists")
    else:
        print_warning("Vault file not found")
        print_warning("Create with: ansible-vault create ansible/group_vars/vault.yml")
    
    # Check for .gitignore
    if os.path.exists('.gitignore'):
        print_success(".gitignore file exists")
        with open('.gitignore', 'r') as f:
            content = f.read()
            if '.env' in content and '.vault_pass' in content:
                print_success(".gitignore properly configured for secrets")
            else:
                print_warning(".gitignore may need to include .env and .vault_pass")
    else:
        print_warning(".gitignore not found")


def print_summary(checks_passed):
    """Print summary"""
    print_header("Validation Summary")
    
    if all(checks_passed.values()):
        print_success("All checks passed!")
        print_success("Your environment is ready for SD-Access automation")
        print(f"\n{Colors.BOLD}Next steps:{Colors.END}")
        print("1. Review and customize ansible/inventory/hosts.yml")
        print("2. Create vault: ansible-vault create ansible/group_vars/vault.yml")
        print("3. Review docs/migration-guide.md")
        print("4. Run: ansible-playbook -i ansible/inventory/hosts.yml ansible/playbooks/01-prepare-underlay.yml")
    else:
        print_warning("Some checks failed")
        print(f"\n{Colors.BOLD}Failed checks:{Colors.END}")
        for check, passed in checks_passed.items():
            if not passed:
                print_error(f"  - {check}")
        print(f"\n{Colors.BOLD}Please fix the issues above before proceeding{Colors.END}")
        print("Refer to docs/mac-setup-guide.md for detailed setup instructions")


def main():
    """Main function"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("SD-Access Automation Environment Validation")
    print("=" * 60)
    print(f"{Colors.END}\n")
    
    # Run all checks
    checks = {
        'Directory Structure': check_directory_structure(),
        'Required Files': check_required_files(),
        'Python Environment': check_python_environment(),
        'System Tools': check_system_tools(),
        'Ansible Collections': check_ansible_collections()
    }
    
    # Check configuration (informational only)
    check_configuration()
    
    # Print summary
    print_summary(checks)
    
    # Return exit code
    if all(checks.values()):
        return 0
    else:
        return 1


if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Validation interrupted{Colors.END}")
        exit(130)
