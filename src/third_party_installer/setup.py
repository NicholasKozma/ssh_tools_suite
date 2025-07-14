#!/usr/bin/env python3
"""
Post-installation setup script for SSH Tools Suite
This script runs after the package is installed via pip/wheel
"""

import os
import sys
import subprocess
from pathlib import Path


def check_third_party_tools():
    """Check if third-party tools are installed."""
    try:
        from third_party_installer.core.installer import ThirdPartyInstaller
        
        installer = ThirdPartyInstaller()
        return installer.is_installation_complete()
    except ImportError:
        return False


def run_third_party_installer():
    """Run the third-party installer GUI."""
    try:
        # Try to run the installer GUI
        from third_party_installer.gui.main_window import ThirdPartyInstallerGUI
        from PySide6.QtWidgets import QApplication, QMessageBox
        
        # Create application
        app = QApplication(sys.argv)
        app.setApplicationName("Third Party Installer")
        app.setApplicationDisplayName("SSH Tools Suite - Post-Installation Setup")
        
        # Show initial dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("SSH Tools Suite - First Time Setup")
        msg.setText("Welcome to SSH Tools Suite!")
        msg.setInformativeText(
            "This is the first time you're running SSH Tools Suite.\n\n"
            "We need to install some third-party tools that are required "
            "for the SSH Tools Suite to function properly.\n\n"
            "Click 'OK' to open the Third Party Installer."
        )
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        msg.setDefaultButton(QMessageBox.Ok)
        
        if msg.exec() == QMessageBox.Ok:
            # Show the installer
            installer = ThirdPartyInstallerGUI()
            installer.show()
            
            # Run the application
            result = app.exec()
            
            # Check if installation was completed
            if check_third_party_tools():
                print("✅ Third-party tools installation completed successfully!")
                return True
            else:
                print("❌ Third-party tools installation was not completed.")
                print("Some SSH Tools Suite features may not work properly.")
                return False
        else:
            print("❌ Third-party tools installation was cancelled.")
            print("SSH Tools Suite installation is incomplete.")
            return False
            
    except ImportError as e:
        print(f"❌ Could not run third-party installer: {e}")
        print("Please install PySide6: pip install PySide6")
        return False
    except Exception as e:
        print(f"❌ Error running third-party installer: {e}")
        return False


def main():
    """Main setup function."""
    print("🔧 SSH Tools Suite Post-Installation Setup")
    print("=" * 50)
    
    # Check if we're in a GUI environment
    if os.environ.get('DISPLAY') is None and os.name != 'nt':
        print("❌ No GUI environment detected.")
        print("Please run the third-party installer manually:")
        print("python -m third_party_installer")
        return 1
    
    # Check if third-party tools are already installed
    if check_third_party_tools():
        print("✅ All required third-party tools are already installed.")
        return 0
    
    print("⚠️  Some required third-party tools are not installed.")
    print("Starting Third Party Installer...")
    
    # Run the installer
    if run_third_party_installer():
        print("✅ Setup completed successfully!")
        return 0
    else:
        print("❌ Setup was not completed.")
        print("\nYou can run the installer manually later with:")
        print("python -m third_party_installer")
        return 1


if __name__ == "__main__":
    sys.exit(main())
