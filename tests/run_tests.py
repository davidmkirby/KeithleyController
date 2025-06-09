#!/usr/bin/env python3
# run_tests.py - Test runner for Keithley Dual Controller
"""
Test runner for Keithley Dual Controller
Runs all tests with proper setup and teardown
"""

import os
import sys
import unittest
import argparse
import time

def setup_environment():
    """Setup test environment"""
    print("Setting up test environment...")
    # Ensure we're in the project directory
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_dir)
    sys.path.insert(0, project_dir)

    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

def run_basic_tests():
    """Run basic tests"""
    print("\n" + "=" * 70)
    print("Running basic tests...")
    print("=" * 70)
    from tests import test_basic
    return test_basic.run_all_tests()

def run_simple_tests():
    """Run simple tests"""
    print("\n" + "=" * 70)
    print("Running simple tests...")
    print("=" * 70)
    from tests import test_simple
    return test_simple.run_all_tests()

def run_comprehensive_tests():
    """Run comprehensive tests"""
    print("\n" + "=" * 70)
    print("Running comprehensive tests...")
    print("=" * 70)
    from tests import test_comprehensive
    return test_comprehensive.run_all_tests()

def run_logger_tests():
    """Run logger-specific tests"""
    print("\n" + "=" * 70)
    print("Running logger tests...")
    print("=" * 70)
    try:
        # Need to run logger tests in a separate process to avoid mock logger interference
        import subprocess
        result = subprocess.run(["python", "tests/test_logger.py"], capture_output=False)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running logger tests: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all test suites"""
    basic_result = run_basic_tests()
    time.sleep(1)  # Small delay between test suites

    simple_result = run_simple_tests()
    time.sleep(1)  # Small delay between test suites

    comprehensive_result = run_comprehensive_tests()
    time.sleep(1)  # Small delay between test suites

    logger_result = run_logger_tests()

    # Print overall summary
    print("\n" + "=" * 70)
    print("OVERALL TEST RESULTS")
    print("=" * 70)
    print(f"Basic tests: {'PASSED' if basic_result else 'FAILED'}")
    print(f"Simple tests: {'PASSED' if simple_result else 'FAILED'}")
    print(f"Comprehensive tests: {'PASSED' if comprehensive_result else 'FAILED'}")
    print(f"Logger tests: {'PASSED' if logger_result else 'FAILED'}")

    overall_result = basic_result and simple_result and comprehensive_result and logger_result
    print(f"\nOverall test status: {'PASSED' if overall_result else 'FAILED'}")

    return overall_result

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Keithley Dual Controller Test Runner")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--basic", action="store_true", help="Run basic tests")
    parser.add_argument("--simple", action="store_true", help="Run simple tests")
    parser.add_argument("--comprehensive", action="store_true", help="Run comprehensive tests")
    parser.add_argument("--logger", action="store_true", help="Run logger tests")
    return parser.parse_args()

if __name__ == "__main__":
    setup_environment()

    args = parse_args()

    # If no specific tests were requested, run all tests
    if not (args.all or args.basic or args.simple or args.comprehensive or args.logger):
        args.all = True

    # Run requested tests
    if args.all:
        success = run_all_tests()
    else:
        success = True
        if args.basic:
            success = run_basic_tests() and success
        if args.simple:
            success = run_simple_tests() and success
        if args.comprehensive:
            success = run_comprehensive_tests() and success
        if args.logger:
            success = run_logger_tests() and success

    # Exit with appropriate code
    sys.exit(0 if success else 1)
