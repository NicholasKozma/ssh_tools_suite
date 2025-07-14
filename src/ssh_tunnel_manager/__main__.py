#!/usr/bin/env python3
"""
SSH Tunnel Manager - Module Entry Point
"""

from .gui import SSHTunnelManager
from .gui.main_window_actions import MainWindowActions

import sys
try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    print("PySide6 not installed. Please install with: pip install PySide6")
    sys.exit(1)


class SSHTunnelManagerApp(SSHTunnelManager, MainWindowActions):
    """Complete SSH Tunnel Manager application with all functionality."""
    pass


def main():
    """Main application entry point."""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Allow running in system tray
    
    # Create and show main window
    window = SSHTunnelManagerApp()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
