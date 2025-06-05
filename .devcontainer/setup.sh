#!/bin/bash

echo "🚀 Setting up Keithley Controller development environment..."

# Update package lists
sudo apt-get update

# Install system dependencies for PyQt6 and GUI applications
echo "📦 Installing system dependencies for PyQt6..."
sudo apt-get install -y \
    qt6-base-dev \
    qt6-tools-dev \
    qt6-tools-dev-tools \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    libxcb-shape0 \
    libxcb-sync1 \
    libxcb-xkb1 \
    libxcb1 \
    libx11-xcb1 \
    libdbus-1-3 \
    libfontconfig1 \
    libfreetype6 \
    libxext6 \
    libxrender1

# Install X11 server for GUI applications
echo "🖥️  Installing X11 server for GUI support..."
sudo apt-get install -y \
    xvfb \
    x11-utils \
    x11-xserver-utils \
    dbus-x11

# Install serial communication tools
echo "🔌 Installing serial communication tools..."
sudo apt-get install -y \
    setserial \
    minicom \
    picocom

# Clean up package cache
sudo apt-get clean
sudo rm -rf /var/lib/apt/lists/*

# Upgrade pip
echo "⬆️  Upgrading pip..."
python -m pip install --upgrade pip

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install --user -r requirements.txt
else
    echo "⚠️  requirements.txt not found, installing basic dependencies..."
    pip install --user PyQt6 pyqtgraph numpy pandas pyserial pyvisa pyinstaller
fi

# Install development dependencies
echo "🛠️  Installing development tools..."
pip install --user \
    black \
    flake8 \
    pylint \
    pytest \
    isort \
    mypy

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p logs
mkdir -p dist
mkdir -p build

# Set up X11 display for GUI applications
echo "🖼️  Setting up virtual display..."
echo 'export DISPLAY=:99' >> ~/.bashrc
echo 'export DISPLAY=:99' >> ~/.zshrc

# Create a script to start X11 server
cat > start_gui.sh << 'EOF'
#!/bin/bash
# Start X11 server in background if not running
if ! pgrep -x "Xvfb" > /dev/null; then
    echo "Starting X11 virtual display..."
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &
    sleep 2
fi

# Start D-Bus if not running
if ! pgrep -x "dbus-daemon" > /dev/null; then
    echo "Starting D-Bus..."
    sudo service dbus start > /dev/null 2>&1
fi

echo "GUI environment ready! You can now run:"
echo "  python keithley_controller.py"
echo "  python build_app.py"
EOF

chmod +x start_gui.sh

# Create a development helper script
cat > dev_setup.sh << 'EOF'
#!/bin/bash
echo "🔧 Keithley Controller Development Helper"
echo "========================================"
echo ""
echo "Available commands:"
echo "  ./start_gui.sh          - Start GUI environment"
echo "  python keithley_controller.py  - Run the application"
echo "  python build_app.py --clean    - Build executables"
echo "  python -m pytest tests/        - Run tests"
echo "  black src/ *.py                - Format code"
echo "  flake8 src/ *.py               - Lint code"
echo ""
echo "Environment info:"
echo "  Python: $(python --version)"
echo "  PyQt6: $(python -c 'import PyQt6; print(PyQt6.QtCore.qVersion())' 2>/dev/null || echo 'Not installed')"
echo "  Display: $DISPLAY"
echo ""
EOF

chmod +x dev_setup.sh

# Set proper permissions for log directory
chmod 755 logs

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "🎯 Next steps:"
echo "   1. Run './start_gui.sh' to start the GUI environment"
echo "   2. Run './dev_setup.sh' to see available commands"
echo "   3. Run 'python keithley_controller.py' to test your application"
echo ""
echo "🔧 For help, run './dev_setup.sh'"
