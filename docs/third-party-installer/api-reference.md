# Third Party Installer - API Reference

Quick reference for developers integrating with the Third Party Installer module.

## Core Classes

### ThirdPartyInstaller

Main class for managing third-party tool installations.

```python
from third_party_installer.core.installer import ThirdPartyInstaller

installer = ThirdPartyInstaller()
```

#### Methods

##### `get_tool_status(tool_name: str) -> InstallationStatus`
Check the installation status of a specific tool.

**Parameters:**
- `tool_name`: Name of the tool to check

**Returns:**
- `InstallationStatus` enum value

**Example:**
```python
status = installer.get_tool_status('psexec')
if status == InstallationStatus.INSTALLED:
    print("PsExec is available")
```

##### `download_tool(tool_name: str, progress_callback=None) -> Optional[Path]`
Download the installer for a specific tool.

**Parameters:**
- `tool_name`: Name of the tool to download
- `progress_callback`: Optional callback function for progress updates

**Returns:**
- `Path` object pointing to downloaded file, or `None` if failed

**Example:**
```python
def progress(percent, message):
    print(f"{percent}% - {message}")

installer_path = installer.download_tool('vlc', progress)
```

##### `install_tool(tool_name: str, progress_callback=None) -> bool`
Install a specific tool.

**Parameters:**
- `tool_name`: Name of the tool to install
- `progress_callback`: Optional callback function for progress updates

**Returns:**
- `True` if installation succeeded, `False` otherwise

**Example:**
```python
success = installer.install_tool('ffmpeg', progress)
if success:
    print("FFmpeg installed successfully")
```

##### `get_missing_required_tools() -> List[str]`
Get list of required tools that are not installed.

**Returns:**
- List of tool names that need installation

**Example:**
```python
missing = installer.get_missing_required_tools()
for tool in missing:
    print(f"Missing required tool: {tool}")
```

##### `is_installation_complete() -> bool`
Check if all required tools are installed.

**Returns:**
- `True` if all required tools are available

**Example:**
```python
if installer.is_installation_complete():
    print("All dependencies satisfied")
else:
    print("Some required tools are missing")
```

##### `get_all_tools_status() -> Dict[str, InstallationStatus]`
Get status of all configured tools.

**Returns:**
- Dictionary mapping tool names to their installation status

**Example:**
```python
status_dict = installer.get_all_tools_status()
for tool, status in status_dict.items():
    print(f"{tool}: {status.value}")
```

### ThirdPartyTool

Data class representing a tool configuration.

```python
from third_party_installer.core.installer import ThirdPartyTool

tool = ThirdPartyTool(
    name='my_tool',
    display_name='My Tool',
    description='Custom tool description',
    download_url='https://example.com/tool.exe',
    executable_paths=['C:\\Tools\\tool.exe'],
    version_command='tool.exe --version',
    installer_type='exe',
    required=False,
    dependencies=[]
)
```

#### Attributes

- `name: str` - Unique tool identifier
- `display_name: str` - Human-readable name
- `description: str` - Tool description
- `download_url: str` - Download source URL
- `executable_paths: List[str]` - Possible installation locations
- `version_command: Optional[str]` - Command to check version
- `installer_type: str` - Installation method ('msi', 'exe', 'zip', 'bundled')
- `required: bool` - Whether tool is mandatory
- `dependencies: List[str]` - List of required dependencies

### InstallationStatus

Enumeration of installation states.

```python
from third_party_installer.core.installer import InstallationStatus

# Possible values:
InstallationStatus.NOT_INSTALLED
InstallationStatus.INSTALLED
InstallationStatus.NEEDS_UPDATE
InstallationStatus.INSTALLATION_FAILED
```

## GUI Components

### ThirdPartyInstallerGUI

Main GUI window for tool installation management.

```python
from third_party_installer.gui.main_window import ThirdPartyInstallerGUI
from PySide6.QtWidgets import QApplication

app = QApplication([])
gui = ThirdPartyInstallerGUI()
gui.show()
app.exec()
```

#### Signals

- `installation_started` - Emitted when installation begins
- `installation_progress(tool_name, progress, message)` - Progress updates
- `installation_finished(tool_name, success, message)` - Installation completion
- `all_installations_finished(success)` - Batch installation completion

### InstallationWorker

Background worker for non-blocking installations.

```python
from third_party_installer.gui.main_window import InstallationWorker
from PySide6.QtCore import QThread

worker = InstallationWorker(['psexec', 'vlc'])
thread = QThread()
worker.moveToThread(thread)

# Connect signals
worker.progress_updated.connect(on_progress)
worker.installation_finished.connect(on_tool_finished)
worker.all_installations_finished.connect(on_all_finished)

thread.started.connect(worker.run)
thread.start()
```

## Configuration

### Proxy Configuration

```python
# Auto-detect system proxy
installer.proxy_config = {
    'enabled': True,
    'auto_detect': True
}

# Manual proxy configuration
installer.proxy_config = {
    'enabled': True,
    'auto_detect': False,
    'server': 'proxy.company.com',
    'port': 8080,
    'username': 'user',
    'password': 'pass'
}

# PX corporate proxy
installer.proxy_config = {
    'enabled': True,
    'use_px': True,
    'px_port': 3128
}
```

### Tool Configuration

```python
# Add custom tool
custom_tool = ThirdPartyTool(
    name='custom',
    display_name='Custom Tool',
    description='My custom tool',
    download_url='https://example.com/tool.zip',
    executable_paths=['C:\\CustomTool\\tool.exe'],
    installer_type='zip',
    required=False,
    dependencies=[]
)

installer.tools_config['custom'] = custom_tool
```

## Common Usage Patterns

### Check and Install Dependencies

```python
def ensure_dependencies():
    installer = ThirdPartyInstaller()
    
    # Check what's missing
    missing = installer.get_missing_required_tools()
    if not missing:
        return True
    
    # Install missing tools
    for tool_name in missing:
        print(f"Installing {tool_name}...")
        if not installer.install_tool(tool_name):
            print(f"Failed to install {tool_name}")
            return False
    
    return installer.is_installation_complete()
```

### Progress Monitoring

```python
def install_with_progress(tool_name):
    def progress_callback(percent, message):
        print(f"\r{tool_name}: {percent:3d}% - {message}", end='', flush=True)
    
    installer = ThirdPartyInstaller()
    success = installer.install_tool(tool_name, progress_callback)
    print()  # New line after progress
    return success
```

### Batch Installation

```python
def install_tools(tool_list):
    installer = ThirdPartyInstaller()
    results = {}
    
    for tool in tool_list:
        print(f"Installing {tool}...")
        results[tool] = installer.install_tool(tool)
    
    return results
```

### Status Report

```python
def print_status_report():
    installer = ThirdPartyInstaller()
    status_dict = installer.get_all_tools_status()
    
    print("Tool Installation Status:")
    print("-" * 40)
    
    for tool_name, status in status_dict.items():
        tool = installer.tools_config[tool_name]
        required = "Required" if tool.required else "Optional"
        print(f"{tool.display_name:20} [{required:8}] {status.value}")
```

### Error Handling

```python
def safe_install(tool_name):
    installer = ThirdPartyInstaller()
    
    try:
        # Check if tool exists in configuration
        if tool_name not in installer.tools_config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Check current status
        status = installer.get_tool_status(tool_name)
        if status == InstallationStatus.INSTALLED:
            print(f"{tool_name} is already installed")
            return True
        
        # Attempt installation
        success = installer.install_tool(tool_name)
        if success:
            print(f"Successfully installed {tool_name}")
        else:
            print(f"Failed to install {tool_name}")
        
        return success
        
    except Exception as e:
        print(f"Error installing {tool_name}: {e}")
        return False
```

## Environment Variables

The installer respects these environment variables:

- `HTTP_PROXY` / `HTTPS_PROXY` - Proxy server URLs
- `NO_PROXY` - Hosts to bypass proxy
- `TEMP` / `TMPDIR` - Temporary directory location
- `SSH_TOOLS_CONFIG_DIR` - Custom configuration directory

## File Locations

### Default Directories

- **Windows**: 
  - Config: `%APPDATA%\SSH_Tools_Suite\third_party_installer`
  - Temp: `%TEMP%\ssh_tools_installer`
- **Linux**: 
  - Config: `~/.config/ssh_tools_suite/third_party_installer`
  - Temp: `/tmp/ssh_tools_installer`
- **macOS**: 
  - Config: `~/Library/Application Support/SSH_Tools_Suite/third_party_installer`
  - Temp: `/tmp/ssh_tools_installer`

### Configuration Files

- `tools_config.json` - Tool definitions
- `proxy_config.json` - Proxy settings
- `installation_log.txt` - Installation history

## Exit Codes

When running as a standalone application:

- `0` - Success
- `1` - General failure
- `2` - Missing required arguments
- `3` - Network error
- `4` - Permission error
- `5` - Installation failed

## Integration Examples

### Flask Web Application

```python
from flask import Flask, jsonify
from third_party_installer.core.installer import ThirdPartyInstaller

app = Flask(__name__)
installer = ThirdPartyInstaller()

@app.route('/api/tools/status')
def get_tools_status():
    status = installer.get_all_tools_status()
    return jsonify({
        tool: status_val.value 
        for tool, status_val in status.items()
    })

@app.route('/api/tools/<tool_name>/install', methods=['POST'])
def install_tool(tool_name):
    try:
        success = installer.install_tool(tool_name)
        return jsonify({'success': success})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

### Command Line Interface

```python
import argparse
from third_party_installer.core.installer import ThirdPartyInstaller

def main():
    parser = argparse.ArgumentParser(description='Install third-party tools')
    parser.add_argument('--tool', help='Specific tool to install')
    parser.add_argument('--all', action='store_true', help='Install all required tools')
    parser.add_argument('--status', action='store_true', help='Show status of all tools')
    
    args = parser.parse_args()
    installer = ThirdPartyInstaller()
    
    if args.status:
        status = installer.get_all_tools_status()
        for tool, stat in status.items():
            print(f"{tool}: {stat.value}")
    
    elif args.tool:
        success = installer.install_tool(args.tool)
        exit(0 if success else 1)
    
    elif args.all:
        missing = installer.get_missing_required_tools()
        for tool in missing:
            installer.install_tool(tool)
        exit(0 if installer.is_installation_complete() else 1)

if __name__ == '__main__':
    main()
```

This API reference provides developers with quick access to the most commonly used classes, methods, and patterns for integrating the Third Party Installer into their applications.
