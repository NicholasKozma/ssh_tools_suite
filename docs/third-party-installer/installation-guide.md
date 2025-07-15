# Third Party Installer - Installation Guide

This guide covers installing and configuring the Third Party Installer for automated management of SSH Tools Suite dependencies.

## Overview

The Third Party Installer is automatically included with the SSH Tools Suite and is typically invoked during first-time setup. However, it can also be run independently to manage tool installations.

## Automatic Installation

### During SSH Tools Suite Setup

The Third Party Installer is automatically triggered when:

1. **First Launch**: SSH Tools Suite detects missing required tools
2. **Post-Installation**: Runs automatically after package installation
3. **Dependency Check**: When applications require missing tools

```bash
# SSH Tools Suite automatically runs:
python -m third_party_installer
```

### Silent Installation Mode

For automated deployments:

```bash
# Install all required tools silently
python -m third_party_installer --silent --required-only

# Install all tools (required + optional)
python -m third_party_installer --silent --all
```

## Manual Installation

### Launching the GUI

```bash
# Method 1: Using the installed script
third-party-installer

# Method 2: Using Python module
python -m third_party_installer

# Method 3: Direct execution (if in source directory)
python third_party_installer_app.py
```

### Command Line Interface

```bash
# Check installation status
python -m third_party_installer --status

# List available tools
python -m third_party_installer --list

# Install specific tool
python -m third_party_installer --install psexec

# Install all required tools
python -m third_party_installer --install-required
```

## Corporate Environment Setup

### Proxy Configuration

#### Automatic Proxy Detection

The installer can automatically detect and use system proxy settings:

1. **Launch Third Party Installer**
2. **Click "Proxy Settings"**
3. **Select "Auto-detect system proxy"**
4. **Test connection and save**

#### Manual Proxy Configuration

For explicit proxy server configuration:

```json
{
    "enabled": true,
    "auto_detect": false,
    "server": "proxy.company.com",
    "port": 8080,
    "username": "your_username",
    "password": "your_password"
}
```

#### PX Corporate Proxy

For environments using PX authentication:

1. **Ensure PX is installed** (bundled with SSH Tools Suite)
2. **Configure PX settings** in the installer
3. **Set proxy to use PX**: `localhost:3128`
4. **Test installation** with proxy

```bash
# Configure PX proxy
px --config
# Start PX service
px --daemon
```

### Network Restrictions

#### Firewall Configuration

Allow outbound HTTPS connections to:
- `download.sysinternals.com` (PsExec)
- `get.videolan.org` (VLC)
- `www.gyan.dev` (FFmpeg)
- `github.com` (PX updates)

#### Alternative Download Methods

If direct downloads are blocked:

1. **Manual Download**: Download tools manually and place in designated directories
2. **Network Share**: Configure installer to use internal file shares
3. **Offline Installation**: Use pre-downloaded installation packages

## Tool-Specific Installation

### PsExec (Required)

**Installation Process**:
1. Downloads PSTools.zip from Microsoft Sysinternals
2. Extracts PsExec.exe to system directory
3. Falls back to user directory if permissions insufficient
4. Verifies installation by checking executable

**Manual Installation**:
```bash
# Download PSTools manually
# Extract PsExec.exe to one of:
# C:\Windows\System32\PsExec.exe
# C:\PsExec\PsExec.exe
```

**Verification**:
```cmd
PsExec.exe
# Should display PsExec help information
```

### VLC Media Player (Optional)

**Installation Process**:
1. Downloads VLC installer from VideoLAN
2. Runs silent installation
3. Configures for RTSP streaming
4. Adds to system PATH if needed

**Manual Installation**:
```bash
# Download VLC from https://www.videolan.org/
# Install normally, ensuring installation to standard directory
```

**Verification**:
```cmd
vlc.exe --version
# Should display VLC version information
```

### FFmpeg (Required)

**Installation Process**:
1. Downloads FFmpeg essentials build
2. Extracts to dedicated directory
3. Configures PATH environment variable
4. Verifies installation with version check

**Manual Installation**:
```bash
# Download FFmpeg from https://ffmpeg.org/
# Extract to C:\ffmpeg\
# Add C:\ffmpeg\bin to PATH
```

**Verification**:
```cmd
ffmpeg -version
# Should display FFmpeg version and configuration
```

### PX Corporate Proxy (Bundled)

**Installation Process**:
1. Verifies bundled PX executable
2. Configures proxy settings
3. Creates service configuration
4. Tests proxy connectivity

**Manual Configuration**:
```bash
# Configure PX settings
px --config

# Set proxy server
px --server=proxy.company.com:8080

# Start PX daemon
px --daemon
```

## Installation Verification

### Automated Verification

The installer automatically verifies all installations:

```python
from third_party_installer.core.installer import ThirdPartyInstaller

installer = ThirdPartyInstaller()

# Check all tool status
all_status = installer.get_all_tools_status()
for tool_name, status in all_status.items():
    print(f"{tool_name}: {status.value}")

# Check if installation is complete
if installer.is_installation_complete():
    print("✅ All required tools are installed!")
else:
    missing = installer.get_missing_required_tools()
    print(f"❌ Missing tools: {', '.join(missing)}")
```

### Manual Verification

#### Check Tool Availability

```bash
# Test PsExec
PsExec.exe
where PsExec.exe

# Test VLC
vlc.exe --version
where vlc.exe

# Test FFmpeg
ffmpeg -version
where ffmpeg.exe

# Test PX
px.exe --version
where px.exe
```

#### Verify Installation Paths

**Windows Registry Check**:
```cmd
# Check VLC installation
reg query "HKLM\SOFTWARE\VideoLAN\VLC"

# Check installed programs
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
```

**Directory Structure Verification**:
```
C:\Windows\System32\PsExec.exe           (or C:\PsExec\)
C:\Program Files\VideoLAN\VLC\vlc.exe   (or x86)
C:\ffmpeg\bin\ffmpeg.exe
C:\px\px.exe                            (or bundled location)
```

## Troubleshooting Installation Issues

### Common Issues

#### "Administrator Privileges Required"

**Solution**: Run installer as administrator or use fallback installation:

```bash
# Run as administrator
runas /user:Administrator "python -m third_party_installer"

# Or allow fallback to user directory installation
# Installer automatically handles this for most tools
```

#### "Download Failed" / "Network Error"

**Solution**: Check network connectivity and proxy settings:

```bash
# Test internet connectivity
ping 8.8.8.8

# Test HTTPS access
curl -I https://download.sysinternals.com

# Configure proxy if needed
python -m third_party_installer --configure-proxy
```

#### "Antivirus Software Blocking Installation"

**Solution**: Temporarily disable antivirus or add exceptions:

1. **Add SSH Tools Suite directory** to antivirus exceptions
2. **Allow downloads** from known sources
3. **Disable real-time scanning** temporarily during installation
4. **Manually verify** downloaded files if needed

#### "Installation Hangs"

**Solution**: Check for conflicting processes:

```bash
# Check for running installers
tasklist | findstr msiexec

# Kill hanging processes
taskkill /F /IM msiexec.exe

# Restart installer
python -m third_party_installer
```

### Advanced Troubleshooting

#### Enable Debug Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run installer with debug output
from third_party_installer.core.installer import ThirdPartyInstaller
installer = ThirdPartyInstaller()
```

#### Manual Tool Verification

```python
from pathlib import Path
from third_party_installer.core.installer import ThirdPartyInstaller

installer = ThirdPartyInstaller()

# Check each tool manually
for tool_name, tool in installer.tools_config.items():
    print(f"\nChecking {tool.display_name}:")
    
    # Check expected paths
    for path in tool.executable_paths:
        if Path(path).exists():
            print(f"  ✅ Found at: {path}")
            break
    else:
        print(f"  ❌ Not found in expected locations")
        
    # Try version command
    if tool.version_command:
        try:
            import subprocess
            result = subprocess.run(
                tool.version_command.split(),
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✅ Version check passed")
            else:
                print(f"  ❌ Version check failed")
        except Exception as e:
            print(f"  ❌ Version check error: {e}")
```

#### Reset Installation State

```bash
# Clear installation cache
rm -rf %APPDATA%\SSH_Tools_Suite\ThirdPartyInstaller

# Or on Unix-like systems
rm -rf ~/.config/ssh_tools_suite/third_party_installer

# Restart installer
python -m third_party_installer
```

## Post-Installation Configuration

### Environment Variables

After successful installation, verify environment variables:

```bash
# Check PATH includes tool directories
echo %PATH%

# Add missing directories if needed
setx PATH "%PATH%;C:\ffmpeg\bin"
```

### Integration Verification

Test integration with SSH Tools Suite:

```bash
# Launch SSH Tunnel Manager
ssh-tunnel-manager-gui

# Check tool availability in application
# Tools should be detected automatically
```

### Corporate Deployment

#### Batch Installation Script

```batch
@echo off
echo Installing SSH Tools Suite Third Party Tools...

REM Install SSH Tools Suite
{{ pip_install_cmd() }}

REM Run third party installer silently
python -m third_party_installer --silent --required-only

REM Verify installation
python -c "from third_party_installer.core.installer import ThirdPartyInstaller; print('Complete' if ThirdPartyInstaller().is_installation_complete() else 'Failed')"

echo Installation complete!
pause
```

#### Group Policy Deployment

For domain environments:

1. **Create installation package** with all dependencies
2. **Deploy via Group Policy** Software Installation
3. **Use silent installation flags** for automated deployment
4. **Verify installation** through login scripts

## Uninstallation

### Remove Third Party Tools

```bash
# Uninstall VLC (if installed via installer)
"%ProgramFiles%\VideoLAN\VLC\uninstall.exe"

# Remove FFmpeg directory
rmdir /S C:\ffmpeg

# Remove PsExec (if installed to system)
del C:\Windows\System32\PsExec.exe

# Remove PX
rmdir /S C:\px
```

### Clean Installation Records

```bash
# Remove installer configuration
rmdir /S "%APPDATA%\SSH_Tools_Suite\ThirdPartyInstaller"

# Clear environment variables
# Remove added PATH entries manually through System Properties
```

## Next Steps

After successful installation:

1. **[Launch SSH Tunnel Manager](../getting-started/quick-start.md)** - Start using the main application
2. **[Configure Tunnels](../guides/creating-tunnels.md)** - Set up your first SSH tunnels
3. **[RTSP Streaming Setup](../guides/rtsp-streaming.md)** - Configure video streaming with installed tools

## Getting Help

If you encounter issues during installation:

1. **Check installation logs** in the GUI log panel
2. **Review error messages** for specific failure details
3. **Consult troubleshooting section** above
4. **Report issues** on [GitHub Issues](https://github.com/NicholasKozma/ssh_tools_suite/issues) with:
   - Operating system and version
   - Error messages and logs
   - Network environment details
   - Corporate proxy information (if applicable)
