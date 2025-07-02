#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python
#   './examples/plotting_scanraw.py'
#   This is a visual comparison of SCAN and SCANRAW to work out some errors in 
#   the decode process. We don't expect SCAN and SCANRAW to be exactly the same, 
#   because the number of points taken are not the same, but they 
#   should be relatively similar values when SCANRAW is decoded
#
#   Last update: July 2, 2025
##-------------------------------------------------------------------------------\


# import tinySA library
# (NOTE: check library path relative to script path)
from src.tinySA_python import tinySA 

# imports FOR THE EXAMPLE
import numpy as np
import matplotlib.pyplot as plt
import struct

def convert_data_to_arrays(start, stop, pts, data):
    # FOR PLOTTING
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

    # NOTE: if repeated read errors with utf-8 occur, uncomment the below as an alternative to the
    # line above. This will show you what value is being returned that caused the problem. It may
    # indicate a different problem with the serial connection permissions

    # data_arr = []
    # for i, line in enumerate(data1.decode('utf-8').split('\n')):
    #     print(f"Line {i}: '{line}'")  # Show the raw line
    #     line = line.strip()
    #     if line:
    #         try:
    #             value = float(line.split()[0])
    #             data_arr.append(value)
    #             # print(f"  Parsed float: {value}")
    #         except ValueError as e:
    #             print(f"  Could not convert line to float: {line} — Error: {e}")

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
    start = int(150e6)   # 150 MHz
    stop = int(500e6)    # 500 MHz
    pts = 450            # for tinySA Ultra
    outmask = 2     # get measured data (y axis)
    # scan raw call - reads until end of stream
    # this CAN be run in a loop. the limiting factor is time to plot. 

    # SCAN
    scan_data_bytes = tsa.scan(start, stop, pts, outmask)

    # SCAN RAW
    scanraw_data_bytes = tsa.scan_raw(start, stop, pts, outmask)

    # for subsequent reads, the tinySA does freeze while preforming SCANRAW
    # if there's an error, the screen will stay frozen (for reading).
    # So start it again so new data can be taken
    tsa.resume()

    # disconnect because we don't need the tinySA to process data
    tsa.disconnect()

    # process the SCAN data (this is already in dBm)
    # convert data to 2 arrays for X and Y
    freq_arr, data_arr = convert_data_to_arrays(start, stop, pts, scan_data_bytes)

    # PROCESS SCANRAW into an array & reuse the FREQ_ARR value
    # remove the intro curly brace ({) 
    bin_scanraw = scanraw_data_bytes[1:] #skip the first char because it's the raminaing curly brace
    # use struct.unpack() because of the repeating pattern
        # <: indicates little-endian byte order, meaning the least significant byte is stored first
        # 'xH'*pts: a repetition of the format 'xH' once per point.
        # 'x': represents a pad byte, which is ignored
        # 'H': represents an unsigned short integer (2 bytes)
    
    expected_len = 3 * pts
    actual_len = len(bin_scanraw)
    print(f"Expected length: {expected_len}, Actual length: {actual_len}")
    
    if actual_len == expected_len:
        # SCANRAW has returned the expected amount of data for the read. 
        # sometimes this function (and not SCAN) does not read the buffer properly
        # a fix is in progress for LINUX systems. it works fine for Windows
        processed_scanraw = struct.unpack( '<' + 'xH'*pts, bin_scanraw ) # ignore trailing '}ch> '
        processed_scanraw = np.array(processed_scanraw, dtype=np.uint16 ).reshape(-1, 1) #unit8 has overflow error

        # CONVERT to dBm Power
        # take the processed binary data and convert it to dBm. 
        # The equation is from tinySA.org & official documentation
        SCALE_FACTOR = 174  # tinySA Basic: 128, tinySA Ultra and newer is 174
        dBm_data = processed_scanraw / 32 - SCALE_FACTOR
        print(dBm_data)

        # plot
        plt.plot(freq_arr, data_arr, label= 'SCAN data')
        plt.plot(freq_arr, dBm_data, label= 'SCANRAW data')
        plt.xlabel("frequency (hz)")
        plt.ylabel("measured data (dBm)")
        plt.title("tinySA SCAN and SCANRAW data")
        plt.legend()
        plt.show()
    else:
        print("SCANRAW did not return the expected amount of data for the read")
