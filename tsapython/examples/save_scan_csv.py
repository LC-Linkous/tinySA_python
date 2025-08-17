#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/save_scan_csv.py'
#   A short example using matplotlib to plot requested SCAN data
#
#   Last update: August 17, 2025
##-------------------------------------------------------------------------------\


# import tinySA_python (tsapython) package
from tsapython import tinySA

# imports FOR THE EXAMPLE
import csv
import numpy as np

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
    
    data1 =bytearray(data.replace(b"-:.0", b"-10.0"))
    
    # get both values in each row returned (for reference)
    #data_arr = [list(map(float, line.split())) for line in data.decode('utf-8').split('\n') if line.strip()] 
   
    # get first value in each returned row
    data_arr = [float(line.split()[0]) for line in data1.decode('utf-8').split('\n') if line.strip()]

    return freq_arr, data_arr


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
    # set scan values
    start = int(1e9)  # 1 GHz
    stop = int(3e9)   # 3 GHz
    pts = 450         # sample points
    outmask = 2       # get measured data (y axis)

    # scan
    data_bytes = tsa.scan(start, stop, pts, outmask)

    print(data_bytes)

    tsa.resume() #resume so screen isn't still frozen

    tsa.disconnect()

    # processing after disconnect (just for this example)

    # convert data to 2 arrays
    freq_arr, data_arr = convert_data_to_arrays(start, stop, pts, data_bytes)


    # Save the data to CSV
    filename = "scan_sample.csv"
        
    # Write out to csv where column 1 is frequency and col 2 is data
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        
        # Write header row
        writer.writerow(['Frequency_Hz', 'Signal_Strength_dBm'])
        
        # Write data rows (frequency, signal strength pairs)
        for freq, signal in zip(freq_arr, data_arr):
            writer.writerow([f'{freq:.0f}', signal])
    
    print(f"Data saved to {filename}")
    print(f"CSV contains {len(freq_arr)} frequency/signal pairs")


    print(f"Data saved to {filename}")
