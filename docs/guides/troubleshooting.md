# Troubleshooting Guide

Common issues and solutions for SSH Tools Suite.

## General Troubleshooting

### Connection Issues

#### "Connection refused" errors

**Symptoms:**
- Cannot connect to SSH server
- "Connection refused" in logs
- Tunnel fails to establish

**Solutions:**

1. **Verify SSH server is running**:
   ```bash
   # Check if SSH service is running
   sudo systemctl status ssh
   # or
   sudo service ssh status
   ```

2. **Check firewall settings**:
   ```bash
   # Ubuntu/Debian
   sudo ufw status
   sudo ufw allow ssh
   
   # CentOS/RHEL
   sudo firewall-cmd --list-all
   sudo firewall-cmd --add-service=ssh --permanent
   ```

3. **Verify SSH port**:
   ```bash
   # Check if SSH is listening
   netstat -tlnp | grep :22
   # or
   ss -tlnp | grep :22
   ```

#### "Permission denied" errors

**Symptoms:**
- SSH authentication fails
- "Permission denied (publickey)" errors
- Cannot authenticate with keys

**Solutions:**

1. **Check SSH key permissions**:
   ```bash
   chmod 600 ~/.ssh/id_rsa
   chmod 644 ~/.ssh/id_rsa.pub
   chmod 700 ~/.ssh
   ```

2. **Verify public key deployment**:
   ```bash
   ssh-copy-id user@server.com
   ```

3. **Test key authentication**:
   ```bash
   ssh -i ~/.ssh/id_rsa -v user@server.com
   ```

#### "Host key verification failed"

**Symptoms:**
- SSH warns about changed host keys
- Connection blocked by host key mismatch

**Solutions:**

1. **Remove old host key**:
   ```bash
   ssh-keygen -R hostname
   ```

2. **Accept new host key**:
   ```bash
   ssh -o StrictHostKeyChecking=no user@server.com
   ```

3. **Verify host authenticity** before accepting

### Tunnel-Specific Issues

#### Port already in use

**Symptoms:**
- "Address already in use" errors
- Cannot bind to local port
- Tunnel startup fails

**Solutions:**

1. **Find process using port**:
   ```bash
   # Windows
   netstat -ano | findstr :8080
   
   # Linux/Mac
   lsof -i :8080
   netstat -tulpn | grep :8080
   ```

2. **Kill conflicting process**:
   ```bash
   # Windows
   taskkill /PID <pid> /F
   
   # Linux/Mac
   kill -9 <pid>
   ```

3. **Use different local port** in tunnel configuration

#### Tunnel disconnects frequently

**Symptoms:**
- Tunnel drops connection regularly
- "Broken pipe" errors
- Intermittent connectivity

**Solutions:**

1. **Enable keep-alive**:
   ```bash
   # In ~/.ssh/config
   Host *
       ServerAliveInterval 60
       ServerAliveCountMax 3
   ```

2. **Check network stability**:
   ```bash
   ping -c 10 server.com
   mtr server.com
   ```

3. **Configure tunnel persistence** in SSH Tunnel Manager

#### Remote service not accessible

**Symptoms:**
- Tunnel establishes but service unreachable
- Connection timeout to remote service
- "No route to host" errors

**Solutions:**

1. **Verify remote service is running**:
   ```bash
   # On remote server
   netstat -tlnp | grep :80
   ```

2. **Check remote firewall**:
   ```bash
   # Test from SSH server
   telnet localhost 80
   ```

3. **Verify tunnel configuration**:
   - Check remote host/port settings
   - Ensure correct bind address

## SSH Tunnel Manager Issues

### Application Won't Start

#### Missing dependencies

**Symptoms:**
- Import errors on startup
- "Module not found" errors
- Application crashes immediately

**Solutions:**

1. **Install missing packages**:
   ```bash
   pip install -e .[dev]
   ```

2. **Check Python version**:
   ```bash
   python --version
   # Requires Python 3.9+
   ```

3. **Verify PySide6 installation**:
   ```bash
   python -c "import PySide6; print(PySide6.__version__)"
   ```

#### GUI display issues

**Symptoms:**
- Blank/black window
- UI elements not rendering
- Application appears frozen

**Solutions:**

1. **Check display environment**:
   ```bash
   echo $DISPLAY
   xauth list
   ```

2. **Try different Qt platform**:
   ```bash
   export QT_QPA_PLATFORM=xcb
   python ssh_tunnel_manager_app.py
   ```

3. **Update graphics drivers**

### Configuration Issues

#### Configuration file corruption

**Symptoms:**
- Settings not saving
- Application crashes on startup
- "Invalid configuration" errors

**Solutions:**

1. **Reset configuration**:
   ```bash
   # Windows
   del "%APPDATA%\SSH_Tunnel_Manager\config.json"
   
   # Linux/Mac
   rm ~/.config/SSH_Tunnel_Manager/config.json
   ```

2. **Backup and restore**:
   ```bash
   # Create backup
   cp config.json config.json.backup
   
   # Restore from backup
   cp config.json.backup config.json
   ```

#### Tunnel configurations lost

**Symptoms:**
- Saved tunnels disappear
- Cannot load tunnel profiles
- Empty tunnel list

**Solutions:**

1. **Check configuration directory**:
   ```bash
   # Windows
   dir "%APPDATA%\SSH_Tunnel_Manager"
   
   # Linux/Mac
   ls -la ~/.config/SSH_Tunnel_Manager/
   ```

2. **Restore from backup**:
   - Look for `.backup` files
   - Import from export files

3. **Check file permissions**:
   ```bash
   chmod 644 ~/.config/SSH_Tunnel_Manager/config.json
   ```

## Third Party Installer Issues

### Installation Failures

#### Download failures

**Symptoms:**
- "Download failed" errors
- Network timeout errors
- Incomplete downloads

**Solutions:**

1. **Check internet connectivity**:
   ```bash
   ping google.com
   curl -I https://github.com
   ```

2. **Configure proxy** if behind corporate firewall

3. **Try manual download** and install

#### Permission errors during installation

**Symptoms:**
- "Access denied" during tool installation
- Cannot write to Program Files
- Installation fails silently

**Solutions:**

1. **Run as administrator** (Windows):
   ```powershell
   Start-Process powershell -Verb RunAs
   ```

2. **Use user-level installation**:
   ```python
   installer.prefer_user_installation = True
   ```

3. **Check antivirus interference**

### Tool Detection Issues

#### Tools not found after installation

**Symptoms:**
- Installer shows "not installed"
- Tools installed but not detected
- Path issues

**Solutions:**

1. **Check installation paths**:
   ```python
   from third_party_installer.core.installer import ThirdPartyInstaller
   installer = ThirdPartyInstaller()
   print(installer.tools_config['vlc'].executable_paths)
   ```

2. **Add to system PATH**:
   ```bash
   # Windows
   setx PATH "%PATH%;C:\Program Files\VLC"
   
   # Linux/Mac
   export PATH=$PATH:/usr/local/bin
   ```

3. **Manual path configuration** in tool settings

## Performance Issues

### High CPU Usage

**Symptoms:**
- Application uses excessive CPU
- System becomes slow
- Fan noise increases

**Solutions:**

1. **Check for busy loops**:
   - Monitor connection status polling
   - Reduce refresh frequency

2. **Limit concurrent tunnels**:
   - Close unused tunnels
   - Use tunnel grouping

3. **Update to latest version**

### High Memory Usage

**Symptoms:**
- Memory usage grows over time
- System runs out of RAM
- Application becomes unresponsive

**Solutions:**

1. **Restart application** periodically

2. **Check for memory leaks**:
   - Monitor with task manager
   - Report if memory keeps growing

3. **Reduce log retention**:
   ```python
   # Limit log file size
   config.log_max_size = 10 * 1024 * 1024  # 10MB
   ```

## Network Issues

### Corporate Firewall

#### Blocked SSH connections

**Symptoms:**
- SSH connections fail from corporate network
- Specific ports blocked
- Proxy authentication required

**Solutions:**

1. **Use alternative SSH port**:
   ```bash
   # Try port 443 (HTTPS)
   ssh -p 443 user@server.com
   ```

2. **Configure HTTP proxy**:
   ```bash
   # In ~/.ssh/config
   Host server.com
       ProxyCommand nc -X connect -x proxy:8080 %h %p
   ```

3. **Use VPN** to bypass restrictions

#### DNS resolution issues

**Symptoms:**
- "Name or service not known" errors
- Cannot resolve hostnames
- IP addresses work but names don't

**Solutions:**

1. **Check DNS settings**:
   ```bash
   nslookup server.com
   dig server.com
   ```

2. **Use alternative DNS**:
   ```bash
   # Use Google DNS
   echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
   ```

3. **Use IP addresses** instead of hostnames

## Platform-Specific Issues

### Windows

#### Windows Defender blocking

**Symptoms:**
- Downloads quarantined
- Executable files blocked
- Installation interrupted

**Solutions:**

1. **Add exclusions**:
   - Windows Security → Virus & threat protection
   - Add folder exclusion for SSH Tools Suite

2. **Temporarily disable** real-time protection during installation

#### PowerShell execution policy

**Symptoms:**
- Scripts cannot run
- "Execution of scripts is disabled" errors

**Solutions:**

1. **Change execution policy**:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### Linux

#### Missing system packages

**Symptoms:**
- "Command not found" errors
- Missing shared libraries
- Compilation failures

**Solutions:**

1. **Install development packages**:
   ```bash
   # Ubuntu/Debian
   sudo apt-get install build-essential python3-dev
   
   # CentOS/RHEL
   sudo yum groupinstall "Development Tools"
   sudo yum install python3-devel
   ```

#### SELinux restrictions

**Symptoms:**
- Permission denied despite correct permissions
- "Operation not permitted" errors
- SSH connections blocked

**Solutions:**

1. **Check SELinux status**:
   ```bash
   sestatus
   getenforce
   ```

2. **Set permissive mode** (temporary):
   ```bash
   sudo setenforce 0
   ```

3. **Configure SELinux policies** for SSH tunneling

### macOS

#### Gatekeeper blocking

**Symptoms:**
- "App cannot be opened because it is from an unidentified developer"
- Downloads quarantined
- Application won't start

**Solutions:**

1. **Allow in Security & Privacy**:
   - System Preferences → Security & Privacy
   - Click "Open Anyway"

2. **Remove quarantine**:
   ```bash
   xattr -d com.apple.quarantine /path/to/app
   ```

#### Keychain access issues

**Symptoms:**
- SSH key access denied
- Keychain prompts repeatedly
- Authentication failures

**Solutions:**

1. **Add key to keychain**:
   ```bash
   ssh-add --apple-use-keychain ~/.ssh/id_rsa
   ```

2. **Configure SSH agent**:
   ```bash
   # In ~/.ssh/config
   Host *
       UseKeychain yes
       AddKeysToAgent yes
   ```

## Getting Help

### Collecting Debug Information

When reporting issues, include:

1. **System information**:
   ```bash
   # OS version
   uname -a
   
   # Python version
   python --version
   
   # SSH Tools Suite version
   python -c "import ssh_tunnel_manager; print(ssh_tunnel_manager.__version__)"
   ```

2. **Error logs**:
   - Application logs
   - System logs
   - SSH debug output (`ssh -v`)

3. **Configuration files** (remove sensitive data)

### Where to Get Help

1. **Documentation**: Check this troubleshooting guide and user guides
2. **GitHub Issues**: Report bugs and feature requests
3. **Stack Overflow**: Use tag `ssh-tools-suite`
4. **Community Forum**: Join discussions and get help

### Creating Bug Reports

Include in bug reports:

1. **Steps to reproduce** the issue
2. **Expected behavior** vs actual behavior
3. **System information** and versions
4. **Log files** and error messages
5. **Screenshots** if applicable

This troubleshooting guide covers most common issues. If you encounter problems not listed here, please create a GitHub issue with detailed information.
