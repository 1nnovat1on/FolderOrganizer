@echo off
setlocal
cd /d "%~dp0"
python -m PyInstaller --noconfirm --clean --onefile --windowed --name "FolderOrganizer" --paths . launcher.py
endlocal
