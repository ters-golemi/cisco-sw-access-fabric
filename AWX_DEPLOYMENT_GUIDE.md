# Ansible AWX Deployment and Automation Guide for macOS

## Table of Contents
1. [Prerequisites and Environment Setup](#prerequisites-and-environment-setup)
2. [AWX Installation on macOS](#awx-installation-on-macos)
3. [AWX Configuration for Cisco SD-Access](#awx-configuration-for-cisco-sd-access)
4. [Integration with Existing Automation](#integration-with-existing-automation)
5. [Project Setup and Execution](#project-setup-and-execution)
6. [Operational Procedures](#operational-procedures)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites and Environment Setup

### System Requirements

**Minimum macOS Requirements:**
- macOS Big Sur (11.0) or later
- 8GB RAM (16GB recommended for large network deployments)
- 50GB available disk space
- Intel or Apple Silicon processor

**Required Software:**
- Docker Desktop for Mac
- Homebrew package manager
- Git command line tools
- Python 3.9 or later

### Initial Environment Setup

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install required packages
brew install git python@3.11 docker-compose kubectl helm

# Install Docker Desktop
brew install --cask docker

# Verify installations
python3 --version
docker --version
docker-compose --version
```

### Python Environment Setup

```bash
# Create virtual environment for AWX management
python3 -m venv awx-env
source awx-env/bin/activate

# Install AWX CLI and dependencies
pip install --upgrade pip
pip install awxkit ansible-core requests pyyaml jinja2
pip install kubernetes docker-compose

# Verify AWX CLI installation
awx --version
```

---

## AWX Installation on macOS

### Method 1: AWX Operator with Kubernetes (Recommended)

**Install Kubernetes Tools:**

```bash
# Install minikube for local Kubernetes cluster
brew install minikube

# Start minikube with sufficient resources
minikube start --driver=docker --memory=8192 --cpus=4

# Verify cluster is running
kubectl cluster-info
```

**Deploy AWX Operator:**

```bash
# Clone AWX Operator repository
git clone https://github.com/ansible/awx-operator.git
cd awx-operator

# Create AWX namespace
kubectl create namespace awx

# Deploy AWX Operator
make deploy

# Verify operator deployment
kubectl get pods -n awx-operator-system
```

**Create AWX Instance:**

```bash
# Create AWX configuration file
cat << 'EOF' > awx-demo.yaml
apiVersion: awx.ansible.com/v1beta1
kind: AWX
metadata:
  name: awx-demo
  namespace: awx
spec:
  service_type: nodeport
  hostname: awx-demo.local
  projects_persistence: true
  projects_storage_size: 8Gi
  web_replicas: 1
  task_replicas: 1
  postgres_storage_requirements:
    requests:
      storage: 8Gi
EOF

# Apply AWX configuration
kubectl apply -f awx-demo.yaml -n awx

# Monitor deployment progress
kubectl get pods -n awx -w
```

**Access AWX Web Interface:**

```bash
# Get AWX service details
kubectl get svc -n awx

# Forward AWX web interface port
kubectl port-forward svc/awx-demo-service 8080:80 -n awx

# Get admin password
kubectl get secret awx-demo-admin-password -o jsonpath="{.data.password}" -n awx | base64 --decode

# Access AWX at http://localhost:8080
# Username: admin
# Password: (output from previous command)
```

### Method 2: Docker Compose (Alternative)

**Create AWX Docker Environment:**

```bash
# Create AWX project directory
mkdir -p ~/awx-docker && cd ~/awx-docker

# Create docker-compose.yml for AWX
cat << 'EOF' > docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: awx
      POSTGRES_USER: awx
      POSTGRES_PASSWORD: awxpass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    
  redis:
    image: redis:7
    
  awx-web:
    image: quay.io/ansible/awx:latest
    depends_on:
      - redis
      - postgres
    ports:
      - "8080:8052"
    environment:
      SECRET_KEY: awxsecret
      DATABASE_NAME: awx
      DATABASE_USER: awx
      DATABASE_PASSWORD: awxpass
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - awx_projects:/var/lib/awx/projects
      
  awx-task:
    image: quay.io/ansible/awx:latest
    depends_on:
      - redis
      - postgres
    environment:
      SECRET_KEY: awxsecret
      DATABASE_NAME: awx
      DATABASE_USER: awx
      DATABASE_PASSWORD: awxpass
      DATABASE_HOST: postgres
      DATABASE_PORT: 5432
      REDIS_HOST: redis
      REDIS_PORT: 6379
    volumes:
      - awx_projects:/var/lib/awx/projects
    command: /usr/bin/launch_awx_task.sh

volumes:
  postgres_data:
  awx_projects:
EOF

# Start AWX services
docker-compose up -d

# Check service status
docker-compose ps
```

---

## AWX Configuration for Cisco SD-Access

### Initial AWX Setup

**Create Organization and Team:**

```bash
# Using AWX CLI
awx organizations create --name "Network Engineering" --description "Cisco Network Automation"
awx teams create --name "SD-Access Team" --organization "Network Engineering"
```

**Configure Credentials:**

1. **Device Credentials (Network)**
   ```bash
   awx credentials create \
     --name "Cisco Device Credentials" \
     --credential_type "Network" \
     --organization "Network Engineering" \
     --inputs '{
       "username": "admin",
       "password": "your_device_password",
       "authorize": true,
       "authorize_password": "your_enable_password"
     }'
   ```

2. **Source Control Credentials**
   ```bash
   awx credentials create \
     --name "GitHub Access" \
     --credential_type "Source Control" \
     --organization "Network Engineering" \
     --inputs '{
       "username": "your_github_username",
       "password": "your_github_token"
     }'
   ```

**Create Inventory:**

```bash
# Create main inventory
awx inventory create \
  --name "SD-Access Infrastructure" \
  --organization "Network Engineering" \
  --description "Cisco SD-Access network devices"

# Create inventory groups
awx groups create \
  --name "wan_routers" \
  --inventory "SD-Access Infrastructure" \
  --variables '{
    "ansible_network_os": "ios",
    "ansible_connection": "network_cli"
  }'

awx groups create \
  --name "core_switches" \
  --inventory "SD-Access Infrastructure" \
  --variables '{
    "ansible_network_os": "ios",
    "ansible_connection": "network_cli"
  }'

awx groups create \
  --name "access_switches" \
  --inventory "SD-Access Infrastructure" \
  --variables '{
    "ansible_network_os": "ios",
    "ansible_connection": "network_cli"
  }'
```

---

## Integration with Existing Automation

### Project Setup in AWX

**Create Project from Repository:**

```bash
awx projects create \
  --name "SD-Access Automation" \
  --organization "Network Engineering" \
  --scm_type git \
  --scm_url "https://github.com/ters-golemi/cisco-sw-access-fabric.git" \
  --scm_credential "GitHub Access" \
  --scm_update_on_launch true \
  --scm_delete_on_update true
```

**Configure Execution Environment:**

```bash
# Create custom execution environment for Cisco automation
cat << 'EOF' > execution-environment.yml
version: 1
dependencies:
  galaxy: requirements.yml
  python: requirements.txt
  system: bindep.txt

additional_build_steps:
  prepend: |
    RUN pip install netmiko napalm ncclient
    RUN ansible-galaxy collection install cisco.ios cisco.nxos
EOF

# Create requirements for collections
cat << 'EOF' > requirements.yml
collections:
  - cisco.ios
  - cisco.nxos
  - cisco.dnac
  - community.general
  - ansible.netcommon
EOF
```

### Job Templates Configuration

**1. Underlay Network Preparation Template:**

```bash
awx job_templates create \
  --name "SD-Access Underlay Preparation" \
  --job_type run \
  --inventory "SD-Access Infrastructure" \
  --project "SD-Access Automation" \
  --playbook "ansible/playbooks/underlay_preparation.yml" \
  --credential "Cisco Device Credentials" \
  --verbosity 2 \
  --ask_variables_on_launch true
```

**2. ISE Integration Template:**

```bash
awx job_templates create \
  --name "ISE Authentication Setup" \
  --job_type run \
  --inventory "SD-Access Infrastructure" \
  --project "SD-Access Automation" \
  --playbook "ansible/playbooks/ise_integration.yml" \
  --credential "Cisco Device Credentials" \
  --verbosity 2
```

**3. Fabric Configuration Template:**

```bash
awx job_templates create \
  --name "SD-Access Fabric Deployment" \
  --job_type run \
  --inventory "SD-Access Infrastructure" \
  --project "SD-Access Automation" \
  --playbook "ansible/playbooks/fabric_deployment.yml" \
  --credential "Cisco Device Credentials" \
  --verbosity 2 \
  --ask_variables_on_launch true
```

### Workflow Templates

**Create Migration Workflow:**

```bash
# Create workflow template
awx workflow_job_templates create \
  --name "Complete SD-Access Migration" \
  --organization "Network Engineering" \
  --description "End-to-end SD-Access fabric deployment workflow"

# Add workflow nodes
awx workflow_job_template_nodes create \
  --workflow_job_template "Complete SD-Access Migration" \
  --unified_job_template "SD-Access Underlay Preparation" \
  --identifier "underlay_prep"

awx workflow_job_template_nodes create \
  --workflow_job_template "Complete SD-Access Migration" \
  --unified_job_template "ISE Authentication Setup" \
  --identifier "ise_setup"

awx workflow_job_template_nodes create \
  --workflow_job_template "Complete SD-Access Migration" \
  --unified_job_template "SD-Access Fabric Deployment" \
  --identifier "fabric_deploy"
```

---

## Project Setup and Execution

### Device Inventory Management

**Dynamic Inventory Script:**

```python
#!/usr/bin/env python3
"""
AWX Dynamic Inventory Script for SD-Access Infrastructure
Integrates with existing device management
"""

import json
import yaml
from pathlib import Path

def load_device_inventory():
    """Load devices from existing configuration files"""
    inventory_file = Path(__file__).parent / "ansible/inventory/hosts.yml"
    
    with open(inventory_file, 'r') as f:
        static_inventory = yaml.safe_load(f)
    
    # Convert to AWX dynamic inventory format
    awx_inventory = {
        '_meta': {'hostvars': {}},
        'all': {'children': list(static_inventory.keys())}
    }
    
    for group_name, group_data in static_inventory.items():
        if 'hosts' in group_data:
            awx_inventory[group_name] = {
                'hosts': list(group_data['hosts'].keys()),
                'vars': group_data.get('vars', {})
            }
            
            # Add host variables
            for host, host_vars in group_data['hosts'].items():
                awx_inventory['_meta']['hostvars'][host] = host_vars
    
    return awx_inventory

if __name__ == '__main__':
    print(json.dumps(load_device_inventory(), indent=2))
```

### Job Execution Procedures

**1. Pre-Migration Validation:**

```bash
# Launch underlay preparation with validation
awx jobs launch \
  --job_template "SD-Access Underlay Preparation" \
  --extra_vars '{
    "validate_only": true,
    "backup_configs": true,
    "check_prerequisites": true
  }' \
  --monitor
```

**2. Phased Migration Execution:**

```bash
# Execute migration workflow
awx workflow_jobs launch \
  --workflow_job_template "Complete SD-Access Migration" \
  --extra_vars '{
    "migration_phase": "production",
    "rollback_enabled": true,
    "notification_email": "network-team@company.com"
  }' \
  --monitor
```

### Custom Job Templates for SD-Access

**Configuration Backup Template:**

```yaml
# backup_template.yml
- name: "Cisco Configuration Backup"
  hosts: all
  gather_facts: no
  vars:
    backup_dir: "/tmp/awx_configs"
    timestamp: "{{ ansible_date_time.epoch }}"
  
  tasks:
    - name: Create backup directory
      file:
        path: "{{ backup_dir }}/{{ timestamp }}"
        state: directory
      delegate_to: localhost
      run_once: true
    
    - name: Backup device configuration
      cisco.ios.ios_config:
        backup: yes
        backup_options:
          filename: "{{ inventory_hostname }}_{{ timestamp }}.cfg"
          dir_path: "{{ backup_dir }}/{{ timestamp }}"
```

**Health Check Template:**

```yaml
# health_check_template.yml
- name: "SD-Access Health Check"
  hosts: all
  gather_facts: no
  
  tasks:
    - name: Check fabric status
      cisco.ios.ios_command:
        commands:
          - show lisp session
          - show device-tracking database
          - show authentication sessions
          - show fabric summary
      register: health_output
    
    - name: Generate health report
      template:
        src: health_report.j2
        dest: "/tmp/health_report_{{ inventory_hostname }}.txt"
      vars:
        health_data: "{{ health_output }}"
      delegate_to: localhost
```

---

## Operational Procedures

### Daily Operations

**Automated Monitoring Setup:**

```bash
# Create scheduled job for daily health checks
awx schedules create \
  --name "Daily SD-Access Health Check" \
  --unified_job_template "SD-Access Health Check" \
  --rrule "DTSTART:20251008T080000Z RRULE:FREQ=DAILY;INTERVAL=1"

# Create configuration drift detection
awx schedules create \
  --name "Configuration Drift Detection" \
  --unified_job_template "Configuration Backup" \
  --rrule "DTSTART:20251008T060000Z RRULE:FREQ=DAILY;INTERVAL=1"
```

**Emergency Response Procedures:**

```bash
# Quick fabric status check
awx jobs launch \
  --job_template "SD-Access Health Check" \
  --limit "core_switches" \
  --verbosity 3 \
  --monitor

# Emergency rollback procedure
awx jobs launch \
  --job_template "Emergency Rollback" \
  --extra_vars '{
    "rollback_timestamp": "20251007_1200",
    "emergency_mode": true
  }' \
  --monitor
```

### Performance Monitoring

**AWX Performance Optimization:**

```bash
# Monitor AWX resource usage
kubectl top pods -n awx

# Scale AWX components if needed
kubectl patch awx awx-demo -n awx --type merge --patch '
spec:
  web_replicas: 2
  task_replicas: 2
'

# Monitor job execution metrics
awx jobs list --status successful --created__gte 2025-10-01
```

---

## Troubleshooting

### Common Issues and Solutions

**1. AWX Pod Startup Issues:**

```bash
# Check pod status and logs
kubectl get pods -n awx
kubectl logs -f deployment/awx-demo-web -n awx
kubectl logs -f deployment/awx-demo-task -n awx

# Restart AWX services
kubectl rollout restart deployment/awx-demo-web -n awx
kubectl rollout restart deployment/awx-demo-task -n awx
```

**2. Playbook Execution Failures:**

```bash
# Enable debug logging for job template
awx job_templates modify \
  --name "SD-Access Underlay Preparation" \
  --verbosity 4

# Check job output and artifacts
awx jobs get <job_id> --format json
awx job_events list --job <job_id>
```

**3. Network Connectivity Issues:**

```bash
# Test connectivity from AWX to devices
awx ad_hoc_commands create \
  --inventory "SD-Access Infrastructure" \
  --module_name "ping" \
  --module_args "data='ping'" \
  --credential "Cisco Device Credentials" \
  --limit "wan_routers"
```

**4. Performance Issues:**

```bash
# Monitor system resources
minikube ssh -- top
minikube ssh -- df -h

# Increase minikube resources if needed
minikube stop
minikube start --driver=docker --memory=16384 --cpus=6
```

### Log Analysis

**AWX Log Collection:**

```bash
# Collect AWX logs for analysis
kubectl logs deployment/awx-demo-web -n awx > awx-web.log
kubectl logs deployment/awx-demo-task -n awx > awx-task.log

# Analyze job execution logs
awx jobs get <job_id> --format json | jq '.result_stdout'
```

**Network Device Log Integration:**

```yaml
# syslog_integration.yml
- name: Configure syslog integration
  cisco.ios.ios_logging:
    dest: host
    name: "{{ awx_server_ip }}"
    level: informational
    facility: local0
```

### Backup and Recovery

**AWX Configuration Backup:**

```bash
# Backup AWX configuration
kubectl get secret awx-demo-admin-password -o yaml -n awx > awx-admin-secret.yaml
kubectl get awx awx-demo -o yaml -n awx > awx-instance.yaml

# Backup project data
kubectl exec -it deployment/awx-demo-web -n awx -- tar czf /tmp/projects-backup.tar.gz /var/lib/awx/projects/
kubectl cp awx-demo-web-pod:/tmp/projects-backup.tar.gz ./projects-backup.tar.gz -n awx
```

---

## Integration with SD-Access Playbooks

The AWX deployment integrates seamlessly with the existing SD-Access automation in this repository. The playbooks in `ansible/playbooks/` are automatically available in AWX job templates, providing:

- **Underlay network preparation** with automated device discovery
- **Authentication and ISE integration** with policy deployment
- **Fabric overlay configuration** with automated testing
- **Monitoring and validation** with health checks and reporting

This comprehensive AWX setup provides enterprise-grade automation capabilities for managing SD-Access fabric deployments while maintaining the flexibility and reliability required for production network environments.