#!/usr/bin/env python3
"""
ISE Policy Manager
This script automates ISE configuration for SD-Access deployment
"""

import json
import requests
import argparse
from typing import Dict, List, Optional
from urllib3.exceptions import InsecureRequestWarning

# Suppress SSL warnings
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)


class ISEPolicyManager:
    """Manages ISE configuration for SD-Access"""
    
    def __init__(self, host: str, username: str, password: str, verify_ssl: bool = False):
        """
        Initialize ISE connection
        
        Args:
            host: ISE IP or hostname
            username: ISE username
            password: ISE password
            verify_ssl: Whether to verify SSL certificates
        """
        self.host = host
        self.username = username
        self.password = password
        self.verify_ssl = verify_ssl
        self.base_url = f"https://{host}"
        self.session = requests.Session()
        self.session.auth = (username, password)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make API request to ISE
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request payload
            
        Returns:
            Response JSON or None on error
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method,
                url,
                json=data,
                verify=self.verify_ssl,
                timeout=30
            )
            response.raise_for_status()
            
            if response.text:
                return response.json()
            return {"status": "success"}
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response: {e.response.text}")
            return None
    
    def create_security_group(self, name: str, tag: int, description: str = "") -> bool:
        """
        Create Security Group Tag (SGT)
        
        Args:
            name: Security group name
            tag: SGT value
            description: Description
            
        Returns:
            bool: True if successful
        """
        endpoint = "/ers/config/sgt"
        data = {
            "Sgt": {
                "name": name,
                "value": tag,
                "description": description,
                "generationId": "0"
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Security group created: {name} (SGT {tag})")
            return True
        return False
    
    def get_security_groups(self) -> List[Dict]:
        """Get all security groups"""
        endpoint = "/ers/config/sgt"
        result = self._make_request("GET", endpoint)
        
        if result and "SearchResult" in result:
            return result["SearchResult"].get("resources", [])
        return []
    
    def create_sgacl(self, name: str, description: str, acl_content: str) -> bool:
        """
        Create Security Group ACL
        
        Args:
            name: SGACL name
            description: Description
            acl_content: ACL content/rules
            
        Returns:
            bool: True if successful
        """
        endpoint = "/ers/config/sgacl"
        data = {
            "Sgacl": {
                "name": name,
                "description": description,
                "aclcontent": acl_content,
                "generationId": "0"
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"SGACL created: {name}")
            return True
        return False
    
    def create_egress_policy(self, name: str, source_sgt: str, dest_sgt: str, 
                            sgacl_name: str) -> bool:
        """
        Create TrustSec egress policy
        
        Args:
            name: Policy name
            source_sgt: Source SGT name
            dest_sgt: Destination SGT name
            sgacl_name: SGACL to apply
            
        Returns:
            bool: True if successful
        """
        endpoint = "/ers/config/egressmatrixcell"
        data = {
            "EgressMatrixCell": {
                "name": name,
                "sourceSgtId": source_sgt,
                "destinationSgtId": dest_sgt,
                "matrixCellStatus": "ENABLED",
                "defaultRule": "NONE",
                "sgacls": [sgacl_name]
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Egress policy created: {source_sgt} -> {dest_sgt}")
            return True
        return False
    
    def add_network_device(self, name: str, ip_address: str, radius_key: str,
                          device_type: str = "Cisco") -> bool:
        """
        Add network device to ISE
        
        Args:
            name: Device name
            ip_address: Device IP
            radius_key: RADIUS shared secret
            device_type: Device type
            
        Returns:
            bool: True if successful
        """
        endpoint = "/ers/config/networkdevice"
        data = {
            "NetworkDevice": {
                "name": name,
                "NetworkDeviceIPList": [{
                    "ipaddress": ip_address,
                    "mask": 32
                }],
                "NetworkDeviceGroupList": [
                    f"Device Type#All Device Types#{device_type}",
                    "Location#All Locations",
                    "IPSEC#Is IPSEC Device#No"
                ],
                "authenticationSettings": {
                    "networkProtocol": "RADIUS",
                    "radiusSharedSecret": radius_key,
                    "enableKeyWrap": False
                }
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Network device added: {name} ({ip_address})")
            return True
        return False
    
    def create_authorization_profile(self, name: str, vlan: int, 
                                    sgt: int, description: str = "") -> bool:
        """
        Create authorization profile
        
        Args:
            name: Profile name
            vlan: VLAN ID
            sgt: Security Group Tag
            description: Description
            
        Returns:
            bool: True if successful
        """
        endpoint = "/ers/config/authorizationprofile"
        data = {
            "AuthorizationProfile": {
                "name": name,
                "description": description,
                "accessType": "ACCESS_ACCEPT",
                "vlan": {
                    "nameID": str(vlan),
                    "tagID": vlan
                },
                "advancedAttributes": [
                    {
                        "leftHandSideDictionaryAttribue": {
                            "AdvancedAttributeValueType": "AttributeReference",
                            "dictionaryName": "Cisco",
                            "attributeName": "cisco-av-pair"
                        },
                        "rightHandSideAttribueValue": {
                            "AdvancedAttributeValueType": "StaticValue",
                            "value": f"cts:security-group-tag={sgt}"
                        }
                    }
                ]
            }
        }
        
        result = self._make_request("POST", endpoint, data)
        
        if result:
            print(f"Authorization profile created: {name}")
            return True
        return False
    
    def deploy_full_config(self, config_file: str) -> bool:
        """
        Deploy complete ISE configuration from file
        
        Args:
            config_file: Path to JSON configuration file
            
        Returns:
            bool: True if successful
        """
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Create security groups
            print("\n=== Creating Security Groups ===")
            for sg in config.get("security_groups", []):
                self.create_security_group(
                    sg["name"],
                    sg["tag"],
                    sg.get("description", "")
                )
            
            # Add network devices
            print("\n=== Adding Network Devices ===")
            for device in config.get("network_devices", []):
                self.add_network_device(
                    device["name"],
                    device["ip"],
                    device["radius_key"],
                    device.get("type", "Cisco")
                )
            
            # Create SGACLs
            print("\n=== Creating SGACLs ===")
            for sgacl in config.get("sgacls", []):
                self.create_sgacl(
                    sgacl["name"],
                    sgacl.get("description", ""),
                    sgacl["acl_content"]
                )
            
            # Create authorization profiles
            print("\n=== Creating Authorization Profiles ===")
            for profile in config.get("authorization_profiles", []):
                self.create_authorization_profile(
                    profile["name"],
                    profile["vlan"],
                    profile["sgt"],
                    profile.get("description", "")
                )
            
            print("\n=== ISE Configuration Complete ===")
            return True
            
        except Exception as e:
            print(f"Configuration failed: {e}")
            return False


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="ISE Policy Manager")
    parser.add_argument("--host", required=True, help="ISE IP or hostname")
    parser.add_argument("--username", required=True, help="ISE username")
    parser.add_argument("--password", required=True, help="ISE password")
    parser.add_argument("--config", required=True, help="Path to configuration JSON file")
    parser.add_argument("--verify-ssl", action="store_true", help="Verify SSL certificates")
    
    args = parser.parse_args()
    
    # Create manager instance
    manager = ISEPolicyManager(
        host=args.host,
        username=args.username,
        password=args.password,
        verify_ssl=args.verify_ssl
    )
    
    # Deploy configuration
    if manager.deploy_full_config(args.config):
        print("\nISE configuration successful!")
        return 0
    else:
        print("\nISE configuration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
