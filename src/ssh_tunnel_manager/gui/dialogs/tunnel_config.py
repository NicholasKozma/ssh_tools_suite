#!/usr/bin/env python3
"""
SSH Tunnel Manager - Configuration Dialog
"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QGroupBox, QLineEdit, 
    QSpinBox, QComboBox, QCheckBox, QDialogButtonBox, QTextEdit, QLabel
)
from PySide6.QtCore import Qt

from ...core.models import TunnelConfig
from ...core.constants import DEFAULT_SSH_PORT, DEFAULT_LOCAL_RTSP_PORT


class TunnelConfigDialog(QDialog):
    """Dialog for creating/editing tunnel configurations."""
    
    def __init__(self, config: Optional[TunnelConfig] = None, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Tunnel Configuration")
        self.setFixedSize(600, 550)  # Increased size for RTSP section
        self.setup_ui()
        
        if config:
            self.load_config(config)
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Form layout
        form = QFormLayout()
        
        # Basic settings
        self.name_edit = QLineEdit()
        self.description_edit = QLineEdit()
        form.addRow("Name:", self.name_edit)
        form.addRow("Description:", self.description_edit)
        
        # SSH connection settings
        ssh_group = QGroupBox("SSH Connection")
        ssh_layout = QFormLayout(ssh_group)
        
        self.ssh_host_edit = QLineEdit()
        self.ssh_port_spin = QSpinBox()
        self.ssh_port_spin.setRange(1, 65535)
        self.ssh_port_spin.setValue(DEFAULT_SSH_PORT)
        self.ssh_user_edit = QLineEdit()
        self.ssh_key_edit = QLineEdit()
        
        ssh_layout.addRow("SSH Host:", self.ssh_host_edit)
        ssh_layout.addRow("SSH Port:", self.ssh_port_spin)
        ssh_layout.addRow("SSH User:", self.ssh_user_edit)
        ssh_layout.addRow("SSH Key Path (optional):", self.ssh_key_edit)
        
        # Tunnel settings
        tunnel_group = QGroupBox("Tunnel Configuration")
        tunnel_layout = QFormLayout(tunnel_group)
        
        self.tunnel_type_combo = QComboBox()
        self.tunnel_type_combo.addItems(['local', 'remote', 'dynamic'])
        self.tunnel_type_combo.currentTextChanged.connect(self.on_tunnel_type_changed)
        
        self.local_port_spin = QSpinBox()
        self.local_port_spin.setRange(1024, 65535)
        self.local_port_spin.setValue(DEFAULT_LOCAL_RTSP_PORT)
        
        self.remote_host_edit = QLineEdit()
        self.remote_host_edit.setText("localhost")
        
        self.remote_port_spin = QSpinBox()
        self.remote_port_spin.setRange(1, 65535)
        self.remote_port_spin.setValue(554)
        
        tunnel_layout.addRow("Tunnel Type:", self.tunnel_type_combo)
        tunnel_layout.addRow("Local Port:", self.local_port_spin)
        tunnel_layout.addRow("Remote Host:", self.remote_host_edit)
        tunnel_layout.addRow("Remote Port:", self.remote_port_spin)
        
        # RTSP Configuration
        rtsp_group = QGroupBox("RTSP Configuration (Optional)")
        rtsp_layout = QFormLayout(rtsp_group)
        
        self.rtsp_url_edit = QLineEdit()
        self.rtsp_url_edit.setPlaceholderText("rtsp://localhost:8554/live/0")
        
        rtsp_help = QLabel("Leave empty to use default: rtsp://localhost:[local_port]/live/0")
        rtsp_help.setWordWrap(True)
        rtsp_help.setStyleSheet("color: gray; font-size: 10px;")
        
        rtsp_layout.addRow("RTSP URL:", self.rtsp_url_edit)
        rtsp_layout.addRow("", rtsp_help)
        
        # Options
        self.auto_start_check = QCheckBox("Auto-start on application launch")
        
        # Layout assembly
        layout.addLayout(form)
        layout.addWidget(ssh_group)
        layout.addWidget(tunnel_group)
        layout.addWidget(rtsp_group)
        layout.addWidget(self.auto_start_check)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Set initial state
        self.on_tunnel_type_changed()
    
    def on_tunnel_type_changed(self):
        """Handle tunnel type changes - enable/disable relevant fields."""
        tunnel_type = self.tunnel_type_combo.currentText()
        
        if tunnel_type == 'dynamic':
            # Dynamic port forwarding (SOCKS proxy)
            self.remote_host_edit.setEnabled(False)
            self.remote_port_spin.setEnabled(False)
            self.local_port_spin.setEnabled(True)
        elif tunnel_type == 'local':
            # Local port forwarding
            self.remote_host_edit.setEnabled(True)
            self.remote_port_spin.setEnabled(True)
            self.local_port_spin.setEnabled(True)
        elif tunnel_type == 'remote':
            # Remote port forwarding
            self.remote_host_edit.setEnabled(True)
            self.remote_port_spin.setEnabled(True)
            self.local_port_spin.setEnabled(True)
    
    def load_config(self, config: TunnelConfig):
        """Load configuration into dialog fields."""
        self.name_edit.setText(config.name)
        self.description_edit.setText(config.description)
        self.ssh_host_edit.setText(config.ssh_host)
        self.ssh_port_spin.setValue(config.ssh_port)
        self.ssh_user_edit.setText(config.ssh_user)
        self.ssh_key_edit.setText(config.ssh_key_path or "")
        self.tunnel_type_combo.setCurrentText(config.tunnel_type)
        self.local_port_spin.setValue(config.local_port)
        self.remote_host_edit.setText(config.remote_host or "localhost")
        self.remote_port_spin.setValue(config.remote_port or 80)
        self.auto_start_check.setChecked(config.auto_start)
        
        # Load RTSP URL
        if hasattr(config, 'rtsp_url') and config.rtsp_url:
            self.rtsp_url_edit.setText(config.rtsp_url)
        
        # Update field states
        self.on_tunnel_type_changed()
    
    def get_config(self) -> TunnelConfig:
        """Get configuration from dialog fields."""
        return TunnelConfig(
            name=self.name_edit.text().strip(),
            description=self.description_edit.text().strip(),
            ssh_host=self.ssh_host_edit.text().strip(),
            ssh_port=self.ssh_port_spin.value(),
            ssh_user=self.ssh_user_edit.text().strip(),
            ssh_key_path=self.ssh_key_edit.text().strip() or "",
            tunnel_type=self.tunnel_type_combo.currentText(),
            local_port=self.local_port_spin.value(),
            remote_host=self.remote_host_edit.text().strip() if self.tunnel_type_combo.currentText() != 'dynamic' else "",
            remote_port=self.remote_port_spin.value() if self.tunnel_type_combo.currentText() != 'dynamic' else 0,
            auto_start=self.auto_start_check.isChecked(),
            rtsp_url=self.rtsp_url_edit.text().strip()
        )
