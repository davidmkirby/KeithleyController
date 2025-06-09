#!/usr/bin/env python3
"""
Build script for Keithley Dual Controller
Creates standalone executables for different platforms
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil

def main():
    """Build the Keithley Dual Controller application"""
    parser = argparse.ArgumentParser(description='Build Keithley Dual Controller')
    parser.add_argument('--clean', action='store_true', help='Clean build directories')
    parser.add_argument('--onefile', action='store_true', help='Create a single executable file')
    parser.add_argument('--target-arch', choices=['x86_64', 'arm64'],
                        help='Target architecture (useful for cross-compilation)')
    args = parser.parse_args()

    # Determine platform
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Get project root
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Clean build directories if requested
    if args.clean:
        print("Cleaning build directories...")
        build_dir = os.path.join(project_root, 'build')
        dist_dir = os.path.join(project_root, 'dist')
        for dir_to_clean in [build_dir, dist_dir]:
            if os.path.exists(dir_to_clean):
                shutil.rmtree(dir_to_clean)
                print(f"Removed {dir_to_clean}")

    # Set build command based on platform and options
    build_cmd = ['pyinstaller', '--clean']

    if args.onefile:
        build_cmd.append('--onefile')

    # Handle cross-architecture builds
    if args.target_arch:
        build_cmd.extend(['--target-architecture', args.target_arch])
        print(f"Building for target architecture: {args.target_arch}")

        # Special warning for ARM->x86_64 cross-compilation on macOS
        if system == 'darwin' and machine == 'arm64' and args.target_arch == 'x86_64':
            print("⚠️  WARNING: Cross-compiling from ARM to x86_64 on macOS may require Rosetta 2")
            print("   If you encounter issues, try installing PyInstaller under Rosetta")

        # Special warning for Windows cross-architecture builds
        if system == 'windows':
            if (machine == 'arm64' and args.target_arch == 'x86_64'):
                print("⚠️  WARNING: Building x86_64 executables on ARM Windows")
                print("   This may not produce compatible executables")
            elif (machine == 'x86_64' and args.target_arch == 'arm64'):
                print("⚠️  WARNING: Building ARM64 executables on x86_64 Windows")
                print("   This may not produce compatible executables")

    # Add spec file
    build_cmd.append('keithley.spec')

    # Run the build command
    print(f"Building for {system} ({machine})...")
    print(f"Running: {' '.join(build_cmd)}")

    try:
        subprocess.run(build_cmd, check=True)
        print("\nBuild completed successfully!")

        # Show output location
        if system == 'darwin':
            print("\nApplication bundle created at:")
            print(f"{project_root}/dist/KeithleyDualController.app")
        elif system == 'windows':
            print("\nExecutable created at:")
            print(f"{project_root}\\dist\\KeithleyDualController\\KeithleyDualController.exe")
        else:  # Linux
            print("\nExecutable created at:")
            print(f"{project_root}/dist/KeithleyDualController/KeithleyDualController")

        print("\nTo run the application:")
        if system == 'darwin':
            print("open dist/KeithleyDualController.app")
        elif system == 'windows':
            print(".\\dist\\KeithleyDualController\\KeithleyDualController.exe")
        else:  # Linux
            print("./dist/KeithleyDualController/KeithleyDualController")

    except subprocess.CalledProcessError as e:
        print(f"Build failed with error code {e.returncode}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
