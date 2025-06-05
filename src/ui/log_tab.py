# log_tab.py - Activity logging and system messages
"""
Log tab for displaying system messages, errors, and activity history

Provides comprehensive logging for troubleshooting and record keeping
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                            QPushButton, QGroupBox, QLabel, QCheckBox,
                            QSpinBox, QFileDialog, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QTextCursor

# Import the new logger system
from src.core.logger import get_logger


class LogTab(QWidget):
    """Activity log and system messages tab"""

    def __init__(self, testing_mode=False):
        super().__init__()

        # Log settings
        self.max_log_entries = 1000
        self.log_file_path = ""
        self.auto_save_enabled = False
        self.current_filter = "ALL"
        self.testing_mode = testing_mode

        # Store log entries separately for efficient filtering
        self.log_entries = []  # List of (timestamp, level, message) tuples

        # Get the system logger
        self.logger = get_logger()

        # Set up the UI first to ensure all widgets are created
        self.setupUI()
        self.setupAutoSave()

        # Only set UI callback if not in testing mode to avoid circular references
        if not testing_mode:
            self.logger.set_ui_callback(self.addLogMessage)

        # Add initial welcome message
        if not testing_mode:
            self.logger.system("Keithley Dual Controller started")
            self.logger.info("Activity logging initialized")

    def setupUI(self):
        """Setup the log tab user interface"""
        layout = QVBoxLayout(self)

        # Log controls
        layout.addWidget(self.createControlGroup())

        # Main log display
        layout.addWidget(self.createLogGroup())

        # Log statistics
        layout.addWidget(self.createStatsGroup())

    def createControlGroup(self):
        """Create log control group"""
        group = QGroupBox("Log Controls")
        layout = QHBoxLayout()

        # Log level filter
        layout.addWidget(QLabel("Filter Level:"))
        self.level_filter_combo = QComboBox()
        self.level_filter_combo.addItems(["ALL", "ERROR", "WARNING", "INFO", "SYSTEM"])
        self.level_filter_combo.setMinimumHeight(30)
        self.level_filter_combo.currentTextChanged.connect(self.filterLogMessages)
        layout.addWidget(self.level_filter_combo)

        layout.addStretch()

        # Clear log button
        self.clear_log_btn = QPushButton("Clear Log")
        self.clear_log_btn.clicked.connect(self.clearLog)
        self.clear_log_btn.setMinimumHeight(35)
        layout.addWidget(self.clear_log_btn)

        # Save log button
        self.save_log_btn = QPushButton("Save Log")
        self.save_log_btn.clicked.connect(self.saveLogToFile)
        self.save_log_btn.setMinimumHeight(35)
        layout.addWidget(self.save_log_btn)

        # Auto-scroll toggle
        self.auto_scroll_check = QCheckBox("Auto-scroll")
        self.auto_scroll_check.setChecked(True)
        layout.addWidget(self.auto_scroll_check)

        # Timestamp toggle
        self.timestamp_check = QCheckBox("Show timestamps")
        self.timestamp_check.setChecked(True)
        self.timestamp_check.stateChanged.connect(self.toggleTimestamps)
        layout.addWidget(self.timestamp_check)

        group.setLayout(layout)
        return group

    def createLogGroup(self):
        """Create the main log display group"""
        group = QGroupBox("Activity Log")
        layout = QVBoxLayout()

        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(400)

        # Set monospace font for better alignment
        # Try macOS/Unix fonts first, then Windows fonts, then generic monospace
        for font_name in ["Menlo", "Monaco", "Courier New", "Consolas", "monospace"]:
            font = QFont(font_name, 9)
            if font.exactMatch() or font_name == "monospace":
                self.log_text.setFont(font)
                break

        # Set dark theme for log
        self.log_text.setProperty("logDisplay", "true")

        layout.addWidget(self.log_text)
        group.setLayout(layout)
        return group

    def createStatsGroup(self):
        """Create log statistics group"""
        group = QGroupBox("Log Statistics")
        layout = QHBoxLayout()

        # Total messages
        layout.addWidget(QLabel("Total Messages:"))
        self.total_messages_label = QLabel("0")
        self.total_messages_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.total_messages_label)

        layout.addStretch()

        # Error count
        layout.addWidget(QLabel("Errors:"))
        self.error_count_label = QLabel("0")
        self.error_count_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.error_count_label.setProperty("logLevel", "error")
        layout.addWidget(self.error_count_label)

        layout.addStretch()

        # Warning count
        layout.addWidget(QLabel("Warnings:"))
        self.warning_count_label = QLabel("0")
        self.warning_count_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.warning_count_label.setProperty("logLevel", "warning")
        layout.addWidget(self.warning_count_label)

        layout.addStretch()

        # Session start time
        layout.addWidget(QLabel("Session Started:"))
        self.session_time_label = QLabel(datetime.now().strftime("%H:%M:%S"))
        self.session_time_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(self.session_time_label)

        layout.addStretch()

        # Auto-save settings
        self.auto_save_check = QCheckBox("Auto-save log")
        self.auto_save_check.stateChanged.connect(self.toggleAutoSave)
        layout.addWidget(self.auto_save_check)

        group.setLayout(layout)
        return group

    def setupAutoSave(self):
        """Setup auto-save timer"""
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.autoSaveLog)
        # Auto-save every 5 minutes if enabled
        self.auto_save_timer.setInterval(300000)  # 5 minutes in milliseconds

        # Keep track of auto-save files for cleanup
        self.max_autosave_files = 10
        self.autosave_files = []

    def cleanup(self):
        """Clean up resources and remove UI callback from logger"""
        if hasattr(self, 'auto_save_timer'):
            self.auto_save_timer.stop()

        # Remove UI callback from logger to prevent accessing destroyed UI elements
        if hasattr(self, 'logger') and not self.testing_mode:
            self.logger.remove_ui_callback()

    def addLogMessage(self, message, level="INFO"):
        """Add a message to the log with timestamp and formatting"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # Store entry in our data structure
        self.log_entries.append((timestamp, level, message))

        # Limit entries to prevent memory issues
        if len(self.log_entries) > self.max_log_entries:
            self.log_entries = self.log_entries[-self.max_log_entries:]

        # Add to display if it passes the current filter and we're not in testing mode
        if not self.testing_mode and self.shouldShowMessage(level):
            self.addMessageToDisplay(timestamp, level, message)

        # Update statistics
        self.updateLogStats()

    def shouldShowMessage(self, level):
        """Check if message should be shown based on current filter"""
        if self.current_filter == "ALL":
            return True
        return level == self.current_filter

    def addMessageToDisplay(self, timestamp, level, message):
        """Add a formatted message to the display"""
        # Skip UI updates in testing mode
        if self.testing_mode:
            return

        # Color mapping for different log levels
        color_map = {
            "ERROR": "#ff6b6b",    # Light red
            "WARNING": "#ffd93d",  # Yellow
            "INFO": "#74c0fc",     # Light blue
            "SYSTEM": "#51cf66",   # Light green
            "DEBUG": "#868e96"     # Gray
        }

        # Icon mapping for different log levels
        icon_map = {
            "ERROR": "[ERROR]",
            "WARNING": "[WARNING]",
            "INFO": "[INFO]",
            "SYSTEM": "[SYSTEM]",
            "DEBUG": "[DEBUG]"
        }

        color = color_map.get(level, "#ffffff")
        icon = icon_map.get(level, "[LOG]")

        # Format the log entry
        if hasattr(self, 'timestamp_check') and self.timestamp_check.isChecked():
            formatted_message = f'<span style="color: #888888;">[{timestamp}]</span> <span style="color: {color};">{icon}:</span> {message}'
        else:
            formatted_message = f'<span style="color: {color};">{icon}:</span> {message}'

        # Add to log display
        self.log_text.append(formatted_message)

        # Auto-scroll if enabled
        if hasattr(self, 'auto_scroll_check') and self.auto_scroll_check.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)

    def rebuildLogDisplay(self):
        """Rebuild the log display based on current filter"""
        self.log_text.clear()

        for timestamp, level, message in self.log_entries:
            if self.shouldShowMessage(level):
                self.addMessageToDisplay(timestamp, level, message)

    def updateLogStats(self):
        """Update log statistics"""
        # Count messages by level from stored entries
        total_count = len(self.log_entries)
        error_count = len([entry for entry in self.log_entries if entry[1] == 'ERROR'])
        warning_count = len([entry for entry in self.log_entries if entry[1] == 'WARNING'])

        self.total_messages_label.setText(str(total_count))
        self.error_count_label.setText(str(error_count))
        self.warning_count_label.setText(str(warning_count))

    def limitLogEntries(self):
        """Limit the number of log entries to prevent memory issues"""
        lines = self.log_text.toPlainText().split('\n')
        if len(lines) > self.max_log_entries:
            # Keep only the last max_log_entries lines
            trimmed_lines = lines[-self.max_log_entries:]
            self.log_text.clear()
            for line in trimmed_lines:
                if line.strip():  # Only add non-empty lines
                    # Re-add with formatting (simplified)
                    if 'ERROR:' in line:
                        level = 'ERROR'
                    elif 'WARNING:' in line:
                        level = 'WARNING'
                    elif 'SYSTEM:' in line:
                        level = 'SYSTEM'
                    else:
                        level = 'INFO'

                    # Extract message part (simplified)
                    if ':' in line:
                        parts = line.split(':', 2)
                        if len(parts) >= 3:
                            message = parts[2].strip()
                            self.addLogMessage(message, level)

    def filterLogMessages(self, filter_level):
        """Filter log messages by level"""
        self.current_filter = filter_level

        if filter_level == "ALL":
            # Show all stored messages
            self.rebuildLogDisplay()
        else:
            # Filter and show only messages of selected level
            self.rebuildLogDisplay()

        self.addLogMessage(f"Log filter set to: {filter_level}", "SYSTEM")

    def toggleTimestamps(self, state):
        """Toggle timestamp display"""
        if state == Qt.CheckState.Checked.value:
            self.addLogMessage("Timestamps enabled", "SYSTEM")
        else:
            self.addLogMessage("Timestamps disabled", "SYSTEM")

    def toggleAutoSave(self, state):
        """Toggle auto-save functionality"""
        if state == Qt.CheckState.Checked.value:
            self.auto_save_enabled = True
            self.auto_save_timer.start()
            self.addLogMessage("Auto-save enabled (every 5 minutes)", "SYSTEM")
        else:
            self.auto_save_enabled = False
            self.auto_save_timer.stop()
            self.addLogMessage("Auto-save disabled", "SYSTEM")

    def clearLog(self):
        """Clear the log display"""
        reply = QMessageBox.question(
            self,
            'Clear Log',
            'Are you sure you want to clear the activity log?\n\n'
            'This action cannot be undone.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.log_text.clear()
            self.log_entries.clear()  # Clear stored entries too
            self.total_messages_label.setText("0")
            self.error_count_label.setText("0")
            self.warning_count_label.setText("0")
            self.addLogMessage("Log cleared by user", "SYSTEM")

    def saveLogToFile(self):
        """Save log to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"keithley_log_{timestamp}.txt"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Activity Log",
            default_filename,
            "Text Files (*.txt);;Log Files (*.log);;All Files (*)"
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    # Write header
                    f.write(f"Keithley Dual Controller Activity Log\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Session started: {self.session_time_label.text()}\n")
                    f.write("=" * 80 + "\n\n")

                    # Write log content from stored entries
                    for timestamp_entry, level, message in self.log_entries:
                        f.write(f"[{timestamp_entry}] {level}: {message}\n")

                    f.write("\n\n" + "=" * 80)
                    f.write(f"\nEnd of log - Total entries: {len(self.log_entries)}")

                self.addLogMessage(f"Log saved to: {filename}", "SYSTEM")

                QMessageBox.information(
                    self,
                    "Log Saved",
                    f"Activity log saved successfully!\n\nFile: {filename}"
                )

            except Exception as e:
                error_msg = f"Failed to save log: {str(e)}"
                self.addLogMessage(error_msg, "ERROR")
                QMessageBox.critical(self, "Save Error", error_msg)

    def autoSaveLog(self):
        """Auto-save the log to a predefined location"""
        if not self.auto_save_enabled:
            return

        try:
            # Create logs directory if it doesn't exist
            logs_dir = "logs"
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(logs_dir, f"keithley_autosave_{timestamp}.log")

            # Write log content from stored entries
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Keithley Dual Controller Auto-saved Log\n")
                f.write(f"Auto-saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 80 + "\n\n")

                # Write entries from our data structure
                for timestamp_entry, level, message in self.log_entries:
                    f.write(f"[{timestamp_entry}] {level}: {message}\n")

            # Track auto-save files for cleanup
            self.autosave_files.append(filename)

            # Clean up old auto-save files
            if len(self.autosave_files) > self.max_autosave_files:
                old_file = self.autosave_files.pop(0)
                try:
                    if os.path.exists(old_file):
                        os.remove(old_file)
                except OSError:
                    pass  # Ignore errors when cleaning up old files

            self.addLogMessage(f"Log auto-saved to: {filename}", "SYSTEM")

        except Exception as e:
            self.addLogMessage(f"Auto-save failed: {str(e)}", "ERROR")

    def logInstrumentEvent(self, instrument, event, details=""):
        """Log instrument-specific events"""
        message = f"{instrument}: {event}"
        if details:
            message += f" - {details}"

        # Determine log level based on event type
        if "error" in event.lower() or "fail" in event.lower():
            level = "ERROR"
        elif "warning" in event.lower() or "disconnect" in event.lower():
            level = "WARNING"
        else:
            level = "INFO"

        self.addLogMessage(message, level)

    def logSafetyEvent(self, event, details=""):
        """Log safety-related events"""
        message = f"SAFETY: {event}"
        if details:
            message += f" - {details}"

        # Safety events are always high priority
        if "emergency" in event.lower() or "stop" in event.lower():
            level = "ERROR"
        else:
            level = "WARNING"

        self.addLogMessage(message, level)

    def getLogSummary(self):
        """Get a summary of log statistics"""
        return {
            "total_messages": int(self.total_messages_label.text()),
            "errors": int(self.error_count_label.text()),
            "warnings": int(self.warning_count_label.text()),
            "session_start": self.session_time_label.text()
        }