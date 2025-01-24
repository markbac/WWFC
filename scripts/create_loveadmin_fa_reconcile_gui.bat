@echo off
REM Set the script and resource paths
set SCRIPT=loveadmin_fa_reconcile_gui.py
set ICON=U5-6_Leaflet_2024-1-400x400.png

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    exit /b
)

REM Install required dependencies
echo Installing required Python dependencies...
pip install pyinstaller pillow pandas openpyxl --quiet

REM Build the executable
echo Building the executable...
pyinstaller --onefile --noconsole --add-data "%ICON%;." %SCRIPT%

REM Check if the build succeeded
if exist dist\%SCRIPT:~0,-3%.exe (
    echo Build succeeded. The executable is located in the "dist" folder.
) else (
    echo Build failed. Check the output for errors.
)
pause
