#!/bin/bash
# File: /home/user/project/sales_management_system/start_sales_system.sh

echo "Starting Sales Management System..."
echo

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    if ! command -v python &> /dev/null; then
        echo "Error: Python is not installed or not in PATH"
        echo "Please install Python 3.7 or higher"
        exit 1
    else
        PYTHON_CMD="python"
    fi
else
    PYTHON_CMD="python3"
fi

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python $REQUIRED_VERSION or higher is required"
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

# Check if the main application file exists
if [ ! -f "src/app.py" ]; then
    echo "Error: Application files not found"
    echo "Please ensure you're running this script from the project root directory"
    exit 1
fi

# Create data directory if it doesn't exist
mkdir -p data

# Make sure the script has execute permissions
chmod +x "$0"

# Run the application
echo "Starting application..."
$PYTHON_CMD src/app.py

# Check exit status
if [ $? -ne 0 ]; then
    echo
    echo "Application exited with an error"
    read -p "Press Enter to continue..."
fi