#!/usr/bin/env python3
"""
Modern Dashboard Widget
Displays overview stats and quick actions
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..styles.modern_theme import COLORS, ICONS


class StatCard(QFrame):
    """A stat card for displaying metrics."""
    
    def __init__(self, icon: str, value: str, label: str, color: str, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(16, 16, 16, 16)
        
        # Icon and value row
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Inter", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        top_layout.addWidget(value_label)
        
        layout.addLayout(top_layout)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setFont(QFont("Inter", 10))
        label_widget.setStyleSheet(f"color: {COLORS['text_secondary']};")
        layout.addWidget(label_widget)


class DashboardWidget(QWidget):
    """Dashboard with overview statistics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("📊 Dashboard")
        title.setFont(QFont("Inter", 18, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_accent']};")
        layout.addWidget(title)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)
        
        # Create stat cards
        self.active_card = StatCard(
            ICONS['running'], "0", "Active Tunnels",
            COLORS['accent_green']
        )
        self.total_card = StatCard(
            ICONS['tunnel'], "0", "Total Configured",
            COLORS['accent_blue']
        )
        self.stopped_card = StatCard(
            ICONS['stopped'], "0", "Stopped",
            COLORS['text_tertiary']
        )
        self.connections_card = StatCard(
            ICONS['network'], "0", "Connections Today",
            COLORS['accent_purple']
        )
        
        stats_layout.addWidget(self.active_card, 0, 0)
        stats_layout.addWidget(self.total_card, 0, 1)
        stats_layout.addWidget(self.stopped_card, 0, 2)
        stats_layout.addWidget(self.connections_card, 0, 3)
        
        layout.addLayout(stats_layout)
        layout.addStretch()
    
    def update_stats(self, active: int, total: int, connections: int = 0):
        """Update dashboard statistics."""
        stopped = total - active
        
        # Update value labels
        self._update_card_value(self.active_card, str(active))
        self._update_card_value(self.total_card, str(total))
        self._update_card_value(self.stopped_card, str(stopped))
        self._update_card_value(self.connections_card, str(connections))
    
    def _update_card_value(self, card: StatCard, value: str):
        """Update a stat card's value."""
        # Find the value label (second QLabel in the layout)
        layout = card.layout()
        top_layout = layout.itemAt(0).layout()
        value_label = top_layout.itemAt(2).widget()
        if isinstance(value_label, QLabel):
            value_label.setText(value)
