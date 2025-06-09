#!/usr/bin/env python3
# test_comprehensive.py - Comprehensive functionality tests
"""
Advanced tests for the Keithley Dual Controller application.
Includes mocking of instrument responses and specific functionality tests.
"""

import sys
import os
import time
import unittest
from unittest.mock import MagicMock, patch
import traceback

# Import test utilities
from tests.test_utils import setup_test_environment, teardown_test_environment

# Import the mock logger for testing
from tests.mock_logger import get_logger as get_mock_logger

# Import application modules
try:
    from src.core.instrument_control import InstrumentController, DataAcquisitionThread
    from src.ui.control_tab import ControlTab
    from src.ui.plotting_tab import PlottingTab
    from src.ui.settings_tab import SettingsTab
    from src.ui.log_tab import LogTab
    from PyQt6.QtWidgets import QApplication, QMessageBox
    from PyQt6.QtCore import Qt, QTimer
    from PyQt6.QtTest import QTest
except ImportError as e:
    print(f"Import Error: {e}")
    print("Make sure you run this from the project directory")
    sys.exit(1)

# Create QApplication for testing
app = QApplication([])

# Set up test environment
test_env = setup_test_environment()

class MockMessageBox:
    """Mock QMessageBox for testing"""
    @staticmethod
    def question(*args, **kwargs):
        # Always return "Yes"
        return QMessageBox.StandardButton.Yes

class MockResource:
    """Mock VISA Resource for testing"""
    def __init__(self, resource_name, is_power_supply=False):
        self.resource_name = resource_name
        self.is_power_supply = is_power_supply
        self.closed = False
        self.commands = {}
        self.setup_default_responses()

    def setup_default_responses(self):
        """Set up default responses for common commands"""
        if self.is_power_supply:
            self.commands["*IDN?"] = "KEITHLEY INSTRUMENTS INC.,2290-5,12345,1.234"
            self.commands["VOUT?"] = "1000.0"
            self.commands["HVON"] = ""
            self.commands["HVOF"] = ""
            self.commands["VOLT?"] = "1000.0"
            self.commands["VLIM?"] = "5000.0"
            self.commands["ILIM?"] = "5.25E-3"
        else:
            self.commands["*IDN?"] = "KEITHLEY INSTRUMENTS INC.,6485,67890,2.345"
            self.commands["READ?"] = "1.23456E-6"
            self.commands["SYST:ZCH ON"] = ""
            self.commands["SYST:ZCH OFF"] = ""
            self.commands["SYST:ZCOR"] = ""

    def write(self, command):
        """Mock write command"""
        # Store command for inspection
        return

    def query(self, command):
        """Mock query command"""
        if command in self.commands:
            return self.commands[command]
        elif command.startswith("VOLT "):
            # Handle voltage setting
            voltage = command.split(" ")[1]
            self.commands["VOLT?"] = voltage
            return ""
        else:
            return "ERROR"

    def close(self):
        """Mock close operation"""
        self.closed = True


class MockResourceManager:
    """Mock VISA ResourceManager for testing"""

    def __init__(self):
        self.resources = {
            "GPIB0::14::INSTR": MockResource("GPIB0::14::INSTR", is_power_supply=True),
            "GPIB0::22::INSTR": MockResource("GPIB0::22::INSTR", is_power_supply=False),
        }

    def list_resources(self):
        """Return list of available resources"""
        return list(self.resources.keys())

    def open_resource(self, resource_name):
        """Return a mock resource"""
        if resource_name in self.resources:
            return self.resources[resource_name]
        raise ValueError(f"Resource {resource_name} not found")

class TestInstrumentController(unittest.TestCase):
    """Test the InstrumentController class"""

    def setUp(self):
        """Set up test environment"""
        # Patch the ResourceManager
        self.patcher = patch('pyvisa.ResourceManager', return_value=MockResourceManager())
        self.mock_rm = self.patcher.start()

        # Patch the logger to avoid UI callback issues
        self.logger_patcher = patch('src.core.logger.get_logger', return_value=get_mock_logger())
        self.mock_logger = self.logger_patcher.start()

        # Create controller
        self.controller = InstrumentController()

    def tearDown(self):
        """Clean up after test"""
        self.patcher.stop()
        self.logger_patcher.stop()

    def test_connect_power_supply(self):
        """Test connecting to power supply"""
        result = self.controller.connectPowerSupply(14)
        self.assertTrue(result)
        self.assertIsNotNone(self.controller.power_supply)

    def test_connect_picoammeter(self):
        """Test connecting to picoammeter"""
        result = self.controller.connectPicoammeter(22)
        self.assertTrue(result)
        self.assertIsNotNone(self.controller.picoammeter)

    def test_voltage_setting(self):
        """Test setting voltage"""
        self.controller.connectPowerSupply(14)
        result = self.controller.setVoltage(2000)
        self.assertTrue(result)

    def test_enable_output(self):
        """Test enabling HV output"""
        self.controller.connectPowerSupply(14)
        result = self.controller.enableOutput()
        self.assertTrue(result)

    def test_disconnect(self):
        """Test disconnecting instruments"""
        self.controller.connectPowerSupply(14)
        self.controller.connectPicoammeter(22)
        self.controller.disconnectAllInstruments()
        self.assertIsNone(self.controller.power_supply)
        self.assertIsNone(self.controller.picoammeter)


class TestLogTab(unittest.TestCase):
    """Test the LogTab functionality"""

    def setUp(self):
        """Set up test environment"""
        # Patch the logger to avoid UI callback issues
        self.logger_patcher = patch('src.core.logger.get_logger', return_value=get_mock_logger())
        self.mock_logger = self.logger_patcher.start()

        # Create LogTab in testing mode to avoid UI callback issues
        self.log_tab = LogTab(testing_mode=True)

    def tearDown(self):
        """Clean up after test"""
        self.logger_patcher.stop()

    def test_add_log_message(self):
        """Test adding log messages"""
        # Mock the QMessageBox to always return "Yes"
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
            # Clear existing messages that might be added during initialization
            self.log_tab.clearLog()

        # Add specific test messages
        self.log_tab.addLogMessage("Test message", "INFO")
        self.log_tab.addLogMessage("Error message", "ERROR")
        self.log_tab.addLogMessage("Warning message", "WARNING")

        # Check counters
        # Since clearing adds a message, there should be 4 messages total (3 added + 1 system)
        self.assertEqual(int(self.log_tab.total_messages_label.text()), 4)
        self.assertEqual(int(self.log_tab.error_count_label.text()), 1)
        self.assertEqual(int(self.log_tab.warning_count_label.text()), 1)

    def test_log_limit(self):
        """Test log entry limiting"""
        # Temporarily set max entries to a small number for testing
        original_max = self.log_tab.max_log_entries
        self.log_tab.max_log_entries = 5

        # Clear any existing log entries
        with patch('PyQt6.QtWidgets.QMessageBox.question', return_value=QMessageBox.StandardButton.Yes):
            self.log_tab.clearLog()

        # Add more than max messages
        for i in range(10):
            self.log_tab.addLogMessage(f"Test message {i}", "INFO")

        # Reset max entries
        self.log_tab.max_log_entries = original_max

        # There should be no more than max_entries in the log
        # Due to how log entries are stored in HTML format, we can only check
        # if the count is less than or equal to the max_entries plus any overhead
        total_messages = int(self.log_tab.total_messages_label.text())
        self.assertLessEqual(total_messages, 5)


class TestControlTab(unittest.TestCase):
    """Test the ControlTab functionality"""

    def setUp(self):
        """Set up test environment"""
        # Patch the logger to avoid UI callback issues
        self.logger_patcher = patch('src.core.logger.get_logger', return_value=get_mock_logger())
        self.mock_logger = self.logger_patcher.start()

        # Create a controller with mocked resources
        self.patcher = patch('pyvisa.ResourceManager', return_value=MockResourceManager())
        self.mock_rm = self.patcher.start()
        self.controller = InstrumentController()
        self.control_tab = ControlTab(self.controller)

    def tearDown(self):
        """Clean up after test"""
        self.patcher.stop()
        self.logger_patcher.stop()

    def test_update_readings(self):
        """Test updating voltage and current readings"""
        # Update readings
        self.control_tab.updateVoltageReading(2500.0)
        self.control_tab.updateCurrentReading(1.23e-3)  # milliamps

        # Check display
        self.assertEqual(self.control_tab.voltage_reading.text(), "2500.0 V")
        self.assertEqual(self.control_tab.current_reading.text(), "1.230 mA")

        # Test various current scales
        test_currents = [
            (2.34e-6, "2.340 µA"),  # microamps
            (3.45e-9, "3.450 nA"),  # nanoamps
            (4.56e-12, "4.560 pA"),  # picoamps
            (5.67e-15, "5.670e-15 A"),  # femtoamps
        ]

        for current, expected in test_currents:
            self.control_tab.updateCurrentReading(current)
            self.assertEqual(self.control_tab.current_reading.text(), expected)

    def test_update_connection_status(self):
        """Test connection status updates"""
        # Test disconnected status
        self.control_tab.updatePowerSupplyStatus(False, "")
        self.assertFalse(self.control_tab.voltage_spinbox.isEnabled())
        self.assertFalse(self.control_tab.enable_hv_btn.isEnabled())

        # Test connected status
        self.control_tab.updatePowerSupplyStatus(True, "KEITHLEY 2290-5")
        self.assertTrue(self.control_tab.voltage_spinbox.isEnabled())
        self.assertTrue(self.control_tab.enable_hv_btn.isEnabled())


class TestPlottingTab(unittest.TestCase):
    """Test the PlottingTab functionality"""

    def setUp(self):
        """Set up test environment"""
        # Patch the logger to avoid UI callback issues
        self.logger_patcher = patch('src.core.logger.get_logger', return_value=get_mock_logger())
        self.mock_logger = self.logger_patcher.start()

        # Create a controller with mocked resources
        self.patcher = patch('pyvisa.ResourceManager', return_value=MockResourceManager())
        self.mock_rm = self.patcher.start()
        self.controller = InstrumentController()
        self.plotting_tab = PlottingTab(self.controller)

    def tearDown(self):
        """Clean up after test"""
        self.patcher.stop()
        self.logger_patcher.stop()

    def test_data_management(self):
        """Test data point management"""
        # Start recording
        self.plotting_tab.is_recording = True  # Directly set the flag

        # Add data points
        test_points = 10
        for i in range(test_points):
            self.plotting_tab.addDataPoint(i, i * 1e-6, i * 100)

        # Check data arrays
        self.assertEqual(len(self.plotting_tab.time_data), test_points)
        self.assertEqual(len(self.plotting_tab.current_data), test_points)
        self.assertEqual(len(self.plotting_tab.voltage_data), test_points)

        # Test clearing data
        self.plotting_tab.clearData()
        self.assertEqual(len(self.plotting_tab.time_data), 0)
        self.assertEqual(len(self.plotting_tab.current_data), 0)
        self.assertEqual(len(self.plotting_tab.voltage_data), 0)


def run_all_tests():
    """Run all tests with user-friendly output"""
    print("=" * 70)
    print("Keithley Dual Controller - Comprehensive Tests")
    print("=" * 70)
    print("\nRunning comprehensive tests for the application...")
    print("This will test functionality without requiring actual hardware.\n")

    # Create and run the test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTest(loader.loadTestsFromTestCase(TestInstrumentController))
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

    if result.failures:
        print("\nFailures:")
        for failure in result.failures:
            print(f"- {failure[0]}")
            print(f"  {failure[1]}")

    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"- {error[0]}")
            print(f"  {error[1]}")

    if not result.failures and not result.errors:
        print("\n🎉 All tests passed! The application should function correctly.")
        print("\n💡 Next steps:")
        print("  - Run the basic tests: python test_basic.py")
        print("  - Start the application: python main.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Troubleshooting tips:")
        print("  - Make sure all dependencies are installed: pip install -r requirements.txt")
        print("  - Check for code modifications that might have broken functionality")

    return result.wasSuccessful()

if __name__ == "__main__":
    run_all_tests()
