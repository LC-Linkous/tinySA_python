#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python
#   './examples/hello_world.py'
#   This is an example of how to use the current tinySA_python library. 
#   Note how this file is OUTSIDE the ./src folder, which contains the 
#   tinySA_python.py library file
#
#   Last update: June 22, 2025
##-------------------------------------------------------------------------------\

# import tinySA library
# (NOTE: check library path relative to script path)
from tinysa import tinySA

#import for EXAMPLE
import matplotlib.pyplot as plt

# create a new tinySA object    
tsa = tinySA()

# set the return message preferences 
tsa.set_verbose(True) #detailed messages
tsa.set_error_byte_return(True) #get explicit b'ERROR' if error thrown


# attempt to autoconnect
found_bool, connected_bool = tsa.autoconnect()

# if port found and connected, then complete task(s) and disconnect
if connected_bool == True: 
    print("device connected")

    # print the device ID
    msg = tsa.get_device_id() 
    print(msg)

    # get the device info    
    msg = tsa.info()
    print(msg)

    # collect some data!
    start_freq = 100e6  # 100 MHz
    stop_freq = 500e6   # 500 MHz
    n_pts = 101         # take 101 pts
    

    # pause the device so we can play with a single trace data
    tsa.pause()

    # Get the Frequency vals the measurements happen at
    outmask_select = 1  # 1 for step in hz, 2 for step in pts
    freq_vals = tsa.hop(start_freq, stop_freq, n_pts, outmask_select)
    print(freq_vals)


    # Get the dBm measurements for the freq
    outmask_select = 2  # 1 for step in hz, 2 for step in pts
    dbm_vals = tsa.hop(start_freq, stop_freq, n_pts, outmask_select)
    print(dbm_vals)

    # disconnect because we've taken the data and don't need the device anymore
    tsa.disconnect()
else:
    print("ERROR: could not connect to port")


# PLOTTING EXAMPLE (see FULL plotting examples in README for more details)

# python version of conversion, without data checking or sanatizing

x_val = [float(x) for x in freq_vals.decode('utf-8').split()]

y_val = [float(x) for x in dbm_vals.decode('utf-8').split()]

# plot
plt.plot(x_val, y_val)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Measured Data (dBm)")
plt.title("tinySA Hop() Plot")
plt.show()
