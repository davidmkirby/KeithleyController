#!/usr/bin/env python3
# mock_logger.py - Mock logger for testing
"""
This file provides a mock logger for testing purposes.
It should be used to replace the logger.py module during tests.
"""

class MockLogger:
    """Mock logger for testing"""
    def __init__(self):
        self.logs = []
        self.ui_callback = None

    def debug(self, message):
        self.logs.append(("DEBUG", message))

    def info(self, message):
        self.logs.append(("INFO", message))

    def warning(self, message):
        self.logs.append(("WARNING", message))

    def error(self, message):
        self.logs.append(("ERROR", message))

    def system(self, message):
        self.logs.append(("SYSTEM", message))

    def exception(self, message):
        self.logs.append(("ERROR", f"Exception: {message}"))

    def log(self, message, level="INFO"):
        self.logs.append((level, message))

    def set_ui_callback(self, callback):
        self.ui_callback = callback

    def setup_file_logging(self, log_dir="logs", max_size_mb=10, backup_count=5):
        """Mock file logging setup"""
        return True

# Create singleton instance
mock_logger = MockLogger()

def get_logger():
    """Get the mock logger instance"""
    return mock_logger

# Make sure the function is exported
__all__ = ['get_logger']
