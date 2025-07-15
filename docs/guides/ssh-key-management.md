# SSH Key Management

Guide for managing SSH keys with the SSH Tools Suite.

## Overview

SSH key management is crucial for secure and efficient tunnel connections. This guide covers creating, managing, and using SSH keys with the SSH Tunnel Manager.

## SSH Key Types

### RSA Keys
The most common and widely supported key type:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### ED25519 Keys
Modern, more secure, and faster:

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

### ECDSA Keys
Elliptic curve keys, good performance:

```bash
ssh-keygen -t ecdsa -b 521 -C "your_email@example.com"
```

## Key Generation

### Using SSH Tools Suite

The SSH Tunnel Manager includes built-in key generation:

1. Open the SSH Tunnel Manager
2. Go to **Settings** → **SSH Keys**
3. Click **Generate New Key Pair**
4. Choose key type and size
5. Enter passphrase (recommended)
6. Save to secure location

### Command Line Generation

```bash
# Generate RSA key
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa_tunnels

# Generate ED25519 key
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519_tunnels

# Generate with specific comment
ssh-keygen -t ed25519 -C "tunnel-keys-$(date +%Y%m%d)" -f ~/.ssh/id_tunnel
```

## Key Management Best Practices

### Secure Storage

1. **Use passphrases**: Always protect private keys with strong passphrases
2. **Restrict permissions**: Set proper file permissions
   ```bash
   chmod 600 ~/.ssh/id_rsa
   chmod 644 ~/.ssh/id_rsa.pub
   ```
3. **Separate keys**: Use different keys for different purposes
4. **Backup safely**: Store backups in encrypted storage

### Key Organization

```
~/.ssh/
├── config                    # SSH client configuration
├── id_rsa_work              # Work-related tunnels
├── id_rsa_work.pub
├── id_rsa_personal          # Personal projects
├── id_rsa_personal.pub
├── id_ed25519_servers       # Server management
├── id_ed25519_servers.pub
└── authorized_keys          # Authorized public keys
```

## SSH Configuration

### Client Configuration (~/.ssh/config)

```bash
# Work servers
Host work-tunnel
    HostName work.company.com
    User tunnel_user
    IdentityFile ~/.ssh/id_rsa_work
    Port 22

# Personal servers
Host personal-server
    HostName personal.example.com
    User myuser
    IdentityFile ~/.ssh/id_ed25519_personal
    Port 2222

# Development environment
Host dev-*
    User developer
    IdentityFile ~/.ssh/id_rsa_dev
    ForwardAgent yes
```

### Using with SSH Tunnel Manager

Configure SSH keys in tunnel profiles:

```python
from ssh_tunnel_manager.core.models import TunnelConfig

config = TunnelConfig(
    name="secure-tunnel",
    ssh_host="server.example.com",
    ssh_port=22,
    ssh_username="user",
    ssh_key_path="~/.ssh/id_ed25519_tunnels",
    ssh_key_passphrase="your_passphrase",
    local_port=8080,
    remote_host="localhost",
    remote_port=80
)
```

## Public Key Deployment

### Manual Deployment

```bash
# Copy public key to server
ssh-copy-id -i ~/.ssh/id_rsa.pub user@server.com

# Manual copy
cat ~/.ssh/id_rsa.pub | ssh user@server.com "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### Using SSH Tools Suite

The tunnel manager can automatically deploy public keys:

1. Create new tunnel configuration
2. Enable **Auto-deploy public key**
3. Provide initial password for deployment
4. Future connections will use key authentication

## Key Rotation

### Regular Rotation Schedule

1. **Generate new keys** quarterly or annually
2. **Deploy new public keys** to all servers
3. **Update tunnel configurations** with new private keys
4. **Remove old public keys** after verification
5. **Securely delete old private keys**

### Rotation Script Example

```bash
#!/bin/bash
# Key rotation script

OLD_KEY="~/.ssh/id_rsa_old"
NEW_KEY="~/.ssh/id_rsa_new"

# Generate new key
ssh-keygen -t ed25519 -f "$NEW_KEY"

# Deploy to servers
for server in server1 server2 server3; do
    ssh-copy-id -i "$NEW_KEY.pub" "user@$server"
done

# Update SSH Tunnel Manager configurations
# (This would typically be done through the GUI)

echo "Key rotation complete. Please update tunnel configurations."
```

## Troubleshooting

### Permission Issues

```bash
# Fix SSH directory permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/id_*.pub
chmod 644 ~/.ssh/config
```

### Connection Issues

1. **Verify key format**:
   ```bash
   ssh-keygen -y -f ~/.ssh/id_rsa
   ```

2. **Test key authentication**:
   ```bash
   ssh -i ~/.ssh/id_rsa -v user@server.com
   ```

3. **Check server authorization**:
   ```bash
   ssh user@server.com "cat ~/.ssh/authorized_keys"
   ```

### Key Not Working

1. **Check SSH agent**:
   ```bash
   ssh-add -l
   ssh-add ~/.ssh/id_rsa
   ```

2. **Verify passphrase**:
   ```bash
   ssh-keygen -y -f ~/.ssh/id_rsa
   ```

3. **Check server logs**:
   ```bash
   sudo tail -f /var/log/auth.log
   ```

## Security Considerations

### Key Security

1. **Never share private keys**
2. **Use strong passphrases**
3. **Monitor key usage**
4. **Rotate keys regularly**
5. **Remove unused keys**

### Server-Side Security

1. **Disable password authentication**:
   ```bash
   # In /etc/ssh/sshd_config
   PasswordAuthentication no
   ChallengeResponseAuthentication no
   ```

2. **Restrict key types**:
   ```bash
   PubkeyAcceptedKeyTypes ssh-ed25519,rsa-sha2-512,rsa-sha2-256
   ```

3. **Enable key logging**:
   ```bash
   LogLevel VERBOSE
   ```

## Integration with CI/CD

### Automated Deployments

```yaml
# GitHub Actions example
- name: Setup SSH Key
  uses: webfactory/ssh-agent@v0.5.3
  with:
    ssh-private-key: ${% raw %}{{ secrets.SSH_PRIVATE_KEY }}{% endraw %}

- name: Deploy via SSH Tunnel
  run: |
    ssh-tunnel-manager create-tunnel \
      --name "deploy-tunnel" \
      --ssh-host "jump.company.com" \
      --ssh-user "deploy" \
      --local-port 3306 \
      --remote-host "db.internal" \
      --remote-port 3306
```

## Best Practices Summary

1. ✅ **Use ED25519 keys** for new installations
2. ✅ **Always use passphrases** on private keys
3. ✅ **Separate keys by purpose** (work, personal, etc.)
4. ✅ **Regular rotation schedule** (quarterly/annually)
5. ✅ **Monitor and audit** key usage
6. ✅ **Secure backup** of key materials
7. ✅ **Document key purposes** and expiration dates
8. ✅ **Remove old/unused keys** promptly

This guide ensures secure and efficient SSH key management for your tunnel operations.
