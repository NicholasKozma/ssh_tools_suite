# SSH Tunnel Manager - Core Module Documentation

The SSH Tunnel Manager is the primary module within the SSH Tools Suite, responsible for creating, managing, and monitoring SSH tunnels with a professional graphical interface.

## Module Purpose

The SSH Tunnel Manager module serves as a comprehensive solution for:

- **Secure Network Access**: Establish encrypted tunnels to access remote services
- **Port Forwarding**: Forward local ports to remote hosts through SSH connections
- **SOCKS Proxy**: Create dynamic SOCKS proxies for flexible routing
- **RTSP Streaming**: Stream video content securely over SSH tunnels
- **Configuration Management**: Store, import, and export tunnel configurations
- **Real-time Monitoring**: Track tunnel status and connection health

## Architecture Overview

The module follows a clean separation of concerns with distinct layers:

```
ssh_tunnel_manager/
├── core/          # Core business logic and data models
├── gui/           # User interface components
└── utils/         # Utility functions and helpers
```

## Key Classes and Functions

### Core Classes

#### `TunnelConfig`
**Location**: `ssh_tunnel_manager.core.models.TunnelConfig`

The central data model representing an SSH tunnel configuration.

**Key Attributes**:
- `name: str` - Unique identifier for the tunnel
- `ssh_host: str` - Target SSH server hostname/IP
- `ssh_port: int` - SSH server port (default: 22)
- `ssh_user: str` - SSH username
- `local_port: int` - Local port for forwarding
- `remote_host: str` - Remote target host
- `remote_port: int` - Remote target port
- `tunnel_type: str` - Type: 'local', 'remote', or 'dynamic'
- `ssh_key_path: str` - Path to SSH private key (optional)
- `rtsp_url: str` - Custom RTSP URL (optional)

**Key Methods**:
- `validate() -> tuple[bool, str]` - Validates configuration parameters
- `get_ssh_command_args() -> list[str]` - Generates SSH command arguments
- `to_dict() -> dict` - Serializes to dictionary (excludes sensitive data)
- `from_dict(data: dict) -> TunnelConfig` - Deserializes from dictionary

#### `ConfigurationManager`
**Location**: `ssh_tunnel_manager.core.config_manager.ConfigurationManager`

Manages tunnel configurations and application settings.

**Key Methods**:
- `load_configurations() -> Dict[str, TunnelConfig]` - Loads saved configurations
- `save_configurations()` - Persists configurations to storage
- `add_configuration(config: TunnelConfig) -> tuple[bool, str]` - Adds new configuration
- `update_configuration(old_name: str, config: TunnelConfig) -> tuple[bool, str]` - Updates existing configuration
- `delete_configuration(name: str) -> bool` - Removes configuration
- `export_configurations(file_path: Path) -> tuple[bool, str]` - Exports to JSON
- `import_configurations(file_path: Path) -> tuple[bool, str]` - Imports from JSON

#### `TunnelProcess`
**Location**: `ssh_tunnel_manager.core.tunnel_process.TunnelProcess`

Manages the lifecycle of individual SSH tunnel processes.

**Key Attributes**:
- `config: TunnelConfig` - Associated tunnel configuration
- `process: subprocess.Popen` - The underlying SSH process
- `is_running: bool` - Current running status
- `status: str` - Detailed status ('stopped', 'starting', 'running', 'error')

**Key Methods**:
- `start() -> bool` - Starts the SSH tunnel process
- `stop() -> bool` - Terminates the tunnel process
- `is_healthy() -> bool` - Checks tunnel health
- `get_status() -> str` - Returns current status

#### `SSHTunnelManager`
**Location**: `ssh_tunnel_manager.gui.main_window.SSHTunnelManager`

The main GUI window providing the user interface for tunnel management.

**Key Components**:
- Tunnel configuration table
- Real-time status monitoring
- Toolbar with action buttons
- System tray integration
- Logging widget

## Inputs and Outputs

### Input Data Types

#### Tunnel Configuration Input
```python
{
    "name": "string",           # Tunnel identifier
    "ssh_host": "string",       # SSH server hostname/IP
    "ssh_port": "int",          # SSH port (1-65535)
    "ssh_user": "string",       # SSH username
    "local_port": "int",        # Local port (1024-65535)
    "remote_host": "string",    # Remote target host
    "remote_port": "int",       # Remote port (1-65535)
    "tunnel_type": "string",    # 'local'|'remote'|'dynamic'
    "description": "string",    # Optional description
    "auto_start": "bool",       # Auto-start on launch
    "ssh_key_path": "string",   # Optional SSH key path
    "rtsp_url": "string"        # Optional custom RTSP URL
}
```

#### SSH Connection Parameters
- **Host**: IP address or hostname of SSH server
- **Port**: SSH service port (typically 22)
- **Username**: SSH authentication username
- **Authentication**: SSH key file or password (prompted at runtime)

### Output Data Types

#### Tunnel Status Information
```python
{
    "name": "string",           # Tunnel name
    "status": "string",         # 'stopped'|'starting'|'running'|'error'
    "is_running": "bool",       # Current state
    "local_port": "int",        # Forwarded port
    "connection_string": "str", # Human-readable connection info
    "pid": "int|None"           # Process ID if running
}
```

#### Configuration Export Format
```json
{
    "version": "1.0",
    "tunnels": {
        "tunnel_name": {
            "name": "tunnel_name",
            "ssh_host": "192.168.1.100",
            "ssh_port": 22,
            "ssh_user": "admin",
            "local_port": 8554,
            "remote_host": "localhost",
            "remote_port": 554,
            "tunnel_type": "local",
            "description": "RTSP Camera Access",
            "auto_start": false,
            "ssh_key_path": "/path/to/key",
            "rtsp_url": "rtsp://localhost:8554/live/0"
        }
    }
}
```

## Dependencies

### External Libraries

#### Core Dependencies
- **PySide6 (>=6.5.0)**: Qt-based GUI framework
- **paramiko (>=2.8.0)**: SSH client implementation
- **cryptography (>=3.4.0)**: Cryptographic operations
- **opencv-python (>=4.8.0)**: Video processing for RTSP
- **requests (>=2.28.0)**: HTTP client for web operations
- **psutil (>=5.9.0)**: System and process utilities

#### Platform-Specific Dependencies
- **Windows**: `WMI (>=1.5.1)`, `pywin32 (>=305)`
- **Linux**: Standard system libraries
- **macOS**: Standard system libraries

### Internal Modules

#### Within SSH Tunnel Manager
- `ssh_tunnel_manager.core` - Core business logic
- `ssh_tunnel_manager.gui` - User interface components
- `ssh_tunnel_manager.utils` - Utility functions

#### Shared Components
- `ssh_tools_common` - Common utilities across the suite

### System Dependencies
- **SSH Client**: System SSH executable (OpenSSH recommended)
- **Terminal Emulator**: For interactive SSH sessions
- **Network Stack**: TCP/IP networking capabilities

## Key Logic and Algorithms

### Tunnel Establishment Algorithm

```python
def establish_tunnel(config: TunnelConfig) -> bool:
    """
    1. Validate configuration parameters
    2. Generate SSH command arguments
    3. Launch SSH process in terminal window
    4. Monitor process startup
    5. Verify tunnel connectivity
    6. Update status tracking
    """
```

**Process Flow**:
1. **Configuration Validation**: Ensures all required parameters are present and valid
2. **SSH Command Generation**: Builds appropriate SSH command based on tunnel type
3. **Process Launch**: Starts SSH in native terminal for password input
4. **Health Monitoring**: Continuously checks tunnel status and connectivity
5. **Error Handling**: Captures and reports connection issues

### Connection Monitoring Algorithm

The module implements a robust monitoring system:

```python
class TunnelMonitorThread:
    """
    - Polls tunnel processes every 2 seconds
    - Tests port connectivity
    - Detects connection losses
    - Triggers reconnection attempts
    - Updates GUI status indicators
    """
```

### Configuration Management

**Storage Strategy**:
- Uses Qt's QSettings for cross-platform configuration storage
- Excludes sensitive data (passwords) from persistent storage
- Supports JSON import/export for backup and sharing

**Validation Logic**:
- Port range validation (1024-65535 for local ports)
- Host/IP address format checking
- SSH parameter validation
- Duplicate name detection

## Usage Examples

### Basic Tunnel Creation

```python
from ssh_tunnel_manager.core.models import TunnelConfig
from ssh_tunnel_manager.core.config_manager import ConfigurationManager

# Create a new tunnel configuration
config = TunnelConfig(
    name="camera_rtsp",
    ssh_host="192.168.1.100",
    ssh_port=22,
    ssh_user="admin",
    local_port=8554,
    remote_host="localhost",
    remote_port=554,
    tunnel_type="local",
    description="IP Camera RTSP Access"
)

# Validate configuration
is_valid, error_msg = config.validate()
if not is_valid:
    print(f"Configuration error: {error_msg}")
    return

# Save configuration
manager = ConfigurationManager()
success, error = manager.add_configuration(config)
if success:
    print("Configuration saved successfully")
else:
    print(f"Failed to save: {error}")
```

### Starting a Tunnel Programmatically

```python
from ssh_tunnel_manager.core.tunnel_process import TunnelProcess

# Create and start tunnel process
tunnel = TunnelProcess(config)
try:
    if tunnel.start():
        print(f"Tunnel started successfully on port {config.local_port}")
    else:
        print("Failed to start tunnel")
except Exception as e:
    print(f"Error starting tunnel: {e}")
```

### Configuration Import/Export

```python
from pathlib import Path

# Export configurations
config_manager = ConfigurationManager()
config_manager.load_configurations()

export_path = Path("tunnels_backup.json")
success, message = config_manager.export_configurations(export_path)
print(f"Export result: {message}")

# Import configurations
import_path = Path("shared_tunnels.json")
success, message = config_manager.import_configurations(import_path)
print(f"Import result: {message}")
```

### Connection Testing

```python
from ssh_tunnel_manager.utils.connection_tester import ConnectionTester

# Test local port connectivity
port_accessible = ConnectionTester.test_local_port(8554)
print(f"Port 8554 accessible: {port_accessible}")

# Test tunnel service
success, message = ConnectionTester.test_tunnel_connection(config)
print(f"Tunnel test: {message}")
```

### GUI Integration

```python
from ssh_tunnel_manager.gui import SSHTunnelManager
from PySide6.QtWidgets import QApplication

# Launch the GUI application
app = QApplication([])
main_window = SSHTunnelManager()
main_window.show()
app.exec()
```

## Potential Edge Cases and Limitations

### Known Limitations

#### Platform-Specific Constraints
- **Windows**: Requires elevated privileges for ports < 1024
- **SSH Key Formats**: Limited to OpenSSH format keys
- **Terminal Dependencies**: Requires system terminal emulator

#### Network Limitations
- **Firewall Restrictions**: Corporate firewalls may block SSH
- **NAT Traversal**: Limited support for complex NAT scenarios
- **IPv6 Support**: Primarily designed for IPv4 networks

#### Concurrent Connection Limits
- **SSH Server Limits**: Target server may limit concurrent connections
- **Port Conflicts**: Local port availability on client system
- **Resource Usage**: High concurrent tunnel count may impact performance

### Edge Cases to Consider

#### Configuration Conflicts
```python
# Example: Duplicate port assignment
config1 = TunnelConfig(name="tunnel1", local_port=8554, ...)
config2 = TunnelConfig(name="tunnel2", local_port=8554, ...)
# Will cause port conflict when both tunnels are active
```

#### Authentication Failures
```python
# SSH key permission issues on Unix systems
# Workaround: Ensure key file has 600 permissions
import os
os.chmod(ssh_key_path, 0o600)
```

#### Network Connectivity Issues
```python
# Handle intermittent connections
try:
    tunnel.start()
except Exception as e:
    if "connection refused" in str(e).lower():
        # Implement retry logic with exponential backoff
        pass
```

#### Process Management Edge Cases
- **Orphaned Processes**: SSH processes may persist after GUI closure
- **Zombie Processes**: Incomplete process cleanup on system shutdown
- **Terminal Window Management**: User accidentally closing terminal windows

### Error Handling Strategies

```python
def robust_tunnel_start(config: TunnelConfig, max_retries: int = 3) -> bool:
    """Example of robust tunnel starting with retry logic"""
    for attempt in range(max_retries):
        try:
            tunnel = TunnelProcess(config)
            if tunnel.start():
                return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            time.sleep(2 ** attempt)  # Exponential backoff
    return False
```

### Performance Considerations

#### Memory Usage
- Each tunnel process consumes ~10-20MB RAM
- GUI components scale with number of configured tunnels
- Monitor thread has minimal overhead (~1% CPU)

#### Startup Time
- Configuration loading: <100ms for typical setups
- GUI initialization: 1-2 seconds
- Tunnel establishment: 2-5 seconds depending on network latency

#### Resource Cleanup
- Automatic process termination on application exit
- Configuration auto-save on changes
- Temporary file cleanup

### Security Considerations

#### Password Handling
- Passwords never stored in configuration files
- Runtime password prompting only
- Memory cleanup after authentication

#### SSH Key Security
- Private keys referenced by path only
- Key permissions validated before use
- Support for passphrase-protected keys

#### Network Security
- All traffic encrypted via SSH protocol
- Host key verification (can be disabled for convenience)
- Connection timeout and keepalive settings

This comprehensive documentation provides developers with the essential information needed to work with or integrate the SSH Tunnel Manager module effectively.
