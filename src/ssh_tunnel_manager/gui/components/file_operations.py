#!/usr/bin/env python3
"""
SSH Tunnel Manager - File Operations Manager
"""

import os
from typing import Optional
from PySide6.QtWidgets import QMessageBox, QDialog, QMenu, QInputDialog
from PySide6.QtCore import QObject, QTimer, Signal

from ...core.models import TunnelConfig
from ...core.tunnel_process import TunnelProcess
from ..dialogs.sftp_browser import SFTPFileBrowser
from ..dialogs.multi_hop_sftp_browser import MultiHopSFTPBrowser
from ..dialogs.quick_transfer import QuickFileTransferDialog


class FileOperationsManager(QObject):
    """Manages file transfer operations with simplified workflow."""
    
    # Signals
    log_message = Signal(str)
    tunnel_needed = Signal(str)  # config_name
    refresh_table = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_manager = None
        self.active_tunnels = None
        
    def set_managers(self, config_manager, active_tunnels):
        """Set the required managers."""
        self.config_manager = config_manager
        self.active_tunnels = active_tunnels
    
    def browse_files(self, config_name: str, config: TunnelConfig):
        """
        Smart file browsing that handles authentication automatically.
        
        Workflow:
        1. SSH Key auth -> Direct SFTP connection
        2. Password auth + tunnel running -> Direct SFTP connection  
        3. Password auth + no tunnel -> Show options menu
        """
        uses_ssh_key = config.ssh_key_path and os.path.exists(config.ssh_key_path)
        is_tunnel_running = config_name in self.active_tunnels and self.active_tunnels[config_name].is_running
        
        if uses_ssh_key:
            # Direct SFTP connection with SSH key
            self.log_message.emit(f"🗂️ Opening file browser with SSH key authentication...")
            self._open_sftp_browser(config)
            
        elif is_tunnel_running:
            # Tunnel is running, so password auth already worked
            self.log_message.emit(f"🗂️ Opening file browser (using established tunnel)...")
            self._open_sftp_browser(config)
            
        else:
            # Need to handle password authentication
            self._show_auth_options(config_name, config)
    
    def _show_auth_options(self, config_name: str, config: TunnelConfig):
        """Show authentication options for password-based connections."""
        menu = QMenu()
        
        # Option 1: Direct SFTP (will prompt for password in SFTP dialog)
        direct_action = menu.addAction("📁 Direct SFTP Connection")
        direct_action.setToolTip("Connect directly to SFTP (password prompt in dialog)")
        
        # Option 2: Quick transfer
        transfer_action = menu.addAction("📤 Quick File Transfer")
        transfer_action.setToolTip("Simple upload/download interface")
        
        # Option 3: Remote host via tunnel
        if config_name in self.active_tunnels and self.active_tunnels[config_name].is_running:
            remote_action = menu.addAction(f"🌐 Browse Remote Host ({config.remote_host})")
            remote_action.setToolTip(f"Access the remote host {config.remote_host} file system via tunnel")
        else:
            remote_action = None
        
        # Show menu near the cursor
        from PySide6.QtGui import QCursor
        action = menu.exec(QCursor.pos())
        
        if action == direct_action:
            self._open_sftp_browser(config)
        elif action == transfer_action:
            self._open_quick_transfer(config)
        elif remote_action and action == remote_action:
            self._open_remote_sftp_browser(config)
    
    def _open_sftp_browser(self, config: TunnelConfig):
        """Open the SFTP file browser."""
        try:
            password = None
            
            # Check if we need password authentication
            uses_ssh_key = config.ssh_key_path and os.path.exists(config.ssh_key_path)
            
            if not uses_ssh_key:
                # Need to prompt for password
                from ..dialogs.password_dialog import SSHPasswordDialog
                
                dialog = SSHPasswordDialog(config.ssh_host, config.ssh_user)
                if dialog.exec() == QDialog.Accepted:
                    credentials = dialog.get_credentials()
                    password = credentials['password']
                else:
                    self.log_message.emit("❌ Password authentication cancelled")
                    return
            
            browser = SFTPFileBrowser(config, password, parent=None)
            browser.exec()
        except Exception as e:
            QMessageBox.critical(
                None,
                "File Browser Error", 
                f"Failed to open file browser:\n{str(e)}"
            )
            self.log_message.emit(f"❌ File browser error: {str(e)}")
    
    def _open_quick_transfer(self, config: TunnelConfig):
        """Open the quick transfer dialog."""
        try:
            password = None
            
            # Check if we need password authentication
            uses_ssh_key = config.ssh_key_path and os.path.exists(config.ssh_key_path)
            
            if not uses_ssh_key:
                # Need to prompt for password
                from ..dialogs.password_dialog import SSHPasswordDialog
                
                dialog = SSHPasswordDialog(config.ssh_host, config.ssh_user)
                if dialog.exec() == QDialog.Accepted:
                    credentials = dialog.get_credentials()
                    password = credentials['password']
                else:
                    self.log_message.emit("❌ Password authentication cancelled")
                    return
            
            transfer_dialog = QuickFileTransferDialog(config, password, parent=None)
            transfer_dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Quick Transfer Error",
                f"Failed to open quick transfer:\n{str(e)}"
            )
            self.log_message.emit(f"❌ Quick transfer error: {str(e)}")
    
    def _open_remote_sftp_browser(self, config: TunnelConfig):
        """Open the SFTP file browser to access the remote host through a tunnel."""
        try:
            password = None
            
            # Check if we need password authentication
            uses_ssh_key = config.ssh_key_path and os.path.exists(config.ssh_key_path)
            
            if not uses_ssh_key:
                # Need to prompt for password
                from ..dialogs.password_dialog import SSHPasswordDialog
                
                dialog = SSHPasswordDialog(config.ssh_host, config.ssh_user)
                if dialog.exec() == QDialog.Accepted:
                    credentials = dialog.get_credentials()
                    password = credentials['password']
                else:
                    self.log_message.emit("❌ Password authentication cancelled")
                    return
            
            # Use the MultiHopSFTPBrowser to access the remote host
            browser = MultiHopSFTPBrowser(config, password, access_remote=True, parent=None)
            browser.exec()
        except Exception as e:
            QMessageBox.critical(
                None,
                "Remote File Browser Error", 
                f"Failed to open remote file browser:\n{str(e)}"
            )
            self.log_message.emit(f"❌ Remote file browser error: {str(e)}")
            
    def browse_remote_files(self, config_name: str, config: TunnelConfig):
        """
        Browse files on the remote host (destination of the tunnel).
        Only available when tunnel is running.
        """
        is_tunnel_running = config_name in self.active_tunnels and self.active_tunnels[config_name].is_running
        
        if is_tunnel_running:
            # Tunnel is running, try to access the remote host
            self.log_message.emit(f"🌐 Opening file browser for remote host {config.remote_host}...")
            self._open_remote_sftp_browser(config)
        else:
            # Tunnel not running, cannot access remote host
            self.log_message.emit(f"❌ Cannot access remote host - tunnel not running")
            QMessageBox.warning(
                None,
                "Tunnel Not Running",
                f"Cannot access the remote host {config.remote_host} because the tunnel is not running.\n\n"
                f"Please start the tunnel first and then try again."
            )
