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
        print("✅ PyQt6 imported successfully")
    except ImportError as e:
        print(f"❌ PyQt6 import failed: {e}")
        return False

    try:
        import pyvisa
        print("✅ PyVISA imported successfully")
    except ImportError as e:
        print(f"❌ PyVISA import failed: {e}")
        return False

    try:
        import pyqtgraph
        print("✅ PyQtGraph imported successfully")
    except ImportError as e:
        print(f"❌ PyQtGraph import failed: {e}")
        return False

    try:
        import numpy
        print("✅ NumPy imported successfully")
    except ImportError as e:
        print(f"❌ NumPy import failed: {e}")
        return False

    return True

def test_visa_resources():
    """Test VISA resource manager initialization"""
    print("\nTesting VISA...")

    try:
        import pyvisa
        rm = pyvisa.ResourceManager()
        resources = rm.list_resources()
        print(f"✅ VISA ResourceManager created successfully")
        print(f"📡 Available resources: {len(resources)}")
        for resource in resources:
            print(f"   - {resource}")
        return True
    except Exception as e:
        print(f"❌ VISA test failed: {e}")
        print("💡 Make sure NI-VISA is installed")
        return False

def test_application_creation():
    """Test that the application components can be created"""
    print("\nTesting application components...")

    try:
        from PyQt6.QtWidgets import QApplication

        # Create QApplication
        app = QApplication([])
        print("✅ QApplication created successfully")

        # Test importing our modules
        try:
            from src.core.instrument_control import InstrumentController
            controller = InstrumentController()
            print("✅ InstrumentController created successfully")
        except Exception as e:
            print(f"❌ InstrumentController creation failed: {e}")
            return False

        try:
            from src.main_window import KeithleyDualController
            # Don't actually show the window in test
            print("✅ KeithleyDualController class imported successfully")
        except Exception as e:
            print(f"❌ KeithleyDualController import failed: {e}")
            return False

        app.quit()
        return True

    except Exception as e:
        print(f"❌ Application test failed: {e}")
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
            print(f"✅ {filename} found")
        else:
            print(f"❌ {filename} missing")
            missing_files.append(filename)

    if missing_files:
        print(f"\n⚠️  Missing files: {missing_files}")
        print("💡 Make sure all Python files are in the correct src subdirectories")
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
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{len(results)}")

    if passed == len(results):
        print("\n🎉 All tests passed! The application should run correctly.")
        print("💡 Try running: python src/main.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")

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
        print(f"\n🧪 Running {test_name} test...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)

    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1

    print(f"\nTests passed: {passed}/{len(results)}")

    success = passed == len(results)
    if success:
        print("\n🎉 All tests passed! The application should run correctly.")
        print("💡 Try running: python src/main.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
        print("💡 Make sure all dependencies are installed: pip install -r requirements.txt")

    return success