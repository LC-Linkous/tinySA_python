#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './tests/test_hardware.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Hardware tests for tsapython library. This REQUIRES a serial connected tinySA device
#
#   Run with: python tests/test_hardware.py
#
#
#   Author(s): Lauren Linkous
#   Last update: August 17, 2025
##--------------------------------------------------------------------------------------------------\


def test_device_connection():
    """Test basic device connection.
    Can we even detect/connect to a tinySA device via serial"""

    print("Testing device connection...")
    try:
        from tsapython import tinySA
        
        # create obj and set the prefered test configs
        tsa = tinySA()
        tsa.set_verbose(True)
        tsa.set_error_byte_return(True)
        
        found_bool, connected_bool = tsa.autoconnect()
        
        if connected_bool:
            print("PASS! Device connected successfully")
            tsa.disconnect()
            return True
        else:
            print("FAIL. Could not connect to device (this is OK if no hardware)")
            return False
            
    except Exception as e:
        print(f"FAIL. Connection test failed: {e}")
        return False


def test_device_info():
    """Test device information retrieval.
    All devices should be able to return a device ID if they are properly connected.
      This works will all models"""

    print("Testing device info retrieval...")
    try:
        from tsapython import tinySA
        
        # create obj and set the prefered test configs
        tsa = tinySA()
        tsa.set_verbose(True)
        tsa.set_error_byte_return(True)
        
        found_bool, connected_bool = tsa.autoconnect()
        
        if not connected_bool:
            print("FAIL. No device connected - skipping device info test")
            return False
        
        # Test device ID
        device_id = tsa.get_device_id()
        if device_id:
            print(f"PASS! Device ID: {device_id}")
        else:
            print("FAIL. Could not get device ID")
            tsa.disconnect()
            return False
        
        # Test device info
        info = tsa.info()
        if info:
            print(f"PASS! Device Info: {info}")
        else:
            print("FAIL. Could not get device info")
            tsa.disconnect()
            return False
        
        tsa.disconnect()
        print("PASS! Device info test passed")
        return True
        
    except Exception as e:
        print(f"FAIL. Device info test failed: {e}")
        return False


def test_data_collection():
    """Test basic data collection. Hop works pretty consistently for pulling data at intervals"""

    print("Testing data collection...")
    try:
        from tsapython import tinySA
        
        # create obj and set the prefered test configs
        tsa = tinySA()
        tsa.set_verbose(True)
        tsa.set_error_byte_return(True)
        
        found_bool, connected_bool = tsa.autoconnect()
        
        if not connected_bool:
            print("FAIL. No device connected - skipping data collection test")
            return False
        
        # Test parameters
        start_freq = 100e6  # 100 MHz
        stop_freq = 500e6   # 500 MHz
        n_pts = 12          # Just 11 points for quick test
        
        # Pause for consistent measurements
        tsa.pause()
        
        # Get frequency data
        freq_vals = tsa.hop(start_freq, stop_freq, n_pts, 1)
        if not freq_vals:
            print("FAIL. Could not collect frequency data")
            tsa.disconnect()
            return False
        
        # Get power data
        dbm_vals = tsa.hop(start_freq, stop_freq, n_pts, 2)
        if not dbm_vals:
            print("FAIL. Could not collect power data")
            tsa.disconnect()
            return False
        
        # Validate data
        freq_list = [float(x) for x in freq_vals.decode('utf-8').split()]
        power_list = [float(x) for x in dbm_vals.decode('utf-8').split()]

        print(power_list)
        
        if len(freq_list) != (n_pts+1) or len(power_list) != (n_pts+1):
            print(f"FAIL. Data length mismatch: got {len(freq_list)} freq, {len(power_list)} power, expected {n_pts}")
            tsa.disconnect()
            return False
        
        print(f"PASS! Collected {len(freq_list)} frequency points and {len(power_list)} power measurements.")
        print("NOTE: it's expected to return 1 MORE data point than requested due to the initial frequency point being included!")
        
        tsa.disconnect()
        return True
        
    except Exception as e:
        print(f"FAIL. Data collection test failed: {e}")
        return False


def run_all_hardware_tests():
    """Run all hardware tests and report results."""


    print("=" * 50)
    print("RUNNING HARDWARE TESTS (Requires Connected tinySA Device)")
    print("=" * 50)
    
    # call by function names in this file, NOT file names in the test directory
    tests = [
        test_device_connection,
        test_device_info,
        test_data_collection
    ]
    
    passed = 0
    total = len(tests)
    skipped = 0
    
    for test_func in tests:
        result = test_func()
        if result:
            passed += 1
        elif "skipping" in str(result):
            skipped += 1
        print("-" * 30)
    
    print(f"\nRESULTS: {passed}/{total} tests passed")
    if skipped > 0:
        print(f"Note: {skipped} tests were skipped (no hardware)")
    
    if passed > 0:
        print("Hardware tests completed!")
        return True
    else:
        print("ERROR: No hardware tests passed (check device connection)")
        return False


if __name__ == "__main__":
    # this will run hardware tests when the file is executed directly. 
    # this call does not happen anywhere in the core library, so it needs to be deliberate

    success = run_all_hardware_tests()

    # Don't exit with error if just no hardware. That's OK. 
    # It just means that the hardware was not detected
    # The library can still be operating fine if the test_basic.py tests are used to check