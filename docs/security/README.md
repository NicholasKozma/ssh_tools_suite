# Security Documentation

This directory contains security-related documentation for the SSH Tools Suite.

## Security Issues

### Resolved Issues
- [Command Injection Vulnerability (Issue #3)](GITHUB_ISSUE_COMMAND_INJECTION.md) - Fixed in commit de331d8
  - **Severity**: High
  - **Component**: SSH Key Deployment
  - **Status**: ✅ Resolved

## Security Fixes
- [Security Fix Summary](SECURITY_FIX_SUMMARY.md) - Comprehensive overview of security improvements

## Security Guidelines

### Reporting Security Issues
If you discover a security vulnerability, please:
1. **Do not** create a public GitHub issue
2. Email security concerns to: Nicholas.Kozma@us.bosch.com
3. Include detailed reproduction steps
4. Allow time for investigation and fix before disclosure

### Security Best Practices
- All user input must be validated and sanitized
- Use parameterized queries/commands when possible
- Implement defense in depth
- Regular security reviews of code changes
- Follow principle of least privilege

## Security Review Checklist
- [ ] Input validation implemented
- [ ] Output encoding applied  
- [ ] Authentication and authorization checked
- [ ] Error handling doesn't leak information
- [ ] Logging includes security events
- [ ] Dependencies are up to date
