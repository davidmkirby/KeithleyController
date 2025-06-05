# Keithley Controller - Development Container

This directory contains the configuration for a GitHub Codespaces development environment optimized for the Keithley Controller PyQt6 application.

## 🚀 Quick Start

### Option 1: GitHub Codespaces (Recommended)
1. Go to your repository on GitHub
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on main"
5. Wait for the environment to build (2-3 minutes)

### Option 2: VS Code Dev Containers (Local)
1. Install Docker Desktop
2. Install the "Dev Containers" extension in VS Code
3. Open the project folder in VS Code
4. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
5. Select "Dev Containers: Reopen in Container"

## 🛠️ What's Included

### System Dependencies
- **Python 3.11** with pip
- **Qt6** development libraries
- **X11 server** (Xvfb) for GUI applications
- **Serial communication** tools
- **Git** and **GitHub CLI**

### Python Packages
- **PyQt6** - GUI framework
- **pyqtgraph** - Plotting library
- **numpy, pandas** - Data manipulation
- **pyserial, pyvisa** - Instrument communication
- **pyinstaller** - Application building
- **Development tools**: black, flake8, pylint, pytest, isort, mypy

### VS Code Extensions
- Python development tools
- Code formatting and linting
- GitHub Actions support
- YAML/XML support
- Jupyter notebook support

## 🖥️ Running GUI Applications

The container includes a virtual X11 display for running GUI applications:

```bash
# Start the GUI environment
./start_gui.sh

# Run your application
python keithley_controller.py

# Build your application
python build_app.py --clean
```

## 📁 Project Structure

```
.devcontainer/
├── devcontainer.json     # Main configuration
├── Dockerfile           # Custom container image
├── docker-compose.yml   # Multi-service setup
├── setup.sh            # Post-creation setup script
└── README.md           # This file
```

## 🔧 Development Workflow

### Available Helper Scripts
- `./start_gui.sh` - Initialize GUI environment
- `./dev_setup.sh` - Show development commands and info

### Common Commands
```bash
# Format code
black src/ *.py

# Lint code
flake8 src/ *.py

# Run tests
python -m pytest tests/

# Build application
python build_app.py --clean

# Install new dependencies
pip install --user <package-name>
# Don't forget to update requirements.txt!
```

## 🔍 Debugging GUI Applications

### X11 Display Issues
If GUI applications don't start:
```bash
# Check X11 server
ps aux | grep Xvfb

# Restart X11 server
pkill Xvfb
./start_gui.sh

# Check display variable
echo $DISPLAY  # Should be :99
```

### Serial Port Access
Note: Hardware serial ports are not available in Codespaces. For development:
- Use simulated/mock serial devices
- Test with local hardware using VS Code Dev Containers

## 📝 Customization

### Adding Python Packages
1. Add to `requirements.txt` in the project root
2. Rebuild the container or run `pip install --user -r requirements.txt`

### Adding System Packages
1. Edit `.devcontainer/Dockerfile`
2. Add packages to the `apt-get install` command
3. Rebuild the container

### VS Code Settings
Edit the `customizations.vscode.settings` section in `devcontainer.json`

## 🚨 Troubleshooting

### Container Won't Start
- Check Docker Desktop is running (local development)
- Verify internet connection for package downloads
- Check GitHub Codespaces quota/billing

### GUI Applications Crash
- Ensure X11 server is running: `./start_gui.sh`
- Check Qt platform plugin: `export QT_QPA_PLATFORM=xcb`
- Verify display variable: `export DISPLAY=:99`

### Build Failures
- Check all dependencies are installed
- Verify Python path: `echo $PYTHONPATH`
- Clean build directory: `python build_app.py --clean`

## 💡 Tips

- **Save frequently** - Codespaces auto-save but manual saves ensure persistence
- **Use port forwarding** - Forward ports for web-based debugging tools
- **Pre-build templates** - Set up prebuilds for faster startup times
- **Resource monitoring** - Use `htop` to monitor CPU/memory usage

## 🔗 Useful Links

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [VS Code Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
- [Docker Documentation](https://docs.docker.com/)
