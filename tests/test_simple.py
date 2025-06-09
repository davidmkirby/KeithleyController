#!/usr/bin/env python3
# test_simple.py - Simple functionality tests
"""
Simplified tests for the Keithley Dual Controller application.
Tests basic functionality without complex mocking.
"""

import sys
import os
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

# Import PyQt
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

# Create application instance for testing
app = QApplication([])

# Import our modules
from src.ui.control_tab import ControlTab
from src.ui.log_tab import LogTab
from src.ui.plotting_tab import PlottingTab
from src.ui.settings_tab import SettingsTab

class SimpleInstrumentControllerMock:
    """Simple mock for InstrumentController"""
    def __init__(self):
        self.power_supply = None
        self.picoammeter = None
        self.power_supply_connected = MagicMock()
        self.picoammeter_connected = MagicMock()
        self.data_ready = MagicMock()
        self.log_message = MagicMock()
        self.status_message = MagicMock()

    def setVoltage(self, voltage):
        return True

    def enableOutput(self):
        return True

    def disableOutput(self):
        return True

    def setCurrentRange(self, range_text):
        return True

    def setIntegrationTime(self, nplc):
        return True

    def performZeroCheck(self):
        return True

class TestLogTab(unittest.TestCase):
    """Test LogTab functionality"""

    def setUp(self):
        """Set up test environment"""
        self.log_tab = LogTab()

        # Override QMessageBox to avoid dialogs during tests
        self.orig_question = QMessageBox.question
        QMessageBox.question = lambda *args, **kwargs: QMessageBox.StandardButton.Yes

    def tearDown(self):
        """Clean up after test"""
        QMessageBox.question = self.orig_question

    def test_add_log_message(self):
        """Test adding log messages"""
        # Clear log first
        self.log_tab.log_text.clear()
        self.log_tab.total_messages_label.setText("0")
        self.log_tab.error_count_label.setText("0")
        self.log_tab.warning_count_label.setText("0")

        # Add messages
        self.log_tab.addLogMessage("Test info message", "INFO")
        self.log_tab.addLogMessage("Test error message", "ERROR")
        self.log_tab.addLogMessage("Test warning message", "WARNING")

        # Get the log content
        log_content = self.log_tab.log_text.toPlainText()

        # Check that messages are in the log
        self.assertIn("Test info message", log_content)
        self.assertIn("Test error message", log_content)
        self.assertIn("Test warning message", log_content)

class TestControlTab(unittest.TestCase):
    """Test ControlTab functionality"""

    def setUp(self):
        """Set up test environment"""
        self.controller = SimpleInstrumentControllerMock()
        self.control_tab = ControlTab(self.controller)

    def test_voltage_reading(self):
        """Test voltage reading display"""
        self.control_tab.updateVoltageReading(1000.0)
        self.assertEqual(self.control_tab.voltage_reading.text(), "1000.0 V")

    def test_current_reading_formats(self):
        """Test current reading formatting with different units"""
        # Test milliamps (mA)
        self.control_tab.updateCurrentReading(0.002)
        self.assertEqual(self.control_tab.current_reading.text(), "2.000 mA")

        # Test microamps (µA)
        self.control_tab.updateCurrentReading(0.000002)
        self.assertEqual(self.control_tab.current_reading.text(), "2.000 µA")

        # Test nanoamps (nA)
        self.control_tab.updateCurrentReading(0.000000002)
        self.assertEqual(self.control_tab.current_reading.text(), "2.000 nA")

        # Test picoamps (pA)
        self.control_tab.updateCurrentReading(0.000000000002)
        self.assertEqual(self.control_tab.current_reading.text(), "2.000 pA")

        # Test very small values
        self.control_tab.updateCurrentReading(0.000000000000002)
        self.assertEqual(self.control_tab.current_reading.text(), "2.000e-15 A")

class TestPlottingTab(unittest.TestCase):
    """Test PlottingTab functionality"""

    def setUp(self):
        """Set up test environment"""
        self.controller = SimpleInstrumentControllerMock()
        self.plotting_tab = PlottingTab(self.controller)

    def test_data_points(self):
        """Test adding and clearing data points"""
        # Start recording (directly set flag to avoid UI interaction)
        self.plotting_tab.is_recording = True

        # Add data points
        for i in range(5):
            self.plotting_tab.addDataPoint(i, i * 0.001, i * 100)

        # Check data arrays
        self.assertEqual(len(self.plotting_tab.time_data), 5)
        self.assertEqual(len(self.plotting_tab.current_data), 5)
        self.assertEqual(len(self.plotting_tab.voltage_data), 5)

        # Check values
        self.assertEqual(self.plotting_tab.time_data[2], 2)
        self.assertEqual(self.plotting_tab.current_data[2], 0.002)
        self.assertEqual(self.plotting_tab.voltage_data[2], 200)

        # Clear data
        self.plotting_tab.clearData()

        # Check arrays are empty
        self.assertEqual(len(self.plotting_tab.time_data), 0)
        self.assertEqual(len(self.plotting_tab.current_data), 0)
        self.assertEqual(len(self.plotting_tab.voltage_data), 0)

if __name__ == '__main__':
    print("=" * 70)
    print("Keithley Dual Controller - Simple Unit Tests")
    print("=" * 70)
    print("Running simplified unit tests...\n")

    unittest.main(verbosity=2)

def run_all_tests():
    """Run all simple tests for integration with run_tests.py"""
    print("=" * 70)
    print("Keithley Dual Controller - Simple Unit Tests")
    print("=" * 70)
    print("Running simplified unit tests...\n")

    # Create and run the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(loader.loadTestsFromTestCase(TestLogTab))
    suite.addTest(loader.loadTestsFromTestCase(TestControlTab))
    suite.addTest(loader.loadTestsFromTestCase(TestPlottingTab))

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    success = len(result.failures) == 0 and len(result.errors) == 0
    if success:
        print("\n🎉 All simple tests passed!")
    else:
        print("\n⚠️ Some tests failed. Check the output above for details.")

    return success
