# Standalone Executable Installation

[![GitHub Release](https://img.shields.io/github/v/release/NicholasKozma/ssh_tools_suite)](https://github.com/NicholasKozma/ssh_tools_suite/releases)

For users who prefer not to install Python or want a portable solution, SSH Tools Suite provides standalone executables that require no additional dependencies.

## Download Options

Visit our [**GitHub Releases**](https://github.com/NicholasKozma/ssh_tools_suite/releases) page to download the latest version.

### Available Downloads

| Platform | File | Description |
|----------|------|-------------|
| Windows | `{{ download_filename() }}` | Main tunnel management application |
| Windows | `{{ download_filename("SSH-Tools-Installer") }}` | Third-party software installer |
| macOS | `SSH-Tools-Suite-v{{ pypi_version() }}.dmg` | Coming soon |
| Linux | `SSH-Tools-Suite-v{{ pypi_version() }}.AppImage` | Coming soon |

## Windows Installation

### Step-by-Step Installation

1. **Download the Archive**
   - Go to [GitHub Releases](https://github.com/NicholasKozma/ssh_tools_suite/releases)
   - Download `{{ download_filename() }}` for the main application
   - Or download `{{ download_filename("SSH-Tools-Installer") }}` for the installer tool

2. **Extract the Files**
   ```cmd
   # Extract to your preferred location
   # Example locations:
   C:\Tools\SSH-Tools\
   C:\Program Files\SSH-Tools\
   D:\Portable Apps\SSH-Tools\
   ```

3. **Run the Application**
   - Double-click `SSH-Tunnel-Manager.exe` to start the GUI
   - Or run from command line for CLI options

### Folder Structure

After extraction, you'll see this structure:

```
SSH-Tunnel-Manager/
├── SSH-Tunnel-Manager.exe          # Main executable
├── _internal/                      # Dependencies (do not modify)
│   ├── PySide6/
│   ├── opencv-python/
│   ├── paramiko/
│   └── ... (other dependencies)
└── assets/                         # Application resources
    ├── icons/
    └── themes/
```

!!! warning "Important"
    Keep all files together! The `_internal` folder contains required dependencies.

## Usage

### GUI Mode (Recommended)

Simply double-click the executable to start the graphical interface:

```cmd
# Start GUI application
SSH-Tunnel-Manager.exe
```

### Command Line Mode

The executable also supports command-line usage:

```cmd
# Show help and available options
SSH-Tunnel-Manager.exe --help

# List all configured tunnels
SSH-Tunnel-Manager.exe --list

# Start a specific tunnel
SSH-Tunnel-Manager.exe --start "My Tunnel"

# Run in console mode (show logs)
SSH-Tunnel-Manager.exe --console

# Start with specific configuration file
SSH-Tunnel-Manager.exe --config "path\to\config.json"
```

### Common Command Line Options

| Option | Description |
|--------|-------------|
| `--help` | Show all available options |
| `--version` | Display version information |
| `--list` | List all configured tunnels |
| `--start <name>` | Start a specific tunnel |
| `--stop <name>` | Stop a specific tunnel |
| `--console` | Show console output |
| `--config <path>` | Use specific configuration file |
| `--debug` | Enable debug logging |

## Advanced Usage

### Portable Installation

The executable is fully portable - copy the entire folder to any location:

```cmd
# Copy to USB drive for portable use
xcopy /E /I C:\Tools\SSH-Tools\ E:\PortableApps\SSH-Tools\

# Copy to network location for shared access
xcopy /E /I C:\Tools\SSH-Tools\ \\server\share\Tools\SSH-Tools\
```

### System Integration

#### Create Desktop Shortcut

1. Right-click on `SSH-Tunnel-Manager.exe`
2. Select "Create shortcut"
3. Move shortcut to Desktop
4. Rename to "SSH Tunnel Manager"

#### Add to System PATH

```cmd
# Add to system PATH for global access
setx PATH "%PATH%;C:\Tools\SSH-Tools\SSH-Tunnel-Manager"

# Now you can run from anywhere:
SSH-Tunnel-Manager.exe --help
```

#### Create Batch Scripts

Create convenient batch files for common tasks:

**start-database-tunnel.bat:**
```batch
@echo off
cd /d "C:\Tools\SSH-Tools\SSH-Tunnel-Manager"
SSH-Tunnel-Manager.exe --start "Database Tunnel"
pause
```

**ssh-tools-gui.bat:**
```batch
@echo off
cd /d "C:\Tools\SSH-Tools\SSH-Tunnel-Manager"
SSH-Tunnel-Manager.exe
```

## Performance

### Startup Time

| Installation Type | Startup Time | Notes |
|------------------|--------------|-------|
| Standalone Executable | 2-3 seconds | Fast startup, all dependencies bundled |
| PyPI Installation | 3-5 seconds | Depends on Python environment |
| Source Installation | 5-10 seconds | Development overhead |

### Memory Usage

- **Base Memory**: ~50-80 MB
- **With Active Tunnels**: ~100-150 MB
- **RTSP Streaming**: +50-100 MB per stream

## Troubleshooting

### Common Issues

#### "Application failed to start"

**Cause**: Missing Microsoft Visual C++ Redistributables

**Solution**:
```cmd
# Download and install VC++ Redistributables
# From: https://aka.ms/vs/17/release/vc_redist.x64.exe
```

#### "Permission denied" errors

**Cause**: Windows security restrictions

**Solution**:
1. Right-click executable → Properties
2. Check "Unblock" if present
3. Run as Administrator if needed

#### Slow startup

**Cause**: Antivirus scanning

**Solution**:
1. Add SSH-Tools folder to antivirus exclusions
2. Use Windows Defender exclusions:
   ```cmd
   # Add folder exclusion
   powershell Add-MpPreference -ExclusionPath "C:\Tools\SSH-Tools"
   ```

### Getting Help

If you encounter issues:

1. **Check Logs**: Enable `--debug` mode for detailed logs
2. **GitHub Issues**: Report bugs at [GitHub Issues](https://github.com/NicholasKozma/ssh_tools_suite/issues)
3. **Documentation**: Check the [full documentation](https://nicholaskozma.github.io/ssh_tools_suite/)

## Comparison: Executable vs PyPI

| Feature | Standalone Executable | PyPI Installation |
|---------|----------------------|-------------------|
| **Python Required** | ❌ No | ✅ Yes |
| **Startup Time** | ⚡ Fast (2-3s) | 🟡 Medium (3-5s) |
| **Portability** | ✅ Fully portable | ❌ Requires Python |
| **Updates** | 🔄 Manual download | 📦 `pip install --upgrade` |
| **Size** | 📦 ~200-300 MB | 💾 ~50-100 MB |
| **Best For** | End users, production | Developers, automation |

## Next Steps

After installation:

1. **[Quick Start Guide](quick-start.md)** - Create your first tunnel
2. **[Configuration Guide](../guides/managing-configurations.md)** - Advanced configuration
3. **[SSH Key Management](../guides/ssh-key-management.md)** - Set up SSH keys
4. **[RTSP Streaming](../guides/rtsp-streaming.md)** - Video streaming setup
