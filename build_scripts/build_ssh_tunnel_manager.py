#!/usr/bin/env python3
"""
Build script for SSH Tunnel Manager GUI executable using PyInstaller
"""

import os
import sys
import shutil
from pathlib import Path
import PyInstaller.__main__

def build_ssh_tunnel_manager():
    """Build SSH Tunnel Manager GUI executable"""
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    # Create dist directory if it doesn't exist
    dist_dir = project_root / "dist" / "executables"
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # PyInstaller arguments
    args = [
        '--name=SSH-Tunnel-Manager-GUI',
        '--onefile',
        '--windowed',  # Hide console on Windows
        '--icon=src/ssh_tunnel_manager/gui/assets/vlc_icon.png' if (src_dir / "ssh_tunnel_manager" / "gui" / "assets" / "vlc_icon.png").exists() else '',
        '--add-data=src/ssh_tunnel_manager/gui/assets;ssh_tunnel_manager/gui/assets',
        '--hidden-import=PySide6',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=ssh_tunnel_manager',
        '--hidden-import=ssh_tunnel_manager.gui',
        '--hidden-import=ssh_tunnel_manager.core',
        '--hidden-import=ssh_tools_common',
        '--distpath=dist/executables',
        '--workpath=build/temp',
        '--specpath=build/specs',
        'src/ssh_tunnel_manager/gui/__main__.py'
    ]
    
    # Remove empty icon argument if no icon exists
    args = [arg for arg in args if arg]
    
    print("Building SSH Tunnel Manager GUI executable...")
    print(f"Arguments: {args}")
    
    # Change to project root
    os.chdir(project_root)
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print(f"Build complete! Executable created in: {dist_dir}")
    
    # List created files
    if dist_dir.exists():
        print("\nCreated files:")
        for file in dist_dir.iterdir():
            print(f"  - {file.name} ({file.stat().st_size / 1024 / 1024:.1f} MB)")

def build_ssh_tools_installer():
    """Build SSH Tools Installer executable"""
    
    # Get project root directory
    project_root = Path(__file__).parent.parent
    
    # PyInstaller arguments
    args = [
        '--name=SSH-Tools-Installer',
        '--onefile',
        '--windowed',
        '--hidden-import=third_party_installer',
        '--hidden-import=third_party_installer.gui',
        '--hidden-import=third_party_installer.core',
        '--hidden-import=ssh_tools_common',
        '--distpath=dist/executables',
        '--workpath=build/temp',
        '--specpath=build/specs',
        'src/third_party_installer/gui/main_window.py'
    ]
    
    print("Building SSH Tools Installer executable...")
    
    # Change to project root
    os.chdir(project_root)
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build_ssh_tunnel_manager()
    build_ssh_tools_installer()
