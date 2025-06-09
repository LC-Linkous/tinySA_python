# import tinySA library
# (NOTE: check library path relative to script path)
from src.tinySA_python import tinySA 


# imports FOR THE EXAMPLE
import numpy as np
import matplotlib.pyplot as plt

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
# attempt to autoconnect
found_bool, connected_bool = tsa.autoconnect()

# if port closed, then return error message
if connected_bool == False:
    print("ERROR: could not connect to port")
else: # if port found and connected, then complete task(s) and disconnect
    # detailed messages turned on
    tsa.set_verbose(True) 
    # set scan values
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

    # plot
    plt.plot(freq_arr, data_arr)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Measured Data (dBm)")
    plt.title("tinySA Scan Plot")
    plt.show()
