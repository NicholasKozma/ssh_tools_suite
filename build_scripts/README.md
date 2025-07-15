# Build Scripts for SSH Tools Suite

This directory contains build scripts for creating standalone executables.

## PyInstaller Build Scripts

### SSH Tunnel Manager GUI
```bash
python build_scripts/build_ssh_tunnel_manager.py
```

### Manual PyInstaller Commands

#### SSH Tunnel Manager GUI
```bash
pyinstaller --name="SSH-Tunnel-Manager-GUI" \
           --onefile \
           --windowed \
           --add-data="src/ssh_tunnel_manager/gui/assets;ssh_tunnel_manager/gui/assets" \
           --hidden-import=PySide6 \
           --hidden-import=ssh_tunnel_manager \
           --distpath=dist/executables \
           src/ssh_tunnel_manager/gui/__main__.py
```

#### SSH Tools Installer
```bash
pyinstaller --name="SSH-Tools-Installer" \
           --onefile \
           --windowed \
           --hidden-import=third_party_installer \
           --distpath=dist/executables \
           src/third_party_installer/__main__.py
```

## Output
- Executables will be created in `dist/executables/`
- Build files will be in `build/`
- Spec files will be in `build/specs/`

## Requirements
- Install PyInstaller: `pip install pyinstaller`
- Or install with dev dependencies: `pip install -e .[dev]`
