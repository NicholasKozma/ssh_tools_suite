#!/usr/bin/env python3
"""
SSH Tunnel Manager - Data Models
"""

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class TunnelConfig:
    """Configuration for an SSH tunnel."""
    name: str
    ssh_host: str
    ssh_port: int
    ssh_user: str
    local_port: int
    remote_host: str
    remote_port: int
    tunnel_type: str  # 'local', 'remote', 'dynamic'
    description: str = ""
    auto_start: bool = False
    ssh_key_path: str = ""
    ssh_password: str = ""  # Runtime password (not saved to config)
    rtsp_url: str = ""  # Custom RTSP URL (single URL)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization (excludes password)."""
        data = asdict(self)
        # Remove password from serialization for security
        data.pop('ssh_password', None)
        return data
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TunnelConfig':
        """Create from dictionary."""
        # Make a copy to avoid modifying the original
        data = data.copy()
        
        # Ensure ssh_password is not loaded from saved config
        data.pop('ssh_password', None)
        
        # Remove any unknown fields that aren't part of the TunnelConfig dataclass
        # This handles backwards compatibility when fields are removed or renamed
        import inspect
        signature = inspect.signature(cls)
        valid_fields = set(signature.parameters.keys())
        
        # Filter out any fields not in the current TunnelConfig definition
        filtered_data = {k: v for k, v in data.items() if k in valid_fields}
        
        return cls(**filtered_data)
    
    def copy(self) -> 'TunnelConfig':
        """Create a copy of this configuration."""
        return TunnelConfig(
            name=self.name,
            ssh_host=self.ssh_host,
            ssh_port=self.ssh_port,
            ssh_user=self.ssh_user,
            local_port=self.local_port,
            remote_host=self.remote_host,
            remote_port=self.remote_port,
            tunnel_type=self.tunnel_type,
            description=self.description,
            auto_start=self.auto_start,
            ssh_key_path=self.ssh_key_path,
            ssh_password=self.ssh_password,
            rtsp_url=self.rtsp_url
        )
    
    def validate(self) -> tuple[bool, str]:
        """Validate configuration."""
        if not self.name.strip():
            return False, "Tunnel name is required"
        
        if not self.ssh_host.strip():
            return False, "SSH host is required"
        
        if not self.ssh_user.strip():
            return False, "SSH user is required"
        
        if not 1 <= self.ssh_port <= 65535:
            return False, "SSH port must be between 1 and 65535"
        
        if not 1024 <= self.local_port <= 65535:
            return False, "Local port must be between 1024 and 65535"
        
        if self.tunnel_type not in ['local', 'remote', 'dynamic']:
            return False, "Invalid tunnel type"
        
        if self.tunnel_type != 'dynamic':
            if not self.remote_host.strip():
                return False, "Remote host is required for local/remote tunnels"
            
            if not 1 <= self.remote_port <= 65535:
                return False, "Remote port must be between 1 and 65535"
        
        return True, ""
    
    def get_ssh_command_args(self) -> list[str]:
        """Generate SSH command arguments for this tunnel."""
        import os
        
        # Build tunnel argument based on type
        if self.tunnel_type == 'local':
            tunnel_arg = f"-L {self.local_port}:{self.remote_host}:{self.remote_port}"
        elif self.tunnel_type == 'remote':
            tunnel_arg = f"-R {self.remote_port}:localhost:{self.local_port}"
        else:  # dynamic
            tunnel_arg = f"-D {self.local_port}"
        
        cmd = [
            'ssh',
            '-N',  # Don't execute remote command
            tunnel_arg,
            f"{self.ssh_user}@{self.ssh_host}",
            '-p', str(self.ssh_port),
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ServerAliveInterval=30',
            '-o', 'ServerAliveCountMax=3',
            '-o', 'TCPKeepAlive=yes',
            '-o', 'ExitOnForwardFailure=yes',
            '-o', 'ConnectTimeout=30'
        ]
        
        # Add SSH key - check specified key first, then default locations
        key_to_use = None
        
        if self.ssh_key_path and os.path.exists(self.ssh_key_path):
            key_to_use = self.ssh_key_path
        else:
            # Check for default SSH keys in standard locations
            from pathlib import Path
            home = Path.home()
            default_keys = [
                home / '.ssh' / 'id_rsa',
                home / '.ssh' / 'id_ed25519',
                home / '.ssh' / 'id_ecdsa',
                home / '.ssh' / 'id_dsa'
            ]
            
            for key_path in default_keys:
                if key_path.exists():
                    key_to_use = str(key_path)
                    break
        
        if key_to_use:
            cmd.extend(['-i', key_to_use])
            # For key authentication, prefer key-based auth but allow fallback
            cmd.extend([
                '-o', 'PreferredAuthentications=publickey,password',
                '-o', 'BatchMode=no'
            ])
        else:
            # For password authentication, enable interactive mode
            cmd.extend([
                '-o', 'BatchMode=no',
                '-o', 'PasswordAuthentication=yes',
                '-o', 'PreferredAuthentications=password',
                '-o', 'NumberOfPasswordPrompts=1'
            ])
        
        return cmd
    
    def get_display_name(self) -> str:
        """Get a display-friendly name for the tunnel."""
        if self.description:
            return f"{self.name} - {self.description}"
        return self.name
    
    def get_connection_string(self) -> str:
        """Get connection string representation."""
        if self.tunnel_type == 'dynamic':
            return f"SOCKS Proxy on localhost:{self.local_port}"
        elif self.tunnel_type == 'local':
            return f"localhost:{self.local_port} → {self.remote_host}:{self.remote_port}"
        else:  # remote
            return f"{self.remote_host}:{self.remote_port} ← localhost:{self.local_port}"
    
    def get_rtsp_url(self) -> str:
        """Get the RTSP URL for this tunnel configuration."""
        if self.rtsp_url:
            return self.rtsp_url
        else:
            # Generate default RTSP URL using the local port
            return f"rtsp://localhost:{self.local_port}/live/0"
    
    def get_common_rtsp_urls(self) -> list[str]:
        """Get common RTSP URL patterns for this tunnel configuration."""
        base_url = f"rtsp://localhost:{self.local_port}"
        return [
            f"{base_url}/live/0",
            f"{base_url}/stream/0",
            f"{base_url}/cam/realmonitor?channel=1&subtype=0",
            f"{base_url}/av0_0",
            f"{base_url}/axis-media/media.amp",
            f"{base_url}/video.mjpg",
            f"{base_url}/live",
            f"{base_url}/stream",
            f"{base_url}/"
        ]
