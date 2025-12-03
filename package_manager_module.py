#!/usr/bin/env python3
"""
Package Manager Module for Desktop AI Agent
Handles system package management
"""

import subprocess
import logging
from typing import Dict, Any, List
from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class PackageManagerModule(BaseModule):
    """
    Package management module
    Handles installation, updates, and removal of packages
    """
    
    def __init__(self):
        super().__init__(
            name="package_manager",
            description="System package management",
            version="1.0.0"
        )
        self.package_manager = self._detect_package_manager()
    
    def get_supported_actions(self) -> List[str]:
        """Get supported package management actions"""
        return [
            "install_package",
            "remove_package",
            "update_system",
            "upgrade_packages",
            "search_package",
            "list_installed",
            "check_updates",
            "fix_broken",
            "remove_unused",
            "get_package_info"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute package management action"""
        try:
            if action == "install_package":
                return self._install_package(parameters)
            elif action == "remove_package":
                return self._remove_package(parameters)
            elif action == "update_system":
                return self._update_system()
            elif action == "upgrade_packages":
                return self._upgrade_packages()
            elif action == "search_package":
                return self._search_package(parameters)
            elif action == "list_installed":
                return self._list_installed(parameters)
            elif action == "check_updates":
                return self._check_updates()
            elif action == "fix_broken":
                return self._fix_broken()
            elif action == "remove_unused":
                return self._remove_unused()
            elif action == "get_package_info":
                return self._get_package_info(parameters)
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
    
    def _detect_package_manager(self) -> str:
        """Detect which package manager is available"""
        managers = {
            "apt": ["apt", "--version"],
            "dnf": ["dnf", "--version"],
            "pacman": ["pacman", "--version"],
            "zypper": ["zypper", "--version"]
        }
        
        for manager, cmd in managers.items():
            try:
                subprocess.run(cmd, capture_output=True, timeout=5)
                logger.info(f"Detected package manager: {manager}")
                return manager
            except Exception:
                pass
        
        logger.warning("No package manager detected")
        return "apt"  # Default to apt
    
    def _install_package(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Install a package"""
        package = parameters.get("package")
        if not package:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="package parameter required",
                data={}
            )
        
        try:
            if self.package_manager == "apt":
                cmd = ["sudo", "apt", "install", "-y", package]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "install", "-y", package]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-S", "--noconfirm", package]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Successfully installed {package}",
                    data={"package": package}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Failed to install {package}",
                    data={"package": package},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Installation error",
                data={},
                error=str(e)
            )
    
    def _remove_package(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Remove a package"""
        package = parameters.get("package")
        if not package:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="package parameter required",
                data={}
            )
        
        try:
            if self.package_manager == "apt":
                cmd = ["sudo", "apt", "remove", "-y", package]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "remove", "-y", package]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-R", "--noconfirm", package]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Successfully removed {package}",
                    data={"package": package}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Failed to remove {package}",
                    data={"package": package},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Removal error",
                data={},
                error=str(e)
            )
    
    def _update_system(self) -> ModuleResult:
        """Update package lists"""
        try:
            if self.package_manager == "apt":
                cmd = ["sudo", "apt", "update"]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "check-update"]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-Sy"]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0 or result.returncode == 1:  # 1 is normal for dnf
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Package lists updated",
                    data={"output": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to update package lists",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Update error",
                data={},
                error=str(e)
            )
    
    def _upgrade_packages(self) -> ModuleResult:
        """Upgrade all packages"""
        try:
            if self.package_manager == "apt":
                cmd = ["sudo", "apt", "upgrade", "-y"]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "upgrade", "-y"]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-Syu", "--noconfirm"]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Packages upgraded successfully",
                    data={"output": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to upgrade packages",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Upgrade error",
                data={},
                error=str(e)
            )
    
    def _search_package(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Search for a package"""
        query = parameters.get("query")
        if not query:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="query parameter required",
                data={}
            )
        
        try:
            if self.package_manager == "apt":
                cmd = ["apt", "search", query]
            elif self.package_manager == "dnf":
                cmd = ["dnf", "search", query]
            elif self.package_manager == "pacman":
                cmd = ["pacman", "-Ss", query]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split("\n"):
                    if line.strip():
                        packages.append(line.strip())
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Found {len(packages)} packages",
                    data={"packages": packages}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Search failed",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Search error",
                data={},
                error=str(e)
            )
    
    def _list_installed(self, parameters: Dict[str, Any]) -> ModuleResult:
        """List installed packages"""
        limit = parameters.get("limit", 50)
        
        try:
            if self.package_manager == "apt":
                cmd = ["dpkg", "-l"]
            elif self.package_manager == "dnf":
                cmd = ["dnf", "list", "installed"]
            elif self.package_manager == "pacman":
                cmd = ["pacman", "-Q"]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                packages = []
                for line in result.stdout.split("\n"):
                    if line.strip():
                        packages.append(line.strip())
                
                # Limit results
                packages = packages[:limit]
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Listed {len(packages)} packages",
                    data={"packages": packages}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to list packages",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="List error",
                data={},
                error=str(e)
            )
    
    def _check_updates(self) -> ModuleResult:
        """Check for available updates"""
        try:
            if self.package_manager == "apt":
                result = subprocess.run(
                    ["apt", "list", "--upgradable"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif self.package_manager == "dnf":
                result = subprocess.run(
                    ["dnf", "check-update"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            elif self.package_manager == "pacman":
                result = subprocess.run(
                    ["pacman", "-Qu"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            updates = []
            for line in result.stdout.split("\n"):
                if line.strip():
                    updates.append(line.strip())
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"Found {len(updates)} updates available",
                data={"updates": updates}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Check updates error",
                data={},
                error=str(e)
            )
    
    def _fix_broken(self) -> ModuleResult:
        """Fix broken packages"""
        try:
            if self.package_manager == "apt":
                cmd = ["sudo", "apt", "--fix-broken", "install", "-y"]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "install", "-y", "--allowerasing"]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-Syu", "--noconfirm"]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Fixed broken packages",
                    data={"output": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to fix broken packages",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Fix broken error",
                data={},
                error=str(e)
            )
    
    def _remove_unused(self) -> ModuleResult:
        """Remove unused packages"""
        try:
            if self.package_manager == "apt":
                cmd = ["sudo", "apt", "autoremove", "-y"]
            elif self.package_manager == "dnf":
                cmd = ["sudo", "dnf", "autoremove", "-y"]
            elif self.package_manager == "pacman":
                cmd = ["sudo", "pacman", "-Rns", "$(pacman -Qdtq)", "--noconfirm"]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Removed unused packages",
                    data={"output": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to remove unused packages",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Remove unused error",
                data={},
                error=str(e)
            )
    
    def _get_package_info(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Get information about a package"""
        package = parameters.get("package")
        if not package:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="package parameter required",
                data={}
            )
        
        try:
            if self.package_manager == "apt":
                cmd = ["apt", "show", package]
            elif self.package_manager == "dnf":
                cmd = ["dnf", "info", package]
            elif self.package_manager == "pacman":
                cmd = ["pacman", "-Si", package]
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Unsupported package manager: {self.package_manager}",
                    data={}
                )
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Package info for {package}",
                    data={"info": result.stdout}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message=f"Package {package} not found",
                    data={},
                    error=result.stderr
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Package info error",
                data={},
                error=str(e)
            )


if __name__ == "__main__":
    module = PackageManagerModule()
    print("Package Manager Module Test")
    print(f"Detected package manager: {module.package_manager}")
    print(f"Supported actions: {module.get_supported_actions()}")
