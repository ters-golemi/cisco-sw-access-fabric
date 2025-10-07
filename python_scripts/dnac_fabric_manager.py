#!/usr/bin/env python3
"""
DNA Center Fabric Manager
This script automates SD-Access fabric deployment using DNA Center APIs
"""

import json
import time
import requests
import argparse
from typing import Dict, List, Optional
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class DNACFabricManager:
    """Manages SD-Access fabric configuration via DNA Center APIs"""
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """
        Initialize DNA Center connection
        
        Args:
            host: DNA Center IP or hostname
            username: DNA Center username
            password: DNA Center password
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}"
        self.token = None
        
    def authenticate(self) -> bool:
        """
        Authenticate to DNA Center and obtain token
        
        Returns:
            bool: True if authentication successful
        """
        url = f"{self.base_url}/dna/system/api/v1/auth/token"
        
        try:
            response = requests.post(
                url,
                auth=(self.username, self.password),
                headers={"Content-Type": "application/json"},
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            self.token = response.json()["Token"]
            print(f"Successfully authenticated to DNA Center at {self.host}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Authentication failed: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make authenticated API request
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            data: Request payload
            
        Returns:
            Response JSON or None on error
        """
        if not self.token:
            print("Not authenticated. Call authenticate() first.")
            return None
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "X-Auth-Token": self.token,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=data,
                verify=self.verify_ssl,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e.response, 'text'):
                print(f"Response: {e.response.text}")
            return None
    
    def get_devices(self) -> List[Dict]:
        """Get all network devices from inventory"""
        endpoint = "/dna/intent/api/v1/network-device"
        result = self._make_request("GET", endpoint)
        
        if result and "response" in result:
            return result["response"]
        return []
    
    def create_fabric_site(self, site_hierarchy: str, fabric_type: str = "FABRIC_SITE") -> bool:
        """
        Create a fabric site
        
        Args:
            site_hierarchy: Site name hierarchy
            fabric_type: Type of fabric site
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/fabric-site"
        data = {
            "siteNameHierarchy": site_hierarchy,
            "fabricType": fabric_type
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Fabric site created: {site_hierarchy}")
            return True
        return False
    
    def add_control_plane_device(self, device_ip: str, site_hierarchy: str) -> bool:
        """
        Add device as control plane node
        
        Args:
            device_ip: Device management IP
            site_hierarchy: Site name hierarchy
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/control-plane-device"
        data = {
            "deviceManagementIpAddress": device_ip,
            "siteNameHierarchy": site_hierarchy,
            "routeDistributionProtocol": "LISP_BGP"
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Control plane device added: {device_ip}")
            return True
        return False
    
    def add_border_device(self, device_ip: str, site_hierarchy: str, 
                         internal_asn: str = "65001") -> bool:
        """
        Add device as border node
        
        Args:
            device_ip: Device management IP
            site_hierarchy: Site name hierarchy
            internal_asn: Internal BGP AS number
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/border-device"
        data = {
            "deviceManagementIpAddress": device_ip,
            "siteNameHierarchy": site_hierarchy,
            "externalDomainRoutingProtocolName": "BGP",
            "internalAutonomouSystemNumber": internal_asn,
            "borderSessionType": "EXTERNAL"
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Border device added: {device_ip}")
            return True
        return False
    
    def add_edge_device(self, device_ip: str, site_hierarchy: str) -> bool:
        """
        Add device as edge node
        
        Args:
            device_ip: Device management IP
            site_hierarchy: Site name hierarchy
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/edge-device"
        data = {
            "deviceManagementIpAddress": device_ip,
            "siteNameHierarchy": site_hierarchy
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Edge device added: {device_ip}")
            return True
        return False
    
    def create_virtual_network(self, vn_name: str, site_hierarchy: str) -> bool:
        """
        Create a virtual network
        
        Args:
            vn_name: Virtual network name
            site_hierarchy: Site name hierarchy
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/virtual-network"
        data = {
            "virtualNetworkName": vn_name,
            "siteNameHierarchy": site_hierarchy
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Virtual network created: {vn_name}")
            return True
        return False
    
    def add_ip_pool_to_vn(self, vn_name: str, ip_pool: str, gateway: str) -> bool:
        """
        Add IP pool to virtual network
        
        Args:
            vn_name: Virtual network name
            ip_pool: IP pool range (CIDR)
            gateway: Gateway IP address
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/virtualnetwork/ippool"
        data = {
            "virtualNetworkName": vn_name,
            "ipPoolName": f"{vn_name}_Pool",
            "trafficType": "DATA",
            "ipPoolRange": ip_pool,
            "gateway": gateway
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"IP pool added to {vn_name}: {ip_pool}")
            return True
        return False
    
    def provision_device(self, device_ip: str, site_hierarchy: str) -> bool:
        """
        Provision fabric configuration to device
        
        Args:
            device_ip: Device management IP
            site_hierarchy: Site name hierarchy
            
        Returns:
            bool: True if successful
        """
        endpoint = "/dna/intent/api/v1/business/sda/provision-device"
        data = {
            "deviceManagementIpAddress": device_ip,
            "siteNameHierarchy": site_hierarchy
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Device provisioning initiated: {device_ip}")
            return True
        return False
    
    def get_fabric_sites(self) -> List[Dict]:
        """Get all fabric sites"""
        endpoint = "/dna/intent/api/v1/business/sda/fabric-site"
        result = self._make_request("GET", endpoint)
        
        if result and "response" in result:
            return result["response"]
        return []
    
    def deploy_full_fabric(self, config_file: str) -> bool:
        """
        Deploy complete fabric from configuration file
        
        Args:
            config_file: Path to JSON configuration file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Create fabric site
            print("\n=== Creating Fabric Site ===")
            if not self.create_fabric_site(
                config["fabric_site"]["site_hierarchy"],
                config["fabric_site"]["fabric_type"]
            ):
                return False
            
            time.sleep(5)
            
            # Add control plane devices
            print("\n=== Adding Control Plane Devices ===")
            for device in config.get("control_plane_devices", []):
                self.add_control_plane_device(
                    device["ip"],
                    config["fabric_site"]["site_hierarchy"]
                )
                time.sleep(2)
            
            # Add border devices
            print("\n=== Adding Border Devices ===")
            for device in config.get("border_devices", []):
                self.add_border_device(
                    device["ip"],
                    config["fabric_site"]["site_hierarchy"]
                )
                time.sleep(2)
            
            # Add edge devices
            print("\n=== Adding Edge Devices ===")
            for device in config.get("edge_devices", []):
                self.add_edge_device(
                    device["ip"],
                    config["fabric_site"]["site_hierarchy"]
                )
                time.sleep(2)
            
            # Create virtual networks
            print("\n=== Creating Virtual Networks ===")
            for vn in config.get("virtual_networks", []):
                if self.create_virtual_network(
                    vn["name"],
                    config["fabric_site"]["site_hierarchy"]
                ):
                    time.sleep(2)
                    self.add_ip_pool_to_vn(
                        vn["name"],
                        vn["ip_pool"],
                        vn["gateway"]
                    )
                time.sleep(2)
            
            # Provision all devices
            print("\n=== Provisioning Devices ===")
            all_devices = (
                config.get("control_plane_devices", []) +
                config.get("border_devices", []) +
                config.get("edge_devices", [])
            )
            
            for device in all_devices:
                self.provision_device(
                    device["ip"],
                    config["fabric_site"]["site_hierarchy"]
                )
                time.sleep(2)
            
            print("\n=== Fabric Deployment Complete ===")
            print("Note: Device provisioning may take 10-20 minutes to complete.")
            return True
            
        except Exception as e:
            print(f"Deployment failed: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="DNA Center Fabric Manager")
    parser.add_argument("--host", required=True, help="DNA Center IP or hostname")
    parser.add_argument("--username", required=True, help="DNA Center username")
    parser.add_argument("--password", required=True, help="DNA Center password")
    parser.add_argument("--config", required=True, help="Path to configuration JSON file")
    parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates")
    
    args = parser.parse_args()
    
    # Create manager instance
    manager = DNACFabricManager(
        host=args.host,
        username=args.username,
        password=args.password,
        verify_ssl=args.verify_ssl
    )
    
    # Authenticate
    if not manager.authenticate():
        print("Authentication failed. Exiting.")
        return 1
    
    # Deploy fabric
    if manager.deploy_full_fabric(args.config):
        print("\nFabric deployment successful!")
        return 0
    else:
        print("\nFabric deployment failed!")
        return 1


if __name__ == "__main__":
    exit(main())
