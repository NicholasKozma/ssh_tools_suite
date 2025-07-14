#!/usr/bin/env python3
"""
SSH Tunnel Manager - Configuration Management
"""

import json
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtCore import QSettings

from .models import TunnelConfig
from .constants import ORGANIZATION_NAME, CONFIG_NAME


class ConfigurationManager:
    """Manages tunnel configurations and application settings."""
    
    def __init__(self):
        self.settings = QSettings(ORGANIZATION_NAME, CONFIG_NAME)
        self.configs: Dict[str, TunnelConfig] = {}
    
    def load_configurations(self) -> Dict[str, TunnelConfig]:
        """Load configurations from settings."""
        configs_data = self.settings.value("tunnels", {})
        
        if isinstance(configs_data, dict):
            for name, config_dict in configs_data.items():
                try:
                    config = TunnelConfig.from_dict(config_dict)
                    self.configs[name] = config
                except Exception as e:
                    print(f"Warning: Failed to load tunnel config '{name}': {e}")
        
        return self.configs
    
    def save_configurations(self):
        """Save configurations to settings."""
        configs_data = {name: config.to_dict() for name, config in self.configs.items()}
        self.settings.setValue("tunnels", configs_data)
        self.settings.sync()
    
    def add_configuration(self, config: TunnelConfig) -> tuple[bool, str]:
        """Add a new tunnel configuration."""
        # Validate configuration
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, error_msg
        
        # Check for duplicate names
        if config.name in self.configs:
            return False, f"Tunnel name '{config.name}' already exists"
        
        self.configs[config.name] = config
        self.save_configurations()
        return True, ""
    
    def update_configuration(self, old_name: str, config: TunnelConfig) -> tuple[bool, str]:
        """Update an existing tunnel configuration."""
        # Validate configuration
        is_valid, error_msg = config.validate()
        if not is_valid:
            return False, error_msg
        
        # Check if name changed and if new name conflicts
        if config.name != old_name and config.name in self.configs:
            return False, f"Tunnel name '{config.name}' already exists"
        
        # Remove old config if name changed
        if config.name != old_name and old_name in self.configs:
            del self.configs[old_name]
        
        self.configs[config.name] = config
        self.save_configurations()
        return True, ""
    
    def delete_configuration(self, name: str) -> bool:
        """Delete a tunnel configuration."""
        if name in self.configs:
            del self.configs[name]
            self.save_configurations()
            return True
        return False
    
    def get_configuration(self, name: str) -> Optional[TunnelConfig]:
        """Get a specific tunnel configuration."""
        return self.configs.get(name)
    
    def get_all_configurations(self) -> Dict[str, TunnelConfig]:
        """Get all tunnel configurations."""
        return self.configs.copy()
    
    def get_auto_start_configurations(self) -> Dict[str, TunnelConfig]:
        """Get configurations marked for auto-start."""
        return {name: config for name, config in self.configs.items() if config.auto_start}
    
    def export_configurations(self, file_path: Path) -> tuple[bool, str]:
        """Export configurations to JSON file."""
        try:
            data = {
                "version": "1.0",
                "tunnels": {name: config.to_dict() for name, config in self.configs.items()}
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True, f"Exported {len(self.configs)} configurations to {file_path}"
        
        except Exception as e:
            return False, f"Export failed: {str(e)}"
    
    def import_configurations(self, file_path: Path, overwrite: bool = False) -> tuple[bool, str]:
        """Import configurations from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or "tunnels" not in data:
                return False, "Invalid configuration file format"
            
            imported_count = 0
            skipped_count = 0
            
            for name, config_dict in data["tunnels"].items():
                try:
                    config = TunnelConfig.from_dict(config_dict)
                    
                    # Validate configuration
                    is_valid, error_msg = config.validate()
                    if not is_valid:
                        print(f"Warning: Skipping invalid config '{name}': {error_msg}")
                        skipped_count += 1
                        continue
                    
                    # Check for duplicates
                    if name in self.configs and not overwrite:
                        print(f"Warning: Skipping duplicate config '{name}' (use overwrite=True to replace)")
                        skipped_count += 1
                        continue
                    
                    self.configs[name] = config
                    imported_count += 1
                
                except Exception as e:
                    print(f"Warning: Failed to import config '{name}': {e}")
                    skipped_count += 1
            
            if imported_count > 0:
                self.save_configurations()
            
            message = f"Imported {imported_count} configurations"
            if skipped_count > 0:
                message += f", skipped {skipped_count}"
            
            return True, message
        
        except Exception as e:
            return False, f"Import failed: {str(e)}"
    
    def get_default_ssh_key_path(self) -> Optional[str]:
        """Get the default SSH key path from settings."""
        return self.settings.value("ssh_key/default_path", "")
    
    def set_default_ssh_key_path(self, key_path: str):
        """Set the default SSH key path in settings."""
        self.settings.setValue("ssh_key/default_path", key_path)
        self.settings.sync()
    
    def get_ssh_key_settings(self) -> dict:
        """Get all SSH key related settings."""
        return {
            'default_path': self.get_default_ssh_key_path(),
            'auto_use_default': self.settings.value("ssh_key/auto_use_default", True, type=bool),
            'remember_last_used': self.settings.value("ssh_key/remember_last_used", True, type=bool)
        }
    
    def update_ssh_key_settings(self, settings: dict):
        """Update SSH key settings."""
        for key, value in settings.items():
            self.settings.setValue(f"ssh_key/{key}", value)
        self.settings.sync()
    
    def get_default_ssh_username(self) -> str:
        """Get the default SSH username from settings."""
        return self.settings.value("ssh/default_username", "")
    
    def set_default_ssh_username(self, username: str):
        """Set the default SSH username in settings."""
        self.settings.setValue("ssh/default_username", username)
        self.settings.sync()

    def backup_configurations(self, backup_path: Optional[Path] = None) -> tuple[bool, str]:
        """Create a backup of current configurations."""
        if backup_path is None:
            backup_path = Path.home() / "ssh_tunnel_manager_backup.json"
        
        return self.export_configurations(backup_path)
