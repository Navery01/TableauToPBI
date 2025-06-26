#!/usr/bin/env python3
"""
Tableau to Power BI Converter - Main Application Entry Point

This is the main entry point for the Tableau to Power BI converter application.
It launches the GUI interface for converting Tableau workbooks to Power BI templates.

Usage:
    python main.py

Requirements:
    - PySide6 (for GUI)
    - tableauhyperapi (for Tableau file parsing)
    - pbi-tools (optional, for .pbit compilation)

Author: Tableau to Power BI Converter Team
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

def setup_environment():
    """Setup the application environment and paths"""
    # Get the application root directory
    app_root = Path(__file__).parent
    
    # Add the src directory to Python path
    src_path = app_root / "src"
    if src_path.exists():
        sys.path.insert(0, str(src_path))
    
    # Add the app directory to Python path
    app_path = app_root / "src" / "app"
    if app_path.exists():
        sys.path.insert(0, str(app_path))
    
    # Add the extractors directory to Python path
    extractors_path = app_root / "src" / "extractors" / "TB2PBI"
    if extractors_path.exists():
        sys.path.insert(0, str(extractors_path))
    
    return app_root

def check_dependencies():
    """Check for required dependencies"""
    missing_deps = []
    
    try:
        import PySide6
    except ImportError:
        missing_deps.append("PySide6")
    
    try:
        import tableauhyperapi
    except ImportError:
        missing_deps.append("tableauhyperapi")
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPlease install missing dependencies using:")
        print("   pip install " + " ".join(missing_deps))
        return False
    
    return True

def main():
    """Main application entry point"""
    print("Tableau to Power BI Converter")
    print("=" * 50)
    
    # Setup environment
    app_root = setup_environment()
    print(f"Application root: {app_root}")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Import and run the application
    try:
        from PySide6.QtWidgets import QApplication
        from app import MainWindow
        
        print("✅ Dependencies loaded successfully")
        print("🚀 Starting GUI application...")
        
        # Create the application
        app = QApplication(sys.argv)
        app.setApplicationName("Tableau to Power BI Converter")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("TableauToPBI")
        
        # Create and show the main window
        window = MainWindow()
        window.show()
        
        print("✅ GUI application started successfully")
        print("   Use the interface to convert Tableau files to Power BI format")
        
        # Run the application
        sys.exit(app.exec())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Please ensure all modules are properly installed")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
