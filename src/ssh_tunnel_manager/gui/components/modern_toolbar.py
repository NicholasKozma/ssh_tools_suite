#!/usr/bin/env python3
"""
Modern Toolbar Component
Clean, icon-focused toolbar with grouped actions
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QFrame, QLabel
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..styles.modern_theme import ICONS, COLORS


class ModernToolbar(QWidget):
    """Modern toolbar with grouped action buttons."""
    
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
        """Setup modern toolbar UI."""
        # Main container with card styling
        container = QFrame()
        container.setObjectName("toolbar")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)
        
        toolbar_layout = QHBoxLayout(container)
        toolbar_layout.setSpacing(16)
        toolbar_layout.setContentsMargins(16, 12, 16, 12)
        
        # App title/logo
        title_layout = QHBoxLayout()
        title_layout.setSpacing(8)
        
        logo = QLabel("🔐")
        logo.setFont(QFont("Segoe UI Emoji", 20))
        title_layout.addWidget(logo)
        
        title = QLabel("SSH Tunnel Manager")
        title.setFont(QFont("Inter", 14, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_accent']};")
        title_layout.addWidget(title)
        
        toolbar_layout.addLayout(title_layout)
        toolbar_layout.addSpacing(20)
        
        # Tunnel Management Group
        toolbar_layout.addWidget(self._create_separator())
        toolbar_layout.addWidget(self._create_group_label("Tunnel"))
        
        self.buttons['add'] = self._create_button("➕", "Add Tunnel", "primary")
        self.buttons['add'].clicked.connect(self.add_tunnel.emit)
        toolbar_layout.addWidget(self.buttons['add'])
        
        self.buttons['start'] = self._create_button("▶️", "Start", "success")
        self.buttons['start'].clicked.connect(self.start_tunnel.emit)
        self.buttons['start'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['start'])
        
        self.buttons['stop'] = self._create_button("⏹️", "Stop", "danger")
        self.buttons['stop'].clicked.connect(self.stop_tunnel.emit)
        self.buttons['stop'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['stop'])
        
        self.buttons['edit'] = self._create_button("✏️", "Edit", "default")
        self.buttons['edit'].clicked.connect(self.edit_tunnel.emit)
        self.buttons['edit'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['edit'])
        
        self.buttons['delete'] = self._create_button("🗑️", "Delete", "default")
        self.buttons['delete'].clicked.connect(self.delete_tunnel.emit)
        self.buttons['delete'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['delete'])
        
        # Connection Tools Group
        toolbar_layout.addWidget(self._create_separator())
        toolbar_layout.addWidget(self._create_group_label("Tools"))
        
        self.buttons['test'] = self._create_button("🔌", "Test", "default")
        self.buttons['test'].clicked.connect(self.test_tunnel.emit)
        self.buttons['test'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['test'])
        
        self.buttons['files'] = self._create_button("📁", "Files", "default")
        self.buttons['files'].clicked.connect(self.browse_files.emit)
        self.buttons['files'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['files'])
        
        self.buttons['web'] = self._create_button("🌐", "Web", "default")
        self.buttons['web'].clicked.connect(self.open_web_browser.emit)
        self.buttons['web'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['web'])
        
        # Advanced Tools Group
        toolbar_layout.addWidget(self._create_separator())
        toolbar_layout.addWidget(self._create_group_label("Advanced"))
        
        self.buttons['rtsp'] = self._create_button("📹", "RTSP", "default")
        self.buttons['rtsp'].clicked.connect(self.launch_rtsp.emit)
        self.buttons['rtsp'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['rtsp'])
        
        self.buttons['rdp'] = self._create_button("🖥️", "RDP", "default")
        self.buttons['rdp'].clicked.connect(self.launch_rdp.emit)
        self.buttons['rdp'].setEnabled(False)
        toolbar_layout.addWidget(self.buttons['rdp'])
        
        self.buttons['scan'] = self._create_button("🔍", "Scan", "default")
        self.buttons['scan'].clicked.connect(self.show_network_scanner.emit)
        toolbar_layout.addWidget(self.buttons['scan'])
        
        self.buttons['powershell'] = self._create_button("⚡", "PowerShell", "default")
        self.buttons['powershell'].clicked.connect(self.show_powershell_generator.emit)
        toolbar_layout.addWidget(self.buttons['powershell'])
        
        self.buttons['ssh_key'] = self._create_button("🔑", "SSH Key", "default")
        self.buttons['ssh_key'].clicked.connect(self.show_ssh_key_manager.emit)
        toolbar_layout.addWidget(self.buttons['ssh_key'])
        
        toolbar_layout.addStretch()
    
    def _create_button(self, icon: str, text: str, style: str) -> QPushButton:
        """Create a modern toolbar button."""
        btn = QPushButton(f"{icon} {text}")
        btn.setObjectName(style)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumWidth(90)
        btn.setFont(QFont("Inter", 9, QFont.DemiBold))
        return btn
    
    def _create_separator(self) -> QFrame:
        """Create a vertical separator."""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.VLine)
        separator.setMaximumWidth(2)
        separator.setMinimumHeight(30)
        return separator
    
    def _create_group_label(self, text: str) -> QLabel:
        """Create a group label."""
        label = QLabel(text.upper())
        label.setFont(QFont("Inter", 8, QFont.Bold))
        label.setStyleSheet(f"color: {COLORS['text_tertiary']}; letter-spacing: 1px;")
        return label
    
    def update_button_states(self, has_selection: bool, is_active: bool):
        """Update button enabled states based on selection."""
        # Buttons that need selection
        self.buttons['edit'].setEnabled(has_selection and not is_active)
        self.buttons['delete'].setEnabled(has_selection and not is_active)
        self.buttons['start'].setEnabled(has_selection and not is_active)
        self.buttons['test'].setEnabled(has_selection)
        
        # Buttons that need active tunnel
        self.buttons['stop'].setEnabled(has_selection and is_active)
        self.buttons['files'].setEnabled(has_selection and is_active)
        self.buttons['web'].setEnabled(has_selection and is_active)
        self.buttons['rtsp'].setEnabled(has_selection and is_active)
        self.buttons['rdp'].setEnabled(has_selection and is_active)
