# Configuration Guide

This guide covers configuring SSH Tools Suite for optimal performance and security.

## Application Settings

### Initial Setup

On first launch, the SSH Tunnel Manager will create default configuration directories:

- **Windows**: `%APPDATA%\SSHTunnelManager\`
- **Linux**: `~/.config/SSHTunnelManager/`
- **macOS**: `~/Library/Preferences/SSHTunnelManager/`

### Configuration Files

The application stores settings in the following files:

```
SSHTunnelManager/
├── settings.ini          # Application preferences
├── tunnels.json          # Tunnel configurations (backup)
└── logs/                 # Application logs
    ├── application.log
    └── tunnel_*.log
```

## SSH Configuration

### SSH Client Setup

#### Windows
Windows 10/11 includes OpenSSH by default. Verify installation:

```cmd
ssh -V
```

If not available, install via Windows Features or download from [OpenSSH for Windows](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse).

#### Linux
Most distributions include OpenSSH client:

```bash
# Ubuntu/Debian
sudo apt install openssh-client

# CentOS/RHEL
sudo yum install openssh-clients

# Fedora
sudo dnf install openssh-clients
```

#### macOS
OpenSSH is pre-installed. Update via Homebrew if needed:

```bash
brew install openssh
```

### SSH Key Configuration

#### Default Key Locations

The application searches for SSH keys in standard locations:

```
~/.ssh/
├── id_rsa              # RSA private key
├── id_rsa.pub          # RSA public key
├── id_ed25519          # ED25519 private key
├── id_ed25519.pub      # ED25519 public key
├── id_ecdsa            # ECDSA private key
├── id_ecdsa.pub        # ECDSA public key
├── authorized_keys     # Authorized public keys
├── known_hosts         # Known host keys
└── config              # SSH client configuration
```

#### SSH Client Configuration

Create or edit `~/.ssh/config` for default settings:

```
# Global defaults
Host *
    ServerAliveInterval 60
    ServerAliveCountMax 3
    StrictHostKeyChecking ask
    UserKnownHostsFile ~/.ssh/known_hosts

# Specific host configuration
Host myserver
    HostName server.example.com
    User admin
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    LocalForward 8080 localhost:80
```

## Application Preferences

### GUI Settings

#### Theme and Appearance
```ini
[appearance]
theme=dark              # dark, light, auto
font_size=10
window_geometry=100,100,1000,700
```

#### Behavior Settings
```ini
[behavior]
minimize_to_tray=true
auto_start_tunnels=false
confirm_deletions=true
save_window_state=true
```

#### Logging Configuration
```ini
[logging]
level=INFO              # DEBUG, INFO, WARNING, ERROR
max_log_size=10485760   # 10MB
backup_count=5
log_to_file=true
```

### Security Settings

#### Authentication Preferences
```ini
[security]
prefer_key_auth=true
batch_mode=false
strict_host_checking=ask
connection_timeout=30
```

#### Key Management
```ini
[ssh_keys]
default_key_path=
auto_use_default=true
remember_last_used=true
```

## Network Configuration

### Firewall Settings

#### Windows Firewall
Allow SSH Tunnel Manager through Windows Defender Firewall:

1. Open Windows Security
2. Go to Firewall & network protection
3. Click "Allow an app through firewall"
4. Add SSH Tunnel Manager executable

#### Linux Firewall (UFW)
```bash
# Allow SSH
sudo ufw allow 22

# Allow specific tunnel ports
sudo ufw allow 8080
sudo ufw allow 8554
```

### Proxy Configuration

If behind a corporate proxy, configure SSH to use it:

```
# In ~/.ssh/config
Host *
    ProxyCommand nc -X connect -x proxy.company.com:8080 %h %p
```

## Performance Tuning

### Connection Optimization

#### SSH Keep-Alive Settings
```
# In tunnel configuration or ~/.ssh/config
ServerAliveInterval 30
ServerAliveCountMax 3
TCPKeepAlive yes
```

#### Connection Multiplexing
```
# In ~/.ssh/config
Host *
    ControlMaster auto
    ControlPath ~/.ssh/master-%r@%h:%p
    ControlPersist 10m
```

### Resource Limits

#### Maximum Tunnels
The application can handle multiple concurrent tunnels, but consider:

- **System resources**: Each tunnel uses ~10-20MB RAM
- **Network bandwidth**: Multiple tunnels share network capacity
- **SSH server limits**: Target servers may limit connections

#### Port Range Configuration
Use ports 1024-65535 for local forwarding to avoid privilege requirements:

```ini
[network]
min_local_port=1024
max_local_port=65535
default_rtsp_port=8554
```

## Import/Export Settings

### Configuration Backup

#### Automatic Backup
The application automatically backs up configurations:

```ini
[backup]
auto_backup=true
backup_interval=24      # hours
max_backups=7
backup_location=auto    # auto, custom path
```

#### Manual Backup
Export all settings and configurations:

1. **File → Export → Complete Backup**
2. Includes:
   - Tunnel configurations
   - Application settings
   - SSH key references (not private keys)

### Migration Between Systems

#### Export from Source System
```bash
# Export configurations
ssh-tunnel-manager export --output=tunnels.json

# Copy SSH keys
cp -r ~/.ssh /path/to/backup/
```

#### Import to Target System
```bash
# Copy SSH keys first
cp -r /path/to/backup/.ssh ~/
chmod 700 ~/.ssh
chmod 600 ~/.ssh/*

# Import configurations
ssh-tunnel-manager import --input=tunnels.json
```

## Troubleshooting Configuration

### Common Issues

#### "Configuration Not Saved"
- Check file permissions in config directory
- Ensure adequate disk space
- Verify application has write access

#### "SSH Keys Not Found"
- Check key file permissions (should be 600)
- Verify key path in configuration
- Ensure SSH agent is running (if using agent)

#### "Settings Reset on Restart"
- Check if configuration directory is read-only
- Verify no conflicting settings files
- Check for permission issues

### Debug Configuration

Enable debug logging:

```ini
[logging]
level=DEBUG
console_output=true
debug_ssh=true
```

View logs:
```bash
# Windows
type %APPDATA%\SSHTunnelManager\logs\application.log

# Linux/macOS
tail -f ~/.config/SSHTunnelManager/logs/application.log
```

### Reset Configuration

#### Partial Reset
1. **Settings → Reset to Defaults**
2. Keeps tunnel configurations, resets preferences

#### Complete Reset
```bash
# Backup first
cp -r ~/.config/SSHTunnelManager ~/ssh-tunnel-backup

# Remove configuration
rm -rf ~/.config/SSHTunnelManager

# Restart application
```

## Advanced Configuration

### Custom SSH Command
Override default SSH command:

```ini
[ssh]
custom_command=/usr/local/bin/ssh
additional_args=-o PreferredAuthentications=publickey
```

### Environment Variables

The application recognizes these environment variables:

```bash
# SSH configuration
export SSH_AUTH_SOCK=/path/to/ssh-agent
export SSH_AGENT_PID=12345

# Application settings
export SSH_TUNNEL_MANAGER_CONFIG=/custom/config/path
export SSH_TUNNEL_MANAGER_DEBUG=1
```

### Integration with External Tools

#### SSH Agent Integration
```bash
# Start SSH agent
eval $(ssh-agent)

# Add keys
ssh-add ~/.ssh/id_ed25519

# Configure application to use agent
```

#### Terminal Customization
```ini
[terminal]
# Windows
terminal_command=wt.exe
# Linux
terminal_command=gnome-terminal
# macOS
terminal_command=open -a Terminal
```

## Next Steps

- **[Creating Tunnels](../guides/creating-tunnels.md)** - Set up your first tunnel
- **[SSH Key Management](../guides/ssh-key-management.md)** - Advanced key handling
- **[Troubleshooting](../guides/troubleshooting.md)** - Solve common issues
