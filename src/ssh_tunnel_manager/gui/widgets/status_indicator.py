#!/usr/bin/env python3
"""
SSH Tunnel Manager - Enhanced Status Indicator Widget
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPainter, QColor, QPen, QBrush


class StatusIndicator(QWidget):
    """Modern animated status indicator widget."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self._status = "stopped"  # stopped, connecting, running
        self._pulse_value = 0
        self._setup_animation()
    
    def _setup_animation(self):
        """Setup pulse animation for connecting state."""
        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._update_pulse)
        
    def set_status(self, status: str):
        """Set the status (stopped, connecting, running)."""
        self._status = status.lower()
        
        if self._status == "connecting":
            self._pulse_timer.start(50)
        else:
            self._pulse_timer.stop()
            self._pulse_value = 0
        
        self.update()
    
    def _update_pulse(self):
        """Update pulse animation."""
        self._pulse_value = (self._pulse_value + 5) % 100
        self.update()
    
    def paintEvent(self, event):
        """Paint the status indicator."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        center_x = self.width() // 2
        center_y = self.height() // 2
        base_radius = 7
        
        if self._status == "running":
            # Green solid circle
            painter.setBrush(QBrush(QColor("#4CAF50")))
            painter.setPen(QPen(QColor("#2E7D32"), 2))
            painter.drawEllipse(center_x - base_radius, center_y - base_radius, 
                              base_radius * 2, base_radius * 2)
        
        elif self._status == "connecting":
            # Orange pulsing circle
            pulse_factor = abs(self._pulse_value - 50) / 50
            radius = int(base_radius * (0.7 + 0.3 * pulse_factor))
            alpha = int(150 + 105 * pulse_factor)
            
            color = QColor("#FF9800")
            color.setAlpha(alpha)
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#F57C00"), 2))
            painter.drawEllipse(center_x - radius, center_y - radius, 
                              radius * 2, radius * 2)
        
        else:  # stopped
            # Red circle with darker border
            painter.setBrush(QBrush(QColor("#F44336")))
            painter.setPen(QPen(QColor("#C62828"), 2))
            painter.drawEllipse(center_x - base_radius, center_y - base_radius, 
                              base_radius * 2, base_radius * 2)


class ModernStatusBar(QWidget):
    """Modern status bar widget with enhanced visuals."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the status bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(12)
        
        # Status indicator
        self.status_indicator = StatusIndicator()
        layout.addWidget(self.status_indicator)
        
        # Status text
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #E0E0E0; font-weight: 500;")
        layout.addWidget(self.status_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setStyleSheet("background-color: #546E7A;")
        separator.setMaximumWidth(1)
        layout.addWidget(separator)
        
        # Connection count
        self.connection_count_label = QLabel("0 active tunnels")
        self.connection_count_label.setStyleSheet("color: #B0BEC5;")
        layout.addWidget(self.connection_count_label)
        
        layout.addStretch()
        
        # App info
        self.info_label = QLabel("SSH Tunnel Manager v1.0")
        self.info_label.setStyleSheet("color: #78909C; font-size: 9pt;")
        layout.addWidget(self.info_label)
    
    def set_status(self, status: str, message: str = ""):
        """Set the status bar state."""
        self.status_indicator.set_status(status)
        
        if message:
            self.status_label.setText(message)
        else:
            if status == "running":
                self.status_label.setText("Connected")
            elif status == "connecting":
                self.status_label.setText("Connecting...")
            else:
                self.status_label.setText("Ready")
    
    def set_connection_count(self, count: int):
        """Set the active connection count."""
        if count == 0:
            self.connection_count_label.setText("No active tunnels")
        elif count == 1:
            self.connection_count_label.setText("1 active tunnel")
        else:
            self.connection_count_label.setText(f"{count} active tunnels")
