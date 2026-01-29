#!/usr/bin/env python3
"""
SSH Tunnel Manager - Modern Professional Stylesheet
"""

# Color Palette - Modern Blue Theme
COLORS = {
    # Primary colors
    'primary': '#2196F3',
    'primary_dark': '#1976D2',
    'primary_light': '#64B5F6',
    
    # Secondary colors
    'secondary': '#4CAF50',
    'secondary_dark': '#388E3C',
    'warning': '#FF9800',
    'error': '#F44336',
    
    # Background colors
    'bg_primary': '#FFFFFF',
    'bg_secondary': '#F5F5F5',
    'bg_dark': '#263238',
    'bg_darker': '#1E272C',
    
    # Text colors
    'text_primary': '#212121',
    'text_secondary': '#757575',
    'text_light': '#FFFFFF',
    
    # Border colors
    'border': '#E0E0E0',
    'border_focus': '#2196F3',
    
    # Status colors
    'status_running': '#4CAF50',
    'status_stopped': '#F44336',
    'status_connecting': '#FF9800',
}

# Main application stylesheet
MAIN_STYLESHEET = f"""
/* ===== Global Styles ===== */
QMainWindow {{
    background-color: {COLORS['bg_secondary']};
}}

QWidget {{
    font-family: 'Segoe UI', 'Arial', sans-serif;
    font-size: 10pt;
    color: {COLORS['text_primary']};
}}

/* ===== Menu Bar ===== */
QMenuBar {{
    background-color: {COLORS['bg_primary']};
    border-bottom: 1px solid {COLORS['border']};
    padding: 4px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['primary_light']};
}}

QMenu {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 4px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px;
    border-radius: 3px;
}}

QMenu::item:selected {{
    background-color: {COLORS['primary_light']};
}}

/* ===== Buttons ===== */
QPushButton {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    color: {COLORS['text_primary']};
    min-height: 32px;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_light']};
    border-color: {COLORS['primary']};
    color: {COLORS['text_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
    border-color: {COLORS['primary_dark']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_secondary']};
    border-color: {COLORS['border']};
    color: {COLORS['text_secondary']};
}}

/* Primary action buttons */
QPushButton#primary {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
    color: {COLORS['text_light']};
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background-color: {COLORS['primary_dark']};
}}

/* Success buttons */
QPushButton#success {{
    background-color: {COLORS['secondary']};
    border-color: {COLORS['secondary']};
    color: {COLORS['text_light']};
    font-weight: 600;
}}

QPushButton#success:hover {{
    background-color: {COLORS['secondary_dark']};
}}

/* Danger buttons */
QPushButton#danger {{
    background-color: {COLORS['error']};
    border-color: {COLORS['error']};
    color: {COLORS['text_light']};
    font-weight: 600;
}}

QPushButton#danger:hover {{
    background-color: #D32F2F;
}}

/* ===== Table Widget ===== */
QTableWidget {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    gridline-color: {COLORS['border']};
    selection-background-color: {COLORS['primary_light']};
    selection-color: {COLORS['text_light']};
    outline: none;
}}

QTableWidget::item {{
    padding: 8px;
    border-bottom: 1px solid {COLORS['border']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['primary']};
    color: {COLORS['text_light']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['primary_light']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_light']};
    padding: 10px;
    border: none;
    border-right: 1px solid {COLORS['bg_darker']};
    font-weight: 600;
    text-transform: uppercase;
    font-size: 9pt;
    letter-spacing: 0.5px;
}}

QHeaderView::section:first {{
    border-top-left-radius: 8px;
}}

QHeaderView::section:last {{
    border-top-right-radius: 8px;
    border-right: none;
}}

QHeaderView::section:hover {{
    background-color: {COLORS['primary_dark']};
}}

/* ===== Scroll Bar ===== */
QScrollBar:vertical {{
    background-color: {COLORS['bg_secondary']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['text_secondary']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_secondary']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['text_secondary']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['primary']};
}}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0px;
}}

/* ===== Text Edit / Text Browser ===== */
QTextEdit, QTextBrowser {{
    background-color: {COLORS['bg_darker']};
    color: #E0E0E0;
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px;
    font-family: 'Consolas', 'Courier New', monospace;
    selection-background-color: {COLORS['primary']};
}}

/* ===== Group Box ===== */
QGroupBox {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 4px;
    padding: 0 8px;
    background-color: {COLORS['bg_primary']};
    color: {COLORS['primary']};
    font-size: 11pt;
}}

/* ===== Splitter ===== */
QSplitter::handle {{
    background-color: {COLORS['border']};
}}

QSplitter::handle:horizontal {{
    width: 2px;
}}

QSplitter::handle:vertical {{
    height: 2px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['primary']};
}}

/* ===== Status Bar ===== */
QStatusBar {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_light']};
    border-top: 1px solid {COLORS['border']};
    padding: 4px;
}}

/* ===== Line Edit ===== */
QLineEdit {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: {COLORS['primary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['primary']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
}}

/* ===== Combo Box ===== */
QComboBox {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 28px;
}}

QComboBox:focus {{
    border-color: {COLORS['primary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: url(none);
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    selection-background-color: {COLORS['primary']};
    selection-color: {COLORS['text_light']};
    outline: none;
}}

/* ===== Check Box ===== */
QCheckBox {{
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS['border']};
    border-radius: 4px;
    background-color: {COLORS['bg_primary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['primary']};
}}

/* ===== Radio Button ===== */
QRadioButton {{
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS['border']};
    border-radius: 10px;
    background-color: {COLORS['bg_primary']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['primary']};
    border-color: {COLORS['primary']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['primary']};
}}

/* ===== Spin Box ===== */
QSpinBox {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    padding: 8px 12px;
    min-height: 28px;
}}

QSpinBox:focus {{
    border-color: {COLORS['primary']};
}}

QSpinBox::up-button, QSpinBox::down-button {{
    background-color: transparent;
    border: none;
    width: 20px;
}}

QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background-color: {COLORS['primary_light']};
}}

/* ===== Tab Widget ===== */
QTabWidget::pane {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    padding: 10px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_primary']};
    border-bottom-color: {COLORS['bg_primary']};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['primary_light']};
}}

/* ===== Progress Bar ===== */
QProgressBar {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border']};
    border-radius: 6px;
    text-align: center;
    height: 24px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['primary']};
    border-radius: 5px;
}}

/* ===== Tool Tip ===== */
QToolTip {{
    background-color: {COLORS['bg_dark']};
    color: {COLORS['text_light']};
    border: 1px solid {COLORS['primary']};
    border-radius: 4px;
    padding: 6px 10px;
    font-size: 9pt;
}}

/* ===== Frame Separator ===== */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    border: none;
    background-color: {COLORS['border']};
    max-width: 1px;
    max-height: 1px;
}}
"""

def get_stylesheet():
    """Get the main application stylesheet."""
    return MAIN_STYLESHEET


def get_status_color(status: str) -> str:
    """Get color for a given status."""
    if 'running' in status.lower() or '🟢' in status:
        return COLORS['status_running']
    elif 'stopped' in status.lower() or '🔴' in status:
        return COLORS['status_stopped']
    elif 'connecting' in status.lower() or '🟡' in status:
        return COLORS['status_connecting']
    return COLORS['text_secondary']
