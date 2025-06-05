#!/usr/bin/env python3
# logger.py - System-wide logging module
"""
Provides a centralized logging system for the Keithley Dual Controller application.
Handles both file-based logging and UI logging integration.
"""

import os
import sys
import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler


class Logger:
    """Centralized logging system with both file and UI integration"""

    # Log levels mapped to standard Python logging levels
    LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "SYSTEM": logging.INFO  # Custom level mapped to INFO for file logging
    }

    # Singleton instance
    _instance = None

    def __new__(cls):
        """Create or return the singleton instance"""
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the logger system once"""
        if self._initialized:
            return

        # Create logger
        self.logger = logging.getLogger("KeithleyController")
        self.logger.setLevel(logging.DEBUG)

        # Flag to track initialization
        self._initialized = True

        # UI callback for log messages (set by LogTab)
        self.ui_callback = None

        # Setup console logging with UTF-8 encoding
        self.setup_console_logging()

        # Setup file logging by default
        self.setup_file_logging()

        # Log the initialization
        self.log("Logger system initialized", "SYSTEM")

    def setup_console_logging(self):
        """Setup console logging with proper encoding handling"""
        try:
            # Create console handler
            console_handler = logging.StreamHandler()

            # Create a custom formatter that handles encoding issues
            class SafeFormatter(logging.Formatter):
                def format(self, record):
                    # Format the record normally first
                    formatted = super().format(record)

                    # Make the message safe for console output
                    try:
                        # Try to encode to the console encoding
                        if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
                            formatted.encode(sys.stdout.encoding)
                        return formatted
                    except UnicodeEncodeError:
                        # Replace any remaining problematic Unicode characters
                        safe_message = formatted.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                        return safe_message

            # Use the safe formatter
            console_formatter = SafeFormatter('%(levelname)s: %(message)s')
            console_handler.setFormatter(console_formatter)

            # Set console handler to only show WARNING and above to reduce noise
            console_handler.setLevel(logging.WARNING)

            # Add the handler to the logger
            self.logger.addHandler(console_handler)

            return True

        except Exception as e:
            print(f"Error setting up console logging: {str(e)}")
            return False

    def setup_file_logging(self, log_dir="logs", max_size_mb=10, backup_count=5):
        """Setup file-based logging"""
        try:
            # Create logs directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            # Generate log filename with date
            today = datetime.now().strftime("%Y%m%d")
            log_file = os.path.join(log_dir, f"keithley_controller_{today}.log")

            # Set up rotating file handler (10MB max, 5 backups)
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=max_size_mb * 1024 * 1024,
                backupCount=backup_count
            )

            # Create formatter with timestamp
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(file_handler)

            self.log(f"File logging enabled: {log_file}", "SYSTEM")
            return True

        except Exception as e:
            # Can't use self.log here due to potential infinite recursion
            print(f"Error setting up file logging: {str(e)}")
            return False

    def set_ui_callback(self, callback):
        """Set the UI callback function for displaying logs"""
        self.ui_callback = callback
        self.log("UI logging integration enabled", "SYSTEM")

    def remove_ui_callback(self):
        """Remove the UI callback to prevent access to destroyed UI components"""
        if hasattr(self, 'ui_callback') and self.ui_callback:
            self.log("UI logging integration disabled", "SYSTEM")
            self.ui_callback = None

    def log(self, message, level="INFO"):
        """Log a message to both file and UI"""
        # Handle Unicode encoding issues by providing safe fallbacks
        safe_message = self._make_message_safe(message)

        # Log to file
        log_level = self.LEVELS.get(level, logging.INFO)
        self.logger.log(log_level, safe_message)

        # Log to UI if callback is set (use original message with emojis)
        if self.ui_callback:
            try:
                self.ui_callback(message, level)
            except Exception as e:
                # Prevent recursive errors if UI callback fails
                print(f"UI logging error: {str(e)} - Original message: {message}")
                # If error mentions deleted C/C++ object, remove the callback
                if "deleted" in str(e) or "destroyed" in str(e):
                    print("UI component appears to be destroyed, removing UI callback")
                    self.ui_callback = None
                # Log this error but don't try to use UI callback
                self.logger.error(f"Error in UI logging callback: {str(e)}", exc_info=True)

    def _make_message_safe(self, message):
        """Make a message safe for console output by replacing problematic characters"""
        try:
            # Try to encode to the console encoding to see if it works
            if hasattr(sys.stdout, 'encoding') and sys.stdout.encoding:
                message.encode(sys.stdout.encoding)
            return message
        except UnicodeEncodeError:
            # Replace any remaining problematic Unicode characters
            safe_message = message.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            return safe_message

    def debug(self, message):
        """Log a debug message"""
        self.log(message, "DEBUG")

    def info(self, message):
        """Log an info message"""
        self.log(message, "INFO")

    def warning(self, message):
        """Log a warning message"""
        self.log(message, "WARNING")

    def error(self, message):
        """Log an error message"""
        self.log(message, "ERROR")

    def system(self, message):
        """Log a system message"""
        self.log(message, "SYSTEM")

    def exception(self, message):
        """Log an exception with traceback"""
        self.logger.exception(message)
        if self.ui_callback:
            import traceback
            error_with_tb = f"{message}\n{traceback.format_exc()}"
            self.ui_callback(error_with_tb, "ERROR")


# Create singleton instance
system_logger = Logger()


def get_logger():
    """Get the application-wide logger instance"""
    return system_logger
