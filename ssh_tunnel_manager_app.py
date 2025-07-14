#!/usr/bin/env python3
"""
SSH Tunnel Manager Application
==============================

A professional, comprehensive application for managing SSH tunnels and connections.

Usage:
    python ssh_tunnel_manager_app.py

Features:
- SSH tunnel creation and management
- Connection monitoring and status tracking
- Port forwarding configuration
- Tunnel persistence and auto-reconnection
- Professional GUI interface
- System tray integration
- Comprehensive logging and error handling

This is the main entry point for the SSH Tunnel Manager application.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
except ImportError:
    print("PySide6 not installed. Please install with: pip install PySide6")
    sys.exit(1)

from ssh_tunnel_manager.gui import SSHTunnelManager
from ssh_tunnel_manager.gui.main_window_actions import MainWindowActions


class SSHTunnelManagerApp(SSHTunnelManager):
    """Complete SSH Tunnel Manager application with all functionality."""
    
    def __init__(self):
        """Initialize the complete SSH Tunnel Manager application."""
        # Initialize the main window (SSHTunnelManager)
        super().__init__()
        
        # Add MainWindowActions functionality as a composition
        self._actions = MainWindowActions()
        self._setup_actions_delegation()
    
    def _setup_actions_delegation(self):
        """Set up delegation of MainWindowActions methods to this main window."""
        # Delegate methods from MainWindowActions to this main window
        # by binding them with self as the proper Qt widget parent
        
        # Bind essential attributes that MainWindowActions might need
        self._actions.config_manager = self.config_manager
        self._actions.active_tunnels = self.active_tunnels
        self._actions.log = self.log
        self._actions.refresh_table = self._refresh_table
        
    def add_tunnel(self):
        """Add a new tunnel configuration."""
        # Call the parent class method
        super()._add_tunnel()
    
    def edit_tunnel(self):
        """Edit selected tunnel configuration."""
        # Call the parent class method instead of defining a custom implementation
        super()._edit_tunnel()
    
    def remove_tunnel(self):
        """Remove selected tunnel configuration."""
        # Call the parent class method
        super()._delete_tunnel()
    

def main():
    """Main application entry point."""
    # Note: High DPI scaling is automatically enabled in Qt6
    # No need to set AA_EnableHighDpiScaling or AA_UseHighDpiPixmaps
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Allow running in system tray
    
    # Create and show main window
    window = SSHTunnelManagerApp()
    window.show()
    
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
