#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './tests/run_all_tests.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Run all tests in sequence.
#
#   Run with: python tests/run_all_tests.py
#
#
#   Author(s): Lauren Linkous
#   Last update: August 16, 2025
##--------------------------------------------------------------------------------------------------\


import sys
import os

# Add the src directory to the path so we can import tsapython
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import our test modules
from test_basic import run_all_basic_tests
from test_hardware import run_all_hardware_tests


def run_all_tests():
    """Run all test suites."""
    print("Starting complete test suite...")
    print("More tests will be added as device inclusion gets smarter...")
    print("=" * 60)
    
    # Run basic tests first
    basic_success = run_all_basic_tests()
    print("\n" + "=" * 60)
    
    # Run hardware tests
    hardware_success = run_all_hardware_tests()
    print("\n" + "=" * 60)
    
    # Summary
    print("FINAL SUMMARY:")
    print(f"Basic tests: {'PASSED' if basic_success else 'FAILED'}")
    print(f"Hardware tests: {'PASSED' if hardware_success else 'SKIPPED/FAILED (no hardware? no serial connection?)'}")
    
    if basic_success:
        print("\nCore functionality is working!")
        if hardware_success:
            print("Hardware integration is working!")
        else:
            print("Hardware tests failed - check device connection")
        return True
    else:
        print("\nBasic functionality has issues")
        return False


if __name__ == "__main__":
    # this will run all tests when the file is executed directly. 
    # this call does not happen anywhere in the core library, so it needs to be deliberate

    success = run_all_tests()
    if not success:
        sys.exit(1)