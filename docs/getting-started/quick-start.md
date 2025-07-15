# Quick Start Guide

Get up and running with SSH Tools Suite in just a few minutes!

## Installation Options

### Option 1: Standalone Executable (Fastest)

1. **Download**: Go to [GitHub Releases](https://github.com/NicholasKozma/ssh_tools_suite/releases)
2. **Extract**: Download and extract `SSH-Tunnel-Manager-v*.*.*.zip`
3. **Run**: Double-click `SSH-Tunnel-Manager.exe`

### Option 2: PyPI Installation

```bash
# Install from PyPI (recommended for Python users)
pip install ssh-tools-suite

# Verify installation
ssh-tunnel-manager --version
```

## Launch the Application

### Using Standalone Executable

```cmd
# Windows: Navigate to extracted folder and run
SSH-Tunnel-Manager.exe

# Or from command line with options
SSH-Tunnel-Manager.exe --help
```

### Using PyPI Installation

**GUI Application:**
```bash
# Method 1: Using the installed script
ssh-tunnel-manager-gui

# Method 2: Using Python module
python -m ssh_tunnel_manager.gui

# Method 3: Direct execution (if in source directory)
python ssh_tunnel_manager_app.py
```

**Command Line Interface:**
```bash
# View available commands
ssh-tunnel-manager --help

# List configurations
ssh-tunnel-manager list

# Start a specific tunnel
ssh-tunnel-manager start tunnel_name
```

## Creating Your First Tunnel

### Step 1: Open the Configuration Dialog

1. Launch the SSH Tunnel Manager GUI
2. Click the **"Add Tunnel"** button (➕) in the toolbar
3. The Tunnel Configuration Dialog will open

### Step 2: Basic Configuration

Fill in the essential information:

```
Name: camera_access
Description: Access to IP camera via SSH tunnel
```

### Step 3: SSH Connection Settings

Configure the SSH connection:

```
SSH Host: 192.168.1.100    # Your SSH server IP/hostname
SSH Port: 22               # SSH port (usually 22)
SSH User: admin            # Your SSH username
SSH Key Path: (optional)   # Leave blank to use password
```

### Step 4: Tunnel Settings

Set up the port forwarding:

```
Tunnel Type: Local
Local Port: 8554           # Port on your computer
Remote Host: localhost     # Target host (from SSH server perspective)
Remote Port: 554           # Target port on remote host
```

### Step 5: Save and Test

1. Click **"OK"** to save the configuration
2. Select your new tunnel in the main table
3. Click **"Start"** (▶️) to establish the tunnel
4. Click **"Test"** (🧪) to verify connectivity

## Common Tunnel Types

### Local Port Forwarding (Most Common)
**Use case**: Access a service on a remote network through an SSH server

```
Type: Local
Local Port: 8080
Remote Host: localhost (or internal IP)
Remote Port: 80
```

**Result**: `http://localhost:8080` → Remote server's port 80

### Remote Port Forwarding
**Use case**: Allow remote users to access your local service

```
Type: Remote
Local Port: 3000
Remote Host: localhost
Remote Port: 8080
```

**Result**: Remote users can access your port 3000 via SSH server's port 8080

### Dynamic Port Forwarding (SOCKS Proxy)
**Use case**: Route all traffic through the SSH server

```
Type: Dynamic
Local Port: 1080
```

**Result**: Configure applications to use SOCKS proxy `localhost:1080`

## Example Configurations

### RTSP Camera Access
```yaml
Name: ip_camera_rtsp
SSH Host: router.example.com
SSH Port: 22
SSH User: admin
Tunnel Type: Local
Local Port: 8554
Remote Host: 192.168.1.50
Remote Port: 554
RTSP URL: rtsp://localhost:8554/live/0
```

### Web Interface Access
```yaml
Name: router_admin
SSH Host: router.example.com
SSH Port: 22
SSH User: admin
Tunnel Type: Local
Local Port: 8080
Remote Host: localhost
Remote Port: 80
```

### Database Connection
```yaml
Name: mysql_dev
SSH Host: db-server.company.com
SSH Port: 22
SSH User: developer
Tunnel Type: Local
Local Port: 3307
Remote Host: localhost
Remote Port: 3306
```

## Using SSH Keys (Recommended)

### Generate SSH Key Pair
```bash
# Generate a new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Or RSA if ed25519 isn't supported
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### Deploy Key to Server
```bash
# Copy public key to server
ssh-copy-id user@hostname

# Or manually copy the public key content
cat ~/.ssh/id_ed25519.pub
# Paste into server's ~/.ssh/authorized_keys
```

### Configure in SSH Tunnel Manager
1. In the tunnel configuration dialog
2. Set **SSH Key Path** to your private key file:
   - Windows: `C:\Users\YourName\.ssh\id_ed25519`
   - Linux/macOS: `/home/username/.ssh/id_ed25519`

## Testing Your Tunnel

### Using the Built-in Tester
1. Select your tunnel in the main table
2. Click **"Start"** to establish the connection
3. Click **"Test"** to verify connectivity
4. Check the log output for results

### Manual Testing

#### Test Port Connectivity
```bash
# Test if the local port is listening
netstat -an | grep :8554    # Linux/macOS
netstat -an | findstr :8554 # Windows

# Test connection
telnet localhost 8554
```

#### Test HTTP Services
```bash
# Using curl
curl http://localhost:8080

# Using browser
# Navigate to http://localhost:8080
```

#### Test RTSP Streams
```bash
# Using ffplay (if available)
ffplay rtsp://localhost:8554/live/0

# Using VLC
vlc rtsp://localhost:8554/live/0
```

## Managing Multiple Tunnels

### Auto-Start Configuration
1. Edit an existing tunnel configuration
2. Check **"Auto-start on application launch"**
3. The tunnel will start automatically when you open the application

### Import/Export Configurations
```bash
# Export all configurations
File → Export Configurations → Save as tunnels.json

# Import configurations
File → Import Configurations → Select tunnels.json
```

### Backup Your Settings
Configuration files are stored in:
- **Windows**: `%APPDATA%\SSHTunnelManager\`
- **Linux**: `~/.config/SSHTunnelManager/`
- **macOS**: `~/Library/Preferences/SSHTunnelManager/`

## System Tray Integration

The SSH Tunnel Manager can run in the system tray:

1. **Minimize to Tray**: Close the main window (tunnel processes continue)
2. **Quick Access**: Right-click tray icon for menu options
3. **Status Indicators**: Tray icon shows overall tunnel status

## Troubleshooting Quick Fixes

### "Connection Refused"
- Verify SSH server is running and accessible
- Check firewall settings on both client and server
- Confirm SSH port (usually 22) is correct

### "Permission Denied"
- Verify username and authentication method
- Check SSH key permissions (should be 600)
- Ensure user has SSH access on the server

### "Port Already in Use"
- Change the local port number
- Kill any processes using the port:
  ```bash
  # Linux/macOS
  lsof -i :8554
  kill -9 <PID>
  
  # Windows
  netstat -ano | findstr :8554
  taskkill /PID <PID> /F
  ```

### "Tunnel Not Working"
- Verify the tunnel is in "running" status
- Check that remote host/port are correct
- Test from the SSH server directly:
  ```bash
  ssh user@hostname
  telnet localhost 554  # Test target service
  ```

## Next Steps

Now that you have your first tunnel working:

1. **[Learn Advanced Features](../guides/creating-tunnels.md)** - Explore more tunnel types
2. **[RTSP Streaming Guide](../guides/rtsp-streaming.md)** - Set up video streaming
3. **[SSH Key Management](../guides/ssh-key-management.md)** - Secure authentication
4. **[Configuration Management](../guides/managing-configurations.md)** - Organize your tunnels

## Need Help?

- **Documentation**: Browse the full [User Guides](../guides/creating-tunnels.md)
- **Examples**: Check the [Usage Examples](../ssh-tunnel-manager/usage-examples.md)
- **Issues**: Report problems on [GitHub](https://github.com/NicholasKozma/ssh_tools_suite/issues)
- **Community**: Join discussions in [GitHub Discussions](https://github.com/NicholasKozma/ssh_tools_suite/discussions)
