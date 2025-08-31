
"""
Main application entry point for the Sales Management System
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Change working directory to project root
os.chdir(project_root)

try:
    from src.views.main_window import MainWindow
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)

def main():
    """Main application function"""
    try:
        # Create and run the application
        app = MainWindow()
        
        # Handle window closing
        app.root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        print("Sales Management System started successfully!")
        app.run()
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Application closed")

if __name__ == "__main__":
    main()
