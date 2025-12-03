#!/usr/bin/env python3
"""
System Cleanup Module for Desktop AI Agent
Handles system optimization and cache clearing
"""

import os
import subprocess
import shutil
import logging
from typing import Dict, Any, List
from pathlib import Path
from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class SystemCleanupModule(BaseModule):
    """
    Cleanup and optimization module
    Clears caches, removes old files, optimizes system
    """
    
    def __init__(self):
        super().__init__(
            name="system_cleanup",
            description="System cleanup and optimization",
            version="1.0.0"
        )
    
    def get_supported_actions(self) -> List[str]:
        """Get supported cleanup actions"""
        return [
            "clear_package_cache",
            "clear_temp_files",
            "clear_thumbnail_cache",
            "remove_old_kernels",
            "clear_browser_cache",
            "empty_trash",
            "cleanup_logs",
            "full_cleanup",
            "get_space_usage"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute cleanup action"""
        try:
            if action == "clear_package_cache":
                return self._clear_package_cache()
            elif action == "clear_temp_files":
                return self._clear_temp_files()
            elif action == "clear_thumbnail_cache":
                return self._clear_thumbnail_cache()
            elif action == "remove_old_kernels":
                return self._remove_old_kernels()
            elif action == "clear_browser_cache":
                return self._clear_browser_cache()
            elif action == "empty_trash":
                return self._empty_trash()
            elif action == "cleanup_logs":
                return self._cleanup_logs()
            elif action == "full_cleanup":
                return self._full_cleanup()
            elif action == "get_space_usage":
                return self._get_space_usage()
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
    
    def _clear_package_cache(self) -> ModuleResult:
        """Clear package manager cache (apt/dnf/pacman)"""
        data = {"cleared": []}
        errors = []
        
        # APT (Debian/Ubuntu)
        try:
            subprocess.run(["sudo", "apt", "clean"], capture_output=True, timeout=30)
            subprocess.run(["sudo", "apt", "autoclean"], capture_output=True, timeout=30)
            data["cleared"].append("apt cache")
        except Exception as e:
            errors.append(f"APT cleanup failed: {e}")
        
        # DNF (Fedora/RHEL)
        try:
            subprocess.run(["sudo", "dnf", "clean", "all"], capture_output=True, timeout=30)
            data["cleared"].append("dnf cache")
        except Exception as e:
            errors.append(f"DNF cleanup failed: {e}")
        
        # Pacman (Arch)
        try:
            subprocess.run(["sudo", "pacman", "-Sc", "--noconfirm"], 
                         capture_output=True, timeout=30)
            data["cleared"].append("pacman cache")
        except Exception as e:
            errors.append(f"Pacman cleanup failed: {e}")
        
        status = ResultStatus.SUCCESS if data["cleared"] else ResultStatus.FAILED
        message = f"Cleared: {', '.join(data['cleared'])}"
        
        return ModuleResult(
            status=status,
            message=message,
            data=data,
            error="; ".join(errors) if errors else None
        )
    
    def _clear_temp_files(self) -> ModuleResult:
        """Clear temporary files"""
        data = {"cleared": 0, "size_freed": 0}
        errors = []
        
        temp_dirs = [
            "/tmp",
            "/var/tmp",
            os.path.expanduser("~/.cache/tmp")
        ]
        
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                try:
                    for item in os.listdir(temp_dir):
                        item_path = os.path.join(temp_dir, item)
                        if os.path.isfile(item_path):
                            size = os.path.getsize(item_path)
                            os.remove(item_path)
                            data["cleared"] += 1
                            data["size_freed"] += size
                        elif os.path.isdir(item_path):
                            size = self._get_dir_size(item_path)
                            shutil.rmtree(item_path, ignore_errors=True)
                            data["cleared"] += 1
                            data["size_freed"] += size
                except Exception as e:
                    errors.append(f"Error cleaning {temp_dir}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Cleared {data['cleared']} items, freed {self._format_size(data['size_freed'])}",
            data=data,
            error="; ".join(errors) if errors else None
        )
    
    def _clear_thumbnail_cache(self) -> ModuleResult:
        """Clear thumbnail cache"""
        data = {"cleared": False, "size_freed": 0}
        
        cache_dir = os.path.expanduser("~/.cache/thumbnails")
        if os.path.exists(cache_dir):
            try:
                size = self._get_dir_size(cache_dir)
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir)
                data["cleared"] = True
                data["size_freed"] = size
            except Exception as e:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to clear thumbnail cache",
                    data=data,
                    error=str(e)
                )
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Cleared thumbnail cache, freed {self._format_size(data['size_freed'])}",
            data=data
        )
    
    def _remove_old_kernels(self) -> ModuleResult:
        """Remove old kernel versions"""
        data = {"removed": []}
        
        try:
            # Get current kernel
            result = subprocess.run(
                ["uname", "-r"],
                capture_output=True,
                text=True,
                timeout=10
            )
            current_kernel = result.stdout.strip()
            
            # List installed kernels
            result = subprocess.run(
                ["dpkg", "-l", "|", "grep", "linux-image"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Remove old kernels (requires sudo)
            subprocess.run(
                ["sudo", "apt", "autoremove", "--purge", "-y"],
                capture_output=True,
                timeout=60
            )
            
            data["current_kernel"] = current_kernel
            data["removed"] = ["Old kernel versions removed via autoremove"]
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message="Old kernels removed",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to remove old kernels",
                data=data,
                error=str(e)
            )
    
    def _clear_browser_cache(self) -> ModuleResult:
        """Clear browser caches"""
        data = {"cleared": [], "size_freed": 0}
        
        browser_caches = {
            "Firefox": os.path.expanduser("~/.cache/mozilla/firefox"),
            "Chrome": os.path.expanduser("~/.cache/google-chrome"),
            "Chromium": os.path.expanduser("~/.cache/chromium"),
            "Brave": os.path.expanduser("~/.cache/BraveSoftware/Brave-Browser")
        }
        
        for browser, cache_path in browser_caches.items():
            if os.path.exists(cache_path):
                try:
                    size = self._get_dir_size(cache_path)
                    shutil.rmtree(cache_path)
                    os.makedirs(cache_path)
                    data["cleared"].append(browser)
                    data["size_freed"] += size
                except Exception as e:
                    logger.warning(f"Failed to clear {browser} cache: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Cleared caches for: {', '.join(data['cleared'])}",
            data=data
        )
    
    def _empty_trash(self) -> ModuleResult:
        """Empty trash/recycle bin"""
        data = {"cleared": False, "size_freed": 0}
        
        trash_dir = os.path.expanduser("~/.local/share/Trash")
        if os.path.exists(trash_dir):
            try:
                size = self._get_dir_size(trash_dir)
                shutil.rmtree(trash_dir)
                os.makedirs(trash_dir)
                data["cleared"] = True
                data["size_freed"] = size
            except Exception as e:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="Failed to empty trash",
                    data=data,
                    error=str(e)
                )
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Emptied trash, freed {self._format_size(data['size_freed'])}",
            data=data
        )
    
    def _cleanup_logs(self) -> ModuleResult:
        """Clean up old log files"""
        data = {"cleaned": 0, "size_freed": 0}
        
        log_dirs = [
            "/var/log",
            os.path.expanduser("~/.local/share/*/logs")
        ]
        
        for log_dir in log_dirs:
            if os.path.exists(log_dir):
                try:
                    for item in Path(log_dir).glob("*.log*"):
                        if item.is_file():
                            try:
                                size = item.stat().st_size
                                item.unlink()
                                data["cleaned"] += 1
                                data["size_freed"] += size
                            except Exception as e:
                                logger.warning(f"Failed to remove {item}: {e}")
                except Exception as e:
                    logger.warning(f"Error cleaning {log_dir}: {e}")
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Cleaned {data['cleaned']} log files, freed {self._format_size(data['size_freed'])}",
            data=data
        )
    
    def _full_cleanup(self) -> ModuleResult:
        """Execute full system cleanup"""
        results = {}
        total_freed = 0
        
        actions = [
            "clear_package_cache",
            "clear_temp_files",
            "clear_thumbnail_cache",
            "clear_browser_cache",
            "empty_trash",
            "cleanup_logs"
        ]
        
        for action in actions:
            result = self.execute(action, {})
            results[action] = result.to_dict()
            if "size_freed" in result.data:
                total_freed += result.data.get("size_freed", 0)
        
        return ModuleResult(
            status=ResultStatus.SUCCESS,
            message=f"Full cleanup completed, freed {self._format_size(total_freed)}",
            data={
                "actions": results,
                "total_freed": total_freed
            }
        )
    
    def _get_space_usage(self) -> ModuleResult:
        """Get disk space usage"""
        try:
            result = subprocess.run(
                ["df", "-h", "/"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            lines = result.stdout.strip().split("\n")
            if len(lines) >= 2:
                parts = lines[1].split()
                data = {
                    "total": parts[1],
                    "used": parts[2],
                    "available": parts[3],
                    "percent": parts[4]
                }
                
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message=f"Disk usage: {data['used']} / {data['total']} ({data['percent']})",
                    data=data
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get disk usage",
                data={},
                error=str(e)
            )
    
    @staticmethod
    def _get_dir_size(path: str) -> int:
        """Get directory size in bytes"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += SystemCleanupModule._get_dir_size(entry.path)
        except Exception:
            pass
        return total
    
    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format bytes to human readable size"""
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"


if __name__ == "__main__":
    module = SystemCleanupModule()
    print("System Cleanup Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
    
    # Test get_space_usage
    result = module.execute("get_space_usage", {})
    print(f"\nDisk Usage: {result.message}")
    print(f"Data: {result.data}")
