# main.py - Main application entry point
"""
Keithley 2290-5 & 6485 Dual Instrument Controller
Main application entry point and window setup

Author: Assistant
Date: 2025
License: MIT
"""

import sys
import os
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add project root to Python path for proper imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now import modules with the corrected path
from src.main_window import KeithleyDualController
from src.ui.theme import apply_app_style
from src.core.logger import get_logger

# Global exception handler to log uncaught exceptions
def exception_handler(exctype, value, tb):
    """Handle uncaught exceptions"""
    logger = get_logger()
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    logger.error(f"Uncaught exception: {error_msg}")

    # Show error dialog
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Icon.Critical)
    error_dialog.setText("An unexpected error occurred")
    error_dialog.setInformativeText(str(value))
    error_dialog.setDetailedText(error_msg)
    error_dialog.setWindowTitle("Application Error")
    error_dialog.exec()

    # Call the default exception handler
    sys.__excepthook__(exctype, value, tb)

def main():
    """Main application entry point"""
    # Set up global exception handler
    sys.excepthook = exception_handler

    # Initialize logger
    logger = get_logger()
    logger.system("Application starting")

    try:
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("Keithley Dual Controller")
        app.setApplicationVersion("1.0")
        app.setOrganizationName("Laboratory Instruments")

        # Set application style
        app.setStyle("Fusion")

        # Apply our custom dark theme
        apply_app_style(app)

        # Create and show the main window
        window = KeithleyDualController()
        window.show()

        # Start the application event loop
        return app.exec()

    except Exception as e:
        logger.error(f"Error during application startup: {str(e)}")
        traceback.print_exc()

        # Show error dialog
        if 'app' in locals():
            error_dialog = QMessageBox()
            error_dialog.setIcon(QMessageBox.Icon.Critical)
            error_dialog.setText("Failed to start application")
            error_dialog.setInformativeText(str(e))
            error_dialog.setDetailedText(traceback.format_exc())
            error_dialog.setWindowTitle("Startup Error")
            error_dialog.exec()

        return 1

if __name__ == "__main__":
    sys.exit(main())