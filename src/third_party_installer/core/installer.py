#!/usr/bin/env python3
"""
Core installer module for third-party tools
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
import urllib.request
import urllib.error
import importlib.resources
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class InstallationStatus(Enum):
    """Status of installation."""
    NOT_INSTALLED = "not_installed"
    INSTALLED = "installed"
    NEEDS_UPDATE = "needs_update"
    INSTALLATION_FAILED = "installation_failed"

@dataclass
class ThirdPartyTool:
    """Configuration for a third-party tool."""
    name: str
    display_name: str
    description: str
    download_url: str
    executable_paths: List[str]  # Possible paths where the tool might be installed
    version_command: Optional[str] = None  # Command to get version
    installer_type: str = "msi"  # msi, exe, zip, etc.
    required: bool = True
    dependencies: List[str] = None  # Other tools this depends on
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

class ThirdPartyInstaller:
    """Core installer for third-party tools."""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize the installer."""
        self.config_dir = config_dir or self._get_default_config_dir()
        self.temp_dir = Path(tempfile.mkdtemp(prefix="third_party_installer_"))
        self.tools_config = self._load_tools_config()
        self.installation_status = {}
        self.proxy_config = self._load_proxy_config()
        
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Initial status check
        self._check_all_tools_status()
    
    def _get_default_config_dir(self) -> Path:
        """Get the default configuration directory."""
        if os.name == 'nt':
            # Windows
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            return Path(app_data) / 'ssh_tools_suite' / 'third_party_installer'
        else:
            # Unix-like systems
            return Path.home() / '.config' / 'ssh_tools_suite' / 'third_party_installer'
    
    def _load_tools_config(self) -> Dict[str, ThirdPartyTool]:
        """Load configuration for third-party tools."""
        tools = {}
        
        # PsExec (PsTools)
        tools['psexec'] = ThirdPartyTool(
            name='psexec',
            display_name='PsExec (PsTools)',
            description='Microsoft Sysinternals PsExec - Execute processes remotely',
            download_url='https://download.sysinternals.com/files/PSTools.zip',
            executable_paths=[
                'C:\\Windows\\System32\\PsExec.exe',
                'C:\\Windows\\SysWOW64\\PsExec.exe',
                'C:\\Program Files\\PSTools\\PsExec.exe',
                'C:\\PsExec\\PsExec.exe'
            ],
            version_command='PsExec.exe',
            installer_type='zip',
            required=True
        )
        
        # VLC Media Player
        tools['vlc'] = ThirdPartyTool(
            name='vlc',
            display_name='VLC Media Player',
            description='VLC Media Player - For RTSP stream viewing',
            download_url='https://get.videolan.org/vlc/3.0.18/win64/vlc-3.0.18-win64.exe',
            executable_paths=[
                'C:\\Program Files\\VideoLAN\\VLC\\vlc.exe',
                'C:\\Program Files (x86)\\VideoLAN\\VLC\\vlc.exe'
            ],
            version_command='vlc.exe --version',
            installer_type='exe',
            required=False
        )
        
        # FFmpeg
        tools['ffmpeg'] = ThirdPartyTool(
            name='ffmpeg',
            display_name='FFmpeg',
            description='FFmpeg - Video/audio processing and streaming',
            download_url='https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip',
            executable_paths=[
                'C:\\ffmpeg\\bin\\ffmpeg.exe',
                'C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe'
            ],
            version_command='ffmpeg -version',
            installer_type='zip',
            required=True
        )
        
        # PX (Corporate Proxy Tool) - Bundled with package
        tools['px'] = ThirdPartyTool(
            name='px',
            display_name='PX (Corporate Proxy)',
            description='PX - Corporate proxy authentication tool (bundled)',
            download_url='',  # Not needed - bundled with package
            executable_paths=[
                self._get_bundled_px_exe_path(),
                'C:\\px\\px.exe',
                'C:\\Program Files\\PX\\px.exe'
            ],
            version_command='px.exe --version',
            installer_type='bundled',
            required=False
        )
        
        return tools
    
    def _load_proxy_config(self) -> Dict[str, Any]:
        """Load proxy configuration from SSH installer."""
        try:
            # Try to load from SSH installer's config
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_file = Path(app_data) / 'SSH_Tools_Suite' / 'proxy_config.json'
            
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {}
    
    def _check_all_tools_status(self):
        """Check installation status of all tools."""
        for tool_name, tool in self.tools_config.items():
            self.installation_status[tool_name] = self._check_tool_status(tool)
    
    def _check_tool_status(self, tool: ThirdPartyTool) -> InstallationStatus:
        """Check if a tool is installed and get its status."""
        try:
            # Check if executable exists in any of the expected paths
            for exe_path in tool.executable_paths:
                if Path(exe_path).exists():
                    return InstallationStatus.INSTALLED
            
            # Check if it's in PATH using PowerShell-compatible method
            if tool.version_command:
                try:
                    # Use 'where' command on Windows to find executable
                    exe_name = tool.version_command.split()[0]
                    if os.name == 'nt':
                        # Windows - use 'where' command
                        result = subprocess.run(
                            ['where', exe_name],
                            capture_output=True,
                            text=True,
                            timeout=5,
                            shell=True
                        )
                        if result.returncode == 0:
                            return InstallationStatus.INSTALLED
                    else:
                        # Unix-like systems
                        result = subprocess.run(
                            ['which', exe_name],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.returncode == 0:
                            return InstallationStatus.INSTALLED
                except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                    pass
            
            return InstallationStatus.NOT_INSTALLED
            
        except Exception:
            return InstallationStatus.NOT_INSTALLED
    
    def get_tool_status(self, tool_name: str) -> InstallationStatus:
        """Get the installation status of a specific tool."""
        return self.installation_status.get(tool_name, InstallationStatus.NOT_INSTALLED)
    
    def get_all_tools_status(self) -> Dict[str, InstallationStatus]:
        """Get installation status of all tools."""
        return self.installation_status.copy()
    
    def is_installation_complete(self) -> bool:
        """Check if all required tools are installed."""
        for tool_name, tool in self.tools_config.items():
            if tool.required:
                status = self.get_tool_status(tool_name)
                if status != InstallationStatus.INSTALLED:
                    return False
        return True
    
    def get_missing_required_tools(self) -> List[str]:
        """Get list of required tools that are not installed."""
        missing = []
        for tool_name, tool in self.tools_config.items():
            if tool.required:
                status = self.get_tool_status(tool_name)
                if status != InstallationStatus.INSTALLED:
                    missing.append(tool_name)
        return missing
    
    def download_tool(self, tool_name: str, progress_callback=None) -> Optional[Path]:
        """Download a tool's installer."""
        if tool_name not in self.tools_config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools_config[tool_name]
        
        try:
            # Skip download for bundled tools
            if tool.installer_type == 'bundled':
                if progress_callback:
                    progress_callback(100, f"{tool.display_name} is bundled with the package")
                return None  # No download needed
            
            # Configure proxy if needed
            if self.proxy_config.get('enabled', False):
                self._configure_proxy()
            
            # Download the file
            response = urllib.request.urlopen(tool.download_url)
            total_size = int(response.headers.get('content-length', 0))
            
            # Determine filename
            filename = tool.download_url.split('/')[-1]
            if not filename or '.' not in filename:
                if tool.installer_type == 'msi':
                    filename = f"{tool_name}.msi"
                elif tool.installer_type == 'exe':
                    filename = f"{tool_name}.exe"
                elif tool.installer_type == 'zip':
                    filename = f"{tool_name}.zip"
                else:
                    filename = f"{tool_name}.bin"
            
            download_path = self.temp_dir / filename
            
            # Download with progress tracking
            downloaded = 0
            with open(download_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if progress_callback and total_size > 0:
                        progress = int((downloaded / total_size) * 100)
                        progress_callback(progress)
            
            return download_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to download {tool.display_name}: {str(e)}")
    
    def install_tool(self, tool_name: str, progress_callback=None) -> bool:
        """Install a tool."""
        if tool_name not in self.tools_config:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools_config[tool_name]
        
        try:
            # Download the installer (skip for bundled tools)
            if progress_callback:
                if tool.installer_type == 'bundled':
                    progress_callback(50, f"Verifying bundled {tool.display_name}...")
                else:
                    progress_callback(0, f"Downloading {tool.display_name}...")
            
            installer_path = self.download_tool(tool_name, 
                lambda p: progress_callback(p // 2, f"Downloading {tool.display_name}...") if progress_callback else None)
            
            if progress_callback and tool.installer_type != 'bundled':
                progress_callback(50, f"Installing {tool.display_name}...")
            
            # Install based on type
            if tool.installer_type == 'bundled':
                # Tool is bundled with the package - just verify it exists
                success = self._verify_bundled_tool(tool)
            elif tool.installer_type == 'msi':
                success = self._install_msi(installer_path, tool)
            elif tool.installer_type == 'exe':
                success = self._install_exe(installer_path, tool)
            elif tool.installer_type == 'zip':
                success = self._install_zip(installer_path, tool)
            else:
                raise ValueError(f"Unsupported installer type: {tool.installer_type}")
            
            if success:
                if progress_callback:
                    progress_callback(100, f"{tool.display_name} installed successfully!")
                
                # Update status
                self.installation_status[tool_name] = InstallationStatus.INSTALLED
                
                # Save installation record
                self._save_installation_record(tool_name, tool)
                
                return True
            else:
                if progress_callback:
                    progress_callback(0, f"Failed to install {tool.display_name}")
                
                self.installation_status[tool_name] = InstallationStatus.INSTALLATION_FAILED
                return False
                
        except Exception as e:
            if progress_callback:
                progress_callback(0, f"Installation error: {str(e)}")
            
            self.installation_status[tool_name] = InstallationStatus.INSTALLATION_FAILED
            return False
    
    def _configure_proxy(self):
        """Configure proxy settings for urllib."""
        if not self.proxy_config.get('enabled', False):
            return
        
        if self.proxy_config.get('auto_detect', False):
            # Use system proxy settings
            proxy_handler = urllib.request.ProxyHandler()
        elif self.proxy_config.get('use_px', False):
            # Use PX proxy (typically localhost:3128)
            px_port = self.proxy_config.get('px_port', 3128)
            proxy_url = f"http://127.0.0.1:{px_port}"
            proxy_handler = urllib.request.ProxyHandler({
                'http': proxy_url,
                'https': proxy_url
            })
        else:
            server = self.proxy_config.get('server', '')
            port = self.proxy_config.get('port', '')
            username = self.proxy_config.get('username', '')
            password = self.proxy_config.get('password', '')
            
            if server and port:
                if username and password:
                    proxy_url = f"http://{username}:{password}@{server}:{port}"
                else:
                    proxy_url = f"http://{server}:{port}"
                
                proxy_handler = urllib.request.ProxyHandler({
                    'http': proxy_url,
                    'https': proxy_url
                })
            else:
                proxy_handler = urllib.request.ProxyHandler()
        
        opener = urllib.request.build_opener(proxy_handler)
        urllib.request.install_opener(opener)
    
    def _verify_bundled_tool(self, tool: ThirdPartyTool) -> bool:
        """Verify that a bundled tool exists and is accessible."""
        try:
            # Check if any of the executable paths exist
            for exe_path in tool.executable_paths:
                if Path(exe_path).exists():
                    return True
            
            # If no direct path exists, the tool might not be properly bundled
            return False
            
        except Exception:
            return False
    
    def _install_msi(self, installer_path: Path, tool: ThirdPartyTool) -> bool:
        """Install MSI package."""
        try:
            cmd = [
                'msiexec',
                '/i', str(installer_path),
                '/quiet',
                '/norestart'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _install_exe(self, installer_path: Path, tool: ThirdPartyTool) -> bool:
        """Install EXE installer."""
        try:
            # Common silent install flags
            cmd = [str(installer_path), '/S']
            
            # Special handling for specific tools
            if tool.name == 'vlc':
                cmd = [str(installer_path), '/S', '/L=1033']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
            return result.returncode == 0
            
        except Exception:
            return False
    
    def _install_zip(self, installer_path: Path, tool: ThirdPartyTool) -> bool:
        """Install ZIP package by extracting to appropriate location."""
        try:
            import zipfile
            
            # Determine installation directory
            if tool.name == 'psexec':
                # Try to install to System32, but fall back to a user directory if no permissions
                install_dir = Path('C:\\Windows\\System32')
                fallback_dir = Path('C:\\PsExec')
            elif tool.name == 'ffmpeg':
                install_dir = Path('C:\\ffmpeg')
                fallback_dir = None
            elif tool.name == 'px':
                install_dir = Path('C:\\px')
                fallback_dir = None
            else:
                install_dir = Path(f'C:\\{tool.name}')
                fallback_dir = None
            
            # Extract the zip file
            with zipfile.ZipFile(installer_path, 'r') as zip_ref:
                if tool.name == 'psexec':
                    # Extract specific files from PSTools
                    try:
                        for file_info in zip_ref.filelist:
                            if file_info.filename.lower().endswith('.exe'):
                                # Try to extract to System32
                                try:
                                    zip_ref.extract(file_info, install_dir)
                                except PermissionError:
                                    # Fall back to user directory
                                    if fallback_dir:
                                        fallback_dir.mkdir(parents=True, exist_ok=True)
                                        zip_ref.extract(file_info, fallback_dir)
                    except Exception:
                        # If System32 fails, try fallback
                        if fallback_dir:
                            fallback_dir.mkdir(parents=True, exist_ok=True)
                            zip_ref.extractall(fallback_dir)
                elif tool.name == 'ffmpeg':
                    # Extract FFmpeg to dedicated directory
                    install_dir.mkdir(parents=True, exist_ok=True)
                    zip_ref.extractall(install_dir)
                    
                    # Move files from subdirectory if needed
                    for subdir in install_dir.iterdir():
                        if subdir.is_dir() and 'ffmpeg' in subdir.name.lower():
                            # Move contents up one level
                            for item in subdir.iterdir():
                                shutil.move(str(item), str(install_dir))
                            subdir.rmdir()
                            break
                else:
                    # Standard extraction
                    install_dir.mkdir(parents=True, exist_ok=True)
                    zip_ref.extractall(install_dir)
            
            return True
            
        except Exception:
            return False
    
    def _save_installation_record(self, tool_name: str, tool: ThirdPartyTool):
        """Save installation record."""
        try:
            record_file = self.config_dir / 'installed_tools.json'
            
            # Load existing records
            records = {}
            if record_file.exists():
                with open(record_file, 'r') as f:
                    records = json.load(f)
            
            # Add new record
            records[tool_name] = {
                'name': tool.name,
                'display_name': tool.display_name,
                'version': 'unknown',  # TODO: Get actual version
                'install_date': str(Path().resolve()),  # Current timestamp
                'install_path': tool.executable_paths[0] if tool.executable_paths else 'unknown'
            }
            
            # Save records
            with open(record_file, 'w') as f:
                json.dump(records, f, indent=2)
                
        except Exception:
            pass  # Non-critical error
    
    def cleanup(self):
        """Clean up temporary files."""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def __del__(self):
        """Cleanup on destruction."""
        self.cleanup()
    
    def _ensure_px_ini(self):
        """Ensure px.ini and px.ini.template exist in the config dir."""
        ini_file = self.config_dir / 'px.ini'
        template_file = self.config_dir / 'px.ini.template'
        # Always ensure px.ini.template is present
        if not template_file.exists():
            try:
                with importlib.resources.files('third_party_installer.data').joinpath('px.ini.template').open('rb') as src, \
                     open(template_file, 'wb') as dst:
                    dst.write(src.read())
            except Exception as e:
                print(f"Failed to copy px.ini.template: {e}")
        # Ensure px.ini exists by copying from template if needed
        if not ini_file.exists() and template_file.exists():
            try:
                shutil.copyfile(template_file, ini_file)
            except Exception as e:
                print(f"Failed to create px.ini from template: {e}")

    def _get_bundled_px_exe_path(self) -> str:
        """Return the path to the bundled px.exe, extracting it if needed."""
        # Extract px.exe from package data to config dir if not already present
        px_exe_path = str(self.config_dir / 'px.exe')
        if not os.path.exists(px_exe_path):
            try:
                with importlib.resources.files('third_party_installer.data').joinpath('px.exe').open('rb') as src, \
                     open(px_exe_path, 'wb') as dst:
                    dst.write(src.read())
            except Exception as e:
                print(f"Failed to extract px.exe: {e}")
        return px_exe_path

__all__ = ["ThirdPartyInstaller", "ThirdPartyTool", "InstallationStatus"]
