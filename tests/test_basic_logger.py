#!/usr/bin/env python3
# test_basic_logger.py - Test the new logging system
"""
Basic tests for the new logging system
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# We need a QApplication for UI components
from PyQt6.QtWidgets import QApplication
app = QApplication([])

# Create a mock logger
mock_logger = MagicMock()
mock_logger.logs = []
mock_logger.info = lambda msg: mock_logger.logs.append(("INFO", msg))
mock_logger.error = lambda msg: mock_logger.logs.append(("ERROR", msg))
mock_logger.warning = lambda msg: mock_logger.logs.append(("WARNING", msg))
mock_logger.system = lambda msg: mock_logger.logs.append(("SYSTEM", msg))
mock_logger.debug = lambda msg: mock_logger.logs.append(("DEBUG", msg))
mock_logger.log = lambda msg, lvl="INFO": mock_logger.logs.append((lvl, msg))
mock_logger.set_ui_callback = lambda callback: None

# Patch the get_logger function
mock_get_logger = MagicMock(return_value=mock_logger)

# Apply the patch
patch('src.core.logger.get_logger', mock_get_logger).start()

# Now import the components that use logger
from src.ui.log_tab import LogTab

class TestLoggerIntegration(unittest.TestCase):
    """Test the integration of the new logging system"""

    def setUp(self):
        """Set up test environment"""
        # Clear any existing logs
        mock_logger.logs = []

        # Create LogTab in testing mode
        self.log_tab = LogTab(testing_mode=True)

    def test_log_messages(self):
        """Test adding log messages through the LogTab"""
        # Add messages to the log
        self.log_tab.addLogMessage("Test info message", "INFO")
        self.log_tab.addLogMessage("Test error message", "ERROR")
        self.log_tab.addLogMessage("Test warning message", "WARNING")

        # Check the log entries
        self.assertEqual(len(self.log_tab.log_entries), 3)
        self.assertEqual(self.log_tab.log_entries[0][1], "INFO")
        self.assertEqual(self.log_tab.log_entries[0][2], "Test info message")
        self.assertEqual(self.log_tab.log_entries[1][1], "ERROR")
        self.assertEqual(self.log_tab.log_entries[1][2], "Test error message")
        self.assertEqual(self.log_tab.log_entries[2][1], "WARNING")
        self.assertEqual(self.log_tab.log_entries[2][2], "Test warning message")

if __name__ == "__main__":
    print("Running logger integration tests...")
    unittest.main(verbosity=2)
