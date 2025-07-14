#!/usr/bin/env python3
"""
SSH Tunnel Manager - RTSP Handler
Handles RTSP viewer functionality with proper icons
"""

import subprocess
import threading
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QMenu, QMessageBox
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCursor, QPixmap, QIcon
from PySide6.QtCore import Qt

from ...core.models import TunnelConfig


class RTSPHandler:
    """Handles RTSP viewer functionality."""
    
    def __init__(self, parent):
        self.parent = parent
        self.config_manager = None
        self.active_tunnels = None
        self.log = None
    
    def set_managers(self, config_manager, active_tunnels, log_func):
        """Set references to managers and functions."""
        self.config_manager = config_manager
        self.active_tunnels = active_tunnels
        self.log = log_func
    
    def launch_rtsp(self):
        """Launch RTSP viewer with menu selection."""
        config_name = self.parent.table_widget.get_selected_config_name()
        if not config_name:
            QMessageBox.information(self.parent, "No Selection", "Please select a tunnel first.")
            return
        
        # Get the tunnel configuration
        config = self.config_manager.get_configuration(config_name)
        if not config:
            self.log(f"Configuration not found: {config_name}")
            return
        
        # Generate RTSP URL
        if hasattr(config, 'rtsp_url') and config.rtsp_url:
            rtsp_url = config.rtsp_url
        else:
            rtsp_url = f"rtsp://localhost:{config.local_port}/live/0"
        
        self._show_rtsp_menu(rtsp_url, config_name)
    
    def launch_rtsp_by_name(self, config_name: str):
        """Launch RTSP viewer for a specific tunnel by name."""
        config = self.config_manager.get_configuration(config_name)
        if not config:
            self.log(f"Configuration not found: {config_name}")
            return
        
        # Check if tunnel is running
        if config_name not in self.active_tunnels or not self.active_tunnels[config_name].is_running:
            # Ask if user wants to start the tunnel
            reply = QMessageBox.question(
                self.parent, 
                "Tunnel Not Running",
                f"The tunnel '{config_name}' is not running.\n\nWould you like to start it first?",
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Yes:
                self.parent._start_tunnel_by_name(config_name)
                # Give tunnel a moment to start, then show menu
                QTimer.singleShot(2000, lambda: self._show_rtsp_menu_for_config(config))
            elif reply == QMessageBox.No:
                self._show_rtsp_menu_for_config(config)
            # If Cancel, do nothing
        else:
            self._show_rtsp_menu_for_config(config)
    
    def _show_rtsp_menu(self, rtsp_url: str, config_name: str, at_button=True):
        """Show RTSP viewer menu."""
        menu = self._create_rtsp_menu()
        
        # Show menu at RTSP button position or cursor
        if at_button:
            rtsp_button = self.parent.toolbar_manager.buttons.get('rtsp')
            if rtsp_button:
                menu_pos = rtsp_button.mapToGlobal(rtsp_button.rect().bottomLeft())
                action = menu.exec(menu_pos)
            else:
                action = menu.exec()
        else:
            action = menu.exec(QCursor.pos())
        
        # Handle selection
        if action and hasattr(action, 'text'):
            if 'VLC' in action.text():
                self._play_rtsp_with_vlc(rtsp_url, config_name)
            elif 'OpenCV' in action.text():
                self._play_rtsp_with_opencv(rtsp_url, config_name)
    
    def _show_rtsp_menu_for_config(self, config: TunnelConfig):
        """Show RTSP viewer menu for the given configuration."""
        # Generate RTSP URL
        if hasattr(config, 'rtsp_url') and config.rtsp_url:
            rtsp_url = config.rtsp_url
        else:
            rtsp_url = f"rtsp://localhost:{config.local_port}/live/0"
        
        self._show_rtsp_menu(rtsp_url, config.name, at_button=False)
    
    def _create_rtsp_menu(self) -> QMenu:
        """Create RTSP viewer selection menu with proper icons."""
        menu = QMenu(self.parent)
        
        # Load icons from assets directory
        assets_dir = Path(__file__).parent.parent / "assets"
        vlc_icon_path = assets_dir / "vlc_icon.png"
        opencv_icon_path = assets_dir / "open_cv_icon.png"
        
        # VLC option
        vlc_action = menu.addAction("VLC Media Player")
        if vlc_icon_path.exists():
            vlc_pixmap = QPixmap(str(vlc_icon_path))
            if not vlc_pixmap.isNull():
                scaled_pixmap = vlc_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                vlc_action.setIcon(QIcon(scaled_pixmap))
        
        if not self._is_vlc_available():
            vlc_action.setText("VLC Media Player (Not Available)")
            vlc_action.setEnabled(False)
        
        # OpenCV option
        opencv_action = menu.addAction("OpenCV Player")
        if opencv_icon_path.exists():
            opencv_pixmap = QPixmap(str(opencv_icon_path))
            if not opencv_pixmap.isNull():
                scaled_pixmap = opencv_pixmap.scaled(16, 16, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                opencv_action.setIcon(QIcon(scaled_pixmap))
        
        try:
            import cv2
        except ImportError:
            opencv_action.setText("OpenCV Player (Not Available)")
            opencv_action.setEnabled(False)
        
        return menu
    
    def _is_vlc_available(self) -> bool:
        """Check if VLC is available."""
        # Check tools directory first (bundled with application)
        tools_vlc = Path(__file__).parent.parent.parent.parent.parent / "tools" / "vlc" / "vlc.exe"
        if tools_vlc.exists():
            return True
        
        # Check common VLC installation paths
        common_paths = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        
        for path in common_paths:
            if Path(path).exists():
                return True
        
        # Try checking PATH
        try:
            subprocess.run(["vlc", "--version"], capture_output=True, timeout=5, check=True)
            return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def _play_rtsp_with_vlc(self, rtsp_url: str, config_name: str):
        """Play RTSP stream using VLC."""
        try:
            # Find VLC executable
            vlc_path = None
            
            # Check tools directory first (bundled with application)
            tools_vlc = Path(__file__).parent.parent.parent.parent.parent / "tools" / "vlc" / "vlc.exe"
            if tools_vlc.exists():
                vlc_path = str(tools_vlc)
            else:
                # Check common VLC installation paths
                common_paths = [
                    r"C:\Program Files\VideoLAN\VLC\vlc.exe",
                    r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
                ]
                
                for path in common_paths:
                    if Path(path).exists():
                        vlc_path = path
                        break
                
                if not vlc_path:
                    # Try checking PATH
                    try:
                        subprocess.run(["vlc", "--version"], capture_output=True, timeout=5, check=True)
                        vlc_path = "vlc"  # Available in PATH
                    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                        pass
            
            if not vlc_path:
                QMessageBox.warning(self.parent, "VLC Not Available", 
                                   "VLC is not installed or not found. Please install VLC Media Player.")
                return
            
            # Launch VLC with the RTSP URL
            subprocess.Popen([
                vlc_path,
                rtsp_url,
                "--intf", "qt",  # Use Qt interface
                "--qt-start-minimized",
                "--no-video-title-show"
            ])
            
            self.log(f"VLC launched for {config_name}: {rtsp_url}")
            
        except Exception as e:
            self.log(f"Error launching VLC: {e}")
            QMessageBox.critical(self.parent, "VLC Error", f"Error launching VLC:\n{str(e)}")
    
    def _play_rtsp_with_opencv(self, rtsp_url: str, config_name: str):
        """Play RTSP stream using OpenCV."""
        try:
            import cv2
            import os
            
            self.log(f"Opening OpenCV stream for {config_name}: {rtsp_url}")
            
            # Set FFmpeg path for OpenCV if available
            ffmpeg_path = Path("C:\\ffmpeg\\bin\\ffmpeg.exe")
            if ffmpeg_path.exists():
                # Set environment variable for OpenCV to find FFmpeg
                os.environ['OPENCV_FFMPEG_BINARY'] = str(ffmpeg_path)
                self.log(f"Using FFmpeg at: {ffmpeg_path}")
            
            # Try multiple backend options
            backends_to_try = []
            if ffmpeg_path.exists():
                backends_to_try.append(('FFmpeg', cv2.CAP_FFMPEG))
            backends_to_try.extend([
                ('DirectShow', cv2.CAP_DSHOW),
                ('OpenCV Default', cv2.CAP_ANY)
            ])
            
            cap = None
            backend_used = None
            
            for backend_name, backend_id in backends_to_try:
                try:
                    self.log(f"Trying {backend_name} backend...")
                    test_cap = cv2.VideoCapture(rtsp_url, backend_id)
                    
                    # Test if we can actually read a frame
                    if test_cap.isOpened():
                        ret, frame = test_cap.read()
                        if ret and frame is not None:
                            cap = test_cap
                            backend_used = backend_name
                            self.log(f"Successfully connected using {backend_name}")
                            break
                        else:
                            self.log(f"{backend_name} opened but can't read frames")
                            test_cap.release()
                    else:
                        self.log(f"{backend_name} failed to open")
                        test_cap.release()
                except Exception as e:
                    self.log(f"{backend_name} error: {e}")
                    try:
                        test_cap.release()
                    except:
                        pass
            
            if cap is None:
                error_msg = f"Failed to connect to RTSP stream with any backend.\n\nURL: {rtsp_url}\n\nTroubleshooting:\n1. Check if the tunnel is running\n2. Verify the RTSP server is broadcasting\n3. Try with VLC first to test the stream"
                self.log(f"No working backend found for RTSP stream")
                QMessageBox.warning(self.parent, "Connection Failed", error_msg)
                return
            
            self.log(f"Stream opened with {backend_used} - Press 'q' in video window to quit")
            
            # Read and display frames in a separate thread to avoid blocking the main UI
            def play_stream():
                window_name = f"RTSP Stream - {config_name} ({backend_used})"
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 800, 600)
                
                frame_count = 0
                error_count = 0
                max_errors = 10
                
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        error_count += 1
                        self.log(f"Frame read failed (error {error_count}/{max_errors})")
                        if error_count >= max_errors:
                            self.log(f"Too many read errors, stopping stream")
                            break
                        continue
                    
                    # Reset error count on successful read
                    error_count = 0
                    frame_count += 1
                    
                    # Display the frame (no overlay text as requested in earlier conversation)
                    cv2.imshow(window_name, frame)
                    
                    # Check for 'q' key press to quit
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                
                # Clean up
                cap.release()
                cv2.destroyAllWindows()
                self.log(f"Stream closed for {config_name} (showed {frame_count} frames)")
            
            # Run in a separate thread to avoid blocking the UI
            stream_thread = threading.Thread(target=play_stream, daemon=True)
            stream_thread.start()
            
        except ImportError:
            QMessageBox.warning(self.parent, "OpenCV Not Available", 
                               "OpenCV is not installed. Install with: pip install opencv-python")
            return
        except Exception as e:
            self.log(f"Error with OpenCV stream: {e}")
            QMessageBox.critical(self.parent, "Stream Error", f"Error playing stream:\n{str(e)}")
