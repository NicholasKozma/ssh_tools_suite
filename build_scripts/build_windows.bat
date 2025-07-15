@echo off
REM Build script for SSH Tools Suite Windows executables

echo Building SSH Tools Suite executables...

REM Install PyInstaller if not already installed
pip install pyinstaller

REM Create output directories
if not exist "dist\executables" mkdir "dist\executables"
if not exist "build\temp" mkdir "build\temp"
if not exist "build\specs" mkdir "build\specs"

echo.
echo Building SSH Tunnel Manager GUI...
pyinstaller --name="SSH-Tunnel-Manager-GUI" ^
           --onefile ^
           --windowed ^
           --add-data="src\ssh_tunnel_manager\gui\assets;ssh_tunnel_manager\gui\assets" ^
           --hidden-import=PySide6 ^
           --hidden-import=PySide6.QtCore ^
           --hidden-import=PySide6.QtGui ^
           --hidden-import=PySide6.QtWidgets ^
           --hidden-import=ssh_tunnel_manager ^
           --hidden-import=ssh_tunnel_manager.gui ^
           --hidden-import=ssh_tunnel_manager.core ^
           --hidden-import=ssh_tools_common ^
           --distpath=dist\executables ^
           --workpath=build\temp ^
           --specpath=build\specs ^
           src\ssh_tunnel_manager\gui\__main__.py

echo.
echo Building SSH Tools Installer...
pyinstaller --name="SSH-Tools-Installer" ^
           --onefile ^
           --windowed ^
           --hidden-import=third_party_installer ^
           --hidden-import=third_party_installer.gui ^
           --hidden-import=third_party_installer.core ^
           --hidden-import=ssh_tools_common ^
           --distpath=dist\executables ^
           --workpath=build\temp ^
           --specpath=build\specs ^
           src\third_party_installer\__main__.py

echo.
echo Build complete! Check dist\executables\ for your executables.
echo.

REM List created files
dir /b dist\executables\

pause
