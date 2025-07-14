# SSH Tunnel Manager Overview

The SSH Tunnel Manager is a comprehensive, professional-grade application for creating, managing, and monitoring SSH tunnels with an intuitive graphical interface.

## What is SSH Tunneling?

SSH tunneling (also known as SSH port forwarding) is a method of transporting network data over an encrypted SSH connection. It allows you to:

- **Securely access remote services** through an encrypted tunnel
- **Bypass network restrictions** by routing traffic through an SSH server
- **Access internal network resources** from outside the network
- **Create secure connections** for applications that don't natively support encryption

## Key Features

### 🚀 Multiple Tunnel Types
- **Local Port Forwarding**: Forward local ports to remote destinations
- **Remote Port Forwarding**: Allow remote access to local services
- **Dynamic Port Forwarding**: Create SOCKS proxy for flexible routing

### 🖥️ Professional GUI
- Clean, intuitive interface built with PySide6
- Real-time tunnel status monitoring
- System tray integration for background operation
- Comprehensive logging and error reporting

### 🔒 Security Features
- SSH key management and deployment
- No password storage (runtime authentication only)
- Host key verification options
- Secure configuration handling

### 📹 RTSP Integration
- Built-in RTSP viewer for video streams
- Automatic RTSP URL generation
- Support for common camera protocols
- One-click stream access

### 📂 File Operations
- SFTP browser for remote file access
- File transfer capabilities
- Multi-hop SFTP through tunnels
- Quick file operations

### ⚙️ Configuration Management
- Import/Export configurations as JSON
- Auto-start tunnels on application launch
- Configuration backup and restore
- Bulk operations support

### 🔧 Advanced Tools
- Network scanner for host discovery
- Connection testing utilities
- PowerShell command generation
- SSH key generation and deployment

## Architecture

The SSH Tunnel Manager follows a modular architecture:

```
SSH Tunnel Manager
├── Core Layer
│   ├── Configuration Management
│   ├── Process Management
│   ├── Monitoring System
│   └── Data Models
├── GUI Layer
│   ├── Main Window
│   ├── Dialog Components
│   ├── Toolbar & Widgets
│   └── System Integration
└── Utilities Layer
    ├── Connection Testing
    ├── RTSP Handling
    ├── File Operations
    └── Network Tools
```

## Use Cases

### Network Administration
- Access internal servers from remote locations
- Manage network equipment through secure tunnels
- Monitor services on isolated networks
- Troubleshoot connectivity issues

### Development & DevOps
- Connect to development databases
- Access staging environments
- Secure API testing
- Remote debugging sessions

### Security & Surveillance
- Access IP cameras and NVR systems
- Stream RTSP video over secure connections
- Monitor remote facilities
- Centralized security management

### Remote Work
- Access office resources securely
- VPN alternative for specific services
- Bypass restrictive network policies
- Secure file transfers

## Getting Started

1. **[Install](../getting-started/installation.md)** the SSH Tools Suite
2. **[Quick Start](../getting-started/quick-start.md)** - Create your first tunnel
3. **[Configure](../getting-started/configuration.md)** your preferences

## Learn More

- **[Core Module Documentation](core-module.md)** - Technical details for developers
- **[GUI Components](gui-components.md)** - User interface overview
- **[Usage Examples](usage-examples.md)** - Practical implementation examples
- **[API Reference](api-reference.md)** - Complete API documentation
