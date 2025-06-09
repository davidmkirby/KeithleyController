#!/usr/bin/env python3
# test_utils.py - Testing utilities
"""
Testing utilities for Keithley Dual Controller tests
Provides mocking and utility functions for tests
"""

from unittest.mock import MagicMock, patch
import sys


class MockLogger:
    """Mock logger for testing"""
    def __init__(self):
        self.logs = []

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
        pass


def patch_logger():
    """Patch the get_logger function to return a mock logger"""
    mock_logger = MockLogger()
    patcher = patch('src.core.logger.get_logger', return_value=mock_logger)
    return patcher, mock_logger


def setup_test_environment():
    """Set up testing environment

    This function should be called at the beginning of each test module
    to ensure a consistent testing environment.
    """
    # Patch common components
    logger_patcher, mock_logger = patch_logger()
    logger_patcher.start()

    return {
        "logger_patcher": logger_patcher,
        "mock_logger": mock_logger
    }


def teardown_test_environment(patches):
    """Clean up testing environment

    This function should be called at the end of each test module
    to clean up any patches or resources created during testing.
    """
    # Stop patchers
    for name, patcher in patches.items():
        if not name.endswith("_mock"):
            patcher.stop()
