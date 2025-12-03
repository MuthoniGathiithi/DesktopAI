#!/usr/bin/env python3
"""
Configuration Manager for Linux Desktop AI Agent
Handles configuration storage and management
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Agent configuration"""
    # Llama settings
    llama_model: str = "llama3.1:8b"
    llama_host: str = "localhost"
    llama_port: int = 11434
    
    # Module settings
    enabled_modules: list = None
    
    # Notification settings
    notifications_enabled: bool = True
    notification_type: str = "desktop"  # desktop, email, both
    email_address: Optional[str] = None
    
    # Automation settings
    auto_cleanup: bool = False
    auto_cleanup_interval: int = 86400  # 24 hours
    auto_update: bool = False
    auto_update_interval: int = 604800  # 7 days
    
    # Alert thresholds
    cpu_threshold: float = 80.0
    memory_threshold: float = 80.0
    disk_threshold: float = 85.0
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "/tmp/linux_desktop_agent.log"
    
    def __post_init__(self):
        if self.enabled_modules is None:
            self.enabled_modules = [
                "system_cleanup",
                "system_monitor",
                "network",
                "file_manager",
                "package_manager",
                "security",
                "developer_tools"
            ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """Create from dictionary"""
        return cls(**data)


class ConfigManager:
    """Manages agent configuration"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        Initialize configuration manager
        
        Args:
            config_dir: Configuration directory (default: ~/.config/linux-desktop-agent)
        """
        if config_dir is None:
            config_dir = Path.home() / ".config" / "linux-desktop-agent"
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.backup_dir = self.config_dir / "backups"
        self.backup_dir.mkdir(exist_ok=True)
        
        self.config = self._load_config()
    
    def _load_config(self) -> AgentConfig:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded configuration from {self.config_file}")
                return AgentConfig.from_dict(data)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return AgentConfig()
        else:
            logger.info("Creating default configuration")
            return AgentConfig()
    
    def save_config(self, config: Optional[AgentConfig] = None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            # Create backup
            if self.config_file.exists():
                import shutil
                from datetime import datetime
                backup_file = self.backup_dir / f"config_{datetime.now().isoformat()}.json"
                shutil.copy(self.config_file, backup_file)
            
            # Save new config
            with open(self.config_file, 'w') as f:
                json.dump(config.to_dict(), f, indent=2)
            
            logger.info(f"Saved configuration to {self.config_file}")
            self.config = config
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
        else:
            logger.warning(f"Unknown configuration key: {key}")
    
    def update(self, updates: Dict[str, Any]):
        """Update multiple configuration values"""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = AgentConfig()
        self.save_config()
        logger.info("Configuration reset to defaults")
    
    def export_config(self, filepath: Path):
        """Export configuration to file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            logger.info(f"Exported configuration to {filepath}")
        except Exception as e:
            logger.error(f"Error exporting config: {e}")
    
    def import_config(self, filepath: Path):
        """Import configuration from file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            self.config = AgentConfig.from_dict(data)
            self.save_config()
            logger.info(f"Imported configuration from {filepath}")
        except Exception as e:
            logger.error(f"Error importing config: {e}")
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.to_dict()


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get global configuration manager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value"""
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any):
    """Set configuration value"""
    get_config_manager().set(key, value)
