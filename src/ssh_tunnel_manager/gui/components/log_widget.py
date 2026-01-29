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
        log_layout.setContentsMargins(12, 20, 12, 12)
        log_layout.setSpacing(8)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setMinimumHeight(150)
        self.log_text.setFont(QFont("Consolas", LOG_FONT_SIZE))
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        # Log controls
        log_controls = QHBoxLayout()
        log_controls.setSpacing(8)
        
        clear_log_btn = QPushButton("🗑️ Clear Log")
        clear_log_btn.setMaximumWidth(150)
        clear_log_btn.setMinimumHeight(32)
        clear_log_btn.clicked.connect(self.clear_log)
        clear_log_btn.setToolTip("Clear all log messages")
        
        log_controls.addWidget(clear_log_btn)
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        return log_group
    
    def log(self, message: str):
        """Add a timestamped message to the log with color coding."""
        if self.log_text:
            timestamp = time.strftime("%H:%M:%S")
            
            # Determine message color based on content
            if any(word in message.lower() for word in ['error', 'failed', 'fail']):
                color = '#F44336'  # Red
                prefix = '❌'
            elif any(word in message.lower() for word in ['warning', 'warn']):
                color = '#FF9800'  # Orange
                prefix = '⚠️'
            elif any(word in message.lower() for word in ['success', 'started', 'connected', 'running']):
                color = '#4CAF50'  # Green
                prefix = '✅'
            elif any(word in message.lower() for word in ['stopped', 'disconnected']):
                color = '#9E9E9E'  # Gray
                prefix = '⏹️'
            else:
                color = '#E0E0E0'  # Light gray for normal messages
                prefix = 'ℹ️'
            
            formatted_message = f'<span style="color: #90CAF9;">[{timestamp}]</span> <span style="color: {color};">{prefix} {message}</span>'
            self.log_text.append(formatted_message)
    
    def clear_log(self):
        """Clear the log."""
        if self.log_text:
            self.log_text.clear()
