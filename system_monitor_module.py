#!/usr/bin/env python3
"""
System Monitor Module for Desktop AI Agent
Monitors system health, resources, and performance
"""

import os
import subprocess
import psutil
import logging
from typing import Dict, Any, List
from module_framework import BaseModule, ModuleResult, ResultStatus

logger = logging.getLogger(__name__)


class SystemMonitorModule(BaseModule):
    """
    System monitoring module
    Tracks CPU, RAM, disk, temperature, processes
    """
    
    def __init__(self):
        super().__init__(
            name="system_monitor",
            description="System health and resource monitoring",
            version="1.0.0"
        )
    
    def get_supported_actions(self) -> List[str]:
        """Get supported monitoring actions"""
        return [
            "get_cpu_info",
            "get_memory_info",
            "get_disk_info",
            "get_temperature",
            "get_processes",
            "get_system_health",
            "get_battery_status",
            "get_network_info",
            "monitor_process"
        ]
    
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """Execute monitoring action"""
        try:
            if action == "get_cpu_info":
                return self._get_cpu_info()
            elif action == "get_memory_info":
                return self._get_memory_info()
            elif action == "get_disk_info":
                return self._get_disk_info()
            elif action == "get_temperature":
                return self._get_temperature()
            elif action == "get_processes":
                return self._get_processes(parameters)
            elif action == "get_system_health":
                return self._get_system_health()
            elif action == "get_battery_status":
                return self._get_battery_status()
            elif action == "get_network_info":
                return self._get_network_info()
            elif action == "monitor_process":
                return self._monitor_process(parameters)
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
    
    def _get_cpu_info(self) -> ModuleResult:
        """Get CPU information and usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count(logical=False)
            cpu_count_logical = psutil.cpu_count(logical=True)
            
            # Get CPU frequency
            freq = psutil.cpu_freq()
            
            # Get per-CPU usage
            per_cpu = psutil.cpu_percent(interval=1, percpu=True)
            
            data = {
                "usage_percent": cpu_percent,
                "physical_cores": cpu_count,
                "logical_cores": cpu_count_logical,
                "frequency_current": freq.current if freq else 0,
                "frequency_max": freq.max if freq else 0,
                "per_cpu_usage": per_cpu
            }
            
            status = ResultStatus.SUCCESS
            if cpu_percent > 80:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"CPU usage: {cpu_percent}%",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get CPU info",
                data={},
                error=str(e)
            )
    
    def _get_memory_info(self) -> ModuleResult:
        """Get memory information"""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            data = {
                "total": memory.total,
                "available": memory.available,
                "used": memory.used,
                "free": memory.free,
                "percent": memory.percent,
                "swap_total": swap.total,
                "swap_used": swap.used,
                "swap_free": swap.free,
                "swap_percent": swap.percent
            }
            
            status = ResultStatus.SUCCESS
            if memory.percent > 80:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"Memory usage: {memory.percent}%",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get memory info",
                data={},
                error=str(e)
            )
    
    def _get_disk_info(self) -> ModuleResult:
        """Get disk information"""
        try:
            disks = {}
            
            # Get info for root partition
            disk = psutil.disk_usage("/")
            disks["/"] = {
                "total": disk.total,
                "used": disk.used,
                "free": disk.free,
                "percent": disk.percent
            }
            
            # Get info for home partition if different
            home_disk = psutil.disk_usage(os.path.expanduser("~"))
            if home_disk.total != disk.total:
                disks["home"] = {
                    "total": home_disk.total,
                    "used": home_disk.used,
                    "free": home_disk.free,
                    "percent": home_disk.percent
                }
            
            # Get I/O counters
            io_counters = psutil.disk_io_counters()
            
            data = {
                "partitions": disks,
                "io_read_count": io_counters.read_count if io_counters else 0,
                "io_write_count": io_counters.write_count if io_counters else 0,
                "io_read_bytes": io_counters.read_bytes if io_counters else 0,
                "io_write_bytes": io_counters.write_bytes if io_counters else 0
            }
            
            status = ResultStatus.SUCCESS
            for partition, info in disks.items():
                if info["percent"] > 80:
                    status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"Disk usage: {disk.percent}%",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get disk info",
                data={},
                error=str(e)
            )
    
    def _get_temperature(self) -> ModuleResult:
        """Get system temperature"""
        try:
            temps = {}
            
            # Try to get temperatures using psutil
            if hasattr(psutil, "sensors_temperatures"):
                temps_dict = psutil.sensors_temperatures()
                for name, entries in temps_dict.items():
                    temps[name] = [
                        {
                            "label": entry.label,
                            "current": entry.current,
                            "high": entry.high,
                            "critical": entry.critical
                        }
                        for entry in entries
                    ]
            
            # Fallback: try to read from /sys/class/thermal
            if not temps:
                thermal_dir = "/sys/class/thermal"
                if os.path.exists(thermal_dir):
                    for zone in os.listdir(thermal_dir):
                        temp_file = os.path.join(thermal_dir, zone, "temp")
                        if os.path.exists(temp_file):
                            try:
                                with open(temp_file) as f:
                                    temp_c = int(f.read().strip()) / 1000
                                    temps[zone] = temp_c
                            except Exception:
                                pass
            
            if temps:
                return ModuleResult(
                    status=ResultStatus.SUCCESS,
                    message="Temperature data retrieved",
                    data={"temperatures": temps}
                )
            else:
                return ModuleResult(
                    status=ResultStatus.UNKNOWN,
                    message="Temperature sensors not available",
                    data={}
                )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get temperature",
                data={},
                error=str(e)
            )
    
    def _get_processes(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Get running processes"""
        try:
            limit = parameters.get("limit", 10)
            sort_by = parameters.get("sort_by", "memory")  # cpu or memory
            
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
                try:
                    processes.append({
                        "pid": proc.info["pid"],
                        "name": proc.info["name"],
                        "cpu_percent": proc.info["cpu_percent"],
                        "memory_percent": proc.info["memory_percent"]
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Sort and limit
            if sort_by == "cpu":
                processes.sort(key=lambda x: x["cpu_percent"], reverse=True)
            else:
                processes.sort(key=lambda x: x["memory_percent"], reverse=True)
            
            processes = processes[:limit]
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message=f"Retrieved top {limit} processes",
                data={"processes": processes}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get processes",
                data={},
                error=str(e)
            )
    
    def _get_system_health(self) -> ModuleResult:
        """Get overall system health"""
        try:
            cpu_result = self._get_cpu_info()
            memory_result = self._get_memory_info()
            disk_result = self._get_disk_info()
            
            health_score = 100
            warnings = []
            
            # Check CPU
            if cpu_result.data.get("usage_percent", 0) > 80:
                health_score -= 20
                warnings.append("High CPU usage")
            
            # Check Memory
            if memory_result.data.get("percent", 0) > 80:
                health_score -= 20
                warnings.append("High memory usage")
            
            # Check Disk
            for partition, info in disk_result.data.get("partitions", {}).items():
                if info["percent"] > 80:
                    health_score -= 20
                    warnings.append(f"Disk {partition} almost full")
            
            data = {
                "health_score": max(0, health_score),
                "warnings": warnings,
                "cpu": cpu_result.data,
                "memory": memory_result.data,
                "disk": disk_result.data
            }
            
            status = ResultStatus.SUCCESS
            if health_score < 50:
                status = ResultStatus.PARTIAL
            
            return ModuleResult(
                status=status,
                message=f"System health: {health_score}/100",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get system health",
                data={},
                error=str(e)
            )
    
    def _get_battery_status(self) -> ModuleResult:
        """Get battery status (for laptops)"""
        try:
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    data = {
                        "percent": battery.percent,
                        "secsleft": battery.secsleft,
                        "power_plugged": battery.power_plugged
                    }
                    
                    status_str = "charging" if battery.power_plugged else "discharging"
                    return ModuleResult(
                        status=ResultStatus.SUCCESS,
                        message=f"Battery: {battery.percent}% ({status_str})",
                        data=data
                    )
            
            return ModuleResult(
                status=ResultStatus.UNKNOWN,
                message="Battery not available",
                data={}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get battery status",
                data={},
                error=str(e)
            )
    
    def _get_network_info(self) -> ModuleResult:
        """Get network information"""
        try:
            net_if_addrs = psutil.net_if_addrs()
            net_io_counters = psutil.net_io_counters()
            
            interfaces = {}
            for interface, addrs in net_if_addrs.items():
                interfaces[interface] = [
                    {
                        "family": str(addr.family),
                        "address": addr.address,
                        "netmask": addr.netmask,
                        "broadcast": addr.broadcast
                    }
                    for addr in addrs
                ]
            
            data = {
                "interfaces": interfaces,
                "bytes_sent": net_io_counters.bytes_sent,
                "bytes_recv": net_io_counters.bytes_recv,
                "packets_sent": net_io_counters.packets_sent,
                "packets_recv": net_io_counters.packets_recv
            }
            
            return ModuleResult(
                status=ResultStatus.SUCCESS,
                message="Network info retrieved",
                data=data
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to get network info",
                data={},
                error=str(e)
            )
    
    def _monitor_process(self, parameters: Dict[str, Any]) -> ModuleResult:
        """Monitor a specific process"""
        try:
            process_name = parameters.get("process_name")
            if not process_name:
                return ModuleResult(
                    status=ResultStatus.FAILED,
                    message="process_name parameter required",
                    data={}
                )
            
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "status"]):
                try:
                    if process_name.lower() in proc.info["name"].lower():
                        data = {
                            "pid": proc.info["pid"],
                            "name": proc.info["name"],
                            "cpu_percent": proc.info["cpu_percent"],
                            "memory_percent": proc.info["memory_percent"],
                            "status": proc.info["status"]
                        }
                        
                        return ModuleResult(
                            status=ResultStatus.SUCCESS,
                            message=f"Process found: {proc.info['name']}",
                            data=data
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Process '{process_name}' not found",
                data={}
            )
        except Exception as e:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message="Failed to monitor process",
                data={},
                error=str(e)
            )


if __name__ == "__main__":
    module = SystemMonitorModule()
    print("System Monitor Module Test")
    print(f"Supported actions: {module.get_supported_actions()}")
    
    # Test system health
    result = module.execute("get_system_health", {})
    print(f"\nSystem Health: {result.message}")
    print(f"Health Score: {result.data.get('health_score')}")
