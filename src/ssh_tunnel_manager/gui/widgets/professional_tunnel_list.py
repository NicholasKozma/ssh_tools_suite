#!/usr/bin/env python3
"""
Professional Tunnel List - Table-based design
Clean, information-dense, enterprise aesthetic
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QFrame
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..styles.professional_theme import COLORS, TYPOGRAPHY, SPACING, RADIUS, get_status_style


class ProfessionalTunnelList(QWidget):
    """Professional table widget for tunnel management."""
    
    # Signals
    selection_changed = Signal(bool, str, bool)  # has_selection, config_name, is_active
    start_tunnel = Signal(str)
    stop_tunnel = Signal(str)
    edit_tunnel = Signal(str)
    delete_tunnel = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup table UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(SPACING['md'])
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.setSpacing(SPACING['md'])
        
        title = QLabel("Tunnels")
        title.setStyleSheet(f"""
            font-size: {TYPOGRAPHY['text_lg']}pt;
            font-weight: {TYPOGRAPHY['weight_semibold']};
            color: {COLORS['text_primary']};
        """)
        header_layout.addWidget(title)
        
        self.count_label = QLabel("0 configured")
        self.count_label.setStyleSheet(f"""
            font-size: {TYPOGRAPHY['text_sm']}pt;
            color: {COLORS['text_tertiary']};
        """)
        header_layout.addWidget(self.count_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Name", "Status", "Type", "Local Port", "Remote", "SSH Host"
        ])
        
        # Table styling
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setFocusPolicy(Qt.StrongFocus)
        self.table.setSortingEnabled(True)
        
        # Column sizing
        header = self.table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Stretch)
        header.setSectionResizeMode(5, QHeaderView.Stretch)
        
        # Row height
        self.table.verticalHeader().setDefaultSectionSize(48)
        
        # Signals
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        
        layout.addWidget(self.table)
    
    def _on_selection_changed(self):
        """Handle selection changes."""
        selected_rows = self.table.selectedItems()
        if not selected_rows:
            self.selection_changed.emit(False, "", False)
            return
        
        row = self.table.currentRow()
        if row < 0:
            return
        
        name_item = self.table.item(row, 0)
        status_item = self.table.item(row, 1)
        
        if name_item and status_item:
            config_name = name_item.text()
            is_active = "Running" in status_item.text()
            self.selection_changed.emit(True, config_name, is_active)
    
    def refresh_table(self, configs: dict, active_tunnels: dict):
        """Refresh the tunnel table."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)
        
        for idx, (name, config) in enumerate(configs.items()):
            self.table.insertRow(idx)
            
            # Name
            name_item = QTableWidgetItem(name)
            name_item.setFont(QFont(TYPOGRAPHY['font_sans'], TYPOGRAPHY['text_base'], TYPOGRAPHY['weight_medium']))
            self.table.setItem(idx, 0, name_item)
            
            # Status
            is_active = name in active_tunnels and active_tunnels[name].is_running
            status_text = "Running" if is_active else "Stopped"
            status_item = QTableWidgetItem(status_text)
            status_item.setFont(QFont(TYPOGRAPHY['font_sans'], TYPOGRAPHY['text_sm'], TYPOGRAPHY['weight_semibold']))
            
            if is_active:
                status_item.setForeground(Qt.GlobalColor(COLORS['accent_success']))
            else:
                status_item.setForeground(Qt.GlobalColor(COLORS['text_tertiary']))
            
            self.table.setItem(idx, 1, status_item)
            
            # Type
            type_item = QTableWidgetItem(config.tunnel_type.upper())
            type_item.setFont(QFont(TYPOGRAPHY['font_mono'], TYPOGRAPHY['text_xs']))
            self.table.setItem(idx, 2, type_item)
            
            # Local Port
            port_item = QTableWidgetItem(str(config.local_port))
            port_item.setFont(QFont(TYPOGRAPHY['font_mono'], TYPOGRAPHY['text_sm']))
            self.table.setItem(idx, 3, port_item)
            
            # Remote
            remote_text = f"{config.remote_host}:{config.remote_port}"
            remote_item = QTableWidgetItem(remote_text)
            remote_item.setFont(QFont(TYPOGRAPHY['font_mono'], TYPOGRAPHY['text_sm']))
            self.table.setItem(idx, 4, remote_item)
            
            # SSH Host
            ssh_text = f"{config.ssh_user}@{config.ssh_host}:{config.ssh_port}"
            ssh_item = QTableWidgetItem(ssh_text)
            ssh_item.setFont(QFont(TYPOGRAPHY['font_mono'], TYPOGRAPHY['text_sm']))
            self.table.setItem(idx, 5, ssh_item)
        
        self.table.setSortingEnabled(True)
        self.count_label.setText(f"{len(configs)} configured, {len(active_tunnels)} active")
        
        # Show empty state
        if not configs:
            self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state message."""
        self.table.setRowCount(1)
        empty_item = QTableWidgetItem("No tunnels configured. Click 'New Tunnel' to get started.")
        empty_item.setTextAlignment(Qt.AlignCenter)
        empty_item.setFont(QFont(TYPOGRAPHY['font_sans'], TYPOGRAPHY['text_base']))
        empty_item.setForeground(Qt.GlobalColor(COLORS['text_tertiary']))
        self.table.setItem(0, 0, empty_item)
        self.table.setSpan(0, 0, 1, 6)
    
    def get_selected_config_name(self) -> str:
        """Get the currently selected config name."""
        row = self.table.currentRow()
        if row < 0:
            return ""
        name_item = self.table.item(row, 0)
        return name_item.text() if name_item else ""
