#!/usr/bin/env python3
"""
SSH Tunnel Manager - RDP Handler
Handles Remote Desktop Protocol (RDP) connections through SSH tunnels
"""

import subprocess
import threading
import os
import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMenu, QMessageBox, QInputDialog, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QSpinBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt

from ...core.models import TunnelConfig


class RDPConnectionDialog(QDialog):
    """Dialog for configuring RDP connection details."""
    
    def __init__(self, config: TunnelConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("RDP Connection Settings")
        self.setModal(True)
        self.resize(400, 300)
        
        self._setup_ui()
        self._load_defaults()
    
    def _setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Remote host information
        info_label = QLabel(f"Connecting to: {self.config.remote_host} via tunnel {self.config.name}")
        info_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        layout.addWidget(info_label)
        
        # RDP Port
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("RDP Port:"))
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(3389)  # Default RDP port
        port_layout.addWidget(self.port_spin)
        layout.addLayout(port_layout)
        
        # Username
        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel("Username:"))
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter RDP username")
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Enter RDP password (optional)")
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)
        
        # Domain
        domain_layout = QHBoxLayout()
        domain_layout.addWidget(QLabel("Domain:"))
        self.domain_edit = QLineEdit()
        self.domain_edit.setPlaceholderText("Enter domain (optional)")
        domain_layout.addWidget(self.domain_edit)
        layout.addLayout(domain_layout)
        
        # Options
        self.fullscreen_check = QCheckBox("Full Screen")
        self.fullscreen_check.setChecked(False)
        layout.addWidget(self.fullscreen_check)
        
        self.multimon_check = QCheckBox("Multiple Monitors")
        self.multimon_check.setChecked(False)
        layout.addWidget(self.multimon_check)
        
        # Buttons
        button_layout = QHBoxLayout()
        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.accept)
        connect_button.setDefault(True)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(connect_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def _load_defaults(self):
        """Load default values."""
        # Try to use SSH username as default RDP username
        if hasattr(self.config, 'ssh_username') and self.config.ssh_username:
            self.username_edit.setText(self.config.ssh_username)
    
    def get_rdp_settings(self):
        """Get the RDP connection settings."""
        return {
            'port': self.port_spin.value(),
            'username': self.username_edit.text().strip(),
            'password': self.password_edit.text(),
            'domain': self.domain_edit.text().strip(),
            'fullscreen': self.fullscreen_check.isChecked(),
            'multimon': self.multimon_check.isChecked()
        }


class RDPHandler:
    """Handles RDP connections through SSH tunnels."""
    
    def __init__(self, parent):
        self.parent = parent
        self.config_manager = None
        self.active_tunnels = None
        self.log = None
    
    def set_managers(self, config_manager, active_tunnels, log_func):
        """Set references to managers and functions."""
        self.config_manager = config_manager
        self.active_tunnels = active_tunnels
        self.log = log_func
    
    def launch_rdp(self):
        """Launch RDP connection through SSH tunnel."""
        config_name = self.parent.table_widget.get_selected_config_name()
        if not config_name:
            QMessageBox.information(self.parent, "No Selection", "Please select a tunnel first.")
            return
        
        # Get the tunnel configuration
        config = self.config_manager.get_configuration(config_name)
        if not config:
            self.log(f"Configuration not found: {config_name}")
            return
        
        # Check if tunnel is running
        if config_name not in self.active_tunnels or not self.active_tunnels[config_name].is_running:
            QMessageBox.warning(self.parent, "Tunnel Not Running", 
                              f"Tunnel '{config_name}' is not running. Please start the tunnel first.")
            return
        
        # Only allow RDP for local tunnels (port forwarding)
        if config.tunnel_type != 'local':
            QMessageBox.warning(self.parent, "Invalid Tunnel Type", 
                              "RDP connections are only supported for local port forwarding tunnels.")
            return
        
        self.launch_rdp_by_name(config_name)
    
    def launch_rdp_by_name(self, config_name: str):
        """Launch RDP for a specific tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if not config:
            self.log(f"Configuration not found: {config_name}")
            return
        
        # Show RDP configuration dialog
        dialog = RDPConnectionDialog(config, self.parent)
        if dialog.exec() != QDialog.Accepted:
            return
        
        rdp_settings = dialog.get_rdp_settings()
        
        # Check if we need to create a new tunnel specifically for RDP
        rdp_port = rdp_settings['port']
        
        if config.remote_port == rdp_port:
            # The existing tunnel already forwards to the RDP port
            target_host = "localhost"
            target_port = config.local_port
            self.log(f"🖥️ Using existing tunnel for RDP: localhost:{target_port} -> {config.remote_host}:{rdp_port}")
        else:
            # We need to create a new tunnel for RDP
            # This would require creating a new tunnel configuration
            QMessageBox.information(self.parent, "Manual Tunnel Setup Required", 
                                  f"The selected tunnel forwards to port {config.remote_port}, but RDP needs port {rdp_port}.\n\n"
                                  f"Please create a new tunnel configuration that forwards to {config.remote_host}:{rdp_port}")
            return
        
        # Launch RDP client
        self._launch_rdp_client(target_host, target_port, rdp_settings, config)
    
    def _launch_rdp_client(self, host: str, port: int, rdp_settings: dict, config: TunnelConfig):
        """Launch the RDP client with the specified settings."""
        try:
            if os.name == 'nt':  # Windows
                self._launch_windows_rdp(host, port, rdp_settings, config)
            else:  # Linux/Mac
                self._launch_unix_rdp(host, port, rdp_settings, config)
        except Exception as e:
            self.log(f"❌ Failed to launch RDP client: {str(e)}")
            QMessageBox.critical(self.parent, "RDP Error", f"Failed to launch RDP client:\n{str(e)}")
    
    def _launch_windows_rdp(self, host: str, port: int, rdp_settings: dict, config: TunnelConfig):
        """Launch Windows Remote Desktop Connection (mstsc)."""
        # Create temporary RDP file
        rdp_content = self._create_rdp_file_content(host, port, rdp_settings)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rdp', delete=False) as rdp_file:
            rdp_file.write(rdp_content)
            rdp_file_path = rdp_file.name
        
        try:
            # Launch mstsc with the RDP file
            cmd = ['mstsc', rdp_file_path]
            self.log(f"🖥️ Launching Windows RDP client to {host}:{port}")
            
            def run_rdp():
                try:
                    subprocess.run(cmd, check=False)
                finally:
                    # Clean up temporary file after RDP client exits
                    try:
                        os.unlink(rdp_file_path)
                    except:
                        pass
            
            # Run in background thread
            threading.Thread(target=run_rdp, daemon=True).start()
            
        except Exception as e:
            os.unlink(rdp_file_path)  # Clean up on error
            raise e
    
    def _launch_unix_rdp(self, host: str, port: int, rdp_settings: dict, config: TunnelConfig):
        """Launch RDP client on Unix systems (Linux/Mac)."""
        # Try common RDP clients
        rdp_clients = [
            'rdesktop',   # Common Linux RDP client
            'xfreerdp',   # FreeRDP client
            'remmina',    # Remmina (if available)
        ]
        
        rdp_client = None
        for client in rdp_clients:
            if self._command_exists(client):
                rdp_client = client
                break
        
        if not rdp_client:
            QMessageBox.warning(self.parent, "RDP Client Not Found", 
                              "No RDP client found. Please install one of the following:\n"
                              "- rdesktop (sudo apt install rdesktop)\n"
                              "- xfreerdp (sudo apt install freerdp2-x11)\n"
                              "- remmina (sudo apt install remmina)")
            return
        
        # Build command based on client
        if rdp_client == 'rdesktop':
            cmd = self._build_rdesktop_command(host, port, rdp_settings)
        elif rdp_client == 'xfreerdp':
            cmd = self._build_xfreerdp_command(host, port, rdp_settings)
        else:
            # For remmina or other clients, use basic connection
            cmd = [rdp_client, f"{host}:{port}"]
        
        self.log(f"🖥️ Launching {rdp_client} RDP client to {host}:{port}")
        
        def run_rdp():
            try:
                subprocess.run(cmd, check=False)
            except Exception as e:
                self.log(f"❌ RDP client error: {str(e)}")
        
        # Run in background thread
        threading.Thread(target=run_rdp, daemon=True).start()
    
    def _create_rdp_file_content(self, host: str, port: int, rdp_settings: dict) -> str:
        """Create RDP file content for Windows mstsc."""
        lines = [
            "screen mode id:i:2",  # Windowed mode by default
            f"use multimon:i:{1 if rdp_settings['multimon'] else 0}",
            f"full address:s:{host}:{port}",
            "audiomode:i:0",  # Play sounds on client
            "authentication level:i:0",  # No authentication required
            "prompt for credentials:i:1",  # Prompt for credentials
            "negotiate security layer:i:1",
            "remoteapplicationmode:i:0",
            "alternate shell:s:",
            "shell working directory:s:",
            "gatewayhostname:s:",
            "gatewayusagemethod:i:4",
            "gatewaycredentialssource:i:4",
            "gatewayprofileusagemethod:i:0",
            "promptcredentialonce:i:0",
            "drivestoredirect:s:",
        ]
        
        # Add username if provided
        if rdp_settings['username']:
            lines.append(f"username:s:{rdp_settings['username']}")
        
        # Add domain if provided
        if rdp_settings['domain']:
            lines.append(f"domain:s:{rdp_settings['domain']}")
        
        # Set full screen mode
        if rdp_settings['fullscreen']:
            lines[0] = "screen mode id:i:1"  # Full screen mode
        
        return '\n'.join(lines)
    
    def _build_rdesktop_command(self, host: str, port: int, rdp_settings: dict) -> list:
        """Build rdesktop command."""
        cmd = ['rdesktop']
        
        if rdp_settings['fullscreen']:
            cmd.append('-f')
        
        if rdp_settings['username']:
            cmd.extend(['-u', rdp_settings['username']])
        
        if rdp_settings['domain']:
            cmd.extend(['-d', rdp_settings['domain']])
        
        if rdp_settings['password']:
            cmd.extend(['-p', rdp_settings['password']])
        
        cmd.append(f"{host}:{port}")
        return cmd
    
    def _build_xfreerdp_command(self, host: str, port: int, rdp_settings: dict) -> list:
        """Build xfreerdp command."""
        cmd = ['xfreerdp']
        
        if rdp_settings['fullscreen']:
            cmd.append('/f')
        
        if rdp_settings['multimon']:
            cmd.append('/multimon')
        
        if rdp_settings['username']:
            cmd.append(f'/u:{rdp_settings["username"]}')
        
        if rdp_settings['domain']:
            cmd.append(f'/d:{rdp_settings["domain"]}')
        
        if rdp_settings['password']:
            cmd.append(f'/p:{rdp_settings["password"]}')
        
        cmd.append(f'/v:{host}:{port}')
        return cmd
    
    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in the system PATH."""
        try:
            subprocess.run(['which', command], check=True, 
                         capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError:
            return False
