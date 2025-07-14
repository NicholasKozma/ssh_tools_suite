# SSH Tunnel Manager - Usage Examples

This page provides practical examples of using the SSH Tunnel Manager for common scenarios.

## Basic SSH Tunnel

Create a simple SSH tunnel to forward a local port to a remote service:

```python
from ssh_tunnel_manager.core.models import TunnelConfig

# Create a basic tunnel configuration
config = TunnelConfig(
    name="Database Tunnel",
    ssh_host="jumpserver.example.com",
    ssh_port=22,
    ssh_username="myuser",
    local_port=5432,
    remote_host="database.internal",
    remote_port=5432
)
```

## Dynamic Port Forwarding (SOCKS Proxy)

Set up a SOCKS proxy for secure browsing:

```python
config = TunnelConfig(
    name="SOCKS Proxy",
    ssh_host="proxy.example.com",
    ssh_port=22,
    ssh_username="proxyuser",
    local_port=1080,
    tunnel_type="dynamic"
)
```

## Reverse Tunnel

Create a reverse tunnel to expose a local service:

```python
config = TunnelConfig(
    name="Reverse Web Service",
    ssh_host="gateway.example.com",
    ssh_port=22,
    ssh_username="webuser",
    local_port=8080,
    remote_port=80,
    tunnel_type="reverse"
)
```

## Multi-hop Tunnel

Connect through multiple SSH servers:

```python
# First hop
hop1_config = TunnelConfig(
    name="Hop 1",
    ssh_host="bastion.example.com",
    ssh_port=22,
    ssh_username="bastionuser",
    local_port=2222,
    remote_host="internal-jump.example.com",
    remote_port=22
)

# Second hop through the first
hop2_config = TunnelConfig(
    name="Final Destination",
    ssh_host="localhost",
    ssh_port=2222,  # Connect through first tunnel
    ssh_username="internaluser",
    local_port=5432,
    remote_host="database.internal",
    remote_port=5432
)
```

## Using SSH Keys

Configure authentication with SSH keys:

```python
config = TunnelConfig(
    name="Key-based Tunnel",
    ssh_host="secure.example.com",
    ssh_port=22,
    ssh_username="keyuser",
    ssh_key_path="/path/to/private/key",
    local_port=3306,
    remote_host="mysql.internal",
    remote_port=3306
)
```

## Monitoring and Health Checks

Enable monitoring for your tunnels:

```python
from ssh_tunnel_manager.core.monitor import TunnelMonitor

# Create monitor with health checks
monitor = TunnelMonitor()
monitor.add_tunnel(config)
monitor.enable_health_check(
    interval=30,  # Check every 30 seconds
    timeout=10    # 10 second timeout
)
```

## GUI Integration

Use the tunnel manager with the GUI:

```python
from ssh_tunnel_manager.gui.main_window import TunnelManagerGUI
from PyQt5.QtWidgets import QApplication

app = QApplication([])
gui = TunnelManagerGUI()
gui.add_tunnel_config(config)
gui.show()
app.exec_()
```

## Common Use Cases

### Database Access
Connect to databases behind firewalls or in private networks.

### Web Development
Access internal APIs and services during development.

### Remote Desktop
Tunnel RDP connections through SSH for added security.

### File Transfer
Create secure file transfer channels using SFTP through tunnels.

### Monitoring Services
Access internal monitoring dashboards and metrics.

## Best Practices

1. **Use SSH keys** instead of passwords when possible
2. **Limit tunnel lifetime** - don't leave tunnels open indefinitely
3. **Monitor tunnel health** to detect connection issues
4. **Use appropriate tunnel types** for your use case
5. **Secure your SSH keys** with proper permissions and passphrases
