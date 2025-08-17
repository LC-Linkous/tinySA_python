#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './src/tests/test_basic.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Basic tests for tsapython. This requires NO hardware.
#   This test is to make sure the library was imported/setup correctly.
#
#   Run with: python tests/test_basic.py
#
#
#   Author(s): Lauren Linkous
#   Last update: August 16, 2025
##--------------------------------------------------------------------------------------------------\



def test_import():
    """Test that the package can be imported properly."""
    print("Testing package import...")
    try:
        from tsapython import tinySA
        print("PASS! Package imported successfully")
        return True
    except ImportError as e:
        print(f"FAIL. Import failed: {e}")
        return False


def test_create_instance():
    """Test that we can create a local tinySA instance (pulled from core.py, class renamed for getting CORE device functionality)."""
    print("Testing instance creation...")
    try:
        from tsapython import tinySA
        tsa = tinySA()
        print("PASS! Instance created successfully")
        return True
    except Exception as e:
        print(f"Fail. Instance creation failed: {e}")
        return False


def test_method_existence():
    """Test that required methods exist. 
    This is using a selction of methods that are not specific to a single tinySA device. 
    BASIC functionlity"""

    print("Testing basic methods exists...")
    try:
        from tsapython import tinySA
        tsa = tinySA()
        
        required_methods = [
            'autoconnect', 'disconnect', 
            'get_device_id', 'info', 
            'set_verbose', 'set_error_byte_return',
            'pause', 
            'hop'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(tsa, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"ERROR!! Missing methods: {missing_methods}")
            return False
        else:
            print("PASS! All required methods exist")
            return True
            
    except Exception as e:
        print(f"FAIL. Method check failed: {e}")
        return False


def test_verbose_setting():
    """Test verbose mode setting. 
    This is an optional setting, but a highly recommended one.
    It's also one of the easiest function to set because it's
    related to the library and not the device"""

    print("Testing verbose mode setting...")
    try:
        from tsapython import tinySA
        tsa = tinySA()
        
        # These should not raise exceptions
        tsa.set_verbose(True)
        tsa.set_verbose(False)
        
        print("PASS! Verbose mode setting works")
        return True
    except Exception as e:
        print(f"Fail. Verbose mode setting failed: {e}")
        return False


def test_error_byte_return():
    """Test error byte return setting.
    Setting controlls if ERROR message, or default device message, is returned.
    Used to mark an explicit ERROR in the return"""

    print("Testing error byte return setting...")
    try:
        from tsapython import tinySA
        tsa = tinySA()
        
        # These should not raise exceptions
        tsa.set_error_byte_return(True)
        tsa.set_error_byte_return(False)
        
        print("PASS! Error byte return setting works")
        return True
    except Exception as e:
        print(f"FAIL. Error byte return setting failed: {e}")
        return False


def run_all_basic_tests():
    """Run all basic tests and report results."""

    print("=" * 50)
    print("RUNNING BASIC TESTS (No Hardware Required)")
    print("=" * 50)
    
    # call by function names in this file, NOT file names in the test directory
    tests = [
        test_import,
        test_create_instance,
        test_method_existence,
        test_verbose_setting,
        test_error_byte_return
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        result = test_func()
        if result:
            passed += 1
        print("-" * 30)
    
    print(f"\nRESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("All basic tests passed!")
        return True
    else:
        print(f"ERROR:  {total - passed} tests failed")
        return False


if __name__ == "__main__":
    # this will run basic tests when the file is executed directly. 
    # this call does not happen anywhere in the core library, so it needs to be deliberate

    success = run_all_basic_tests()
    if not success:
        exit(1)  # Exit with error code if tests failed