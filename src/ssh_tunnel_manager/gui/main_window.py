#!/usr/bin/env python3
"""
SSH Tunnel Manager - Simplified Main Window
"""

import sys
import webbrowser
from pathlib import Path
from typing import Dict, Optional

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter, 
    QSystemTrayIcon, QMenu, QApplication, QMessageBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QBrush

from ..core.models import TunnelConfig
from ..core.config_manager import ConfigurationManager
from ..core.tunnel_process import TunnelProcess
from ..core.monitor import TunnelMonitorThread
from ..core.constants import APP_NAME

from .components.toolbar import ToolbarManager
from .components.table_widget import TunnelTableWidget
from .components.log_widget import LogWidget
from .components.file_operations import FileOperationsManager
from .components.rtsp_handler import RTSPHandler
from .components.rdp_handler import RDPHandler
from .components.network_scanner import NetworkScannerManager

# Import SSH key setup dialog
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from .components.powershell_generator import PowerShellGeneratorManager
from .components.ssh_key_generator import SSHKeyManager
from .components.ssh_key_deployment import SSHKeyDeploymentManager


class SSHTunnelManager(QMainWindow):
    """Simplified SSH Tunnel Manager with clean component-based architecture."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} - Professional")
        self.setGeometry(100, 100, 1000, 700)
        
        # Core managers
        self.config_manager = ConfigurationManager()
        self.active_tunnels: Dict[str, TunnelProcess] = {}
        
        # UI Components
        self.toolbar_manager = ToolbarManager(self)
        self.table_widget = TunnelTableWidget(self)
        self.log_widget = LogWidget(self)
        self.file_ops_manager = FileOperationsManager(self)
        self.rtsp_handler = RTSPHandler(self)
        self.rdp_handler = RDPHandler(self)
        self.network_scanner = NetworkScannerManager(self)
        self.powershell_generator = PowerShellGeneratorManager(self)
        self.ssh_key_manager = SSHKeyManager(self)
        self.ssh_key_deployment = SSHKeyDeploymentManager(self)
        
        # Setup
        self._setup_ui()
        self._setup_connections()
        self._setup_menu()
        self._setup_system_tray()
        
        # Initialize data
        self._load_configurations()
        self._start_monitoring()
    
    def _setup_ui(self):
        """Setup the main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Toolbar
        toolbar_layout = self.toolbar_manager.create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # Main content splitter
        content_splitter = QSplitter(Qt.Vertical)
        
        # Table
        table = self.table_widget.create_table()
        content_splitter.addWidget(table)
        
        # Log
        log_group = self.log_widget.create_log_widget()
        content_splitter.addWidget(log_group)
        
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Initial log
        self.log("SSH Tunnel Manager started")
    
    def _setup_connections(self):
        """Connect component signals."""
        # Toolbar signals
        self.toolbar_manager.add_tunnel.connect(self._add_tunnel)
        self.toolbar_manager.edit_tunnel.connect(self._edit_tunnel)
        self.toolbar_manager.delete_tunnel.connect(self._delete_tunnel)
        self.toolbar_manager.start_tunnel.connect(self._start_tunnel)
        self.toolbar_manager.stop_tunnel.connect(self._stop_tunnel)
        self.toolbar_manager.test_tunnel.connect(self._test_tunnel)
        self.toolbar_manager.browse_files.connect(self._browse_files)
        self.toolbar_manager.browse_remote_files.connect(self._browse_remote_files)
        self.toolbar_manager.open_web_browser.connect(self._open_web_browser)
        self.toolbar_manager.launch_rtsp.connect(self.rtsp_handler.launch_rtsp)
        self.toolbar_manager.launch_rdp.connect(self.rdp_handler.launch_rdp)
        self.toolbar_manager.show_network_scanner.connect(self.network_scanner.show_scanner)
        self.toolbar_manager.show_powershell_generator.connect(self.powershell_generator.show_generator)
        
        # Table selection
        self.table_widget.selection_changed.connect(self._on_selection_changed)
        
        # Table context menu
        self.table_widget.context_menu_start.connect(self._start_tunnel_by_name)
        self.table_widget.context_menu_stop.connect(self._stop_tunnel_by_name)
        self.table_widget.context_menu_browse_files.connect(self._browse_files_by_name)
        self.table_widget.context_menu_browse_remote_files.connect(self._browse_remote_files_by_name)
        self.table_widget.context_menu_launch_rtsp.connect(self.rtsp_handler.launch_rtsp_by_name)
        self.table_widget.context_menu_launch_rdp.connect(self.rdp_handler.launch_rdp_by_name)
        self.table_widget.context_menu_deploy_ssh_key.connect(self._deploy_ssh_key_by_name)
        
        # File operations
        self.file_ops_manager.log_message.connect(self.log)
        self.file_ops_manager.tunnel_needed.connect(self._start_tunnel_by_name)
        self.file_ops_manager.refresh_table.connect(self._refresh_table)
        self.file_ops_manager.set_managers(self.config_manager, self.active_tunnels)
        
        # Setup RTSP handler
        self.rtsp_handler.set_managers(self.config_manager, self.active_tunnels, self.log)
        
        # Setup RDP handler
        self.rdp_handler.set_managers(self.config_manager, self.active_tunnels, self.log)
    
    def _setup_menu(self):
        """Setup minimal menu."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        ssh_key_action = QAction("🔑 Generate SSH Key...", self)
        ssh_key_action.triggered.connect(self._setup_ssh_key)
        tools_menu.addAction(ssh_key_action)
        
        deploy_key_action = QAction("📤 Deploy SSH Key...", self)
        deploy_key_action.triggered.connect(self._deploy_ssh_key)
        tools_menu.addAction(deploy_key_action)
        
        powershell_action = QAction("📜 PowerShell SSH Setup...", self)
        powershell_action.triggered.connect(self.powershell_generator.show_generator)
        tools_menu.addAction(powershell_action)
        
        tools_menu.addSeparator()
        network_scanner_action = QAction("🔍 Network Scanner", self)
        network_scanner_action.triggered.connect(self.network_scanner.show_scanner)
        tools_menu.addAction(network_scanner_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_system_tray(self):
        """Setup system tray."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        
        # Create icon
        try:
            icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
            if icon.isNull():
                pixmap = QPixmap(16, 16)
                pixmap.fill(Qt.blue)
                icon = QIcon(pixmap)
        except:
            icon = QIcon()
        
        self.tray_icon.setIcon(icon)
        self.tray_icon.setToolTip("SSH Tunnel Manager")
        
        # Tray menu
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self._quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
    
    def _load_configurations(self):
        """Load and display configurations."""
        self.config_manager.load_configurations()
        self._refresh_table()
    
    def _start_monitoring(self):
        """Start tunnel monitoring."""
        self.monitor_thread = TunnelMonitorThread(self.active_tunnels)
        self.monitor_thread.status_update.connect(self._update_tunnel_status)
        self.monitor_thread.connection_lost.connect(self._handle_connection_lost)
        self.monitor_thread.start()
    
    def _refresh_table(self):
        """Refresh the tunnel table."""
        configs = self.config_manager.get_all_configurations()
        self.table_widget.refresh_table(configs, self.active_tunnels)
    
    def _on_selection_changed(self, selected: bool, config_name: str):
        """Handle table selection changes."""
        if selected and config_name:
            config = self.config_manager.get_configuration(config_name)
            is_running = config_name in self.active_tunnels and self.active_tunnels[config_name].is_running
            
            # Determine service capabilities
            web_enabled = (config and config.tunnel_type == 'local' and 
                         config.remote_port in [80, 443, 8080, 8443, 8000, 3000, 5000, 9000])
            rtsp_enabled = (config and config.tunnel_type == 'local' and 
                          config.remote_port in [554, 8554])
            rdp_enabled = (config and config.tunnel_type == 'local' and 
                         config.remote_port == 3389)  # Standard RDP port
            
            self.toolbar_manager.update_button_states(True, is_running, web_enabled, rtsp_enabled, rdp_enabled)
        else:
            self.toolbar_manager.update_button_states(False)
    
    def _update_tunnel_status(self, name: str, is_running: bool):
        """Update tunnel status from monitor."""
        if name in self.active_tunnels:
            self.active_tunnels[name].is_running = is_running
        self._refresh_table()
    
    def _handle_connection_lost(self, name: str):
        """Handle connection lost event (limited to 10 messages)."""
        self.log(f"⚠️ Tunnel {name} disconnected unexpectedly")
    
    # Action handlers (simplified - delegate to main_window_actions.py)
    def _add_tunnel(self):
        """Add tunnel - delegate to actions."""
        from .main_window_actions import MainWindowActions
        actions = MainWindowActions()
        actions.config_manager = self.config_manager
        actions.log = self.log
        actions.refresh_table = self._refresh_table
        actions.parent_widget = self  # Set the parent widget
        actions.add_tunnel(parent=self)  # Pass self as parent
    
    def _edit_tunnel(self):
        """Edit tunnel - delegate to actions."""
        from PySide6.QtWidgets import QMessageBox, QDialog
        
        config_name = self.table_widget.get_selected_config_name()
        if not config_name:
            QMessageBox.information(self, "Information", "Please select a tunnel to edit.")
            return
        
        config = self.config_manager.get_configuration(config_name)
        if not config:
            QMessageBox.warning(self, "Error", f"Configuration '{config_name}' not found.")
            return
        
        from ssh_tunnel_manager.gui.dialogs.tunnel_config import TunnelConfigDialog
        dialog = TunnelConfigDialog(config=config, parent=self)
        if dialog.exec() == QDialog.Accepted:
            updated_config = dialog.get_config()
            
            success, error_msg = self.config_manager.update_configuration(config_name, updated_config)
            if success:
                self._refresh_table()
                self.log(f"Updated tunnel configuration: {updated_config.name}")
            else:
                QMessageBox.warning(self, "Error", error_msg)
    
    def _delete_tunnel(self):
        """Delete tunnel."""
        from PySide6.QtWidgets import QMessageBox
        
        config_name = self.table_widget.get_selected_config_name()
        if not config_name:
            QMessageBox.information(self, "Information", "Please select a tunnel to delete.")
            return
        
        # Ask for confirmation
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete tunnel '{config_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop tunnel if running
            if config_name in self.active_tunnels:
                self.active_tunnels[config_name].stop()
                del self.active_tunnels[config_name]
            
            # Remove from configurations
            success = self.config_manager.delete_configuration(config_name)
            if success:
                self._refresh_table()
                self.log(f"Deleted tunnel configuration: {config_name}")
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete configuration '{config_name}'")
    
    def _start_tunnel(self):
        """Start selected tunnel."""
        config_name = self.table_widget.get_selected_config_name()
        if config_name:
            self._start_tunnel_by_name(config_name)
    
    def _start_tunnel_by_name(self, config_name: str):
        """Start tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if not config:
            return
        
        self.log(f"🚀 Starting tunnel: {config_name}")
        
        if config_name not in self.active_tunnels:
            self.active_tunnels[config_name] = TunnelProcess(config, None)
        
        tunnel = self.active_tunnels[config_name]
        
        # Set to starting status and refresh table to show yellow indicator
        tunnel.status = tunnel.STATUS_STARTING
        self._refresh_table()
        
        if tunnel.start():
            self.log(f"✅ Tunnel started: {config_name}")
            self._refresh_table()
        else:
            self.log(f"❌ Failed to start tunnel: {config_name}")
            self._refresh_table()
    
    def _stop_tunnel(self):
        """Stop selected tunnel."""
        config_name = self.table_widget.get_selected_config_name()
        if not config_name or config_name not in self.active_tunnels:
            return
        
        self.log(f"🛑 Stopping tunnel: {config_name}")
        tunnel = self.active_tunnels[config_name]
        tunnel.stop()
        self._refresh_table()
    
    def _test_tunnel(self):
        """Test tunnel connection."""
        from PySide6.QtWidgets import QMessageBox
        from ..utils.connection_tester import ConnectionTester
        
        config_name = self.table_widget.get_selected_config_name()
        if not config_name:
            QMessageBox.information(self, "Information", "Please select a tunnel to test.")
            return
            
        config = self.config_manager.get_configuration(config_name)
        if not config:
            QMessageBox.warning(self, "Error", f"Configuration '{config_name}' not found.")
            return
            
        # Check if tunnel is running
        is_running = config_name in self.active_tunnels and self.active_tunnels[config_name].is_running
        if not is_running:
            QMessageBox.warning(self, "Test Error", f"Tunnel '{config_name}' is not running. Please start the tunnel first.")
            return
            
        self.log(f"🧪 Testing tunnel: {config_name}")
        
        try:
            if config.tunnel_type == 'local':
                # Test local port connectivity
                if ConnectionTester.test_local_port(config.local_port):
                    self.log(f"✅ Local port {config.local_port} is accessible")
                    
                    # Test tunnel connection
                    success, message = ConnectionTester.test_tunnel_connection(config)
                    if success:
                        self.log(f"✅ {message}")
                        QMessageBox.information(self, "Test Result", 
                                              f"✅ Tunnel '{config_name}' is working correctly!\n\n{message}")
                    else:
                        self.log(f"⚠️ {message}")
                        QMessageBox.warning(self, "Test Result",
                                          f"⚠️ Tunnel '{config_name}' has issues:\n\n{message}")
                else:
                    self.log(f"❌ Local port {config.local_port} is not accessible")
                    QMessageBox.critical(self, "Test Result",
                                       f"❌ Tunnel '{config_name}' test failed!\n\n"
                                       f"Local port {config.local_port} is not accessible")
                    
            elif config.tunnel_type == 'dynamic':
                # Test SOCKS proxy
                if ConnectionTester.test_local_port(config.local_port):
                    self.log(f"✅ SOCKS proxy on port {config.local_port} is accessible")
                    QMessageBox.information(self, "Test Result",
                                          f"✅ SOCKS proxy '{config_name}' is working!\n\n"
                                          f"Proxy available on localhost:{config.local_port}")
                else:
                    self.log(f"❌ SOCKS proxy port {config.local_port} is not accessible")
                    QMessageBox.critical(self, "Test Result",
                                       f"❌ SOCKS proxy '{config_name}' test failed!\n\n"
                                       f"Port {config.local_port} is not accessible")
            else:
                # Remote tunnel
                self.log(f"ℹ️ Remote tunnel testing limited - check remote server")
                QMessageBox.information(self, "Test Result",
                                     f"ℹ️ Remote tunnel '{config_name}' status:\n\n"
                                     f"The tunnel appears to be running, but remote tunnels "
                                     f"can only be tested from the remote server side.")
        except Exception as e:
            self.log(f"❌ Error testing tunnel: {str(e)}")
            QMessageBox.critical(self, "Test Error", f"Test failed: {str(e)}")
    
    def _browse_files(self):
        """Browse files via SFTP."""
        config_name = self.table_widget.get_selected_config_name()
        if not config_name:
            return
        
        config = self.config_manager.get_configuration(config_name)
        if config:
            self.file_ops_manager.browse_files(config_name, config)
    
    def _browse_remote_files(self):
        """Browse files on the remote host (destination of the tunnel) via SFTP."""
        config_name = self.table_widget.get_selected_config_name()
        if not config_name:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Information", "Please select a tunnel to browse remote files.")
            return
        
        config = self.config_manager.get_configuration(config_name)
        if config:
            self.file_ops_manager.browse_remote_files(config_name, config)
    
    def _open_web_browser(self):
        """Open web browser for tunnel."""
        config_name = self.table_widget.get_selected_config_name()
        config = self.config_manager.get_configuration(config_name)
        if config and config.tunnel_type == 'local':
            url = f"http://localhost:{config.local_port}"
            webbrowser.open(url)
            self.log(f"🌐 Opened web browser: {url}")
    
    def _setup_ssh_key(self):
        """Setup SSH key."""
        # Get currently selected tunnel config if any
        config_name = self.table_widget.get_selected_config_name()
        tunnel_config = None
        if config_name:
            tunnel_config = self.config_manager.get_configuration(config_name)
            if tunnel_config:
                tunnel_config = {
                    'name': config_name,
                    'host': tunnel_config.ssh_host,
                    'port': tunnel_config.ssh_port,
                    'username': tunnel_config.ssh_user
                }
        
        self.ssh_key_manager.show_key_generator(tunnel_config)
    
    def _deploy_ssh_key(self):
        """Deploy SSH key to server."""
        # Get currently selected tunnel config if any
        config_name = self.table_widget.get_selected_config_name()
        tunnel_config = None
        if config_name:
            tunnel_config = self.config_manager.get_configuration(config_name)
            if tunnel_config:
                tunnel_config = {
                    'name': config_name,
                    'host': tunnel_config.ssh_host,
                    'port': tunnel_config.ssh_port,
                    'username': tunnel_config.ssh_user
                }
        
        self.ssh_key_deployment.deploy_key_for_tunnel(tunnel_config)
    
    def _deploy_ssh_key_by_name(self, config_name: str):
        """Deploy SSH key for a specific tunnel by name."""
        tunnel_config = self.config_manager.get_configuration(config_name)
        if tunnel_config:
            tunnel_config_dict = {
                'name': config_name,
                'host': tunnel_config.ssh_host,
                'port': tunnel_config.ssh_port,
                'username': tunnel_config.ssh_user
            }
            self.ssh_key_deployment.deploy_key_for_tunnel(tunnel_config_dict)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(self, "About", f"{APP_NAME}\nProfessional SSH Tunnel Manager")
    
    def log(self, message: str):
        """Log a message."""
        self.log_widget.log(message)
    
    def closeEvent(self, event):
        """Handle close event."""
        if QSystemTrayIcon.isSystemTrayAvailable() and hasattr(self, 'tray_icon'):
            self.hide()
            event.ignore()
        else:
            self._quit_application()
    
    def _quit_application(self):
        """Quit application."""
        # Stop all tunnels
        for tunnel in self.active_tunnels.values():
            tunnel.stop()
        
        # Stop monitoring
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        
        QApplication.quit()

    def _stop_tunnel_by_name(self, config_name: str):
        """Stop tunnel by name."""
        if config_name in self.active_tunnels:
            self.log(f"🛑 Stopping tunnel: {config_name}")
            tunnel = self.active_tunnels[config_name]
            tunnel.stop()
            self._refresh_table()
    
    def _browse_files_by_name(self, config_name: str):
        """Browse files for a specific tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if config:
            self.file_ops_manager.browse_files(config_name, config)
    
    def _browse_remote_files_by_name(self, config_name: str):
        """Browse remote files for a specific tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if config:
            self.file_ops_manager.browse_remote_files(config_name, config)
