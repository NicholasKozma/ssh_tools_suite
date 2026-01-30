#!/usr/bin/env python3
"""
Professional Dashboard Widget
Overview statistics and metrics
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont

from ..styles.professional_theme import COLORS


class StatCard(QFrame):
    """A stat card for displaying a single metric."""
    
    def __init__(self, label: str, value: str = "0", color: str = None, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setMinimumHeight(80)
        self.setMaximumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(14, 12, 14, 12)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.value_label.setStyleSheet(f"color: {color or COLORS['accent_secondary']};")
        layout.addWidget(self.value_label)
        
        # Label
        label_widget = QLabel(label)
        label_widget.setObjectName("muted")
        label_widget.setFont(QFont("Segoe UI", 10))
        layout.addWidget(label_widget)
        
        layout.addStretch()
    
    def set_value(self, value: str):
        """Update the displayed value."""
        self.value_label.setText(value)


class ProfessionalDashboard(QWidget):
    """Dashboard with overview statistics."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Title
        title = QLabel("Overview")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet(f"color: {COLORS['text_primary']};")
        layout.addWidget(title)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(12)
        
        self.active_card = StatCard("Active Tunnels", "0", COLORS['accent_primary'])
        self.total_card = StatCard("Total Configured", "0", COLORS['accent_secondary'])
        self.stopped_card = StatCard("Stopped", "0", COLORS['text_secondary'])
        self.connections_card = StatCard("Connections Today", "0", COLORS['accent_tertiary'])
        
        stats_layout.addWidget(self.active_card, 0, 0)
        stats_layout.addWidget(self.total_card, 0, 1)
        stats_layout.addWidget(self.stopped_card, 0, 2)
        stats_layout.addWidget(self.connections_card, 0, 3)
        
        layout.addLayout(stats_layout)
    
    def update_stats(self, active: int, total: int, connections: int = 0):
        """Update dashboard statistics."""
        stopped = total - active
        
        self.active_card.set_value(str(active))
        self.total_card.set_value(str(total))
        self.stopped_card.set_value(str(stopped))
        self.connections_card.set_value(str(connections))
