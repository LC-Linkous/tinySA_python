# import tinySA library
# (NOTE: check library path relative to script path)
from src.tinySA_python import tinySA 

# create a new tinySA object    
tsa = tinySA()

# attempt to autoconnect
found_bool, connected_bool = tsa.autoconnect()

# if port found and connected, then complete task(s) and disconnect
if connected_bool == True: # or  if success == True:
    print("device connected")
    tsa.set_verbose(True) #detailed messages
    tsa.set_error_byte_return(True) #get explicit b'ERROR' if error thrown
    msg = tsa.get_device_id() 
    print(msg)
    

    tsa.disconnect()
else:
    print("ERROR: could not connect to port")