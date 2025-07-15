"""
Third Party Installer Application
=================================

A professional tool for installing and managing third-party dependencies for SSH Tools Suite.

Usage:
    python third_party_installer_app.py

Features:
- Automated installation of PsExec, VLC, FFmpeg, and PX tools
- Corporate proxy support
- Progress tracking and status monitoring  
- Professional GUI interface
- PowerShell/Windows compatible installation
- Comprehensive error handling and logging

This installer handles all third-party tool dependencies required by SSH Tools Suite.
Required tools like PsExec are automatically installed, while optional tools like VLC 
and FFmpeg can be installed as needed.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from PySide6.QtWidgets import QApplication
except ImportError:
    import subprocess
    print("PySide6 not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PySide6"])
    from PySide6.QtWidgets import QApplication

from third_party_installer.gui.main_window import ThirdPartyInstallerGUI


def main():
    """Main application entry point."""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Third Party Installer")
    app.setApplicationVersion("1.0.1")
    app.setOrganizationName("SSH Tools")
    app.setApplicationDisplayName("SSH Tools - Third Party Installer")
    
    # Set application icon if available
    try:
        from PySide6.QtGui import QIcon
        from pathlib import Path
        icon_path = Path(__file__).parent / "src" / "third_party_installer" / "resources" / "icon.ico"
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        pass  # Icon not critical
    
    # Create and show main window
    window = ThirdPartyInstallerGUI()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
