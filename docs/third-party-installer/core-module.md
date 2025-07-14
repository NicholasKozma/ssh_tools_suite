# Third Party Installer - Core Module Documentation

The Third Party Installer is a specialized module within the SSH Tools Suite responsible for automated installation and management of external dependencies required by the suite's applications.

## Module Purpose

The Third Party Installer module serves as a comprehensive dependency management system with the following responsibilities:

- **Automated Tool Installation**: Downloads and installs required third-party executables
- **Dependency Validation**: Verifies tool availability and installation status
- **Corporate Environment Support**: Handles proxy configurations and network restrictions
- **Cross-Platform Compatibility**: Manages installation differences across Windows/Linux/macOS
- **Progressive Installation**: Supports both required and optional tool installation
- **Installation Recovery**: Provides fallback mechanisms for failed installations

## Architecture Overview

The module follows a clean separation between core installation logic and user interface:

```
third_party_installer/
├── core/          # Core installation engine
│   └── installer.py
├── gui/           # User interface components
│   └── main_window.py
├── __init__.py    # Module exports
├── __main__.py    # CLI entry point
└── setup.py       # Post-installation setup
```

## Key Classes and Functions

### Core Classes

#### `ThirdPartyInstaller`
**Location**: `third_party_installer.core.installer.ThirdPartyInstaller`

The central class responsible for managing third-party tool installations.

**Key Attributes**:
- `config_dir: Path` - Configuration storage directory
- `temp_dir: Path` - Temporary download directory
- `tools_config: Dict[str, ThirdPartyTool]` - Available tools configuration
- `installation_status: Dict[str, InstallationStatus]` - Current tool status
- `proxy_config: Dict[str, Any]` - Corporate proxy settings

**Key Methods**:
- `get_tool_status(tool_name: str) -> InstallationStatus` - Check tool installation status
- `download_tool(tool_name: str, progress_callback=None) -> Optional[Path]` - Download tool installer
- `install_tool(tool_name: str, progress_callback=None) -> bool` - Install specific tool
- `is_installation_complete() -> bool` - Verify all required tools are installed
- `get_missing_required_tools() -> List[str]` - List uninstalled required tools

#### `ThirdPartyTool`
**Location**: `third_party_installer.core.installer.ThirdPartyTool`

Data class representing a third-party tool configuration.

**Key Attributes**:
- `name: str` - Tool identifier (e.g., "psexec", "vlc")
- `display_name: str` - Human-readable name
- `description: str` - Tool description and purpose
- `download_url: str` - Source URL for installer
- `executable_paths: List[str]` - Possible installation locations
- `version_command: Optional[str]` - Command to check version/existence
- `installer_type: str` - Installation method ("msi", "exe", "zip", "bundled")
- `required: bool` - Whether tool is mandatory
- `dependencies: List[str]` - Other tools this depends on

#### `InstallationStatus`
**Location**: `third_party_installer.core.installer.InstallationStatus`

Enumeration of possible installation states.

**Values**:
- `NOT_INSTALLED` - Tool is not present on system
- `INSTALLED` - Tool is properly installed and accessible
- `NEEDS_UPDATE` - Tool exists but may need updating
- `INSTALLATION_FAILED` - Previous installation attempt failed

#### `ThirdPartyInstallerGUI`
**Location**: `third_party_installer.gui.main_window.ThirdPartyInstallerGUI`

Professional GUI interface for managing tool installations.

**Key Components**:
- Tool status display with progress indicators
- Installation progress tracking
- Corporate proxy configuration
- Installation logging and error reporting
- Batch installation capabilities

#### `InstallationWorker`
**Location**: `third_party_installer.gui.main_window.InstallationWorker`

Background thread for non-blocking installation operations.

**Signals**:
- `progress_updated(tool_name, progress, message)` - Installation progress updates
- `installation_finished(tool_name, success, message)` - Single tool completion
- `all_installations_finished(success)` - Batch installation completion

## Inputs and Outputs

### Input Data Types

#### Tool Configuration Input
```python
{
    "name": "string",              # Tool identifier
    "display_name": "string",      # Human-readable name
    "description": "string",       # Tool description
    "download_url": "string",      # Download source URL
    "executable_paths": ["string"], # Installation locations to check
    "version_command": "string",   # Command to verify installation
    "installer_type": "string",    # "msi"|"exe"|"zip"|"bundled"
    "required": "bool",            # Mandatory installation flag
    "dependencies": ["string"]     # Other required tools
}
```

#### Proxy Configuration Input
```python
{
    "enabled": "bool",             # Proxy usage enabled
    "auto_detect": "bool",         # Use system proxy settings
    "use_px": "bool",              # Use PX corporate proxy tool
    "server": "string",            # Proxy server hostname
    "port": "int",                 # Proxy server port
    "username": "string",          # Proxy authentication username
    "password": "string",          # Proxy authentication password
    "px_port": "int"               # PX proxy port (default: 3128)
}
```

### Output Data Types

#### Installation Status Response
```python
{
    "tool_name": "string",         # Tool identifier
    "status": "InstallationStatus", # Current installation state
    "display_name": "string",      # Human-readable name
    "description": "string",       # Tool description
    "required": "bool",            # Whether tool is mandatory
    "executable_path": "string|None", # Located executable path
    "version": "string|None"       # Detected version (if available)
}
```

#### Installation Progress Callback
```python
def progress_callback(progress: int, message: str) -> None:
    """
    progress: 0-100 completion percentage
    message: Human-readable status message
    """
```

#### Installation Result
```python
{
    "success": "bool",             # Overall operation success
    "installed_tools": ["string"], # Successfully installed tools
    "failed_tools": ["string"],   # Tools that failed installation
    "error_messages": {"string": "string"}, # Error details per tool
    "installation_complete": "bool" # All required tools installed
}
```

## Dependencies

### External Libraries

#### Core Dependencies
- **urllib.request**: HTTP downloading with proxy support
- **subprocess**: External process execution for installers
- **zipfile**: ZIP archive extraction for portable tools
- **tempfile**: Temporary file management
- **json**: Configuration serialization
- **pathlib**: Cross-platform path handling

#### GUI Dependencies
- **PySide6**: Qt-based graphical interface
  - `QtWidgets`: UI components
  - `QtCore`: Threading and signals
  - `QtGui`: Graphics and styling

#### Platform-Specific Dependencies
- **Windows**: Built-in MSI and EXE installer support
- **Linux**: Package manager integration capabilities
- **macOS**: DMG and PKG installer support

### Internal Modules

#### Within Third Party Installer
- `third_party_installer.core.installer` - Core installation logic
- `third_party_installer.gui.main_window` - User interface
- `third_party_installer.setup` - Post-installation setup

#### SSH Tools Suite Integration
- `ssh_tools_common` - Shared utilities and constants
- Configuration sharing with main SSH Tunnel Manager

### System Dependencies

#### Required System Tools
- **Windows**: `msiexec`, `where` command, Windows Installer service
- **Linux**: `which`, `wget`/`curl`, package managers
- **macOS**: `which`, built-in installation frameworks

#### Network Requirements
- Internet connectivity for tool downloads
- Proxy server access (if applicable)
- Corporate network traversal capabilities

#### File System Permissions
- Write access to system directories (for system-wide installation)
- Write access to user directories (for fallback installation)
- Temporary directory access for downloads

## Key Logic and Algorithms

### Tool Detection Algorithm

The installer uses a multi-stage detection process:

```python
def _check_tool_status(self, tool: ThirdPartyTool) -> InstallationStatus:
    """
    1. Check predefined installation paths
    2. Query system PATH using 'where'/'which' commands
    3. Attempt version command execution
    4. Return most accurate status
    """
```

**Detection Strategy**:
1. **Direct Path Check**: Verify tool exists at expected installation locations
2. **PATH Search**: Use system commands to locate tool in PATH
3. **Version Verification**: Execute version command to confirm functionality
4. **Status Resolution**: Return most specific status based on findings

### Installation Process Algorithm

```python
def install_tool(self, tool_name: str, progress_callback=None) -> bool:
    """
    Multi-phase installation process:
    1. Tool validation and prerequisite checks
    2. Download phase with progress tracking
    3. Installation execution based on installer type
    4. Post-installation verification
    5. Status update and logging
    """
```

**Installation Flow**:
1. **Pre-Installation Validation**:
   - Verify tool configuration exists
   - Check if tool is already installed
   - Validate system requirements

2. **Download Phase**:
   - Configure proxy settings if needed
   - Download installer with progress tracking
   - Verify download integrity

3. **Installation Execution**:
   - **MSI**: Silent installation via `msiexec`
   - **EXE**: Silent installation with appropriate flags
   - **ZIP**: Extraction to target directories with permission handling
   - **Bundled**: Verification of pre-packaged tools

4. **Post-Installation**:
   - Verify installation success
   - Update internal status tracking
   - Save installation records
   - Clean up temporary files

### Proxy Configuration Algorithm

```python
def _configure_proxy(self):
    """
    Corporate proxy handling:
    1. Auto-detection of system proxy settings
    2. PX proxy tool integration
    3. Manual proxy configuration
    4. Authentication handling
    """
```

**Proxy Resolution Strategy**:
1. **Auto-Detection**: Use system proxy settings when available
2. **PX Integration**: Leverage PX tool for corporate proxy authentication
3. **Manual Configuration**: Support explicit proxy server settings
4. **Authentication**: Handle username/password authentication

### Error Handling and Recovery

**Robust Error Handling**:
```python
def robust_installation_strategy(self, tool: ThirdPartyTool) -> bool:
    """
    1. Primary installation attempt
    2. Permission-based fallback (user vs system directories)
    3. Alternative download sources
    4. Manual installation guidance
    """
```

**Recovery Mechanisms**:
- **Permission Fallbacks**: Install to user directory if system installation fails
- **Alternative Sources**: Try different download URLs if available
- **Partial Installation**: Handle tools with multiple components
- **Manual Guidance**: Provide user instructions for manual installation

## Usage Examples

### Basic Tool Installation

```python
from third_party_installer.core.installer import ThirdPartyInstaller

# Initialize installer
installer = ThirdPartyInstaller()

# Check current installation status
status = installer.get_tool_status('psexec')
print(f"PsExec status: {status}")

# Install a specific tool
def progress_callback(progress: int, message: str):
    print(f"Progress: {progress}% - {message}")

success = installer.install_tool('psexec', progress_callback)
if success:
    print("PsExec installed successfully!")
else:
    print("Installation failed")
```

### Batch Installation

```python
# Check which required tools are missing
missing_tools = installer.get_missing_required_tools()
print(f"Missing required tools: {missing_tools}")

# Install all missing required tools
for tool_name in missing_tools:
    print(f"Installing {tool_name}...")
    success = installer.install_tool(tool_name, progress_callback)
    if not success:
        print(f"Failed to install {tool_name}")

# Verify installation completion
if installer.is_installation_complete():
    print("All required tools are now installed!")
```

### Custom Tool Configuration

```python
from third_party_installer.core.installer import ThirdPartyTool

# Define a custom tool
custom_tool = ThirdPartyTool(
    name='custom_app',
    display_name='Custom Application',
    description='Custom tool for SSH operations',
    download_url='https://example.com/tool.zip',
    executable_paths=[
        'C:\\Program Files\\CustomApp\\app.exe',
        'C:\\CustomApp\\app.exe'
    ],
    version_command='app.exe --version',
    installer_type='zip',
    required=False,
    dependencies=['psexec']
)

# Add to installer configuration
installer.tools_config['custom_app'] = custom_tool
installer._check_all_tools_status()
```

### Proxy Configuration

```python
# Configure proxy settings
installer.proxy_config = {
    'enabled': True,
    'auto_detect': False,
    'use_px': True,
    'px_port': 3128
}

# Configure manual proxy
installer.proxy_config = {
    'enabled': True,
    'auto_detect': False,
    'server': 'proxy.company.com',
    'port': 8080,
    'username': 'user',
    'password': 'pass'
}

# Install tool with proxy
success = installer.install_tool('vlc', progress_callback)
```

### GUI Integration

```python
from third_party_installer.gui.main_window import ThirdPartyInstallerGUI
from PySide6.QtWidgets import QApplication

# Create GUI application
app = QApplication([])
installer_gui = ThirdPartyInstallerGUI()

# Show installer window
installer_gui.show()

# Run event loop
app.exec()
```

### Installation Status Monitoring

```python
# Get comprehensive status of all tools
all_status = installer.get_all_tools_status()

for tool_name, status in all_status.items():
    tool = installer.tools_config[tool_name]
    print(f"{tool.display_name}: {status.value}")
    
    if status == InstallationStatus.NOT_INSTALLED and tool.required:
        print(f"  ⚠️  Required tool not installed!")
    elif status == InstallationStatus.INSTALLED:
        print(f"  ✅ Tool is available")

# Check specific tool executable location
for exe_path in installer.tools_config['psexec'].executable_paths:
    if Path(exe_path).exists():
        print(f"PsExec found at: {exe_path}")
        break
```

### Error Handling

```python
try:
    success = installer.install_tool('nonexistent_tool')
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"Installation error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Clean up temporary files
    installer.cleanup()
```

## Potential Edge Cases and Limitations

### Known Limitations

#### Platform-Specific Constraints
- **Windows**: Requires administrator privileges for system directory installation
- **Corporate Networks**: May require proxy authentication or certificate installation
- **Linux Package Managers**: Different distributions require different handling
- **macOS Security**: Gatekeeper may block unsigned applications

#### Network Dependencies
- **Internet Connectivity**: Required for downloading tools from external sources
- **Download Reliability**: Large files may fail on unstable connections
- **Corporate Firewalls**: May block access to download sources
- **Bandwidth Limitations**: Large downloads may be slow or timeout

#### Storage and Permissions
- **Disk Space**: Requires sufficient space for downloads and installation
- **File Permissions**: May fail if target directories are read-only
- **Antivirus Interference**: Security software may quarantine downloaded files
- **Path Length Limits**: Windows path length restrictions may cause issues

### Edge Cases to Consider

#### Installation Conflicts
```python
# Example: Tool already installed in different location
if installer.get_tool_status('vlc') == InstallationStatus.INSTALLED:
    # VLC may be installed in non-standard location
    # Installer might not detect it properly
    for path in installer.tools_config['vlc'].executable_paths:
        if Path(path).exists():
            print(f"VLC detected at: {path}")
            break
    else:
        # Tool exists but not in expected locations
        print("VLC may be installed in a custom location")
```

#### Download Failures
```python
# Handle network issues during download
max_retries = 3
for attempt in range(max_retries):
    try:
        installer_path = installer.download_tool('ffmpeg', progress_callback)
        break
    except RuntimeError as e:
        if attempt == max_retries - 1:
            print(f"Download failed after {max_retries} attempts: {e}")
            # Provide manual download instructions
            tool = installer.tools_config['ffmpeg']
            print(f"Please download manually from: {tool.download_url}")
        else:
            print(f"Download attempt {attempt + 1} failed, retrying...")
            time.sleep(2 ** attempt)  # Exponential backoff
```

#### Permission Escalation
```python
# Handle cases where elevation is required
try:
    success = installer.install_tool('psexec')
    if not success:
        # May need administrator privileges
        print("Installation may require administrator privileges")
        print("Please run as administrator or install manually")
except PermissionError:
    print("Insufficient permissions for installation")
    print("Attempting fallback to user directory...")
```

#### Proxy Authentication
```python
# Handle complex proxy scenarios
if installer.proxy_config.get('enabled') and not installer.proxy_config.get('use_px'):
    # Manual proxy configuration
    if not installer.proxy_config.get('username'):
        print("Proxy requires authentication but no credentials provided")
        # Could prompt user for credentials in GUI
```

#### Tool Version Conflicts
```python
# Handle cases where tool version is incompatible
def check_tool_compatibility(tool_name: str) -> bool:
    """Check if installed tool version is compatible"""
    if installer.get_tool_status(tool_name) == InstallationStatus.INSTALLED:
        # Could check version and compare with requirements
        version_cmd = installer.tools_config[tool_name].version_command
        if version_cmd:
            try:
                result = subprocess.run(version_cmd.split(), 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Parse version from output
                    version_output = result.stdout
                    # Compare with minimum required version
                    return True  # Simplified check
            except Exception:
                pass
    return False
```

### Performance Considerations

#### Resource Management
- **Memory Usage**: Large downloads consume significant RAM during installation
- **CPU Usage**: ZIP extraction and MSI installation can be CPU-intensive
- **Disk I/O**: Concurrent installations may cause disk bottlenecks
- **Network Bandwidth**: Multiple simultaneous downloads may saturate connection

#### Scalability Limits
- **Concurrent Installations**: Avoid installing multiple tools simultaneously
- **Temporary Storage**: Clean up downloads to prevent disk space exhaustion
- **Process Limits**: System may limit number of concurrent installer processes

### Security Considerations

#### Download Security
- **HTTPS Verification**: Ensure downloads use secure connections
- **Checksum Validation**: Verify file integrity after download
- **Digital Signatures**: Check tool signatures when available
- **Sandbox Execution**: Consider running installers in isolated environment

#### Permission Management
- **Principle of Least Privilege**: Install tools with minimum required permissions
- **User vs System Installation**: Prefer user-level installation when possible
- **Path Injection**: Validate installation paths to prevent security issues

#### Corporate Compliance
- **Approved Software Lists**: Verify tools comply with corporate policies
- **License Compliance**: Ensure tool licenses are compatible
- **Audit Logging**: Maintain records of installed tools and versions

This comprehensive documentation provides developers with the essential knowledge needed to work with or integrate the Third Party Installer module effectively. The module's robust design handles complex corporate environments while maintaining simplicity for basic use cases.
