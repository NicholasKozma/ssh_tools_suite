#!/usr/bin/env python3
"""
Modern Card Widget for SSH Tunnels
Displays tunnels in a beautiful card-based layout instead of table rows
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont

from ..styles.modern_theme import COLORS, ICONS, get_status_badge_style


class TunnelCard(QFrame):
    """A modern card widget representing a single tunnel."""
    
    # Signals
    clicked = Signal(str)  # config_name
    start_clicked = Signal(str)
    stop_clicked = Signal(str)
    edit_clicked = Signal(str)
    delete_clicked = Signal(str)
    files_clicked = Signal(str)
    
    def __init__(self, config_name: str, config: dict, is_active: bool = False, parent=None):
        super().__init__(parent)
        self.config_name = config_name
        self.config = config
        self.is_active = is_active
        
        self.setObjectName("card")
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setMinimumHeight(140)
        
        self._setup_ui()
        self._setup_animation()
    
    def _setup_ui(self):
        """Setup the card UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Header row (name + status)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        # Tunnel icon and name
        name_container = QHBoxLayout()
        name_container.setSpacing(10)
        
        icon_label = QLabel(ICONS['tunnel'])
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        name_container.addWidget(icon_label)
        
        name_label = QLabel(self.config_name)
        name_label.setFont(QFont("Inter", 14, QFont.Bold))
        name_label.setStyleSheet(f"color: {COLORS['text_primary']};")
        name_container.addWidget(name_label)
        name_container.addStretch()
        
        header_layout.addLayout(name_container)
        
        # Status badge
        status_text = "🟢 Running" if self.is_active else "🔴 Stopped"
        status_badge = QLabel(status_text)
        status_style = get_status_badge_style('running' if self.is_active else 'stopped')
        status_badge.setStyleSheet(status_style)
        header_layout.addWidget(status_badge)
        
        layout.addLayout(header_layout)
        
        # Info row
        info_layout = QHBoxLayout()
        info_layout.setSpacing(20)
        
        # Connection info - access TunnelConfig attributes directly
        tunnel_type = getattr(self.config, 'tunnel_type', 'local')
        local_port = getattr(self.config, 'local_port', 'N/A')
        remote_host = getattr(self.config, 'remote_host', 'N/A')
        remote_port = getattr(self.config, 'remote_port', 'N/A')
        ssh_host = getattr(self.config, 'ssh_host', 'N/A')
        
        info_items = [
            (f"📍 Type: {tunnel_type.upper()}", f"color: {COLORS['text_secondary']};"),
            (f"🔌 Local: {local_port}", f"color: {COLORS['accent_blue']};"),
            (f"🌐 Remote: {remote_host}:{remote_port}", f"color: {COLORS['accent_purple']};"),
            (f"🖥️ SSH: {ssh_host}", f"color: {COLORS['accent_green']};"),
        ]
        
        for text, style in info_items:
            label = QLabel(text)
            label.setFont(QFont("Inter", 9))
            label.setStyleSheet(f"{style} font-weight: 500;")
            info_layout.addWidget(label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        # Description
        description = getattr(self.config, 'description', '')
        if description:
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Inter", 9))
            desc_label.setStyleSheet(f"color: {COLORS['text_tertiary']}; font-style: italic;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)
        
        # Action buttons row
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(8)
        
        if self.is_active:
            stop_btn = self._create_action_button("⏹️ Stop", "danger")
            stop_btn.clicked.connect(lambda: self.stop_clicked.emit(self.config_name))
            actions_layout.addWidget(stop_btn)
            
            files_btn = self._create_action_button("📁 Files", "default")
            files_btn.clicked.connect(lambda: self.files_clicked.emit(self.config_name))
            actions_layout.addWidget(files_btn)
        else:
            start_btn = self._create_action_button("▶️ Start", "success")
            start_btn.clicked.connect(lambda: self.start_clicked.emit(self.config_name))
            actions_layout.addWidget(start_btn)
            
            edit_btn = self._create_action_button("✏️ Edit", "default")
            edit_btn.clicked.connect(lambda: self.edit_clicked.emit(self.config_name))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = self._create_action_button("🗑️ Delete", "danger")
            delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.config_name))
            actions_layout.addWidget(delete_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
    
    def _create_action_button(self, text: str, style: str) -> QPushButton:
        """Create a styled action button."""
        btn = QPushButton(text)
        btn.setObjectName(style)
        btn.setMinimumWidth(100)
        btn.setMaximumWidth(120)
        btn.setCursor(Qt.PointingHandCursor)
        return btn
    
    def _setup_animation(self):
        """Setup hover animation."""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
    
    def enterEvent(self, event):
        """Card hover enter."""
        # Subtle lift effect
        current_geo = self.geometry()
        self.animation.setStartValue(current_geo)
        new_geo = QRect(current_geo.x(), current_geo.y() - 2, current_geo.width(), current_geo.height())
        self.animation.setEndValue(new_geo)
        self.animation.start()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Card hover leave."""
        current_geo = self.geometry()
        self.animation.setStartValue(current_geo)
        new_geo = QRect(current_geo.x(), current_geo.y() + 2, current_geo.width(), current_geo.height())
        self.animation.setEndValue(new_geo)
        self.animation.start()
        super().leaveEvent(event)


class TunnelCardsWidget(QWidget):
    """Container widget that displays tunnels as modern cards."""
    
    # Signals
    card_clicked = Signal(str)
    start_tunnel = Signal(str)
    stop_tunnel = Signal(str)
    edit_tunnel = Signal(str)
    delete_tunnel = Signal(str)
    files_tunnel = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.cards = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the scrollable cards container."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Cards container
        self.cards_container = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setSpacing(16)
        self.cards_layout.setContentsMargins(16, 16, 16, 16)
        self.cards_layout.addStretch()
        
        scroll.setWidget(self.cards_container)
        main_layout.addWidget(scroll)
    
    def refresh_cards(self, configs: dict, active_tunnels: dict):
        """Refresh all tunnel cards."""
        # Remove existing cards
        for card in self.cards.values():
            self.cards_layout.removeWidget(card)
            card.deleteLater()
        self.cards.clear()
        
        # Create new cards
        for name, config in configs.items():
            is_active = name in active_tunnels
            card = TunnelCard(name, config, is_active, self)
            
            # Connect signals
            card.clicked.connect(self.card_clicked.emit)
            card.start_clicked.connect(self.start_tunnel.emit)
            card.stop_clicked.connect(self.stop_tunnel.emit)
            card.edit_clicked.connect(self.edit_tunnel.emit)
            card.delete_clicked.connect(self.delete_tunnel.emit)
            card.files_clicked.connect(self.files_tunnel.emit)
            
            self.cards[name] = card
            self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        
        # Show empty state if no tunnels
        if not configs:
            self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state message."""
        empty_widget = QWidget()
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        icon_label = QLabel("🔐")
        icon_label.setFont(QFont("Segoe UI Emoji", 48))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        
        text_label = QLabel("No Tunnels Configured")
        text_label.setFont(QFont("Inter", 16, QFont.Bold))
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setStyleSheet(f"color: {COLORS['text_secondary']};")
        
        hint_label = QLabel("Click '➕ Add' to create your first SSH tunnel")
        hint_label.setFont(QFont("Inter", 10))
        hint_label.setAlignment(Qt.AlignCenter)
        hint_label.setStyleSheet(f"color: {COLORS['text_tertiary']};")
        
        empty_layout.addWidget(icon_label)
        empty_layout.addWidget(text_label)
        empty_layout.addWidget(hint_label)
        
        self.cards_layout.insertWidget(0, empty_widget)
