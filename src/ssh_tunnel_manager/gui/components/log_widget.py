#!/usr/bin/env python3
"""
SSH Tunnel Manager - Log Widget Component
"""

import time
from PySide6.QtWidgets import QTextEdit, QGroupBox, QVBoxLayout, QHBoxLayout, QPushButton
from PySide6.QtGui import QFont
from PySide6.QtCore import QObject

from ...core.constants import LOG_FONT_SIZE


class LogWidget(QObject):
    """Manages the log display widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.log_text = None
        
    def create_log_widget(self) -> QGroupBox:
        """Create the log widget group."""
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout(log_group)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setFont(QFont("Consolas", LOG_FONT_SIZE))
        log_layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("Clear Log")
        clear_log_btn.clicked.connect(self.clear_log)
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        return log_group
    
    def log(self, message: str):
        """Add a timestamped message to the log."""
        if self.log_text:
            timestamp = time.strftime("%H:%M:%S")
            self.log_text.append(f"[{timestamp}] {message}")
    
    def clear_log(self):
        """Clear the log."""
        if self.log_text:
            self.log_text.clear()
