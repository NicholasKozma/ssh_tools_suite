# Tools Directory

This directory contains bundled tools and scripts for SSH Tools Suite.

## Directory Structure:

```
tools/
├── README.md           # This documentation
├── px/                 # PX Corporate Proxy (bundled)
│   ├── px.exe          # Main executable
│   ├── px.ini          # Configuration template
│   └── README.md       # PX-specific documentation
├── psexec/             # PsExec tools (optional bundled versions)
│   ├── PsExec.exe      # 32-bit version
│   ├── PsExec64.exe    # 64-bit version
│   └── README.md       # PsExec documentation
└── scripts/            # Helper scripts
    ├── setup_px.bat    # PX setup script
    ├── debug_ssh.py    # SSH debugging utility
    └── verify_structure.py  # Structure verification
```

## Bundled Tools:

### PX Corporate Proxy
- **Status**: Bundled with package
- **Purpose**: Corporate proxy authentication
- **Auto-detected**: Yes
- **Configuration**: Via Third Party Installer GUI

### PsExec (Optional)
- **Status**: Downloaded automatically by installer
- **Purpose**: Remote command execution
- **Bundled versions**: Provided as fallback
- **Primary source**: Microsoft Sysinternals download

## Installation Behavior:

1. **PX**: Always available (bundled)
2. **PsExec**: Downloaded from Microsoft during installation
3. **FFmpeg**: Downloaded during installation
4. **VLC**: Downloaded during installation (optional)

## Usage:

Tools are automatically detected and managed by the Third Party Installer.
Users interact with tools through the SSH Tools Suite GUI applications.

## License Information:

- **PX**: Open source (see px/README.md)
- **PsExec**: Microsoft proprietary (see psexec/README.md)
- **Scripts**: Part of SSH Tools Suite

### License:
`px.exe` is licensed under the MIT License. See `../licenses/THIRD_PARTY_LICENSES.md` for full license text and attribution.

## Detection Order:
The installer checks for PsExec in this order:
1. `tools\PsExec.exe` (repository local)
2. `tools\PsExec64.exe` (repository local 64-bit)
3. `C:\PsTools\PsExec.exe` (your current location)
4. System PATH
5. Program Files
6. System32

## License Note:
PsExec is owned by Microsoft. Please ensure you comply with Microsoft's license terms when redistributing.
Download from: https://docs.microsoft.com/en-us/sysinternals/downloads/psexec
