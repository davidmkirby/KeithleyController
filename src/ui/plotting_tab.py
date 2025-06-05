# plotting_tab.py - Data acquisition and plotting interface
"""
Plotting tab for real-time data visualization and CSV export
Handles continuous data acquisition from instruments
"""

import csv
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                            QGroupBox, QLabel, QPushButton, QDoubleSpinBox,
                            QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
import pyqtgraph as pg


class PlottingTab(QWidget):
    """Data acquisition and plotting tab"""

    # Signals
    log_message = pyqtSignal(str)

    def __init__(self, instrument_controller):
        super().__init__()
        self.instrument_controller = instrument_controller

        # Data storage
        self.time_data = []
        self.current_data = []
        self.voltage_data = []
        self.is_recording = False
        self.max_points = 10000
        self.start_time = None

        self.setupUI()
        self.connectSignals()

    def setupUI(self):
        """Setup the plotting tab user interface"""
        layout = QVBoxLayout(self)

        # Set proper spacing and margins for the main layout
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        # Data acquisition controls
        layout.addWidget(self.createControlGroup())

        # Plot widget
        layout.addWidget(self.createPlotGroup())

        # Statistics group
        layout.addWidget(self.createStatsGroup())

    def createControlGroup(self):
        """Create data acquisition control group"""
        group = QGroupBox("Data Acquisition Control")
        layout = QHBoxLayout()

        # Recording controls
        self.start_recording_btn = QPushButton("Start Recording")
        self.start_recording_btn.clicked.connect(self.startRecording)
        self.start_recording_btn.setEnabled(False)
        self.start_recording_btn.setMinimumHeight(40)
        self.start_recording_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        layout.addWidget(self.start_recording_btn)

        self.stop_recording_btn = QPushButton("Stop Recording")
        self.stop_recording_btn.clicked.connect(self.stopRecording)
        self.stop_recording_btn.setEnabled(False)
        self.stop_recording_btn.setMinimumHeight(40)
        self.stop_recording_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        layout.addWidget(self.stop_recording_btn)

        # Sampling rate control
        layout.addWidget(QLabel("Sampling Rate (Hz):"))
        self.sampling_rate_spin = QDoubleSpinBox()
        self.sampling_rate_spin.setRange(0.1, 10.0)
        self.sampling_rate_spin.setValue(2.0)
        self.sampling_rate_spin.setDecimals(1)
        self.sampling_rate_spin.setMinimumHeight(35)
        self.sampling_rate_spin.valueChanged.connect(self.updateSamplingRate)
        layout.addWidget(self.sampling_rate_spin)

        layout.addStretch()

        # File operations
        self.export_btn = QPushButton("Export Data")
        self.export_btn.clicked.connect(self.exportDataToCSV)
        self.export_btn.setMinimumHeight(40)
        layout.addWidget(self.export_btn)

        self.clear_plot_btn = QPushButton("Clear Plot")
        self.clear_plot_btn.clicked.connect(self.clearData)
        self.clear_plot_btn.setMinimumHeight(40)
        layout.addWidget(self.clear_plot_btn)

        group.setLayout(layout)
        return group

    def createPlotGroup(self):
        """Create the plotting group"""
        group = QGroupBox("Current vs. Time")
        layout = QVBoxLayout()

        # Add proper margins to prevent cutoff - extra top margin for group box title
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(5)

        # Create pyqtgraph plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setLabel('left', 'Current', units='A')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setMinimumHeight(400)

        # Set proper margins around the plot area to prevent cutoff
        # Increase the top margin to prevent legend/title cutoff
        self.plot_widget.getPlotItem().setContentsMargins(10, 20, 10, 10)

        # Add legend with proper positioning to avoid cutoff
        self.plot_widget.addLegend(offset=(10, 10))

        # Create plot data lines
        self.current_line = self.plot_widget.plot(
            pen=pg.mkPen(color='b', width=2),
            name='Current',
            symbol='o',
            symbolSize=3,
            symbolBrush='b'
        )

        # Add crosshair cursor
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
        self.plot_widget.addItem(self.crosshair_v, ignoreBounds=True)
        self.plot_widget.addItem(self.crosshair_h, ignoreBounds=True)

        # Connect mouse movement for crosshair
        self.plot_widget.scene().sigMouseMoved.connect(self.updateCrosshair)

        layout.addWidget(self.plot_widget)
        group.setLayout(layout)
        return group

    def createStatsGroup(self):
        """Create statistics display group"""
        group = QGroupBox("Statistics & Information")
        layout = QGridLayout()

        # Recording info
        layout.addWidget(QLabel("Samples:"), 0, 0)
        self.samples_label = QLabel("0")
        self.samples_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.samples_label, 0, 1)

        layout.addWidget(QLabel("Recording Time:"), 0, 2)
        self.time_label = QLabel("-- s")
        self.time_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.time_label, 0, 3)

        layout.addWidget(QLabel("Sampling Rate:"), 0, 4)
        self.actual_rate_label = QLabel("-- Hz")
        self.actual_rate_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.actual_rate_label, 0, 5)

        # Current statistics
        layout.addWidget(QLabel("Current Min:"), 1, 0)
        self.min_label = QLabel("-- A")
        self.min_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.min_label, 1, 1)

        layout.addWidget(QLabel("Current Max:"), 1, 2)
        self.max_label = QLabel("-- A")
        self.max_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.max_label, 1, 3)

        layout.addWidget(QLabel("Current Mean:"), 1, 4)
        self.mean_label = QLabel("-- A")
        self.mean_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.mean_label, 1, 5)

        # Additional statistics
        layout.addWidget(QLabel("Current Std:"), 2, 0)
        self.std_label = QLabel("-- A")
        self.std_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.std_label, 2, 1)

        layout.addWidget(QLabel("Voltage:"), 2, 2)
        self.voltage_label = QLabel("-- V")
        self.voltage_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.voltage_label, 2, 3)

        layout.addWidget(QLabel("Status:"), 2, 4)
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(self.status_label, 2, 5)

        group.setLayout(layout)
        return group

    def connectSignals(self):
        """Connect signals"""
        # Connect to instrument controller
        self.instrument_controller.data_ready.connect(self.addDataPoint)
        self.instrument_controller.picoammeter_connected.connect(self.updateConnectionStatus)

    def updateConnectionStatus(self, connected, info):
        """Update connection status and enable/disable controls"""
        if connected:
            self.start_recording_btn.setEnabled(True)
            self.status_label.setText("Connected")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.start_recording_btn.setEnabled(False)
            self.stop_recording_btn.setEnabled(False)
            if self.is_recording:
                self.stopRecording()
            self.status_label.setText("Disconnected")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def startRecording(self):
        """Start data recording"""
        if not self.instrument_controller.picoammeter:
            self.log_message.emit("ERROR: Cannot start recording: Picoammeter not connected")
            return

        sampling_rate = self.sampling_rate_spin.value()

        if self.instrument_controller.startDataAcquisition(sampling_rate):
            self.is_recording = True
            self.start_time = datetime.now()

            # Update UI
            self.start_recording_btn.setEnabled(False)
            self.stop_recording_btn.setEnabled(True)
            self.status_label.setText("Recording...")
            self.status_label.setStyleSheet("color: orange; font-weight: bold;")

            # Clear previous data if desired
            if not self.time_data:  # Only clear if no data exists
                self.clearData()

            self.log_message.emit(f"Recording started at {sampling_rate} Hz")
        else:
            self.log_message.emit("ERROR: Failed to start recording")

    def stopRecording(self):
        """Stop data recording"""
        if self.instrument_controller.stopDataAcquisition():
            self.is_recording = False

            # Update UI
            self.start_recording_btn.setEnabled(True)
            self.stop_recording_btn.setEnabled(False)
            self.status_label.setText("Stopped")
            self.status_label.setStyleSheet("color: gray; font-weight: bold;")

            self.log_message.emit("Recording stopped")

    def addDataPoint(self, time_val, current, voltage):
        """Add a new data point to the plot"""
        if not self.is_recording:
            return

        # Add to data arrays
        self.time_data.append(time_val)
        self.current_data.append(current)
        self.voltage_data.append(voltage)

        # Limit data points to prevent memory issues
        if len(self.time_data) > self.max_points:
            self.time_data = self.time_data[-self.max_points:]
            self.current_data = self.current_data[-self.max_points:]
            self.voltage_data = self.voltage_data[-self.max_points:]

        # Update plot
        self.current_line.setData(self.time_data, self.current_data)

        # Update statistics
        self.updateStatistics()

    def updateStatistics(self):
        """Update statistics display"""
        if not self.current_data:
            return

        current_array = np.array(self.current_data)

        # Basic statistics
        self.samples_label.setText(str(len(self.current_data)))

        if self.time_data:
            self.time_label.setText(f"{self.time_data[-1]:.1f} s")

            # Calculate actual sampling rate
            if len(self.time_data) > 1:
                dt = self.time_data[-1] - self.time_data[0]
                actual_rate = (len(self.time_data) - 1) / dt if dt > 0 else 0
                self.actual_rate_label.setText(f"{actual_rate:.2f} Hz")

        # Current statistics with appropriate units
        min_current = np.min(current_array)
        max_current = np.max(current_array)
        mean_current = np.mean(current_array)
        std_current = np.std(current_array)

        self.min_label.setText(self.formatCurrent(min_current))
        self.max_label.setText(self.formatCurrent(max_current))
        self.mean_label.setText(self.formatCurrent(mean_current))
        self.std_label.setText(self.formatCurrent(std_current))

        # Latest voltage
        if self.voltage_data:
            self.voltage_label.setText(f"{self.voltage_data[-1]:.1f} V")

    def formatCurrent(self, current):
        """Format current value with appropriate units"""
        abs_current = abs(current)
        if abs_current >= 1e-3:
            return f"{current*1000:.3f} mA"
        elif abs_current >= 1e-6:
            return f"{current*1e6:.3f} µA"
        elif abs_current >= 1e-9:
            return f"{current*1e9:.3f} nA"
        elif abs_current >= 1e-12:
            return f"{current*1e12:.3f} pA"
        else:
            return f"{current:.3e} A"

    def updateCrosshair(self, pos):
        """Update crosshair position on mouse move"""
        if self.plot_widget.plotItem.vb.mapSceneToView(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            self.crosshair_v.setPos(mouse_point.x())
            self.crosshair_h.setPos(mouse_point.y())

    def updateSamplingRate(self, rate):
        """Update sampling rate during acquisition"""
        if self.is_recording:
            self.instrument_controller.setSamplingRate(rate)
            self.log_message.emit(f"Sampling rate updated to {rate} Hz")

    def clearData(self):
        """Clear all plot data"""
        self.time_data.clear()
        self.current_data.clear()
        self.voltage_data.clear()

        # Clear plot
        self.current_line.setData([], [])

        # Reset statistics
        self.samples_label.setText("0")
        self.time_label.setText("-- s")
        self.actual_rate_label.setText("-- Hz")
        self.min_label.setText("-- A")
        self.max_label.setText("-- A")
        self.mean_label.setText("-- A")
        self.std_label.setText("-- A")
        self.voltage_label.setText("-- V")

        self.log_message.emit("Plot data cleared")

    def exportDataToCSV(self):
        """Export data to CSV file"""
        if not self.time_data:
            QMessageBox.warning(self, "No Data", "No data to export!")
            return

        # Get filename from user
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"keithley_data_{timestamp}.csv"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data to CSV",
            default_name,
            "CSV Files (*.csv);;All Files (*)"
        )

        if not filename:
            return

        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                # Write header
                writer.writerow([
                    "Time (s)",
                    "Current (A)",
                    "Voltage (V)",
                    "Timestamp"
                ])

                # Write data
                start_timestamp = self.start_time if self.start_time else datetime.now()
                for i, (t, current, voltage) in enumerate(zip(self.time_data, self.current_data, self.voltage_data)):
                    timestamp = start_timestamp.timestamp() + t
                    writer.writerow([t, current, voltage, timestamp])

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Data exported successfully!\n\n"
                f"File: {filename}\n"
                f"Records: {len(self.time_data)}\n"
                f"Time span: {self.time_data[-1]:.1f} seconds"
            )

            self.log_message.emit(f"Data exported to {filename} ({len(self.time_data)} points)")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Failed to export data:\n{str(e)}"
            )
            self.log_message.emit(f"ERROR: Export failed: {str(e)}")