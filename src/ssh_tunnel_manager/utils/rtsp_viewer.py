"""
RTSP stream viewer utilities for SSH Tunnel Manager.
Provides OpenCV-based RTSP stream viewing through SSH tunnels.
"""

try:
    import cv2
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None

import sys
import time
import socket
import threading
import logging
from typing import List, Dict, Optional, Callable, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RTSPViewer:
    """OpenCV-based RTSP stream viewer for tunneled connections."""
    
    def __init__(self):
        """Initialize RTSP viewer."""
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available. RTSP viewing functionality disabled.")
            logger.info("Install OpenCV with: pip install opencv-python")
        
        self.active_streams = {}
        self.running = False
        
    def detect_active_tunnels(self) -> List[int]:
        """
        Detect active SSH tunnels by checking common RTSP ports.
        
        Returns:
            List of accessible RTSP ports
        """
        active_ports = []
        common_rtsp_ports = [554, 8554, 1935, 8080, 8888, 9554]
        
        for port in common_rtsp_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    active_ports.append(port)
                    logger.info(f"Detected active tunnel on port {port}")
            except Exception:
                continue
        
        return active_ports
    
    def construct_rtsp_url(self, port: int, path: str = "", username: str = "", password: str = "") -> str:
        """
        Construct RTSP URL for local tunnel connection.
        
        Args:
            port: Local port number
            path: RTSP path (optional)
            username: RTSP username (optional) 
            password: RTSP password (optional)
            
        Returns:
            Formatted RTSP URL
        """
        if username and password:
            auth = f"{username}:{password}@"
        else:
            auth = ""
        
        if path and not path.startswith('/'):
            path = '/' + path
        
        return f"rtsp://{auth}localhost:{port}{path}"
    
    def test_rtsp_connection(self, rtsp_url: str, timeout: int = 10) -> bool:
        """
        Test RTSP connection without opening viewer.
        
        Args:
            rtsp_url: RTSP URL to test
            timeout: Connection timeout in seconds
            
        Returns:
            True if connection successful
        """
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV not available. Cannot test RTSP connection.")
            return False
            
        try:
            logger.info(f"Testing RTSP connection: {rtsp_url}")
            
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_TIMEOUT, timeout * 1000)  # OpenCV timeout in milliseconds
            
            if cap.isOpened():
                ret, frame = cap.read()
                cap.release()
                
                if ret and frame is not None:
                    logger.info("✅ RTSP connection test successful")
                    return True
                else:
                    logger.warning("❌ RTSP connection opened but no frame received")
                    return False
            else:
                logger.warning("❌ RTSP connection failed to open")
                return False
                
        except Exception as e:
            logger.error(f"RTSP connection test error: {e}")
            return False
    
    def view_rtsp_stream(self, rtsp_url: str, window_name: str = "RTSP Stream", 
                        save_frames: bool = False, frame_callback: Optional[Callable] = None) -> bool:
        """
        View RTSP stream in OpenCV window.
        
        Args:
            rtsp_url: RTSP URL to view
            window_name: OpenCV window name
            save_frames: Whether to save frames to disk
            frame_callback: Optional callback function for each frame
            
        Returns:
            True if streaming was successful
        """
        if not OPENCV_AVAILABLE:
            logger.error("OpenCV not available. Cannot view RTSP stream.")
            logger.info("Install OpenCV with: pip install opencv-python")
            return False
            
        try:
            logger.info(f"Opening RTSP stream: {rtsp_url}")
            
            cap = cv2.VideoCapture(rtsp_url)
            
            if not cap.isOpened():
                logger.error("Failed to open RTSP stream")
                return False
            
            # Get stream properties
            fps = cap.get(cv2.CAP_PROP_FPS) or 30
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            logger.info(f"Stream properties: {width}x{height} @ {fps} FPS")
            
            # Create window
            cv2.namedWindow(window_name, cv2.WINDOW_RESIZABLE)
            
            frame_count = 0
            start_time = time.time()
            
            while True:
                ret, frame = cap.read()
                
                if not ret:
                    logger.warning("Failed to read frame from RTSP stream")
                    break
                
                frame_count += 1
                
                # Call frame callback if provided
                if frame_callback:
                    try:
                        frame_callback(frame, frame_count)
                    except Exception as e:
                        logger.error(f"Frame callback error: {e}")
                
                # Save frame if requested
                if save_frames and frame_count % 30 == 0:  # Save every 30th frame
                    self.save_frame(frame, frame_count)
                
                # Display frame
                cv2.imshow(window_name, frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    logger.info("User requested quit")
                    break
                elif key == ord('s'):
                    self.save_frame(frame, frame_count)
                    logger.info(f"Saved frame {frame_count}")
                elif key == ord('f'):
                    # Toggle fullscreen
                    if cv2.getWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN) == cv2.WINDOW_FULLSCREEN:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                    else:
                        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            
            # Cleanup
            cap.release()
            cv2.destroyAllWindows()
            
            logger.info(f"RTSP viewing session completed. Total frames: {frame_count}")
            return True
            
        except Exception as e:
            logger.error(f"RTSP viewing error: {e}")
            return False
    
    def save_frame(self, frame: Any, frame_number: int, output_dir: str = "rtsp_frames") -> bool:
        """
        Save a frame to disk.
        
        Args:
            frame: OpenCV frame to save
            frame_number: Frame number for filename
            output_dir: Output directory
            
        Returns:
            True if save successful
        """
        try:
            # Create output directory if it doesn't exist
            Path(output_dir).mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"frame_{frame_number:06d}_{timestamp}.jpg"
            filepath = Path(output_dir) / filename
            
            # Save frame
            success = cv2.imwrite(str(filepath), frame)
            
            if success:
                logger.info(f"Saved frame to: {filepath}")
                return True
            else:
                logger.error(f"Failed to save frame: {filepath}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving frame: {e}")
            return False
    
    def view_multiple_streams(self, rtsp_urls: List[str]) -> bool:
        """
        View multiple RTSP streams in separate windows.
        
        Args:
            rtsp_urls: List of RTSP URLs to view
            
        Returns:
            True if all streams opened successfully
        """
        if not rtsp_urls:
            logger.warning("No RTSP URLs provided")
            return False
        
        threads = []
        success_count = 0
        
        for i, url in enumerate(rtsp_urls):
            window_name = f"RTSP Stream {i+1}"
            
            # Create thread for each stream
            thread = threading.Thread(
                target=self.view_rtsp_stream,
                args=(url, window_name),
                daemon=True
            )
            threads.append(thread)
            thread.start()
            
            # Brief delay between starting streams
            time.sleep(0.5)
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        return success_count == len(rtsp_urls)
    
    def get_stream_info(self, rtsp_url: str) -> Dict[str, any]:
        """
        Get information about an RTSP stream.
        
        Args:
            rtsp_url: RTSP URL to analyze
            
        Returns:
            Dictionary with stream information
        """
        info = {
            'url': rtsp_url,
            'accessible': False,
            'properties': {}
        }
        
        try:
            cap = cv2.VideoCapture(rtsp_url)
            
            if cap.isOpened():
                info['accessible'] = True
                
                # Get stream properties
                properties = {
                    'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                    'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                    'fps': cap.get(cv2.CAP_PROP_FPS),
                    'codec': int(cap.get(cv2.CAP_PROP_FOURCC)),
                    'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                }
                
                info['properties'] = properties
                
                # Try to read a frame to verify stream is working
                ret, frame = cap.read()
                info['frame_readable'] = ret and frame is not None
                
            cap.release()
            
        except Exception as e:
            info['error'] = str(e)
            logger.error(f"Error getting stream info: {e}")
        
        return info


class RTSPTunnelHelper:
    """Helper class for RTSP streaming through SSH tunnels."""
    
    @staticmethod
    def generate_rtsp_urls_for_tunnels(active_ports: List[int], 
                                     common_paths: List[str] = None) -> List[str]:
        """
        Generate common RTSP URL variations for active tunnel ports.
        
        Args:
            active_ports: List of active tunnel ports
            common_paths: List of common RTSP paths to try
            
        Returns:
            List of RTSP URLs to test
        """
        if common_paths is None:
            common_paths = [
                "",  # Root path
                "/stream",
                "/live",
                "/video",
                "/cam1",
                "/camera1",
                "/rtsp",
                "/media"
            ]
        
        rtsp_urls = []
        
        for port in active_ports:
            for path in common_paths:
                url = f"rtsp://localhost:{port}{path}"
                rtsp_urls.append(url)
        
        return rtsp_urls
    
    @staticmethod
    def find_working_rtsp_streams(active_ports: List[int]) -> List[Dict[str, any]]:
        """
        Test multiple RTSP URLs and return working ones.
        
        Args:
            active_ports: List of active tunnel ports
            
        Returns:
            List of working stream information
        """
        viewer = RTSPViewer()
        urls_to_test = RTSPTunnelHelper.generate_rtsp_urls_for_tunnels(active_ports)
        
        working_streams = []
        
        for url in urls_to_test:
            logger.info(f"Testing RTSP URL: {url}")
            
            if viewer.test_rtsp_connection(url, timeout=5):
                stream_info = viewer.get_stream_info(url)
                working_streams.append(stream_info)
                logger.info(f"✅ Working stream found: {url}")
            else:
                logger.debug(f"❌ Stream not working: {url}")
        
        return working_streams
