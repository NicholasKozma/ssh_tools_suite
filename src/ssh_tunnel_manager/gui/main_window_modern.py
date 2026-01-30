#!/usr/bin/env python3
"""
SSH Tunnel Manager - Ultra Modern Redesigned Main Window
Complete visual overhaul with card-based interface, dashboard, and modern styling
"""

import sys
import webbrowser
from pathlib import Path
from typing import Dict

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QSystemTrayIcon, QMenu, QApplication, QMessageBox, QTabWidget
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon, QPixmap, QPainter, QBrush

from ..core.models import TunnelConfig
from ..core.config_manager import ConfigurationManager
from ..core.tunnel_process import TunnelProcess
from ..core.monitor import TunnelMonitorThread
from ..core.constants import APP_NAME

# Import modern components
from .components.modern_toolbar import ModernToolbar
from .widgets.tunnel_cards import TunnelCardsWidget
from .widgets.dashboard import DashboardWidget
from .widgets.modern_log import ModernLogWidget, log_level_from_message

# Import existing components
from .components.file_operations import FileOperationsManager
from .components.rtsp_handler import RTSPHandler
from .components.rdp_handler import RDPHandler
from .components.network_scanner import NetworkScannerManager
from .components.powershell_generator import PowerShellGeneratorManager
from .components.ssh_key_generator import SSHKeyManager
from .components.ssh_key_deployment import SSHKeyDeploymentManager

# Import modern theme
from .styles.modern_theme import get_modern_stylesheet


class SSHTunnelManager(QMainWindow):
    """Ultra-modern SSH Tunnel Manager with card-based dashboard interface."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"🔐 {APP_NAME} - Modern Edition")
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1200, 700)
        
        # Apply ultra-modern stylesheet
        self.setStyleSheet(get_modern_stylesheet())
        
        # Set window icon
        self._set_window_icon()
        
        # Core managers
        self.config_manager = ConfigurationManager()
        self.active_tunnels: Dict[str, TunnelProcess] = {}
        
        # Modern UI Components
        self.toolbar = ModernToolbar(self)
        self.dashboard = DashboardWidget(self)
        self.tunnel_cards = TunnelCardsWidget(self)
        self.log_widget = ModernLogWidget(self)
        
        # Existing service handlers
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
    
    def _set_window_icon(self):
        """Set a custom window icon."""
        try:
            from .styles.modern_theme import COLORS
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Modern icon design
            painter.setBrush(QBrush(Qt.GlobalColor.blue))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(4, 4, 56, 56)
            
            painter.setPen(Qt.GlobalColor.white)
            painter.setBrush(QBrush(Qt.GlobalColor.white))
            painter.drawRect(16, 24, 32, 4)
            painter.drawRect(16, 32, 32, 4)
            
            painter.end()
            
            icon = QIcon(pixmap)
            self.setWindowIcon(icon)
        except:
            pass
    
    def _setup_ui(self):
        """Setup the ultra-modern UI."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # Modern toolbar
        main_layout.addWidget(self.toolbar)
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Vertical)
        content_splitter.setHandleWidth(4)
        
        # Top section: Dashboard + Tunnel Cards
        top_section = QWidget()
        top_layout = QVBoxLayout(top_section)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(16)
        
        # Dashboard (collapsible stats)
        top_layout.addWidget(self.dashboard)
        
        # Tunnel cards
        top_layout.addWidget(self.tunnel_cards)
        
        content_splitter.addWidget(top_section)
        
        # Bottom section: Modern log
        content_splitter.addWidget(self.log_widget)
        
        # Set splitter proportions
        content_splitter.setStretchFactor(0, 3)
        content_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(content_splitter)
        
        # Modern status bar
        status_bar = self.statusBar()
        status_bar.showMessage("🚀 Ready")
        
        # Welcome message
        self.log("🎉 SSH Tunnel Manager launched successfully", "success")
        self.log(f"📦 Loaded {len(self.config_manager.get_all_configurations())} tunnel configurations", "info")
    
    def _setup_connections(self):
        """Connect all signal handlers."""
        # Toolbar signals
        self.toolbar.add_tunnel.connect(self._add_tunnel)
        self.toolbar.edit_tunnel.connect(self._edit_tunnel)
        self.toolbar.delete_tunnel.connect(self._delete_tunnel)
        self.toolbar.start_tunnel.connect(self._start_tunnel)
        self.toolbar.stop_tunnel.connect(self._stop_tunnel)
        self.toolbar.test_tunnel.connect(self._test_tunnel)
        self.toolbar.browse_files.connect(self._browse_files)
        self.toolbar.browse_remote_files.connect(self._browse_remote_files)
        self.toolbar.open_web_browser.connect(self._open_web_browser)
        self.toolbar.launch_rtsp.connect(self.rtsp_handler.launch_rtsp)
        self.toolbar.launch_rdp.connect(self.rdp_handler.launch_rdp)
        self.toolbar.show_network_scanner.connect(self.network_scanner.show_scanner)
        self.toolbar.show_powershell_generator.connect(self.powershell_generator.show_generator)
        self.toolbar.show_ssh_key_manager.connect(self._setup_ssh_key)
        
        # Tunnel cards signals
        self.tunnel_cards.start_tunnel.connect(self._start_tunnel_by_name)
        self.tunnel_cards.stop_tunnel.connect(self._stop_tunnel_by_name)
        self.tunnel_cards.edit_tunnel.connect(self._edit_tunnel_by_name)
        self.tunnel_cards.delete_tunnel.connect(self._delete_tunnel_by_name)
        self.tunnel_cards.files_tunnel.connect(self._browse_files_by_name)
        
        # File operations
        self.file_ops_manager.log_message.connect(lambda msg: self.log(msg, log_level_from_message(msg)))
        self.file_ops_manager.tunnel_needed.connect(self._start_tunnel_by_name)
        self.file_ops_manager.refresh_table.connect(self._refresh_ui)
        self.file_ops_manager.set_managers(self.config_manager, self.active_tunnels)
        
        # Setup service handlers
        self.rtsp_handler.set_managers(self.config_manager, self.active_tunnels, self.log)
        self.rdp_handler.set_managers(self.config_manager, self.active_tunnels, self.log)
    
    def _setup_menu(self):
        """Setup menu bar."""
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
        
        powershell_action = QAction("⚡ PowerShell SSH Setup...", self)
        powershell_action.triggered.connect(self.powershell_generator.show_generator)
        tools_menu.addAction(powershell_action)
        
        tools_menu.addSeparator()
        network_scanner_action = QAction("🔍 Network Scanner", self)
        network_scanner_action.triggered.connect(self.network_scanner.show_scanner)
        tools_menu.addAction(network_scanner_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        toggle_dashboard_action = QAction("Toggle Dashboard", self)
        toggle_dashboard_action.triggered.connect(self._toggle_dashboard)
        view_menu.addAction(toggle_dashboard_action)
        
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
        
        try:
            icon = self.windowIcon()
            if icon.isNull():
                icon = self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon)
        except:
            pixmap = QPixmap(16, 16)
            pixmap.fill(Qt.blue)
            icon = QIcon(pixmap)
        
        self.tray_icon.setIcon(icon)
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
        """Load and display configurations."""
        self.config_manager.load_configurations()
        self._refresh_ui()
    
    def _start_monitoring(self):
        """Start tunnel monitoring."""
        self.monitor_thread = TunnelMonitorThread(self.active_tunnels)
        self.monitor_thread.status_update.connect(self._update_tunnel_status)
        self.monitor_thread.connection_lost.connect(self._handle_connection_lost)
        self.monitor_thread.start()
    
    def _refresh_ui(self):
        """Refresh all UI components."""
        configs = self.config_manager.get_all_configurations()
        
        # Update dashboard stats
        active_count = len([t for t in self.active_tunnels.values() if t.is_running])
        total_count = len(configs)
        self.dashboard.update_stats(active_count, total_count)
        
        # Update tunnel cards
        self.tunnel_cards.refresh_cards(configs, self.active_tunnels)
        
        # Update toolbar button states
        self.toolbar.update_button_states(False, False)
    
    def _update_tunnel_status(self, name: str, is_running: bool):
        """Update tunnel status from monitor."""
        if name in self.active_tunnels:
            self.active_tunnels[name].is_running = is_running
        self._refresh_ui()
    
    def _handle_connection_lost(self, name: str):
        """Handle connection lost event."""
        self.log(f"Connection lost for tunnel: {name}", "warning")
    
    def _toggle_dashboard(self):
        """Toggle dashboard visibility."""
        self.dashboard.setVisible(not self.dashboard.isVisible())
    
    # ==================== TUNNEL ACTIONS ====================
    
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
        """Edit selected tunnel (placeholder - needs selection)."""
        QMessageBox.information(self, "Info", "Please click Edit button on a tunnel card")
    
    def _edit_tunnel_by_name(self, config_name: str):
        """Edit tunnel by name."""
        from PySide6.QtWidgets import QDialog
        from ssh_tunnel_manager.gui.dialogs.tunnel_config import TunnelConfigDialog
        
        config = self.config_manager.get_configuration(config_name)
        if not config:
            QMessageBox.warning(self, "Error", f"Configuration '{config_name}' not found")
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
                self.log(f"Failed to update tunnel: {error_msg}", "error")
    
    def _delete_tunnel(self):
        """Delete selected tunnel (placeholder)."""
        QMessageBox.information(self, "Info", "Please click Delete button on a tunnel card")
    
    def _delete_tunnel_by_name(self, config_name: str):
        """Delete tunnel by name."""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete tunnel '{config_name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Stop if running
            if config_name in self.active_tunnels:
                self.active_tunnels[config_name].stop()
                del self.active_tunnels[config_name]
            
            success = self.config_manager.delete_configuration(config_name)
            if success:
                self._refresh_ui()
                self.log(f"Deleted tunnel: {config_name}", "success")
            else:
                QMessageBox.warning(self, "Error", f"Failed to delete configuration")
                self.log(f"Failed to delete tunnel: {config_name}", "error")
    
    def _start_tunnel(self):
        """Start selected tunnel (placeholder)."""
        QMessageBox.information(self, "Info", "Please click Start button on a tunnel card")
    
    def _start_tunnel_by_name(self, config_name: str):
        """Start tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if not config:
            return
        
        self.log(f"Starting tunnel: {config_name}", "info")
        
        if config_name not in self.active_tunnels:
            self.active_tunnels[config_name] = TunnelProcess(config, None)
        
        tunnel = self.active_tunnels[config_name]
        tunnel.status = tunnel.STATUS_STARTING
        self._refresh_ui()
        
        if tunnel.start():
            self.log(f"Tunnel started: {config_name}", "success")
            self._refresh_ui()
        else:
            self.log(f"Failed to start tunnel: {config_name}", "error")
            self._refresh_ui()
    
    def _stop_tunnel(self):
        """Stop selected tunnel (placeholder)."""
        QMessageBox.information(self, "Info", "Please click Stop button on a tunnel card")
    
    def _stop_tunnel_by_name(self, config_name: str):
        """Stop tunnel by name."""
        if config_name not in self.active_tunnels:
            return
        
        self.log(f"Stopping tunnel: {config_name}", "info")
        tunnel = self.active_tunnels[config_name]
        tunnel.stop()
        self._refresh_ui()
        self.log(f"Tunnel stopped: {config_name}", "success")
    
    def _test_tunnel(self):
        """Test tunnel connection."""
        QMessageBox.information(self, "Info", "Please select a running tunnel first")
    
    def _browse_files(self):
        """Browse files via SFTP."""
        QMessageBox.information(self, "Info", "Please select a running tunnel first")
    
    def _browse_files_by_name(self, config_name: str):
        """Browse files for tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if config:
            self.file_ops_manager.browse_files(config_name, config)
    
    def _browse_remote_files(self):
        """Browse remote files."""
        QMessageBox.information(self, "Info", "Please select a running tunnel first")
    
    def _open_web_browser(self):
        """Open web browser."""
        QMessageBox.information(self, "Info", "Please select a running tunnel with web service")
    
    def _setup_ssh_key(self):
        """Setup SSH key."""
        self.ssh_key_manager.show_key_generator(None)
    
    def _deploy_ssh_key(self):
        """Deploy SSH key."""
        self.ssh_key_deployment.deploy_key_for_tunnel(None)
    
    def _show_about(self):
        """Show about dialog."""
        about_text = f"""
        <div style='text-align: center; background: #1a1f2e; padding: 20px; border-radius: 12px;'>
            <h2 style='color: #00d4ff; margin-bottom: 10px;'>🔐 {APP_NAME}</h2>
            <p style='font-size: 12pt; color: #e5e7eb; margin: 5px 0;'>
                <b>Modern SSH Tunnel Manager</b>
            </p>
            <hr style='border: none; border-top: 2px solid #00d4ff; margin: 15px 0;'>
            <p style='color: #9ca3af; margin: 10px 0;'>
                Beautiful, modern interface for managing<br>
                SSH tunnels and secure connections.
            </p>
            <p style='color: #6b7280; font-size: 9pt; margin-top: 20px;'>
                Powered by Python & PySide6 ⚡
            </p>
        </div>
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("About")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()
    
    def log(self, message: str, level: str = "info"):
        """Log a message with level."""
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
        # Stop all tunnels
        for tunnel in self.active_tunnels.values():
            tunnel.stop()
        
        # Stop monitoring
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        
        QApplication.quit()
