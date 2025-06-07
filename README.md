# Keithley 2290-5 & 6485 Dual Controller

PyQt6 application for controlling Keithley 2290-5 High Voltage Power Supply and 6485 Picoammeter instruments via GPIB interface.

## Features

- **GPIB Control**: Control both instruments using SCPI commands
- **Real-time Monitoring**: Live voltage and current readings with auto-updates
- **Data Acquisition**: Data logging with live plotting
- **Data Export**: Export measurement data to CSV with timestamps
- **Safety Features**: Emergency stop, confirmation dialogs, and safety limits
- **Activity Logging**: Logging for troubleshooting
- **Interface**: Tabbed interface

## Requirements

### Hardware
- Keithley 2290-5 High Voltage Power Supply (up to 5kV)
- Keithley 6485 Picoammeter
- NI GPIB-USB-HS adapter (or compatible GPIB interface)
- GPIB cables and safety equipment

### Software Dependencies

Required Python packages:
```bash
# Core GUI Framework
PyQt6>=6.4.0
PyQt6-QScintilla>=2.14.1

# Instrument Communication
pyvisa>=1.13.0
pyvisa-py>=0.7.0  # Pure Python VISA backend (if NI-VISA not available)

# Data Processing and Visualization
numpy>=1.21.0
pyqtgraph>=0.13.0
pandas>=1.5.0

# See requirements.txt for complete list
```

Install dependencies:
```bash
pip install -r requirements.txt
```

### VISA Drivers
- Install NI-VISA runtime and NI-488.2 drivers for GPIB communication
- Available from National Instruments website

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/davidmkirby/KeithleyController.git
   cd KeithleyController
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install GPIB drivers**:
   - Download and install NI-VISA from National Instruments
   - Install NI-488.2 drivers for GPIB support

## Usage

### Starting the Application

Run the application:

```bash
# Using main.py from project root
cd KeithleyController
python src/main.py

# Using launcher script
cd KeithleyController
./keithley_controller.py
```

### Initial Setup

1. **Configure GPIB Addresses** (Settings Tab):
   - Power Supply (2290-5): Default address 14
   - Picoammeter (6485): Default address 22
   - Adjust addresses to match your instrument configuration

2. **Connect Instruments** (Control Panel):
   - Use "Connect All Instruments" from Connection menu
   - Or connect individually using Control Panel buttons
   - Verify connections show green status

3. **Safety Setup**:
   - Set voltage and current limits
   - Ensure interlock connections
   - Test emergency stop (F1 key)

### Basic Operation

#### Manual Control
1. Go to **Control Panel** tab
2. Set voltage using the voltage spinbox
3. Click "Set Voltage" to apply
4. Set voltage and current limits for safety
5. Click "ENABLE HV OUTPUT" to turn on high voltage
6. Monitor readings in Live Measurements section

#### Data Acquisition
1. Go to **Data Acquisition** tab
2. Set sampling rate (0.1 to 10 Hz)
3. Click "Start Recording" to begin data collection
4. Monitor real-time plot of current vs. time
5. Click "Stop Recording" when finished
6. Export data using "Export Data" button

### Safety Features

- **Emergency Stop**: Press F1 or use Safety menu to disable all outputs
- **Confirmation Dialogs**: Confirms before enabling high voltage
- **Auto Shutdowns**: Instruments disconnect safely on application exit
- **Current Limits**: Protection against overcurrent conditions
- **Activity Logging**: All operations are logged for review

## File Structure

```
KeithleyController/
├── keithley_controller.py    # Launcher script
├── requirements.txt          # Dependencies list
├── README.md                 # This file
├── logs/                     # Log files directory
├── src/                      # Source code
│   ├── main.py               # Application entry point
│   ├── main_window.py        # Main window class
│   ├── core/                 # Core functionality
│   │   ├── instrument_control.py  # VISA/SCPI communication
│   │   └── logger.py         # Logging system
│   └── ui/                   # User interface
│       ├── control_tab.py    # Manual control interface
│       ├── plotting_tab.py   # Data acquisition and plotting
│       ├── settings_tab.py   # Configuration settings
│       ├── log_tab.py        # Activity logging
│       └── theme.py          # UI styling
```

## SCPI Commands Used

### Keithley 2290-5 Power Supply
- `VSET <value>` - Set output voltage
- `VOUT?` - Query output voltage
- `HVON` - Enable high voltage output
- `HVOF` - Disable high voltage output
- `VLIM <value>` - Set voltage limit
- `ILIM <value>` - Set current limit
- `SYST:LOC` - Return to local control (restore front panel)
- `*RST` - Reset instrument
- `*IDN?` - Query identification

### Keithley 6485 Picoammeter
- `READ?` - Take current reading
- `CURR:RANG <value>` - Set current range
- `CURR:RANG:AUTO ON` - Enable auto-ranging
- `CURR:NPLC <value>` - Set integration time
- `SYST:ZCH ON/OFF` - Control zero check
- `SYST:ZCOR:ACQ` - Acquire zero correction
- `SYST:AZER ON/OFF` - Enable/disable auto zero correction
- `SYST:LOC` - Return to local control (restore front panel)

## Troubleshooting

### Connection Issues
1. **Verify GPIB addresses** in Settings tab
2. **Check VISA installation** - run `python -c "import pyvisa; print(pyvisa.ResourceManager().list_resources())"`
3. **Test individual connections** using Settings tab test buttons
4. **Check physical connections** - GPIB cables, power, etc.
5. **Front panel controls disabled** - Normal when connected remotely via GPIB. Disconnect from GUI to restore local control.

### Data Acquisition Problems
1. **Ensure picoammeter is connected** before starting recording
2. **Check sampling rate** - high rates may cause timeouts
3. **Verify current range settings** for your measurement needs
4. **Review Activity Log** for error messages

### High Voltage Safety
1. **Always disable HV** before disconnecting instruments
2. **Use safety enclosures** with interlocks
3. **Never touch exposed connections** when HV is enabled
4. **Keep emergency stop accessible** (F1 key)

### Local Control Recovery
1. **Front panel locked** - When instruments are connected via GUI, front panel controls are disabled
2. **Disconnect properly** - Use disconnect buttons in Control Panel to restore front panel operation
3. **Emergency recovery** - If GUI crashes, power cycle instruments to restore local control
4. **Manual recovery** - Send `SYST:LOC` command via GPIB to restore local control

### Import/Module Issues
1. **Run from project root** directory
2. **Use launcher scripts** (keithley_controller.py)
3. **Set PYTHONPATH** environment variable if needed
4. **Check Python version** compatibility (3.8+ recommended)

## Data Export Format

CSV files contain the following columns:
- `Time (s)` - Elapsed time since recording started
- `Current (A)` - Current reading from picoammeter
- `Voltage (V)` - Voltage reading from power supply
- `Timestamp` - Unix timestamp of measurement

## Configuration Files

The application stores settings in memory during runtime. For persistent settings, use the Settings tab to configure:
- GPIB addresses
- Export directories
- Safety limits
- Display preferences

## Packaging as Standalone Executable

The Keithley Dual Controller can be packaged as a standalone executable for distribution to users without Python installed.

### Prerequisites

Install PyInstaller:
```bash
pip install pyinstaller
```

### Building the Application

To build the standalone application:

```bash
# Build the application (creates directory with all dependencies)
./build_app.py

# Or, create single executable file (larger but more portable)
./build_app.py --onefile

# Clean previous builds
./build_app.py --clean

# For cross-architecture builds (e.g., building x86_64 executables on ARM)
./build_app.py --target-arch x86_64
```

### Output Locations

Packaged application will be created in the `dist` directory:

- **macOS**: `dist/KeithleyDualController.app`
- **Windows**: `dist\KeithleyDualController\KeithleyDualController.exe`
- **Linux**: `dist/KeithleyDualController/KeithleyDualController`

### Cross-Platform Building

To create executables for different platforms:

1. **macOS**:
   - Build on Mac system
   - For Apple Silicon (M1/M2/M3) Macs, default is ARM64
   - Use `--target-arch x86_64` to build for Intel Macs

2. **Windows**:
   - **Recommended**: Build on x86_64 Windows system or VM
   - If using Windows on ARM (in VM on Apple Silicon):
     - Install x64 Python, not ARM Python
     - Use `--target-arch x86_64` for maximum compatibility
   - Resulting executable will run on most Windows PCs

3. **Linux**:
   - Build on Linux system or use virtual machine
   - For maximum compatibility, build on x86_64 system

For distribution, consider using CI/CD services that offer multi-platform build environments.

## Support

For issues related to:
- **Instrument communication**: Check SCPI command reference in Help menu
- **GPIB connectivity**: Verify NI-VISA installation and drivers
- **Application bugs**: Review Activity Log for error information
- **Safety concerns**: Consult instrument manuals and follow procedures

## References

- [Keithley 2290-5 User Manual](https://www.tek.com/en/manual/model-2290-5-kv-power-supply-user%E2%80%99s-manual)
- [Keithley 6485 Documentation](https://www.tek.com/en/products/keithley)
- [PyVISA Documentation](https://pyvisa.readthedocs.io/)
- [National Instruments VISA](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html)

## License

This software is provided as-is for educational and research purposes. Always follow safety procedures when working with high voltage equipment.

## Last Updated

May 22, 2025

---

**WARNING: This application controls high voltage equipment. Always follow safety procedures and consult instrument manuals before use.**