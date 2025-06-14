# control_tab.py - Instrument control interface
"""
Control tab for managing Keithley 2290-5 and 6485 instruments
Provides direct control interface for voltage, current, and safety settings
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QPushButton, QDoubleSpinBox,
                            QComboBox, QCheckBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from src.ui.theme import AppTheme


class ControlTab(QWidget):
    """Control tab for instrument operation"""

    # Signals
    log_message = pyqtSignal(str)

    def __init__(self, instrument_controller):
        super().__init__()
        self.instrument_controller = instrument_controller
        self.setupUI()
        self.connectSignals()

    def setupUI(self):
        """Setup the control tab user interface"""
        layout = QVBoxLayout(self)

        # Connection status group
        layout.addWidget(self.createConnectionGroup())

        # Power supply controls
        layout.addWidget(self.createPowerSupplyGroup())

        # Picoammeter controls
        layout.addWidget(self.createPicoammeterGroup())

        # Live readings
        layout.addWidget(self.createReadingsGroup())

        # Add stretch to push everything to top
        layout.addStretch()

    def createConnectionGroup(self):
        """Create the connection status group"""
        group = QGroupBox("Instrument Connection Status")
        layout = QGridLayout()

        # Power Supply Connection
        layout.addWidget(QLabel("Power Supply (2290-5):"), 0, 0)
        self.ps_status = QLabel("Not Connected")
        self.ps_status.setFrameShape(QFrame.Shape.Panel)
        self.ps_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ps_status.setStyleSheet(AppTheme.get_status_style("disconnected"))
        self.ps_status.setMinimumHeight(35)
        layout.addWidget(self.ps_status, 0, 1)

        ps_button_layout = QHBoxLayout()
        self.ps_connect_btn = QPushButton("Connect")
        self.ps_connect_btn.clicked.connect(self.connectPowerSupply)
        self.ps_connect_btn.setMinimumHeight(35)
        ps_button_layout.addWidget(self.ps_connect_btn)

        self.ps_disconnect_btn = QPushButton("Disconnect")
        self.ps_disconnect_btn.clicked.connect(self.disconnectPowerSupply)
        self.ps_disconnect_btn.setEnabled(False)
        self.ps_disconnect_btn.setMinimumHeight(35)
        ps_button_layout.addWidget(self.ps_disconnect_btn)

        layout.addLayout(ps_button_layout, 0, 2)

        # Picoammeter Connection
        layout.addWidget(QLabel("Picoammeter (6485):"), 1, 0)
        self.pa_status = QLabel("Not Connected")
        self.pa_status.setFrameShape(QFrame.Shape.Panel)
        self.pa_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pa_status.setStyleSheet(AppTheme.get_status_style("disconnected"))
        self.pa_status.setMinimumHeight(35)
        layout.addWidget(self.pa_status, 1, 1)

        pa_button_layout = QHBoxLayout()
        self.pa_connect_btn = QPushButton("Connect")
        self.pa_connect_btn.clicked.connect(self.connectPicoammeter)
        self.pa_connect_btn.setMinimumHeight(35)
        pa_button_layout.addWidget(self.pa_connect_btn)

        self.pa_disconnect_btn = QPushButton("Disconnect")
        self.pa_disconnect_btn.clicked.connect(self.disconnectPicoammeter)
        self.pa_disconnect_btn.setEnabled(False)
        self.pa_disconnect_btn.setMinimumHeight(35)
        pa_button_layout.addWidget(self.pa_disconnect_btn)

        layout.addLayout(pa_button_layout, 1, 2)

        group.setLayout(layout)
        return group

    def createPowerSupplyGroup(self):
        """Create power supply control group"""
        group = QGroupBox("Power Supply Control (2290-5)")
        layout = QGridLayout()

        # Voltage setting
        layout.addWidget(QLabel("Output Voltage (V):"), 0, 0)
        self.voltage_spinbox = QDoubleSpinBox()
        self.voltage_spinbox.setRange(0, 5000)
        self.voltage_spinbox.setDecimals(0)  # No decimal places for 2290-5
        self.voltage_spinbox.setSingleStep(10)
        self.voltage_spinbox.setMinimumHeight(35)
        self.voltage_spinbox.setFont(QFont("Arial", 11))
        self.voltage_spinbox.setEnabled(False)
        layout.addWidget(self.voltage_spinbox, 0, 1)

        self.set_voltage_btn = QPushButton("Set Voltage")
        self.set_voltage_btn.clicked.connect(self.setVoltage)
        self.set_voltage_btn.setEnabled(False)
        self.set_voltage_btn.setMinimumHeight(35)
        layout.addWidget(self.set_voltage_btn, 0, 2)

        # Voltage limit setting
        layout.addWidget(QLabel("Voltage Limit (V):"), 1, 0)
        self.voltage_limit_spinbox = QDoubleSpinBox()
        self.voltage_limit_spinbox.setRange(0, 5000)
        self.voltage_limit_spinbox.setValue(5000)  # Safe default
        self.voltage_limit_spinbox.setDecimals(0)  # No decimal places for 2290-5
        self.voltage_limit_spinbox.setSingleStep(100)
        self.voltage_limit_spinbox.setMinimumHeight(35)
        self.voltage_limit_spinbox.setFont(QFont("Arial", 11))
        self.voltage_limit_spinbox.setEnabled(False)
        layout.addWidget(self.voltage_limit_spinbox, 1, 1)

        self.set_vlimit_btn = QPushButton("Set Limit")
        self.set_vlimit_btn.clicked.connect(self.setVoltageLimit)
        self.set_vlimit_btn.setEnabled(False)
        self.set_vlimit_btn.setMinimumHeight(35)
        layout.addWidget(self.set_vlimit_btn, 1, 2)

        # Current limit setting
        layout.addWidget(QLabel("Current Limit (mA):"), 2, 0)
        self.current_limit_spinbox = QDoubleSpinBox()
        self.current_limit_spinbox.setRange(0.001, 5.25)
        self.current_limit_spinbox.setValue(5.0)  # Safe default
        self.current_limit_spinbox.setDecimals(3)
        self.current_limit_spinbox.setSingleStep(0.1)
        self.current_limit_spinbox.setMinimumHeight(35)
        self.current_limit_spinbox.setFont(QFont("Arial", 11))
        self.current_limit_spinbox.setEnabled(False)
        layout.addWidget(self.current_limit_spinbox, 2, 1)

        self.set_ilimit_btn = QPushButton("Set I-Limit")
        self.set_ilimit_btn.clicked.connect(self.setCurrentLimit)
        self.set_ilimit_btn.setEnabled(False)
        self.set_ilimit_btn.setMinimumHeight(35)
        layout.addWidget(self.set_ilimit_btn, 2, 2)

        # Timer controls
        layout.addWidget(QLabel("HV Timer (hours):"), 3, 0)
        self.timer_spinbox = QDoubleSpinBox()
        self.timer_spinbox.setRange(0.0, 24.0)
        self.timer_spinbox.setValue(4.0)  # Default 4 hours
        self.timer_spinbox.setDecimals(1)
        self.timer_spinbox.setSingleStep(0.5)
        self.timer_spinbox.setMinimumHeight(35)
        self.timer_spinbox.setFont(QFont("Arial", 11))
        self.timer_spinbox.setEnabled(False)
        layout.addWidget(self.timer_spinbox, 3, 1)

        # Timer control buttons
        timer_button_layout = QHBoxLayout()
        self.enable_hv_with_timer_btn = QPushButton("Enable with Timer")
        self.enable_hv_with_timer_btn.clicked.connect(self.enableOutputWithTimer)
        self.enable_hv_with_timer_btn.setEnabled(False)
        self.enable_hv_with_timer_btn.setMinimumHeight(35)
        timer_button_layout.addWidget(self.enable_hv_with_timer_btn)

        self.stop_timer_btn = QPushButton("Stop Timer")
        self.stop_timer_btn.clicked.connect(self.stopTimer)
        self.stop_timer_btn.setEnabled(False)
        self.stop_timer_btn.setMinimumHeight(35)
        timer_button_layout.addWidget(self.stop_timer_btn)

        layout.addLayout(timer_button_layout, 3, 2)

        # Timer status display
        layout.addWidget(QLabel("Timer Status:"), 4, 0)
        self.timer_status = QLabel("Inactive")
        self.timer_status.setFrameShape(QFrame.Shape.Panel)
        self.timer_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_status.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.timer_status.setMinimumHeight(35)
        self.timer_status.setProperty("timerStatus", "inactive")
        layout.addWidget(self.timer_status, 4, 1, 1, 2)

        # HV Output control - prominent styling for safety
        hv_layout = QHBoxLayout()

        self.enable_hv_btn = QPushButton("ENABLE HV OUTPUT")
        self.enable_hv_btn.setMinimumHeight(50)
        self.enable_hv_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.enable_hv_btn.setProperty("hvButton", "enable")
        self.enable_hv_btn.clicked.connect(self.enableOutput)
        self.enable_hv_btn.setEnabled(False)
        hv_layout.addWidget(self.enable_hv_btn)

        self.disable_hv_btn = QPushButton("DISABLE HV OUTPUT")
        self.disable_hv_btn.setMinimumHeight(50)
        self.disable_hv_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.disable_hv_btn.setProperty("hvButton", "disable")
        self.disable_hv_btn.clicked.connect(self.disableOutput)
        self.disable_hv_btn.setEnabled(False)
        hv_layout.addWidget(self.disable_hv_btn)

        layout.addLayout(hv_layout, 5, 0, 1, 3)

        group.setLayout(layout)
        return group

    def createPicoammeterGroup(self):
        """Create picoammeter control group"""
        group = QGroupBox("Picoammeter Control (6485)")
        layout = QGridLayout()

        # Range setting
        layout.addWidget(QLabel("Current Range:"), 0, 0)
        self.current_range_combo = QComboBox()
        self.current_range_combo.addItems([
            "AUTO", "2e-9", "2e-8", "2e-7", "2e-6",
            "2e-5", "2e-4", "2e-3", "2e-2"
        ])
        self.current_range_combo.setMinimumHeight(35)
        self.current_range_combo.setEnabled(False)
        self.current_range_combo.currentTextChanged.connect(self.setCurrentRange)
        layout.addWidget(self.current_range_combo, 0, 1)

        # Integration time (NPLC)
        layout.addWidget(QLabel("Integration Time:"), 1, 0)
        self.integration_combo = QComboBox()
        self.integration_combo.addItems(["0.01", "0.1", "1", "10"])
        self.integration_combo.setCurrentIndex(2)  # Default to 1 PLC
        self.integration_combo.setMinimumHeight(35)
        self.integration_combo.setEnabled(False)
        self.integration_combo.currentTextChanged.connect(self.setIntegrationTime)
        layout.addWidget(self.integration_combo, 1, 1)

        # Zero check controls
        zero_layout = QHBoxLayout()
        self.zero_check_btn = QPushButton("Zero Check")
        self.zero_check_btn.setEnabled(False)
        self.zero_check_btn.setMinimumHeight(35)
        self.zero_check_btn.clicked.connect(self.performZeroCheck)
        zero_layout.addWidget(self.zero_check_btn)

        self.auto_zero_check = QCheckBox("Auto Zero")
        self.auto_zero_check.setEnabled(False)
        self.auto_zero_check.stateChanged.connect(self.setAutoZero)
        zero_layout.addWidget(self.auto_zero_check)

        layout.addLayout(zero_layout, 0, 2, 2, 1)

        group.setLayout(layout)
        return group

    def createReadingsGroup(self):
        """Create live readings display group"""
        group = QGroupBox("Live Measurements")
        layout = QGridLayout()

        # Voltage reading
        layout.addWidget(QLabel("Output Voltage:"), 0, 0)
        self.voltage_reading = QLabel("-- V")
        self.voltage_reading.setFrameShape(QFrame.Shape.Panel)
        self.voltage_reading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.voltage_reading.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.voltage_reading.setMinimumHeight(40)
        self.voltage_reading.setProperty("readingType", "voltage")
        layout.addWidget(self.voltage_reading, 0, 1)

        # Output status
        layout.addWidget(QLabel("HV Status:"), 0, 2)
        self.output_status = QLabel("DISABLED")
        self.output_status.setProperty("outputStatus", "disabled")
        self.output_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.output_status.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.output_status.setMinimumHeight(40)
        layout.addWidget(self.output_status, 0, 3)

        # Current reading
        layout.addWidget(QLabel("Current Reading:"), 1, 0)
        self.current_reading = QLabel("-- A")
        self.current_reading.setFrameShape(QFrame.Shape.Panel)
        self.current_reading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_reading.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.current_reading.setMinimumHeight(40)
        self.current_reading.setProperty("readingType", "current")
        layout.addWidget(self.current_reading, 1, 1)

        # Connection indicator
        layout.addWidget(QLabel("Instruments:"), 1, 2)
        self.connection_indicator = QLabel("Disconnected")
        self.connection_indicator.setFrameShape(QFrame.Shape.Panel)
        self.connection_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connection_indicator.setMinimumHeight(40)
        self.connection_indicator.setProperty("connectionStatus", "disconnected")
        layout.addWidget(self.connection_indicator, 1, 3)

        group.setLayout(layout)
        return group

    def connectSignals(self):
        """Connect internal signals"""
        # Connect to instrument controller signals
        self.instrument_controller.power_supply_connected.connect(
            self.updatePowerSupplyStatus)
        self.instrument_controller.picoammeter_connected.connect(
            self.updatePicoammeterStatus)
        self.instrument_controller.timer_updated.connect(
            self.updateTimerStatus)
        self.instrument_controller.timer_expired.connect(
            self.onTimerExpired)

    # Connection methods
    def connectPowerSupply(self):
        """Connect to power supply"""
        # Use default address for 2290-5
        default_address = 14
        self.log_message.emit(f"Connecting to power supply at GPIB address {default_address}...")

        success = self.instrument_controller.connectPowerSupply(default_address)
        if success:
            self.log_message.emit("Power supply connected successfully")
        else:
            self.log_message.emit("ERROR: Power supply connection failed")

    def disconnectPowerSupply(self):
        """Disconnect power supply using improved safe disconnect"""
        if self.instrument_controller.power_supply:
            try:
                # Use the improved safe disconnect method
                self.instrument_controller._safeDisconnectPowerSupply()
                self.instrument_controller.power_supply = None
                self.log_message.emit("Power supply disconnected")
            except Exception as e:
                self.log_message.emit(f"WARNING: Error disconnecting power supply: {str(e)}")
                self.instrument_controller.power_supply = None

            # Emit disconnection signal to update UI
            self.instrument_controller.power_supply_connected.emit(False, "")

    def connectPicoammeter(self):
        """Connect to picoammeter"""
        # Use default address for 6485
        default_address = 22
        self.log_message.emit(f"Connecting to picoammeter at GPIB address {default_address}...")

        success = self.instrument_controller.connectPicoammeter(default_address)
        if success:
            self.log_message.emit("Picoammeter connected successfully")
        else:
            self.log_message.emit("ERROR: Picoammeter connection failed")

    def disconnectPicoammeter(self):
        """Disconnect picoammeter using improved safe disconnect"""
        if self.instrument_controller.picoammeter:
            try:
                # Use the improved safe disconnect method
                self.instrument_controller._safeDisconnectPicoammeter()
                self.instrument_controller.picoammeter = None
                self.log_message.emit("Picoammeter disconnected")
            except Exception as e:
                self.log_message.emit(f"WARNING: Error disconnecting picoammeter: {str(e)}")
                self.instrument_controller.picoammeter = None

            # Emit disconnection signal to update UI
            self.instrument_controller.picoammeter_connected.emit(False, "")

    # Control methods
    def setVoltage(self):
        """Set output voltage"""
        voltage = self.voltage_spinbox.value()
        if self.instrument_controller.setVoltage(voltage):
            self.log_message.emit(f"Voltage set to {voltage}V")

    def setVoltageLimit(self):
        """Set voltage limit"""
        limit = self.voltage_limit_spinbox.value()
        if self.instrument_controller.setVoltageLimit(limit):
            self.log_message.emit(f"Voltage limit set to {limit}V")

    def setCurrentLimit(self):
        """Set current limit"""
        limit = self.current_limit_spinbox.value()
        if self.instrument_controller.setCurrentLimit(limit):
            self.log_message.emit(f"Current limit set to {limit}mA")

    def enableOutput(self):
        """Enable high voltage output"""
        if self.instrument_controller.enableOutput():
            self.output_status.setText("ENABLED")
            self.output_status.setProperty("outputStatus", "enabled")
            self.output_status.style().unpolish(self.output_status)
            self.output_status.style().polish(self.output_status)
            self.enable_hv_btn.setEnabled(False)
            self.disable_hv_btn.setEnabled(True)

    def disableOutput(self):
        """Disable high voltage output"""
        if self.instrument_controller.disableOutput():
            self.output_status.setText("DISABLED")
            self.output_status.setProperty("outputStatus", "disabled")
            self.output_status.style().unpolish(self.output_status)
            self.output_status.style().polish(self.output_status)
            self.enable_hv_btn.setEnabled(True)
            self.disable_hv_btn.setEnabled(False)
            self.enable_hv_with_timer_btn.setEnabled(True)
            self.stop_timer_btn.setEnabled(False)

    def enableOutputWithTimer(self):
        """Enable high voltage output with timer"""
        timer_hours = self.timer_spinbox.value()
        timer_seconds = int(timer_hours * 3600)  # Convert hours to seconds

        if timer_seconds <= 0:
            self.log_message.emit("ERROR: Timer duration must be greater than 0")
            return

        if self.instrument_controller.enableOutputWithTimer(timer_seconds):
            self.output_status.setText("ENABLED")
            self.output_status.setProperty("outputStatus", "enabled")
            self.output_status.style().unpolish(self.output_status)
            self.output_status.style().polish(self.output_status)
            self.enable_hv_btn.setEnabled(False)
            self.enable_hv_with_timer_btn.setEnabled(False)
            self.disable_hv_btn.setEnabled(True)
            self.stop_timer_btn.setEnabled(True)

    def stopTimer(self):
        """Stop the HV timer"""
        self.instrument_controller.stopHVTimer()
        self.stop_timer_btn.setEnabled(False)
        if "ENABLED" in self.output_status.text():
            self.enable_hv_with_timer_btn.setEnabled(False)  # HV is still on, just no timer
        else:
            self.enable_hv_with_timer_btn.setEnabled(True)   # HV is off, can start with timer

    def setCurrentRange(self, range_text):
        """Set picoammeter current range"""
        self.instrument_controller.setCurrentRange(range_text)

    def setIntegrationTime(self, nplc_text):
        """Set integration time"""
        nplc = float(nplc_text)
        self.instrument_controller.setIntegrationTime(nplc)

    def performZeroCheck(self):
        """Perform zero check"""
        self.instrument_controller.performZeroCheck()

    def setAutoZero(self, state):
        """Set auto zero state"""
        enabled = state == 2  # Qt.Checked = 2
        self.instrument_controller.setAutoZero(enabled)

    # Update methods
    def updatePowerSupplyStatus(self, connected, info):
        """Update power supply connection status"""
        if connected:
            self.ps_status.setText(f"Connected")
            self.ps_status.setProperty("connectionStatus", "connected")
            self.ps_status.style().unpolish(self.ps_status)
            self.ps_status.style().polish(self.ps_status)
            self.ps_connect_btn.setEnabled(False)
            self.ps_disconnect_btn.setEnabled(True)

            # Enable controls
            self.voltage_spinbox.setEnabled(True)
            self.voltage_limit_spinbox.setEnabled(True)
            self.current_limit_spinbox.setEnabled(True)
            self.set_voltage_btn.setEnabled(True)
            self.set_vlimit_btn.setEnabled(True)
            self.set_ilimit_btn.setEnabled(True)
            self.enable_hv_btn.setEnabled(True)
            self.timer_spinbox.setEnabled(True)
            self.enable_hv_with_timer_btn.setEnabled(True)
        else:
            self.ps_status.setText("Not Connected")
            self.ps_status.setProperty("connectionStatus", "disconnected")
            self.ps_status.style().unpolish(self.ps_status)
            self.ps_status.style().polish(self.ps_status)
            self.ps_connect_btn.setEnabled(True)
            self.ps_disconnect_btn.setEnabled(False)

            # Disable controls
            self.voltage_spinbox.setEnabled(False)
            self.voltage_limit_spinbox.setEnabled(False)
            self.current_limit_spinbox.setEnabled(False)
            self.set_voltage_btn.setEnabled(False)
            self.set_vlimit_btn.setEnabled(False)
            self.set_ilimit_btn.setEnabled(False)
            self.enable_hv_btn.setEnabled(False)
            self.disable_hv_btn.setEnabled(False)
            self.timer_spinbox.setEnabled(False)
            self.enable_hv_with_timer_btn.setEnabled(False)
            self.stop_timer_btn.setEnabled(False)

        self.updateConnectionIndicator()

    def updatePicoammeterStatus(self, connected, info):
        """Update picoammeter connection status"""
        if connected:
            self.pa_status.setText(f"Connected")
            self.pa_status.setProperty("connectionStatus", "connected")
            self.pa_status.style().unpolish(self.pa_status)
            self.pa_status.style().polish(self.pa_status)
            self.pa_connect_btn.setEnabled(False)
            self.pa_disconnect_btn.setEnabled(True)

            # Enable controls
            self.current_range_combo.setEnabled(True)
            self.integration_combo.setEnabled(True)
            self.zero_check_btn.setEnabled(True)
            self.auto_zero_check.setEnabled(True)
        else:
            self.pa_status.setText("Not Connected")
            self.pa_status.setProperty("connectionStatus", "disconnected")
            self.pa_status.style().unpolish(self.pa_status)
            self.pa_status.style().polish(self.pa_status)
            self.pa_connect_btn.setEnabled(True)
            self.pa_disconnect_btn.setEnabled(False)

            # Disable controls
            self.current_range_combo.setEnabled(False)
            self.integration_combo.setEnabled(False)
            self.zero_check_btn.setEnabled(False)
            self.auto_zero_check.setEnabled(False)

        self.updateConnectionIndicator()

    def updateConnectionIndicator(self):
        """Update overall connection status indicator"""
        ps_connected = "Connected" in self.ps_status.text()
        pa_connected = "Connected" in self.pa_status.text()

        if ps_connected and pa_connected:
            self.connection_indicator.setText("All Connected")
            self.connection_indicator.setProperty("connectionStatus", "connected")
        elif ps_connected or pa_connected:
            self.connection_indicator.setText("Partial")
            self.connection_indicator.setProperty("connectionStatus", "partial")
        else:
            self.connection_indicator.setText("Disconnected")
            self.connection_indicator.setProperty("connectionStatus", "disconnected")

        # Update the style
        self.connection_indicator.style().unpolish(self.connection_indicator)
        self.connection_indicator.style().polish(self.connection_indicator)

    def updateVoltageReading(self, voltage):
        """Update voltage reading display"""
        self.voltage_reading.setText(f"{int(voltage)} V")

    def updateCurrentReading(self, current):
        """Update current reading display"""
        # Format current with appropriate units
        if abs(current) >= 1e-3:
            self.current_reading.setText(f"{current*1000:.3f} mA")
        elif abs(current) >= 1e-6:
            self.current_reading.setText(f"{current*1e6:.3f} µA")
        elif abs(current) >= 1e-9:
            self.current_reading.setText(f"{current*1e9:.3f} nA")
        elif abs(current) >= 1e-12:
            self.current_reading.setText(f"{current*1e12:.3f} pA")
        else:
            self.current_reading.setText(f"{current:.3e} A")

    def updateTimerStatus(self, remaining_seconds):
        """Update timer status display"""
        if remaining_seconds > 0:
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60
            self.timer_status.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
            self.timer_status.setProperty("timerStatus", "active")
        else:
            self.timer_status.setText("Inactive")
            self.timer_status.setProperty("timerStatus", "inactive")

        # Update the style
        self.timer_status.style().unpolish(self.timer_status)
        self.timer_status.style().polish(self.timer_status)

    def onTimerExpired(self):
        """Handle timer expiration"""
        self.log_message.emit("HV timer expired - output automatically disabled")

        # Update UI to reflect that HV is now disabled
        self.output_status.setText("DISABLED")
        self.output_status.setProperty("outputStatus", "disabled")
        self.output_status.style().unpolish(self.output_status)
        self.output_status.style().polish(self.output_status)

        # Update button states
        self.enable_hv_btn.setEnabled(True)
        self.enable_hv_with_timer_btn.setEnabled(True)
        self.disable_hv_btn.setEnabled(False)
        self.stop_timer_btn.setEnabled(False)

        # Update timer status
        self.timer_status.setText("Expired")
        self.timer_status.setProperty("timerStatus", "expired")
        self.timer_status.style().unpolish(self.timer_status)
        self.timer_status.style().polish(self.timer_status)