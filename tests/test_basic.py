# test_basic.py - Basic functionality tests
"""
Basic tests to verify the application can start and components load correctly.
Run this to check if all imports work and the UI can be created.
"""

import sys
import traceback

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")

    try:
        import PyQt6
        print("[SUCCESS] PyQt6 imported successfully")
    except ImportError as e:
        print(f"[ERROR] PyQt6 import failed: {e}")
        return False

    try:
        import pyvisa
        print("[SUCCESS] PyVISA imported successfully")
    except ImportError as e:
        print(f"[ERROR] PyVISA import failed: {e}")
        return False

    try:
        import pyqtgraph
        print("[SUCCESS] PyQtGraph imported successfully")
    except ImportError as e:
        print(f"[ERROR] PyQtGraph import failed: {e}")
        return False

    try:
        import numpy
        print("[SUCCESS] NumPy imported successfully")
    except ImportError as e:
        print(f"[ERROR] NumPy import failed: {e}")
        return False

    return True

def test_visa_resources():
    """Test VISA resource manager initialization"""
    print("\nTesting VISA...")

    try:
        import pyvisa
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        print(f"[SUCCESS] VISA ResourceManager created successfully")
        print(f"Available resources: {len(resources)}")
        for resource in resources:
            print(f"   - {resource}")
        return True
    except Exception as e:
        print(f"[ERROR] VISA test failed: {e}")
        print("NOTE: Make sure NI-VISA is installed")
        return False

def test_application_creation():
    """Test that the application components can be created"""
    print("\nTesting application components...")

    try:
        from PyQt6.QtWidgets import QApplication

        # Create QApplication
        app = QApplication([])
        print("[SUCCESS] QApplication created successfully")

        # Test importing our modules
        try:
            from src.core.instrument_control import InstrumentController
            controller = InstrumentController()
            print("[SUCCESS] InstrumentController created successfully")
        except Exception as e:
            print(f"[ERROR] InstrumentController creation failed: {e}")
            return False

        try:
            from src.main_window import KeithleyDualController
            # Don't actually show the window in test
            print("[SUCCESS] KeithleyDualController class imported successfully")
        except Exception as e:
            print(f"[ERROR] KeithleyDualController import failed: {e}")
            return False

        app.quit()
        return True

    except Exception as e:
        print(f"[ERROR] Application test failed: {e}")
        traceback.print_exc()
        return False

def test_file_structure():
    """Test that all required files are present"""
    print("\nTesting file structure...")

    required_files = [
        'src/main.py',
        'src/main_window.py',
        'src/core/instrument_control.py',
        'src/ui/control_tab.py',
        'src/ui/plotting_tab.py',
        'src/ui/settings_tab.py',
        'src/ui/log_tab.py'
    ]

    import os
    missing_files = []
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Get project root

    for filename in required_files:
        # Check existence from project root
        if os.path.exists(os.path.join(project_root, filename)):
            print(f"[SUCCESS] {filename} found")
        else:
            print(f"[ERROR] {filename} missing")
            missing_files.append(filename)

    if missing_files:
        print(f"\n[WARNING] Missing files: {missing_files}")
        print("NOTE: Make sure all Python files are in the correct src subdirectories")
        return False

    return True

def main():
    """Run all basic tests"""
    print("=" * 60)
    print("Keithley Dual Controller - Basic Functionality Test")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("VISA Resources", test_visa_resources),
        ("Application Creation", test_application_creation)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"FAIL: {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{len(results)}")

    if passed == len(results):
        print("\nAll tests passed! The application should run correctly.")
        print("Try running: python src/main.py")
    else:
        print("\nSome tests failed. Check the output above for details.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()

def run_all_tests():
    """Run all basic tests for integration with run_tests.py"""
    print("=" * 60)
    print("Keithley Dual Controller - Basic Functionality Test")
    print("=" * 60)

    tests = [
        ("File Structure", test_file_structure),
        ("Module Imports", test_imports),
        ("VISA Resources", test_visa_resources),
        ("Application Creation", test_application_creation)
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\nRunning {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"FAIL: {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{len(results)}")

    success = passed == len(results)
    if success:
        print("\nAll tests passed! The application should run correctly.")
        print("Try running: python src/main.py")
    else:
        print("\nSome tests failed. Check the output above for details.")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")

    return success