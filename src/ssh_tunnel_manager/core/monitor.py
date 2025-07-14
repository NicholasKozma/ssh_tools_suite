#!/usr/bin/env python3
"""
SSH Tunnel Manager - Monitor Thread
"""

import time
from typing import Dict

from PySide6.QtCore import QThread, Signal

from .tunnel_process import TunnelProcess
from .constants import MONITOR_INTERVAL


class TunnelMonitorThread(QThread):
    """Background thread to monitor tunnel status."""
    
    status_update = Signal(str, bool)  # tunnel_name, is_running
    connection_lost = Signal(str)  # tunnel_name when connection is lost
    
    def __init__(self, active_tunnels: Dict[str, TunnelProcess]):
        super().__init__()
        self.active_tunnels = active_tunnels
        self.running = True
    
    def run(self):
        """Main monitoring loop."""
        while self.running:
            for name, tunnel_process in self.active_tunnels.items():
                try:
                    # Check if the process is alive
                    if hasattr(tunnel_process, 'is_alive'):
                        is_alive = tunnel_process.is_alive()
                    else:
                        is_alive = tunnel_process.is_running
                    
                    # If tunnel is in STARTING state, try to transition to RUNNING
                    if (tunnel_process.status == tunnel_process.STATUS_STARTING and 
                        hasattr(tunnel_process, 'transition_to_running_if_healthy')):
                        if tunnel_process.transition_to_running_if_healthy():
                            self.status_update.emit(name, True)
                            continue
                    
                    # Handle connection lost scenarios
                    was_running = tunnel_process.is_running
                    current_running = is_alive and (tunnel_process.status == tunnel_process.STATUS_RUNNING)
                    
                    if was_running and not current_running:
                        # Connection was lost
                        if tunnel_process.connection_lost_count < 10:  # Limit to 10 messages
                            tunnel_process.connection_lost_count += 1
                            self.connection_lost.emit(name)
                    
                    self.status_update.emit(name, current_running)
                    
                except Exception as e:
                    # In case of any error, assume the tunnel is not running
                    self.status_update.emit(name, False)
            
            time.sleep(MONITOR_INTERVAL)
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
