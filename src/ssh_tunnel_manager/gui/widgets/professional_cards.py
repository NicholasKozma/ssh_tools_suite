#!/usr/bin/env python3
"""
Professional Tunnel Cards Widget
Clean, enterprise-grade card-based display
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..styles.professional_theme import COLORS, get_status_style


class ProfessionalTunnelCard(QFrame):
    """A professional card widget for displaying tunnel information."""
    
    # Signals
    start_clicked = Signal(str)
    stop_clicked = Signal(str)
    edit_clicked = Signal(str)
    delete_clicked = Signal(str)
    files_clicked = Signal(str)
    web_clicked = Signal(str)
    rtsp_clicked = Signal(str)
    rdp_clicked = Signal(str)
    test_clicked = Signal(str)
    
    def __init__(self, config_name: str, config, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.config_name = config_name
        self.config = config
        self.is_active = is_active
        
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(220)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 14, 20, 10)
        
        # Header row
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Name
        name_label = QLabel(self.config_name)
        name_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        header_layout.addWidget(name_label)
        
        header_layout.addStretch()
        
        # Status badge
        status_text = "ACTIVE" if self.is_active else "STOPPED"
        status_badge = QLabel(status_text)
        status_style = get_status_style('active' if self.is_active else 'inactive')
        status_badge.setStyleSheet(status_style)
        header_layout.addWidget(status_badge)
        
        layout.addLayout(header_layout)
        
        # Connection details
        details_layout = QHBoxLayout()
        details_layout.setSpacing(24)
        
        tunnel_type = getattr(self.config, 'tunnel_type', 'local')
        local_port = getattr(self.config, 'local_port', 'N/A')
        remote_host = getattr(self.config, 'remote_host', 'N/A')
        remote_port = getattr(self.config, 'remote_port', 'N/A')
        ssh_host = getattr(self.config, 'ssh_host', 'N/A')
        
        details = [
            ("Type", tunnel_type.upper()),
            ("Local", str(local_port)),
            ("Remote", f"{remote_host}:{remote_port}"),
            ("SSH Host", ssh_host),
        ]
        
        for label_text, value in details:
            detail_container = QVBoxLayout()
            detail_container.setSpacing(2)
            
            label = QLabel(label_text)
            label.setObjectName("tertiary")
            label.setFont(QFont("Segoe UI", 10))
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 11, QFont.DemiBold))
            value_label.setStyleSheet(f"color: {COLORS['accent_secondary']};")
            value_label.setWordWrap(True)
            value_label.setMinimumWidth(120)
            value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            
            detail_container.addWidget(label)
            detail_container.addWidget(value_label)
            
            details_layout.addLayout(detail_container)
        
        details_layout.addStretch()
        layout.addLayout(details_layout)
        
        # Description
        description = getattr(self.config, 'description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("muted")
            layout.addWidget(desc_label)
        
        # Context-aware actions based on tunnel state and type
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        if self.is_active:
            # Active tunnel - show operational actions
            stop_btn = self._create_button("Stop", "danger")
            stop_btn.clicked.connect(lambda: self.stop_clicked.emit(self.config_name))
            actions_layout.addWidget(stop_btn)
            
            # Add context-aware service buttons
            if tunnel_type == 'local':
                # Check if it's a web service
                if remote_port in [80, 443, 8080, 8443, 8000, 3000, 5000, 9000]:
                    web_btn = self._create_button("Browser", "primary")
                    web_btn.clicked.connect(lambda: self.web_clicked.emit(self.config_name))
                    actions_layout.addWidget(web_btn)
                
                # Check if it's RTSP
                elif remote_port in [554, 8554]:
                    rtsp_btn = self._create_button("RTSP", "primary")
                    rtsp_btn.clicked.connect(lambda: self.rtsp_clicked.emit(self.config_name))
                    actions_layout.addWidget(rtsp_btn)
                
                # Check if it's RDP
                elif remote_port == 3389:
                    rdp_btn = self._create_button("RDP", "primary")
                    rdp_btn.clicked.connect(lambda: self.rdp_clicked.emit(self.config_name))
                    actions_layout.addWidget(rdp_btn)
            
            # Always show browse files for active tunnels
            files_btn = self._create_button("Files", "default")
            files_btn.clicked.connect(lambda: self.files_clicked.emit(self.config_name))
            actions_layout.addWidget(files_btn)
            
            # Test connection
            test_btn = self._create_button("Test", "default")
            test_btn.clicked.connect(lambda: self.test_clicked.emit(self.config_name))
            actions_layout.addWidget(test_btn)
        else:
            # Inactive tunnel - show management actions
            start_btn = self._create_button("Start", "success")
            start_btn.clicked.connect(lambda: self.start_clicked.emit(self.config_name))
            actions_layout.addWidget(start_btn)
            
            edit_btn = self._create_button("Edit", "default")
            edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.config_name))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = self._create_button("Delete", "danger")
            delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.config_name))
            actions_layout.addWidget(delete_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
    
    def _create_button(self, text: str, style: str) -> QPushButton:
        """Create an action button."""
        btn = QPushButton(text)
        btn.setObjectName(style)
        btn.setMinimumWidth(80)
        btn.setMaximumWidth(100)
        btn.setMaximumHeight(32)
        btn.setCursor(Qt.PointingHandCursor)
        return btn


class ProfessionalTunnelCardsWidget(QWidget):
    """Container for professional tunnel cards."""
    
    # Signals
    start_tunnel = Signal(str)
    stop_tunnel = Signal(str)
    edit_tunnel = Signal(str)
    delete_tunnel = Signal(str)
    files_tunnel = Signal(str)
    web_tunnel = Signal(str)
    rtsp_tunnel = Signal(str)
    rdp_tunnel = Signal(str)
    test_tunnel = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the container UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.NoFrame)
        
        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(12)
        self.cards_layout.setContentsMargins(16, 16, 16, 16)
        self.cards_layout.addStretch()
        
        scroll.setWidget(self.cards_container)
        layout.addWidget(scroll)
    
    def update_tunnels(self, tunnels_dict: dict, active_tunnels: dict):
        """Update the cards display."""
        # Clear existing cards
        while self.cards_layout.count() > 1:
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Create cards
        for config_name, config in tunnels_dict.items():
            # Check if tunnel is actually running, not just in the dict
            is_active = (config_name in active_tunnels and 
                        active_tunnels[config_name].is_running)
            card = ProfessionalTunnelCard(config_name, config, is_active)
            
            # Connect signals
            card.start_clicked.connect(self.start_tunnel.emit)
            card.stop_clicked.connect(self.stop_tunnel.emit)
            card.edit_clicked.connect(self.edit_tunnel.emit)
            card.delete_clicked.connect(self.delete_tunnel.emit)
            card.files_clicked.connect(self.files_tunnel.emit)
            card.web_clicked.connect(self.web_tunnel.emit)
            card.rtsp_clicked.connect(self.rtsp_tunnel.emit)
            card.rdp_clicked.connect(self.rdp_tunnel.emit)
            card.test_clicked.connect(self.test_tunnel.emit)
            
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # Show empty state if no tunnels
        if not tunnels_dict:
            empty_label = QLabel("No tunnels configured\nClick 'New Tunnel' to get started")
            empty_label.setObjectName("tertiary")
            empty_label.setAlignment(Qt.AlignCenter)
            empty_label.setFont(QFont("Segoe UI", 12))
            self.cards_layout.insertWidget(0, empty_label)
