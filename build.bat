@echo off
pyinstaller --onefile main.py
xcopy /d resources dist\resources
DEL /f build
pause
