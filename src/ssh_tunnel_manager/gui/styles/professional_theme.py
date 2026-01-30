#!/usr/bin/env python3
"""
SSH Tunnel Manager - Professional Enterprise Theme
Inspired by Linear, VS Code, and Slack - clean, purposeful, sophisticated
"""

# Professional Color Palette - Enterprise Dark Theme
COLORS = {
    # Base colors
    'bg_app': '#0d1117',           # Deep dark base
    'bg_primary': '#161b22',       # Primary surface
    'bg_secondary': '#1c2128',     # Secondary surface
    'bg_tertiary': '#21262d',      # Tertiary surface
    'bg_elevated': '#252c35',      # Elevated elements
    'bg_overlay': '#2d333b',       # Overlays and modals
    
    # Accent colors - Carefully chosen for accessibility
    'accent_primary': '#2ea44f',   # Green - success/active
    'accent_secondary': '#1f6feb', # Blue - info/links
    'accent_tertiary': '#8957e5',  # Purple - special
    'accent_warning': '#d29922',   # Amber - warnings
    'accent_error': '#f85149',     # Red - errors/stop
    
    # Text colors
    'text_primary': '#e6edf3',     # Primary text
    'text_secondary': '#7d8590',   # Secondary text
    'text_tertiary': '#656d76',    # Tertiary/disabled text
    'text_link': '#58a6ff',        # Links
    'text_success': '#3fb950',     # Success messages
    'text_error': '#ff7b72',       # Error messages
    
    # Border colors
    'border_default': '#30363d',   # Default borders
    'border_muted': '#21262d',     # Subtle borders
    'border_strong': '#6e7681',    # Strong borders
    'border_accent': '#1f6feb',    # Accent borders
    
    # Status colors
    'status_active': '#2ea44f',    # Active/running
    'status_inactive': '#6e7681',  # Inactive/stopped
    'status_warning': '#d29922',   # Warning state
    'status_error': '#f85149',     # Error state
    'status_pending': '#58a6ff',   # Pending/connecting
    
    # Button states
    'btn_primary_bg': '#238636',
    'btn_primary_hover': '#2ea044',
    'btn_primary_active': '#1a7f37',
    'btn_secondary_bg': '#21262d',
    'btn_secondary_hover': '#30363d',
    'btn_danger_bg': '#da3633',
    'btn_danger_hover': '#f85149',
}


def get_professional_stylesheet() -> str:
    """Return the complete professional stylesheet."""
    return f"""
/* ==================== GLOBAL STYLES ==================== */
QMainWindow {{
    background-color: {COLORS['bg_app']};
}}

QWidget {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
    font-size: 13px;
    color: {COLORS['text_primary']};
    outline: none;
}}

/* ==================== MENU BAR ==================== */
QMenuBar {{
    background-color: {COLORS['bg_primary']};
    border-bottom: 1px solid {COLORS['border_default']};
    padding: 4px 8px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 6px;
    color: {COLORS['text_secondary']};
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_primary']};
}}

QMenuBar::item:pressed {{
    background-color: {COLORS['bg_tertiary']};
}}

QMenu {{
    background-color: {COLORS['bg_overlay']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 4px;
}}

QMenu::item {{
    padding: 8px 24px 8px 12px;
    border-radius: 4px;
    color: {COLORS['text_primary']};
}}

QMenu::item:selected {{
    background-color: {COLORS['accent_secondary']};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background: {COLORS['border_default']};
    margin: 4px 8px;
}}

/* ==================== BUTTONS ==================== */
QPushButton {{
    background-color: {COLORS['btn_secondary_bg']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 5px 16px;
    font-weight: 500;
    color: {COLORS['text_primary']};
    min-height: 28px;
}}

QPushButton:hover {{
    background-color: {COLORS['btn_secondary_hover']};
    border-color: {COLORS['border_strong']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_secondary']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_secondary']};
    border-color: {COLORS['border_muted']};
    color: {COLORS['text_tertiary']};
}}

/* Primary button */
QPushButton#primary {{
    background-color: {COLORS['btn_primary_bg']};
    border: 1px solid rgba(240, 246, 252, 0.1);
    color: white;
    font-weight: 600;
}}

QPushButton#primary:hover {{
    background-color: {COLORS['btn_primary_hover']};
}}

QPushButton#primary:pressed {{
    background-color: {COLORS['btn_primary_active']};
}}

/* Success button */
QPushButton#success {{
    background-color: {COLORS['btn_primary_bg']};
    border: 1px solid rgba(240, 246, 252, 0.1);
    color: white;
    font-weight: 600;
}}

QPushButton#success:hover {{
    background-color: {COLORS['btn_primary_hover']};
}}

/* Danger button */
QPushButton#danger {{
    background-color: {COLORS['btn_danger_bg']};
    border: 1px solid rgba(248, 81, 73, 0.4);
    color: white;
    font-weight: 600;
}}

QPushButton#danger:hover {{
    background-color: {COLORS['btn_danger_hover']};
}}

/* ==================== TABLE WIDGET ==================== */
QTableWidget {{
    background-color: {COLORS['bg_primary']};
    gridline-color: {COLORS['border_muted']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    selection-background-color: {COLORS['bg_tertiary']};
}}

QTableWidget::item {{
    padding: 8px;
    border: none;
}}

QTableWidget::item:selected {{
    background-color: {COLORS['bg_tertiary']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['bg_secondary']};
}}

QHeaderView::section {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_secondary']};
    padding: 8px;
    border: none;
    border-bottom: 1px solid {COLORS['border_default']};
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ==================== SCROLLBAR ==================== */
QScrollBar:vertical {{
    background-color: {COLORS['bg_primary']};
    width: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['border_strong']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {COLORS['text_tertiary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_primary']};
    height: 12px;
    border-radius: 6px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['border_strong']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background-color: {COLORS['text_tertiary']};
}}

/* ==================== TEXT EDIT ==================== */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 8px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_secondary']};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['accent_secondary']};
}}

/* ==================== LINE EDIT ==================== */
QLineEdit {{
    background-color: {COLORS['bg_tertiary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 6px 10px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_secondary']};
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_secondary']};
    background-color: {COLORS['bg_elevated']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_secondary']};
    color: {COLORS['text_tertiary']};
}}

/* ==================== COMBO BOX ==================== */
QComboBox {{
    background-color: {COLORS['bg_tertiary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 5px 10px;
    color: {COLORS['text_primary']};
    min-height: 28px;
}}

QComboBox:hover {{
    border-color: {COLORS['border_strong']};
}}

QComboBox:focus {{
    border-color: {COLORS['accent_secondary']};
}}

QComboBox::drop-down {{
    border: none;
    width: 30px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 5px solid {COLORS['text_secondary']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_overlay']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    selection-background-color: {COLORS['accent_secondary']};
    color: {COLORS['text_primary']};
    padding: 4px;
}}

/* ==================== SPIN BOX ==================== */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_tertiary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 5px 10px;
    color: {COLORS['text_primary']};
    min-height: 28px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['accent_secondary']};
}}

/* ==================== CHECK BOX ==================== */
QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid {COLORS['border_strong']};
    border-radius: 4px;
    background-color: {COLORS['bg_tertiary']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent_secondary']};
}}

QCheckBox::indicator:checked {{
    background-color: {COLORS['accent_secondary']};
    border-color: {COLORS['accent_secondary']};
}}

/* ==================== RADIO BUTTON ==================== */
QRadioButton {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 18px;
    height: 18px;
    border: 1.5px solid {COLORS['border_strong']};
    border-radius: 9px;
    background-color: {COLORS['bg_tertiary']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['accent_secondary']};
}}

QRadioButton::indicator:checked {{
    background-color: {COLORS['accent_secondary']};
    border-color: {COLORS['accent_secondary']};
}}

/* ==================== GROUP BOX ==================== */
QGroupBox {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
    margin-top: 16px;
    padding-top: 20px;
    font-weight: 600;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    top: 6px;
    color: {COLORS['text_secondary']};
    background-color: {COLORS['bg_primary']};
    padding: 2px 8px;
}}

/* ==================== TAB WIDGET ==================== */
QTabWidget::pane {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    top: -1px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
    color: {COLORS['text_secondary']};
    font-weight: 500;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['bg_tertiary']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:selected {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_primary']};
    border-bottom: 2px solid {COLORS['accent_secondary']};
}}

/* ==================== PROGRESS BAR ==================== */
QProgressBar {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-weight: 600;
    height: 20px;
}}

QProgressBar::chunk {{
    background-color: {COLORS['accent_primary']};
    border-radius: 7px;
}}

/* ==================== STATUS BAR ==================== */
QStatusBar {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_secondary']};
    border-top: 1px solid {COLORS['border_default']};
    padding: 4px 8px;
}}

QStatusBar::item {{
    border: none;
}}

/* ==================== TOOLTIP ==================== */
QToolTip {{
    background-color: {COLORS['bg_overlay']};
    color: {COLORS['text_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 6px;
    padding: 6px 10px;
    font-size: 12px;
}}

/* ==================== SPLITTER ==================== */
QSplitter::handle {{
    background-color: {COLORS['border_default']};
}}

QSplitter::handle:horizontal {{
    width: 1px;
}}

QSplitter::handle:vertical {{
    height: 1px;
}}

QSplitter::handle:hover {{
    background-color: {COLORS['border_strong']};
}}

/* ==================== CUSTOM FRAMES ==================== */
QFrame#card {{
    background-color: {COLORS['bg_secondary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
    padding: 16px;
}}

QFrame#card:hover {{
    border-color: {COLORS['border_strong']};
}}

QFrame#separator {{
    background-color: {COLORS['border_default']};
    max-height: 1px;
    border: none;
}}

QFrame#toolbar {{
    background-color: {COLORS['bg_primary']};
    border: 1px solid {COLORS['border_default']};
    border-radius: 8px;
    padding: 8px;
}}

/* ==================== LABELS ==================== */
QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QLabel#heading {{
    font-size: 24px;
    font-weight: 600;
    color: {COLORS['text_primary']};
}}

QLabel#subheading {{
    font-size: 16px;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}

QLabel#muted {{
    color: {COLORS['text_secondary']};
}}

QLabel#tertiary {{
    color: {COLORS['text_tertiary']};
}}
"""


def get_status_style(status: str) -> str:
    """Get inline style for status indicators."""
    status_styles = {
        'active': f"background-color: {COLORS['status_active']}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;",
        'inactive': f"background-color: {COLORS['status_inactive']}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;",
        'warning': f"background-color: {COLORS['status_warning']}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;",
        'error': f"background-color: {COLORS['status_error']}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;",
        'pending': f"background-color: {COLORS['status_pending']}; color: white; padding: 4px 10px; border-radius: 12px; font-weight: 600; font-size: 11px;",
    }
    return status_styles.get(status.lower(), status_styles['inactive'])
