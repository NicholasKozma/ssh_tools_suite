# PX Corporate Proxy Tool

This directory contains the PX proxy tool that enables SSH Tools Suite to work in corporate environments with proxy authentication.

## Files:

- **px.exe** - Main PX executable (bundled with SSH Tools Suite)
- **px.ini** - Configuration file template
- **README.md** - This documentation

## Configuration:

The `px.ini` file contains proxy settings. Key settings include:

```ini
[proxy]
server = your-proxy-server.com:8080
port = 3128
username = 
auth = 
noproxy = 127.0.0.*,10.*.*.*,192.168.*.*

[settings]
workers = 3
threads = 8
foreground = 0
```

## Usage:

PX is automatically detected by the third-party installer when:
1. The bundled version is present (tools/px/px.exe)
2. Or installed system-wide (C:\px\px.exe)
3. Or installed in Program Files

Configure proxy settings through the Third Party Installer GUI:
- Open Third Party Installer
- Click "Configure Proxy Settings"
- Enable proxy and configure PX settings
- PX will handle corporate proxy authentication automatically

## License:

PX is open source software. See the original project at:
https://github.com/genotrance/px
