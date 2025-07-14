#!/usr/bin/env python3
"""
SSH Tunnel Manager - SFTP File Browser Dialog
"""

import os
import stat
import threading
from pathlib import Path
from typing import Optional, List, Dict, Any

import paramiko
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTreeWidget, 
    QTreeWidgetItem, QSplitter, QLabel, QLineEdit, QProgressBar,
    QTextEdit, QGroupBox, QMessageBox, QFileDialog, QMenu, 
    QComboBox, QCheckBox, QSpinBox, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QAction, QIcon, QFont, QCursor

from ...core.models import TunnelConfig


class FileTransferWorker(QThread):
    """Worker thread for file transfer operations."""
    
    progress_updated = Signal(int, str)  # progress, status
    transfer_finished = Signal(bool, str)  # success, message
    
    def __init__(self, operation: str, ssh_config: Dict[str, Any], 
                 local_path: str, remote_path: str):
        super().__init__()
        self.operation = operation  # 'upload' or 'download'
        self.ssh_config = ssh_config
        self.local_path = local_path
        self.remote_path = remote_path
        self.cancelled = False
        
    def run(self):
        """Execute the file transfer."""
        try:
            # Create SSH client
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Connect
            ssh.connect(
                hostname=self.ssh_config['hostname'],
                port=self.ssh_config.get('port', 22),
                username=self.ssh_config['username'],
                password=self.ssh_config.get('password'),
                key_filename=self.ssh_config.get('key_filename'),
                timeout=30
            )
            
            # Create SFTP client
            sftp = ssh.open_sftp()
            
            if self.operation == 'upload':
                self._upload_file(sftp, self.local_path, self.remote_path)
            elif self.operation == 'download':
                self._download_file(sftp, self.remote_path, self.local_path)
            
            sftp.close()
            ssh.close()
            
            self.transfer_finished.emit(True, f"{self.operation.title()} completed successfully")
            
        except Exception as e:
            self.transfer_finished.emit(False, f"{self.operation.title()} failed: {str(e)}")
    
    def _upload_file(self, sftp, local_path: str, remote_path: str):
        """Upload a file with progress tracking."""
        file_size = os.path.getsize(local_path)
        transferred = 0
        
        def progress_callback(transferred_bytes, total_bytes):
            if self.cancelled:
                raise Exception("Transfer cancelled by user")
            progress = int((transferred_bytes / total_bytes) * 100)
            self.progress_updated.emit(progress, f"Uploading... {transferred_bytes}/{total_bytes} bytes")
        
        sftp.put(local_path, remote_path, callback=progress_callback)
    
    def _download_file(self, sftp, remote_path: str, local_path: str):
        """Download a file with progress tracking."""
        remote_stat = sftp.stat(remote_path)
        file_size = remote_stat.st_size
        
        def progress_callback(transferred_bytes, total_bytes):
            if self.cancelled:
                raise Exception("Transfer cancelled by user")
            progress = int((transferred_bytes / total_bytes) * 100)
            self.progress_updated.emit(progress, f"Downloading... {transferred_bytes}/{total_bytes} bytes")
        
        sftp.get(remote_path, local_path, callback=progress_callback)
    
    def cancel(self):
        """Cancel the transfer."""
        self.cancelled = True


class SFTPFileBrowser(QDialog):
    """SFTP File Browser Dialog for remote file management."""
    
    def __init__(self, tunnel_config: TunnelConfig, password: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.tunnel_config = tunnel_config
        self.password = password
        self.ssh_client = None
        self.sftp_client = None
        self.current_remote_path = "/"
        self.transfer_worker = None
        
        self.setWindowTitle(f"SFTP File Browser - {tunnel_config.ssh_host}")
        self.setGeometry(200, 200, 900, 600)
        self.setup_ui()
        self.connect_to_server()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Connection info
        info_layout = QHBoxLayout()
        info_label = QLabel(f"Connected to: {self.tunnel_config.ssh_host}:{self.tunnel_config.ssh_port}")
        info_label.setStyleSheet("QLabel { font-weight: bold; color: #0066cc; }")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        # Disconnect button
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_and_close)
        info_layout.addWidget(self.disconnect_btn)
        
        layout.addLayout(info_layout)
        
        # Main splitter
        main_splitter = QSplitter(Qt.Horizontal)
        
        # Left panel - Remote file browser
        remote_panel = self._create_remote_panel()
        main_splitter.addWidget(remote_panel)
        
        # Right panel - Transfer controls and log
        control_panel = self._create_control_panel()
        main_splitter.addWidget(control_panel)
        
        main_splitter.setStretchFactor(0, 2)
        main_splitter.setStretchFactor(1, 1)
        
        layout.addWidget(main_splitter)
        
        # Status bar
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
    
    def _create_remote_panel(self) -> QGroupBox:
        """Create the remote file browser panel."""
        group = QGroupBox("Remote Files")
        layout = QVBoxLayout(group)
        
        # Navigation
        nav_layout = QHBoxLayout()
        
        self.path_edit = QLineEdit()
        self.path_edit.setText(self.current_remote_path)
        self.path_edit.returnPressed.connect(self.navigate_to_path)
        
        nav_up_btn = QPushButton("↑ Up")
        nav_up_btn.clicked.connect(self.navigate_up)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_remote_files)
        
        nav_layout.addWidget(QLabel("Path:"))
        nav_layout.addWidget(self.path_edit)
        nav_layout.addWidget(nav_up_btn)
        nav_layout.addWidget(refresh_btn)
        
        layout.addLayout(nav_layout)
        
        # File tree
        self.remote_tree = QTreeWidget()
        self.remote_tree.setHeaderLabels(["Name", "Size", "Modified", "Permissions"])
        self.remote_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.remote_tree.customContextMenuRequested.connect(self.show_remote_context_menu)
        self.remote_tree.itemDoubleClicked.connect(self.on_remote_item_double_clicked)
        
        # Set column widths
        header = self.remote_tree.header()
        header.resizeSection(0, 200)  # Name
        header.resizeSection(1, 80)   # Size
        header.resizeSection(2, 120)  # Modified
        header.resizeSection(3, 100)  # Permissions
        
        layout.addWidget(self.remote_tree)
        
        return group
    
    def _create_control_panel(self) -> QGroupBox:
        """Create the transfer controls and log panel."""
        group = QGroupBox("Transfer Controls")
        layout = QVBoxLayout(group)
        
        # Upload section
        upload_group = QGroupBox("Upload Files")
        upload_layout = QVBoxLayout(upload_group)
        
        upload_btn = QPushButton("📁 Select Files to Upload")
        upload_btn.clicked.connect(self.select_files_to_upload)
        upload_layout.addWidget(upload_btn)
        
        upload_folder_btn = QPushButton("📂 Select Folder to Upload")
        upload_folder_btn.clicked.connect(self.select_folder_to_upload)
        upload_layout.addWidget(upload_folder_btn)
        
        layout.addWidget(upload_group)
        
        # Progress section
        progress_group = QGroupBox("Transfer Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel("No active transfers")
        
        self.cancel_btn = QPushButton("Cancel Transfer")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_transfer)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox("Transfer Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setFont(QFont("Consolas", 9))
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_text.clear)
        
        log_layout.addWidget(self.log_text)
        log_layout.addWidget(clear_log_btn)
        
        layout.addWidget(log_group)
        
        return group
    
    def connect_to_server(self):
        """Connect to the SSH server and setup SFTP."""
        try:
            self.log("Connecting to SSH server...")
            
            # Create SSH client
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Prepare connection parameters
            connect_params = {
                'hostname': self.tunnel_config.ssh_host,
                'port': self.tunnel_config.ssh_port,
                'username': self.tunnel_config.ssh_user,
                'timeout': 30
            }
            
            # Add authentication
            if self.password:
                connect_params['password'] = self.password
            elif self.tunnel_config.ssh_key_path and os.path.exists(self.tunnel_config.ssh_key_path):
                connect_params['key_filename'] = self.tunnel_config.ssh_key_path
            
            # Connect
            self.ssh_client.connect(**connect_params)
            
            # Create SFTP client
            self.sftp_client = self.ssh_client.open_sftp()
            
            self.log("Connected successfully!")
            self.status_label.setText("Connected")
            
            # Load initial directory
            self.refresh_remote_files()
            
        except Exception as e:
            self.log(f"Connection failed: {str(e)}")
            QMessageBox.critical(self, "Connection Error", f"Failed to connect to SSH server:\n{str(e)}")
            self.close()
    
    def disconnect_and_close(self):
        """Disconnect from server and close dialog."""
        self.disconnect()
        self.close()
    
    def disconnect(self):
        """Disconnect from the SSH server."""
        try:
            if self.transfer_worker and self.transfer_worker.isRunning():
                self.cancel_transfer()
                
            if self.sftp_client:
                self.sftp_client.close()
                self.sftp_client = None
                
            if self.ssh_client:
                self.ssh_client.close()
                self.ssh_client = None
                
            self.log("Disconnected from server")
            self.status_label.setText("Disconnected")
            
        except Exception as e:
            self.log(f"Error during disconnect: {str(e)}")
    
    def refresh_remote_files(self):
        """Refresh the remote file listing."""
        if not self.sftp_client:
            return
            
        try:
            self.log(f"Loading directory: {self.current_remote_path}")
            self.remote_tree.clear()
            
            # Add parent directory entry if not at root
            if self.current_remote_path != "/":
                parent_item = QTreeWidgetItem([".. (Parent Directory)", "", "", ""])
                parent_item.setData(0, Qt.UserRole, "..")
                self.remote_tree.addTopLevelItem(parent_item)
            
            # List directory contents
            items = self.sftp_client.listdir_attr(self.current_remote_path)
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (not stat.S_ISDIR(x.st_mode), x.filename.lower()))
            
            for item in items:
                self._add_remote_item(item)
                
            self.path_edit.setText(self.current_remote_path)
            self.log(f"Loaded {len(items)} items")
            
        except Exception as e:
            self.log(f"Error loading directory: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to load directory:\n{str(e)}")
    
    def _add_remote_item(self, item):
        """Add an item to the remote file tree."""
        # Format size
        if stat.S_ISDIR(item.st_mode):
            size_str = "<DIR>"
            icon = "📁"
        else:
            size_str = self._format_size(item.st_size)
            icon = "📄"
        
        # Format modification time
        import datetime
        mod_time = datetime.datetime.fromtimestamp(item.st_mtime).strftime("%Y-%m-%d %H:%M")
        
        # Format permissions
        perms = stat.filemode(item.st_mode)
        
        # Create tree item
        tree_item = QTreeWidgetItem([
            f"{icon} {item.filename}",
            size_str,
            mod_time,
            perms
        ])
        
        # Store item data
        tree_item.setData(0, Qt.UserRole, item.filename)
        tree_item.setData(1, Qt.UserRole, item)
        
        self.remote_tree.addTopLevelItem(tree_item)
    
    def _format_size(self, size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"
    
    def navigate_to_path(self):
        """Navigate to the path in the path edit."""
        new_path = self.path_edit.text().strip()
        if new_path:
            self.current_remote_path = new_path
            self.refresh_remote_files()
    
    def navigate_up(self):
        """Navigate to parent directory."""
        if self.current_remote_path != "/":
            parent = str(Path(self.current_remote_path).parent)
            if parent == ".":
                parent = "/"
            self.current_remote_path = parent
            self.refresh_remote_files()
    
    def on_remote_item_double_clicked(self, item, column):
        """Handle double-click on remote item."""
        filename = item.data(0, Qt.UserRole)
        
        if filename == "..":
            self.navigate_up()
            return
        
        item_data = item.data(1, Qt.UserRole)
        if item_data and stat.S_ISDIR(item_data.st_mode):
            # Navigate into directory
            new_path = os.path.join(self.current_remote_path, filename).replace("\\", "/")
            if not new_path.startswith("/"):
                new_path = "/" + new_path
            self.current_remote_path = new_path
            self.refresh_remote_files()
    
    def show_remote_context_menu(self, position):
        """Show context menu for remote files."""
        item = self.remote_tree.itemAt(position)
        if not item:
            return
        
        filename = item.data(0, Qt.UserRole)
        if filename == "..":
            return
        
        menu = QMenu(self)
        
        # Download action
        download_action = QAction("📥 Download", self)
        download_action.triggered.connect(lambda: self.download_file(filename))
        menu.addAction(download_action)
        
        # Delete action
        menu.addSeparator()
        delete_action = QAction("🗑️ Delete", self)
        delete_action.triggered.connect(lambda: self.delete_remote_file(filename))
        menu.addAction(delete_action)
        
        # View action for text files
        item_data = item.data(1, Qt.UserRole)
        if item_data and not stat.S_ISDIR(item_data.st_mode):
            if any(filename.lower().endswith(ext) for ext in ['.txt', '.log', '.conf', '.cfg', '.ini', '.py', '.js', '.html', '.css']):
                view_action = QAction("👀 View", self)
                view_action.triggered.connect(lambda: self.view_remote_file(filename))
                menu.addAction(view_action)
        
        menu.exec(self.remote_tree.mapToGlobal(position))
    
    def select_files_to_upload(self):
        """Select local files to upload."""
        files, _ = QFileDialog.getOpenFileNames(
            self, 
            "Select Files to Upload",
            "",
            "All Files (*.*)"
        )
        
        if files:
            for file_path in files:
                self.upload_file(file_path)
    
    def select_folder_to_upload(self):
        """Select a local folder to upload."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Folder to Upload"
        )
        
        if folder:
            self.upload_folder(folder)
    
    def upload_file(self, local_path: str):
        """Upload a single file."""
        if not self.sftp_client:
            return
        
        filename = os.path.basename(local_path)
        remote_path = os.path.join(self.current_remote_path, filename).replace("\\", "/")
        
        self.log(f"Starting upload: {filename}")
        self._start_transfer('upload', local_path, remote_path)
    
    def upload_folder(self, local_folder: str):
        """Upload a folder recursively."""
        # This is a simplified version - in a full implementation,
        # you'd want to handle this recursively
        QMessageBox.information(
            self, 
            "Upload Folder", 
            "Folder upload is not yet implemented.\nPlease select individual files for now."
        )
    
    def download_file(self, filename: str):
        """Download a file from the remote server."""
        remote_path = os.path.join(self.current_remote_path, filename).replace("\\", "/")
        
        # Choose local save location
        local_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File As",
            filename,
            "All Files (*.*)"
        )
        
        if local_path:
            self.log(f"Starting download: {filename}")
            self._start_transfer('download', local_path, remote_path)
    
    def delete_remote_file(self, filename: str):
        """Delete a file on the remote server."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{filename}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                remote_path = os.path.join(self.current_remote_path, filename).replace("\\", "/")
                
                # Check if it's a directory or file
                stat_info = self.sftp_client.stat(remote_path)
                if stat.S_ISDIR(stat_info.st_mode):
                    self.sftp_client.rmdir(remote_path)
                else:
                    self.sftp_client.remove(remote_path)
                
                self.log(f"Deleted: {filename}")
                self.refresh_remote_files()
                
            except Exception as e:
                self.log(f"Failed to delete {filename}: {str(e)}")
                QMessageBox.warning(self, "Delete Error", f"Failed to delete file:\n{str(e)}")
    
    def view_remote_file(self, filename: str):
        """View the contents of a remote text file."""
        try:
            remote_path = os.path.join(self.current_remote_path, filename).replace("\\", "/")
            
            # Read file content (limit to 1MB for safety)
            with self.sftp_client.file(remote_path, 'r') as f:
                content = f.read(1024 * 1024)  # 1MB limit
            
            # Show in a simple dialog
            from PySide6.QtWidgets import QTextBrowser
            
            dialog = QDialog(self)
            dialog.setWindowTitle(f"View File: {filename}")
            dialog.setGeometry(300, 300, 600, 400)
            
            layout = QVBoxLayout(dialog)
            
            text_browser = QTextBrowser()
            text_browser.setPlainText(content)
            text_browser.setFont(QFont("Consolas", 10))
            
            layout.addWidget(text_browser)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.exec()
            
        except Exception as e:
            self.log(f"Failed to view {filename}: {str(e)}")
            QMessageBox.warning(self, "View Error", f"Failed to view file:\n{str(e)}")
    
    def _start_transfer(self, operation: str, local_path: str, remote_path: str):
        """Start a file transfer operation."""
        if self.transfer_worker and self.transfer_worker.isRunning():
            QMessageBox.warning(self, "Transfer in Progress", "Another transfer is already in progress.")
            return
        
        # Prepare SSH config for worker
        ssh_config = {
            'hostname': self.tunnel_config.ssh_host,
            'port': self.tunnel_config.ssh_port,
            'username': self.tunnel_config.ssh_user,
        }
        
        if self.password:
            ssh_config['password'] = self.password
        elif self.tunnel_config.ssh_key_path:
            ssh_config['key_filename'] = self.tunnel_config.ssh_key_path
        
        # Create and start worker
        self.transfer_worker = FileTransferWorker(operation, ssh_config, local_path, remote_path)
        self.transfer_worker.progress_updated.connect(self.on_transfer_progress)
        self.transfer_worker.transfer_finished.connect(self.on_transfer_finished)
        
        self.progress_bar.setValue(0)
        self.cancel_btn.setEnabled(True)
        self.transfer_worker.start()
    
    def on_transfer_progress(self, progress: int, status: str):
        """Handle transfer progress updates."""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(status)
    
    def on_transfer_finished(self, success: bool, message: str):
        """Handle transfer completion."""
        self.progress_bar.setValue(100 if success else 0)
        self.progress_label.setText("Transfer completed" if success else "Transfer failed")
        self.cancel_btn.setEnabled(False)
        
        self.log(message)
        
        if success:
            # Refresh the remote file list to show changes
            self.refresh_remote_files()
        
        # Show completion message
        if success:
            QMessageBox.information(self, "Transfer Complete", message)
        else:
            QMessageBox.warning(self, "Transfer Failed", message)
    
    def cancel_transfer(self):
        """Cancel the current transfer."""
        if self.transfer_worker:
            self.transfer_worker.cancel()
            self.log("Transfer cancelled by user")
            self.progress_label.setText("Cancelling...")
    
    def log(self, message: str):
        """Add a message to the log."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.transfer_worker and self.transfer_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Transfer in Progress",
                "A file transfer is in progress. Do you want to cancel it and close?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            else:
                self.cancel_transfer()
        
        self.disconnect()
        event.accept()
    
    @staticmethod
    def check_ssh_port(host, port=22, timeout=5):
        """
        Check if SSH port is accessible on a host directly (without jump host).
        Returns (is_accessible, ssh_banner, error_message)
        """
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result == 0:
                try:
                    sock.settimeout(2)
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    sock.close()
                    if banner and "SSH" in banner:
                        return True, banner, None
                    else:
                        return True, None, f"Port {port} is open but no SSH banner detected"
                except socket.timeout:
                    sock.close()
                    return True, None, f"Port {port} is open but banner read timed out"
                except Exception as e:
                    sock.close()
                    return True, None, f"Port {port} is open but banner read failed: {str(e)}"
            else:
                sock.close()
                return False, None, f"Connection refused to {host}:{port}"
        except socket.timeout:
            return False, None, f"Connection timeout to {host}:{port}"
        except socket.gaierror as e:
            return False, None, f"DNS resolution failed for {host}: {str(e)}"
        except Exception as e:
            return False, None, f"Connection failed to {host}:{port}: {str(e)}"
