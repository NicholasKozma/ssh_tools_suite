# SSH Tools Suite Documentation

[![PyPI version](https://badge.fury.io/py/ssh-tools-suite.svg)](https://badge.fury.io/py/ssh-tools-suite)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ssh-tools-suite)](https://pypi.org/project/ssh-tools-suite/)
[![GitHub Release](https://img.shields.io/github/v/release/NicholasKozma/ssh_tools_suite)](https://github.com/NicholasKozma/ssh_tools_suite/releases)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/NicholasKozma/ssh_tools_suite/blob/main/LICENSE)

Welcome to the SSH Tools Suite documentation! This comprehensive toolkit provides powerful SSH tunnel management capabilities and third-party software installation utilities.

## Installation Options

### Option 1: Standalone Executables (No Python Required)
Download pre-built executables from [**GitHub Releases**](https://github.com/NicholasKozma/ssh_tools_suite/releases):

- **Windows**: `SSH-Tunnel-Manager-v{{ pypi_version() }}.zip` - Fast startup, no dependencies
- **Benefits**: ⚡ 2-3 second startup, 🚀 portable, 🔒 all dependencies included

### Option 2: PyPI Installation (For Python Users)
```bash
{{ pip_install_cmd() }}
```

### Option 3: From Source (For Developers)
```bash
git clone https://github.com/NicholasKozma/ssh_tools_suite.git
cd ssh_tools_suite
pip install -e .
```

## What is SSH Tools Suite?

SSH Tools Suite is a professional-grade application suite designed for:

- **SSH Tunnel Management**: Create, manage, and monitor SSH tunnels with an intuitive GUI
- **RTSP Streaming**: Stream video over secure SSH tunnels
- **File Operations**: Browse and transfer files via SFTP
- **Network Tools**: Scan networks and test connections
- **Third-Party Installation**: Automated installation of external tools

## Key Features

### SSH Tunnel Manager
- Multiple tunnel types (Local, Remote, Dynamic/SOCKS)
- Real-time monitoring and health checks
- RTSP video streaming support
- SSH key management and deployment
- Configuration import/export
- System tray integration

### Third-Party Installer
- Automated tool installation
- Dependency management
- Configuration validation

## Quick Navigation

- **[Installation Guide](getting-started/installation.md)** - All installation methods
- **[Standalone Executables](getting-started/executable-installation.md)** - No Python required!
- **[Quick Start](getting-started/quick-start.md)** - Get running in minutes
- **[SSH Tunnel Manager](ssh-tunnel-manager/overview.md)** - Core tunnel management functionality
- **[User Guides](guides/creating-tunnels.md)** - Step-by-step tutorials
- **[GitHub Releases](https://github.com/NicholasKozma/ssh_tools_suite/releases)** - Download executables and releases

## System Requirements

### For Standalone Executables
- **Operating System**: Windows 10/11 (macOS and Linux coming soon)
- **Memory**: 4GB RAM minimum
- **Disk Space**: 500MB for installation

### For PyPI Installation  
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.9 or higher
- **Dependencies**: PySide6, OpenCV, Paramiko, and more (see installation guide)

## License

This project is licensed under the MIT License. See the [LICENSE](https://github.com/NicholasKozma/ssh_tools_suite/blob/main/LICENSE) file for details.

## Support

- **Documentation**: This site
- **Issues**: [GitHub Issues](https://github.com/NicholasKozma/ssh_tools_suite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/NicholasKozma/ssh_tools_suite/discussions)
