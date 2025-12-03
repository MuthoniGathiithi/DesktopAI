#!/usr/bin/env python3
"""
Module Framework for Desktop AI Agent
Provides base classes and registry system for pluggable modules
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

logger = logging.getLogger(__name__)


class ResultStatus(Enum):
    """Result status codes"""
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"
    UNKNOWN = "unknown"


@dataclass
class ModuleResult:
    """Result from module execution"""
    status: ResultStatus
    message: str
    data: Dict[str, Any]
    error: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary"""
        return {
            "status": self.status.value,
            "message": self.message,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "timestamp": self.timestamp.isoformat()
        }


class BaseModule(ABC):
    """
    Base class for all desktop AI agent modules
    All modules must inherit from this class
    """
    
    def __init__(self, name: str, description: str, version: str = "1.0.0"):
        """
        Initialize base module
        
        Args:
            name: Module name
            description: Module description
            version: Module version
        """
        self.name = name
        self.description = description
        self.version = version
        self.enabled = True
        self.logger = logging.getLogger(name)
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.last_execution = None
        self.error_count = 0
    
    @abstractmethod
    def execute(self, action: str, parameters: Dict[str, Any]) -> ModuleResult:
        """
        Execute module action
        
        Args:
            action: Action to perform
            parameters: Action parameters
            
        Returns:
            ModuleResult with execution status and data
        """
        pass
    
    @abstractmethod
    def get_supported_actions(self) -> List[str]:
        """
        Get list of supported actions
        
        Returns:
            List of action names
        """
        pass
    
    def validate_parameters(self, parameters: Dict[str, Any], required: List[str]) -> Tuple[bool, str]:
        """
        Validate required parameters
        
        Args:
            parameters: Parameters to validate
            required: List of required parameter names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for param in required:
            if param not in parameters:
                return False, f"Missing required parameter: {param}"
        return True, ""
    
    def log_execution(self, action: str, status: ResultStatus, execution_time: float):
        """Log module execution"""
        self.execution_count += 1
        self.total_execution_time += execution_time
        self.last_execution = datetime.now()
        
        if status == ResultStatus.FAILED:
            self.error_count += 1
        
        self.logger.info(
            f"Action '{action}' completed with status {status.value} "
            f"in {execution_time:.2f}s"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get module statistics"""
        avg_time = (self.total_execution_time / self.execution_count 
                   if self.execution_count > 0 else 0)
        
        return {
            "name": self.name,
            "version": self.version,
            "enabled": self.enabled,
            "execution_count": self.execution_count,
            "error_count": self.error_count,
            "total_execution_time": self.total_execution_time,
            "average_execution_time": avg_time,
            "last_execution": self.last_execution.isoformat() if self.last_execution else None
        }
    
    def info(self) -> Dict[str, Any]:
        """Get module information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "supported_actions": self.get_supported_actions(),
            "enabled": self.enabled
        }


class ModuleRegistry:
    """
    Registry for managing all modules
    Handles module registration, lookup, and execution
    """
    
    def __init__(self):
        """Initialize module registry"""
        self.modules: Dict[str, BaseModule] = {}
        self.logger = logging.getLogger("ModuleRegistry")
    
    def register(self, module: BaseModule) -> bool:
        """
        Register a module
        
        Args:
            module: Module instance to register
            
        Returns:
            True if successful, False if module already exists
        """
        if module.name in self.modules:
            self.logger.warning(f"Module '{module.name}' already registered")
            return False
        
        self.modules[module.name] = module
        self.logger.info(f"Registered module: {module.name}")
        return True
    
    def unregister(self, module_name: str) -> bool:
        """
        Unregister a module
        
        Args:
            module_name: Name of module to unregister
            
        Returns:
            True if successful
        """
        if module_name in self.modules:
            del self.modules[module_name]
            self.logger.info(f"Unregistered module: {module_name}")
            return True
        return False
    
    def get_module(self, module_name: str) -> Optional[BaseModule]:
        """
        Get module by name
        
        Args:
            module_name: Name of module
            
        Returns:
            Module instance or None
        """
        return self.modules.get(module_name)
    
    def get_all_modules(self) -> Dict[str, BaseModule]:
        """Get all registered modules"""
        return self.modules.copy()
    
    def execute(self, module_name: str, action: str, 
                parameters: Dict[str, Any]) -> ModuleResult:
        """
        Execute module action
        
        Args:
            module_name: Name of module
            action: Action to perform
            parameters: Action parameters
            
        Returns:
            ModuleResult
        """
        module = self.get_module(module_name)
        
        if not module:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Module '{module_name}' not found",
                data={},
                error=f"Unknown module: {module_name}"
            )
        
        if not module.enabled:
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Module '{module_name}' is disabled",
                data={},
                error="Module disabled"
            )
        
        if action not in module.get_supported_actions():
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Action '{action}' not supported by module '{module_name}'",
                data={},
                error=f"Unsupported action: {action}"
            )
        
        try:
            import time
            start_time = time.time()
            result = module.execute(action, parameters)
            execution_time = time.time() - start_time
            
            module.log_execution(action, result.status, execution_time)
            result.execution_time = execution_time
            
            return result
        except Exception as e:
            self.logger.error(f"Error executing {module_name}.{action}: {e}")
            return ModuleResult(
                status=ResultStatus.FAILED,
                message=f"Error executing action: {str(e)}",
                data={},
                error=str(e)
            )
    
    def get_module_by_category(self, category: str) -> Optional[BaseModule]:
        """
        Get module for a command category
        
        Args:
            category: Command category
            
        Returns:
            Module instance or None
        """
        category_map = {
            "system_control": "system_monitor",
            "file_management": "file_manager",
            "package_management": "package_manager",
            "security": "security",
            "network": "network",
            "monitoring": "system_monitor",
            "developer": "developer_tools",
            "automation": "automation",
            "cleanup": "system_cleanup"
        }
        
        module_name = category_map.get(category)
        return self.get_module(module_name) if module_name else None
    
    def list_modules(self) -> List[Dict[str, Any]]:
        """List all registered modules with info"""
        return [module.info() for module in self.modules.values()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all modules"""
        return {
            module_name: module.get_stats()
            for module_name, module in self.modules.items()
        }
    
    def enable_module(self, module_name: str) -> bool:
        """Enable a module"""
        module = self.get_module(module_name)
        if module:
            module.enabled = True
            self.logger.info(f"Enabled module: {module_name}")
            return True
        return False
    
    def disable_module(self, module_name: str) -> bool:
        """Disable a module"""
        module = self.get_module(module_name)
        if module:
            module.enabled = False
            self.logger.info(f"Disabled module: {module_name}")
            return True
        return False


# Global registry instance
_registry = ModuleRegistry()


def get_registry() -> ModuleRegistry:
    """Get global module registry"""
    return _registry


def register_module(module: BaseModule) -> bool:
    """Register module in global registry"""
    return _registry.register(module)


def execute_action(module_name: str, action: str, 
                   parameters: Dict[str, Any]) -> ModuleResult:
    """Execute action in global registry"""
    return _registry.execute(module_name, action, parameters)
