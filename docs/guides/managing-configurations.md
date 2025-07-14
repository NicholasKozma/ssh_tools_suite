# Configuration Management

Guide for managing SSH tunnel configurations in the SSH Tools Suite.

## Overview

Configuration management is central to efficiently using the SSH Tunnel Manager. This guide covers creating, organizing, sharing, and maintaining tunnel configurations.

## Configuration Structure

### Tunnel Configuration Format

```json
{
  "name": "production-database",
  "description": "Production MySQL database tunnel",
  "ssh_host": "jump.company.com",
  "ssh_port": 22,
  "ssh_username": "tunnel_user",
  "ssh_key_path": "~/.ssh/id_rsa_work",
  "ssh_key_passphrase": null,
  "local_port": 3306,
  "remote_host": "db.internal.company.com",
  "remote_port": 3306,
  "auto_start": false,
  "keep_alive": true,
  "compression": true,
  "tags": ["production", "database", "mysql"]
}
```

### Application Settings

```json
{
  "general": {
    "minimize_to_tray": true,
    "start_minimized": false,
    "check_for_updates": true,
    "theme": "system"
  },
  "logging": {
    "level": "INFO",
    "max_file_size": "10MB",
    "backup_count": 5,
    "enable_console": false
  },
  "security": {
    "encrypt_passwords": true,
    "lock_after_idle": 30,
    "require_confirmation": true
  },
  "network": {
    "connection_timeout": 30,
    "retry_attempts": 3,
    "keep_alive_interval": 60
  }
}
```

## Creating Configurations

### Using the GUI

1. **Open SSH Tunnel Manager**
2. **Click "Add Tunnel"**
3. **Fill in connection details**:
   - **Name**: Descriptive identifier
   - **SSH Host**: Jump server address
   - **SSH Credentials**: Username and key/password
   - **Tunnel Details**: Local and remote ports

4. **Configure advanced options**:
   - **Auto-start**: Start tunnel with application
   - **Keep-alive**: Maintain persistent connection
   - **Compression**: Enable SSH compression

5. **Save configuration**

### Programmatic Creation

```python
from ssh_tunnel_manager.core.models import TunnelConfig
from ssh_tunnel_manager.core.config_manager import ConfigManager

# Create configuration
config = TunnelConfig(
    name="api-server",
    description="Development API server tunnel",
    ssh_host="dev.company.com",
    ssh_username="developer",
    ssh_key_path="~/.ssh/id_ed25519_dev",
    local_port=8080,
    remote_host="api.internal",
    remote_port=80,
    tags=["development", "api"]
)

# Save configuration
config_manager = ConfigManager()
config_manager.save_tunnel_config(config)
```

### Batch Configuration Creation

```python
import json
from pathlib import Path

# Load from JSON file
def load_configurations(file_path: str):
    with open(file_path, 'r') as f:
        configs_data = json.load(f)
    
    for config_data in configs_data:
        config = TunnelConfig(**config_data)
        config_manager.save_tunnel_config(config)

# Example configuration file
configs = [
    {
        "name": "web-server",
        "ssh_host": "server1.com",
        "ssh_username": "user",
        "local_port": 8080,
        "remote_host": "localhost",
        "remote_port": 80
    },
    {
        "name": "database",
        "ssh_host": "server1.com", 
        "ssh_username": "user",
        "local_port": 3306,
        "remote_host": "db.internal",
        "remote_port": 3306
    }
]

with open('tunnels.json', 'w') as f:
    json.dump(configs, f, indent=2)
```

## Configuration Organization

### Using Tags

Organize configurations with tags:

```python
# Tag examples
config.tags = [
    "production",    # Environment
    "database",      # Service type
    "mysql",         # Technology
    "critical"       # Priority
]

# Filter by tags
production_configs = config_manager.get_configs_by_tag("production")
database_configs = config_manager.get_configs_by_tag("database")
```

### Grouping Strategies

1. **By Environment**:
   - `development`
   - `staging`
   - `production`

2. **By Service Type**:
   - `database`
   - `web-server`
   - `api`
   - `monitoring`

3. **By Project**:
   - `project-alpha`
   - `project-beta`
   - `internal-tools`

4. **By Priority**:
   - `critical`
   - `important`
   - `optional`

### Naming Conventions

Use consistent naming patterns:

```
{environment}-{service}-{purpose}

Examples:
- prod-mysql-orders
- dev-api-users
- staging-redis-cache
- test-web-frontend
```

## Configuration Profiles

### Environment-Specific Profiles

```python
class ConfigProfile:
    def __init__(self, name: str, base_config: dict):
        self.name = name
        self.base_config = base_config
    
    def create_tunnel_config(self, overrides: dict = None) -> TunnelConfig:
        config = self.base_config.copy()
        if overrides:
            config.update(overrides)
        return TunnelConfig(**config)

# Define profiles
profiles = {
    "development": ConfigProfile("development", {
        "ssh_host": "dev.company.com",
        "ssh_username": "developer",
        "ssh_key_path": "~/.ssh/id_dev"
    }),
    "production": ConfigProfile("production", {
        "ssh_host": "prod.company.com", 
        "ssh_username": "prod_user",
        "ssh_key_path": "~/.ssh/id_prod"
    })
}

# Create environment-specific tunnels
dev_db = profiles["development"].create_tunnel_config({
    "name": "dev-database",
    "local_port": 3306,
    "remote_host": "db.dev.internal",
    "remote_port": 3306
})

prod_db = profiles["production"].create_tunnel_config({
    "name": "prod-database",
    "local_port": 3307,
    "remote_host": "db.prod.internal",
    "remote_port": 3306
})
```

## Configuration Templates

### Template System

```python
from string import Template

# Configuration template
tunnel_template = Template("""
{
  "name": "${environment}-${service}",
  "ssh_host": "${ssh_host}",
  "ssh_username": "${ssh_username}",
  "local_port": ${local_port},
  "remote_host": "${remote_host}",
  "remote_port": ${remote_port},
  "tags": ["${environment}", "${service}"]
}
""")

# Generate configuration
config_data = tunnel_template.substitute(
    environment="staging",
    service="api",
    ssh_host="staging.company.com",
    ssh_username="api_user",
    local_port=8080,
    remote_host="api.staging.internal",
    remote_port=80
)

config = TunnelConfig(**json.loads(config_data))
```

### Common Templates

#### Database Tunnel Template

```python
def create_database_tunnel(environment: str, db_type: str, local_port: int):
    return TunnelConfig(
        name=f"{environment}-{db_type}",
        description=f"{environment.title()} {db_type.upper()} database",
        ssh_host=f"{environment}.company.com",
        ssh_username="db_user",
        ssh_key_path=f"~/.ssh/id_{environment}",
        local_port=local_port,
        remote_host=f"{db_type}.{environment}.internal",
        remote_port=3306 if db_type == "mysql" else 5432,
        tags=[environment, "database", db_type]
    )

# Usage
dev_mysql = create_database_tunnel("dev", "mysql", 3306)
staging_postgres = create_database_tunnel("staging", "postgres", 5432)
```

#### Web Service Template

```python
def create_web_tunnel(service: str, environment: str, port: int):
    return TunnelConfig(
        name=f"{environment}-{service}",
        description=f"{environment.title()} {service} service",
        ssh_host=f"{environment}.company.com",
        ssh_username="web_user",
        local_port=port,
        remote_host=f"{service}.{environment}.internal",
        remote_port=80,
        tags=[environment, "web", service]
    )
```

## Import and Export

### Exporting Configurations

```python
def export_configurations(file_path: str, tag_filter: str = None):
    configs = config_manager.get_all_configs()
    
    if tag_filter:
        configs = [c for c in configs if tag_filter in c.tags]
    
    export_data = {
        "version": "1.0",
        "exported_at": datetime.now().isoformat(),
        "tunnels": [config.to_dict() for config in configs]
    }
    
    with open(file_path, 'w') as f:
        json.dump(export_data, f, indent=2)

# Export all configurations
export_configurations("all_tunnels.json")

# Export production configurations only
export_configurations("prod_tunnels.json", "production")
```

### Importing Configurations

```python
def import_configurations(file_path: str, merge: bool = True):
    with open(file_path, 'r') as f:
        import_data = json.load(f)
    
    existing_names = [c.name for c in config_manager.get_all_configs()]
    
    for tunnel_data in import_data["tunnels"]:
        config = TunnelConfig(**tunnel_data)
        
        if not merge and config.name in existing_names:
            print(f"Skipping existing tunnel: {config.name}")
            continue
        
        if config.name in existing_names:
            config.name += "_imported"
        
        config_manager.save_tunnel_config(config)

# Import configurations
import_configurations("shared_tunnels.json")
```

### Backup and Restore

```python
import shutil
from datetime import datetime

def backup_configurations():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(f"config_backup_{timestamp}")
    backup_dir.mkdir()
    
    # Copy configuration files
    config_dir = config_manager.get_config_directory()
    shutil.copytree(config_dir, backup_dir / "config")
    
    # Export as JSON
    export_configurations(backup_dir / "tunnels_export.json")
    
    print(f"Backup created: {backup_dir}")

def restore_configurations(backup_dir: str):
    backup_path = Path(backup_dir)
    
    if (backup_path / "tunnels_export.json").exists():
        import_configurations(backup_path / "tunnels_export.json")
    else:
        # Restore from config files
        config_backup = backup_path / "config"
        if config_backup.exists():
            config_dir = config_manager.get_config_directory()
            shutil.copytree(config_backup, config_dir, dirs_exist_ok=True)
```

## Configuration Validation

### Validation Rules

```python
def validate_tunnel_config(config: TunnelConfig) -> list:
    errors = []
    
    # Required fields
    if not config.name:
        errors.append("Tunnel name is required")
    
    if not config.ssh_host:
        errors.append("SSH host is required")
    
    # Port validation
    if not (1 <= config.local_port <= 65535):
        errors.append("Local port must be between 1 and 65535")
    
    if not (1 <= config.remote_port <= 65535):
        errors.append("Remote port must be between 1 and 65535")
    
    # SSH key validation
    if config.ssh_key_path:
        key_path = Path(config.ssh_key_path).expanduser()
        if not key_path.exists():
            errors.append(f"SSH key file not found: {config.ssh_key_path}")
    
    # Name uniqueness
    existing_configs = config_manager.get_all_configs()
    existing_names = [c.name for c in existing_configs if c.name != config.name]
    if config.name in existing_names:
        errors.append(f"Tunnel name already exists: {config.name}")
    
    return errors

# Usage
config = TunnelConfig(name="test", ssh_host="server.com", local_port=8080, remote_port=80)
errors = validate_tunnel_config(config)
if errors:
    print("Validation errors:")
    for error in errors:
        print(f"  - {error}")
```

### Pre-save Validation

```python
def save_tunnel_config_with_validation(config: TunnelConfig):
    errors = validate_tunnel_config(config)
    
    if errors:
        raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
    
    config_manager.save_tunnel_config(config)
```

## Configuration Security

### Sensitive Data Handling

```python
def encrypt_sensitive_fields(config: TunnelConfig, encryption_key: str):
    """Encrypt sensitive configuration fields"""
    from cryptography.fernet import Fernet
    
    fernet = Fernet(encryption_key.encode())
    
    # Encrypt passphrase if present
    if config.ssh_key_passphrase:
        encrypted = fernet.encrypt(config.ssh_key_passphrase.encode())
        config.ssh_key_passphrase = encrypted.decode()
    
    return config

def decrypt_sensitive_fields(config: TunnelConfig, encryption_key: str):
    """Decrypt sensitive configuration fields"""
    from cryptography.fernet import Fernet
    
    fernet = Fernet(encryption_key.encode())
    
    # Decrypt passphrase if present
    if config.ssh_key_passphrase:
        decrypted = fernet.decrypt(config.ssh_key_passphrase.encode())
        config.ssh_key_passphrase = decrypted.decode()
    
    return config
```

### Configuration File Permissions

```python
import os
import stat

def secure_config_files():
    """Set secure permissions on configuration files"""
    config_dir = config_manager.get_config_directory()
    
    # Set directory permissions (owner read/write/execute only)
    os.chmod(config_dir, stat.S_IRWXU)
    
    # Set file permissions (owner read/write only)
    for config_file in config_dir.glob("*.json"):
        os.chmod(config_file, stat.S_IRUSR | stat.S_IWUSR)
```

## Best Practices

### Configuration Management

1. ✅ **Use descriptive names** that indicate purpose
2. ✅ **Tag configurations** for easy organization  
3. ✅ **Regular backups** of configuration data
4. ✅ **Version control** for shared configurations
5. ✅ **Validate configurations** before saving
6. ✅ **Document purposes** in descriptions
7. ✅ **Use templates** for consistency
8. ✅ **Secure sensitive data** with encryption

### Organization Tips

1. **Consistent naming** across environments
2. **Logical grouping** by project or service
3. **Clear documentation** for each tunnel purpose
4. **Regular cleanup** of unused configurations
5. **Team sharing** through export/import

This guide provides comprehensive coverage of configuration management for the SSH Tools Suite, enabling efficient organization and maintenance of tunnel configurations.
