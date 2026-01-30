#!/usr/bin/env python3
"""
Professional Toolbar Component
Clean, enterprise-grade toolbar with grouped controls
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..styles.professional_theme import COLORS


class ProfessionalToolbar(QWidget):
    """Professional toolbar with grouped action buttons."""
    
    # Signals
    add_tunnel = Signal()
    edit_tunnel = Signal()
    delete_tunnel = Signal()
    start_tunnel = Signal()
    stop_tunnel = Signal()
    test_tunnel = Signal()
    browse_files = Signal()
    browse_remote_files = Signal()
    open_web_browser = Signal()
    launch_rtsp = Signal()
    launch_rdp = Signal()
    show_network_scanner = Signal()
    show_powershell_generator = Signal()
    show_ssh_key_manager = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup toolbar UI."""
        container = QFrame()
        container.setObjectName("toolbar")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        toolbar_layout = QHBoxLayout(container)
        toolbar_layout.setSpacing(12)
        toolbar_layout.setContentsMargins(12, 10, 12, 10)
        
        # App title
        title = QLabel("SSH Tunnel Manager")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        toolbar_layout.addWidget(title)
        
        toolbar_layout.addSpacing(16)
        
        # Tunnel management group
        toolbar_layout.addWidget(self._create_separator())
        toolbar_layout.addWidget(self._create_group_label("Tunnels"))
        
        self.buttons['add'] = self._create_button("New Tunnel", "primary")
        self.buttons['add'].clicked.connect(self.add_tunnel.emit)
        toolbar_layout.addWidget(self.buttons['add'])
        
        # Tools group - simplified, actions moved to cards
        toolbar_layout.addWidget(self._create_separator())
        toolbar_layout.addWidget(self._create_group_label("Tools"))
        
        self.buttons['scan'] = self._create_button("Network Scanner", "default")
        self.buttons['scan'].clicked.connect(self.show_network_scanner.emit)
        toolbar_layout.addWidget(self.buttons['scan'])
        
        self.buttons['ssh_key'] = self._create_button("SSH Keys", "default")
        self.buttons['ssh_key'].clicked.connect(self.show_ssh_key_manager.emit)
        toolbar_layout.addWidget(self.buttons['ssh_key'])
        
        toolbar_layout.addStretch()
    
    def _create_button(self, text: str, style: str) -> QPushButton:
        """Create a toolbar button."""
        btn = QPushButton(text)
        btn.setObjectName(style)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(90)
        btn.setFont(QFont("Segoe UI", 12, QFont.DemiBold))
        return btn
    
    def _create_separator(self) -> QFrame:
        """Create a vertical separator."""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.VLine)
        separator.setMaximumWidth(1)
        separator.setMinimumHeight(24)
        return separator
    
    def _create_group_label(self, text: str) -> QLabel:
        """Create a group label."""
        label = QLabel(text.upper())
        label.setFont(QFont("Segoe UI", 9, QFont.Bold))
        label.setStyleSheet(f"color: {COLORS['text_tertiary']}; letter-spacing: 0.5px;")
        return label
    
    def update_button_states(self, has_selection: bool, is_active: bool):
        """Update button states based on selection (most actions now on cards)."""
        pass  # Actions moved to cards
