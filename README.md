# SSH Tools Suite

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://python.org)
[![PyPI version](https://img.shields.io/pypi/v/ssh-tools-suite.svg)](https://pypi.org/project/ssh-tools-suite/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/ssh-tools-suite)](https://pypi.org/project/ssh-tools-suite/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/NicholasKozma/ssh_tools_suite)
[![Documentation](https://img.shields.io/badge/docs-MkDocs-blue.svg)](https://nicholaskozma.github.io/ssh_tools_suite/)

> **Professional SSH tunnel management and third-party software installation suite with intuitive GUI**

SSH Tools Suite is a comprehensive toolkit for managing SSH tunnels, streaming RTSP video, and automating third-party software installations. Built with Python and PySide6, it provides both command-line and graphical interfaces for maximum flexibility.

## ✨ Features

### 🔐 SSH Tunnel Manager
- **Multiple Tunnel Types**: Local, Remote, and Dynamic (SOCKS) tunnels
- **Real-time Monitoring**: Live status updates and health checks
- **RTSP Video Streaming**: Stream video securely through SSH tunnels
- **SSH Key Management**: Generate, deploy, and manage SSH keys
- **Network Tools**: Port scanner, connection tester, and network visualizer
- **SFTP File Browser**: Browse and transfer files with drag-and-drop support
- **Configuration Management**: Import/export tunnel configurations
- **System Tray Integration**: Minimize to tray with notifications

### 🛠️ Third-Party Installer
- **Automated Installation**: Install external tools and dependencies
- **Configuration Validation**: Ensure proper tool setup
- **Dependency Management**: Handle complex installation requirements
- **GUI and CLI Modes**: Flexible installation options

### 🎥 RTSP Streaming
- **Video Playback**: View RTSP streams through secure tunnels
- **Recording Capabilities**: Save streams to local files
- **Multiple Stream Support**: Handle concurrent video feeds
- **Quality Controls**: Adjust stream parameters

## 🚀 Quick Start

### Installation

#### From PyPI (Recommended)
```bash
# Install the latest stable version from PyPI
pip install ssh-tools-suite
```

#### From Source
```bash
# Install from GitHub source
git clone https://github.com/NicholasKozma/ssh_tools_suite.git
cd ssh_tools_suite
pip install -e .
```

### Verify Installation
```bash
# Check if installation was successful
ssh-tunnel-manager --version
ssh-tools-installer --version
```

### Basic Usage

#### GUI Mode (Recommended)
```bash
# Start SSH Tunnel Manager GUI
ssh-tunnel-manager-gui

# Start Third-Party Installer GUI  
third-party-installer-gui
```

#### Command Line Mode
```bash
# SSH Tunnel Manager CLI
ssh-tunnel-manager --help

# Third-Party Installer CLI
third-party-installer --help
```

### Create Your First Tunnel

1. **Launch the GUI**: `ssh-tunnel-manager-gui`
2. **Add New Tunnel**: Click "Add Tunnel" button
3. **Configure Connection**:
   - **Name**: "Database Tunnel"
   - **SSH Host**: `jumpserver.example.com`
   - **Username**: Your SSH username
   - **Local Port**: `5432`
   - **Remote Host**: `database.internal`
   - **Remote Port**: `5432`
4. **Start Tunnel**: Click "Start" button
5. **Connect**: Use `localhost:5432` to access your database

## 📚 Documentation

- **[Full Documentation](https://nicholaskozma.github.io/ssh_tools_suite/)** - Complete guides and API reference
- **[Getting Started](docs/getting-started/installation.md)** - Installation and setup
- **[User Guides](docs/guides/creating-tunnels.md)** - Step-by-step tutorials  
- **[API Reference](docs/ssh-tunnel-manager/api-reference.md)** - Developer documentation
- **[Contributing](CONTRIBUTING.md)** - How to contribute to the project

## 🖼️ Screenshots

### SSH Tunnel Manager
![SSH Tunnel Manager Main Window](docs/assets/screenshots/main-window.png)
*Main tunnel management interface with real-time status monitoring*

### RTSP Video Streaming
![RTSP Viewer](docs/assets/screenshots/rtsp-viewer.png)
*Secure video streaming through SSH tunnels*

### Network Scanner
![Network Scanner](docs/assets/screenshots/network-scanner.png)
*Built-in network discovery and port scanning tools*

## 🛠️ Development

### Prerequisites

- **Python 3.8+**
- **Git**
- **Virtual Environment** (recommended)

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/NicholasKozma/ssh_tools_suite.git
cd ssh_tools_suite

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install development dependencies
pip install -e .[dev,gui,rtsp]
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest tests/gui/
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

### Documentation

```bash
# Serve documentation locally
mkdocs serve

# Build documentation
mkdocs build
```

## 📋 Requirements

### System Requirements
- **Operating System**: Windows 10/11, Linux, macOS
- **Python**: 3.8 or higher
- **Memory**: 512 MB RAM minimum
- **Storage**: 100 MB free space

### Dependencies
- **Core**: `paramiko`, `cryptography`, `psutil`
- **GUI**: `PySide6` (optional, for graphical interface)
- **RTSP**: `opencv-python` (optional, for video streaming)
- **Development**: `pytest`, `black`, `flake8`, `mypy`

## 🔧 Configuration

### Configuration Files

```
~/.ssh-tools-suite/
├── config.json          # Main configuration
├── tunnels.json          # Tunnel configurations  
├── logs/                 # Application logs
└── keys/                 # SSH keys storage
```

### Environment Variables

```bash
# Custom configuration directory
export SSH_TOOLS_CONFIG_DIR="/path/to/config"

# Enable debug logging
export SSH_TOOLS_DEBUG=1

# Default SSH key path
export SSH_TOOLS_DEFAULT_KEY="/path/to/key"
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Priorities

- Cross-platform compatibility improvements
- Performance optimizations  
- New tunnel types and protocols
- Enhanced GUI features
- Documentation and examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Paramiko](https://www.paramiko.org/)** - SSH implementation for Python
- **[PySide6](https://doc.qt.io/qtforpython/)** - Qt for Python GUI framework
- **[OpenCV](https://opencv.org/)** - Computer vision and video processing
- **[MkDocs](https://www.mkdocs.org/)** - Documentation generation

## 🐛 Issues and Support

- **Bug Reports**: [GitHub Issues](https://github.com/NicholasKozma/ssh_tools_suite/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/NicholasKozma/ssh_tools_suite/discussions)
- **Documentation**: [Full Documentation](https://nicholaskozma.github.io/ssh_tools_suite/)

## 🔗 Links

- **Homepage**: [https://ssh-tools-suite.github.io/](https://ssh-tools-suite.github.io/)
- **Documentation**: [https://nicholaskozma.github.io/ssh_tools_suite/](https://nicholaskozma.github.io/ssh_tools_suite/)
- **PyPI**: [https://pypi.org/project/ssh-tools-suite/](https://pypi.org/project/ssh-tools-suite/)

---

<div align="center">

**Made with ❤️ by the SSH Tools Suite Team**

[⭐ Star us on GitHub](https://github.com/NicholasKozma/ssh_tools_suite) • [📖 Read the Docs](https://nicholaskozma.github.io/ssh_tools_suite/) • [💬 Join Discussions](https://github.com/NicholasKozma/ssh_tools_suite/discussions)

</div>
