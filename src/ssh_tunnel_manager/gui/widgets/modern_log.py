#!/usr/bin/env python3
"""
Modern Log Widget
Beautiful, colored log output with filtering
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QLabel, QFrame, QPushButton, QLineEdit
)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QFont, QTextCursor, QTextCharFormat, QColor

from ..styles.modern_theme import COLORS, ICONS


class ModernLogWidget(QWidget):
    """Modern log widget with colored output and search."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup log widget UI."""
        # Main container with card styling
        container = QFrame()
        container.setObjectName("card")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        layout = QVBoxLayout(container)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel(f"{ICONS['info']} Activity Log")
        title.setFont(QFont("Inter", 12, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_accent']};")
        header_layout.addWidget(title)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search logs...")
        self.search_box.setMaximumWidth(200)
        self.search_box.textChanged.connect(self._on_search)
        header_layout.addWidget(self.search_box)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear")
        clear_btn.setObjectName("default")
        clear_btn.setMaximumWidth(90)
        clear_btn.clicked.connect(self.clear_logs)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMinimumHeight(150)
        layout.addWidget(self.log_text)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.log_count_label = QLabel("0 entries")
        self.log_count_label.setFont(QFont("Inter", 8))
        self.log_count_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        status_layout.addWidget(self.log_count_label)
        status_layout.addStretch()
        
        layout.addLayout(status_layout)
        
        self.log_count = 0
    
    def add_log(self, message: str, level: str = "info"):
        """Add a log message with color coding."""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        
        # Determine color and icon based on level
        colors_map = {
            'info': (COLORS['accent_blue'], ICONS['info']),
            'success': (COLORS['accent_green'], ICONS['success']),
            'warning': (COLORS['accent_yellow'], ICONS['warning']),
            'error': (COLORS['accent_red'], ICONS['error']),
        }
        
        color, icon = colors_map.get(level, (COLORS['text_primary'], ICONS['info']))
        
        # Format the message
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Timestamp
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(COLORS['text_tertiary']))
        cursor.insertText(f"[{timestamp}] ", fmt)
        
        # Icon
        fmt.setForeground(QColor(color))
        cursor.insertText(f"{icon} ", fmt)
        
        # Message
        fmt.setForeground(QColor(COLORS['text_primary']))
        cursor.insertText(f"{message}\n", fmt)
        
        # Auto-scroll
        self.log_text.setTextCursor(cursor)
        self.log_text.ensureCursorVisible()
        
        # Update count
        self.log_count += 1
        self.log_count_label.setText(f"{self.log_count} entries")
    
    def clear_logs(self):
        """Clear all logs."""
        self.log_text.clear()
        self.log_count = 0
        self.log_count_label.setText("0 entries")
    
    def _on_search(self, text: str):
        """Handle search text change."""
        if not text:
            # Clear highlighting
            cursor = self.log_text.textCursor()
            cursor.select(QTextCursor.Document)
            fmt = QTextCharFormat()
            cursor.setCharFormat(fmt)
            return
        
        # Simple search highlighting
        # Note: For production, implement proper search highlighting
        pass


def log_level_from_message(message: str) -> str:
    """Determine log level from message content."""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['error', 'failed', 'failure', 'exception']):
        return 'error'
    elif any(word in message_lower for word in ['warning', 'warn']):
        return 'warning'
    elif any(word in message_lower for word in ['success', 'started', 'connected', 'complete']):
        return 'success'
    else:
        return 'info'
