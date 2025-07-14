#!/usr/bin/env python3
"""
SSH Tunnel Manager - Toolbar Manager
"""

from PySide6.QtWidgets import QHBoxLayout, QPushButton, QFrame
from PySide6.QtCore import QObject, Signal


class ToolbarManager(QObject):
    """Manages the main toolbar with simplified buttons."""
    
    # Signals for button actions
    add_tunnel = Signal()
    edit_tunnel = Signal()
    delete_tunnel = Signal()
    start_tunnel = Signal()
    stop_tunnel = Signal()
    test_tunnel = Signal()
    browse_files = Signal()
    browse_remote_files = Signal()  # New signal for remote file browsing
    open_web_browser = Signal()
    launch_rtsp = Signal()
    launch_rdp = Signal()
    show_network_scanner = Signal()
    show_powershell_generator = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = {}
        
    def create_toolbar(self) -> QHBoxLayout:
        """Create the simplified toolbar with essential buttons."""
        toolbar_layout = QHBoxLayout()
        
        # Core tunnel management buttons
        self.buttons['add'] = QPushButton("➕ Add")
        self.buttons['edit'] = QPushButton("✏️ Edit")
        self.buttons['delete'] = QPushButton("🗑️ Delete")
        
        # Tunnel control buttons
        self.buttons['start'] = QPushButton("▶️ Start")
        self.buttons['stop'] = QPushButton("⏹️ Stop")
        self.buttons['test'] = QPushButton("🔍 Test")
        
        # Service access buttons (simplified)
        self.buttons['files'] = QPushButton("📁 Files")
        self.buttons['remote_files'] = QPushButton("🔒 Remote Files")
        self.buttons['web'] = QPushButton("🌐 Web")
        self.buttons['rtsp'] = QPushButton("📹 RTSP")
        self.buttons['rdp'] = QPushButton("🖥️ RDP")
        
        # Network tools
        self.buttons['network_scanner'] = QPushButton("🔍 Network Scanner")
        self.buttons['powershell_generator'] = QPushButton("📜 PowerShell")
        
        # Connect signals
        self.buttons['add'].clicked.connect(self.add_tunnel)
        self.buttons['edit'].clicked.connect(self.edit_tunnel)
        self.buttons['delete'].clicked.connect(self.delete_tunnel)
        self.buttons['start'].clicked.connect(self.start_tunnel)
        self.buttons['stop'].clicked.connect(self.stop_tunnel)
        self.buttons['test'].clicked.connect(self.test_tunnel)
        self.buttons['files'].clicked.connect(self.browse_files)
        self.buttons['remote_files'].clicked.connect(self.browse_remote_files)
        self.buttons['web'].clicked.connect(self.open_web_browser)
        self.buttons['rtsp'].clicked.connect(self.launch_rtsp)
        self.buttons['rdp'].clicked.connect(self.launch_rdp)
        self.buttons['network_scanner'].clicked.connect(self.show_network_scanner)
        self.buttons['powershell_generator'].clicked.connect(self.show_powershell_generator)
        
        # Set initial states
        self.set_initial_button_states()
        
        # Add to layout with separators
        toolbar_layout.addWidget(self.buttons['add'])
        toolbar_layout.addWidget(self.buttons['edit'])
        toolbar_layout.addWidget(self.buttons['delete'])
        toolbar_layout.addWidget(self._create_separator())
        
        toolbar_layout.addWidget(self.buttons['start'])
        toolbar_layout.addWidget(self.buttons['stop'])
        toolbar_layout.addWidget(self.buttons['test'])
        toolbar_layout.addWidget(self._create_separator())
        
        toolbar_layout.addWidget(self.buttons['files'])
        toolbar_layout.addWidget(self.buttons['remote_files'])
        toolbar_layout.addWidget(self.buttons['web'])
        toolbar_layout.addWidget(self.buttons['rtsp'])
        toolbar_layout.addWidget(self.buttons['rdp'])
        toolbar_layout.addWidget(self._create_separator())
        
        toolbar_layout.addWidget(self.buttons['network_scanner'])
        toolbar_layout.addWidget(self.buttons['powershell_generator'])
        
        toolbar_layout.addStretch()
        
        return toolbar_layout
    
    def _create_separator(self) -> QFrame:
        """Create a visual separator."""
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        return separator
    
    def set_initial_button_states(self):
        """Set initial button states."""
        # Tunnel management buttons
        self.buttons['edit'].setEnabled(False)
        self.buttons['delete'].setEnabled(False)
        
        # Control buttons
        self.buttons['start'].setEnabled(False)
        self.buttons['stop'].setEnabled(False)
        self.buttons['test'].setEnabled(False)
        
        # Service buttons
        self.buttons['files'].setEnabled(False)
        self.buttons['remote_files'].setEnabled(False)
        self.buttons['web'].setEnabled(False)
        self.buttons['rtsp'].setEnabled(False)
        self.buttons['rdp'].setEnabled(False)
    
    def update_button_states(self, selected: bool, is_running: bool = False, 
                           web_enabled: bool = False, rtsp_enabled: bool = False, 
                           rdp_enabled: bool = False):
        """Update button states based on selection and tunnel status."""
        # Tunnel management
        self.buttons['edit'].setEnabled(selected)
        self.buttons['delete'].setEnabled(selected)
        
        if selected:
            # Control buttons
            self.buttons['start'].setEnabled(not is_running)
            self.buttons['stop'].setEnabled(is_running)
            self.buttons['test'].setEnabled(True)  # Always allow testing
            
            # Service buttons
            self.buttons['files'].setEnabled(True)  # Always allow file browsing if tunnel selected
            self.buttons['remote_files'].setEnabled(is_running)  # Only allow remote file browsing if tunnel is running
            self.buttons['web'].setEnabled(web_enabled and is_running)
            self.buttons['rtsp'].setEnabled(rtsp_enabled and is_running)
            self.buttons['rdp'].setEnabled(rdp_enabled and is_running)
        else:
            # No selection - disable all
            self.buttons['start'].setEnabled(False)
            self.buttons['stop'].setEnabled(False)
            self.buttons['test'].setEnabled(False)
            self.buttons['files'].setEnabled(False)
            self.buttons['remote_files'].setEnabled(False)
            self.buttons['web'].setEnabled(False)
            self.buttons['rtsp'].setEnabled(False)
            self.buttons['rdp'].setEnabled(False)
