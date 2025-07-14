#!/usr/bin/env python3
"""
SSH Tunnel Manager - RTSP Viewer Dialog
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QComboBox, QLineEdit, QPushButton, QListWidget, QLabel,
    QMessageBox, QTextEdit, QSplitter
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap, QIcon

from ...core.models import TunnelConfig


class VLCViewer:
    """VLC-based RTSP viewer."""
    
    def __init__(self):
        self.vlc_path = self._find_vlc()
    
    def _find_vlc(self) -> Optional[str]:
        """Find VLC executable."""
        # Check tools directory first (bundled with application)
        tools_vlc = Path(__file__).parent.parent.parent.parent.parent / "tools" / "vlc" / "vlc.exe"
        if tools_vlc.exists():
            return str(tools_vlc)
        
        # Check common VLC installation paths
        common_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return path
        
        # Try checking PATH
        try:
            subprocess.run(["vlc", "--version"], capture_output=True, timeout=5, check=True)
            return "vlc"  # Available in PATH
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return None
    
    def is_available(self) -> bool:
        """Check if VLC is available."""
        return self.vlc_path is not None
    
    def play_stream(self, rtsp_url: str) -> bool:
        """Play RTSP stream using VLC."""
        if not self.is_available():
            return False
        
        try:
            # Launch VLC with the RTSP URL
            subprocess.Popen([
                self.vlc_path,
                rtsp_url,
                "--intf", "qt",  # Use Qt interface
                "--qt-start-minimized",
                "--no-video-title-show"
            ])
            return True
        except Exception as e:
            print(f"Error launching VLC: {e}")
            return False


class RTSPViewerDialog(QDialog):
    """Simple dialog for choosing RTSP viewer and playing a stream."""
    
    def __init__(self, tunnel_config: Optional[TunnelConfig] = None, parent=None):
        super().__init__(parent)
        self.tunnel_config = tunnel_config
        self.vlc_viewer = VLCViewer()
        
        self.setWindowTitle("RTSP Stream Viewer")
        self.setGeometry(200, 200, 400, 250)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Choose RTSP Viewer")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # RTSP URL display/edit
        url_group = QGroupBox("RTSP Stream URL")
        url_layout = QVBoxLayout(url_group)
        
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("rtsp://localhost:8554/live/0")
        
        # Set URL from tunnel config
        if self.tunnel_config:
            if hasattr(self.tunnel_config, 'rtsp_url') and self.tunnel_config.rtsp_url:
                self.url_edit.setText(self.tunnel_config.rtsp_url)
            else:
                # Generate default URL
                default_url = f"rtsp://localhost:{self.tunnel_config.local_port}/live/0"
                self.url_edit.setText(default_url)
        
        url_layout.addWidget(self.url_edit)
        layout.addWidget(url_group)
        
        # Viewer selection
        viewer_group = QGroupBox("Select Viewer")
        viewer_layout = QVBoxLayout(viewer_group)
        
        # Load icons from assets directory
        assets_dir = Path(__file__).parent.parent / "assets"
        vlc_icon_path = assets_dir / "vlc_icon.png"
        opencv_icon_path = assets_dir / "open_cv_icon.png"
        
        # Create VLC button with icon
        self.vlc_btn = QPushButton("VLC Media Player")
        if vlc_icon_path.exists():
            vlc_pixmap = QPixmap(str(vlc_icon_path))
            if not vlc_pixmap.isNull():
                # Scale icon to a reasonable size (32x32)
                scaled_pixmap = vlc_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                vlc_icon = QIcon(scaled_pixmap)
                self.vlc_btn.setIcon(vlc_icon)
                self.vlc_btn.setIconSize(scaled_pixmap.size())
        
        # Create OpenCV button with icon
        self.opencv_btn = QPushButton("OpenCV Player")
        if opencv_icon_path.exists():
            opencv_pixmap = QPixmap(str(opencv_icon_path))
            if not opencv_pixmap.isNull():
                # Scale icon to a reasonable size (32x32)
                scaled_pixmap = opencv_pixmap.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                opencv_icon = QIcon(scaled_pixmap)
                self.opencv_btn.setIcon(opencv_icon)
                self.opencv_btn.setIconSize(scaled_pixmap.size())
        
        # Check availability and update buttons
        if not self.vlc_viewer.is_available():
            self.vlc_btn.setText("VLC Media Player (Not Available)")
            self.vlc_btn.setEnabled(False)
            self.vlc_btn.setToolTip("VLC is not installed or not found. Please install VLC Media Player.")
        else:
            self.vlc_btn.setToolTip("Play RTSP stream using VLC Media Player")
        
        try:
            import cv2
            self.opencv_btn.setToolTip("Play RTSP stream using OpenCV (Python)")
        except ImportError:
            self.opencv_btn.setText("OpenCV Player (Not Available)")
            self.opencv_btn.setEnabled(False)
            self.opencv_btn.setToolTip("OpenCV is not installed. Install with: pip install opencv-python")
        
        self.vlc_btn.clicked.connect(self._play_with_vlc)
        self.opencv_btn.clicked.connect(self._play_with_opencv)
        
        viewer_layout.addWidget(self.vlc_btn)
        viewer_layout.addWidget(self.opencv_btn)
        layout.addWidget(viewer_group)
        
        # Status
        self.status_label = QLabel("Ready to play RTSP stream")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    
    def _play_with_vlc(self):
        """Play stream with VLC."""
        rtsp_url = self.url_edit.text().strip()
        if not rtsp_url:
            QMessageBox.warning(self, "No URL", "Please enter an RTSP URL.")
            return
        
        if not self.vlc_viewer.is_available():
            QMessageBox.warning(self, "VLC Not Available", 
                               "VLC is not installed or not found. Please install VLC Media Player.")
            return
        
        self.status_label.setText("Launching VLC...")
        success = self.vlc_viewer.play_stream(rtsp_url)
        if success:
            self.status_label.setText("VLC launched successfully")
        else:
            self.status_label.setText("Failed to launch VLC")
    
    def _play_with_opencv(self):
        """Play stream with OpenCV."""
        rtsp_url = self.url_edit.text().strip()
        if not rtsp_url:
            QMessageBox.warning(self, "No URL", "Please enter an RTSP URL.")
            return
        
        try:
            import cv2
        except ImportError:
            QMessageBox.warning(self, "OpenCV Not Available", 
                               "OpenCV is not installed. Install with: pip install opencv-python")
            return
        
        self.status_label.setText("Opening stream with OpenCV...")
        self._open_opencv_stream(rtsp_url)
    
    def _open_opencv_stream(self, rtsp_url: str):
        """Open RTSP stream using OpenCV in a simple window."""
        try:
            import cv2
            import os
            
            # Set FFmpeg path for OpenCV if available
            ffmpeg_path = Path("C:\\ffmpeg\\bin\\ffmpeg.exe")
            if ffmpeg_path.exists():
                # Set environment variable for OpenCV to find FFmpeg
                os.environ['OPENCV_FFMPEG_BINARY'] = str(ffmpeg_path)
                # Try to use FFmpeg backend explicitly
                try:
                    cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)
                except:
                    # Fallback to default if FFmpeg backend fails
                    cap = cv2.VideoCapture(rtsp_url)
            else:
                # Create video capture object with default backend
                cap = cv2.VideoCapture(rtsp_url)
            
            if not cap.isOpened():
                self.status_label.setText("Failed to connect to RTSP stream")
                QMessageBox.warning(self, "Connection Failed", f"Could not connect to RTSP stream:\n{rtsp_url}")
                return
            
            self.status_label.setText("Stream opened - Press 'q' in video window to quit")
            
            # Read and display frames
            window_name = f"RTSP Stream - {rtsp_url}"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Display the frame
                cv2.imshow(window_name, frame)
                
                # Check for 'q' key press to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            # Clean up
            cap.release()
            cv2.destroyAllWindows()
            self.status_label.setText("Stream closed")
            
        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            QMessageBox.critical(self, "Stream Error", f"Error playing stream:\n{str(e)}")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        event.accept()
