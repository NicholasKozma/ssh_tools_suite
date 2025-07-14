#!/usr/bin/env python3
"""
SSH Tunnel Manager - Quick File Transfer Dialog
"""

import os
from typing import Optional, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QProgressBar, QTextEdit, QGroupBox, QMessageBox,
    QFileDialog, QComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from .sftp_browser import FileTransferWorker
from ...core.models import TunnelConfig


class QuickFileTransferDialog(QDialog):
    """Quick file transfer dialog for simple upload/download operations."""
    
    def __init__(self, tunnel_config: TunnelConfig, password: Optional[str] = None, parent=None):
        super().__init__(parent)
        self.tunnel_config = tunnel_config
        self.password = password
        self.transfer_worker = None
        
        self.setWindowTitle(f"Quick File Transfer - {tunnel_config.ssh_host}")
        self.setFixedSize(500, 400)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Connection info
        info_label = QLabel(f"Server: {self.tunnel_config.ssh_host}:{self.tunnel_config.ssh_port}")
        info_label.setStyleSheet("QLabel { font-weight: bold; color: #0066cc; }")
        layout.addWidget(info_label)
        
        # Upload section
        upload_group = QGroupBox("Upload Files")
        upload_layout = QVBoxLayout(upload_group)
        
        # Local file selection
        local_layout = QHBoxLayout()
        self.local_file_edit = QLineEdit()
        self.local_file_edit.setPlaceholderText("Select local file(s) to upload...")
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_local_files)
        
        local_layout.addWidget(QLabel("Local file:"))
        local_layout.addWidget(self.local_file_edit)
        local_layout.addWidget(browse_btn)
        upload_layout.addLayout(local_layout)
        
        # Remote destination
        remote_layout = QHBoxLayout()
        self.remote_path_edit = QLineEdit()
        self.remote_path_edit.setText("/tmp/")
        self.remote_path_edit.setPlaceholderText("Remote destination path...")
        
        remote_layout.addWidget(QLabel("Remote path:"))
        remote_layout.addWidget(self.remote_path_edit)
        upload_layout.addLayout(remote_layout)
        
        # Upload button
        self.upload_btn = QPushButton("📤 Upload")
        self.upload_btn.clicked.connect(self.start_upload)
        upload_layout.addWidget(self.upload_btn)
        
        layout.addWidget(upload_group)
        
        # Download section
        download_group = QGroupBox("Download Files")
        download_layout = QVBoxLayout(download_group)
        
        # Remote file path
        remote_file_layout = QHBoxLayout()
        self.remote_file_edit = QLineEdit()
        self.remote_file_edit.setPlaceholderText("Remote file path to download...")
        
        remote_file_layout.addWidget(QLabel("Remote file:"))
        remote_file_layout.addWidget(self.remote_file_edit)
        download_layout.addLayout(remote_file_layout)
        
        # Local destination
        local_dest_layout = QHBoxLayout()
        self.local_dest_edit = QLineEdit()
        self.local_dest_edit.setPlaceholderText("Local destination...")
        browse_dest_btn = QPushButton("Browse...")
        browse_dest_btn.clicked.connect(self.browse_local_destination)
        
        local_dest_layout.addWidget(QLabel("Local dest:"))
        local_dest_layout.addWidget(self.local_dest_edit)
        local_dest_layout.addWidget(browse_dest_btn)
        download_layout.addLayout(local_dest_layout)
        
        # Download button
        self.download_btn = QPushButton("📥 Download")
        self.download_btn.clicked.connect(self.start_download)
        download_layout.addWidget(self.download_btn)
        
        layout.addWidget(download_group)
        
        # Progress section
        progress_group = QGroupBox("Transfer Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        self.progress_label = QLabel("No active transfers")
        self.progress_bar = QProgressBar()
        
        self.cancel_btn = QPushButton("Cancel Transfer")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.clicked.connect(self.cancel_transfer)
        
        progress_layout.addWidget(self.progress_label)
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(progress_group)
        
        # Log section
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(100)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)
        
        # Button box
        button_layout = QHBoxLayout()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.log_text.clear)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        
        button_layout.addWidget(clear_log_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def browse_local_files(self):
        """Browse for local files to upload."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Upload",
            "",
            "All Files (*.*)"
        )
        
        if files:
            # For multiple files, just show the first one with count
            if len(files) == 1:
                self.local_file_edit.setText(files[0])
            else:
                self.local_file_edit.setText(f"{files[0]} (and {len(files)-1} more)")
            
            # Store all selected files
            self.selected_files = files
    
    def browse_local_destination(self):
        """Browse for local destination folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Destination Folder"
        )
        
        if folder:
            self.local_dest_edit.setText(folder)
    
    def start_upload(self):
        """Start uploading selected files."""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select files to upload.")
            return
        
        remote_path = self.remote_path_edit.text().strip()
        if not remote_path:
            QMessageBox.warning(self, "No Destination", "Please specify a remote destination path.")
            return
        
        # For simplicity, upload the first file
        # In a full implementation, you'd handle multiple files
        local_file = self.selected_files[0]
        filename = os.path.basename(local_file)
        
        # Ensure remote path ends with the filename
        if remote_path.endswith('/'):
            full_remote_path = remote_path + filename
        else:
            full_remote_path = remote_path + '/' + filename
        
        self.log(f"Starting upload: {filename}")
        self._start_transfer('upload', local_file, full_remote_path)
    
    def start_download(self):
        """Start downloading the specified file."""
        remote_file = self.remote_file_edit.text().strip()
        if not remote_file:
            QMessageBox.warning(self, "No Remote File", "Please specify a remote file path.")
            return
        
        local_dest = self.local_dest_edit.text().strip()
        if not local_dest:
            QMessageBox.warning(self, "No Destination", "Please specify a local destination.")
            return
        
        # If local_dest is a directory, append the filename
        filename = os.path.basename(remote_file)
        if os.path.isdir(local_dest):
            local_file = os.path.join(local_dest, filename)
        else:
            local_file = local_dest
        
        self.log(f"Starting download: {filename}")
        self._start_transfer('download', local_file, remote_file)
    
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
        self.upload_btn.setEnabled(False)
        self.download_btn.setEnabled(False)
        
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
        self.upload_btn.setEnabled(True)
        self.download_btn.setEnabled(True)
        
        self.log(message)
        
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
        cursor.movePosition(cursor.End)
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
        
        event.accept()
