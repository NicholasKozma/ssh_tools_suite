#!/usr/bin/env python3
"""
SSH Password Dialog
==================

A dialog for securely entering SSH passwords with option to save credentials.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon


class SSHPasswordDialog(QDialog):
    """Dialog for entering SSH password and optionally saving credentials."""
    
    def __init__(self, hostname, username, parent=None):
        super().__init__(parent)
        self.hostname = hostname
        self.username = username
        self.password = ""
        self.save_credentials = False
        
        self.setWindowTitle("SSH Authentication Required")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedSize(400, 350)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header_label = QLabel("🔐 SSH Authentication Required")
        header_font = QFont()
        header_font.setPointSize(12)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Connection info
        info_group = QGroupBox("Connection Details")
        info_layout = QVBoxLayout(info_group)
        
        host_label = QLabel(f"Server: {self.hostname}")
        user_label = QLabel(f"Username: {self.username}")
        
        info_layout.addWidget(host_label)
        info_layout.addWidget(user_label)
        layout.addWidget(info_group)
        
        # Password input
        password_group = QGroupBox("Authentication")
        password_layout = QVBoxLayout(password_group)
        
        password_layout.addWidget(QLabel("Password:"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setPlaceholderText("Enter your SSH password")
        self.password_edit.returnPressed.connect(self.accept)
        password_layout.addWidget(self.password_edit)
        
        # Save credentials option
        self.save_checkbox = QCheckBox("Remember password for this session")
        self.save_checkbox.setToolTip("Password will be stored in memory only during this session")
        password_layout.addWidget(self.save_checkbox)
        
        layout.addWidget(password_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        
        self.connect_button = QPushButton("Connect")
        self.connect_button.setDefault(True)
        self.connect_button.clicked.connect(self.accept)
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        button_layout.addWidget(self.connect_button)
        
        layout.addLayout(button_layout)
        
        # Focus on password field
        self.password_edit.setFocus()
        
    def accept(self):
        """Handle dialog acceptance."""
        self.password = self.password_edit.text()
        self.save_credentials = self.save_checkbox.isChecked()
        
        if not self.password:
            QMessageBox.warning(self, "Missing Password", "Please enter a password.")
            self.password_edit.setFocus()
            return
            
        super().accept()
        
    def get_credentials(self):
        """Get the entered credentials."""
        return {
            'password': self.password,
            'save_credentials': self.save_credentials
        }
