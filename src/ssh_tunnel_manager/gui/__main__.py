#!/usr/bin/env python3
"""
SSH Tunnel Manager GUI entry point
"""

import sys
from pathlib import Path

# Add the parent directory to Python path for relative imports
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent
sys.path.insert(0, str(src_dir))

def main():
    """Main entry point for SSH Tunnel Manager GUI."""
    # Check if required third-party tools are installed
    try:
        from ssh_tools_common.install_check import ensure_third_party_tools_installed
        if not ensure_third_party_tools_installed("SSH Tunnel Manager"):
            return 1
    except ImportError:
        print("Warning: Could not verify third-party tools installation")
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
    except ImportError:
        print("PySide6 not installed. Please install with: pip install ssh-tools-suite[gui]")
        sys.exit(1)

    # Import the main application
    try:
        # Try importing from the installed package first
        from ssh_tunnel_manager.gui import SSHTunnelManager
    except ImportError:
        # Fall back to relative import for development
        sys.path.insert(0, str(src_dir.parent))
        from ssh_tunnel_manager_app import SSHTunnelManagerApp as SSHTunnelManager

    # Create and run the application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Allow running in system tray
    
    # Create and show main window
    window = SSHTunnelManager()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
