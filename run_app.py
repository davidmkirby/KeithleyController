#!/usr/bin/env python3
"""
Launcher script for Keithley Dual Controller application.
This script adds the current directory to the Python path
to ensure proper module resolution.
"""

import os
import sys

# Configure environment for proper Unicode handling on Windows
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Set console code page to UTF-8 on Windows
if sys.platform.startswith('win'):
    try:
        import subprocess
        subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
    except Exception:
        pass  # Fail silently if chcp command is not available

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now run the main application
from src.main import main

if __name__ == "__main__":
    sys.exit(main())
