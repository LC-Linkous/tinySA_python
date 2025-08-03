#! /usr/bin/python3
##-------------------------------------------------------------------------------\
#   tinySA_python
#   './examples/plotting_waterfall_1.py'
#   A waterfall plot example using matplotlib to plot multiple SCAN data over time
#
#   Last update: June 22, 2025
##-------------------------------------------------------------------------------\
# import tinySA library
# (NOTE: check library path relative to script path)
from tinysa import tinySA

# imports FOR THE EXAMPLE
import csv
import numpy as np
import matplotlib.pyplot as plt
import time
from datetime import datetime

def convert_data_to_arrays(start, stop, pts, data):
    # using the start and stop frequencies, and the number of points,
    freq_arr = np.linspace(start, stop, pts) # note that the decimals might go out to many places.
                                                # you can truncate this because its only used
                                                # for plotting in this example
    # As of the Jan. 2024 build in some data returned with SWEEP or SCAN calls there is error data.  
    # https://groups.io/g/tinysa/topic/tinasa_ultra_sweep_command/104194367  
    # this shows up as "-:.000000e+01".
    # TEMP fix - replace the colon character with a -10. This puts the 'filled in' points around the noise floor.
    # more advanced filtering should be applied for actual analysis.
   
    data1 = bytearray(data.replace(b"-:.0", b"-10.0"))
   
    # get both values in each row returned (for reference)
    #data_arr = [list(map(float, line.split())) for line in data.decode('utf-8').split('\n') if line.strip()]
   
    # get first value in each returned row
    data_arr = [float(line.split()[0]) for line in data1.decode('utf-8').split('\n') if line.strip()]
    return freq_arr, data_arr

def collect_waterfall_data(tsa, start, stop, pts, outmask, num_scans, scan_interval):

    waterfall_data = []  # 2D array of scan data (time x frequency)
    timestamps = []
    freq_arr = None
    
    print(f"Collecting {num_scans} scans with {scan_interval}s intervals...")
    
    for i in range(num_scans):
        print(f"Scan {i+1}/{num_scans}")
        
        # Perform scan
        data_bytes = tsa.scan(start, stop, pts, outmask)
        
        # Convert to arrays
        if freq_arr is None:
            freq_arr, data_arr = convert_data_to_arrays(start, stop, pts, data_bytes)
        else:
            _, data_arr = convert_data_to_arrays(start, stop, pts, data_bytes)
        
        # Store data and timestamp
        waterfall_data.append(data_arr)
        timestamps.append(datetime.now())
        
        # Wait before next scan (except for last scan)
        if i < num_scans - 1:
            time.sleep(scan_interval)
    
    return freq_arr, np.array(waterfall_data), timestamps

def plot_waterfall(freq_arr, waterfall_data, timestamps, start, stop):
    # Create figure with subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Waterfall plot (main plot)
    # Create time array for y-axis (scan number or elapsed time)
    time_arr = np.arange(len(timestamps))
    
    # Create meshgrid for pcolormesh
    freq_mesh, time_mesh = np.meshgrid(freq_arr, time_arr)
    
    # Plot waterfall
    im = ax1.pcolormesh(freq_mesh/1e9, time_mesh, waterfall_data, 
                       shading='nearest', cmap='viridis')
    
    ax1.set_xlabel('Frequency (GHz)')
    ax1.set_ylabel('Scan Number')
    ax1.set_title(f'Waterfall Plot: {start/1e9:.1f} - {stop/1e9:.1f} GHz')
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax1)
    cbar.set_label('Signal Strength (dBm)')
    
    # Latest scan plot (bottom subplot)
    ax2.plot(freq_arr/1e9, waterfall_data[-1])
    ax2.set_xlabel('Frequency (GHz)')
    ax2.set_ylabel('Signal Strength (dBm)')
    ax2.set_title('Latest Scan')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig

# create a new tinySA object    
tsa = tinySA()
# set the return message preferences
tsa.set_verbose(True) #detailed messages
tsa.set_error_byte_return(True) #get explicit b'ERROR' if error thrown

# attempt to autoconnect
found_bool, connected_bool = tsa.autoconnect()

# if port closed, then return error message
if connected_bool == False:
    print("ERROR: could not connect to port")
else: # if port found and connected, then complete task(s) and disconnect
    try:
        # set scan values
        start = int(1e9)  # 1 GHz
        stop = int(3e9)   # 3 GHz
        pts = 450         # sample points
        outmask = 2       # get measured data (y axis)
        
        # waterfall parameters
        num_scans = 50        # number of scans to collect
        scan_interval = 0.5   # seconds between scans
        
        # collect waterfall data
        freq_arr, waterfall_data, timestamps = collect_waterfall_data(
            tsa, start, stop, pts, outmask, num_scans, scan_interval)
        
        print("Data collection complete!")
        
        # resume and disconnect
        tsa.resume() #resume so screen isn't still frozen
        tsa.disconnect()
        
        # processing after disconnect
        print("Creating waterfall plot...")
        
        # create waterfall plot
        fig = plot_waterfall(freq_arr, waterfall_data, timestamps, start, stop)
        
        # Save data out to .csv
        filename = "waterfall_1_sample.csv"
            
        # Create CSV with frequency headers and time/scan data
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header row with frequencies (in Hz)
            header = ['Scan_Number', 'Timestamp'] + [f'{freq:.0f}' for freq in freq_arr]
            writer.writerow(header)
            
            # Write data rows
            for i, (scan_data, timestamp) in enumerate(zip(waterfall_data, timestamps)):
                row = [i+1, timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]] + scan_data.tolist()
                writer.writerow(row)
            
        print(f"Data saved to {filename}")
        print(f"CSV contains {len(waterfall_data)} scans with {len(freq_arr)} frequency points each")
        
        # show plot
        plt.show()

    except KeyboardInterrupt:
        print("\nScan interrupted by user")
        tsa.resume()
        tsa.disconnect()
    except Exception as e:
        print(f"Error occurred: {e}")
        tsa.resume()
        tsa.disconnect()