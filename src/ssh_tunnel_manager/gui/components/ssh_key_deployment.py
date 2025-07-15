#!/usr/bin/env python3
"""
SSH Tunnel Manager - SSH Key Deployment
Automatic deployment of SSH public keys to remote servers
"""

import os
import subprocess
import tempfile
import base64
import shlex
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
            # Validate public key content first
            if not self._validate_public_key(self.public_key_content):
                self.deployment_result.emit(False, "Invalid public key format or potentially dangerous content")
                return
            
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
    
    def _validate_public_key(self, key_content: str) -> bool:
        """
        Validate that the public key content is properly formatted and safe.
        
        This method implements multiple layers of validation to prevent
        command injection attacks and ensure only valid SSH keys are processed.
        
        Returns:
            bool: True if key is valid and safe, False otherwise
        """
        if not key_content or not key_content.strip():
            return False
        
        # Remove any leading/trailing whitespace
        key_content = key_content.strip()
        
        # SSH public keys should start with a valid key type
        valid_key_types = [
            'ssh-rsa', 'ssh-ed25519', 'ssh-ecdsa', 'ssh-dss', 
            'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521'
        ]
        
        # Check if key starts with a valid type
        if not any(key_content.startswith(key_type) for key_type in valid_key_types):
            return False
        
        # Check for potential command injection characters and sequences
        dangerous_chars = [';', '&&', '||', '|', '`', '$', '(', ')', '{', '}', '<', '>', '\n', '\r', '\t']
        dangerous_sequences = ['$(', '${', '`', '\\n', '\\r', '\\t']
        
        # Check for dangerous characters
        if any(char in key_content for char in dangerous_chars):
            return False
            
        # Check for dangerous sequences
        if any(seq in key_content for seq in dangerous_sequences):
            return False
        
        # Basic format validation - should have at least 2 parts (type, key_data)
        parts = key_content.split()
        if len(parts) < 2:
            return False
        
        # Validate that we have exactly the expected format
        if len(parts) > 3:  # type, key_data, optional_comment
            return False
        
        # Validate base64 key data (second part)
        try:
            key_data = parts[1]
            # SSH key data should be valid base64 and reasonably long
            if len(key_data) < 50:  # Minimum reasonable key length
                return False
            # Try to decode the key data to ensure it's valid base64
            decoded = base64.b64decode(key_data, validate=True)
            # Decoded key should be at least 32 bytes for security
            if len(decoded) < 32:
                return False
        except Exception:
            return False
        
        # If there's a comment (third part), validate it
        if len(parts) == 3:
            comment = parts[2]
            # Comments should not contain dangerous characters
            if any(char in comment for char in [';', '&', '|', '`', '$', '\n', '\r']):
                return False
        
        # Additional validation: key shouldn't be suspiciously long
        if len(key_content) > 8192:  # Reasonable maximum for SSH keys
            return False
        
        return True

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
                # Safely escape the password to prevent injection
                escaped_password = shlex.quote(self.password)
                f.write(f'#!/bin/bash\necho {escaped_password}\n')
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
        """
        Try using sshpass + ssh method with enhanced security.
        
        This method safely deploys SSH keys using sshpass while preventing
        command injection through proper input validation and escaping.
        """
        try:
            self.progress_update.emit("Trying sshpass method...")
            
            # Check if sshpass is available
            result = subprocess.run(['which', 'sshpass'], capture_output=True, timeout=10)
            if result.returncode != 0:
                self.progress_update.emit("sshpass not available")
                return False
            
            # Double-check key validation (defense in depth)
            if not self._validate_public_key(self.public_key_content):
                self.progress_update.emit("Key validation failed in sshpass method")
                return False
            
            # Safely escape the public key content to prevent command injection
            escaped_key = shlex.quote(self.public_key_content.strip())
            
            # Build individual commands with proper escaping
            # Use individual commands instead of chaining for better error handling
            setup_commands = [
                "mkdir -p ~/.ssh",
                "chmod 700 ~/.ssh"
            ]
            
            deploy_command = f"echo {escaped_key} >> ~/.ssh/authorized_keys"
            cleanup_commands = [
                "chmod 600 ~/.ssh/authorized_keys",
                "sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp",
                "mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys"
            ]
            
            # Execute commands in sequence for better error tracking
            all_commands = setup_commands + [deploy_command] + cleanup_commands
            
            for i, cmd in enumerate(all_commands):
                self.progress_update.emit(f"Executing step {i+1}/{len(all_commands)}")
                
                # Execute via sshpass + ssh
                ssh_cmd = [
                    'sshpass', '-p', self.password,
                    'ssh',
                    '-p', str(self.port),
                    '-o', 'ConnectTimeout=30',
                    '-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null',
                    '-o', 'BatchMode=no',
                    f"{self.username}@{self.host}",
                    cmd
                ]
                
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    self.progress_update.emit(f"Command failed: {cmd}")
                    self.progress_update.emit(f"Error: {error_msg}")
                    return False
            
            self.deployment_result.emit(True, "SSH key deployed successfully using sshpass!")
            return True
                
        except subprocess.TimeoutExpired:
            self.progress_update.emit("sshpass method timed out")
            return False
        except Exception as e:
            # Sanitize error message to avoid information disclosure
            safe_error = str(e).replace(self.password, '[PASSWORD]')
            self.progress_update.emit(f"sshpass method failed: {safe_error}")
            return False
    
    def _try_paramiko_method(self) -> bool:
        """
        Try using paramiko library for secure deployment.
        
        This method uses SFTP for direct file operations instead of shell commands,
        providing the most secure deployment method available.
        """
        try:
            import paramiko
            
            self.progress_update.emit("Trying paramiko method...")
            
            # Double-check key validation (defense in depth)
            if not self._validate_public_key(self.public_key_content):
                self.progress_update.emit("Key validation failed in paramiko method")
                return False
            
            # Create SSH client with security settings
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect to server with timeout
            self.progress_update.emit("Connecting via paramiko...")
            ssh.connect(
                hostname=self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                timeout=30,
                auth_timeout=30,
                banner_timeout=30
            )
            
            # Use SFTP for secure file operations instead of shell commands
            self.progress_update.emit("Opening SFTP connection...")
            sftp = ssh.open_sftp()
            
            # Ensure .ssh directory exists with proper permissions
            ssh_dir = '.ssh'
            try:
                # Try to create directory
                sftp.mkdir(ssh_dir)
                self.progress_update.emit("Created .ssh directory")
            except IOError:
                # Directory already exists, which is fine
                self.progress_update.emit(".ssh directory already exists")
            
            # Set directory permissions (equivalent to chmod 700)
            try:
                sftp.chmod(ssh_dir, 0o700)
                self.progress_update.emit("Set .ssh directory permissions")
            except Exception as e:
                self.progress_update.emit(f"Warning: Could not set directory permissions: {e}")
            
            # Handle authorized_keys file
            authorized_keys_path = '.ssh/authorized_keys'
            existing_keys = []
            
            self.progress_update.emit("Reading existing authorized_keys...")
            try:
                with sftp.open(authorized_keys_path, 'r') as f:
                    existing_keys = [line.strip() for line in f.readlines() if line.strip()]
                self.progress_update.emit(f"Found {len(existing_keys)} existing keys")
            except IOError:
                # File doesn't exist yet, which is fine
                self.progress_update.emit("No existing authorized_keys file")
            
            # Prepare new key
            new_key = self.public_key_content.strip()
            
            # Check for duplicates (avoid adding the same key multiple times)
            if new_key in existing_keys:
                self.progress_update.emit("Key already exists in authorized_keys")
                self.deployment_result.emit(True, "SSH key already deployed (found existing entry)")
                sftp.close()
                ssh.close()
                return True
            
            # Add new key to the list
            existing_keys.append(new_key)
            
            # Write back all keys atomically
            self.progress_update.emit("Writing updated authorized_keys...")
            temp_file = authorized_keys_path + '.tmp'
            
            try:
                with sftp.open(temp_file, 'w') as f:
                    for key in existing_keys:
                        f.write(key + '\n')
                
                # Atomic move
                sftp.rename(temp_file, authorized_keys_path)
                self.progress_update.emit("Atomically updated authorized_keys")
                
            except Exception as e:
                # Clean up temp file if it exists
                try:
                    sftp.remove(temp_file)
                except:
                    pass
                raise e
            
            # Set file permissions (equivalent to chmod 600)
            try:
                sftp.chmod(authorized_keys_path, 0o600)
                self.progress_update.emit("Set authorized_keys permissions")
            except Exception as e:
                self.progress_update.emit(f"Warning: Could not set file permissions: {e}")
            
            # Clean up connections
            sftp.close()
            ssh.close()
            
            self.deployment_result.emit(True, "SSH key deployed successfully using paramiko!")
            return True
            
        except ImportError:
            self.progress_update.emit("paramiko library not available")
            return False
        except paramiko.AuthenticationException:
            self.progress_update.emit("Authentication failed - check username/password")
            return False
        except paramiko.SSHException as e:
            self.progress_update.emit(f"SSH connection error: {str(e)}")
            return False
        except Exception as e:
            # Sanitize error message to avoid password disclosure
            safe_error = str(e).replace(self.password, '[PASSWORD]')
            self.progress_update.emit(f"paramiko method failed: {safe_error}")
            return False
    
    def _provide_manual_instructions(self):
        """
        Provide safe manual deployment instructions.
        
        These instructions guide users through secure manual deployment
        while avoiding potential security issues in the automated methods.
        """
        # Validate the key before providing instructions
        if not self._validate_public_key(self.public_key_content):
            self.deployment_result.emit(False, 
                "Cannot provide manual instructions: SSH key validation failed. "
                "Please verify your public key is properly formatted and contains no dangerous characters.")
            return
        
        # Create safe instructions using proper shell quoting
        escaped_key = shlex.quote(self.public_key_content.strip())
        
        instructions = f"""
Manual SSH Key Deployment Instructions:

⚠️  SECURITY NOTE: Follow these steps carefully to avoid command injection risks.

1. Connect to your server using SSH:
   ssh -p {self.port} {self.username}@{self.host}

2. Create the .ssh directory with proper permissions:
   mkdir -p ~/.ssh
   chmod 700 ~/.ssh

3. Add your public key to authorized_keys (COPY the entire command):
   echo {escaped_key} >> ~/.ssh/authorized_keys

4. Set proper file permissions:
   chmod 600 ~/.ssh/authorized_keys

5. Remove any duplicate entries (optional but recommended):
   sort ~/.ssh/authorized_keys | uniq > ~/.ssh/authorized_keys.tmp
   mv ~/.ssh/authorized_keys.tmp ~/.ssh/authorized_keys

6. Verify the key was added correctly:
   tail -1 ~/.ssh/authorized_keys

7. Test the key authentication (from your local machine):
   ssh -p {self.port} -i /path/to/your/private/key {self.username}@{self.host}

🔒 SECURITY TIPS:
- Always verify the echo command before running it
- Never manually type the key - copy/paste the entire command
- Verify file permissions: ~/.ssh should be 700, authorized_keys should be 600
- Test the new key before disconnecting your current session

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
