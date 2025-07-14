#!/usr/bin/env python3
"""
SSH Tunnel Manager - Multi-Hop SFTP Browser

This module extends the SFTP Browser to support accessing file systems through 
tunneled connections, enabling access to both the SSH host and the remote host
at the end of the tunnel.
"""

import os
import stat
import threading
import socket
import paramiko
from pathlib import Path
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox,
    QLabel, QMessageBox, QGroupBox, QTreeWidget, QTreeWidgetItem,
    QSplitter, QLineEdit, QProgressBar, QTextEdit, QMenu,
    QCheckBox, QSpinBox, QApplication, QFileDialog, QWidget
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QAction, QIcon, QFont, QCursor

from ...core.models import TunnelConfig
from .sftp_browser import SFTPFileBrowser, FileTransferWorker


class MultiHopSFTPBrowser(SFTPFileBrowser):
    """SFTP Browser that supports accessing both the SSH host and tunneled remote host."""
    
    def __init__(self, tunnel_config: TunnelConfig, password: Optional[str] = None, 
                access_remote: bool = False, parent: Optional[QWidget] = None):
        """
        Initialize the Multi-Hop SFTP Browser.
        
        Args:
            tunnel_config: The tunnel configuration
            password: Optional SSH password
            access_remote: If True, try to access the remote host through the tunnel
            parent: Parent Qt widget
        """
        # Don't call super() yet - we'll do our own initialization
        QDialog.__init__(self, parent)
        self.tunnel_config = tunnel_config
        self.password = password
        self.ssh_client = None
        self.sftp_client = None
        self.current_remote_path = "/"
        self.transfer_worker = None
        self.access_remote = access_remote
        
        # Set window title based on access mode
        if access_remote:
            self.target_host = tunnel_config.remote_host
            self.target_port = tunnel_config.remote_port
            self.setWindowTitle(f"SFTP Browser - {tunnel_config.remote_host} (via tunnel)")
        else:
            self.target_host = tunnel_config.ssh_host
            self.target_port = tunnel_config.ssh_port
            self.setWindowTitle(f"SFTP Browser - {tunnel_config.ssh_host}")
        
        self.setGeometry(200, 200, 900, 600)
        self.setup_ui()
        
        # Connect to the appropriate host
        if access_remote:
            self.connect_through_tunnel()
        else:
            self.connect_to_server()
    
    def setup_ui(self):
        """Setup the dialog UI with connection selector."""
        super().setup_ui()
        
        # Create host selector at the top
        host_selector_layout = QHBoxLayout()
        host_selector_layout.addWidget(QLabel("Access:"))
        
        self.host_selector = QComboBox()
        self.host_selector.addItem(f"SSH Host ({self.tunnel_config.ssh_host})")
        self.host_selector.addItem(f"Remote Host ({self.tunnel_config.remote_host})")
        self.host_selector.setCurrentIndex(1 if self.access_remote else 0)
        self.host_selector.currentIndexChanged.connect(self.on_host_changed)
        host_selector_layout.addWidget(self.host_selector)
        
        # Insert the host selector layout at the top
        main_layout = self.layout()
        main_layout.insertLayout(0, host_selector_layout)
        
    def on_host_changed(self, index):
        """Handle changing between SSH host and remote host."""
        if index == 0 and self.access_remote:
            # Switching from remote to SSH host
            self.disconnect()
            self.access_remote = False
            self.target_host = self.tunnel_config.ssh_host
            self.target_port = self.tunnel_config.ssh_port
            self.setWindowTitle(f"SFTP Browser - {self.tunnel_config.ssh_host}")
            self.connect_to_server()
            
        elif index == 1 and not self.access_remote:
            # Switching from SSH host to remote
            self.disconnect()
            self.access_remote = True
            self.target_host = self.tunnel_config.remote_host
            self.target_port = self.tunnel_config.remote_port
            self.setWindowTitle(f"SFTP Browser - {self.tunnel_config.remote_host} (via tunnel)")
            self.connect_through_tunnel()
    
    def connect_through_tunnel(self):
        """
        Connect to the remote host through the SSH tunnel.
        
        This creates a new SSH connection to the remote host using the existing
        SSH tunnel as a jump host.
        """
        try:
            self.log(f"Connecting to remote host {self.tunnel_config.remote_host} via tunnel...")
            
            # First check if tunnel is active by attempting to connect to the forwarded port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            
            try:
                # Try to connect to the local port that's forwarded
                sock.connect(('localhost', self.tunnel_config.local_port))
                sock.close()
                
                # If we get here, the tunnel is active
                self.log(f"Tunnel is active on localhost:{self.tunnel_config.local_port}")
                
                # Additional validation using the dedicated method
                if not self._check_local_tunnel_port():
                    raise Exception(f"Local tunnel port {self.tunnel_config.local_port} validation failed")
                
            except (socket.timeout, socket.error, ConnectionRefusedError) as e:
                self.log(f"Tunnel not active on localhost:{self.tunnel_config.local_port}")
                QMessageBox.critical(
                    self, 
                    "Tunnel Not Active", 
                    f"Cannot connect to {self.tunnel_config.remote_host} because the tunnel is not active.\n\n"
                    f"Please start the tunnel first and then try again.\n\n"
                    f"Error: {str(e)}"
                )
                self.close()
                return
                
            # Now we need to create a new SSH connection to the remote host
            # Since we can't directly SSH to the remote host through the forwarded port
            # (which forwards to remote_host:remote_port, not remote_host:22),
            # we need to use the existing SSH connection as a jump host
            
            # Create first SSH connection to the jump host
            jump_ssh = paramiko.SSHClient()
            jump_ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            jump_connect_params = {
                'hostname': self.tunnel_config.ssh_host,
                'port': self.tunnel_config.ssh_port,
                'username': self.tunnel_config.ssh_user,
                'timeout': 30
            }
            
            # Add authentication for jump host
            if self.password:
                jump_connect_params['password'] = self.password
            elif self.tunnel_config.ssh_key_path and os.path.exists(self.tunnel_config.ssh_key_path):
                jump_connect_params['key_filename'] = self.tunnel_config.ssh_key_path
            
            self.log(f"Connecting to jump host {self.tunnel_config.ssh_host}...")
            jump_ssh.connect(**jump_connect_params)
            
            # Check if SSH is available on the remote host
            self.log(f"Checking SSH connectivity to {self.tunnel_config.remote_host}:22...")
            if not self._check_remote_ssh_port(jump_ssh):
                raise Exception(f"SSH port (22) is not accessible on remote host {self.tunnel_config.remote_host}")
            
            # Create a channel through the jump host to the remote host's SSH port
            self.log(f"Creating channel to {self.tunnel_config.remote_host}:22...")
            jump_transport = jump_ssh.get_transport()
            dest_addr = (self.tunnel_config.remote_host, 22)  # SSH port on remote host
            local_addr = ('localhost', self.tunnel_config.local_port)  # Local tunnel port
            channel = jump_transport.open_channel("direct-tcpip", dest_addr, local_addr)
            
            # Create SSH client for the remote host using the channel
            self.log(f"Creating SSH transport for remote host {self.tunnel_config.remote_host}...")
            
            # Create transport directly from the channel
            remote_transport = paramiko.Transport(channel)
            
            # Start the client
            remote_transport.start_client()
            
            # Authenticate to the remote host
            if self.password:
                self.log(f"Authenticating with password...")
                remote_transport.auth_password(self.tunnel_config.ssh_user, self.password)
            elif self.tunnel_config.ssh_key_path and os.path.exists(self.tunnel_config.ssh_key_path):
                self.log(f"Authenticating with SSH key...")
                # Load the private key
                try:
                    # Try different key types
                    for key_class in [paramiko.RSAKey, paramiko.Ed25519Key, paramiko.ECDSAKey, paramiko.DSSKey]:
                        try:
                            private_key = key_class.from_private_key_file(self.tunnel_config.ssh_key_path)
                            break
                        except:
                            continue
                    else:
                        raise Exception("Could not load SSH private key")
                    
                    remote_transport.auth_publickey(self.tunnel_config.ssh_user, private_key)
                except Exception as key_error:
                    raise Exception(f"SSH key authentication failed: {str(key_error)}")
            else:
                raise Exception("No authentication method provided")
            
            if not remote_transport.is_authenticated():
                raise Exception("Authentication to remote host failed")
                
            self.log(f"Successfully authenticated to remote host!")
            
            # Create SFTP client from the transport
            self.sftp_client = paramiko.SFTPClient.from_transport(remote_transport)
            
            # Store the transport for cleanup
            self.remote_transport = remote_transport
            
            self.log(f"Connected successfully to {self.tunnel_config.remote_host} via tunnel!")
            self.status_label.setText(f"Connected to {self.tunnel_config.remote_host} via tunnel")
            
            # Store jump connection for cleanup
            self.jump_ssh = jump_ssh
            
            # Load initial directory
            self.refresh_remote_files()
                
        except Exception as e:
            self.log(f"Connection to remote host failed: {str(e)}")
            error_msg = f"Failed to connect to remote host through tunnel:\n\n{str(e)}"
            
            # Add specific guidance for common issues
            if "Authentication failed" in str(e):
                error_msg += "\n\nTroubleshooting:\n"
                error_msg += "• Verify SSH credentials for the remote host\n"
                error_msg += "• Check if SSH keys are properly configured\n"
                error_msg += "• Ensure the remote host allows SSH connections"
            elif "No route to host" in str(e) or "Connection refused" in str(e):
                error_msg += "\n\nTroubleshooting:\n"
                error_msg += "• Verify the remote host IP/hostname is correct\n"
                error_msg += "• Check if SSH service is running on the remote host\n"
                error_msg += "• Ensure firewall allows SSH connections on port 22"
            elif "timeout" in str(e).lower():
                error_msg += "\n\nTroubleshooting:\n"
                error_msg += "• Check network connectivity to the remote host\n"
                error_msg += "• Verify the tunnel is properly forwarding traffic\n"
                error_msg += "• Try increasing connection timeout"
            
            QMessageBox.critical(self, "Connection Error", error_msg)
            self.close()
    
    def disconnect(self):
        """Disconnect all SSH connections."""
        try:
            if hasattr(self, 'sftp_client') and self.sftp_client:
                self.sftp_client.close()
                self.sftp_client = None
                
            if hasattr(self, 'remote_transport') and self.remote_transport:
                self.remote_transport.close()
                self.remote_transport = None
                
            if hasattr(self, 'ssh_client') and self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
                
            if hasattr(self, 'jump_ssh') and self.jump_ssh:
                self.jump_ssh.close()
                self.jump_ssh = None
                
        except Exception as e:
            self.log(f"Error during disconnect: {str(e)}")
    
    def _check_remote_ssh_port(self, jump_ssh, timeout=5):
        """
        Check if SSH port (22) is accessible on the remote host through the jump host.
        
        Args:
            jump_ssh: Connected SSH client to the jump host
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if SSH port is accessible, False otherwise
        """
        try:
            self.log(f"Checking SSH port 22 accessibility on {self.tunnel_config.remote_host}...")
            
            # Method 1: Try direct SSH channel (most reliable)
            if self._test_ssh_channel_direct(jump_ssh, timeout):
                return True
                
            # Method 2: Try command-line tools on jump host
            if self._test_ssh_with_commands(jump_ssh, timeout):
                return True
                
            # Method 3: Try SSH banner detection
            if self._test_ssh_banner(jump_ssh, timeout):
                return True
                
            self.log(f"❌ SSH port 22 is not accessible on {self.tunnel_config.remote_host}")
            return False
            
        except Exception as e:
            self.log(f"❌ SSH port check failed: {str(e)}")
            return False
    
    def _test_ssh_channel_direct(self, jump_ssh, timeout=5):
        """
        Test SSH connectivity using direct channel through jump host.
        
        Args:
            jump_ssh: Connected SSH client to the jump host
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if SSH port is accessible, False otherwise
        """
        try:
            self.log(f"Testing direct SSH channel to {self.tunnel_config.remote_host}:22...")
            
            transport = jump_ssh.get_transport()
            # Set socket timeout for the transport
            transport.sock.settimeout(timeout)
            
            # Try to open a channel to the SSH port
            test_channel = transport.open_channel(
                "direct-tcpip", 
                (self.tunnel_config.remote_host, 22), 
                ('localhost', 0)
            )
            
            # If we got here, the port is open. Let's try to read SSH banner
            test_channel.settimeout(timeout)
            banner = test_channel.recv(1024).decode('utf-8', errors='ignore')
            test_channel.close()
            
            if "SSH" in banner:
                self.log(f"✅ SSH port 22 is accessible on {self.tunnel_config.remote_host} (SSH banner detected)")
                return True
            else:
                self.log(f"⚠️ Port 22 is open but no SSH banner detected on {self.tunnel_config.remote_host}")
                return True  # Port is open, might still be SSH
                
        except socket.timeout:
            self.log(f"❌ Connection timeout to {self.tunnel_config.remote_host}:22")
            return False
        except Exception as e:
            self.log(f"❌ Direct channel test failed: {str(e)}")
            return False
    
    def _test_ssh_with_commands(self, jump_ssh, timeout=5):
        """
        Test SSH connectivity using command-line tools on the jump host.
        
        Args:
            jump_ssh: Connected SSH client to the jump host
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if SSH port is accessible, False otherwise
        """
        try:
            self.log(f"Testing SSH connectivity using command-line tools...")
            
            # Prepare commands in order of preference
            test_commands = [
                # netcat with zero I/O mode (most reliable)
                f"nc -z -w{timeout} {self.tunnel_config.remote_host} 22",
                
                # nmap if available
                f"nmap -p 22 --open --host-timeout {timeout}s {self.tunnel_config.remote_host} 2>/dev/null | grep -q '22/tcp open'",
                
                # telnet with timeout
                f"timeout {timeout} telnet {self.tunnel_config.remote_host} 22 </dev/null 2>&1 | grep -q 'Connected\\|SSH'",
                
                # bash TCP redirection
                f"timeout {timeout} bash -c 'exec 3<>/dev/tcp/{self.tunnel_config.remote_host}/22 && echo \"Connection successful\" >&3' 2>/dev/null",
                
                # Python socket test
                f"python3 -c \"import socket; s=socket.socket(); s.settimeout({timeout}); s.connect(('{self.tunnel_config.remote_host}', 22)); print('Connected'); s.close()\" 2>/dev/null",
                
                # Alternative Python check
                f"python -c \"import socket; s=socket.socket(); s.settimeout({timeout}); s.connect(('{self.tunnel_config.remote_host}', 22)); print('Connected'); s.close()\" 2>/dev/null"
            ]
            
            for cmd in test_commands:
                try:
                    tool_name = cmd.split()[0]
                    self.log(f"Testing with {tool_name}...")
                    
                    stdin, stdout, stderr = jump_ssh.exec_command(cmd, timeout=timeout + 5)
                    exit_status = stdout.channel.recv_exit_status()
                    output = stdout.read().decode('utf-8', errors='ignore').strip()
                    error_output = stderr.read().decode('utf-8', errors='ignore').strip()
                    
                    if exit_status == 0:
                        self.log(f"✅ SSH port 22 is accessible on {self.tunnel_config.remote_host} (verified with {tool_name})")
                        if output:
                            self.log(f"Command output: {output}")
                        return True
                    else:
                        self.log(f"❌ {tool_name} failed (exit code: {exit_status})")
                        if error_output:
                            self.log(f"Error: {error_output}")
                        
                except Exception as e:
                    self.log(f"❌ Command '{cmd.split()[0]}' failed: {str(e)}")
                    continue
            
            return False
            
        except Exception as e:
            self.log(f"❌ Command-line test failed: {str(e)}")
            return False
    
    def _test_ssh_banner(self, jump_ssh, timeout=3):
        """
        Test SSH connectivity by attempting to read SSH banner.
        
        Args:
            jump_ssh: Connected SSH client to the jump host
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if SSH banner is detected, False otherwise
        """
        try:
            self.log(f"Testing SSH banner detection on {self.tunnel_config.remote_host}:22...")
            
            # Use socat or nc to connect and read banner
            banner_commands = [
                f"timeout {timeout} socat TCP:{self.tunnel_config.remote_host}:22 STDOUT 2>/dev/null | head -1",
                f"timeout {timeout} nc {self.tunnel_config.remote_host} 22 2>/dev/null | head -1",
                f"echo '' | timeout {timeout} telnet {self.tunnel_config.remote_host} 22 2>/dev/null | grep SSH"
            ]
            
            for cmd in banner_commands:
                try:
                    stdin, stdout, stderr = jump_ssh.exec_command(cmd, timeout=timeout + 2)
                    output = stdout.read().decode('utf-8', errors='ignore').strip()
                    
                    if output and "SSH" in output:
                        self.log(f"✅ SSH banner detected: {output}")
                        return True
                        
                except Exception as e:
                    continue
            
            return False
            
        except Exception as e:
            self.log(f"❌ Banner test failed: {str(e)}")
            return False
    
    def _check_local_tunnel_port(self, timeout=2):
        """
        Check if the local tunnel port is active and accepting connections.
        
        Args:
            timeout: Connection timeout in seconds
            
        Returns:
            bool: True if port is accessible, False otherwise
        """
        try:
            self.log(f"Checking local tunnel port {self.tunnel_config.local_port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('localhost', self.tunnel_config.local_port))
            sock.close()
            
            if result == 0:
                self.log(f"✅ Local tunnel port {self.tunnel_config.local_port} is active")
                return True
            else:
                self.log(f"❌ Local tunnel port {self.tunnel_config.local_port} is not accessible")
                return False
                
        except Exception as e:
            self.log(f"❌ Local port check failed: {str(e)}")
            return False
