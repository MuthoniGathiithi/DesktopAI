#!/usr/bin/env python3
"""
Security Module for Desktop AI Agent
Handles security checks, monitoring, and hardening
"""

import subprocess
import os
import logging
from typing import Dict, Any, List
from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class SecurityModule(BaseModule):
    """
    Security module
    Performs security checks, malware scanning, permission audits
    """
    
    def __init__(self):
        super().__init__(
            name="security",
            description="System security and hardening",
            version="1.0.0"
        )
    
    def get_supported_actions(self) -> List[str]:
        """Get supported security actions"""
        return [
            "scan_malware",
            "check_permissions",
            "check_firewall",
            "monitor_logins",
            "check_ssh_keys",
            "find_rootkits",
            "check_updates",
            "audit_users",
            "check_sudo_access",
            "security_report"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute security action"""
        try:
            if action == "scan_malware":
                return self._scan_malware(parameters)
            elif action == "check_permissions":
                return self._check_permissions(parameters)
            elif action == "check_firewall":
                return self._check_firewall()
            elif action == "monitor_logins":
                return self._monitor_logins()
            elif action == "check_ssh_keys":
                return self._check_ssh_keys()
            elif action == "find_rootkits":
                return self._find_rootkits()
            elif action == "check_updates":
                return self._check_updates()
            elif action == "audit_users":
                return self._audit_users()
            elif action == "check_sudo_access":
                return self._check_sudo_access()
            elif action == "security_report":
                return self._security_report()
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
    
    def _scan_malware(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Scan for malware using ClamAV"""
        path = parameters.get("path", os.path.expanduser("~"))
        
        try:
            # Check if ClamAV is installed
            result = subprocess.run(
                ["which", "clamscan"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="ClamAV not installed",
                    data={},
                    error="Install with: sudo apt install clamav"
                )
            
            # Update virus definitions
            subprocess.run(
                ["sudo", "freshclam"],
                capture_output=True,
                timeout=60
            )
            
            # Run scan
            scan_result = subprocess.run(
                ["clamscan", "-r", "-i", path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            data = {
                "path": path,
                "output": scan_result.stdout,
                "infected": "Infected files" in scan_result.stdout
            }
            
            status = ResultStatus.SUCCESS
            if data["infected"]:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message="Malware scan complete",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Malware scan error",
                data={},
                error=str(e)
            )
    
    def _check_permissions(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Check file permissions"""
        path = parameters.get("path", os.path.expanduser("~"))
        
        try:
            result = subprocess.run(
                ["find", path, "-type", "f", "-perm", "-002"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            world_writable = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            data = {
                "path": path,
                "world_writable_files": world_writable,
                "count": len(world_writable)
            }
            
            status = ResultStatus.SUCCESS
            if len(world_writable) > 0:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"Found {len(world_writable)} world-writable files",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Permission check error",
                data={},
                error=str(e)
            )
    
    def _check_firewall(self) -> ModuleResult:
        """Check firewall status"""
        try:
            # Check UFW (Ubuntu Firewall)
            result = subprocess.run(
                ["sudo", "ufw", "status"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                status_text = result.stdout.strip()
                enabled = "active" in status_text.lower()
                
                data = {
                    "firewall": "UFW",
                    "enabled": enabled,
                    "status": status_text
                }
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Firewall status: {status_text}",
                    data=data
                )
            else:
                # Try iptables
                result = subprocess.run(
                    ["sudo", "iptables", "-L"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode == 0:
                    return ModuleResult(
                        status=ResultStatus.SUCCESS,
                        message="Firewall (iptables) is configured",
                        data={"firewall": "iptables"}
                    )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Firewall check error",
                data={},
                error=str(e)
            )
    
    def _monitor_logins(self) -> ModuleResult:
        """Monitor failed login attempts"""
        try:
            result = subprocess.run(
                ["grep", "Failed password", "/var/log/auth.log"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            failed_attempts = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            # Count by IP
            ip_counts = {}
            for line in failed_attempts:
                if "from" in line:
                    parts = line.split("from")
                    if len(parts) > 1:
                        ip = parts[1].strip().split()[0]
                        ip_counts[ip] = ip_counts.get(ip, 0) + 1
            
            data = {
                "total_failed": len(failed_attempts),
                "by_ip": ip_counts
            }
            
            status = ResultStatus.SUCCESS
            if len(failed_attempts) > 10:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"Found {len(failed_attempts)} failed login attempts",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Login monitoring error",
                data={},
                error=str(e)
            )
    
    def _check_ssh_keys(self) -> ModuleResult:
        """Check SSH key security"""
        try:
            ssh_dir = os.path.expanduser("~/.ssh")
            
            if not os.path.exists(ssh_dir):
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="No SSH directory found",
                    data={"ssh_configured": False}
                )
            
            issues = []
            
            # Check directory permissions
            dir_stat = os.stat(ssh_dir)
            if oct(dir_stat.st_mode)[-3:] != "700":
                issues.append(f"SSH directory has wrong permissions: {oct(dir_stat.st_mode)}")
            
            # Check key files
            for filename in os.listdir(ssh_dir):
                if filename.endswith("_key"):
                    filepath = os.path.join(ssh_dir, filename)
                    file_stat = os.stat(filepath)
                    if oct(file_stat.st_mode)[-3:] != "600":
                        issues.append(f"{filename} has wrong permissions: {oct(file_stat.st_mode)}")
            
            data = {
                "ssh_configured": True,
                "issues": issues
            }
            
            status = ResultStatus.SUCCESS if not issues else ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"SSH security check: {len(issues)} issues found",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="SSH key check error",
                data={},
                error=str(e)
            )
    
    def _find_rootkits(self) -> ModuleResult:
        """Scan for rootkits using rkhunter"""
        try:
            result = subprocess.run(
                ["which", "rkhunter"],
                capture_output=True,
                timeout=5
            )
            
            if result.returncode != 0:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="rkhunter not installed",
                    data={},
                    error="Install with: sudo apt install rkhunter"
                )
            
            # Update database
            subprocess.run(
                ["sudo", "rkhunter", "--update"],
                capture_output=True,
                timeout=60
            )
            
            # Run scan
            scan_result = subprocess.run(
                ["sudo", "rkhunter", "--check", "--skip-keypress"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            data = {
                "output": scan_result.stdout,
                "warnings": "WARNING" in scan_result.stdout
            }
            
            status = ResultStatus.SUCCESS
            if data["warnings"]:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message="Rootkit scan complete",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Rootkit scan error",
                data={},
                error=str(e)
            )
    
    def _check_updates(self) -> ModuleResult:
        """Check for security updates"""
        try:
            result = subprocess.run(
                ["apt", "list", "--upgradable"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            updates = result.stdout.strip().split("\n") if result.stdout.strip() else []
            
            # Filter security updates
            security_updates = [u for u in updates if "security" in u.lower()]
            
            data = {
                "total_updates": len(updates),
                "security_updates": len(security_updates),
                "updates": security_updates
            }
            
            status = ResultStatus.SUCCESS
            if len(security_updates) > 0:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"Found {len(security_updates)} security updates",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Security update check error",
                data={},
                error=str(e)
            )
    
    def _audit_users(self) -> ModuleResult:
        """Audit system users"""
        try:
            result = subprocess.run(
                ["cat", "/etc/passwd"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            users = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split(":")
                    users.append({
                        "username": parts[0],
                        "uid": parts[2],
                        "gid": parts[3],
                        "shell": parts[6]
                    })
            
            # Check for suspicious users
            suspicious = [u for u in users if int(u["uid"]) == 0 and u["username"] != "root"]
            
            data = {
                "total_users": len(users),
                "suspicious_users": suspicious,
                "users": users
            }
            
            status = ResultStatus.SUCCESS
            if suspicious:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"Audited {len(users)} users",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="User audit error",
                data={},
                error=str(e)
            )
    
    def _check_sudo_access(self) -> ModuleResult:
        """Check sudo access configuration"""
        try:
            result = subprocess.run(
                ["sudo", "-l"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Current user has sudo access",
                    data={"sudo_access": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Current user does not have sudo access",
                    data={}
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Sudo access check error",
                data={},
                error=str(e)
            )
    
    def _security_report(self) -> ModuleResult:
        """Generate comprehensive security report"""
        report = {}
        
        # Run all checks
        report["firewall"] = self._check_firewall().to_dict()
        report["ssh_keys"] = self._check_ssh_keys().to_dict()
        report["logins"] = self._monitor_logins().to_dict()
        report["users"] = self._audit_users().to_dict()
        report["updates"] = self._check_updates().to_dict()
        
        # Calculate overall security score
        score = 100
        issues = 0
        
        for check_name, check_result in report.items():
            if check_result["status"] == "partial":
                score -= 15
                issues += 1
            elif check_result["status"] == "failed":
                score -= 25
                issues += 1
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Security report generated - Score: {score}/100",
            data={
                "security_score": score,
                "issues_found": issues,
                "report": report
            }
        )


if __name__ == "__main__":
    module = SecurityModule()
    print("Security Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
