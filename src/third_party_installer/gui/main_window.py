#!/usr/bin/env python3
"""
Main window for Third Party Installer GUI
"""

import os
import sys
import json
from typing import Dict, List, Optional
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
        QLabel, QPushButton, QTextEdit, QProgressBar, QMessageBox, QLineEdit,
        QGroupBox, QListWidget, QListWidgetItem, QCheckBox, QDialog,
        QScrollArea, QFrame, QSplitter, QDialogButtonBox, QApplication
    )
    from PySide6.QtCore import Qt, QThread, Signal, QTimer
    from PySide6.QtGui import QFont, QPixmap, QIcon, QTextCursor
except ImportError:
    raise ImportError("PySide6 is required but not installed")

from ..core.installer import ThirdPartyInstaller, InstallationStatus, ThirdPartyTool


class InstallationWorker(QThread):
    """Worker thread for installing tools."""
    
    progress_updated = Signal(str, int, str)  # tool_name, progress, message
    installation_finished = Signal(str, bool, str)  # tool_name, success, message
    all_installations_finished = Signal(bool)  # success
    
    def __init__(self, installer: ThirdPartyInstaller, tools_to_install: List[str]):
        super().__init__()
        self.installer = installer
        self.tools_to_install = tools_to_install
        self.should_stop = False
    
    def run(self):
        """Run the installation process."""
        overall_success = True
        
        for tool_name in self.tools_to_install:
            if self.should_stop:
                break
            
            try:
                def progress_callback(progress: int, message: str):
                    if not self.should_stop:
                        self.progress_updated.emit(tool_name, progress, message)
                
                success = self.installer.install_tool(tool_name, progress_callback)
                
                if success:
                    tool = self.installer.tools_config[tool_name]
                    self.installation_finished.emit(tool_name, True, f"{tool.display_name} installed successfully!")
                else:
                    tool = self.installer.tools_config[tool_name]
                    self.installation_finished.emit(tool_name, False, f"Failed to install {tool.display_name}")
                    overall_success = False
                
            except Exception as e:
                self.installation_finished.emit(tool_name, False, f"Installation error: {str(e)}")
                overall_success = False
        
        self.all_installations_finished.emit(overall_success and not self.should_stop)
    
    def stop(self):
        """Stop the installation process."""
        self.should_stop = True


class ToolStatusWidget(QFrame):
    """Widget to display status of a single tool."""
    
    def __init__(self, tool: ThirdPartyTool, status: InstallationStatus, parent=None):
        super().__init__(parent)
        self.tool = tool
        self.status = status
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the widget UI."""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(1)
        
        layout = QHBoxLayout(self)
        
        # Status indicator
        self.status_label = QLabel()
        self.update_status_display()
        layout.addWidget(self.status_label)
        
        # Tool info
        info_layout = QVBoxLayout()
        
        name_label = QLabel(self.tool.display_name)
        name_label.setFont(QFont("", 10, QFont.Bold))
        info_layout.addWidget(name_label)
        
        desc_label = QLabel(self.tool.description)
        desc_label.setStyleSheet("color: #666;")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        if self.tool.required:
            req_label = QLabel("REQUIRED")
            req_label.setStyleSheet("color: red; font-weight: bold; font-size: 9px;")
            info_layout.addWidget(req_label)
        
        layout.addLayout(info_layout, 1)
        
        # Install checkbox
        self.install_checkbox = QCheckBox("Install")
        self.install_checkbox.setChecked(self.status != InstallationStatus.INSTALLED)
        self.install_checkbox.setEnabled(self.status != InstallationStatus.INSTALLED)
        layout.addWidget(self.install_checkbox)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_message = QLabel()
        self.status_message.setVisible(False)
        layout.addWidget(self.status_message)
    
    def update_status_display(self):
        """Update the status indicator."""
        if self.status == InstallationStatus.INSTALLED:
            self.status_label.setText("✅")
            self.status_label.setToolTip("Installed")
        elif self.status == InstallationStatus.NOT_INSTALLED:
            self.status_label.setText("❌")
            self.status_label.setToolTip("Not Installed")
        elif self.status == InstallationStatus.INSTALLATION_FAILED:
            self.status_label.setText("⚠️")
            self.status_label.setToolTip("Installation Failed")
        else:
            self.status_label.setText("❓")
            self.status_label.setToolTip("Unknown Status")
    
    def set_installation_progress(self, progress: int, message: str):
        """Update installation progress."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress)
        self.status_message.setText(message)
        self.status_message.setVisible(True)
    
    def set_installation_finished(self, success: bool, message: str):
        """Mark installation as finished."""
        self.progress_bar.setVisible(False)
        self.status_message.setText(message)
        
        if success:
            self.status = InstallationStatus.INSTALLED
            self.install_checkbox.setChecked(False)
            self.install_checkbox.setEnabled(False)
            self.status_message.setStyleSheet("color: green;")
        else:
            self.status = InstallationStatus.INSTALLATION_FAILED
            self.status_message.setStyleSheet("color: red;")
        
        self.update_status_display()
    
    def is_selected_for_installation(self) -> bool:
        """Check if this tool is selected for installation."""
        return self.install_checkbox.isChecked() and self.install_checkbox.isEnabled()


class ProxyConfigDialog(QDialog):
    """Dialog for configuring corporate proxy settings."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_config = self.load_proxy_config()
        self.setup_ui()
        self.load_saved_settings()
    
    def setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("Corporate Proxy Configuration")
        self.setModal(True)
        self.setFixedSize(600, 580)  # Made wider and taller to accommodate new button
        
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Configure Corporate Proxy Settings")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Info label
        info_label = QLabel("Configure proxy settings to download third-party tools through corporate firewalls.\n"
                           "💡 Tip: For corporate networks, px.exe handles authentication automatically - "
                           "you typically only need to enable the proxy without entering credentials.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(info_label)
        
        # px.exe status group
        px_group = QGroupBox("px.exe Corporate Proxy Tool")
        px_layout = QVBoxLayout(px_group)
        
        # Status label
        self.px_status_label = QLabel()
        self.update_px_status()
        px_layout.addWidget(self.px_status_label)
        
        # px.exe buttons
        px_button_layout = QHBoxLayout()
        
        self.start_px_btn = QPushButton("Start px.exe")
        self.start_px_btn.clicked.connect(self.start_px_exe)
        
        self.stop_px_btn = QPushButton("Stop px.exe") 
        self.stop_px_btn.clicked.connect(self.stop_px_exe)
        
        self.configure_px_btn = QPushButton("Configure px.ini")
        self.configure_px_btn.clicked.connect(self.configure_px_ini)
        
        px_button_layout.addWidget(self.start_px_btn)
        px_button_layout.addWidget(self.stop_px_btn)
        px_button_layout.addWidget(self.configure_px_btn)
        
        # Check proxy environment button
        self.check_proxy_env_btn = QPushButton("Check Environment")
        self.check_proxy_env_btn.clicked.connect(self.check_proxy_environment)
        px_button_layout.addWidget(self.check_proxy_env_btn)
        
        px_layout.addLayout(px_button_layout)
        
        # Proxy settings group
        proxy_group = QGroupBox("Proxy Settings")
        proxy_layout = QFormLayout(proxy_group)
        
        # Enable proxy checkbox
        self.enable_proxy_cb = QCheckBox("Use corporate proxy")
        self.enable_proxy_cb.toggled.connect(self.on_proxy_enabled_changed)
        proxy_layout.addRow(self.enable_proxy_cb)
        
        # Use PX checkbox
        self.use_px_cb = QCheckBox("Use px.exe (recommended for corporate networks)")
        self.use_px_cb.toggled.connect(self.on_use_px_changed)
        proxy_layout.addRow(self.use_px_cb)
        
        # PX port
        self.px_port_edit = QLineEdit()
        self.px_port_edit.setText("3128")
        self.px_port_edit.setPlaceholderText("3128")
        proxy_layout.addRow("PX Port:", self.px_port_edit)
        
        # Proxy server
        self.server_edit = QLineEdit()
        self.server_edit.setPlaceholderText("proxy.company.com")
        proxy_layout.addRow("Proxy Server:", self.server_edit)
        
        # Proxy port
        self.port_edit = QLineEdit()
        self.port_edit.setPlaceholderText("8080")
        proxy_layout.addRow("Port:", self.port_edit)
        
        # Authentication group
        auth_group = QGroupBox("Authentication (Usually Not Required)")
        auth_layout = QFormLayout(auth_group)
        
        # Username
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("domain\\username")
        auth_layout.addRow("Username:", self.username_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("password")
        auth_layout.addRow("Password:", self.password_edit)
        
        # Auto-detect option
        self.auto_detect_cb = QCheckBox("Auto-detect proxy settings from system")
        self.auto_detect_cb.toggled.connect(self.on_auto_detect_changed)
        
        # Buttons
        button_layout = QHBoxLayout()
        test_button = QPushButton("Test Connection")
        test_button.clicked.connect(self.test_proxy)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        save_button.setDefault(True)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(test_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(save_button)
        
        # Add all widgets to main layout
        layout.addWidget(px_group)
        layout.addWidget(proxy_group)
        layout.addWidget(auth_group)
        layout.addWidget(self.auto_detect_cb)
        layout.addStretch()
        layout.addLayout(button_layout)
        
        # Initial state
        self.on_proxy_enabled_changed()
    
    def on_proxy_enabled_changed(self):
        """Handle proxy enable/disable."""
        enabled = self.enable_proxy_cb.isChecked()
        self.use_px_cb.setEnabled(enabled)
        self.px_port_edit.setEnabled(enabled and self.use_px_cb.isChecked())
        self.server_edit.setEnabled(enabled and not self.auto_detect_cb.isChecked() and not self.use_px_cb.isChecked())
        self.port_edit.setEnabled(enabled and not self.auto_detect_cb.isChecked() and not self.use_px_cb.isChecked())
        self.username_edit.setEnabled(enabled and not self.use_px_cb.isChecked())
        self.password_edit.setEnabled(enabled and not self.use_px_cb.isChecked())
        self.auto_detect_cb.setEnabled(enabled and not self.use_px_cb.isChecked())
    
    def on_use_px_changed(self):
        """Handle PX enable/disable."""
        self.on_proxy_enabled_changed()  # Refresh all controls
    
    def on_auto_detect_changed(self):
        """Handle auto-detect change."""
        self.on_proxy_enabled_changed()  # Refresh all controls
    
    def test_proxy(self):
        """Test the proxy configuration."""
        if not self.enable_proxy_cb.isChecked():
            QMessageBox.information(self, "Test Result", "Proxy is disabled.")
            return
        
        # Get proxy settings
        config = self.get_current_config()
        
        try:
            import urllib.request
            import urllib.error
            
            # Configure proxy
            if config.get('use_px'):
                # Use PX proxy
                px_port = config.get('px_port', 3128)
                proxy_url = f"http://127.0.0.1:{px_port}"
                proxy_handler = urllib.request.ProxyHandler({
                    'http': proxy_url,
                    'https': proxy_url
                })
            elif config.get('auto_detect'):
                # Use system proxy
                proxy_handler = urllib.request.ProxyHandler()
            else:
                server = config.get('server', '').strip()
                port = config.get('port', '').strip()
                
                if not server or not port:
                    QMessageBox.warning(self, "Test Failed", "Please enter proxy server and port.")
                    return
                
                # Build proxy URL
                proxy_url = f"http://{server}:{port}"
                if config.get('username') and config.get('password'):
                    username = config['username']
                    password = config['password']
                    proxy_url = f"http://{username}:{password}@{server}:{port}"
                
                proxy_handler = urllib.request.ProxyHandler({
                    'http': proxy_url,
                    'https': proxy_url
                })
            
            opener = urllib.request.build_opener(proxy_handler)
            urllib.request.install_opener(opener)
            
            # Test connection to Microsoft's PsExec download
            test_url = "https://download.sysinternals.com/files/PSTools.zip"
            request = urllib.request.Request(test_url, method='HEAD')
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    QMessageBox.information(self, "Test Successful", 
                                          "Proxy connection test successful! ✅\n"
                                          "Third-party tool downloads should work with these settings.")
                else:
                    QMessageBox.warning(self, "Test Failed", 
                                      f"Unexpected response code: {response.status}")
        
        except urllib.error.URLError as e:
            error_msg = str(e)
            if "407" in error_msg or "Proxy Authentication Required" in error_msg:
                QMessageBox.critical(self, "Proxy Authentication Required", 
                                   "❌ Error 407: Proxy Authentication Required\n\n" 
                                   "This usually means px.exe is not running or not configured properly.\n\n"
                                   "For corporate networks:\n"
                                   "• Make sure px.exe is running in the background\n"
                                   "• px.exe should handle Windows authentication automatically\n"
                                   "• Check your px.ini configuration file\n\n"
                                   "Manual credentials are usually NOT required with px.exe.")
            else:
                QMessageBox.critical(self, "Test Failed", 
                                   f"Proxy connection failed:\n{error_msg}\n\n"
                                   "Please check your proxy settings.")
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", 
                               f"Test error: {str(e)}")
    
    def get_current_config(self) -> Dict:
        """Get current proxy configuration."""
        config = {
            'enabled': self.enable_proxy_cb.isChecked(),
            'use_px': self.use_px_cb.isChecked(),
            'px_port': int(self.px_port_edit.text()) if self.px_port_edit.text().isdigit() else 3128,
            'auto_detect': self.auto_detect_cb.isChecked(),
            'server': self.server_edit.text().strip(),
            'port': self.port_edit.text().strip(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text().strip(),
        }
        return config
    
    def save_settings(self):
        """Save proxy settings and close dialog."""
        config = self.get_current_config()
        
        # Validate settings if proxy is enabled
        if config['enabled']:
            if config['use_px']:
                # Validate PX port
                try:
                    port = int(config['px_port'])
                    if not (1 <= port <= 65535):
                        raise ValueError()
                except (ValueError, TypeError):
                    QMessageBox.warning(self, "Invalid PX Port", 
                                      "Please enter a valid PX port number (1-65535).")
                    return
            elif not config['auto_detect']:
                if not config['server'] or not config['port']:
                    QMessageBox.warning(self, "Invalid Settings", 
                                      "Please enter proxy server and port.")
                    return
                
                # Validate port number
                try:
                    port = int(config['port'])
                    if not (1 <= port <= 65535):
                        raise ValueError()
                except ValueError:
                    QMessageBox.warning(self, "Invalid Port", 
                                      "Please enter a valid port number (1-65535).")
                    return
        
        # Save configuration
        self.save_proxy_config(config)
        
        # Show confirmation
        if config['enabled']:
            if config['use_px']:
                msg = f"Proxy enabled using px.exe on port {config['px_port']}."
            elif config['auto_detect']:
                msg = "Proxy enabled with auto-detection."
            else:
                msg = f"Proxy enabled: {config['server']}:{config['port']}"
        else:
            msg = "Proxy disabled."
        
        QMessageBox.information(self, "Settings Saved", f"{msg}\n\nSettings saved successfully!")
        self.accept()
    
    def load_saved_settings(self):
        """Load previously saved settings."""
        config = self.proxy_config
        
        self.enable_proxy_cb.setChecked(config.get('enabled', False))
        self.use_px_cb.setChecked(config.get('use_px', True))  # Default to PX
        self.px_port_edit.setText(str(config.get('px_port', 3128)))
        self.auto_detect_cb.setChecked(config.get('auto_detect', False))
        self.server_edit.setText(config.get('server', ''))
        self.port_edit.setText(config.get('port', ''))
        self.username_edit.setText(config.get('username', ''))
        # Don't load password for security
    
    def get_config_file_path(self) -> Path:
        """Get path to proxy configuration file."""
        # Store in user's AppData directory
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        config_dir = Path(app_data) / 'SSH_Tools_Suite'
        config_dir.mkdir(exist_ok=True)
        return config_dir / 'proxy_config.json'
    
    def load_proxy_config(self) -> Dict:
        """Load proxy configuration from file."""
        config_file = self.get_config_file_path()
        try:
            if config_file.exists():
                with open(config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {}
    
    def save_proxy_config(self, config: Dict):
        """Save proxy configuration to file."""
        config_file = self.get_config_file_path()
        try:
            # Don't save password to file
            config_to_save = config.copy()
            config_to_save.pop('password', None)
            
            with open(config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save configuration: {str(e)}")
    
    def update_px_status(self):
        """Update px.exe status display."""
        try:
            import subprocess
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True, timeout=5)
            px_running = ':3128' in result.stdout and 'LISTENING' in result.stdout
            
            if px_running:
                self.px_status_label.setText("🟢 px.exe is running on port 3128")
                self.px_status_label.setStyleSheet("color: green;")
                self.start_px_btn.setEnabled(False)
                self.stop_px_btn.setEnabled(True)
            else:
                self.px_status_label.setText("🔴 px.exe is not running")
                self.px_status_label.setStyleSheet("color: red;")
                self.start_px_btn.setEnabled(True)
                self.stop_px_btn.setEnabled(False)
        except Exception:
            self.px_status_label.setText("❓ Unable to check px.exe status")
            self.px_status_label.setStyleSheet("color: orange;")
    
    def start_px_exe(self):
        """Start px.exe from user config directory (new structure)."""
        try:
            import os
            import subprocess
            from pathlib import Path
            # Use the config dir where px.exe is extracted by the installer
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = Path(app_data) / 'SSH_Tools_Suite' / 'ThirdPartyInstaller'
            px_path = config_dir / 'px.exe'
            if not px_path.exists():
                QMessageBox.warning(self, "px.exe Not Found", 
                                  f"px.exe not found in config directory:\n{px_path}\n\n"
                                  f"Expected location: {px_path}")
                return
            subprocess.Popen([str(px_path)], 
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            import time
            time.sleep(2)
            self.update_px_status()
            QMessageBox.information(self, "px.exe Started", 
                                  "px.exe has been started successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error Starting px.exe", 
                               f"Could not start px.exe:\n{str(e)}")

    def stop_px_exe(self):
        """Stop px.exe process."""
        try:
            import subprocess
            import os
            
            if os.name == 'nt':
                # Windows
                subprocess.run(['taskkill', '/F', '/IM', 'px.exe'], 
                             capture_output=True, timeout=10)
            else:
                # Unix-like
                subprocess.run(['pkill', 'px'], capture_output=True, timeout=10)
            
            # Update status
            self.update_px_status()
            
            QMessageBox.information(self, "px.exe Stopped", 
                                  "px.exe has been stopped.")
        except Exception as e:
            QMessageBox.warning(self, "Error Stopping px.exe", 
                              f"Could not stop px.exe:\n{str(e)}")
    
    def configure_px_ini(self):
        """Open px.ini configuration from user config directory (new structure)."""
        try:
            import os
            import subprocess
            from pathlib import Path
            app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
            config_dir = Path(app_data) / 'SSH_Tools_Suite' / 'ThirdPartyInstaller'
            px_ini_path = config_dir / 'px.ini'
            if not px_ini_path.exists():
                QMessageBox.warning(self, "px.ini Not Found", 
                                  f"px.ini not found in config directory:\n{px_ini_path}\n\n"
                                  f"Expected location: {px_ini_path}")
                return
            if os.name == 'nt':
                os.startfile(str(px_ini_path))
            else:
                subprocess.run(['xdg-open', str(px_ini_path)])
        except Exception as e:
            QMessageBox.critical(self, "Error Opening px.ini", 
                               f"Could not open px.ini:\n{str(e)}")

    def check_proxy_environment(self):
        """Check current proxy environment variables and show status."""
        try:
            import os
            
            # Get current environment variables
            http_proxy = os.environ.get('http_proxy', '').strip()
            https_proxy = os.environ.get('https_proxy', '').strip()
            HTTP_PROXY = os.environ.get('HTTP_PROXY', '').strip()
            HTTPS_PROXY = os.environ.get('HTTPS_PROXY', '').strip()
            
            # Read px.ini to get configured port
            px_port = 3128  # default
            try:
                tools_dir = Path(__file__).parent.parent.parent.parent / "tools"
                px_ini_path = tools_dir / "px" / "px.ini"
                
                if px_ini_path.exists():
                    with open(px_ini_path, 'r') as f:
                        content = f.read()
                        for line in content.split('\n'):
                            if 'port' in line.lower() and '=' in line:
                                try:
                                    port_value = line.split('=')[1].strip()
                                    px_port = int(port_value)
                                    break
                                except (ValueError, IndexError):
                                    continue
            except Exception:
                pass  # Use default port
            
            # Build status message
            status_msg = "Current Proxy Environment Variables:\n\n"
            
            # Check each variable
            if http_proxy or HTTP_PROXY:
                status_msg += f"✅ http_proxy: {http_proxy or HTTP_PROXY}\n"
            else:
                status_msg += f"❌ http_proxy: Not set\n"
            
            if https_proxy or HTTPS_PROXY:
                status_msg += f"✅ https_proxy: {https_proxy or HTTPS_PROXY}\n"
            else:
                status_msg += f"❌ https_proxy: Not set\n"
            
            status_msg += f"\n💡 PX Configuration:\n"
            status_msg += f"   • Configured port: {px_port}\n"
            status_msg += f"   • Recommended proxy: localhost:{px_port}\n\n"
            
            # Add tips for setting environment variables
            if not http_proxy and not HTTP_PROXY:
                status_msg += "📋 To set proxy environment variables:\n"
                status_msg += f"   set http_proxy=http://localhost:{px_port}\n"
                status_msg += f"   set https_proxy=http://localhost:{px_port}\n\n"
                status_msg += "Or for current session only:\n"
                status_msg += f"   set HTTP_PROXY=http://localhost:{px_port}\n"
                status_msg += f"   set HTTPS_PROXY=http://localhost:{px_port}\n\n"
            
            status_msg += "🔧 Note: These environment variables help command-line tools\n"
            status_msg += "use the proxy. The Third Party Installer uses its own proxy\n"
            status_msg += "configuration from the 'Proxy Settings' section above."
            
            # Show in a message box with monospace font for better formatting
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Proxy Environment Status")
            msg_box.setText(status_msg)
            msg_box.setFont(QFont("Consolas", 9))
            msg_box.exec()
                
        except Exception as e:
            QMessageBox.critical(self, "Error Checking Environment", 
                               f"Could not check proxy environment:\n{str(e)}")

class ThirdPartyInstallerGUI(QMainWindow):
    """Main GUI for the Third Party Installer."""
    
    def __init__(self):
        super().__init__()
        self.installer = ThirdPartyInstaller()
        self.tool_widgets = {}
        self.installation_worker = None
        
        self.setWindowTitle("SSH Tools Suite - Third Party Installer")
        self.setGeometry(100, 100, 800, 750)  # Made taller (was 600)
        
        self.setup_ui()
        self.check_installation_status()
    
    def setup_ui(self):
        """Setup the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header
        header_label = QLabel("Third Party Tools Installation")
        header_label.setFont(QFont("", 16, QFont.Bold))
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel(
            "This installer manages third-party tools required by the SSH Tools Suite. "
            "Required tools must be installed before you can use the main applications."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin: 10px;")
        layout.addWidget(desc_label)
        
        # Tools list
        tools_group = QGroupBox("Available Tools")
        tools_layout = QVBoxLayout(tools_group)
        
        # Scroll area for tools
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.tools_layout = QVBoxLayout(scroll_widget)
        
        # Create tool widgets
        for tool_name, tool in self.installer.tools_config.items():
            status = self.installer.get_tool_status(tool_name)
            widget = ToolStatusWidget(tool, status)
            self.tool_widgets[tool_name] = widget
            self.tools_layout.addWidget(widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        tools_layout.addWidget(scroll_area)
        
        layout.addWidget(tools_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.proxy_btn = QPushButton("Proxy Settings")
        self.proxy_btn.clicked.connect(self.open_proxy_settings)
        button_layout.addWidget(self.proxy_btn)
        
        self.refresh_btn = QPushButton("Refresh Status")
        self.refresh_btn.clicked.connect(self.refresh_status)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        self.install_selected_btn = QPushButton("Install Selected")
        self.install_selected_btn.clicked.connect(self.install_selected_tools)
        self.install_selected_btn.setStyleSheet("QPushButton { background-color: #0066cc; color: white; font-weight: bold; }")
        button_layout.addWidget(self.install_selected_btn)
        
        self.install_required_btn = QPushButton("Install Required Only")
        self.install_required_btn.clicked.connect(self.install_required_tools)
        self.install_required_btn.setStyleSheet("QPushButton { background-color: #cc6600; color: white; font-weight: bold; }")
        button_layout.addWidget(self.install_required_btn)
        
        layout.addLayout(button_layout)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Log area
        log_group = QGroupBox("Installation Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
    
    def check_installation_status(self):
        """Check and display installation status."""
        self.installer._check_all_tools_status()
        
        # Update tool widgets
        for tool_name, widget in self.tool_widgets.items():
            status = self.installer.get_tool_status(tool_name)
            widget.status = status
            widget.update_status_display()
            widget.install_checkbox.setChecked(status != InstallationStatus.INSTALLED)
            widget.install_checkbox.setEnabled(status != InstallationStatus.INSTALLED)
        
        # Check if installation is complete
        if self.installer.is_installation_complete():
            self.status_label.setText("✅ All required tools are installed!")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            missing = self.installer.get_missing_required_tools()
            self.status_label.setText(f"❌ Missing required tools: {', '.join(missing)}")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
        
        self.log(f"Status check completed. Installation complete: {self.installer.is_installation_complete()}")
    
    def refresh_status(self):
        """Refresh the installation status."""
        self.log("Refreshing installation status...")
        self.check_installation_status()
    
    def open_proxy_settings(self):
        """Open proxy settings dialog."""
        dialog = ProxyConfigDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # Reload proxy config
            self.installer.proxy_config = self.installer._load_proxy_config()
            self.log("Proxy configuration updated.")
    
    def install_selected_tools(self):
        """Install all selected tools."""
        selected_tools = []
        
        for tool_name, widget in self.tool_widgets.items():
            if widget.is_selected_for_installation():
                selected_tools.append(tool_name)
        
        if not selected_tools:
            QMessageBox.information(self, "No Tools Selected", "Please select tools to install.")
            return
        
        self.start_installation(selected_tools)
    
    def install_required_tools(self):
        """Install only the required tools."""
        required_tools = []
        
        for tool_name, tool in self.installer.tools_config.items():
            if tool.required and self.installer.get_tool_status(tool_name) != InstallationStatus.INSTALLED:
                required_tools.append(tool_name)
        
        if not required_tools:
            QMessageBox.information(self, "No Required Tools", "All required tools are already installed.")
            return
        
        self.start_installation(required_tools)
    
    def start_installation(self, tools_to_install: List[str]):
        """Start the installation process."""
        if self.installation_worker and self.installation_worker.isRunning():
            QMessageBox.warning(self, "Installation in Progress", "Another installation is already in progress.")
            return
        
        # Confirm installation
        tool_names = [self.installer.tools_config[name].display_name for name in tools_to_install]
        reply = QMessageBox.question(
            self,
            "Confirm Installation",
            f"Install the following tools?\n\n{chr(10).join(tool_names)}\n\n"
            "This may take several minutes and requires administrator privileges for some tools.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Disable buttons
        self.install_selected_btn.setEnabled(False)
        self.install_required_btn.setEnabled(False)
        self.refresh_btn.setEnabled(False)
        
        # Reset tool widget states
        for tool_name in tools_to_install:
            if tool_name in self.tool_widgets:
                widget = self.tool_widgets[tool_name]
                widget.progress_bar.setValue(0)
                widget.progress_bar.setVisible(True)
                widget.status_message.setText("Preparing...")
                widget.status_message.setVisible(True)
        
        self.log(f"Starting installation of {len(tools_to_install)} tools...")
        
        # Start worker thread
        self.installation_worker = InstallationWorker(self.installer, tools_to_install)
        self.installation_worker.progress_updated.connect(self.on_installation_progress)
        self.installation_worker.installation_finished.connect(self.on_tool_installation_finished)
        self.installation_worker.all_installations_finished.connect(self.on_all_installations_finished)
        self.installation_worker.start()
    
    def on_installation_progress(self, tool_name: str, progress: int, message: str):
        """Handle installation progress updates."""
        if tool_name in self.tool_widgets:
            self.tool_widgets[tool_name].set_installation_progress(progress, message)
        
        self.log(f"{tool_name}: {message}")
    
    def on_tool_installation_finished(self, tool_name: str, success: bool, message: str):
        """Handle individual tool installation completion."""
        if tool_name in self.tool_widgets:
            self.tool_widgets[tool_name].set_installation_finished(success, message)
        
        if success:
            self.log(f"✅ {tool_name}: {message}")
        else:
            self.log(f"❌ {tool_name}: {message}")
    
    def on_all_installations_finished(self, success: bool):
        """Handle completion of all installations."""
        # Re-enable buttons
        self.install_selected_btn.setEnabled(True)
        self.install_required_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        
        # Update status
        self.check_installation_status()
        
        if success:
            self.log("🎉 All installations completed successfully!")
            
            # Check if all required tools are now installed
            if self.installer.is_installation_complete():
                QMessageBox.information(
                    self,
                    "Installation Complete",
                    "All required tools have been installed successfully!\n\n"
                    "You can now use the SSH Tools Suite applications."
                )
        else:
            self.log("❌ Some installations failed. Please check the log for details.")
            QMessageBox.warning(
                self,
                "Installation Issues",
                "Some tools failed to install. Please check the log for details.\n\n"
                "You may need to install them manually or check your proxy settings."
            )
    
    def log(self, message: str):
        """Add a message to the log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Handle window close event."""
        if self.installation_worker and self.installation_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Installation in Progress",
                "Installation is in progress. Do you want to cancel it and exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            else:
                # Stop the worker
                self.installation_worker.stop()
                self.installation_worker.wait(3000)  # Wait up to 3 seconds
        
        # Cleanup installer
        self.installer.cleanup()
        event.accept()


def main():
    """Main function for running the installer standalone."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Third Party Installer")
    app.setApplicationDisplayName("SSH Tools Suite - Third Party Installer")
    app.setApplicationVersion("1.0.1")
    
    # Create and show the installer window
    installer = ThirdPartyInstallerGUI()
    installer.show()
    
    # Check if we need to show a warning about required tools
    if not installer.installer.is_installation_complete():
        missing_tools = installer.installer.get_missing_required_tools()
        tool_names = [installer.installer.tools_config[name].display_name for name in missing_tools]
        
        QMessageBox.warning(
            installer,
            "Required Tools Missing",
            f"The following required tools are not installed:\n\n{chr(10).join(tool_names)}\n\n"
            "Please install these tools before using the SSH Tools Suite."
        )
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
