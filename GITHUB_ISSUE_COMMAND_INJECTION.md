# Security Issue: Command Injection Vulnerability in SSH Key Deployment

## Summary
**Severity**: 🔴 **HIGH** - Critical Security Vulnerability  
**Component**: SSH Key Deployment (`ssh_key_deployment.py`)  
**Type**: Command Injection  
**Status**: Identified and Ready for Fix

## Description
A critical command injection vulnerability exists in the SSH key deployment functionality within the SSH Tunnel Manager. The vulnerability allows potentially malicious content in SSH public keys to execute arbitrary shell commands on both the client system and remote servers.

## Affected Code
**File**: `src/ssh_tunnel_manager/gui/components/ssh_key_deployment.py`  
**Methods**: 
- `_try_sshpass_method()` (lines ~150-180)
- `_try_paramiko_method()` (lines ~200-230)
- `_try_ssh_copy_id()` (lines ~100-140)

## Vulnerability Details

### Root Cause
User-provided SSH public key content is directly interpolated into shell commands without proper escaping:

```python
# VULNERABLE CODE:
f"echo '{self.public_key_content}' >> ~/.ssh/authorized_keys"
```

### Attack Vector
An attacker could provide a malicious "SSH public key" containing shell metacharacters:
```
ssh-rsa AAAAB3... comment'; rm -rf /; echo 'pwned
```

This would result in command execution:
```bash
echo 'ssh-rsa AAAAB3... comment'; rm -rf /; echo 'pwned' >> ~/.ssh/authorized_keys
```

### Impact
- **Client-side code execution**: Malicious commands executed on user's machine
- **Server-side code execution**: Commands executed on target SSH servers
- **Data destruction**: Potential for destructive commands (`rm -rf`, etc.)
- **Privilege escalation**: Commands run with SSH user privileges
- **Information disclosure**: Access to sensitive files and system information

## Affected Methods

### 1. `_try_sshpass_method()`
```python
# Lines ~150-180
commands = [
    "mkdir -p ~/.ssh",
    "chmod 700 ~/.ssh",
    f"echo '{self.public_key_content}' >> ~/.ssh/authorized_keys",  # VULNERABLE
    # ...
]
```

### 2. `_try_paramiko_method()`
```python
# Lines ~200-230
commands = [
    "mkdir -p ~/.ssh",
    "chmod 700 ~/.ssh", 
    f"echo '{self.public_key_content}' >> ~/.ssh/authorized_keys",  # VULNERABLE
    # ...
]
```

### 3. `_try_ssh_copy_id()` (Password Script)
```python
# Lines ~110-120
f.write(f'#!/bin/bash\necho "{self.password}"\n')  # POTENTIALLY VULNERABLE
```

## Reproduction Steps
1. Launch SSH Tunnel Manager
2. Access SSH Key Deployment dialog
3. Input malicious public key content: `ssh-rsa test'; echo "INJECTED"; echo 'end`
4. Attempt deployment
5. Observe command injection execution

## Security Requirements for Fix

### Input Validation
- [ ] Validate SSH public key format
- [ ] Check for valid key types (ssh-rsa, ssh-ed25519, etc.)
- [ ] Detect and reject dangerous characters
- [ ] Validate base64 key data

### Command Safety
- [ ] Use `shlex.quote()` for shell escaping
- [ ] Replace shell commands with direct file operations where possible
- [ ] Implement parameterized command execution

### Defense in Depth
- [ ] Multiple validation layers
- [ ] Secure fallback methods
- [ ] Error handling without information disclosure

## Proposed Solution

### Phase 1: Input Validation
```python
def _validate_public_key(self, key_content: str) -> bool:
    """Validate SSH public key format and safety."""
    # 1. Format validation
    # 2. Key type validation  
    # 3. Dangerous character detection
    # 4. Base64 validation
```

### Phase 2: Command Safety
```python
# Replace vulnerable code:
f"echo '{self.public_key_content}' >> ~/.ssh/authorized_keys"

# With safe escaping:
escaped_key = shlex.quote(self.public_key_content.strip())
f"echo {escaped_key} >> ~/.ssh/authorized_keys"
```

### Phase 3: SFTP Implementation
```python
# Replace shell commands with direct file operations
sftp = ssh.open_sftp()
with sftp.open('.ssh/authorized_keys', 'a') as f:
    f.write(validated_key + '\n')
```

## Testing Requirements

### Security Tests
- [ ] Test with injection payloads
- [ ] Verify key validation rejects malicious input
- [ ] Test all deployment methods (ssh-copy-id, sshpass, paramiko)
- [ ] Verify error handling doesn't leak information

### Functional Tests  
- [ ] Test with legitimate SSH keys (RSA, ED25519, ECDSA)
- [ ] Test key deployment to various server configurations
- [ ] Test error scenarios and recovery

## Timeline
- **Discovery**: Immediate
- **Fix Development**: 1-2 hours
- **Testing**: 2-4 hours  
- **Review**: 1 hour
- **Deployment**: Immediate after review

## Priority Justification
This is a **critical security vulnerability** that:
- Allows arbitrary code execution
- Affects both client and server systems
- Has a simple attack vector
- Could lead to complete system compromise
- Must be fixed before any public release

## Related Security Considerations
- Review all other user input handling for similar issues
- Implement security testing in CI/CD pipeline
- Add input sanitization guidelines to development docs
- Consider security audit of entire codebase

---
**Reporter**: Security Review  
**Date**: July 15, 2025  
**Classification**: Critical Security Vulnerability  
**CVE**: TBD (if publishing publicly)
