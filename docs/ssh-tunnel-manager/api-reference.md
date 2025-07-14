# SSH Tunnel Manager - API Reference

This page provides detailed API documentation for the SSH Tunnel Manager modules.

# SSH Tunnel Manager - API Reference

This page provides detailed API documentation for the SSH Tunnel Manager modules.

## Core Modules

### TunnelConfig (`ssh_tunnel_manager.core.models`)

Configuration model for SSH tunnels.

**Class**: `TunnelConfig`
- **Purpose**: Represents a tunnel configuration with all necessary parameters
- **Key Attributes**:
  - `name`: Human-readable tunnel name
  - `ssh_host`: SSH server hostname or IP
  - `ssh_port`: SSH server port (default: 22)
  - `ssh_username`: SSH username
  - `ssh_password`: SSH password (optional if using keys)
  - `ssh_key_path`: Path to SSH private key file
  - `local_port`: Local port for forwarding
  - `remote_host`: Target host for forwarding
  - `remote_port`: Target port for forwarding
  - `tunnel_type`: Type of tunnel (local, remote, dynamic)

### ConfigManager (`ssh_tunnel_manager.core.config_manager`)

Manages tunnel configurations and persistence.

**Class**: `ConfigManager`
- **Purpose**: Handles saving, loading, and managing tunnel configurations
- **Key Methods**:
  - `save_config(config)`: Save a tunnel configuration
  - `load_configs()`: Load all saved configurations
  - `delete_config(name)`: Delete a configuration by name
  - `get_config_by_name(name)`: Retrieve a specific configuration
  - `export_configs(filepath)`: Export configurations to file
  - `import_configs(filepath)`: Import configurations from file

### TunnelProcess (`ssh_tunnel_manager.core.tunnel_process`)

Handles SSH tunnel process management.

**Class**: `TunnelProcess`
- **Purpose**: Manages the lifecycle of SSH tunnel processes
- **Key Methods**:
  - `start()`: Start the tunnel process
  - `stop()`: Stop the tunnel process
  - `restart()`: Restart the tunnel process
  - `is_active()`: Check if tunnel is running
  - `get_status()`: Get detailed tunnel status
  - `get_pid()`: Get process ID

### TunnelMonitor (`ssh_tunnel_manager.core.monitor`)

Monitors tunnel health and status.

**Class**: `TunnelMonitor`
- **Purpose**: Provides monitoring and health checking for tunnels
- **Key Methods**:
  - `add_tunnel(tunnel)`: Add tunnel to monitoring
  - `remove_tunnel(tunnel)`: Remove tunnel from monitoring
  - `start_monitoring()`: Begin monitoring process
  - `stop_monitoring()`: Stop monitoring process
  - `get_tunnel_status(name)`: Get status of specific tunnel
  - `get_all_statuses()`: Get status of all monitored tunnels

### Constants (`ssh_tunnel_manager.core.constants`)

Application constants and configuration values.

**Constants**:
- `DEFAULT_SSH_PORT`: Default SSH port (22)
- `DEFAULT_TIMEOUT`: Default connection timeout
- `LOG_LEVELS`: Available logging levels
- `TUNNEL_TYPES`: Supported tunnel types
- `CONFIG_DIR`: Configuration directory path
- `LOG_DIR`: Log directory path

## GUI Modules

### Main Window (`ssh_tunnel_manager.gui.main_window`)

Primary application window and controller.

**Class**: `TunnelManagerGUI`
- **Purpose**: Main application window that orchestrates all functionality
- **Key Features**:
  - Tunnel table display and management
  - Real-time status monitoring
  - System tray integration
  - Menu and toolbar management
- **Key Methods**:
  - `add_tunnel_config(config)`: Add new tunnel configuration
  - `start_tunnel(name)`: Start specific tunnel
  - `stop_tunnel(name)`: Stop specific tunnel
  - `refresh_status()`: Update tunnel status display
  - `show_logs()`: Display application logs

### Dialog Components

#### Tunnel Configuration Dialog

**Class**: `TunnelConfigDialog`
- **Purpose**: Modal dialog for creating and editing tunnel configurations
- **Features**:
  - Form-based configuration input
  - Validation and error handling
  - Test connection functionality
  - SSH key file selection

#### SFTP Browser

**Class**: `SftpBrowser`
- **Purpose**: File browser for remote SFTP access through tunnels
- **Features**:
  - Directory navigation
  - File upload/download
  - Permission management
  - Drag-and-drop support

#### RTSP Viewer

**Class**: `RtspViewer`
- **Purpose**: Video stream viewer for RTSP connections through tunnels
- **Features**:
  - Video playback controls
  - Stream quality settings
  - Recording capabilities

### Widget Components

#### SSH Terminal Widget

**Class**: `SshTerminal`
- **Purpose**: Embedded terminal for SSH sessions
- **Features**:
  - Terminal emulation
  - Command history
  - Copy/paste support
  - Customizable appearance

## Utility Modules

### Connection Tester (`ssh_tunnel_manager.utils.connection_tester`)

Tests SSH connections and tunnel functionality.

**Class**: `ConnectionTester`
- **Purpose**: Validates SSH connections and tunnel functionality
- **Key Methods**:
  - `test_ssh_connection(config)`: Test SSH connectivity
  - `test_tunnel_forwarding(config)`: Test port forwarding
  - `ping_host(host)`: Basic connectivity test
  - `scan_port(host, port)`: Check if port is open

### RTSP Viewer Utility (`ssh_tunnel_manager.utils.rtsp_viewer`)

RTSP stream viewing utilities.

**Class**: `RtspViewerUtil`
- **Purpose**: Utilities for RTSP stream handling
- **Key Methods**:
  - `connect_stream(url)`: Connect to RTSP stream
  - `get_stream_info(url)`: Get stream metadata
  - `record_stream(url, output_file)`: Record stream to file

## Examples

### Basic Usage

```python
from ssh_tunnel_manager.core.models import TunnelConfig
from ssh_tunnel_manager.core.tunnel_process import TunnelProcess

# Create tunnel configuration
config = TunnelConfig(
    name="Database Tunnel",
    ssh_host="jumpserver.example.com",
    ssh_port=22,
    ssh_username="myuser",
    local_port=5432,
    remote_host="database.internal",
    remote_port=5432
)

# Start tunnel
tunnel = TunnelProcess(config)
tunnel.start()

# Check status
if tunnel.is_active():
    print("Tunnel is running")

# Stop tunnel
tunnel.stop()
```

### Configuration Management

```python
from ssh_tunnel_manager.core.config_manager import ConfigManager

# Initialize configuration manager
config_mgr = ConfigManager()

# Save configuration
config_mgr.save_config(config)

# Load all configurations
configs = config_mgr.load_configs()

# Find configuration by name
config = config_mgr.get_config_by_name("Database Tunnel")
```

### Monitoring

```python
from ssh_tunnel_manager.core.monitor import TunnelMonitor

# Create monitor
monitor = TunnelMonitor()

# Add tunnel to monitor
monitor.add_tunnel(tunnel)

# Start monitoring
monitor.start_monitoring(interval=30)

# Get tunnel status
status = monitor.get_tunnel_status(tunnel.config.name)
```

## Error Handling

All API methods raise appropriate exceptions for error conditions:

- `TunnelError`: General tunnel operation errors
- `ConfigError`: Configuration validation errors
- `ConnectionError`: SSH connection failures
- `AuthenticationError`: SSH authentication failures

Example error handling:

```python
from ssh_tunnel_manager.core.exceptions import TunnelError

try:
    tunnel.start()
except TunnelError as e:
    print(f"Failed to start tunnel: {e}")
    # Handle error appropriately
```

## Configuration Schema

Tunnel configurations are stored as JSON with the following schema:

```json
{
    "name": "string",
    "ssh_host": "string",
    "ssh_port": "integer",
    "ssh_username": "string",
    "ssh_password": "string (optional)",
    "ssh_key_path": "string (optional)",
    "local_port": "integer",
    "remote_host": "string",
    "remote_port": "integer",
    "tunnel_type": "string (local|remote|dynamic)",
    "compression": "boolean",
    "keep_alive": "boolean",
    "auto_reconnect": "boolean"
}
```

## Thread Safety

The SSH Tunnel Manager is designed to be thread-safe:

- Configuration operations are protected by locks
- Tunnel processes run in separate threads
- GUI updates are dispatched to the main thread
- Monitor operations use thread-safe collections

## Performance Considerations

- Tunnel processes are lightweight and efficient
- Configuration loading is optimized for large numbers of tunnels
- Monitoring uses minimal system resources
- GUI updates are batched for better performance
