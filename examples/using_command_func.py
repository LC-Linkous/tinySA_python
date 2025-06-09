# import tinySA library
# (NOTE: check library path relative to script path)
from src.tinySA_python import tinySA 


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
    start = 150e6   # 150 MHz
    stop = 200e6    # 200 MHz
    pts = 450       # for tinySA Ultra
    outmask = 1     # get measured data (y axis)
    # scan
    data_bytes = tsa.command("scan 150e6 200e6 5 2")

    print(data_bytes)

    tsa.resume() #resume 

    tsa.disconnect()

