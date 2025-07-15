#!/usr/bin/env python3
"""
SSH Tunnel Manager - Main Package
"""

__version__ = "1.0.2"
__author__ = "SSH Tunnel Manager Team"
__description__ = "Professional SSH Tunnel Manager for RTSP streaming and secure service access"

from .core import TunnelConfig, ConfigurationManager, TunnelProcess
from .gui import SSHTunnelManager
from .utils import ConnectionTester

__all__ = [
    'TunnelConfig',
    'ConfigurationManager', 
    'TunnelProcess',
    'SSHTunnelManager',
    'ConnectionTester'
]
