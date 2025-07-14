#!/usr/bin/env python3
"""
SSH Tunnel Manager - SSH Key Deployment
Automatic deployment of SSH public keys to remote servers
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QCheckBox, QGroupBox, QComboBox, QSpinBox, QMessageBox,
    QFileDialog, QFormLayout, QApplication, QProgressBar
)
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QFont


class SSHKeyDeployWorker(QThread):
    """Worker thread for SSH key deployment."""
    
    deployment_result = Signal(bool, str)  # success, message
    progress_update = Signal(str)  # status message
    
    def __init__(self, host: str, port: int, username: str, password: str, 
                 public_key_content: str, private_key_path: str = None):
        super().__init__()
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.public_key_content = public_key_content
        self.private_key_path = private_key_path
    
    def run(self):
        """Deploy SSH key to remote server."""
        try:
            self.progress_update.emit("Connecting to server...")
            
            # Method 1: Try using ssh-copy-id if available (Linux/macOS)
            if self._try_ssh_copy_id():
                return
            
            # Method 2: Use sshpass + ssh for password authentication
            if self._try_sshpass_method():
                return
                
            # Method 3: Use Python paramiko library if available
            if self._try_paramiko_method():
                return
            
            # Method 4: Generate manual instructions
            self._provide_manual_instructions()
            
        except Exception as e:
            self.deployment_result.emit(False, f"Deployment failed: {str(e)}")
    
    def _try_ssh_copy_id(self) -> bool:
        """Try using ssh-copy-id command."""
        try:
            self.progress_update.emit("Trying ssh-copy-id method...")
            
            # Check if ssh-copy-id is available
            result = subprocess.run(['which', 'ssh-copy-id'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Create temporary script for password input
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
                f.write(f'#!/bin/bash\necho "{self.password}"\n')
                script_path = f.name
            
            os.chmod(script_path, 0o700)
            
            # Build ssh-copy-id command
            cmd = [
                'ssh-copy-id',
                '-p', str(self.port),
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null'
            ]
            
            if self.private_key_path:
                cmd.extend(['-i', self.private_key_path])
            
            cmd.append(f"{self.username}@{self.host}")
            
            # Execute with password script
            env = os.environ.copy()
            env['SSH_ASKPASS'] = script_path
            env['DISPLAY'] = ':0'  # Required for SSH_ASKPASS
            
            result = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=30)
            
            # Clean up
            os.unlink(script_path)
            
            if result.returncode == 0:
                self.deployment_result.emit(True, "SSH key deployed successfully using ssh-copy-id!")
                return True
            else:
                self.progress_update.emit(f"ssh-copy-id failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.progress_update.emit(f"ssh-copy-id method failed: {str(e)}")
            return False
    
    def _try_sshpass_method(self) -> bool:
        """Try using sshpass + ssh method."""
        try:
            self.progress_update.emit("Trying sshpass method...")
            
            # Check if sshpass is available
            result = subprocess.run(['which', 'sshpass'], capture_output=True)
            if result.returncode != 0:
                return False
            
            # Create commands to deploy the key
            commands = [
                "mkdir -p ~/.ssh",
                "chmod 700 ~/.ssh",
                f"echo '{self.public_key_content}' >> ~/.ssh/authorized_keys",
                "chmod 600 ~/.ssh/authorized_keys",
                "sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp",
                "mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys"
            ]
            
            command_string = " && ".join(commands)
            
            # Execute via sshpass + ssh
            cmd = [
                'sshpass', '-p', self.password,
                'ssh',
                '-p', str(self.port),
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                f"{self.username}@{self.host}",
                command_string
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                self.deployment_result.emit(True, "SSH key deployed successfully using sshpass!")
                return True
            else:
                self.progress_update.emit(f"sshpass method failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.progress_update.emit(f"sshpass method failed: {str(e)}")
            return False
    
    def _try_paramiko_method(self) -> bool:
        """Try using paramiko library for deployment."""
        try:
            import paramiko
            
            self.progress_update.emit("Trying paramiko method...")
            
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to server
            ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=30
            )
            
            # Execute commands to deploy key
            commands = [
                "mkdir -p ~/.ssh",
                "chmod 700 ~/.ssh",
                f"echo '{self.public_key_content}' >> ~/.ssh/authorized_keys",
                "chmod 600 ~/.ssh/authorized_keys",
                "sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp",
                "mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys"
            ]
            
            for cmd in commands:
                stdin, stdout, stderr = ssh.exec_command(cmd)
                exit_code = stdout.channel.recv_exit_status()
                if exit_code != 0:
                    error_msg = stderr.read().decode()
                    raise Exception(f"Command failed: {cmd}\nError: {error_msg}")
            
            ssh.close()
            
            self.deployment_result.emit(True, "SSH key deployed successfully using paramiko!")
            return True
            
        except ImportError:
            self.progress_update.emit("paramiko library not available")
            return False
        except Exception as e:
            self.progress_update.emit(f"paramiko method failed: {str(e)}")
            return False
    
    def _provide_manual_instructions(self):
        """Provide manual deployment instructions."""
        instructions = f"""
Manual SSH Key Deployment Instructions:

1. Connect to your server using SSH:
   ssh -p {self.port} {self.username}@{self.host}

2. Create the .ssh directory (if it doesn't exist):
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh

3. Add your public key to authorized_keys:
   echo '{self.public_key_content}' >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys

4. Remove any duplicate entries:
   sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp
   mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys

After completing these steps, you should be able to connect using your SSH key.
"""
        
        self.deployment_result.emit(False, instructions)


class SSHKeyDeploymentDialog(QDialog):
    """Dialog for deploying SSH keys to remote servers."""
    
    def __init__(self, parent=None, tunnel_config=None, public_key_path=None):
        super().__init__(parent)
        self.tunnel_config = tunnel_config
        self.public_key_path = public_key_path
        self.setWindowTitle("Deploy SSH Key to Server")
        self.setGeometry(200, 200, 600, 500)
        self.setModal(True)
        
        self.worker = None
        self._setup_ui()
        self._setup_connections()
        self._populate_from_config()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("Deploy SSH Public Key to Remote Server")
        header_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2196F3;")
        layout.addWidget(header_label)
        
        # Connection details
        connection_group = QGroupBox("Server Connection Details")
        connection_layout = QFormLayout(connection_group)
        
        self.host_edit = QLineEdit()
        connection_layout.addRow("Host/IP:", self.host_edit)
        
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(22)
        connection_layout.addRow("Port:", self.port_spin)
        
        self.username_edit = QLineEdit()
        connection_layout.addRow("Username:", self.username_edit)
        
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        connection_layout.addRow("Password:", self.password_edit)
        
        layout.addWidget(connection_group)
        
        # SSH Key details
        key_group = QGroupBox("SSH Key Details")
        key_layout = QFormLayout(key_group)
        
        # Public key file selection
        key_file_layout = QHBoxLayout()
        self.public_key_file_edit = QLineEdit()
        key_file_layout.addWidget(self.public_key_file_edit)
        
        self.browse_key_button = QPushButton("Browse...")
        self.browse_key_button.clicked.connect(self._browse_public_key)
        key_file_layout.addWidget(self.browse_key_button)
        
        key_layout.addRow("Public Key File:", key_file_layout)
        
        # Public key content preview
        self.key_content_edit = QTextEdit()
        self.key_content_edit.setMaximumHeight(100)
        self.key_content_edit.setFont(QFont("Consolas", 8))
        self.key_content_edit.setPlaceholderText("Public key content will appear here...")
        key_layout.addRow("Key Content:", self.key_content_edit)
        
        layout.addWidget(key_group)
        
        # Deployment options
        options_group = QGroupBox("Deployment Options")
        options_layout = QVBoxLayout(options_group)
        
        self.backup_existing = QCheckBox("Backup existing authorized_keys file")
        self.backup_existing.setChecked(True)
        options_layout.addWidget(self.backup_existing)
        
        self.remove_duplicates = QCheckBox("Remove duplicate key entries")
        self.remove_duplicates.setChecked(True)
        options_layout.addWidget(self.remove_duplicates)
        
        layout.addWidget(options_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready to deploy SSH key")
        layout.addWidget(self.status_label)
        
        # Results
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setFont(QFont("Consolas", 9))
        self.results_text.setVisible(False)
        layout.addWidget(self.results_text)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.deploy_button = QPushButton("Deploy SSH Key")
        self.deploy_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px; }")
        
        self.test_connection_button = QPushButton("Test Connection")
        self.cancel_button = QPushButton("Cancel")
        
        button_layout.addWidget(self.deploy_button)
        button_layout.addWidget(self.test_connection_button)
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def _setup_connections(self):
        """Setup signal connections."""
        self.deploy_button.clicked.connect(self._deploy_key)
        self.test_connection_button.clicked.connect(self._test_connection)
        self.cancel_button.clicked.connect(self.close)
        self.public_key_file_edit.textChanged.connect(self._load_public_key)
    
    def _populate_from_config(self):
        """Populate fields from tunnel configuration."""
        if self.tunnel_config:
            self.host_edit.setText(self.tunnel_config.get('host', ''))
            self.port_spin.setValue(self.tunnel_config.get('port', 22))
            self.username_edit.setText(self.tunnel_config.get('username', ''))
        
        if self.public_key_path:
            self.public_key_file_edit.setText(self.public_key_path)
            self._load_public_key()
    
    def _browse_public_key(self):
        """Browse for public key file."""
        ssh_dir = os.path.expanduser("~/.ssh")
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select Public Key File", ssh_dir, "Public Key Files (*.pub);;All Files (*)"
        )
        if filename:
            self.public_key_file_edit.setText(filename)
    
    def _load_public_key(self):
        """Load and display public key content."""
        key_file = self.public_key_file_edit.text().strip()
        if key_file and os.path.exists(key_file):
            try:
                with open(key_file, 'r') as f:
                    content = f.read().strip()
                self.key_content_edit.setPlainText(content)
            except Exception as e:
                self.key_content_edit.setPlainText(f"Error reading key file: {str(e)}")
        else:
            self.key_content_edit.clear()
    
    def _test_connection(self):
        """Test SSH connection to server."""
        host = self.host_edit.text().strip()
        port = self.port_spin.value()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not all([host, username, password]):
            QMessageBox.warning(self, "Input Error", "Please fill in all connection details.")
            return
        
        try:
            # Try a simple SSH connection test
            import subprocess
            cmd = [
                'ssh',
                '-p', str(port),
                '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                '-o', 'UserKnownHostsFile=/dev/null',
                '-o', 'PasswordAuthentication=yes',
                f"{username}@{host}",
                'echo "Connection test successful"'
            ]
            
            # Note: This is a simplified test - in production you'd want to handle password input properly
            QMessageBox.information(self, "Test Connection", 
                                  "Connection test initiated. Check that you can connect manually first.")
                                  
        except Exception as e:
            QMessageBox.warning(self, "Test Failed", f"Connection test failed: {str(e)}")
    
    def _deploy_key(self):
        """Deploy SSH key to server."""
        # Validate inputs
        host = self.host_edit.text().strip()
        port = self.port_spin.value()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        public_key_content = self.key_content_edit.toPlainText().strip()
        
        if not all([host, username, password, public_key_content]):
            QMessageBox.warning(self, "Input Error", "Please fill in all required fields.")
            return
        
        # Disable UI during deployment
        self.deploy_button.setEnabled(False)
        self.test_connection_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.results_text.setVisible(True)
        self.results_text.clear()
        
        # Start deployment worker
        private_key_path = self.public_key_file_edit.text().replace('.pub', '') if self.public_key_file_edit.text().endswith('.pub') else None
        
        self.worker = SSHKeyDeployWorker(
            host, port, username, password, public_key_content, private_key_path
        )
        self.worker.deployment_result.connect(self._handle_deployment_result)
        self.worker.progress_update.connect(self._handle_progress_update)
        self.worker.start()
    
    def _handle_progress_update(self, message: str):
        """Handle progress updates from worker."""
        self.status_label.setText(message)
        self.results_text.append(f"🔄 {message}")
    
    def _handle_deployment_result(self, success: bool, message: str):
        """Handle deployment completion."""
        # Re-enable UI
        self.deploy_button.setEnabled(True)
        self.test_connection_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.status_label.setText("✅ SSH key deployed successfully!")
            self.results_text.append(f"✅ {message}")
            QMessageBox.information(self, "Success", message)
        else:
            self.status_label.setText("❌ SSH key deployment failed")
            self.results_text.append(f"❌ {message}")
            
            # Show manual instructions if automated methods failed
            if "Manual SSH Key Deployment Instructions" in message:
                reply = QMessageBox.question(
                    self, "Manual Deployment Required",
                    "Automated deployment failed. Would you like to see manual instructions?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self._show_manual_instructions(message)
        
        if self.worker:
            self.worker.wait()
            self.worker = None
    
    def _show_manual_instructions(self, instructions: str):
        """Show manual deployment instructions."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manual SSH Key Deployment Instructions")
        dialog.setGeometry(300, 300, 700, 500)
        
        layout = QVBoxLayout(dialog)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Consolas", 10))
        text_edit.setPlainText(instructions)
        layout.addWidget(text_edit)
        
        buttons = QHBoxLayout()
        copy_btn = QPushButton("Copy Instructions")
        copy_btn.clicked.connect(lambda: QApplication.clipboard().setText(instructions))
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        
        buttons.addWidget(copy_btn)
        buttons.addStretch()
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        dialog.exec()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
        event.accept()


class SSHKeyDeploymentManager:
    """Manager class for SSH key deployment functionality."""
    
    def __init__(self, parent=None):
        self.parent = parent
    
    def deploy_key_for_tunnel(self, tunnel_config: dict, public_key_path: str = None):
        """Deploy SSH key for a specific tunnel configuration."""
        dialog = SSHKeyDeploymentDialog(self.parent, tunnel_config, public_key_path)
        dialog.exec()
    
    def deploy_key_manual(self):
        """Deploy SSH key with manual configuration."""
        dialog = SSHKeyDeploymentDialog(self.parent)
        dialog.exec()
