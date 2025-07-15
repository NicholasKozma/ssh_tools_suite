# Installation Guide

[![PyPI version](https://img.shields.io/pypi/v/ssh-tools-suite.svg)](https://pypi.org/project/ssh-tools-suite/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ssh-tools-suite)](https://pypi.org/project/ssh-tools-suite/)

This guide will help you install and set up the SSH Tools Suite on your system.

## Quick Installation

The easiest way to install SSH Tools Suite is via PyPI:

```bash
{{ pip_install_cmd() }}
```

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10/11, Linux (Ubuntu 20.04+), macOS 10.15+
- **Python**: 3.9 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Disk Space**: 500MB for installation plus space for configurations
- **Network**: Internet connection for package installation

### Recommended Requirements
- **Python**: 3.11 or higher
- **RAM**: 8GB or more
- **SSH Client**: OpenSSH (usually pre-installed on modern systems)

## Installation Methods

### Method 1: PyPI Installation (Recommended)

#### Basic Installation
```bash
# Install the latest stable version
{{ pip_install_cmd() }}

# Verify installation
ssh-tunnel-manager --version
ssh-tools-installer --version
```

#### With Optional Dependencies
```bash
# Install with development tools
{{ pip_install_dev() }}

# Install with documentation tools
{{ pip_install_docs() }}

# Install with all optional dependencies
{{ pip_install_all() }}
```

#### Upgrade to Latest Version
```bash
# Upgrade to the latest version
pip install --upgrade ssh-tools-suite
```

### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/NicholasKozma/ssh_tools_suite.git
cd ssh-tools-suite

# Install in development mode
pip install -e .

# Or install with dependencies
pip install -e .[dev,docs]
```

### Method 3: Using Poetry (For Developers)

```bash
# Clone the repository
git clone https://github.com/NicholasKozma/ssh_tools_suite.git
cd ssh-tools-suite

# Install dependencies with Poetry
poetry install --with dev,docs

# Activate the virtual environment
poetry shell
```

## Platform-Specific Setup

### Windows

1. **Install Python 3.9+** from [python.org](https://python.org) or Microsoft Store
2. **Install SSH Tools Suite**:
   ```cmd
   {{ pip_install_cmd() }}
   ```
3. **Verify SSH Client**: Windows 10/11 includes OpenSSH by default
   ```cmd
   ssh -V
   ```

#### Windows-Specific Dependencies
The following packages are automatically installed on Windows:
- `WMI>=1.5.1` - Windows Management Instrumentation
- `pywin32>=305` - Windows API access

### Linux (Ubuntu/Debian)

1. **Update system packages**:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python and pip** (if not already installed):
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Install system dependencies**:
   ```bash
   sudo apt install openssh-client qt6-base-dev
   ```

4. **Install SSH Tools Suite**:
   ```bash
   pip3 install ssh-tools-suite
   ```

### Linux (CentOS/RHEL/Fedora)

1. **Install Python and dependencies**:
   ```bash
   # CentOS/RHEL
   sudo yum install python3 python3-pip openssh-clients qt6-qtbase-devel

   # Fedora
   sudo dnf install python3 python3-pip openssh-clients qt6-qtbase-devel
   ```

2. **Install SSH Tools Suite**:
   ```bash
   pip3 install ssh-tools-suite
   ```

### macOS

1. **Install Python 3.9+** using Homebrew:
   ```bash
   brew install python@3.11
   ```

2. **Install SSH Tools Suite**:
   ```bash
   pip3 install ssh-tools-suite
   ```

3. **Verify SSH Client** (usually pre-installed):
   ```bash
   ssh -V
   ```

## Verification

### Test Installation

```bash
# Check if the package is installed correctly
python -c "import ssh_tunnel_manager; print('Installation successful!')"

# Check version
python -c "import ssh_tunnel_manager; print(ssh_tunnel_manager.__version__)"
```

### Launch GUI Application

```bash
# Start the SSH Tunnel Manager GUI
ssh-tunnel-manager-gui

# Or run the module directly
python -m ssh_tunnel_manager.gui
```

### Command Line Tools

```bash
# SSH Tunnel Manager CLI
ssh-tunnel-manager --help

# Third-Party Installer
ssh-tools-installer --help
```

## Common Installation Issues

### Issue: "No module named 'PySide6'"

**Solution**: Install PySide6 manually
```bash
pip install PySide6>=6.5.0
```

### Issue: "Microsoft Visual C++ 14.0 is required" (Windows)

**Solution**: Install Visual Studio Build Tools
1. Download from [Microsoft](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
2. Install with C++ build tools
3. Retry installation

### Issue: "Permission denied" on Linux

**Solution**: Use virtual environment or user installation
```bash
# User installation
pip install --user ssh-tools-suite

# Or use virtual environment
python -m venv ssh-tools-env
source ssh-tools-env/bin/activate  # Linux/macOS
# ssh-tools-env\Scripts\activate  # Windows
{{ pip_install_cmd() }}
```

### Issue: Qt platform plugin issues on Linux

**Solution**: Install Qt platform plugins
```bash
# Ubuntu/Debian
sudo apt install qt6-qpa-plugins

# CentOS/RHEL
sudo yum install qt6-qtbase-gui
```

## Development Installation

For developers who want to contribute or modify the code:

### 1. Clone and Setup Development Environment

```bash
git clone https://github.com/NicholasKozma/ssh_tools_suite.git
cd ssh-tools-suite

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate  # Windows

# Install in development mode with all dependencies
pip install -e .[dev,docs]
```

### 2. Install Pre-commit Hooks

```bash
pre-commit install
```

### 3. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/ssh_tunnel_manager

# Run specific test category
pytest -m "not slow"  # Skip slow tests
pytest -m gui  # Run only GUI tests
```

### 4. Build Documentation

```bash
# Install documentation dependencies
pip install .[docs]

# Build and serve documentation locally
mkdocs serve

# Build for production
mkdocs build
```

## Next Steps

After successful installation:

1. **[Quick Start Guide](quick-start.md)** - Learn basic usage
2. **[Configuration Guide](configuration.md)** - Set up your preferences
3. **[Creating Your First Tunnel](../guides/creating-tunnels.md)** - Step-by-step tutorial

## Uninstallation

To remove SSH Tools Suite:

```bash
# Remove the package
pip uninstall ssh-tools-suite

# Remove configuration files (optional)
# Windows: Remove %APPDATA%\SSHTunnelManager
# Linux/macOS: Remove ~/.config/SSHTunnelManager
```

## Getting Help

If you encounter issues during installation:

1. Check the [Troubleshooting Guide](../guides/troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/NicholasKozma/ssh_tools_suite/issues)
3. Create a new issue with:
   - Your operating system and version
   - Python version (`python --version`)
   - Complete error message
   - Installation method used
