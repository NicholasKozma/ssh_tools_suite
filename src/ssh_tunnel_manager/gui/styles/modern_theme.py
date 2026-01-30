#!/usr/bin/env python3
"""
SSH Tunnel Manager - Ultra Modern Theme
A complete visual redesign with card-based interface, gradients, and animations
"""

# Modern Color Palette - Dark/Light hybrid with vibrant accents
COLORS = {
    # Base colors
    'bg_app': '#0f1419',  # Deep charcoal
    'bg_primary': '#1a1f2e',  # Dark blue-grey
    'bg_secondary': '#242b3d',  # Lighter panel
    'bg_card': '#2a3142',  # Card background
    'bg_card_hover': '#313952',  # Card hover state
    
    # Accent colors
    'accent_blue': '#00d4ff',  # Bright cyan
    'accent_purple': '#a855f7',  # Vibrant purple
    'accent_green': '#10b981',  # Modern green
    'accent_orange': '#fb923c',  # Warm orange
    'accent_red': '#ef4444',  # Alert red
    'accent_yellow': '#fbbf24',  # Warning yellow
    
    # Gradients
    'gradient_primary': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00d4ff, stop:1 #a855f7)',
    'gradient_success': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #10b981, stop:1 #14b8a6)',
    'gradient_warning': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #fb923c, stop:1 #f59e0b)',
    'gradient_danger': 'qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ef4444, stop:1 #dc2626)',
    
    # Text colors
    'text_primary': '#e5e7eb',  # Almost white
    'text_secondary': '#9ca3af',  # Grey
    'text_tertiary': '#6b7280',  # Dim grey
    'text_accent': '#00d4ff',  # Bright accent
    
    # Status colors
    'status_running': '#10b981',
    'status_stopped': '#6b7280',
    'status_error': '#ef4444',
    'status_connecting': '#fb923c',
    
    # Borders and shadows
    'border': '#374151',
    'border_focus': '#00d4ff',
    'shadow': 'rgba(0, 0, 0, 0.5)',
}


def get_modern_stylesheet() -> str:
    """Return the complete ultra-modern stylesheet."""
    return f"""
/* ==================== GLOBAL ==================== */
QMainWindow {{
    background-color: {COLORS['bg_app']};
}}

QWidget {{
    font-family: 'Inter', 'Segoe UI', 'Roboto', sans-serif;
    font-size: 9.5pt;
    color: {COLORS['text_primary']};
    outline: none;
}}

/* ==================== MENU BAR ==================== */
QMenuBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['bg_primary']},
        stop:1 {COLORS['bg_app']});
    border-bottom: 2px solid {COLORS['border']};
    padding: 6px;
    spacing: 8px;
}}

QMenuBar::item {{
    background-color: transparent;
    padding: 8px 16px;
    border-radius: 6px;
    color: {COLORS['text_secondary']};
    font-weight: 500;
}}

QMenuBar::item:selected {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_accent']};
}}

QMenu {{
    background-color: {COLORS['bg_card']};
    border: 1px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px;
}}

QMenu::item {{
    padding: 10px 32px 10px 16px;
    border-radius: 6px;
    color: {COLORS['text_primary']};
}}

QMenu::item:selected {{
    background: {COLORS['gradient_primary']};
    color: white;
}}

QMenu::separator {{
    height: 1px;
    background: {COLORS['border']};
    margin: 6px 12px;
}}

/* ==================== BUTTONS ==================== */
QPushButton {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 9.5pt;
    color: {COLORS['text_primary']};
    min-height: 36px;
}}

QPushButton:hover {{
    background-color: {COLORS['bg_card_hover']};
    border-color: {COLORS['accent_blue']};
    color: {COLORS['accent_blue']};
}}

QPushButton:pressed {{
    background-color: {COLORS['bg_primary']};
}}

QPushButton:disabled {{
    background-color: {COLORS['bg_primary']};
    border-color: {COLORS['border']};
    color: {COLORS['text_tertiary']};
}}

/* Button variants */
QPushButton#primary {{
    background: {COLORS['gradient_primary']};
    border: none;
    color: white;
    font-weight: 700;
}}

QPushButton#primary:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #00b8e6, stop:1 #9333ea);
}}

QPushButton#success {{
    background: {COLORS['gradient_success']};
    border: none;
    color: white;
    font-weight: 700;
}}

QPushButton#success:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #059669, stop:1 #0d9488);
}}

QPushButton#danger {{
    background: {COLORS['gradient_danger']};
    border: none;
    color: white;
    font-weight: 700;
}}

QPushButton#danger:hover {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #dc2626, stop:1 #b91c1c);
}}

QPushButton#warning {{
    background: {COLORS['gradient_warning']};
    border: none;
    color: white;
    font-weight: 700;
}}

/* Icon-only buttons */
QPushButton#iconButton {{
    min-width: 40px;
    min-height: 40px;
    max-width: 40px;
    max-height: 40px;
    border-radius: 20px;
    padding: 0px;
    background-color: {COLORS['bg_card']};
}}

QPushButton#iconButton:hover {{
    background: {COLORS['gradient_primary']};
    border-color: transparent;
}}

/* ==================== TABLE / CARDS ==================== */
QTableWidget {{
    background-color: transparent;
    gridline-color: transparent;
    border: none;
    selection-background-color: {COLORS['bg_card_hover']};
    outline: none;
}}

QTableWidget::item {{
    background-color: {COLORS['bg_card']};
    padding: 16px;
    border-radius: 12px;
    margin: 8px;
    border: 2px solid {COLORS['border']};
}}

QTableWidget::item:hover {{
    background-color: {COLORS['bg_card_hover']};
    border-color: {COLORS['accent_blue']};
}}

QTableWidget::item:selected {{
    background-color: {COLORS['bg_card_hover']};
    border: 2px solid {COLORS['accent_blue']};
}}

QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['bg_primary']},
        stop:1 {COLORS['bg_app']});
    color: {COLORS['text_secondary']};
    padding: 12px;
    border: none;
    font-weight: 700;
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

QHeaderView::section:hover {{
    color: {COLORS['text_accent']};
}}

/* ==================== SCROLLBAR ==================== */
QScrollBar:vertical {{
    background-color: {COLORS['bg_primary']};
    width: 12px;
    border-radius: 6px;
    margin: 0px;
}}

QScrollBar::handle:vertical {{
    background-color: {COLORS['bg_card']};
    border-radius: 6px;
    min-height: 30px;
}}

QScrollBar::handle:vertical:hover {{
    background: {COLORS['gradient_primary']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background-color: {COLORS['bg_primary']};
    height: 12px;
    border-radius: 6px;
    margin: 0px;
}}

QScrollBar::handle:horizontal {{
    background-color: {COLORS['bg_card']};
    border-radius: 6px;
    min-width: 30px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {COLORS['gradient_primary']};
}}

/* ==================== TEXT WIDGETS ==================== */
QTextEdit, QPlainTextEdit {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 12px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_blue']};
}}

QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {COLORS['accent_blue']};
}}

/* ==================== LINE EDIT / INPUT ==================== */
QLineEdit {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 10px 14px;
    color: {COLORS['text_primary']};
    selection-background-color: {COLORS['accent_blue']};
    font-size: 10pt;
}}

QLineEdit:focus {{
    border-color: {COLORS['accent_blue']};
    background-color: {COLORS['bg_card_hover']};
}}

QLineEdit:disabled {{
    background-color: {COLORS['bg_primary']};
    color: {COLORS['text_tertiary']};
}}

/* ==================== COMBO BOX ==================== */
QComboBox {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    min-height: 32px;
}}

QComboBox:hover {{
    border-color: {COLORS['accent_blue']};
}}

QComboBox::drop-down {{
    border: none;
    width: 32px;
}}

QComboBox::down-arrow {{
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid {COLORS['text_secondary']};
    margin-right: 8px;
}}

QComboBox QAbstractItemView {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['accent_blue']};
    border-radius: 8px;
    selection-background-color: {COLORS['accent_blue']};
    color: {COLORS['text_primary']};
    padding: 4px;
}}

/* ==================== SPIN BOX ==================== */
QSpinBox, QDoubleSpinBox {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 8px;
    padding: 8px 12px;
    color: {COLORS['text_primary']};
    min-height: 32px;
}}

QSpinBox:focus, QDoubleSpinBox:focus {{
    border-color: {COLORS['accent_blue']};
}}

QSpinBox::up-button, QDoubleSpinBox::up-button {{
    background-color: {COLORS['bg_primary']};
    border-radius: 4px;
    margin: 2px;
}}

QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {COLORS['accent_blue']};
}}

QSpinBox::down-button, QDoubleSpinBox::down-button {{
    background-color: {COLORS['bg_primary']};
    border-radius: 4px;
    margin: 2px;
}}

QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {COLORS['accent_blue']};
}}

/* ==================== CHECK BOX ==================== */
QCheckBox {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QCheckBox::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS['border']};
    border-radius: 6px;
    background-color: {COLORS['bg_card']};
}}

QCheckBox::indicator:hover {{
    border-color: {COLORS['accent_blue']};
}}

QCheckBox::indicator:checked {{
    background: {COLORS['gradient_primary']};
    border-color: {COLORS['accent_blue']};
    image: url(data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'><path d='M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z'/></svg>);
}}

/* ==================== RADIO BUTTON ==================== */
QRadioButton {{
    color: {COLORS['text_primary']};
    spacing: 8px;
}}

QRadioButton::indicator {{
    width: 20px;
    height: 20px;
    border: 2px solid {COLORS['border']};
    border-radius: 10px;
    background-color: {COLORS['bg_card']};
}}

QRadioButton::indicator:hover {{
    border-color: {COLORS['accent_blue']};
}}

QRadioButton::indicator:checked {{
    background: {COLORS['gradient_primary']};
    border-color: {COLORS['accent_blue']};
}}

/* ==================== GROUP BOX ==================== */
QGroupBox {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 12px;
    margin-top: 24px;
    padding-top: 24px;
    font-weight: 600;
    font-size: 10pt;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 16px;
    top: 8px;
    color: {COLORS['text_accent']};
    background-color: {COLORS['bg_card']};
    padding: 4px 12px;
    border-radius: 6px;
}}

/* ==================== TAB WIDGET ==================== */
QTabWidget::pane {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 12px;
    padding: 8px;
}}

QTabBar::tab {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-bottom: none;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    padding: 10px 20px;
    margin-right: 4px;
    color: {COLORS['text_secondary']};
    font-weight: 600;
}}

QTabBar::tab:hover {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
}}

QTabBar::tab:selected {{
    background: {COLORS['gradient_primary']};
    color: white;
    border-color: {COLORS['accent_blue']};
}}

/* ==================== PROGRESS BAR ==================== */
QProgressBar {{
    background-color: {COLORS['bg_primary']};
    border: 2px solid {COLORS['border']};
    border-radius: 10px;
    text-align: center;
    color: {COLORS['text_primary']};
    font-weight: 600;
    height: 24px;
}}

QProgressBar::chunk {{
    background: {COLORS['gradient_primary']};
    border-radius: 8px;
}}

/* ==================== STATUS BAR ==================== */
QStatusBar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['bg_primary']},
        stop:1 {COLORS['bg_app']});
    color: {COLORS['text_secondary']};
    border-top: 2px solid {COLORS['border']};
    padding: 6px 12px;
}}

QStatusBar::item {{
    border: none;
}}

/* ==================== TOOLTIP ==================== */
QToolTip {{
    background-color: {COLORS['bg_card']};
    color: {COLORS['text_primary']};
    border: 2px solid {COLORS['accent_blue']};
    border-radius: 8px;
    padding: 8px 12px;
    font-size: 9pt;
}}

/* ==================== SPLITTER ==================== */
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
    background: {COLORS['gradient_primary']};
}}

/* ==================== DIALOG ==================== */
QDialog {{
    background-color: {COLORS['bg_primary']};
}}

/* ==================== LABEL ==================== */
QLabel {{
    color: {COLORS['text_primary']};
    background-color: transparent;
}}

QLabel#heading {{
    font-size: 18pt;
    font-weight: 700;
    color: {COLORS['text_accent']};
}}

QLabel#subheading {{
    font-size: 12pt;
    font-weight: 600;
    color: {COLORS['text_secondary']};
}}

QLabel#status {{
    padding: 6px 12px;
    border-radius: 6px;
    font-weight: 700;
    font-size: 9pt;
}}

QLabel#statusRunning {{
    background-color: {COLORS['status_running']};
    color: white;
}}

QLabel#statusStopped {{
    background-color: {COLORS['status_stopped']};
    color: white;
}}

QLabel#statusError {{
    background-color: {COLORS['status_error']};
    color: white;
}}

/* ==================== CUSTOM WIDGETS ==================== */
QFrame#card {{
    background-color: {COLORS['bg_card']};
    border: 2px solid {COLORS['border']};
    border-radius: 16px;
    padding: 20px;
}}

QFrame#card:hover {{
    border-color: {COLORS['accent_blue']};
    background-color: {COLORS['bg_card_hover']};
}}

QFrame#separator {{
    background-color: {COLORS['border']};
    max-height: 2px;
    border: none;
}}

QFrame#toolbar {{
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 {COLORS['bg_primary']},
        stop:1 {COLORS['bg_app']});
    border: 2px solid {COLORS['border']};
    border-radius: 12px;
    padding: 12px;
}}

/* ==================== ANIMATIONS (via property) ==================== */
* {{
    /* Smooth transitions for interactive elements */
}}
"""


# Status badge styles
def get_status_badge_style(status: str) -> str:
    """Get style for status badges."""
    status_styles = {
        'running': f"background: {COLORS['gradient_success']}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 9pt;",
        'stopped': f"background-color: {COLORS['status_stopped']}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 9pt;",
        'connecting': f"background: {COLORS['gradient_warning']}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 9pt;",
        'error': f"background: {COLORS['gradient_danger']}; color: white; padding: 6px 16px; border-radius: 20px; font-weight: 700; font-size: 9pt;",
    }
    return status_styles.get(status.lower(), status_styles['stopped'])


# Icon mapping for modern design
ICONS = {
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'start': '▶️',
    'stop': '⏹️',
    'test': '🔌',
    'files': '📁',
    'web': '🌐',
    'rtsp': '📹',
    'rdp': '🖥️',
    'scan': '🔍',
    'powershell': '⚡',
    'running': '🟢',
    'stopped': '🔴',
    'connecting': '🟡',
    'settings': '⚙️',
    'info': 'ℹ️',
    'warning': '⚠️',
    'error': '❌',
    'success': '✅',
    'tunnel': '🔐',
    'network': '🌐',
    'key': '🔑',
}
