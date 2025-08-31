@echo off
REM File: /home/user/project/sales_management_system/start_sales_system.bat

echo Starting Sales Management System...
echo.

REM Check if Python is installed
set PYTHON_CMD=
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    goto :python_found
)

python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    goto :python_found
)

python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    goto :python_found
)

echo Error: Python is not installed or not in PATH
echo Please install Python 3.7 or higher
pause
exit /b 1

:python_found
REM Change to the script directory
cd /d "%~dp0"

REM Check if the main application file exists
if not exist "src\app.py" (
    echo Error: Application files not found
    echo Please ensure you're running this script from the project root directory
    pause
    exit /b 1
)

REM Create data directory if it doesn't exist
if not exist "data" mkdir data

REM Run the application
echo Starting application...
%PYTHON_CMD% src\app.py

REM Pause to see any error messages
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)