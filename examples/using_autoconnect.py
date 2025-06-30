#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python
#   './examples/using_autoconnect.py'
#   This is an example of using the autoconnect feature. 
#   The detected device ID is returned and the serial disconnected
#
#   Last update: June 18, 2025
##-------------------------------------------------------------------------------\

# import tinySA library
# (NOTE: check library path relative to script path)
from src.tinySA_python import tinySA 

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

    msg = tsa.get_device_id() 
    print(msg)
    

    tsa.disconnect()
else:
    print("ERROR: could not connect to port")