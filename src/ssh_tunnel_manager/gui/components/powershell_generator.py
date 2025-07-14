#!/usr/bin/env python3
"""
SSH Tunnel Manager - PowerShell Script Generator
Generates PowerShell scripts for SSH server setup and configuration
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QCheckBox, QGroupBox, QTabWidget, QWidget, QComboBox,
    QSpinBox, QMessageBox, QFileDialog, QFormLayout, QApplication
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PowerShellGeneratorDialog(QDialog):
    """Dialog for generating PowerShell scripts for SSH setup."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PowerShell SSH Setup Script Generator")
        self.setGeometry(200, 200, 800, 600)
        self.setModal(False)
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Configuration tab
        self.config_tab = self._create_config_tab()
        self.tab_widget.addTab(self.config_tab, "🔧 Configuration")
        
        # Generated script tab
        self.script_tab = self._create_script_tab()
        self.tab_widget.addTab(self.script_tab, "📜 Generated Script")
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("Generate Script")
        self.save_button = QPushButton("Save Script")
        self.copy_button = QPushButton("Copy to Clipboard")
        self.close_button = QPushButton("Close")
        
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.copy_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _create_config_tab(self) -> QWidget:
        """Create the configuration tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # SSH Service Configuration
        ssh_group = QGroupBox("SSH Server Configuration")
        ssh_layout = QFormLayout(ssh_group)
        
        self.install_openssh = QCheckBox("Install OpenSSH Server")
        self.install_openssh.setChecked(True)
        ssh_layout.addRow("", self.install_openssh)
        
        self.ssh_port = QSpinBox()
        self.ssh_port.setRange(1, 65535)
        self.ssh_port.setValue(22)
        ssh_layout.addRow("SSH Port:", self.ssh_port)
        
        self.enable_password_auth = QCheckBox("Enable Password Authentication")
        self.enable_password_auth.setChecked(False)
        ssh_layout.addRow("", self.enable_password_auth)
        
        self.enable_key_auth = QCheckBox("Enable Public Key Authentication")
        self.enable_key_auth.setChecked(True)
        ssh_layout.addRow("", self.enable_key_auth)
        
        layout.addWidget(ssh_group)
        
        # User Configuration
        user_group = QGroupBox("User Configuration")
        user_layout = QFormLayout(user_group)
        
        self.create_user = QCheckBox("Create SSH User")
        user_layout.addRow("", self.create_user)
        
        self.username = QLineEdit()
        self.username.setPlaceholderText("Enter username (optional)")
        user_layout.addRow("Username:", self.username)
        
        self.user_password = QLineEdit()
        self.user_password.setPlaceholderText("Enter password (optional)")
        self.user_password.setEchoMode(QLineEdit.Password)
        user_layout.addRow("Password:", self.user_password)
        
        layout.addWidget(user_group)
        
        # Firewall Configuration
        firewall_group = QGroupBox("Firewall Configuration")
        firewall_layout = QFormLayout(firewall_group)
        
        self.configure_firewall = QCheckBox("Configure Windows Firewall")
        self.configure_firewall.setChecked(True)
        firewall_layout.addRow("", self.configure_firewall)
        
        self.allow_specific_ips = QCheckBox("Restrict to Specific IPs")
        firewall_layout.addRow("", self.allow_specific_ips)
        
        self.allowed_ips = QLineEdit()
        self.allowed_ips.setPlaceholderText("Enter IP addresses separated by commas")
        firewall_layout.addRow("Allowed IPs:", self.allowed_ips)
        
        layout.addWidget(firewall_group)
        
        # Key Management
        key_group = QGroupBox("SSH Key Management")
        key_layout = QFormLayout(key_group)
        
        self.generate_keys = QCheckBox("Generate SSH Keys")
        key_layout.addRow("", self.generate_keys)
        
        self.key_type = QComboBox()
        self.key_type.addItems(["rsa", "ed25519", "ecdsa"])
        self.key_type.setCurrentText("ed25519")
        key_layout.addRow("Key Type:", self.key_type)
        
        self.key_bits = QSpinBox()
        self.key_bits.setRange(1024, 8192)
        self.key_bits.setValue(4096)
        key_layout.addRow("Key Bits (RSA):", self.key_bits)
        
        layout.addWidget(key_group)
        
        # Additional Options
        options_group = QGroupBox("Additional Options")
        options_layout = QFormLayout(options_group)
        
        self.enable_logging = QCheckBox("Enable SSH Logging")
        self.enable_logging.setChecked(True)
        options_layout.addRow("", self.enable_logging)
        
        self.disable_root_login = QCheckBox("Disable Root Login")
        self.disable_root_login.setChecked(True)
        options_layout.addRow("", self.disable_root_login)
        
        self.max_auth_tries = QSpinBox()
        self.max_auth_tries.setRange(1, 10)
        self.max_auth_tries.setValue(3)
        options_layout.addRow("Max Auth Tries:", self.max_auth_tries)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        return tab
    
    def _create_script_tab(self) -> QWidget:
        """Create the script display tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Info label
        info_label = QLabel("Generated PowerShell script will appear here. Click 'Generate Script' to create it.")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Script text area
        self.script_text = QTextEdit()
        self.script_text.setReadOnly(True)
        self.script_text.setFont(QFont("Consolas", 10))
        layout.addWidget(self.script_text)
        
        return tab
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.generate_button.clicked.connect(self._generate_script)
        self.save_button.clicked.connect(self._save_script)
        self.copy_button.clicked.connect(self._copy_script)
        self.close_button.clicked.connect(self.close)
        
        # Enable/disable related controls
        self.create_user.toggled.connect(lambda checked: self.username.setEnabled(checked))
        self.create_user.toggled.connect(lambda checked: self.user_password.setEnabled(checked))
        self.allow_specific_ips.toggled.connect(lambda checked: self.allowed_ips.setEnabled(checked))
        self.generate_keys.toggled.connect(lambda checked: self.key_type.setEnabled(checked))
        self.generate_keys.toggled.connect(lambda checked: self.key_bits.setEnabled(checked))
        
        # Initial state
        self.username.setEnabled(False)
        self.user_password.setEnabled(False)
        self.allowed_ips.setEnabled(False)
        self.key_type.setEnabled(False)
        self.key_bits.setEnabled(False)
    
    def _generate_script(self):
        """Generate the PowerShell script based on configuration."""
        script_parts = []
        
        # Script header
        script_parts.append("""# PowerShell SSH Server Setup Script
# Generated by SSH Tunnel Manager
# Run this script as Administrator on Windows Server/Desktop

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator"))
{
    Write-Error "This script must be run as Administrator!"
    exit 1
}

Write-Host "SSH Server Setup Script Starting..." -ForegroundColor Green
""")
        
        # Install OpenSSH Server
        if self.install_openssh.isChecked():
            script_parts.append("""
# Install OpenSSH Server
Write-Host "Installing OpenSSH Server..." -ForegroundColor Yellow
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0

# Start and enable SSH service
Write-Host "Starting SSH service..." -ForegroundColor Yellow
Start-Service sshd
Set-Service -Name sshd -StartupType 'Automatic'
""")
        
        # Configure SSH
        ssh_config = []
        if not self.enable_password_auth.isChecked():
            ssh_config.append("PasswordAuthentication no")
        else:
            ssh_config.append("PasswordAuthentication yes")
        
        if self.enable_key_auth.isChecked():
            ssh_config.append("PubkeyAuthentication yes")
        
        if self.ssh_port.value() != 22:
            ssh_config.append(f"Port {self.ssh_port.value()}")
        
        if self.disable_root_login.isChecked():
            ssh_config.append("PermitRootLogin no")
        
        ssh_config.append(f"MaxAuthTries {self.max_auth_tries.value()}")
        
        if self.enable_logging.isChecked():
            ssh_config.append("LogLevel INFO")
        
        if ssh_config:
            script_parts.append(f"""
# Configure SSH settings
Write-Host "Configuring SSH settings..." -ForegroundColor Yellow
$sshd_config = @"
{chr(10).join(ssh_config)}
"@

# Backup original config
$configPath = "$env:ProgramData\\ssh\\sshd_config"
if (Test-Path $configPath) {{
    Copy-Item $configPath "$configPath.backup"
}}

# Apply configuration
$sshd_config | Out-File -FilePath $configPath -Encoding UTF8 -Append
""")
        
        # Create user
        if self.create_user.isChecked() and self.username.text().strip():
            username = self.username.text().strip()
            password_part = ""
            if self.user_password.text().strip():
                password_part = f"""
$securePassword = ConvertTo-SecureString "{self.user_password.text()}" -AsPlainText -Force
New-LocalUser -Name "{username}" -Password $securePassword -Description "SSH User" -UserMayNotChangePassword
"""
            else:
                password_part = f"""
New-LocalUser -Name "{username}" -NoPassword -Description "SSH User"
"""
            
            script_parts.append(f"""
# Create SSH user
Write-Host "Creating user {username}..." -ForegroundColor Yellow
{password_part}
Add-LocalGroupMember -Group "Remote Desktop Users" -Member "{username}"
""")
        
        # Generate SSH keys
        if self.generate_keys.isChecked():
            key_type = self.key_type.currentText()
            key_bits_param = ""
            if key_type == "rsa":
                key_bits_param = f" -b {self.key_bits.value()}"
            
            script_parts.append(f"""
# Generate SSH keys
Write-Host "Generating SSH keys..." -ForegroundColor Yellow
$keyPath = "$env:USERPROFILE\\.ssh\\id_{key_type}"
if (-not (Test-Path "$env:USERPROFILE\\.ssh")) {{
    New-Item -ItemType Directory -Path "$env:USERPROFILE\\.ssh" -Force
}}

# Generate key pair
ssh-keygen -t {key_type}{key_bits_param} -f $keyPath -N '""' -C "Generated by SSH Setup Script"

Write-Host "SSH keys generated:" -ForegroundColor Green
Write-Host "Private key: $keyPath" -ForegroundColor Cyan
Write-Host "Public key: $keyPath.pub" -ForegroundColor Cyan
""")
        
        # Configure firewall
        if self.configure_firewall.isChecked():
            port = self.ssh_port.value()
            if self.allow_specific_ips.isChecked() and self.allowed_ips.text().strip():
                ips = [ip.strip() for ip in self.allowed_ips.text().split(",") if ip.strip()]
                ip_param = f" -RemoteAddress {','.join(ips)}"
            else:
                ip_param = ""
            
            script_parts.append(f"""
# Configure Windows Firewall
Write-Host "Configuring firewall..." -ForegroundColor Yellow
New-NetFirewallRule -DisplayName "SSH Server" -Direction Inbound -Protocol TCP -LocalPort {port} -Action Allow{ip_param}
""")
        
        # Restart SSH service
        script_parts.append("""
# Restart SSH service to apply changes
Write-Host "Restarting SSH service..." -ForegroundColor Yellow
Restart-Service sshd

# Show service status
Write-Host "SSH Server setup completed!" -ForegroundColor Green
Get-Service sshd

Write-Host "SSH server is now running on port """ + str(self.ssh_port.value()) + """" -ForegroundColor Cyan
""")
        
        # Generate final script
        script = "\n".join(script_parts)
        self.script_text.setPlainText(script)
        
        # Switch to script tab
        self.tab_widget.setCurrentIndex(1)
        
        QMessageBox.information(self, "Script Generated", "PowerShell script has been generated successfully!")
    
    def _save_script(self):
        """Save the script to a file."""
        if not self.script_text.toPlainText().strip():
            QMessageBox.warning(self, "No Script", "Please generate a script first.")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save PowerShell Script", "ssh_setup.ps1", "PowerShell Scripts (*.ps1);;All Files (*)"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.script_text.toPlainText())
                QMessageBox.information(self, "Script Saved", f"Script saved to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Save Error", f"Failed to save script: {str(e)}")
    
    def _copy_script(self):
        """Copy the script to clipboard."""
        if not self.script_text.toPlainText().strip():
            QMessageBox.warning(self, "No Script", "Please generate a script first.")
            return
        
        clipboard = QApplication.clipboard()
        clipboard.setText(self.script_text.toPlainText())
        QMessageBox.information(self, "Copied", "Script copied to clipboard!")


class PowerShellGeneratorManager:
    """Manager class for PowerShell script generation."""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.dialog = None
    
    def show_generator(self):
        """Show the PowerShell generator dialog."""
        if self.dialog is None:
            self.dialog = PowerShellGeneratorDialog(self.parent)
        
        self.dialog.show()
        self.dialog.raise_()
        self.dialog.activateWindow()
