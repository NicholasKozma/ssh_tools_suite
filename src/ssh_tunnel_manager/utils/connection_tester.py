#!/usr/bin/env python3
"""
SSH Tunnel Manager - Connection Testing Utilities
"""

import socket
import urllib.request
import urllib.error
from typing import Optional

from ..core.models import TunnelConfig
from ..core.constants import HTTP_PORTS, HTTPS_PORTS, RTSP_PORTS


class ConnectionTester:
    """Utilities for testing tunnel connections."""
    
    @staticmethod
    def test_local_port(port: int, host: str = "localhost", timeout: int = 2) -> bool:
        """Test if a local port is accessible."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    @staticmethod
    def test_tunnel_connection(config: TunnelConfig) -> tuple[bool, str]:
        """Test the actual tunnel connection."""
        try:
            if not ConnectionTester.test_local_port(config.local_port):
                return False, f"Local port {config.local_port} is not accessible"
            
            # Test based on service type
            if config.remote_port in RTSP_PORTS:
                success, message = ConnectionTester._test_rtsp_service(config.local_port)
            elif config.remote_port in HTTP_PORTS + HTTPS_PORTS:
                success, message = ConnectionTester._test_http_service(config.local_port)
            else:
                # Generic port test
                success = True
                message = f"Port {config.local_port} is accessible"
            
            return success, message
            
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    @staticmethod
    def _test_rtsp_service(local_port: int) -> tuple[bool, str]:
        """Test RTSP service connectivity."""
        try:
            # RTSP uses TCP initially
            if ConnectionTester.test_local_port(local_port, timeout=3):
                rtsp_url = f"rtsp://localhost:{local_port}/live/0"
                return True, f"RTSP service responding. Try: {rtsp_url}"
            return False, "RTSP service not responding"
            
        except Exception as e:
            return False, f"RTSP test failed: {str(e)}"
    
    @staticmethod
    def _test_http_service(local_port: int) -> tuple[bool, str]:
        """Test HTTP service connectivity."""
        try:
            # Try HTTP first, then HTTPS
            for protocol in ['http', 'https']:
                try:
                    url = f"{protocol}://localhost:{local_port}"
                    req = urllib.request.Request(url)
                    req.add_header('User-Agent', 'SSH-Tunnel-Tester/1.0')
                    
                    with urllib.request.urlopen(req, timeout=3) as response:
                        return True, f"{protocol.upper()} service responding: {url}"
                        
                except urllib.error.HTTPError as e:
                    # Even HTTP errors mean the service is responding
                    if e.code in [200, 301, 302, 401, 403, 404]:
                        return True, f"{protocol.upper()} service responding (HTTP {e.code}): {url}"
                except:
                    continue
                    
            return False, "HTTP/HTTPS service not responding"
            
        except Exception as e:
            return False, f"HTTP test failed: {str(e)}"
    
    @staticmethod
    def get_service_urls(config: TunnelConfig) -> list[str]:
        """Get potential service URLs for a tunnel."""
        if config.tunnel_type != 'local':
            return []
        
        urls = []
        port = config.local_port
        
        # RTSP URLs
        if config.remote_port in RTSP_PORTS:
            urls.extend([
                f"rtsp://localhost:{port}/live/0",
                f"rtsp://localhost:{port}/stream",
                f"rtsp://localhost:{port}/",
            ])
        
        # HTTP URLs
        if config.remote_port in HTTP_PORTS:
            urls.append(f"http://localhost:{port}")
        
        # HTTPS URLs
        if config.remote_port in HTTPS_PORTS:
            urls.append(f"https://localhost:{port}")
        
        # Generic URL for other services
        if not urls:
            if config.remote_port in [80, 8080, 3000, 5000, 8000, 9000]:
                urls.append(f"http://localhost:{port}")
            elif config.remote_port in [443, 8443]:
                urls.append(f"https://localhost:{port}")
        
        return urls
    
    @staticmethod
    def test_ssh_connectivity(host: str, port: int = 22, timeout: int = 5) -> tuple[bool, str]:
        """Test basic SSH connectivity (port 22)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                return True, f"SSH port {port} is accessible on {host}"
            else:
                return False, f"Cannot connect to SSH port {port} on {host}"
                
        except socket.gaierror:
            return False, f"Cannot resolve hostname: {host}"
        except Exception as e:
            return False, f"SSH connectivity test failed: {str(e)}"
