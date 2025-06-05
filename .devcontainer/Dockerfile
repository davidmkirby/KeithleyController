FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies for PyQt6 and GUI applications
RUN apt-get update && apt-get install -y \
    # Qt6 and GUI dependencies
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
    libxrender1 \
    # X11 server for GUI
    xvfb \
    x11-utils \
    x11-xserver-utils \
    dbus-x11 \
    # Serial communication
    setserial \
    minicom \
    picocom \
    # Development tools
    git \
    curl \
    wget \
    vim \
    nano \
    htop \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set up environment variables
ENV DISPLAY=:99
ENV QT_QPA_PLATFORM=xcb
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

# Create the user if it doesn't exist
RUN if ! id -u $USERNAME > /dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME \
        && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
        && apt-get update \
        && apt-get install -y sudo \
        && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
        && chmod 0440 /etc/sudoers.d/$USERNAME; \
    fi

# Switch to the user
USER $USERNAME

# Install Python packages that are commonly needed
RUN python -m pip install --upgrade pip \
    && pip install --user \
        PyQt6 \
        pyqtgraph \
        numpy \
        pandas \
        pyserial \
        pyvisa \
        pyinstaller \
        black \
        flake8 \
        pylint \
        pytest \
        isort \
        mypy

# Set the working directory
WORKDIR /workspace

# Create startup script for X11
RUN echo '#!/bin/bash\n\
# Start X11 server if not running\n\
if ! pgrep -x "Xvfb" > /dev/null; then\n\
    Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &\n\
    sleep 2\n\
fi\n\
\n\
# Start D-Bus if not running\n\
if ! pgrep -x "dbus-daemon" > /dev/null; then\n\
    sudo service dbus start > /dev/null 2>&1\n\
fi\n\
\n\
echo "GUI environment ready!"\n\
exec "$@"' > /usr/local/bin/start-gui \
    && chmod +x /usr/local/bin/start-gui

# Set default command
CMD ["sleep", "infinity"]
