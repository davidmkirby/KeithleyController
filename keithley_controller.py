#!/usr/bin/env python3
"""
Keithley Controller - Application Launcher
This script provides a convenient way to start the application from any directory.
"""

import os
import sys
import subprocess

def main():
    """Run the Keithley Controller application"""
    # Get the directory containing this script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Set the Python path to include the project root
    env = os.environ.copy()
    env["PYTHONPATH"] = script_dir

    # Path to the main application file
    main_script = os.path.join(script_dir, "src", "main.py")

    print("Starting Keithley Dual Controller...")

    # Run the application
    try:
        subprocess.run([sys.executable, main_script], env=env, check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error running application: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nApplication terminated by user")
        return 0

if __name__ == "__main__":
    sys.exit(main())
