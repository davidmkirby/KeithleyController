# instrument_control.py - Instrument communication and control
"""
Handles communication with Keithley 2290-5 and 6485 instruments
Based on official Keithley SCPI commands from manuals
"""

import time
import pyvisa
import traceback
from PyQt6.QtCore import QObject, pyqtSignal, QThread

# Import the logger
from src.core.logger import get_logger

class DataAcquisitionThread(QThread):
    """Thread for continuous data acquisition from instruments"""
    data_acquired = pyqtSignal(float, float, float)  # time, current, voltage
    error_occurred = pyqtSignal(str)

    def __init__(self, picoammeter, power_supply=None, sampling_interval=0.5):
        super().__init__()
        self.picoammeter = picoammeter
        self.power_supply = power_supply
        self.sampling_interval = sampling_interval
        self.running = False
        self.start_time = 0
        self.logger = get_logger()

    def run(self):
        """Main data acquisition loop"""
        self.running = True
        self.start_time = time.time()
        self.logger.info(f"Data acquisition thread started with {self.sampling_interval}s interval")

        error_count = 0
        max_consecutive_errors = 5

        while self.running:
            try:
                # Check if instruments are still available
                if not self.picoammeter:
                    error_msg = "Picoammeter disconnected during acquisition"
                    self.error_occurred.emit(error_msg)
                    self.logger.error(error_msg)
                    self.running = False
                    break

                # Read current from picoammeter
                current_str = self.picoammeter.query("READ?").strip()
                current = float(current_str)

                # Read voltage from power supply if available
                voltage = 0.0
                if self.power_supply:
                    try:
                        voltage_str = self.power_supply.query("VOUT?").strip()
                        voltage = float(voltage_str)
                    except Exception as e:
                        error_msg = f"Power supply reading error: {str(e)}"
                        self.error_occurred.emit(error_msg)
                        self.logger.warning(error_msg)
                        voltage = 0.0

                elapsed_time = time.time() - self.start_time

                # Emit the acquired data
                self.data_acquired.emit(elapsed_time, current, voltage)

                # Reset error counter on successful reading
                error_count = 0

                # Wait for next sample
                time.sleep(self.sampling_interval)

            except Exception as e:
                error_msg = f"Data acquisition error: {str(e)}"
                self.error_occurred.emit(error_msg)
                self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

                # Count consecutive errors
                error_count += 1

                # Stop after too many consecutive errors
                if error_count >= max_consecutive_errors:
                    self.error_occurred.emit(f"Stopping acquisition after {error_count} consecutive errors")
                    self.logger.error(f"Stopping acquisition after {error_count} consecutive errors")
                    self.running = False
                    break

                # Don't immediately retry on serious errors to avoid error flooding
                time.sleep(1)  # Avoid rapid error messages

                # Check if we should stop
                if not self.running:
                    break

    def stop(self):
        """Stop the data acquisition thread"""
        self.logger.info("Data acquisition thread stopping")
        self.running = False
        if not self.wait(2000):  # Wait up to 2 seconds
            self.logger.warning("Data acquisition thread did not stop gracefully, terminating")
            self.terminate()  # Force termination if necessary
        self.logger.info("Data acquisition thread stopped")

    def setSamplingInterval(self, interval):
        """Update sampling interval"""
        self.sampling_interval = interval
        self.logger.info(f"Sampling interval updated to {interval}s")


class InstrumentController(QObject):
    """Controller for Keithley 2290-5 and 6485 instruments"""

    # Signals
    power_supply_connected = pyqtSignal(bool, str)  # connected, info
    picoammeter_connected = pyqtSignal(bool, str)   # connected, info
    data_ready = pyqtSignal(float, float, float)    # time, current, voltage
    log_message = pyqtSignal(str)
    status_message = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Instrument handles
        self.power_supply = None  # Keithley 2290-5
        self.picoammeter = None   # Keithley 6485
        self.resource_manager = None

        # Data acquisition thread
        self.acquisition_thread = None
        self.is_acquiring = False

        # Get logger
        self.logger = get_logger()

        # Initialize VISA
        self.initializeVISA()

    def initializeVISA(self):
        """Initialize the VISA resource manager"""
        try:
            self.resource_manager = pyvisa.ResourceManager()
            self.log_message.emit("VISA resource manager initialized")
            self.logger.info("VISA resource manager initialized")
        except Exception as e:
            error_msg = f"Failed to initialize VISA: {str(e)}"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            self.resource_manager = None

    def scanForInstruments(self):
        """Scan for available GPIB instruments"""
        if not self.resource_manager:
            return {}

        instruments = {}
        try:
            resources = self.resource_manager.list_resources()
            self.log_message.emit(f"Found {len(resources)} VISA resources")
            self.logger.info(f"Found {len(resources)} VISA resources")

            for resource in resources:
                if "GPIB" in resource:
                    try:
                        # Extract GPIB address
                        parts = resource.split("::")
                        if len(parts) >= 2:
                            addr = parts[1]

                            # Try to connect and get identification
                            instr = self.resource_manager.open_resource(resource)
                            instr.timeout = 2000  # 2 second timeout for scan

                            try:
                                idn = instr.query("*IDN?").strip()
                                instruments[addr] = idn
                            except:
                                instruments[addr] = "Unknown instrument"
                            finally:
                                instr.close()

                    except Exception as e:
                        self.log_message.emit(f"Error scanning {resource}: {str(e)}")
                        self.logger.error(f"Error scanning {resource}: {str(e)}\n{traceback.format_exc()}")

        except Exception as e:
            self.log_message.emit(f"Error during scan: {str(e)}")
            self.logger.error(f"Error during scan: {str(e)}\n{traceback.format_exc()}")

        return instruments

    def connectPowerSupply(self, gpib_address):
        """Connect to Keithley 2290-5 power supply"""
        if not self.resource_manager:
            error_msg = "VISA not initialized"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(error_msg)
            return False

        try:
            resource_string = f"GPIB0::{gpib_address}::INSTR"
            self.log_message.emit(f"Connecting to power supply at {resource_string}")
            self.logger.info(f"Connecting to power supply at {resource_string}")

            # Connect to instrument
            self.power_supply = self.resource_manager.open_resource(resource_string)
            self.power_supply.timeout = 5000  # 5 second timeout

            # Reset and initialize
            self.power_supply.write("*RST")
            self.power_supply.write("*CLS")
            self.power_supply.write("*RCL 0")  # Recall default settings

            # Get instrument identification
            idn = self.power_supply.query("*IDN?").strip()
            self.logger.info(f"Power supply identification: {idn}")

            # Verify it's a 2290-5
            if "2290-5" not in idn:
                warning_msg = f"Warning: Expected 2290-5, got: {idn}"
                self.log_message.emit(f"WARNING: {warning_msg}")
                self.logger.warning(warning_msg)

            # Set safe default limits (from manual defaults)
            self.power_supply.write("VLIM 5000")  # 5000V voltage limit
            self.power_supply.write("ILIM 5.25E-3")  # 5.25mA current limit

            self.log_message.emit(f"Power supply connected: {idn}")
            self.logger.info(f"Power supply connected successfully: {idn}")
            self.power_supply_connected.emit(True, idn)
            return True

        except Exception as e:
            error_msg = f"Failed to connect power supply: {str(e)}"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

            if self.power_supply:
                try:
                    self.power_supply.close()
                except Exception as close_error:
                    self.logger.error(f"Error closing power supply: {str(close_error)}")
                self.power_supply = None

            self.power_supply_connected.emit(False, "")
            return False

    def connectPicoammeter(self, gpib_address):
        """Connect to Keithley 6485 picoammeter"""
        if not self.resource_manager:
            error_msg = "VISA not initialized"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(error_msg)
            return False

        try:
            resource_string = f"GPIB0::{gpib_address}::INSTR"
            self.log_message.emit(f"Connecting to picoammeter at {resource_string}")
            self.logger.info(f"Connecting to picoammeter at {resource_string}")

            # Connect to instrument
            self.picoammeter = self.resource_manager.open_resource(resource_string)
            self.picoammeter.timeout = 5000  # 5 second timeout

            # Reset and initialize according to 6485 manual
            self.picoammeter.write("*RST")
            self.picoammeter.write("*CLS")

            # Configure for current measurements (6485 specific commands)
            self.picoammeter.write("SYST:ZCH OFF")  # Disable zero check
            self.picoammeter.write("CURR:RANG:AUTO ON")  # Enable auto-ranging
            self.picoammeter.write("CURR:NPLC 1")  # 1 PLC integration time
            self.picoammeter.write("FORM:ELEM READ")  # Format for readings only

            # Get instrument identification
            idn = self.picoammeter.query("*IDN?").strip()
            self.logger.info(f"Picoammeter identification: {idn}")

            # Verify it's a 6485
            if "6485" not in idn:
                warning_msg = f"Warning: Expected 6485, got: {idn}"
                self.log_message.emit(f"WARNING: {warning_msg}")
                self.logger.warning(warning_msg)

            self.log_message.emit(f"Picoammeter connected: {idn}")
            self.logger.info(f"Picoammeter connected successfully: {idn}")
            self.picoammeter_connected.emit(True, idn)
            return True

        except Exception as e:
            error_msg = f"Failed to connect picoammeter: {str(e)}"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

            if self.picoammeter:
                try:
                    self.picoammeter.close()
                except Exception as close_error:
                    self.logger.error(f"Error closing picoammeter: {str(close_error)}")
                self.picoammeter = None

            self.picoammeter_connected.emit(False, "")
            return False

    def disconnectAllInstruments(self):
        """Safely disconnect all instruments with improved error recovery"""
        self.logger.info("Disconnecting all instruments")

        # Stop data acquisition
        if self.is_acquiring:
            self.stopDataAcquisition()

        # Disconnect power supply
        if self.power_supply:
            try:
                self._safeDisconnectPowerSupply()
            except Exception as e:
                error_msg = f"Error disconnecting power supply: {str(e)}"
                self.log_message.emit(f"ERROR: {error_msg}")
                self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            finally:
                self.power_supply = None
                self.power_supply_connected.emit(False, "")

        # Disconnect picoammeter
        if self.picoammeter:
            try:
                self._safeDisconnectPicoammeter()
            except Exception as e:
                error_msg = f"Error disconnecting picoammeter: {str(e)}"
                self.log_message.emit(f"ERROR: {error_msg}")
                self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
            finally:
                self.picoammeter = None
                self.picoammeter_connected.emit(False, "")

    def _clearInstrumentErrors(self, instrument, instrument_name):
        """Clear error queue and status from instrument"""
        try:
            # Clear errors and status
            instrument.write("*CLS")
            time.sleep(0.1)  # Allow time for clear to complete

            # Query and clear any remaining errors
            try:
                errors = []
                for _ in range(10):  # Check up to 10 errors
                    error = instrument.query("SYST:ERR?").strip()
                    if "No error" in error or "+0," in error:
                        break
                    errors.append(error)

                if errors:
                    self.logger.warning(f"{instrument_name} had errors: {'; '.join(errors)}")
                    self.log_message.emit(f"WARNING: {instrument_name} had errors that were cleared")
            except:
                # If error query fails, continue with disconnect
                pass

        except Exception as e:
            self.logger.warning(f"Could not clear {instrument_name} errors: {str(e)}")

    def _waitForInstrumentReady(self, instrument, instrument_name, timeout=3.0):
        """Wait for instrument to be ready for commands"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    # Query operation complete status
                    opc = instrument.query("*OPC?").strip()
                    if opc == "1":
                        return True
                except:
                    pass
                time.sleep(0.1)

            self.logger.warning(f"{instrument_name} did not respond ready within timeout")
            return False

        except Exception as e:
            self.logger.warning(f"Could not check {instrument_name} ready status: {str(e)}")
            return False

    def _safeDisconnectPowerSupply(self):
        """Safely disconnect power supply with proper error handling"""
        self.logger.info("Starting safe power supply disconnect sequence")

        # Step 1: Clear any existing errors
        self._clearInstrumentErrors(self.power_supply, "Power Supply")

        # Step 2: Disable output with verification
        try:
            self.power_supply.write("HVOF")
            self.logger.info("Power supply output disabled")
            time.sleep(1.0)  # Allow more time for HV to discharge

            # Verify output is off
            try:
                output_state = self.power_supply.query("OUTP?").strip()
                if output_state != "0":
                    self.logger.warning(f"Power supply output state unexpected: {output_state}")
            except:
                pass  # Continue even if query fails

        except Exception as e:
            self.logger.error(f"Failed to disable power supply output: {str(e)}")
            # Continue with disconnect even if HVOF fails

        # Step 3: Wait for instrument to be ready
        self._waitForInstrumentReady(self.power_supply, "Power Supply")

        # Step 4: Clear errors again before local mode
        self._clearInstrumentErrors(self.power_supply, "Power Supply")

        # Step 5: Return to local control with multiple attempts
        local_success = False
        for attempt in range(3):
            try:
                self.power_supply.write("SYST:LOC")
                time.sleep(0.5)  # Allow time for local mode to take effect

                # Try to verify local mode (this might fail if already local)
                try:
                    # Send a simple query to check if communication still works
                    self.power_supply.query("*IDN?")
                    # If we get here, instrument is still in remote mode
                    if attempt < 2:  # Don't log warning on last attempt
                        self.logger.warning(f"Power supply local mode attempt {attempt + 1} - still responding to queries")
                except:
                    # If query fails, instrument likely went to local mode successfully
                    local_success = True
                    break

            except Exception as loc_error:
                self.logger.warning(f"Power supply local mode attempt {attempt + 1} failed: {str(loc_error)}")
                if attempt < 2:  # Don't sleep on last attempt
                    time.sleep(0.5)

        if local_success:
            self.logger.info("Power supply returned to local control")
        else:
            self.logger.warning("Power supply local mode status uncertain - attempting to close connection")

        # Step 6: Close the connection
        try:
            self.power_supply.close()
            self.log_message.emit("Power supply disconnected")
            self.logger.info("Power supply connection closed")
        except Exception as e:
            self.logger.error(f"Error closing power supply connection: {str(e)}")

    def _safeDisconnectPicoammeter(self):
        """Safely disconnect picoammeter with proper error handling"""
        self.logger.info("Starting safe picoammeter disconnect sequence")

        # Step 1: Clear any existing errors
        self._clearInstrumentErrors(self.picoammeter, "Picoammeter")

        # Step 2: Stop any ongoing measurements
        try:
            self.picoammeter.write("ABOR")  # Abort any running measurements
            time.sleep(0.2)
        except:
            pass  # Continue even if abort fails

        # Step 3: Wait for instrument to be ready
        self._waitForInstrumentReady(self.picoammeter, "Picoammeter")

        # Step 4: Clear errors again before local mode
        self._clearInstrumentErrors(self.picoammeter, "Picoammeter")

        # Step 5: Return to local control with multiple attempts
        local_success = False
        for attempt in range(3):
            try:
                self.picoammeter.write("SYST:LOC")
                time.sleep(0.5)  # Allow time for local mode to take effect

                # Try to verify local mode (this might fail if already local)
                try:
                    # Send a simple query to check if communication still works
                    self.picoammeter.query("*IDN?")
                    # If we get here, instrument is still in remote mode
                    if attempt < 2:  # Don't log warning on last attempt
                        self.logger.warning(f"Picoammeter local mode attempt {attempt + 1} - still responding to queries")
                except:
                    # If query fails, instrument likely went to local mode successfully
                    local_success = True
                    break

            except Exception as loc_error:
                self.logger.warning(f"Picoammeter local mode attempt {attempt + 1} failed: {str(loc_error)}")
                if attempt < 2:  # Don't sleep on last attempt
                    time.sleep(0.5)

        if local_success:
            self.logger.info("Picoammeter returned to local control")
        else:
            self.logger.warning("Picoammeter local mode status uncertain - attempting to close connection")

        # Step 6: Close the connection
        try:
            self.picoammeter.close()
            self.log_message.emit("Picoammeter disconnected")
            self.logger.info("Picoammeter connection closed")
        except Exception as e:
            self.logger.error(f"Error closing picoammeter connection: {str(e)}")

    def __del__(self):
        """Destructor - ensure proper cleanup"""
        try:
            # Make sure we stop any acquisition threads
            if hasattr(self, 'is_acquiring') and self.is_acquiring:
                self.stopDataAcquisition()

            # Clean up any resources
            if hasattr(self, 'power_supply') and self.power_supply:
                try:
                    # Safety first - disable HV
                    try:
                        self.power_supply.write("HVOF")
                    except:
                        pass
                    # Return to local control
                    try:
                        self.power_supply.write("SYST:LOC")
                    except:
                        pass
                    self.power_supply.close()
                except:
                    pass

            if hasattr(self, 'picoammeter') and self.picoammeter:
                try:
                    # Return to local control
                    try:
                        self.picoammeter.write("SYST:LOC")
                    except:
                        pass
                    self.picoammeter.close()
                except:
                    pass

            # Explicitly disconnect signals
            try:
                if hasattr(self, 'power_supply_connected'):
                    self.power_supply_connected.disconnect()
                if hasattr(self, 'picoammeter_connected'):
                    self.picoammeter_connected.disconnect()
                if hasattr(self, 'data_ready'):
                    self.data_ready.disconnect()
                if hasattr(self, 'log_message'):
                    self.log_message.disconnect()
                if hasattr(self, 'status_message'):
                    self.status_message.disconnect()
            except:
                # This is normal if signals weren't connected
                pass

            # Log resource cleanup if logger is available
            if hasattr(self, 'logger'):
                self.logger.info("InstrumentController resources cleaned up")

        except Exception:
            # Don't let errors in __del__ propagate
            if hasattr(self, 'logger'):
                self.logger.error("Error during InstrumentController cleanup")
            pass

    # Power Supply Control Methods (2290-5 SCPI commands)
    def setVoltage(self, voltage):
        """Set output voltage using VSET command"""
        if not self.power_supply:
            return False
        try:
            self.power_supply.write(f"VSET {voltage}")
            self.log_message.emit(f"Voltage set to {voltage}V")
            self.logger.info(f"Voltage set to {voltage}V")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error setting voltage: {str(e)}")
            self.logger.error(f"Error setting voltage: {str(e)}\n{traceback.format_exc()}")
            return False

    def setVoltageLimit(self, limit):
        """Set voltage limit using VLIM command"""
        if not self.power_supply:
            return False
        try:
            self.power_supply.write(f"VLIM {limit}")
            self.log_message.emit(f"Voltage limit set to {limit}V")
            self.logger.info(f"Voltage limit set to {limit}V")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error setting voltage limit: {str(e)}")
            self.logger.error(f"Error setting voltage limit: {str(e)}\n{traceback.format_exc()}")
            return False

    def setCurrentLimit(self, limit_ma):
        """Set current limit using ILIM command (convert mA to A)"""
        if not self.power_supply:
            return False
        try:
            limit_a = limit_ma / 1000.0  # Convert mA to A
            self.power_supply.write(f"ILIM {limit_a}")
            self.log_message.emit(f"Current limit set to {limit_ma}mA")
            self.logger.info(f"Current limit set to {limit_ma}mA")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error setting current limit: {str(e)}")
            self.logger.error(f"Error setting current limit: {str(e)}\n{traceback.format_exc()}")
            return False

    def enableOutput(self):
        """Enable high voltage output using HVON command"""
        if not self.power_supply:
            return False
        try:
            self.power_supply.write("HVON")
            self.log_message.emit("High voltage output ENABLED")
            self.logger.info("High voltage output ENABLED")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error enabling output: {str(e)}")
            self.logger.error(f"Error enabling output: {str(e)}\n{traceback.format_exc()}")
            return False

    def disableOutput(self):
        """Disable high voltage output using HVOF command"""
        if not self.power_supply:
            return False
        try:
            self.power_supply.write("HVOF")
            self.log_message.emit("High voltage output DISABLED")
            self.logger.info("High voltage output DISABLED")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error disabling output: {str(e)}")
            self.logger.error(f"Error disabling output: {str(e)}\n{traceback.format_exc()}")
            return False

    def readVoltage(self):
        """Read output voltage using VOUT? query"""
        if not self.power_supply:
            return None
        try:
            voltage_str = self.power_supply.query("VOUT?").strip()
            return float(voltage_str)
        except Exception as e:
            self.log_message.emit(f"ERROR: Error reading voltage: {str(e)}")
            self.logger.error(f"Error reading voltage: {str(e)}\n{traceback.format_exc()}")
            return None

    # Picoammeter Control Methods (6485 SCPI commands)
    def readCurrent(self):
        """Read current using READ? command"""
        if not self.picoammeter:
            return None
        try:
            current_str = self.picoammeter.query("READ?").strip()
            return float(current_str)
        except Exception as e:
            self.log_message.emit(f"ERROR: Error reading current: {str(e)}")
            self.logger.error(f"Error reading current: {str(e)}\n{traceback.format_exc()}")
            return None

    def setCurrentRange(self, range_value):
        """Set current range or enable auto-ranging"""
        if not self.picoammeter:
            return False
        try:
            if range_value == "AUTO":
                self.picoammeter.write("CURR:RANG:AUTO ON")
                self.log_message.emit("Current range set to AUTO")
                self.logger.info("Current range set to AUTO")
            else:
                self.picoammeter.write("CURR:RANG:AUTO OFF")
                self.picoammeter.write(f"CURR:RANG {range_value}")
                self.log_message.emit(f"Current range set to {range_value}A")
                self.logger.info(f"Current range set to {range_value}A")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error setting current range: {str(e)}")
            self.logger.error(f"Error setting current range: {str(e)}\n{traceback.format_exc()}")
            return False

    def setIntegrationTime(self, nplc):
        """Set integration time using NPLC command"""
        if not self.picoammeter:
            return False
        try:
            self.picoammeter.write(f"CURR:NPLC {nplc}")
            self.log_message.emit(f"Integration time set to {nplc} PLC")
            self.logger.info(f"Integration time set to {nplc} PLC")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error setting integration time: {str(e)}")
            self.logger.error(f"Error setting integration time: {str(e)}\n{traceback.format_exc()}")
            return False

    def performZeroCheck(self):
        """Perform zero check and correction"""
        if not self.picoammeter:
            return False
        try:
            self.picoammeter.write("SYST:ZCH ON")
            self.picoammeter.write("INIT")
            self.picoammeter.write("SYST:ZCOR:ACQ")
            self.picoammeter.write("SYST:ZCH OFF")
            self.log_message.emit("Zero check completed")
            self.logger.info("Zero check completed")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error during zero check: {str(e)}")
            self.logger.error(f"Error during zero check: {str(e)}\n{traceback.format_exc()}")
            return False

    def setAutoZero(self, enabled):
        """Enable or disable auto zero function"""
        if not self.picoammeter:
            return False
        try:
            if enabled:
                self.picoammeter.write("SYST:AZER ON")
                self.log_message.emit("Auto zero enabled")
                self.logger.info("Auto zero enabled")
            else:
                self.picoammeter.write("SYST:AZER OFF")
                self.log_message.emit("Auto zero disabled")
                self.logger.info("Auto zero disabled")
            return True
        except Exception as e:
            self.log_message.emit(f"ERROR: Error setting auto zero: {str(e)}")
            self.logger.error(f"Error setting auto zero: {str(e)}\n{traceback.format_exc()}")
            return False

    # Data Acquisition Methods
    def startDataAcquisition(self, sampling_rate):
        """Start continuous data acquisition"""
        if not self.picoammeter:
            error_msg = "Cannot start acquisition: Picoammeter not connected"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(error_msg)
            return False

        if self.is_acquiring:
            warning_msg = "Data acquisition already running"
            self.log_message.emit(f"WARNING: {warning_msg}")
            self.logger.warning(warning_msg)
            return False

        try:
            sampling_interval = 1.0 / sampling_rate
            self.logger.info(f"Starting data acquisition at {sampling_rate} Hz (interval: {sampling_interval}s)")

            # Create thread with current instrument references
            self.acquisition_thread = DataAcquisitionThread(
                self.picoammeter, self.power_supply, sampling_interval)

            # Connect signals
            self.acquisition_thread.data_acquired.connect(self.data_ready.emit)
            self.acquisition_thread.error_occurred.connect(self.log_message.emit)

            # Start the thread
            self.acquisition_thread.start()
            self.is_acquiring = True

            self.log_message.emit(f"Data acquisition started at {sampling_rate} Hz")
            return True

        except Exception as e:
            error_msg = f"Error starting data acquisition: {str(e)}"
            self.log_message.emit(f"ERROR: {error_msg}")
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

            # Clean up partially initialized resources
            if self.acquisition_thread:
                try:
                    self.acquisition_thread.stop()
                except:
                    pass
                self.acquisition_thread = None

            self.is_acquiring = False
            return False

    def stopDataAcquisition(self):
        """Stop data acquisition and ensure proper thread cleanup"""
        if self.acquisition_thread and self.is_acquiring:
            try:
                self.logger.info("Stopping data acquisition")

                # Signal the thread to stop
                self.acquisition_thread.running = False

                # Give the thread time to process the stop signal
                if not self.acquisition_thread.wait(2000):  # Wait up to 2 seconds
                    # Force termination if it doesn't stop gracefully
                    self.logger.warning("Data acquisition thread did not stop gracefully, terminating")
                    self.acquisition_thread.terminate()
                    self.log_message.emit("WARNING: Had to force terminate data acquisition thread")

                # Cleanup - disconnect all signals to allow proper garbage collection
                try:
                    self.acquisition_thread.data_acquired.disconnect()
                    self.acquisition_thread.error_occurred.disconnect()
                except TypeError:
                    # Already disconnected, ignore
                    pass

                # Clear the reference
                self.acquisition_thread = None
                self.is_acquiring = False
                self.log_message.emit("Data acquisition stopped")
                self.logger.info("Data acquisition successfully stopped")
                return True

            except Exception as e:
                error_msg = f"Error stopping data acquisition: {str(e)}"
                self.log_message.emit(f"ERROR: {error_msg}")
                self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

                # Ensure thread is terminated in case of error
                if self.acquisition_thread:
                    try:
                        if self.acquisition_thread.isRunning():
                            self.acquisition_thread.terminate()
                            self.acquisition_thread.wait()
                    except:
                        pass

                self.acquisition_thread = None
                self.is_acquiring = False
                return False

        return False  # Nothing was running to stop

    def setSamplingRate(self, rate):
        """Update sampling rate during acquisition"""
        if self.acquisition_thread and self.is_acquiring:
            interval = 1.0 / rate
            self.acquisition_thread.setSamplingInterval(interval)