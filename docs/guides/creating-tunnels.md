# Creating SSH Tunnels

This comprehensive guide covers creating different types of SSH tunnels using the SSH Tunnel Manager.

## Understanding Tunnel Types

### Local Port Forwarding
**Concept**: Forward a local port to a remote destination through an SSH server.

**Format**: `ssh -L local_port:remote_host:remote_port user@ssh_server`

**Use case**: Access services on a remote network that aren't directly accessible.

```
[Your Computer] → [SSH Server] → [Target Service]
     8080       →      22       →   80 (web server)
```

### Remote Port Forwarding
**Concept**: Allow remote users to access your local services through the SSH server.

**Format**: `ssh -R remote_port:local_host:local_port user@ssh_server`

**Use case**: Share a local service with remote users.

```
[Remote Users] → [SSH Server] → [Your Computer]
                    8080       →      3000
```

### Dynamic Port Forwarding (SOCKS Proxy)
**Concept**: Create a SOCKS proxy that routes traffic through the SSH server.

**Format**: `ssh -D local_port user@ssh_server`

**Use case**: Route all application traffic through the SSH server.

```
[Your Apps] → [SOCKS Proxy] → [SSH Server] → [Internet]
              localhost:1080      22
```

## Step-by-Step Tunnel Creation

### Creating a Local Port Forward

#### Example: Accessing a Web Interface

1. **Open Configuration Dialog**
   - Click **"Add Tunnel"** (➕) in the toolbar
   - Or use menu: **File → New Tunnel**

2. **Basic Information**
   ```
   Name: router_admin
   Description: Access router admin interface
   ```

3. **SSH Connection Settings**
   ```
   SSH Host: router.example.com
   SSH Port: 22
   SSH User: admin
   SSH Key Path: C:\Users\YourName\.ssh\id_rsa
   ```

4. **Tunnel Configuration**
   ```
   Tunnel Type: Local
   Local Port: 8080
   Remote Host: localhost
   Remote Port: 80
   ```

5. **Save and Test**
   - Click **"OK"** to save
   - Select the tunnel and click **"Start"**
   - Access via `http://localhost:8080`

#### Example: Database Connection

1. **Configuration**
   ```
   Name: mysql_production
   Description: Production MySQL database
   SSH Host: db-server.company.com
   SSH Port: 22
   SSH User: dbadmin
   Tunnel Type: Local
   Local Port: 3307
   Remote Host: localhost
   Remote Port: 3306
   ```

2. **Database Client Setup**
   ```
   Host: localhost
   Port: 3307
   Username: mysql_user
   Password: [mysql_password]
   ```

### Creating a Remote Port Forward

#### Example: Sharing Local Development Server

1. **Configuration**
   ```
   Name: dev_server_share
   Description: Share local development server
   SSH Host: public-server.example.com
   SSH Port: 22
   SSH User: developer
   Tunnel Type: Remote
   Local Port: 3000
   Remote Host: localhost
   Remote Port: 8080
   ```

2. **Result**
   - Your local port 3000 is accessible at `public-server.example.com:8080`
   - Others can visit `http://public-server.example.com:8080`

### Creating a Dynamic Port Forward (SOCKS Proxy)

#### Example: Browsing Through SSH Server

1. **Configuration**
   ```
   Name: company_proxy
   Description: Browse through company network
   SSH Host: vpn.company.com
   SSH Port: 22
   SSH User: employee
   Tunnel Type: Dynamic
   Local Port: 1080
   ```

2. **Browser Configuration**
   - **Firefox**: Settings → Network → Manual proxy
     - SOCKS Host: `localhost`
     - Port: `1080`
     - SOCKS v5: Enabled
   
   - **Chrome**: Start with proxy settings
     ```bash
     chrome --proxy-server="socks5://localhost:1080"
     ```

## Advanced Configuration Options

### SSH Key Authentication

#### Generating SSH Keys
1. **Using SSH Tunnel Manager**
   - Click **"SSH Key Setup"** in toolbar
   - Follow the key generation wizard
   - Automatically deploys keys to servers

2. **Manual Generation**
   ```bash
   # Generate ED25519 key (recommended)
   ssh-keygen -t ed25519 -C "your_email@example.com"
   
   # Generate RSA key (compatibility)
   ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
   ```

#### Key Deployment
```bash
# Copy public key to server
ssh-copy-id user@hostname

# Manual deployment
cat ~/.ssh/id_ed25519.pub | ssh user@hostname "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Auto-Start Configuration

Enable tunnels to start automatically:

1. Edit tunnel configuration
2. Check **"Auto-start on application launch"**
3. Tunnels will start when the application opens

### Multiple Hops (Jump Servers)

For accessing servers through intermediate hosts:

1. **First Tunnel** (to jump server)
   ```
   Name: jump_server
   SSH Host: jump.company.com
   SSH Port: 22
   SSH User: admin
   Tunnel Type: Local
   Local Port: 2222
   Remote Host: internal-server.local
   Remote Port: 22
   ```

2. **Second Tunnel** (through first tunnel)
   ```
   Name: internal_service
   SSH Host: localhost
   SSH Port: 2222
   SSH User: internal_admin
   Tunnel Type: Local
   Local Port: 8080
   Remote Host: localhost
   Remote Port: 80
   ```

## RTSP Video Streaming

### IP Camera Access

1. **Tunnel Configuration**
   ```
   Name: security_camera_01
   Description: Office security camera
   SSH Host: office-router.example.com
   SSH Port: 22
   SSH User: admin
   Tunnel Type: Local
   Local Port: 8554
   Remote Host: 192.168.1.50
   Remote Port: 554
   RTSP URL: rtsp://localhost:8554/live/0
   ```

2. **Testing the Stream**
   - Start the tunnel
   - Click **"Launch RTSP"** in toolbar
   - Or use external player: `vlc rtsp://localhost:8554/live/0`

### Common RTSP URLs

The SSH Tunnel Manager automatically suggests common RTSP URL patterns:

```
rtsp://localhost:8554/live/0                    # Generic
rtsp://localhost:8554/stream/0                  # Alternative
rtsp://localhost:8554/cam/realmonitor?channel=1 # Dahua cameras
rtsp://localhost:8554/av0_0                     # Some HIKVISION
rtsp://localhost:8554/axis-media/media.amp      # Axis cameras
```

## Configuration Import/Export

### Exporting Configurations

1. **Individual Export**
   - Right-click tunnel in table
   - Select **"Export Configuration"**

2. **Bulk Export**
   - Menu: **File → Export Configurations**
   - Saves all tunnels to JSON file

### Importing Configurations

1. **From File**
   - Menu: **File → Import Configurations**
   - Select JSON file
   - Choose to overwrite or skip duplicates

2. **From Another Installation**
   - Copy configuration files between systems
   - Windows: `%APPDATA%\SSHTunnelManager\`
   - Linux: `~/.config/SSHTunnelManager/`

### Configuration Format

```json
{
  "version": "1.0",
  "tunnels": {
    "camera_rtsp": {
      "name": "camera_rtsp",
      "ssh_host": "192.168.1.1",
      "ssh_port": 22,
      "ssh_user": "admin",
      "local_port": 8554,
      "remote_host": "192.168.1.50",
      "remote_port": 554,
      "tunnel_type": "local",
      "description": "Security camera access",
      "auto_start": true,
      "ssh_key_path": "/path/to/key",
      "rtsp_url": "rtsp://localhost:8554/live/0"
    }
  }
}
```

## Best Practices

### Security

1. **Use SSH Keys**: More secure than passwords
2. **Limit Key Access**: Set proper file permissions (600)
3. **Regular Key Rotation**: Update keys periodically
4. **Host Key Verification**: Enable when security is critical

### Performance

1. **Connection Limits**: Don't create excessive concurrent tunnels
2. **Keep-Alive Settings**: Use built-in keep-alive for stability
3. **Local Port Selection**: Use ports above 1024 to avoid privilege issues
4. **Monitor Resources**: Check system resources with many tunnels

### Organization

1. **Descriptive Names**: Use clear, descriptive tunnel names
2. **Grouping**: Use naming conventions for related tunnels
3. **Documentation**: Add meaningful descriptions
4. **Regular Cleanup**: Remove unused configurations

## Troubleshooting

### Common Issues

#### "Connection Refused"
```bash
# Check SSH service
ssh -v user@hostname

# Verify port accessibility
telnet hostname 22

# Check firewall
# Linux: sudo ufw status
# Windows: Windows Defender Firewall settings
```

#### "Port Already in Use"
```bash
# Find process using port
netstat -tulpn | grep :8080  # Linux
netstat -ano | findstr :8080 # Windows

# Kill process if needed
kill -9 <PID>        # Linux
taskkill /PID <PID>  # Windows
```

#### "Permission Denied (publickey)"
```bash
# Check key permissions
chmod 600 ~/.ssh/id_rsa

# Test SSH connection
ssh -i ~/.ssh/id_rsa user@hostname

# Check authorized_keys on server
cat ~/.ssh/authorized_keys
```

#### "Tunnel Established but Service Unreachable"
```bash
# Test from SSH server
ssh user@hostname
telnet remote_host remote_port

# Check tunnel status
netstat -an | grep local_port
```

### Debug Mode

Enable detailed logging:

1. **GUI Application**
   - View → Show Debug Log
   - Higher verbosity in settings

2. **Command Line**
   ```bash
   ssh-tunnel-manager --debug start tunnel_name
   ```

3. **SSH Verbose Mode**
   - Add `-v`, `-vv`, or `-vvv` to SSH commands for debugging

## Next Steps

- **[Managing Configurations](managing-configurations.md)** - Organize your tunnels
- **[SSH Key Management](ssh-key-management.md)** - Advanced key handling
- **[RTSP Streaming](rtsp-streaming.md)** - Video streaming specifics
- **[Troubleshooting](troubleshooting.md)** - Detailed problem solving
