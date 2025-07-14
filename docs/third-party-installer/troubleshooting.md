# Third Party Installer - Troubleshooting Guide

Common issues and solutions when working with the Third Party Installer module.

## Common Issues

### Installation Failures

#### Issue: "Permission denied" errors during installation

**Symptoms:**
- Installation fails with permission errors
- MSI/EXE installers fail to run
- Cannot write to Program Files directory

**Solutions:**

1. **Run as Administrator** (Windows):
```powershell
# Run PowerShell as Administrator
Start-Process powershell -Verb RunAs
cd "C:\Path\To\SSH_Tools_Suite"
python -m third_party_installer
```

2. **Use user-level installation**:
```python
from third_party_installer.core.installer import ThirdPartyInstaller

installer = ThirdPartyInstaller()
# This will attempt user directory installation as fallback
installer.install_tool('vlc')
```

3. **Check and modify permissions**:
```powershell
# Check current permissions
icacls "C:\Program Files"

# Grant write permissions to user (if you have admin rights)
icacls "C:\Program Files\MyApp" /grant Users:F
```

#### Issue: "Network connection failed" during download

**Symptoms:**
- Download timeouts
- "Unable to connect" errors
- Proxy authentication failures

**Solutions:**

1. **Check internet connectivity**:
```bash
# Test basic connectivity
ping google.com

# Test HTTPS connectivity
curl -I https://github.com
```

2. **Configure proxy settings**:
```python
installer = ThirdPartyInstaller()

# Auto-detect proxy
installer.proxy_config = {
    'enabled': True,
    'auto_detect': True
}

# Or manual configuration
installer.proxy_config = {
    'enabled': True,
    'server': 'proxy.company.com',
    'port': 8080,
    'username': 'your_username',
    'password': 'your_password'
}
```

3. **Use PX for corporate proxies**:
```python
# First install PX
installer.install_tool('px')

# Then configure PX proxy
installer.proxy_config = {
    'enabled': True,
    'use_px': True,
    'px_port': 3128
}
```

#### Issue: "Tool not found after installation"

**Symptoms:**
- Installation appears successful
- Tool status shows "NOT_INSTALLED"
- Executable not found in expected locations

**Solutions:**

1. **Check all possible locations**:
```python
installer = ThirdPartyInstaller()
tool = installer.tools_config['vlc']

for path in tool.executable_paths:
    if Path(path).exists():
        print(f"Found at: {path}")
        break
else:
    print("Tool not found in any expected location")
```

2. **Search system PATH**:
```python
import shutil

# Use system 'where' command (Windows) or 'which' (Unix)
vlc_path = shutil.which('vlc')
if vlc_path:
    print(f"VLC found in PATH: {vlc_path}")
else:
    print("VLC not found in system PATH")
```

3. **Manual verification**:
```python
import subprocess

try:
    result = subprocess.run(['vlc', '--version'], 
                          capture_output=True, text=True, timeout=5)
    if result.returncode == 0:
        print("VLC is functional")
        print(result.stdout)
    else:
        print("VLC installed but not working properly")
except FileNotFoundError:
    print("VLC executable not found")
except subprocess.TimeoutExpired:
    print("VLC command timed out")
```

### Corporate Environment Issues

#### Issue: Corporate firewall blocking downloads

**Symptoms:**
- Downloads fail with SSL/TLS errors
- Specific URLs are blocked
- Certificate verification failures

**Solutions:**

1. **Use internal mirror URLs**:
```python
# Configure custom download URLs for corporate environment
custom_tool = installer.tools_config['vlc']
custom_tool.download_url = 'https://internal-mirror.company.com/software/vlc.exe'
```

2. **Disable SSL verification** (temporary workaround):
```python
import ssl
import urllib.request

# Create custom SSL context (use with caution)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Apply to urllib requests
urllib.request.install_opener(
    urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl_context)
    )
)
```

3. **Use certificate bundle**:
```python
import certifi
import ssl

# Use certifi certificate bundle
ssl_context = ssl.create_default_context(cafile=certifi.where())
```

#### Issue: PX proxy authentication problems

**Symptoms:**
- PX tool fails to start
- Authentication timeouts
- "Access denied" from proxy

**Solutions:**

1. **Verify PX configuration**:
```python
# Check if PX is properly installed and configured
px_config = Path.home() / '.px' / 'px.ini'
if px_config.exists():
    with open(px_config) as f:
        print(f.read())
else:
    print("PX configuration not found")
```

2. **Manual PX setup**:
```ini
# Create px.ini file manually
[proxy]
server = proxy.company.com
port = 8080
username = your_domain_username
# password will be prompted

[settings]
port = 3128
workers = 2
```

3. **Test PX connectivity**:
```python
import subprocess
import time

# Start PX in background
px_process = subprocess.Popen(['px', '--debug'])
time.sleep(2)  # Wait for startup

# Test proxy connection
test_cmd = ['curl', '-x', 'localhost:3128', 'https://httpbin.org/ip']
result = subprocess.run(test_cmd, capture_output=True, text=True)

px_process.terminate()

if result.returncode == 0:
    print("PX proxy working correctly")
    print(result.stdout)
else:
    print("PX proxy test failed")
    print(result.stderr)
```

### Tool-Specific Issues

#### Issue: VLC installation fails on Windows

**Common causes:**
- Windows Store version conflicts
- Existing installation in non-standard location
- Corrupted download

**Solutions:**

1. **Remove existing VLC installations**:
```powershell
# Check for existing VLC installations
Get-WmiObject -Class Win32_Product | Where-Object {$_.Name -like "*VLC*"}

# Uninstall via Control Panel or PowerShell
# Then retry installation
```

2. **Use portable version**:
```python
# Configure VLC as portable installation
vlc_tool = installer.tools_config['vlc']
vlc_tool.installer_type = 'zip'
vlc_tool.download_url = 'https://download.videolan.org/vlc/last/win64/vlc-x.x.x-win64.zip'
```

#### Issue: FFmpeg extraction fails

**Common causes:**
- ZIP file corruption
- Insufficient disk space
- Path length limitations on Windows

**Solutions:**

1. **Verify download integrity**:
```python
import hashlib

def verify_download(file_path, expected_hash=None):
    """Verify downloaded file integrity"""
    if not Path(file_path).exists():
        return False
    
    # Calculate file hash
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    
    file_hash = sha256_hash.hexdigest()
    print(f"File hash: {file_hash}")
    
    if expected_hash:
        return file_hash == expected_hash
    return True
```

2. **Use shorter extraction path**:
```python
# Configure shorter extraction path for Windows
import tempfile

installer.temp_dir = Path(tempfile.gettempdir()) / 'ssh_tools'
installer.temp_dir.mkdir(exist_ok=True)
```

#### Issue: PsExec installation blocked by antivirus

**Common causes:**
- Antivirus false positives
- Corporate security policies
- Download from untrusted source

**Solutions:**

1. **Download from Microsoft directly**:
```python
# Verify PsExec download URL is from Microsoft
psexec_tool = installer.tools_config['psexec']
print(f"Download URL: {psexec_tool.download_url}")

# Should be: https://download.sysinternals.com/files/PSTools.zip
```

2. **Add antivirus exclusions**:
```powershell
# Add Windows Defender exclusion (requires admin)
Add-MpPreference -ExclusionPath "C:\Program Files\SSH_Tools_Suite"
Add-MpPreference -ExclusionProcess "psexec.exe"
```

3. **Manual installation**:
```python
# Provide manual installation instructions
def manual_psexec_install():
    print("Manual PsExec installation:")
    print("1. Download PSTools.zip from https://docs.microsoft.com/sysinternals/downloads/pstools")
    print("2. Extract psexec.exe to C:\\Windows\\System32\\")
    print("3. Or add psexec.exe location to system PATH")
```

## Debugging Tools

### Comprehensive Diagnostic Script

```python
import sys
import platform
import subprocess
import urllib.request
from pathlib import Path

def run_diagnostics():
    """Run comprehensive diagnostics for installation issues"""
    
    print("=== SSH Tools Suite Third Party Installer Diagnostics ===\n")
    
    # System Information
    print("System Information:")
    print(f"  OS: {platform.system()} {platform.release()}")
    print(f"  Python: {sys.version}")
    print(f"  Architecture: {platform.machine()}")
    print()
    
    # Network Connectivity
    print("Network Connectivity:")
    test_urls = [
        'https://github.com',
        'https://download.videolan.org',
        'https://download.sysinternals.com',
        'https://ffmpeg.org'
    ]
    
    for url in test_urls:
        try:
            with urllib.request.urlopen(url, timeout=5) as response:
                status = "✓ OK" if response.getcode() == 200 else f"✗ {response.getcode()}"
        except Exception as e:
            status = f"✗ {str(e)[:50]}"
        print(f"  {url}: {status}")
    print()
    
    # Disk Space
    import shutil
    try:
        total, used, free = shutil.disk_usage('/')
        free_gb = free / (1024**3)
        print(f"Disk Space: {free_gb:.1f} GB available")
    except:
        print("Disk Space: Unable to check")
    print()
    
    # Permissions
    print("Permissions:")
    test_dirs = []
    
    if platform.system() == 'Windows':
        test_dirs = [
            'C:\\Program Files',
            'C:\\Windows\\System32',
            Path.home() / 'AppData' / 'Local'
        ]
    else:
        test_dirs = [
            '/usr/local/bin',
            '/opt',
            Path.home() / '.local' / 'bin'
        ]
    
    for test_dir in test_dirs:
        try:
            test_file = Path(test_dir) / '.installer_test'
            test_file.touch()
            test_file.unlink()
            status = "✓ Writable"
        except PermissionError:
            status = "✗ No write access"
        except FileNotFoundError:
            status = "✗ Directory not found"
        except Exception as e:
            status = f"✗ {str(e)[:30]}"
        
        print(f"  {test_dir}: {status}")
    print()
    
    # Tool Detection
    print("Tool Detection:")
    from third_party_installer.core.installer import ThirdPartyInstaller
    
    installer = ThirdPartyInstaller()
    for tool_name, tool in installer.tools_config.items():
        status = installer.get_tool_status(tool_name)
        print(f"  {tool.display_name}: {status.value}")
    print()
    
    # Proxy Detection
    print("Proxy Configuration:")
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                          r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            proxy_enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
            if proxy_enabled:
                proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
                print(f"  System Proxy: {proxy_server}")
            else:
                print("  System Proxy: Disabled")
    except:
        print("  System Proxy: Unable to detect")
    
    # Environment variables
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"  {var}: {value}")

if __name__ == '__main__':
    run_diagnostics()
```

### Log Analysis Script

```python
import re
from pathlib import Path
from datetime import datetime

def analyze_installation_logs():
    """Analyze installation logs for common error patterns"""
    
    log_dir = Path.home() / '.ssh_tools_suite' / 'logs'
    if not log_dir.exists():
        print("No log directory found")
        return
    
    # Common error patterns
    error_patterns = {
        'permission_denied': r'Permission denied|Access is denied',
        'network_error': r'Network is unreachable|Connection timed out|Name resolution failed',
        'download_failed': r'Download failed|HTTP Error|SSL Error',
        'installation_failed': r'Installation failed|Exit code [^0]',
        'tool_not_found': r'not found|No such file'
    }
    
    print("=== Log Analysis ===\n")
    
    for log_file in log_dir.glob('*.log'):
        print(f"Analyzing {log_file.name}:")
        
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Count error patterns
            for error_type, pattern in error_patterns.items():
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    print(f"  {error_type}: {len(matches)} occurrences")
            
            # Recent errors (last 24 hours)
            recent_errors = []
            for line in content.split('\n'):
                if any(keyword in line.lower() for keyword in ['error', 'failed', 'exception']):
                    recent_errors.append(line)
            
            if recent_errors:
                print(f"  Recent errors: {len(recent_errors)}")
                # Show last few errors
                for error in recent_errors[-3:]:
                    print(f"    {error[:80]}...")
            
        except Exception as e:
            print(f"  Error reading log: {e}")
        
        print()

if __name__ == '__main__':
    analyze_installation_logs()
```

## Recovery Procedures

### Complete Reset

```python
def reset_installer():
    """Reset installer to clean state"""
    
    from third_party_installer.core.installer import ThirdPartyInstaller
    import shutil
    
    installer = ThirdPartyInstaller()
    
    print("Resetting Third Party Installer...")
    
    # Clear temporary files
    if installer.temp_dir.exists():
        shutil.rmtree(installer.temp_dir, ignore_errors=True)
        print("✓ Cleared temporary files")
    
    # Clear configuration cache
    config_files = [
        installer.config_dir / 'installation_status.json',
        installer.config_dir / 'proxy_config.json',
        installer.config_dir / 'download_cache.json'
    ]
    
    for config_file in config_files:
        if config_file.exists():
            config_file.unlink()
            print(f"✓ Removed {config_file.name}")
    
    # Recreate directories
    installer.temp_dir.mkdir(parents=True, exist_ok=True)
    installer.config_dir.mkdir(parents=True, exist_ok=True)
    
    print("Reset complete. Please retry installation.")

if __name__ == '__main__':
    reset_installer()
```

### Repair Installation

```python
def repair_installation():
    """Attempt to repair problematic installation"""
    
    from third_party_installer.core.installer import ThirdPartyInstaller, InstallationStatus
    
    installer = ThirdPartyInstaller()
    
    print("=== Repair Installation ===\n")
    
    # Check each tool
    for tool_name, tool in installer.tools_config.items():
        print(f"Checking {tool.display_name}...")
        
        status = installer.get_tool_status(tool_name)
        
        if status == InstallationStatus.NOT_INSTALLED and tool.required:
            print(f"  ⚠️  Required tool not installed, attempting installation...")
            success = installer.install_tool(tool_name)
            if success:
                print(f"  ✓ Successfully installed {tool.display_name}")
            else:
                print(f"  ✗ Failed to install {tool.display_name}")
        
        elif status == InstallationStatus.INSTALLATION_FAILED:
            print(f"  ⚠️  Previous installation failed, retrying...")
            success = installer.install_tool(tool_name)
            if success:
                print(f"  ✓ Successfully repaired {tool.display_name}")
            else:
                print(f"  ✗ Repair failed for {tool.display_name}")
        
        elif status == InstallationStatus.INSTALLED:
            print(f"  ✓ {tool.display_name} is working correctly")
        
        print()
    
    # Final status check
    if installer.is_installation_complete():
        print("✓ All required tools are now installed")
    else:
        missing = installer.get_missing_required_tools()
        print(f"⚠️  Still missing required tools: {missing}")

if __name__ == '__main__':
    repair_installation()
```

## Getting Help

### Collecting Debug Information

When reporting issues, please include the following information:

1. **System Information**:
   - Operating System and version
   - Python version
   - SSH Tools Suite version

2. **Error Details**:
   - Complete error messages
   - Steps to reproduce the issue
   - Expected vs actual behavior

3. **Log Files**:
   - Installation logs
   - Error logs
   - Configuration files (remove sensitive data)

4. **Environment**:
   - Network configuration (corporate/home)
   - Proxy settings
   - Antivirus software
   - Administrative privileges

### Debug Information Script

```python
def collect_debug_info():
    """Collect comprehensive debug information for support"""
    
    import json
    import platform
    import sys
    from datetime import datetime
    
    debug_info = {
        'timestamp': datetime.now().isoformat(),
        'system': {
            'platform': platform.platform(),
            'python_version': sys.version,
            'architecture': platform.machine()
        },
        'installer_config': {},
        'tool_status': {},
        'recent_logs': []
    }
    
    # Collect installer information
    try:
        from third_party_installer.core.installer import ThirdPartyInstaller
        installer = ThirdPartyInstaller()
        
        # Tool status
        debug_info['tool_status'] = {
            name: status.value 
            for name, status in installer.get_all_tools_status().items()
        }
        
        # Configuration (sanitized)
        debug_info['installer_config'] = {
            'temp_dir': str(installer.temp_dir),
            'config_dir': str(installer.config_dir),
            'proxy_enabled': installer.proxy_config.get('enabled', False)
        }
        
    except Exception as e:
        debug_info['installer_error'] = str(e)
    
    # Recent log entries
    log_dir = Path.home() / '.ssh_tools_suite' / 'logs'
    if log_dir.exists():
        for log_file in log_dir.glob('*.log'):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()[-50:]  # Last 50 lines
                    debug_info['recent_logs'].append({
                        'file': log_file.name,
                        'lines': lines
                    })
            except:
                pass
    
    # Save debug information
    debug_file = Path('debug_info.json')
    with open(debug_file, 'w') as f:
        json.dump(debug_info, f, indent=2)
    
    print(f"Debug information saved to: {debug_file}")
    print("Please include this file when reporting issues.")

if __name__ == '__main__':
    collect_debug_info()
```

### Contact Information

For additional support:

1. **Documentation**: Check the [Developer Guide](developer-guide.md) and [API Reference](api-reference.md)
2. **GitHub Issues**: Report bugs and feature requests
3. **Stack Overflow**: Use tag `ssh-tools-suite` for community help
4. **Email Support**: Include debug information and detailed error descriptions

This troubleshooting guide should help resolve most common issues with the Third Party Installer. If problems persist, use the debug collection scripts to gather information for support requests.
