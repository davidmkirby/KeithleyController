# settings_tab.py - Application settings and configuration
"""
Settings tab for configuring GPIB addresses, file export options,
and other application preferences
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QPushButton, QSpinBox,
                            QComboBox, QCheckBox, QLineEdit, QFileDialog,
                            QTextEdit, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SettingsTab(QWidget):
    """Settings and configuration tab"""

    # Signals
    log_message = pyqtSignal(str)

    def __init__(self, instrument_controller):
        super().__init__()
        self.instrument_controller = instrument_controller

        # Default settings
        self.ps_address = 14  # Default for 2290-5
        self.pa_address = 22  # Default for 6485
        self.export_directory = ""

        self.setupUI()

    def setupUI(self):
        """Setup the settings tab user interface"""
        layout = QVBoxLayout(self)

        # Create sub-tabs for different setting categories
        self.settings_tabs = QTabWidget()

        # Connection settings tab
        self.connection_tab = QWidget()
        self.setupConnectionTab()
        self.settings_tabs.addTab(self.connection_tab, "Connection")

        # Data settings tab
        self.data_tab = QWidget()
        self.setupDataTab()
        self.settings_tabs.addTab(self.data_tab, "Data Export")

        # Display settings tab
        self.display_tab = QWidget()
        self.setupDisplayTab()
        self.settings_tabs.addTab(self.display_tab, "Display")

        # Safety settings tab
        self.safety_tab = QWidget()
        self.setupSafetyTab()
        self.settings_tabs.addTab(self.safety_tab, "Safety")

        layout.addWidget(self.settings_tabs)

        # Apply button
        apply_layout = QHBoxLayout()
        apply_layout.addStretch()

        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.clicked.connect(self.applySettings)
        self.apply_btn.setMinimumHeight(40)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_layout.addWidget(self.apply_btn)

        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.resetToDefaults)
        self.reset_btn.setMinimumHeight(40)
        apply_layout.addWidget(self.reset_btn)

        layout.addLayout(apply_layout)

    def setupConnectionTab(self):
        """Setup the connection settings tab"""
        layout = QVBoxLayout(self.connection_tab)

        # GPIB Settings Group
        gpib_group = QGroupBox("GPIB Communication Settings")
        gpib_layout = QGridLayout()

        # Power Supply GPIB Address
        gpib_layout.addWidget(QLabel("Power Supply (2290-5) GPIB Address:"), 0, 0)
        self.ps_gpib_spin = QSpinBox()
        self.ps_gpib_spin.setRange(0, 30)
        self.ps_gpib_spin.setValue(self.ps_address)
        self.ps_gpib_spin.setMinimumHeight(35)
        self.ps_gpib_spin.setToolTip("GPIB address for Keithley 2290-5 (typically 14)")
        gpib_layout.addWidget(self.ps_gpib_spin, 0, 1)

        # Test connection button for power supply
        self.test_ps_btn = QPushButton("Test Connection")
        self.test_ps_btn.clicked.connect(self.testPowerSupplyConnection)
        self.test_ps_btn.setMinimumHeight(35)
        gpib_layout.addWidget(self.test_ps_btn, 0, 2)

        # Picoammeter GPIB Address
        gpib_layout.addWidget(QLabel("Picoammeter (6485) GPIB Address:"), 1, 0)
        self.pa_gpib_spin = QSpinBox()
        self.pa_gpib_spin.setRange(0, 30)
        self.pa_gpib_spin.setValue(self.pa_address)
        self.pa_gpib_spin.setMinimumHeight(35)
        self.pa_gpib_spin.setToolTip("GPIB address for Keithley 6485 (typically 22)")
        gpib_layout.addWidget(self.pa_gpib_spin, 1, 1)

        # Test connection button for picoammeter
        self.test_pa_btn = QPushButton("Test Connection")
        self.test_pa_btn.clicked.connect(self.testPicoammeterConnection)
        self.test_pa_btn.setMinimumHeight(35)
        gpib_layout.addWidget(self.test_pa_btn, 1, 2)

        # GPIB Timeout
        gpib_layout.addWidget(QLabel("GPIB Timeout (ms):"), 2, 0)
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1000, 30000)
        self.timeout_spin.setValue(5000)
        self.timeout_spin.setSingleStep(1000)
        self.timeout_spin.setMinimumHeight(35)
        self.timeout_spin.setToolTip("Timeout for GPIB communications")
        gpib_layout.addWidget(self.timeout_spin, 2, 1)

        gpib_group.setLayout(gpib_layout)
        layout.addWidget(gpib_group)

        # Auto-connection settings
        auto_group = QGroupBox("Auto-Connection Settings")
        auto_layout = QVBoxLayout()

        self.auto_connect_check = QCheckBox("Automatically connect to instruments on startup")
        self.auto_connect_check.setChecked(False)
        auto_layout.addWidget(self.auto_connect_check)

        self.auto_scan_check = QCheckBox("Scan for instruments if connection fails")
        self.auto_scan_check.setChecked(True)
        auto_layout.addWidget(self.auto_scan_check)

        auto_group.setLayout(auto_layout)
        layout.addWidget(auto_group)

        layout.addStretch()

    def setupDataTab(self):
        """Setup the data export settings tab"""
        layout = QVBoxLayout(self.data_tab)

        # Export Settings Group
        export_group = QGroupBox("Data Export Settings")
        export_layout = QGridLayout()

        # Export directory
        export_layout.addWidget(QLabel("Default Export Directory:"), 0, 0)
        self.export_dir_edit = QLineEdit()
        self.export_dir_edit.setPlaceholderText("Select directory...")
        self.export_dir_edit.setMinimumHeight(35)
        export_layout.addWidget(self.export_dir_edit, 0, 1)

        self.browse_dir_btn = QPushButton("Browse")
        self.browse_dir_btn.clicked.connect(self.browseExportDirectory)
        self.browse_dir_btn.setMinimumHeight(35)
        export_layout.addWidget(self.browse_dir_btn, 0, 2)

        # CSV format settings
        export_layout.addWidget(QLabel("CSV Delimiter:"), 1, 0)
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems(["Comma (,)", "Semicolon (;)", "Tab"])
        self.delimiter_combo.setMinimumHeight(35)
        export_layout.addWidget(self.delimiter_combo, 1, 1)

        # Number format
        export_layout.addWidget(QLabel("Number Format:"), 2, 0)
        self.number_format_combo = QComboBox()
        self.number_format_combo.addItems(["Scientific", "Fixed Point", "Engineering"])
        self.number_format_combo.setMinimumHeight(35)
        export_layout.addWidget(self.number_format_combo, 2, 1)

        # Auto-export options
        self.auto_export_check = QCheckBox("Auto-export data after each recording session")
        export_layout.addWidget(self.auto_export_check, 3, 0, 1, 3)

        self.timestamp_check = QCheckBox("Include timestamp in filename")
        self.timestamp_check.setChecked(True)
        export_layout.addWidget(self.timestamp_check, 4, 0, 1, 3)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Data Buffer Settings
        buffer_group = QGroupBox("Data Buffer Settings")
        buffer_layout = QGridLayout()

        buffer_layout.addWidget(QLabel("Maximum Data Points:"), 0, 0)
        self.max_points_spin = QSpinBox()
        self.max_points_spin.setRange(1000, 100000)
        self.max_points_spin.setValue(10000)
        self.max_points_spin.setSingleStep(1000)
        self.max_points_spin.setMinimumHeight(35)
        self.max_points_spin.setToolTip("Maximum number of data points to keep in memory")
        buffer_layout.addWidget(self.max_points_spin, 0, 1)

        self.auto_clear_check = QCheckBox("Auto-clear old data when buffer is full")

        buffer_group.setLayout(buffer_layout)
        layout.addWidget(buffer_group)

        layout.addStretch()

    def setupDisplayTab(self):
        """Setup the display settings tab"""
        layout = QVBoxLayout(self.display_tab)

        # Plot Settings Group
        plot_group = QGroupBox("Plot Display Settings")
        plot_layout = QGridLayout()

        # Auto-scale options
        plot_layout.addWidget(QLabel("Y-Axis Auto-scale:"), 0, 0)
        self.autoscale_combo = QComboBox()
        self.autoscale_combo.addItems(["Always", "On New Data", "Manual"])
        self.autoscale_combo.setCurrentIndex(1)
        self.autoscale_combo.setMinimumHeight(35)
        plot_layout.addWidget(self.autoscale_combo, 0, 1)

        # Grid options
        self.show_grid_check = QCheckBox("Show grid lines")
        self.show_grid_check.setChecked(True)
        plot_layout.addWidget(self.show_grid_check, 1, 0, 1, 2)

        self.show_crosshair_check = QCheckBox("Show crosshair cursor")
        self.show_crosshair_check.setChecked(True)
        plot_layout.addWidget(self.show_crosshair_check, 2, 0, 1, 2)

        # Plot colors
        plot_layout.addWidget(QLabel("Current Plot Color:"), 3, 0)
        self.current_color_combo = QComboBox()
        self.current_color_combo.addItems(["Blue", "Red", "Green", "Black", "Purple"])
        self.current_color_combo.setMinimumHeight(35)
        plot_layout.addWidget(self.current_color_combo, 3, 1)

        plot_group.setLayout(plot_layout)
        layout.addWidget(plot_group)

        # Units Display Group
        units_group = QGroupBox("Units Display Settings")
        units_layout = QGridLayout()

        # Current units preference
        units_layout.addWidget(QLabel("Preferred Current Units:"), 0, 0)
        self.current_units_combo = QComboBox()
        self.current_units_combo.addItems(["Auto", "A", "mA", "µA", "nA", "pA"])
        self.current_units_combo.setMinimumHeight(35)
        units_layout.addWidget(self.current_units_combo, 0, 1)

        # Voltage units
        units_layout.addWidget(QLabel("Voltage Units:"), 1, 0)
        self.voltage_units_combo = QComboBox()
        self.voltage_units_combo.addItems(["V", "kV"])
        self.voltage_units_combo.setMinimumHeight(35)
        units_layout.addWidget(self.voltage_units_combo, 1, 1)

        # Decimal places
        units_layout.addWidget(QLabel("Decimal Places:"), 2, 0)
        self.decimal_spin = QSpinBox()
        self.decimal_spin.setRange(1, 6)
        self.decimal_spin.setValue(3)
        self.decimal_spin.setMinimumHeight(35)
        units_layout.addWidget(self.decimal_spin, 2, 1)

        units_group.setLayout(units_layout)
        layout.addWidget(units_group)

        layout.addStretch()

    def setupSafetyTab(self):
        """Setup the safety settings tab"""
        layout = QVBoxLayout(self.safety_tab)

        # Safety Limits Group
        safety_group = QGroupBox("Safety Settings")
        safety_layout = QGridLayout()

        # Maximum voltage limit
        safety_layout.addWidget(QLabel("Maximum Voltage Limit (V):"), 0, 0)
        self.max_voltage_spin = QSpinBox()
        self.max_voltage_spin.setRange(100, 5000)
        self.max_voltage_spin.setValue(5000)
        self.max_voltage_spin.setSingleStep(100)
        self.max_voltage_spin.setMinimumHeight(35)
        self.max_voltage_spin.setToolTip("Software limit for maximum voltage setting")
        safety_layout.addWidget(self.max_voltage_spin, 0, 1)

        # Maximum current limit
        safety_layout.addWidget(QLabel("Maximum Current Limit (mA):"), 1, 0)
        self.max_current_spin = QSpinBox()
        self.max_current_spin.setRange(1, 5250)
        self.max_current_spin.setValue(5250)
        self.max_current_spin.setSingleStep(100)
        self.max_current_spin.setMinimumHeight(35)
        self.max_current_spin.setToolTip("Software limit for maximum current setting (mA)")
        safety_layout.addWidget(self.max_current_spin, 1, 1)

        # Safety confirmations
        self.confirm_hv_enable_check = QCheckBox("Confirm before enabling high voltage")
        self.confirm_hv_enable_check.setChecked(True)
        safety_layout.addWidget(self.confirm_hv_enable_check, 2, 0, 1, 2)

        self.confirm_exit_check = QCheckBox("Confirm before exiting application")
        self.confirm_exit_check.setChecked(True)
        safety_layout.addWidget(self.confirm_exit_check, 3, 0, 1, 2)

        self.auto_disable_hv_check = QCheckBox("Auto-disable HV on disconnect")
        self.auto_disable_hv_check.setChecked(True)
        safety_layout.addWidget(self.auto_disable_hv_check, 4, 0, 1, 2)

        safety_group.setLayout(safety_layout)
        layout.addWidget(safety_group)

        # Emergency Settings Group
        emergency_group = QGroupBox("Emergency Settings")
        emergency_layout = QVBoxLayout()

        emergency_info = QLabel("""
        Emergency Stop (F1): Immediately disables all outputs and stops data acquisition.

        Safety Procedures:
        • Always ensure proper grounding before enabling high voltage
        • Never touch exposed connections when HV is enabled
        • Use appropriate safety enclosures with interlocks
        • Keep emergency stop button easily accessible
        """)
        emergency_info.setWordWrap(True)
        emergency_info.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        emergency_layout.addWidget(emergency_info)

        # Emergency stop test button
        self.test_emergency_btn = QPushButton("Test Emergency Stop")
        self.test_emergency_btn.clicked.connect(self.testEmergencyStop)
        self.test_emergency_btn.setMinimumHeight(40)
        self.test_emergency_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #cc3333;
            }
        """)
        emergency_layout.addWidget(self.test_emergency_btn)

        emergency_group.setLayout(emergency_layout)
        layout.addWidget(emergency_group)

        layout.addStretch()

    def testPowerSupplyConnection(self):
        """Test connection to power supply"""
        address = self.ps_gpib_spin.value()
        self.log_message.emit(f"Testing power supply connection at GPIB address {address}...")

        success = self.instrument_controller.connectPowerSupply(address)
        if success:
            self.log_message.emit("Power supply connection test successful")
        else:
            self.log_message.emit("Power supply connection test failed")

    def testPicoammeterConnection(self):
        """Test connection to picoammeter"""
        address = self.pa_gpib_spin.value()
        self.log_message.emit(f"Testing picoammeter connection at GPIB address {address}...")

        success = self.instrument_controller.connectPicoammeter(address)
        if success:
            self.log_message.emit("Picoammeter connection test successful")
        else:
            self.log_message.emit("Picoammeter connection test failed")

    def browseExportDirectory(self):
        """Browse for export directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory",
            self.export_dir_edit.text() or ""
        )

        if directory:
            self.export_dir_edit.setText(directory)
            self.export_directory = directory
            self.log_message.emit(f"Export directory set to: {directory}")

    def testEmergencyStop(self):
        """Test emergency stop functionality"""
        self.log_message.emit("Testing emergency stop...")

        # Simulate emergency stop
        if self.instrument_controller.power_supply:
            self.instrument_controller.disableOutput()

        if self.instrument_controller.is_acquiring:
            self.instrument_controller.stopDataAcquisition()

        self.log_message.emit("Emergency stop test completed")

    def applySettings(self):
        """Apply all settings"""
        # Update addresses
        self.ps_address = self.ps_gpib_spin.value()
        self.pa_address = self.pa_gpib_spin.value()

        # Update export directory
        self.export_directory = self.export_dir_edit.text()

        self.log_message.emit("Settings applied successfully")

    def resetToDefaults(self):
        """Reset all settings to defaults"""
        # Reset GPIB addresses
        self.ps_gpib_spin.setValue(14)
        self.pa_gpib_spin.setValue(22)

        # Reset timeout
        self.timeout_spin.setValue(5000)

        # Reset checkboxes
        self.auto_connect_check.setChecked(False)
        self.auto_scan_check.setChecked(True)
        self.auto_export_check.setChecked(False)
        self.timestamp_check.setChecked(True)
        self.auto_clear_check.setChecked(True)
        self.show_grid_check.setChecked(True)
        self.show_crosshair_check.setChecked(True)
        self.confirm_hv_enable_check.setChecked(True)
        self.confirm_exit_check.setChecked(True)
        self.auto_disable_hv_check.setChecked(True)

        # Reset combo boxes
        self.delimiter_combo.setCurrentIndex(0)
        self.number_format_combo.setCurrentIndex(0)
        self.autoscale_combo.setCurrentIndex(1)
        self.current_color_combo.setCurrentIndex(0)
        self.current_units_combo.setCurrentIndex(0)
        self.voltage_units_combo.setCurrentIndex(0)

        # Reset spin boxes
        self.max_points_spin.setValue(10000)
        self.decimal_spin.setValue(3)
        self.max_voltage_spin.setValue(5000)
        self.max_current_spin.setValue(5250)

        # Clear export directory
        self.export_dir_edit.clear()
        self.export_directory = ""

        self.log_message.emit("Settings reset to defaults")

    # Getter methods for other components to access settings
    def getPowerSupplyAddress(self):
        """Get power supply GPIB address"""
        return self.ps_gpib_spin.value()

    def getPicoammeterAddress(self):
        """Get picoammeter GPIB address"""
        return self.pa_gpib_spin.value()

    def getExportDirectory(self):
        """Get export directory"""
        return self.export_dir_edit.text()

    def getMaxDataPoints(self):
        """Get maximum data points setting"""
        return self.max_points_spin.value()

    def getCSVDelimiter(self):
        """Get CSV delimiter"""
        delim_map = {
            "Comma (,)": ",",
            "Semicolon (;)": ";",
            "Tab": "\t"
        }
        return delim_map.get(self.delimiter_combo.currentText(), ",")

    def shouldConfirmHVEnable(self):
        """Check if HV enable confirmation is required"""
        return self.confirm_hv_enable_check.isChecked()

    def shouldAutoDisableHV(self):
        """Check if auto-disable HV is enabled"""
        return self.auto_disable_hv_check.isChecked()