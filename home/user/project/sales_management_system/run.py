
#!/usr/bin/env python3
"""
Cross-platform startup script for the Sales Management System
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print(f"Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    return True

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import tkinter
        return True
    except ImportError:
        print("Error: tkinter is not available")
        print("Please install tkinter:")
        print("  - On Ubuntu/Debian: sudo apt-get install python3-tk")
        print("  - On CentOS/RHEL: sudo yum install tkinter")
        print("  - On macOS: tkinter should be included with Python")
        print("  - On Windows: tkinter should be included with Python")
        return False

def setup_environment():
    """Setup the environment for running the application"""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Add project root to Python path
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Create necessary directories
    (script_dir / "data").mkdir(exist_ok=True)
    
    return script_dir

def main():
    """Main function to start the application"""
    print("=" * 50)
    print("Sales Management System")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return 1
    
    # Check dependencies
    if not check_dependencies():
        input("Press Enter to exit...")
        return 1
    
    # Setup environment
    try:
        project_dir = setup_environment()
        print(f"Project directory: {project_dir}")
    except Exception as e:
        print(f"Error setting up environment: {e}")
        input("Press Enter to exit...")
        return 1
    
    # Check if application files exist
    app_file = project_dir / "src" / "app.py"
    if not app_file.exists():
        print(f"Error: Application file not found: {app_file}")
        print("Please ensure all files are properly installed")
        input("Press Enter to exit...")
        return 1
    
    # Start the application
    try:
        print("Starting application...")
        print()
        
        # Import and run the application
        from src.app import main as app_main
        app_main()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to exit...")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
