# SSH Tunnel Manager - GUI Components

This page documents the GUI components and architecture of the SSH Tunnel Manager.

## Main Window (`main_window.py`)

The central GUI component that orchestrates all tunnel management functionality.

### Key Features
- Tunnel configuration management
- Real-time status monitoring
- Log viewing and filtering
- System tray integration

### Main Components

#### Tunnel Table Widget
Displays all configured tunnels with their status, ports, and connection information.

#### Control Buttons
- **Start/Stop**: Control individual tunnel connections
- **Add/Edit**: Manage tunnel configurations
- **Delete**: Remove tunnel configurations

#### Status Bar
Shows application status, active tunnels count, and system notifications.

## Dialog Components

### Tunnel Configuration Dialog (`tunnel_config.py`)
Modal dialog for creating and editing tunnel configurations.

**Fields:**
- Connection details (host, port, username)
- Authentication (password, SSH key)
- Port forwarding settings
- Advanced options (compression, keep-alive)

### Password Dialog (`password_dialog.py`)
Secure password input for SSH authentication.

**Features:**
- Password masking
- Remember option (encrypted storage)
- Timeout handling

### SFTP Browser (`sftp_browser.py`)
File browser for remote SFTP access through tunnels.

**Capabilities:**
- Directory navigation
- File upload/download
- Permission management
- Drag-and-drop support

### RTSP Viewer (`rtsp_viewer.py`)
Video stream viewer for RTSP connections through tunnels.

**Features:**
- Video playback controls
- Stream quality settings
- Recording capabilities
- Multiple stream support

### Multi-hop SFTP Browser (`multi_hop_sftp_browser.py`)
Advanced SFTP browser for multi-hop connections.

## Widget Components

### SSH Terminal Widget (`ssh_terminal.py`)
Embedded terminal for SSH sessions.

**Features:**
- Terminal emulation
- Command history
- Copy/paste support
- Customizable appearance

### Log Widget (`log_widget.py`)
Displays application and tunnel logs.

**Capabilities:**
- Log level filtering
- Search functionality
- Export options
- Auto-scroll

### Table Widget (`table_widget.py`)
Custom table widget for tunnel display.

**Features:**
- Sortable columns
- Context menus
- Status indicators
- Batch operations

## Utility Components

### Network Scanner (`network_scanner.py`)
Scans for available hosts and services.

**Functions:**
- Port scanning
- Service detection
- Network discovery
- Host availability checks

### Network Visualizer (`network_visualizer.py`)
Visual representation of network topology.

**Features:**
- Network diagrams
- Connection mapping
- Real-time updates
- Interactive navigation

### SSH Key Management (`ssh_key_generator.py`, `ssh_key_deployment.py`)
Tools for SSH key generation and deployment.

**Capabilities:**
- Key generation (RSA, Ed25519)
- Key deployment to remote hosts
- Key format conversion
- Security validation

### PowerShell Generator (`powershell_generator.py`)
Generates PowerShell scripts for tunnel automation.

**Output:**
- Windows batch files
- PowerShell scripts
- Scheduled task definitions
- Registry entries

### RDP Handler (`rdp_handler.py`)
Manages Remote Desktop Protocol connections through tunnels.

**Features:**
- RDP file generation
- Connection testing
- Credential management
- Session monitoring

### RTSP Handler (`rtsp_handler.py`)
Handles RTSP video streams through tunnels.

**Capabilities:**
- Stream discovery
- Protocol negotiation
- Quality adjustment
- Recording management

## File Operations (`file_operations.py`)

Handles file operations for tunnel configurations and logs.

**Functions:**
- Configuration import/export
- Log file management
- Backup and restore
- Template management

## Toolbar (`toolbar.py`)

Main application toolbar with quick actions.

**Buttons:**
- New tunnel
- Import/Export
- Settings
- Help

## Architecture Overview

```
Main Window
├── Menu Bar
├── Toolbar
├── Central Widget
│   ├── Tunnel Table
│   ├── Control Panel
│   └── Status Display
├── Dock Widgets
│   ├── Log Viewer
│   ├── Network Scanner
│   └── File Browser
└── Status Bar
```

## Event Handling

### Signals and Slots
The GUI uses Qt's signal-slot mechanism for component communication.

### State Management
Application state is managed through a central configuration manager.

### Error Handling
Comprehensive error handling with user-friendly messages and recovery options.

## Styling and Themes

### Custom Styles
- Dark and light themes
- Color-coded status indicators
- Responsive layouts
- Accessibility features

### Platform Integration
- Native look and feel
- System tray integration
- File associations
- URL handlers

## Performance Considerations

### Threading
- Background operations in separate threads
- Non-blocking UI updates
- Efficient data structures

### Memory Management
- Resource cleanup
- Cache management
- Memory leak prevention

### Responsiveness
- Asynchronous operations
- Progress indicators
- User feedback
