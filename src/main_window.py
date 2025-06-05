# main_window.py - Main application window
"""
Main window class for Keithley Dual Controller
Handles the overall UI layout, tabs, and coordination between components
"""

import sys
import time
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                            QStatusBar, QMessageBox, QApplication)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QAction, QFont

from src.core.instrument_control import InstrumentController
from src.ui.control_tab import ControlTab
from src.ui.plotting_tab import PlottingTab
from src.ui.settings_tab import SettingsTab
from src.ui.log_tab import LogTab


class KeithleyDualController(QMainWindow):
    """Main application window for controlling Keithley 2290-5 and 6485 instruments"""

    def __init__(self):
        super().__init__()

        # Create instrument controller
        self.instrument_controller = InstrumentController()

        # Initialize UI
        self.initUI()

        # Connect signals
        self.connectSignals()

        # Start update timer
        self.setupTimers()

    def initUI(self):
        """Initialize the user interface"""
        # Main window setup
        self.setWindowTitle("Keithley 2290-5 & 6485 High Voltage Lab Controller v1.0")
        self.setGeometry(100, 100, 1400, 900)

        # Create central widget with tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create tab widgets
        self.control_tab = ControlTab(self.instrument_controller)
        self.plotting_tab = PlottingTab(self.instrument_controller)
        self.settings_tab = SettingsTab(self.instrument_controller)
        self.log_tab = LogTab()

        # Add tabs to the tab widget
        self.tabs.addTab(self.control_tab, "Control Panel")
        self.tabs.addTab(self.plotting_tab, "Data Acquisition")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.log_tab, "Activity Log")

        # Create menu bar
        self.createMenuBar()

        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Ready - Please connect instruments")

    def createMenuBar(self):
        """Create the application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        export_action = QAction("Export Data to CSV", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.plotting_tab.exportDataToCSV)
        file_menu.addAction(export_action)

        clear_action = QAction("Clear Data", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.plotting_tab.clearData)
        file_menu.addAction(clear_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Connection menu
        conn_menu = menubar.addMenu("Connection")

        connect_all_action = QAction("Connect All Instruments", self)
        connect_all_action.triggered.connect(self.connectAllInstruments)
        conn_menu.addAction(connect_all_action)

        disconnect_all_action = QAction("Disconnect All Instruments", self)
        disconnect_all_action.triggered.connect(self.disconnectAllInstruments)
        conn_menu.addAction(disconnect_all_action)

        conn_menu.addSeparator()

        scan_action = QAction("Scan for Instruments", self)
        scan_action.triggered.connect(self.scanForInstruments)
        conn_menu.addAction(scan_action)

        # Safety menu
        safety_menu = menubar.addMenu("Safety")

        emergency_stop_action = QAction("EMERGENCY STOP", self)
        emergency_stop_action.setShortcut("F1")
        emergency_stop_action.triggered.connect(self.emergencyStop)
        safety_menu.addAction(emergency_stop_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

        commands_action = QAction("Command Reference", self)
        commands_action.triggered.connect(self.showCommandReference)
        help_menu.addAction(commands_action)

    def connectSignals(self):
        """Connect signals between components"""
        # Connect instrument status updates to UI
        self.instrument_controller.power_supply_connected.connect(
            self.control_tab.updatePowerSupplyStatus)
        self.instrument_controller.picoammeter_connected.connect(
            self.control_tab.updatePicoammeterStatus)

        # Data updates to plotting are handled in plotting_tab.connectSignals()

        # Connect log messages
        self.instrument_controller.log_message.connect(
            self.log_tab.addLogMessage)
        self.control_tab.log_message.connect(
            self.log_tab.addLogMessage)
        self.plotting_tab.log_message.connect(
            self.log_tab.addLogMessage)

        # Connect status bar updates
        self.instrument_controller.status_message.connect(
            self.statusBar.showMessage)

    def setupTimers(self):
        """Setup periodic update timers"""
        # Timer for periodic readings
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.updateReadings)
        self.updateTimer.start(1000)  # Update every second

    def updateReadings(self):
        """Update instrument readings periodically"""
        if self.instrument_controller.power_supply:
            try:
                # Update voltage reading
                voltage = self.instrument_controller.readVoltage()
                if voltage is not None:
                    self.control_tab.updateVoltageReading(voltage)
            except Exception as e:
                self.log_tab.addLogMessage(f"Error reading voltage: {str(e)}")

        if self.instrument_controller.picoammeter:
            try:
                # Update current reading
                current = self.instrument_controller.readCurrent()
                if current is not None:
                    self.control_tab.updateCurrentReading(current)
            except Exception as e:
                self.log_tab.addLogMessage(f"Error reading current: {str(e)}")

    def connectAllInstruments(self):
        """Connect to all instruments"""
        self.log_tab.addLogMessage("Attempting to connect to all instruments...")

        # Get GPIB addresses from settings
        ps_address = self.settings_tab.getPowerSupplyAddress()
        pa_address = self.settings_tab.getPicoammeterAddress()

        # Connect power supply
        ps_success = self.instrument_controller.connectPowerSupply(ps_address)
        if ps_success:
            self.log_tab.addLogMessage("[SUCCESS] Power supply connected successfully")
        else:
            self.log_tab.addLogMessage("[ERROR] Failed to connect power supply")

        # Connect picoammeter
        pa_success = self.instrument_controller.connectPicoammeter(pa_address)
        if pa_success:
            self.log_tab.addLogMessage("[SUCCESS] Picoammeter connected successfully")
        else:
            self.log_tab.addLogMessage("[ERROR] Failed to connect picoammeter")

        if ps_success and pa_success:
            self.statusBar.showMessage("All instruments connected")
        elif ps_success or pa_success:
            self.statusBar.showMessage("Some instruments connected")
        else:
            self.statusBar.showMessage("No instruments connected")

    def disconnectAllInstruments(self):
        """Disconnect from all instruments"""
        self.log_tab.addLogMessage("Disconnecting all instruments...")

        # Stop any ongoing data acquisition
        if self.plotting_tab.is_recording:
            self.plotting_tab.stopRecording()

        # Disconnect instruments
        self.instrument_controller.disconnectAllInstruments()

        self.statusBar.showMessage("All instruments disconnected")
        self.log_tab.addLogMessage("[SUCCESS] All instruments disconnected safely")

    def scanForInstruments(self):
        """Scan for available GPIB instruments"""
        self.log_tab.addLogMessage("Scanning for GPIB instruments...")
        self.statusBar.showMessage("Scanning for instruments...")

        try:
            instruments = self.instrument_controller.scanForInstruments()

            if instruments:
                self.log_tab.addLogMessage(f"Found {len(instruments)} instruments:")
                for addr, info in instruments.items():
                    self.log_tab.addLogMessage(f"  GPIB {addr}: {info}")
                self.statusBar.showMessage(f"Found {len(instruments)} instruments")
            else:
                self.log_tab.addLogMessage("No GPIB instruments found")
                self.statusBar.showMessage("No instruments found")

        except Exception as e:
            error_msg = f"Error during scan: {str(e)}"
            self.log_tab.addLogMessage(error_msg)
            self.statusBar.showMessage("Scan failed")

    def emergencyStop(self):
        """Emergency stop - immediately disable all outputs"""
        self.log_tab.addLogMessage("[EMERGENCY] EMERGENCY STOP ACTIVATED")

        try:
            # Stop data acquisition
            if self.plotting_tab.is_recording:
                self.plotting_tab.stopRecording()

            # Disable high voltage output
            if self.instrument_controller.power_supply:
                self.instrument_controller.disableOutput()
                self.log_tab.addLogMessage("[SUCCESS] High voltage output disabled")

            self.statusBar.showMessage("EMERGENCY STOP - All outputs disabled")

            # Show emergency stop dialog
            QMessageBox.warning(self, "Emergency Stop",
                              "Emergency stop activated!\n\n"
                              "High voltage output has been disabled.\n"
                              "Data acquisition has been stopped.\n\n"
                              "Please check your setup before continuing.")

        except Exception as e:
            self.log_tab.addLogMessage(f"[ERROR] Error during emergency stop: {str(e)}")

    def showAbout(self):
        """Show about dialog"""
        about_text = """
        <h2>Keithley Dual Instrument Controller</h2>
        <p><b>Version:</b> 1.0</p>
        <p><b>Purpose:</b> Control Keithley 2290-5 Power Supply and 6485 Picoammeter</p>

        <h3>Features:</h3>
        <ul>
        <li>GPIB instrument control using PyVISA</li>
        <li>Real-time current and voltage monitoring</li>
        <li>Live data plotting and acquisition</li>
        <li>Data export to CSV format</li>
        <li>Safety features and emergency stop</li>
        <li>Comprehensive activity logging</li>
        </ul>

        <p><b>Based on:</b> Official Keithley manuals and SCPI commands</p>
        <p><b>Built with:</b> PyQt6, PyVISA, PyQtGraph</p>

        <p><i>Always follow proper safety procedures when working with high voltage!</i></p>
        """

        QMessageBox.about(self, "About Keithley Controller", about_text)

    def showCommandReference(self):
        """Show SCPI command reference"""
        commands_text = """
        <h2>SCPI Command Reference</h2>

        <h3>Keithley 2290-5 Power Supply Commands:</h3>
        <table>
        <tr><td><b>VSET value</b></td><td>Set output voltage</td></tr>
        <tr><td><b>VOUT?</b></td><td>Query output voltage</td></tr>
        <tr><td><b>HVON</b></td><td>Enable high voltage output</td></tr>
        <tr><td><b>HVOF</b></td><td>Disable high voltage output</td></tr>
        <tr><td><b>VLIM value</b></td><td>Set voltage limit</td></tr>
        <tr><td><b>ILIM value</b></td><td>Set current limit</td></tr>
        <tr><td><b>SYST:LOC</b></td><td>Return to local control (restore front panel)</td></tr>
        <tr><td><b>*IDN?</b></td><td>Query instrument identification</td></tr>
        <tr><td><b>*RST</b></td><td>Reset to default settings</td></tr>
        </table>

        <h3>Keithley 6485 Picoammeter Commands:</h3>
        <table>
        <tr><td><b>READ?</b></td><td>Take a current reading</td></tr>
        <tr><td><b>CURR:RANG value</b></td><td>Set current range</td></tr>
        <tr><td><b>CURR:RANG:AUTO ON</b></td><td>Enable auto-ranging</td></tr>
        <tr><td><b>CURR:NPLC value</b></td><td>Set integration time</td></tr>
        <tr><td><b>SYST:ZCH ON</b></td><td>Enable zero check</td></tr>
        <tr><td><b>SYST:ZCOR:ACQ</b></td><td>Acquire zero correction</td></tr>
        <tr><td><b>SYST:AZER ON/OFF</b></td><td>Enable/disable auto zero correction</td></tr>
        <tr><td><b>SYST:LOC</b></td><td>Return to local control (restore front panel)</td></tr>
        </table>

        <p><i>See instrument manuals for complete command reference</i></p>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("Command Reference")
        msg.setText(commands_text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.exec()

    def closeEvent(self, event):
        """Handle application close event"""
        # Ask for confirmation
        reply = QMessageBox.question(self, 'Exit Application',
                                   'Are you sure you want to exit?\n\n'
                                   'This will disconnect all instruments and stop data acquisition.',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                   QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            # Stop any timers
            if hasattr(self, 'updateTimer'):
                self.updateTimer.stop()

            # Disconnect all instruments safely
            self.disconnectAllInstruments()

            # Log application shutdown
            from src.core.logger import get_logger
            logger = get_logger()
            logger.system("Application shutting down")

            # Clean up LogTab first to remove UI callback from logger
            if hasattr(self, 'log_tab'):
                self.log_tab.cleanup()

            # Disconnect signals to prevent memory leaks
            self.disconnectSignals()

            event.accept()
        else:
            event.ignore()

    def disconnectSignals(self):
        """Disconnect all signals to prevent memory leaks"""
        try:
            # Disconnect instrument controller signals
            self.instrument_controller.power_supply_connected.disconnect()
            self.instrument_controller.picoammeter_connected.disconnect()
            self.instrument_controller.data_ready.disconnect()
            self.instrument_controller.log_message.disconnect()
            self.instrument_controller.status_message.disconnect()

            # Stop timers
            self.updateTimer.stop()

        except (TypeError, RuntimeError):
            # This can happen if signals were never connected
            pass