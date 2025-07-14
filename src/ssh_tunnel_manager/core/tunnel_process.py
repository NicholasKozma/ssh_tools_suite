#!/usr/bin/env python3
"""
SSH Tunnel Manager - SSH Process Management
"""

import os
import sys
import time
import subprocess
from typing import Optional

from .models import TunnelConfig
from .constants import PROCESS_START_DELAY, PROCESS_ESTABLISH_DELAY


class TunnelProcess:
    """Manages an SSH tunnel process."""
    
    # Status constants
    STATUS_STOPPED = "stopped"
    STATUS_STARTING = "starting"
    STATUS_RUNNING = "running"
    STATUS_ERROR = "error"
    
    def __init__(self, config: TunnelConfig, terminal_widget=None):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.status = self.STATUS_STOPPED
        self.terminal_widget = terminal_widget
        self.connection_lost_count = 0  # Track connection lost messages
        
    def start(self) -> bool:
        """Start the SSH tunnel in a native terminal window."""
        if self.is_running:
            return True
            
        try:
            # Set status to starting and reset connection lost counter
            self.status = self.STATUS_STARTING
            self.connection_lost_count = 0
            
            cmd = self.config.get_ssh_command_args()
            
            # Always start in native terminal window for password entry
            self.process = self._start_native_terminal_process(cmd)
                
            # Give SSH time to establish the tunnel
            time.sleep(PROCESS_ESTABLISH_DELAY)
            
            # Check if process is still running (but don't mark as fully running yet)
            if hasattr(self.process, 'poll'):  # subprocess.Popen
                if self.process.poll() is None:
                    # Process is running, but keep in STARTING state until health check passes
                    # The monitor thread will transition it to RUNNING when it's actually connected
                    return True
                else:
                    return_code = self.process.returncode
                    error_message = self._get_error_message(return_code)
                    self.status = self.STATUS_ERROR
                    raise Exception(error_message)
            else:
                self.status = self.STATUS_ERROR
                raise Exception("Unknown process type")
                
        except Exception as e:
            self.is_running = False
            self.status = self.STATUS_ERROR
            raise e

    def _start_native_terminal_process(self, cmd: list[str]) -> subprocess.Popen:
        """Start SSH process in a native terminal window for user password entry."""
        if sys.platform == "win32":
            # Windows: Create new console window with descriptive title
            console_title = f"SSH Tunnel: {self.config.name} - KEEP OPEN TO MAINTAIN TUNNEL"
            startup_info = subprocess.STARTUPINFO()
            startup_info.lpTitle = console_title
            
            # Add a warning message to the command
            warning_cmd = [
                'cmd', '/c', 
                f'title {console_title} && '
                f'echo. && '
                f'echo ============================================= && '
                f'echo SSH TUNNEL: {self.config.name} && '
                f'echo ============================================= && '
                f'echo IMPORTANT: Keep this window open to maintain && '
                f'echo the SSH tunnel connection. Closing this && '
                f'echo window will terminate the tunnel. && '
                f'echo. && '
                f'echo Connecting to: {self.config.ssh_user}@{self.config.ssh_host}:{self.config.ssh_port} && '
                f'echo Local port: {self.config.local_port} && '
                f'echo Remote: {self.config.remote_host}:{self.config.remote_port} && '
                f'echo. && '
                f'{" ".join(cmd)}'
            ]
            
            return subprocess.Popen(
                warning_cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                startupinfo=startup_info
            )
        else:
            # Linux/Mac: Try to launch in common terminal emulators
            warning_msg = f'''
echo "============================================="
echo "SSH TUNNEL: {self.config.name}"
echo "============================================="
echo "IMPORTANT: Keep this terminal open to maintain"
echo "the SSH tunnel connection. Closing this"
echo "terminal will terminate the tunnel."
echo ""
echo "Connecting to: {self.config.ssh_user}@{self.config.ssh_host}:{self.config.ssh_port}"
echo "Local port: {self.config.local_port}"
echo "Remote: {self.config.remote_host}:{self.config.remote_port}"
echo ""
{' '.join(cmd)}
read -p "Press Enter to close..."
'''
            
            terminal_commands = [
                ['gnome-terminal', '--title', f'SSH Tunnel: {self.config.name}', '--', 'sh', '-c', warning_msg],
                ['xterm', '-title', f'SSH Tunnel: {self.config.name}', '-e', 'sh', '-c', warning_msg],
                ['konsole', '--title', f'SSH Tunnel: {self.config.name}', '-e', 'sh', '-c', warning_msg],
                ['mate-terminal', '--title', f'SSH Tunnel: {self.config.name}', '-e', f'sh -c "{warning_msg}"'],
            ]
            
            # Try each terminal emulator until one works
            for terminal_cmd in terminal_commands:
                try:
                    return subprocess.Popen(terminal_cmd)
                except FileNotFoundError:
                    continue
            
            # Fallback: run directly in current terminal (not ideal but works)
            return subprocess.Popen(cmd)

    def _get_error_message(self, return_code: int) -> str:
        """Get error message based on SSH return code."""
        error_messages = {
            255: "SSH connection failed - most likely authentication failure, network issue, or server unreachable",
            1: "SSH connection failed - check host/port configuration",
            130: "SSH connection interrupted by user",
            2: "SSH protocol error or invalid command line arguments",
            65: "Host key verification failed",
            67: "Authentication method not supported"
        }
        
        base_message = error_messages.get(
            return_code, 
            f"SSH tunnel failed to start (exit code: {return_code})"
        )
        
        # Add specific guidance for common issues
        if return_code == 255:
            base_message += "\n\nTroubleshooting steps:"
            base_message += "\n1. Verify SSH server is reachable: ssh user@host"
            base_message += "\n2. Check username and password are correct"
            base_message += "\n3. Ensure SSH server allows password authentication"
            base_message += "\n4. Verify network connectivity and firewall settings"
        
        return base_message
    
    def stop(self):
        """Stop the SSH tunnel."""
        if not self.process or not self.is_running:
            return
            
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
        except Exception:
            # Force kill if graceful termination fails
            try:
                self.process.kill()
                self.process.wait()
            except:
                pass
        finally:
            self.is_running = False
            self.status = self.STATUS_STOPPED
            self.connection_lost_count = 0  # Reset counter when manually stopped
            self.process = None
    
    def is_alive(self) -> bool:
        """Check if the tunnel process is alive."""
        if not self.process:
            self.is_running = False
            self.status = self.STATUS_STOPPED
            return False
        
        poll_result = self.process.poll()
        if poll_result is not None:
            self.is_running = False
            self.status = self.STATUS_STOPPED
            return False
        
        return True
    
    def get_status(self) -> str:
        """Get human-readable status."""
        if self.status == self.STATUS_STARTING:
            return "🟡 Starting"
        elif self.status == self.STATUS_RUNNING and self.is_alive():
            return "🟢 Running"
        elif self.status == self.STATUS_ERROR:
            return "🔴 Error"
        else:
            return "🔴 Stopped"
    
    def health_check(self) -> bool:
        """Perform a health check to see if the tunnel is actually working."""
        if not self.process or self.process.poll() is not None:
            return False
        
        # For local tunnels, try to connect to the local port
        if self.config.tunnel_type == 'local':
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)  # 2 second timeout
                result = sock.connect_ex(('localhost', self.config.local_port))
                sock.close()
                return result == 0
            except Exception:
                return False
        
        # For dynamic tunnels (SOCKS), try to bind to the port
        elif self.config.tunnel_type == 'dynamic':
            import socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', self.config.local_port))
                sock.close()
                return result == 0
            except Exception:
                return False
        
        # For remote tunnels, we can only check if the process is running
        else:
            return True
    
    def transition_to_running_if_healthy(self):
        """Transition from STARTING to RUNNING if health check passes."""
        if self.status == self.STATUS_STARTING and self.health_check():
            self.status = self.STATUS_RUNNING
            self.is_running = True
            return True
        return False
