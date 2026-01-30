#!/usr/bin/env python3
"""
SSH Tunnel Manager - Professional Enterprise Interface
Clean, purposeful, information-dense design inspired by Linear and VS Code
"""

import sys
import webbrowser
from pathlib import Path
from typing import Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QSplitter,
    QSystemTrayIcon, QMenu, QApplication, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QBrush

from ..core.models import TunnelConfig
from ..core.config_manager import ConfigurationManager
from ..core.tunnel_process import TunnelProcess
from ..core.monitor import TunnelMonitorThread
from ..core.constants import APP_NAME

# Professional components
from .components.professional_toolbar import ProfessionalToolbar
from .widgets.professional_tunnel_list import ProfessionalTunnelList
from .widgets.professional_log import ProfessionalLogWidget, log_level_from_message

# Existing service handlers
from .components.file_operations import FileOperationsManager
from .components.rtsp_handler import RTSPHandler
from .components.rdp_handler import RDPHandler
from .components.network_scanner import NetworkScannerManager
from .components.powershell_generator import PowerShellGeneratorManager
from .components.ssh_key_generator import SSHKeyManager
from .components.ssh_key_deployment import SSHKeyDeploymentManager

# Professional theme
from .styles.professional_theme import get_professional_stylesheet, SPACING


class SSHTunnelManager(QMainWindow):
    """Professional SSH Tunnel Manager with enterprise-grade interface."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}")
        self.setGeometry(100, 100, 1300, 850)
        self.setMinimumSize(1100, 650)
        
        # Apply professional stylesheet
        self.setStyleSheet(get_professional_stylesheet())
        
        # Set window icon
        self._set_window_icon()
        
        # Core managers
        self.config_manager = ConfigurationManager()
        self.active_tunnels: Dict[str, TunnelProcess] = {}
        
        # UI Components
        self.toolbar = ProfessionalToolbar(self)
        self.tunnel_list = ProfessionalTunnelList(self)
        self.log_widget = ProfessionalLogWidget(self)
        
        # Service handlers
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
        
        # Initialize
        self._load_configurations()
        self._start_monitoring()
    
    def _set_window_icon(self):
        """Set window icon."""
        try:
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QBrush(Qt.GlobalColor.blue))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(4, 4, 56, 56)
            painter.end()
            
            self.setWindowIcon(QIcon(pixmap))
        except:
            pass
    
    def _setup_ui(self):
        """Setup main UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(SPACING['lg'], SPACING['lg'], SPACING['lg'], SPACING['lg'])
        main_layout.setSpacing(SPACING['lg'])
        
        # Toolbar
        main_layout.addWidget(self.toolbar)
        
        # Main content splitter
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(2)
        
        # Tunnel list
        splitter.addWidget(self.tunnel_list)
        
        # Log widget
        splitter.addWidget(self.log_widget)
        
        # Set proportions
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Status bar
        status_bar = self.statusBar()
        status_bar.showMessage("Ready")
        
        # Welcome log
        self.log("SSH Tunnel Manager initialized", "success")
        self.log(f"Loaded {len(self.config_manager.get_all_configurations())} tunnel configurations", "info")
    
    def _setup_connections(self):
        """Connect signals."""
        # Toolbar
        self.toolbar.add_tunnel.connect(self._add_tunnel)
        self.toolbar.edit_tunnel.connect(self._edit_tunnel)
        self.toolbar.delete_tunnel.connect(self._delete_tunnel)
        self.toolbar.start_tunnel.connect(self._start_tunnel)
        self.toolbar.stop_tunnel.connect(self._stop_tunnel)
        self.toolbar.test_tunnel.connect(self._test_tunnel)
        self.toolbar.browse_files.connect(self._browse_files)
        self.toolbar.open_web_browser.connect(self._open_web_browser)
        self.toolbar.launch_rtsp.connect(self.rtsp_handler.launch_rtsp)
        self.toolbar.launch_rdp.connect(self.rdp_handler.launch_rdp)
        self.toolbar.show_network_scanner.connect(self.network_scanner.show_scanner)
        self.toolbar.show_powershell_generator.connect(self.powershell_generator.show_generator)
        self.toolbar.show_ssh_key_manager.connect(self._setup_ssh_key)
        
        # Tunnel list
        self.tunnel_list.selection_changed.connect(self._on_selection_changed)
        self.tunnel_list.start_tunnel.connect(self._start_tunnel_by_name)
        self.tunnel_list.stop_tunnel.connect(self._stop_tunnel_by_name)
        self.tunnel_list.edit_tunnel.connect(self._edit_tunnel_by_name)
        self.tunnel_list.delete_tunnel.connect(self._delete_tunnel_by_name)
        
        # File operations
        self.file_ops_manager.log_message.connect(lambda msg: self.log(msg, log_level_from_message(msg)))
        self.file_ops_manager.tunnel_needed.connect(self._start_tunnel_by_name)
        self.file_ops_manager.refresh_table.connect(self._refresh_ui)
        self.file_ops_manager.set_managers(self.config_manager, self.active_tunnels)
        
        # Service handlers
        self.rtsp_handler.set_managers(self.config_manager, self.active_tunnels, self.log)
        self.rdp_handler.set_managers(self.config_manager, self.active_tunnels, self.log)
    
    def _setup_menu(self):
        """Setup menu bar."""
        menubar = self.menuBar()
        
        # File
        file_menu = menubar.addMenu("File")
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools
        tools_menu = menubar.addMenu("Tools")
        
        ssh_key_action = QAction("Generate SSH Key...", self)
        ssh_key_action.triggered.connect(self._setup_ssh_key)
        tools_menu.addAction(ssh_key_action)
        
        deploy_key_action = QAction("Deploy SSH Key...", self)
        deploy_key_action.triggered.connect(self._deploy_ssh_key)
        tools_menu.addAction(deploy_key_action)
        
        tools_menu.addSeparator()
        
        scanner_action = QAction("Network Scanner", self)
        scanner_action.triggered.connect(self.network_scanner.show_scanner)
        tools_menu.addAction(scanner_action)
        
        powershell_action = QAction("PowerShell Setup...", self)
        powershell_action.triggered.connect(self.powershell_generator.show_generator)
        tools_menu.addAction(powershell_action)
        
        # Help
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _setup_system_tray(self):
        """Setup system tray."""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setToolTip("SSH Tunnel Manager")
        
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
        """Load configurations."""
        self.config_manager.load_configurations()
        self._refresh_ui()
    
    def _start_monitoring(self):
        """Start tunnel monitoring."""
        self.monitor_thread = TunnelMonitorThread(self.active_tunnels)
        self.monitor_thread.status_update.connect(self._update_tunnel_status)
        self.monitor_thread.connection_lost.connect(self._handle_connection_lost)
        self.monitor_thread.start()
    
    def _refresh_ui(self):
        """Refresh UI components."""
        configs = self.config_manager.get_all_configurations()
        self.tunnel_list.refresh_table(configs, self.active_tunnels)
    
    def _on_selection_changed(self, has_selection: bool, config_name: str, is_active: bool):
        """Handle selection changes."""
        self.toolbar.update_button_states(has_selection, is_active)
        self.selected_config_name = config_name if has_selection else None
    
    def _update_tunnel_status(self, name: str, is_running: bool):
        """Update tunnel status."""
        if name in self.active_tunnels:
            self.active_tunnels[name].is_running = is_running
        self._refresh_ui()
    
    def _handle_connection_lost(self, name: str):
        """Handle connection lost."""
        self.log(f"Connection lost: {name}", "warning")
    
    # Tunnel actions
    def _add_tunnel(self):
        """Add new tunnel."""
        from PySide6.QtWidgets import QDialog
        from ssh_tunnel_manager.gui.dialogs.tunnel_config import TunnelConfigDialog
        
        dialog = TunnelConfigDialog(parent=self)
        if dialog.exec() == QDialog.Accepted:
            config = dialog.get_config()
            success, error_msg = self.config_manager.add_configuration(config)
            if success:
                self._refresh_ui()
                self.log(f"Added tunnel: {config.name}", "success")
            else:
                QMessageBox.warning(self, "Error", error_msg)
                self.log(f"Failed to add tunnel: {error_msg}", "error")
    
    def _edit_tunnel(self):
        """Edit selected tunnel."""
        if not hasattr(self, 'selected_config_name') or not self.selected_config_name:
            return
        self._edit_tunnel_by_name(self.selected_config_name)
    
    def _edit_tunnel_by_name(self, config_name: str):
        """Edit tunnel by name."""
        from PySide6.QtWidgets import QDialog
        from ssh_tunnel_manager.gui.dialogs.tunnel_config import TunnelConfigDialog
        
        config = self.config_manager.get_configuration(config_name)
        if not config:
            return
        
        dialog = TunnelConfigDialog(config=config, parent=self)
        if dialog.exec() == QDialog.Accepted:
            updated_config = dialog.get_config()
            success, error_msg = self.config_manager.update_configuration(config_name, updated_config)
            if success:
                self._refresh_ui()
                self.log(f"Updated tunnel: {updated_config.name}", "success")
            else:
                QMessageBox.warning(self, "Error", error_msg)
    
    def _delete_tunnel(self):
        """Delete selected tunnel."""
        if not hasattr(self, 'selected_config_name') or not self.selected_config_name:
            return
        self._delete_tunnel_by_name(self.selected_config_name)
    
    def _delete_tunnel_by_name(self, config_name: str):
        """Delete tunnel by name."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete tunnel '{config_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if config_name in self.active_tunnels:
                self.active_tunnels[config_name].stop()
                del self.active_tunnels[config_name]
            
            if self.config_manager.delete_configuration(config_name):
                self._refresh_ui()
                self.log(f"Deleted tunnel: {config_name}", "success")
    
    def _start_tunnel(self):
        """Start selected tunnel."""
        if hasattr(self, 'selected_config_name') and self.selected_config_name:
            self._start_tunnel_by_name(self.selected_config_name)
    
    def _start_tunnel_by_name(self, config_name: str):
        """Start tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if not config:
            return
        
        self.log(f"Starting tunnel: {config_name}", "info")
        
        if config_name not in self.active_tunnels:
            self.active_tunnels[config_name] = TunnelProcess(config, None)
        
        tunnel = self.active_tunnels[config_name]
        if tunnel.start():
            self.log(f"Tunnel started: {config_name}", "success")
        else:
            self.log(f"Failed to start tunnel: {config_name}", "error")
        
        self._refresh_ui()
    
    def _stop_tunnel(self):
        """Stop selected tunnel."""
        if hasattr(self, 'selected_config_name') and self.selected_config_name:
            self._stop_tunnel_by_name(self.selected_config_name)
    
    def _stop_tunnel_by_name(self, config_name: str):
        """Stop tunnel by name."""
        if config_name in self.active_tunnels:
            self.log(f"Stopping tunnel: {config_name}", "info")
            self.active_tunnels[config_name].stop()
            self._refresh_ui()
    
    def _test_tunnel(self):
        """Test tunnel connection."""
        from ..utils.connection_tester import ConnectionTester
        
        if not hasattr(self, 'selected_config_name') or not self.selected_config_name:
            return
        
        config = self.config_manager.get_configuration(self.selected_config_name)
        if not config:
            return
        
        self.log(f"Testing tunnel: {self.selected_config_name}", "info")
        success, message = ConnectionTester.test_tunnel_connection(config)
        
        if success:
            self.log(f"Test successful: {message}", "success")
            QMessageBox.information(self, "Test Result", f"Success: {message}")
        else:
            self.log(f"Test failed: {message}", "error")
            QMessageBox.warning(self, "Test Result", f"Failed: {message}")
    
    def _browse_files(self):
        """Browse files."""
        if hasattr(self, 'selected_config_name') and self.selected_config_name:
            config = self.config_manager.get_configuration(self.selected_config_name)
            if config:
                self.file_ops_manager.browse_files(self.selected_config_name, config)
    
    def _open_web_browser(self):
        """Open web browser."""
        if hasattr(self, 'selected_config_name') and self.selected_config_name:
            config = self.config_manager.get_configuration(self.selected_config_name)
            if config and config.tunnel_type == 'local':
                url = f"http://localhost:{config.local_port}"
                webbrowser.open(url)
                self.log(f"Opened browser: {url}", "info")
    
    def _setup_ssh_key(self):
        """Setup SSH key."""
        self.ssh_key_manager.show_key_generator(None)
    
    def _deploy_ssh_key(self):
        """Deploy SSH key."""
        self.ssh_key_deployment.deploy_key_for_tunnel(None)
    
    def _show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About",
            f"<h3>{APP_NAME}</h3>"
            "<p>Professional SSH tunnel management</p>"
            "<p>Secure connections, port forwarding, and remote access</p>"
        )
    
    def log(self, message: str, level: str = "info"):
        """Log a message."""
        self.log_widget.add_log(message, level)
    
    def closeEvent(self, event):
        """Handle close event."""
        if QSystemTrayIcon.isSystemTrayAvailable() and hasattr(self, 'tray_icon'):
            self.hide()
            event.ignore()
        else:
            self._quit_application()
    
    def _quit_application(self):
        """Quit application."""
        for tunnel in self.active_tunnels.values():
            tunnel.stop()
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        
        QApplication.quit()
