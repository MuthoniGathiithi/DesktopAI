#!/usr/bin/env python3
"""
Network Module for Desktop AI Agent
Handles network diagnostics and connectivity
"""

import subprocess
import socket
import logging
from typing import Dict, Any, List
from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class NetworkModule(BaseModule):
    """
    Network diagnostics and management module
    Tests connectivity, speed, DNS, WiFi
    """
    
    def __init__(self):
        super().__init__(
            name="network",
            description="Network diagnostics and management",
            version="1.0.0"
        )
    
    def get_supported_actions(self) -> List[str]:
        """Get supported network actions"""
        return [
            "test_connectivity",
            "speed_test",
            "ping_server",
            "check_dns",
            "test_wifi_signal",
            "get_network_interfaces",
            "diagnose_connection",
            "switch_dns",
            "get_gateway",
            "test_port"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute network action"""
        try:
            if action == "test_connectivity":
                return self._test_connectivity()
            elif action == "speed_test":
                return self._speed_test()
            elif action == "ping_server":
                return self._ping_server(parameters)
            elif action == "check_dns":
                return self._check_dns()
            elif action == "test_wifi_signal":
                return self._test_wifi_signal()
            elif action == "get_network_interfaces":
                return self._get_network_interfaces()
            elif action == "diagnose_connection":
                return self._diagnose_connection()
            elif action == "switch_dns":
                return self._switch_dns(parameters)
            elif action == "get_gateway":
                return self._get_gateway()
            elif action == "test_port":
                return self._test_port(parameters)
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unknown action: {action}",
                    data={}
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Error executing {action}",
                data={},
                error=str(e)
            )
    
    def _test_connectivity(self) -> ModuleResult:
        """Test internet connectivity"""
        servers = [
            ("8.8.8.8", "Google DNS"),
            ("1.1.1.1", "Cloudflare DNS"),
            ("208.67.222.222", "OpenDNS")
        ]
        
        results = {}
        connected = False
        
        for server, name in servers:
            try:
                socket.create_connection((server, 53), timeout=2)
                results[name] = True
                connected = True
            except (socket.timeout, socket.error):
                results[name] = False
        
        status = ResultStatus.SUCCESS if connected else ResultStatus.FAILED
        message = "Internet connected" if connected else "No internet connection"
        
        return ModuleResult(
            status=status,
            message=message,
            data={"servers": results, "connected": connected}
        )
    
    def _speed_test(self) -> ModuleResult:
        """Run speed test (requires speedtest-cli)"""
        try:
            result = subprocess.run(
                ["speedtest-cli", "--simple"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    download = float(lines[0])
                    upload = float(lines[1])
                    
                    data = {
                        "download_mbps": download,
                        "upload_mbps": upload
                    }
                    
                    return ModuleResult(
                        status=ResultStatus.SUCCESS,
                        message=f"Download: {download:.2f} Mbps, Upload: {upload:.2f} Mbps",
                        data=data
                    )
            
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Speed test failed",
                data={},
                error=result.stderr
            )
        except FileNotFoundError:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="speedtest-cli not installed",
                data={},
                error="Install with: pip install speedtest-cli"
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Speed test error",
                data={},
                error=str(e)
            )
    
    def _ping_server(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Ping a server"""
        server = parameters.get("server", "8.8.8.8")
        count = parameters.get("count", 4)
        
        try:
            result = subprocess.run(
                ["ping", "-c", str(count), server],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse ping output
                lines = result.stdout.strip().split("\n")
                stats_line = lines[-1]
                
                data = {
                    "server": server,
                    "packets_sent": count,
                    "output": result.stdout
                }
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Ping to {server} successful",
                    data=data
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Ping to {server} failed",
                    data={"server": server},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Ping error",
                data={},
                error=str(e)
            )
    
    def _check_dns(self) -> ModuleResult:
        """Check DNS resolution"""
        test_domains = [
            "google.com",
            "github.com",
            "ubuntu.com"
        ]
        
        results = {}
        all_working = True
        
        for domain in test_domains:
            try:
                ip = socket.gethostbyname(domain)
                results[domain] = ip
            except socket.gaierror:
                results[domain] = "Failed"
                all_working = False
        
        status = ResultStatus.SUCCESS if all_working else ResultStatus.PARTIAL
        
        return ModuleResult(
            status=status,
            message="DNS resolution check complete",
            data={"dns_results": results, "all_working": all_working}
        )
    
    def _test_wifi_signal(self) -> ModuleResult:
        """Test WiFi signal strength"""
        try:
            result = subprocess.run(
                ["iwconfig"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                output = result.stdout
                
                # Parse signal strength
                data = {
                    "output": output,
                    "interfaces": []
                }
                
                # Look for signal strength information
                for line in output.split("\n"):
                    if "Signal level" in line or "Link Quality" in line:
                        data["interfaces"].append(line.strip())
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="WiFi signal info retrieved",
                    data=data
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to get WiFi info",
                    data={},
                    error=result.stderr
                )
        except FileNotFoundError:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="iwconfig not found",
                data={},
                error="Install wireless-tools: sudo apt install wireless-tools"
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="WiFi signal test error",
                data={},
                error=str(e)
            )
    
    def _get_network_interfaces(self) -> ModuleResult:
        """Get network interfaces"""
        try:
            result = subprocess.run(
                ["ip", "link", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                interfaces = []
                for line in result.stdout.split("\n"):
                    if ":" in line and not line.startswith(" "):
                        interfaces.append(line.strip())
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Network interfaces retrieved",
                    data={"interfaces": interfaces}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to get interfaces",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Error getting interfaces",
                data={},
                error=str(e)
            )
    
    def _diagnose_connection(self) -> ModuleResult:
        """Full connection diagnosis"""
        diagnostics = {}
        
        # Test connectivity
        connectivity = self._test_connectivity()
        diagnostics["connectivity"] = connectivity.to_dict()
        
        # Check DNS
        dns = self._check_dns()
        diagnostics["dns"] = dns.to_dict()
        
        # Get interfaces
        interfaces = self._get_network_interfaces()
        diagnostics["interfaces"] = interfaces.to_dict()
        
        # Ping common server
        ping = self._ping_server({"server": "8.8.8.8"})
        diagnostics["ping"] = ping.to_dict()
        
        status = ResultStatus.SUCCESS
        if not connectivity.data.get("connected"):
            status = ResultStatus.FAILED
        
        return ModuleResult(
            status=status,
            message="Network diagnosis complete",
            data=diagnostics
        )
    
    def _switch_dns(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Switch DNS servers"""
        dns_provider = parameters.get("provider", "cloudflare")
        
        dns_servers = {
            "google": "8.8.8.8 8.8.4.4",
            "cloudflare": "1.1.1.1 1.0.0.1",
            "opendns": "208.67.222.222 208.67.220.220"
        }
        
        dns = dns_servers.get(dns_provider)
        if not dns:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Unknown DNS provider: {dns_provider}",
                data={}
            )
        
        try:
            # This requires sudo and modifying system files
            # For now, just return the command needed
            command = f"sudo nano /etc/resolv.conf  # Add: nameserver {dns.split()[0]}"
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"To switch to {dns_provider} DNS, run: {command}",
                data={"dns_servers": dns, "provider": dns_provider}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to switch DNS",
                data={},
                error=str(e)
            )
    
    def _get_gateway(self) -> ModuleResult:
        """Get default gateway"""
        try:
            result = subprocess.run(
                ["ip", "route", "show"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                gateway = None
                for line in result.stdout.split("\n"):
                    if "default via" in line:
                        parts = line.split()
                        gateway = parts[2]
                        break
                
                data = {
                    "gateway": gateway,
                    "routes": result.stdout
                }
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Gateway: {gateway}",
                    data=data
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to get gateway",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Error getting gateway",
                data={},
                error=str(e)
            )
    
    def _test_port(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Test if a port is open"""
        host = parameters.get("host", "localhost")
        port = parameters.get("port")
        
        if not port:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="port parameter required",
                data={}
            )
        
        try:
            socket.create_connection((host, int(port)), timeout=2)
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"Port {port} on {host} is open",
                data={"host": host, "port": port, "open": True}
            )
        except (socket.timeout, socket.error):
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Port {port} on {host} is closed",
                data={"host": host, "port": port, "open": False}
            )


if __name__ == "__main__":
    module = NetworkModule()
    print("Network Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
    
    # Test connectivity
    result = module.execute("test_connectivity", {})
    print(f"\nConnectivity: {result.message}")
