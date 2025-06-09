#!/usr/bin/env python3
# test_logger.py - Test the new logging system
"""
Tests for the new logger.py module and its integration with other components.
Tests both file-based logging and UI integration.
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
import time
from datetime import datetime
import sys

# Add project root to sys.path to allow for src imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Importing modules for logger tests...")

# Make sure we're using the real logger, not the mock
if 'mock_logger' in sys.modules:
    del sys.modules['mock_logger']

# Ensure Logger singleton is reset
import importlib
if 'logger' in sys.modules:
    importlib.reload(sys.modules['logger'])

# Create QApplication for UI tests
from PyQt6.QtWidgets import QApplication
app = QApplication([])

# Import the logger - make sure we get the real one
from src.core.logger import get_logger, Logger

# Now the log_tab which uses the logger
from src.ui.log_tab import LogTab

print("Modules imported successfully.")


class TestLoggerFunctionality(unittest.TestCase):
    """Test the Logger class functionality"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logs_")

        # Reset the Logger singleton for testing
        Logger._instance = None
        self.logger = get_logger()

        # Configure the logger to use the test directory
        self.logger.setup_file_logging(log_dir=self.test_log_dir)

    def tearDown(self):
        """Clean up after test"""
        # Clean up temporary directory
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)

    def test_singleton_pattern(self):
        """Test that logger implements singleton pattern"""
        logger1 = get_logger()
        logger2 = get_logger()
        self.assertIs(logger1, logger2)
        self.assertIs(self.logger, logger1)

    def test_log_levels(self):
        """Test different log levels"""
        # Log messages at different levels
        self.logger.debug("Debug test message")
        self.logger.info("Info test message")
        self.logger.warning("Warning test message")
        self.logger.error("Error test message")
        self.logger.system("System test message")

        # Check that log file was created
        log_files = os.listdir(self.test_log_dir)
        self.assertGreaterEqual(len(log_files), 1)

        # Read the log file to check contents
        log_file_path = os.path.join(self.test_log_dir, log_files[0])
        with open(log_file_path, 'r') as f:
            log_content = f.read()

        # Check that messages were logged
        self.assertIn("Debug test message", log_content)
        self.assertIn("Info test message", log_content)
        self.assertIn("Warning test message", log_content)
        self.assertIn("Error test message", log_content)
        self.assertIn("System test message", log_content)

    def test_exception_logging(self):
        """Test exception logging"""
        try:
            # Raise an exception
            1/0
        except Exception as e:
            self.logger.exception("Test exception occurred")

        # Check that log file contains exception info
        log_files = os.listdir(self.test_log_dir)
        log_file_path = os.path.join(self.test_log_dir, log_files[0])
        with open(log_file_path, 'r') as f:
            log_content = f.read()

        self.assertIn("Test exception occurred", log_content)
        self.assertIn("ZeroDivisionError", log_content)

    def test_ui_callback(self):
        """Test UI callback functionality"""
        # Create a mock callback
        mock_callback = MagicMock()

        # Set the callback
        self.logger.set_ui_callback(mock_callback)

        # Log a message
        self.logger.info("UI callback test")

        # Check that callback was called
        mock_callback.assert_called_with("UI callback test", "INFO")


class TestLogTabIntegration(unittest.TestCase):
    """Test the integration between Logger and LogTab"""

    def setUp(self):
        """Set up test environment"""
        # Create a temporary directory for logs
        self.test_log_dir = tempfile.mkdtemp(prefix="test_logs_")

        # Reset the Logger singleton for testing
        Logger._instance = None
        self.logger = get_logger()

        # Configure the logger to use the test directory
        self.logger.setup_file_logging(log_dir=self.test_log_dir)

        # Create LogTab in non-testing mode to test integration
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=1):  # Mock QMessageBox
            self.log_tab = LogTab(testing_mode=False)

    def tearDown(self):
        """Clean up after test"""
        # Clean up temporary directory
        if os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)

    def test_log_message_propagation(self):
        """Test that log messages propagate to LogTab"""
        # Clear any existing messages
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=1):
            self.log_tab.clearLog()

        # Initial count
        initial_count = int(self.log_tab.total_messages_label.text())

        # Log messages through the logger
        self.logger.info("Test info message")
        self.logger.error("Test error message")
        self.logger.warning("Test warning message")

        # Check that messages were added to LogTab
        final_count = int(self.log_tab.total_messages_label.text())
        self.assertEqual(final_count, initial_count + 3)

        # Check error and warning counters
        self.assertEqual(int(self.log_tab.error_count_label.text()), 1)
        self.assertEqual(int(self.log_tab.warning_count_label.text()), 1)


def run_all_tests():
    """Run all logger tests with user-friendly output"""
    print("=" * 70)
    print("Keithley Dual Controller - Logger Tests")
    print("=" * 70)
    print("\nRunning tests for the new logging system...")

    try:
        # Create and run the test suite
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        # Add test cases
        print("Loading test cases...")
        suite.addTest(loader.loadTestsFromTestCase(TestLoggerFunctionality))
        suite.addTest(loader.loadTestsFromTestCase(TestLogTabIntegration))

        # Run the tests
        print("Running tests...")
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        # Summary
        print("\n" + "=" * 70)
        print("TEST RESULTS SUMMARY")
        print("=" * 70)
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")

        if not result.failures and not result.errors:
            print("\n✅ All logger tests passed successfully!")
        else:
            print("\n⚠️ Some tests failed. Check the output above for details.")

        return result.wasSuccessful()
    except Exception as e:
        print(f"Error running tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    run_all_tests()
