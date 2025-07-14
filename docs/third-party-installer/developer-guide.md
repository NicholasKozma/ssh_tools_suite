# Third Party Installer - Developer Guide

This guide provides advanced technical information for developers who need to integrate, extend, or customize the Third Party Installer module.

## Developer Workflow Integration

### Embedding in Applications

The Third Party Installer is designed for seamless integration into larger applications:

```python
from third_party_installer.core.installer import ThirdPartyInstaller, InstallationStatus
from pathlib import Path
import logging

class ApplicationWithDependencies:
    def __init__(self):
        self.installer = ThirdPartyInstaller()
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for installation operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('installation.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def ensure_dependencies(self) -> bool:
        """Ensure all required tools are installed before proceeding"""
        missing_tools = self.installer.get_missing_required_tools()
        
        if not missing_tools:
            self.logger.info("All required tools are already installed")
            return True
            
        self.logger.info(f"Missing required tools: {missing_tools}")
        
        # Option 1: Automatic installation
        return self._install_missing_tools(missing_tools)
        
        # Option 2: Prompt user for installation
        # return self._prompt_user_for_installation(missing_tools)
    
    def _install_missing_tools(self, tools: list) -> bool:
        """Install missing tools automatically"""
        success_count = 0
        
        for tool_name in tools:
            self.logger.info(f"Installing {tool_name}...")
            
            try:
                success = self.installer.install_tool(
                    tool_name, 
                    progress_callback=self._log_progress
                )
                
                if success:
                    success_count += 1
                    self.logger.info(f"Successfully installed {tool_name}")
                else:
                    self.logger.error(f"Failed to install {tool_name}")
                    
            except Exception as e:
                self.logger.error(f"Exception during {tool_name} installation: {e}")
        
        return success_count == len(tools)
    
    def _log_progress(self, progress: int, message: str):
        """Log installation progress"""
        if progress % 10 == 0:  # Log every 10%
            self.logger.info(f"Progress: {progress}% - {message}")
    
    def run_application(self):
        """Main application entry point with dependency checking"""
        if not self.ensure_dependencies():
            self.logger.error("Failed to install required dependencies")
            return False
            
        self.logger.info("Starting application with all dependencies satisfied")
        # Your application logic here
        return True

# Usage
if __name__ == "__main__":
    app = ApplicationWithDependencies()
    app.run_application()
```

### Custom Tool Definitions

Add support for your own tools by extending the configuration:

```python
from third_party_installer.core.installer import ThirdPartyTool
import json
from pathlib import Path

class CustomToolManager:
    def __init__(self, installer: ThirdPartyInstaller):
        self.installer = installer
        
    def add_custom_tools(self):
        """Add custom tools to the installer configuration"""
        
        # Example: Adding OpenSSH as a managed tool
        openssh_tool = ThirdPartyTool(
            name='openssh',
            display_name='OpenSSH Client',
            description='OpenSSH client for secure shell connections',
            download_url='https://github.com/PowerShell/Win32-OpenSSH/releases/latest/download/OpenSSH-Win64.zip',
            executable_paths=[
                'C:\\Program Files\\OpenSSH\\ssh.exe',
                'C:\\Windows\\System32\\OpenSSH\\ssh.exe',
                'C:\\OpenSSH\\ssh.exe'
            ],
            version_command='ssh -V',
            installer_type='zip',
            required=True,
            dependencies=[]
        )
        
        # Example: Adding a custom monitoring tool
        monitoring_tool = ThirdPartyTool(
            name='custom_monitor',
            display_name='Custom Network Monitor',
            description='Custom tool for network monitoring',
            download_url='https://your-company.com/tools/monitor.exe',
            executable_paths=[
                'C:\\Program Files\\CustomMonitor\\monitor.exe',
                'C:\\Tools\\monitor.exe'
            ],
            version_command='monitor.exe --version',
            installer_type='exe',
            required=False,
            dependencies=['openssh']
        )
        
        # Add to installer configuration
        self.installer.tools_config['openssh'] = openssh_tool
        self.installer.tools_config['custom_monitor'] = monitoring_tool
        
        # Save custom configuration
        self._save_custom_config()
    
    def _save_custom_config(self):
        """Save custom tool configuration to file"""
        config_path = Path(self.installer.config_dir) / 'custom_tools.json'
        
        custom_tools = {}
        for name, tool in self.installer.tools_config.items():
            if name not in ['psexec', 'vlc', 'ffmpeg', 'px']:  # Skip built-in tools
                custom_tools[name] = {
                    'name': tool.name,
                    'display_name': tool.display_name,
                    'description': tool.description,
                    'download_url': tool.download_url,
                    'executable_paths': tool.executable_paths,
                    'version_command': tool.version_command,
                    'installer_type': tool.installer_type,
                    'required': tool.required,
                    'dependencies': tool.dependencies
                }
        
        with open(config_path, 'w') as f:
            json.dump(custom_tools, f, indent=2)
    
    def load_custom_config(self):
        """Load custom tool configuration from file"""
        config_path = Path(self.installer.config_dir) / 'custom_tools.json'
        
        if not config_path.exists():
            return
            
        try:
            with open(config_path, 'r') as f:
                custom_tools = json.load(f)
                
            for name, config in custom_tools.items():
                tool = ThirdPartyTool(**config)
                self.installer.tools_config[name] = tool
                
        except Exception as e:
            print(f"Failed to load custom tools: {e}")

# Usage
installer = ThirdPartyInstaller()
custom_manager = CustomToolManager(installer)
custom_manager.load_custom_config()
custom_manager.add_custom_tools()
```

### Advanced Proxy Configuration

Handle complex corporate proxy scenarios:

```python
class CorporateProxyManager:
    def __init__(self, installer: ThirdPartyInstaller):
        self.installer = installer
        
    def setup_corporate_proxy(self):
        """Configure proxy for corporate environment"""
        
        # Try to detect existing proxy configuration
        if self._detect_system_proxy():
            self.installer.proxy_config['auto_detect'] = True
            return True
            
        # Try PX proxy tool
        if self._setup_px_proxy():
            return True
            
        # Fallback to manual configuration
        return self._setup_manual_proxy()
    
    def _detect_system_proxy(self) -> bool:
        """Detect system proxy settings"""
        try:
            import winreg
            
            # Check Windows registry for proxy settings
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                              r"Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings") as key:
                
                proxy_enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
                if proxy_enabled:
                    proxy_server = winreg.QueryValueEx(key, "ProxyServer")[0]
                    self.installer.proxy_config.update({
                        'enabled': True,
                        'auto_detect': True,
                        'server': proxy_server.split(':')[0],
                        'port': int(proxy_server.split(':')[1]) if ':' in proxy_server else 8080
                    })
                    return True
                    
        except Exception:
            pass
            
        return False
    
    def _setup_px_proxy(self) -> bool:
        """Setup PX corporate proxy tool"""
        px_status = self.installer.get_tool_status('px')
        
        if px_status != InstallationStatus.INSTALLED:
            # Install PX if not available
            success = self.installer.install_tool('px')
            if not success:
                return False
        
        # Configure PX proxy
        self.installer.proxy_config.update({
            'enabled': True,
            'use_px': True,
            'px_port': 3128
        })
        
        return True
    
    def _setup_manual_proxy(self) -> bool:
        """Setup manual proxy configuration"""
        # In a real application, prompt user for proxy details
        # For this example, we'll use environment variables
        import os
        
        proxy_server = os.getenv('HTTP_PROXY') or os.getenv('HTTPS_PROXY')
        if proxy_server:
            # Parse proxy URL (e.g., http://proxy.company.com:8080)
            from urllib.parse import urlparse
            parsed = urlparse(proxy_server)
            
            self.installer.proxy_config.update({
                'enabled': True,
                'auto_detect': False,
                'server': parsed.hostname,
                'port': parsed.port or 8080,
                'username': parsed.username,
                'password': parsed.password
            })
            return True
            
        return False

# Usage
proxy_manager = CorporateProxyManager(installer)
proxy_manager.setup_corporate_proxy()
```

## Debugging and Troubleshooting

### Comprehensive Logging Setup

```python
import logging
import sys
from pathlib import Path

class InstallerDebugger:
    def __init__(self, installer: ThirdPartyInstaller):
        self.installer = installer
        self.setup_debug_logging()
        
    def setup_debug_logging(self):
        """Setup comprehensive logging for debugging"""
        log_dir = Path(self.installer.config_dir) / 'logs'
        log_dir.mkdir(exist_ok=True)
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        )
        simple_formatter = logging.Formatter('%(levelname)s: %(message)s')
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(log_dir / 'installer_debug.log')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        
        # Console handler for important messages
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        
        # Configure logger
        logger = logging.getLogger('third_party_installer')
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        logger.propagate = False
        
        return logger
    
    def diagnose_installation_issues(self, tool_name: str):
        """Comprehensive diagnosis of installation issues"""
        logger = logging.getLogger('third_party_installer')
        tool = self.installer.tools_config.get(tool_name)
        
        if not tool:
            logger.error(f"Tool '{tool_name}' not found in configuration")
            return
            
        logger.info(f"Diagnosing installation issues for {tool.display_name}")
        
        # Check tool configuration
        self._check_tool_config(tool, logger)
        
        # Check network connectivity
        self._check_network_connectivity(tool, logger)
        
        # Check system requirements
        self._check_system_requirements(tool, logger)
        
        # Check permissions
        self._check_permissions(tool, logger)
        
        # Check existing installation
        self._check_existing_installation(tool, logger)
    
    def _check_tool_config(self, tool: ThirdPartyTool, logger):
        """Validate tool configuration"""
        logger.info("Checking tool configuration...")
        
        required_fields = ['name', 'download_url', 'executable_paths', 'installer_type']
        for field in required_fields:
            value = getattr(tool, field, None)
            if not value:
                logger.error(f"Missing required field: {field}")
            else:
                logger.debug(f"{field}: {value}")
    
    def _check_network_connectivity(self, tool: ThirdPartyTool, logger):
        """Check network connectivity to download source"""
        logger.info("Checking network connectivity...")
        
        try:
            import urllib.request
            import ssl
            
            # Create SSL context that doesn't verify certificates (for testing)
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Attempt to connect to download URL
            req = urllib.request.Request(tool.download_url)
            req.add_header('User-Agent', 'SSH-Tools-Suite-Installer/1.0')
            
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                if response.getcode() == 200:
                    logger.info(f"Successfully connected to {tool.download_url}")
                    content_length = response.headers.get('Content-Length')
                    if content_length:
                        logger.info(f"Download size: {int(content_length) / 1024 / 1024:.1f} MB")
                else:
                    logger.warning(f"Unexpected response code: {response.getcode()}")
                    
        except Exception as e:
            logger.error(f"Network connectivity test failed: {e}")
            logger.info("Possible issues:")
            logger.info("- No internet connection")
            logger.info("- Corporate firewall blocking access")
            logger.info("- Proxy configuration required")
            logger.info("- Download URL is invalid or moved")
    
    def _check_system_requirements(self, tool: ThirdPartyTool, logger):
        """Check system requirements for tool installation"""
        logger.info("Checking system requirements...")
        
        import platform
        import shutil
        import psutil
        
        # Platform check
        system = platform.system()
        logger.info(f"Operating System: {system} {platform.release()}")
        
        # Disk space check
        if hasattr(shutil, 'disk_usage'):
            total, used, free = shutil.disk_usage('/')
            free_gb = free / (1024**3)
            logger.info(f"Available disk space: {free_gb:.1f} GB")
            
            if free_gb < 1.0:  # Less than 1GB free
                logger.warning("Low disk space may cause installation failures")
        
        # Memory check
        memory = psutil.virtual_memory()
        logger.info(f"Available memory: {memory.available / (1024**3):.1f} GB")
        
        # Administrator privileges check (Windows)
        if system == 'Windows':
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            logger.info(f"Administrator privileges: {'Yes' if is_admin else 'No'}")
            
            if not is_admin and tool.installer_type in ['msi', 'exe']:
                logger.warning("Administrator privileges may be required for installation")
    
    def _check_permissions(self, tool: ThirdPartyTool, logger):
        """Check file system permissions"""
        logger.info("Checking file system permissions...")
        
        # Check write permissions for installation directories
        for exe_path in tool.executable_paths:
            install_dir = Path(exe_path).parent
            logger.debug(f"Checking directory: {install_dir}")
            
            try:
                # Try to create a test file
                test_file = install_dir / '.installer_test'
                test_file.touch()
                test_file.unlink()
                logger.info(f"Write access confirmed: {install_dir}")
                break
            except PermissionError:
                logger.warning(f"No write access: {install_dir}")
            except FileNotFoundError:
                logger.info(f"Directory does not exist: {install_dir}")
        
        # Check temporary directory permissions
        temp_dir = Path(self.installer.temp_dir)
        try:
            test_file = temp_dir / '.installer_test'
            test_file.touch()
            test_file.unlink()
            logger.info(f"Temporary directory accessible: {temp_dir}")
        except Exception as e:
            logger.error(f"Temporary directory issues: {e}")
    
    def _check_existing_installation(self, tool: ThirdPartyTool, logger):
        """Check for existing installations"""
        logger.info("Checking for existing installations...")
        
        status = self.installer.get_tool_status(tool.name)
        logger.info(f"Current status: {status.value}")
        
        # Check each possible installation location
        for exe_path in tool.executable_paths:
            path_obj = Path(exe_path)
            if path_obj.exists():
                logger.info(f"Found existing installation: {exe_path}")
                
                # Try to get version information
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
                            logger.info(f"Version info: {result.stdout.strip()}")
                        else:
                            logger.warning(f"Version command failed: {result.stderr}")
                    except Exception as e:
                        logger.warning(f"Could not get version: {e}")
            else:
                logger.debug(f"Not found: {exe_path}")

# Usage for debugging
debugger = InstallerDebugger(installer)
debugger.diagnose_installation_issues('psexec')
```

### Performance Monitoring

```python
import time
import threading
from contextlib import contextmanager

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        
    @contextmanager
    def time_operation(self, operation_name: str):
        """Context manager for timing operations"""
        start_time = time.time()
        start_memory = self._get_memory_usage()
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = self._get_memory_usage()
            
            self.metrics[operation_name] = {
                'duration': end_time - start_time,
                'memory_delta': end_memory - start_memory,
                'timestamp': time.time()
            }
    
    def _get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024
        except ImportError:
            return 0
    
    def monitor_installation(self, installer: ThirdPartyInstaller, tool_name: str):
        """Monitor installation performance"""
        
        with self.time_operation(f'{tool_name}_total'):
            
            with self.time_operation(f'{tool_name}_download'):
                installer_path = installer.download_tool(tool_name)
                
            if installer_path:
                with self.time_operation(f'{tool_name}_install'):
                    success = installer.install_tool(tool_name)
                    
        return success if 'installer_path' in locals() and installer_path else False
    
    def print_report(self):
        """Print performance report"""
        print("\n=== Performance Report ===")
        for operation, metrics in self.metrics.items():
            print(f"{operation}:")
            print(f"  Duration: {metrics['duration']:.2f} seconds")
            print(f"  Memory Delta: {metrics['memory_delta']:.1f} MB")
            print()

# Usage
monitor = PerformanceMonitor()
success = monitor.monitor_installation(installer, 'vlc')
monitor.print_report()
```

## Testing and Validation

### Unit Testing Framework

```python
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import tempfile
import shutil

class TestThirdPartyInstaller(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path(tempfile.mkdtemp())
        self.installer = ThirdPartyInstaller()
        self.installer.config_dir = self.test_dir / 'config'
        self.installer.temp_dir = self.test_dir / 'temp'
        self.installer.config_dir.mkdir(parents=True)
        self.installer.temp_dir.mkdir(parents=True)
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_tool_status_detection(self):
        """Test tool status detection logic"""
        
        # Test case: Tool not installed
        status = self.installer.get_tool_status('nonexistent_tool')
        self.assertEqual(status, InstallationStatus.NOT_INSTALLED)
        
        # Test case: Mock installed tool
        test_tool = ThirdPartyTool(
            name='test_tool',
            display_name='Test Tool',
            description='A test tool',
            download_url='https://example.com/tool.zip',
            executable_paths=[str(self.test_dir / 'tool.exe')],
            version_command='tool.exe --version',
            installer_type='zip',
            required=True,
            dependencies=[]
        )
        
        self.installer.tools_config['test_tool'] = test_tool
        
        # Create mock executable
        (self.test_dir / 'tool.exe').touch()
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = 'Test Tool v1.0'
            
            status = self.installer.get_tool_status('test_tool')
            self.assertEqual(status, InstallationStatus.INSTALLED)
    
    @patch('urllib.request.urlretrieve')
    def test_download_tool(self, mock_urlretrieve):
        """Test tool download functionality"""
        
        # Mock successful download
        test_file = self.test_dir / 'downloaded_tool.exe'
        test_file.touch()
        mock_urlretrieve.return_value = (str(test_file), None)
        
        # Add test tool to configuration
        test_tool = ThirdPartyTool(
            name='download_test',
            display_name='Download Test',
            description='Tool for testing downloads',
            download_url='https://example.com/tool.exe',
            executable_paths=[str(self.test_dir / 'tool.exe')],
            installer_type='exe',
            required=True,
            dependencies=[]
        )
        
        self.installer.tools_config['download_test'] = test_tool
        
        # Test download
        result = self.installer.download_tool('download_test')
        
        # Verify download was attempted
        mock_urlretrieve.assert_called_once()
        self.assertIsInstance(result, Path)
    
    def test_missing_required_tools(self):
        """Test identification of missing required tools"""
        
        # Add required and optional tools
        required_tool = ThirdPartyTool(
            name='required_tool',
            display_name='Required Tool',
            description='A required tool',
            download_url='https://example.com/required.exe',
            executable_paths=['/nonexistent/path'],
            installer_type='exe',
            required=True,
            dependencies=[]
        )
        
        optional_tool = ThirdPartyTool(
            name='optional_tool',
            display_name='Optional Tool',
            description='An optional tool',
            download_url='https://example.com/optional.exe',
            executable_paths=['/nonexistent/path'],
            installer_type='exe',
            required=False,
            dependencies=[]
        )
        
        self.installer.tools_config['required_tool'] = required_tool
        self.installer.tools_config['optional_tool'] = optional_tool
        
        missing = self.installer.get_missing_required_tools()
        
        self.assertIn('required_tool', missing)
        self.assertNotIn('optional_tool', missing)
    
    def test_proxy_configuration(self):
        """Test proxy configuration handling"""
        
        # Test manual proxy configuration
        proxy_config = {
            'enabled': True,
            'auto_detect': False,
            'server': 'proxy.company.com',
            'port': 8080,
            'username': 'testuser',
            'password': 'testpass'
        }
        
        self.installer.proxy_config = proxy_config
        
        # Verify proxy configuration is stored correctly
        self.assertTrue(self.installer.proxy_config['enabled'])
        self.assertEqual(self.installer.proxy_config['server'], 'proxy.company.com')
        self.assertEqual(self.installer.proxy_config['port'], 8080)
    
    @patch('subprocess.run')
    def test_installation_validation(self, mock_run):
        """Test installation validation logic"""
        
        # Mock successful tool execution
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = 'Tool v1.0'
        
        test_tool = ThirdPartyTool(
            name='validation_test',
            display_name='Validation Test',
            description='Tool for testing validation',
            download_url='https://example.com/tool.exe',
            executable_paths=[str(self.test_dir / 'tool.exe')],
            version_command='tool.exe --version',
            installer_type='exe',
            required=True,
            dependencies=[]
        )
        
        # Create mock executable
        (self.test_dir / 'tool.exe').touch()
        
        self.installer.tools_config['validation_test'] = test_tool
        
        # Test validation
        status = self.installer.get_tool_status('validation_test')
        self.assertEqual(status, InstallationStatus.INSTALLED)

class TestInstallerIntegration(unittest.TestCase):
    """Integration tests for installer components"""
    
    def setUp(self):
        self.installer = ThirdPartyInstaller()
    
    def test_real_tool_detection(self):
        """Test detection of real system tools"""
        
        # Test common Windows tools
        import platform
        if platform.system() == 'Windows':
            # Test if Windows built-in tools are detected
            test_paths = [
                'C:\\Windows\\System32\\ping.exe',
                'C:\\Windows\\System32\\ipconfig.exe'
            ]
            
            for path in test_paths:
                if Path(path).exists():
                    self.assertTrue(Path(path).is_file())
    
    @unittest.skipIf(not Path('/usr/bin/which').exists(), "which command not available")
    def test_unix_tool_detection(self):
        """Test detection on Unix-like systems"""
        
        import subprocess
        
        # Test common Unix tools
        try:
            result = subprocess.run(['which', 'ls'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                ls_path = result.stdout.strip()
                self.assertTrue(Path(ls_path).exists())
        except FileNotFoundError:
            self.skipTest("which command not available")

if __name__ == '__main__':
    # Run specific test suites
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTest(unittest.makeSuite(TestThirdPartyInstaller))
    
    # Add integration tests (commented out for normal runs)
    # suite.addTest(unittest.makeSuite(TestInstallerIntegration))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with error code if tests failed
    exit(0 if result.wasSuccessful() else 1)
```

### Load Testing

```python
import concurrent.futures
import time
import threading
from collections import defaultdict

class LoadTester:
    def __init__(self, installer: ThirdPartyInstaller):
        self.installer = installer
        self.results = defaultdict(list)
        self.lock = threading.Lock()
    
    def stress_test_detection(self, iterations: int = 100):
        """Stress test tool detection logic"""
        
        def detect_all_tools():
            start_time = time.time()
            try:
                for tool_name in self.installer.tools_config.keys():
                    status = self.installer.get_tool_status(tool_name)
                
                duration = time.time() - start_time
                with self.lock:
                    self.results['detection_times'].append(duration)
                return True
                
            except Exception as e:
                with self.lock:
                    self.results['detection_errors'].append(str(e))
                return False
        
        # Run concurrent detection tests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(detect_all_tools) for _ in range(iterations)]
            concurrent.futures.wait(futures)
        
        # Print results
        print(f"\n=== Tool Detection Stress Test ===")
        print(f"Iterations: {iterations}")
        print(f"Successful detections: {len(self.results['detection_times'])}")
        print(f"Errors: {len(self.results['detection_errors'])}")
        
        if self.results['detection_times']:
            times = self.results['detection_times']
            print(f"Average time: {sum(times) / len(times):.3f}s")
            print(f"Min time: {min(times):.3f}s")
            print(f"Max time: {max(times):.3f}s")
    
    def concurrent_download_test(self, tool_names: list, max_workers: int = 3):
        """Test concurrent downloads (use with caution)"""
        
        def download_tool(tool_name):
            start_time = time.time()
            try:
                result = self.installer.download_tool(tool_name)
                duration = time.time() - start_time
                
                with self.lock:
                    self.results[f'{tool_name}_downloads'].append({
                        'success': result is not None,
                        'duration': duration
                    })
                    
                return result is not None
                
            except Exception as e:
                with self.lock:
                    self.results[f'{tool_name}_errors'].append(str(e))
                return False
        
        print(f"\n=== Concurrent Download Test ===")
        print(f"Tools: {tool_names}")
        print(f"Max workers: {max_workers}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(download_tool, tool): tool for tool in tool_names}
            
            for future in concurrent.futures.as_completed(futures):
                tool_name = futures[future]
                try:
                    success = future.result()
                    print(f"{tool_name}: {'Success' if success else 'Failed'}")
                except Exception as e:
                    print(f"{tool_name}: Exception - {e}")

# Usage
load_tester = LoadTester(installer)
load_tester.stress_test_detection(50)

# Test concurrent downloads (be careful with this - it may overwhelm servers)
# load_tester.concurrent_download_test(['vlc'], max_workers=1)
```

## Configuration and Customization

### Configuration File Management

```python
import json
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigurationManager:
    def __init__(self, installer: ThirdPartyInstaller):
        self.installer = installer
        self.config_file = Path(installer.config_dir) / 'installer_config.json'
        self.user_config_file = Path(installer.config_dir) / 'user_config.yaml'
    
    def save_configuration(self):
        """Save current configuration to file"""
        config = {
            'tools': {},
            'proxy': self.installer.proxy_config,
            'settings': {
                'temp_dir': str(self.installer.temp_dir),
                'config_dir': str(self.installer.config_dir)
            }
        }
        
        # Save tool configurations
        for name, tool in self.installer.tools_config.items():
            config['tools'][name] = {
                'name': tool.name,
                'display_name': tool.display_name,
                'description': tool.description,
                'download_url': tool.download_url,
                'executable_paths': tool.executable_paths,
                'version_command': tool.version_command,
                'installer_type': tool.installer_type,
                'required': tool.required,
                'dependencies': tool.dependencies
            }
        
        # Save to JSON
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_configuration(self) -> bool:
        """Load configuration from file"""
        if not self.config_file.exists():
            return False
            
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            # Load proxy configuration
            if 'proxy' in config:
                self.installer.proxy_config.update(config['proxy'])
            
            # Load tool configurations
            if 'tools' in config:
                for name, tool_config in config['tools'].items():
                    tool = ThirdPartyTool(**tool_config)
                    self.installer.tools_config[name] = tool
            
            # Load settings
            if 'settings' in config:
                settings = config['settings']
                if 'temp_dir' in settings:
                    self.installer.temp_dir = Path(settings['temp_dir'])
                if 'config_dir' in settings:
                    self.installer.config_dir = Path(settings['config_dir'])
            
            return True
            
        except Exception as e:
            print(f"Failed to load configuration: {e}")
            return False
    
    def load_user_preferences(self) -> Dict[str, Any]:
        """Load user preferences from YAML file"""
        if not self.user_config_file.exists():
            return {}
            
        try:
            with open(self.user_config_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Failed to load user preferences: {e}")
            return {}
    
    def save_user_preferences(self, preferences: Dict[str, Any]):
        """Save user preferences to YAML file"""
        try:
            with open(self.user_config_file, 'w') as f:
                yaml.safe_dump(preferences, f, indent=2)
        except Exception as e:
            print(f"Failed to save user preferences: {e}")
    
    def create_deployment_config(self, target_dir: Path):
        """Create deployment configuration for enterprise deployment"""
        deployment_config = {
            'installer_settings': {
                'silent_mode': True,
                'required_tools_only': True,
                'skip_optional_tools': True,
                'log_level': 'INFO'
            },
            'proxy_settings': {
                'auto_detect': True,
                'use_px': True,
                'fallback_manual': False
            },
            'installation_paths': {
                'prefer_system_wide': True,
                'fallback_user_dir': True,
                'custom_install_dir': None
            },
            'tool_overrides': {
                'vlc': {
                    'required': False,
                    'download_url': 'https://internal-mirror.company.com/vlc.exe'
                }
            }
        }
        
        deployment_file = target_dir / 'deployment_config.json'
        with open(deployment_file, 'w') as f:
            json.dump(deployment_config, f, indent=2)
        
        print(f"Deployment configuration saved to: {deployment_file}")

# Usage
config_manager = ConfigurationManager(installer)
config_manager.save_configuration()

# Load user preferences
user_prefs = config_manager.load_user_preferences()
print(f"User preferences: {user_prefs}")

# Create deployment configuration
config_manager.create_deployment_config(Path('./deployment'))
```

This comprehensive developer guide provides the advanced technical information needed to effectively work with, extend, and integrate the Third Party Installer module. It covers embedding in applications, custom tool definitions, debugging strategies, testing frameworks, and configuration management for enterprise deployments.
