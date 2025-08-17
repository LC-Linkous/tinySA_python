#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './tests/test_example_workflow.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Full workflow test. This was originally "hello_world.py" in the examples, but has been modified
#   to include feedback in a 'test' format. This is a more realistic format than the tests.
#   HARDWARE IS REQUIRED
#
#   Run with: python tests/test_example_workflow.py
#
#
#   Author(s): Lauren Linkous
#   Last update: August 17, 2025
##--------------------------------------------------------------------------------------------------\


import matplotlib.pyplot as plt


def run_complete_example():
    """Run the complete tinySA example workflow."""


    print("=" * 50)
    print("RUNNING COMPLETE EXAMPLE WORKFLOW")
    print("=" * 50)
    
    try:
        from tsapython import tinySA
        
        # Create a new tinySA object    
        tsa = tinySA()
        
        # Set the return message preferences
        tsa.set_verbose(True)  # detailed messages
        tsa.set_error_byte_return(True)  # get explicit b'ERROR' if error thrown
        
        # Attempt to autoconnect
        print("Attempting to connect to device...")
        found_bool, connected_bool = tsa.autoconnect()
        
        # If port found and connected, then complete task(s) and disconnect
        if connected_bool:
            print("PASS! Device connected")
            
            # Print the device ID
            msg = tsa.get_device_id()
            print(f"Device ID: {msg}")
            
            # Get the device info    
            msg = tsa.info()
            print(f"Device Info: {msg}")
            
            # Collect some data!
            start_freq = 100e6  # 100 MHz
            stop_freq = 500e6   # 500 MHz
            n_pts = 101         # take 101 pts
           
            print(f"Collecting data from {start_freq/1e6:.1f} MHz to {stop_freq/1e6:.1f} MHz ({n_pts} points)...")
            
            # Pause the device so we can play with a single trace data
            tsa.pause()
            
            # Get the Frequency vals the measurements happen at
            outmask_select = 1  # 1 for step in hz, 2 for step in pts
            freq_vals = tsa.hop(start_freq, stop_freq, n_pts, outmask_select)
            print(f"PASS! Frequency data collected: {len(freq_vals.decode('utf-8').split())} points")
            
            # Get the dBm measurements for the freq
            outmask_select = 2  # 1 for step in hz, 2 for step in pts
            dbm_vals = tsa.hop(start_freq, stop_freq, n_pts, outmask_select)
            print(f"PASS! Power data collected: {len(dbm_vals.decode('utf-8').split())} points")
            
            # Disconnect because we've taken the data and don't need the device anymore
            tsa.disconnect()
            print("PASS! Device disconnected")
            
            # PLOTTING EXAMPLE
            print("Creating plot...")
            try:
                # Python version of conversion, without data checking or sanitizing
                x_val = [float(x) for x in freq_vals.decode('utf-8').split()]
                y_val = [float(x) for x in dbm_vals.decode('utf-8').split()]
                
                # Create plot
                plt.figure(figsize=(12, 8))
                plt.plot(x_val, y_val, 'b-', linewidth=1.5, alpha=0.8)
                plt.xlabel("Frequency (Hz)", fontsize=12)
                plt.ylabel("Measured Data (dBm)", fontsize=12)
                plt.title("tinySA Hop() Plot - Complete Example", fontsize=14, fontweight='bold')
                plt.grid(True, alpha=0.3)
                
                # Format x-axis to show frequencies in a readable format
                plt.ticklabel_format(style='scientific', axis='x', scilimits=(0,0))
                
                # Save the plot
                plot_filename = "example_sweep_plot.png"
                plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
                print(f"PASS! Plot saved as: {plot_filename}")
                
                # Show the plot
                plt.show()
                
                print("DONE! Complete example workflow finished successfully!")
                return True
                
            except Exception as plot_error:
                print(f"ERROR: Plotting failed: {plot_error}")
                return False
                
        else:
            print("ERROR: could not connect to port")
            print("Make sure your tinySA device is connected and try again.")
            return False
            
    except Exception as e:
        print(f"ERROR: Example workflow failed: {e}")
        return False


if __name__ == "__main__":
    # this will run hardware tests when the file is executed directly. 
    # this call does not happen anywhere in the core library, so it needs to be deliberate

    # Hardware MUST be connected


    success = run_complete_example()
    if success:
        print("\nExample completed successfully!")
    else:
        print("\nWARNING: Example had issues - check device connection")