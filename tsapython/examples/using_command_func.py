#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/using_command_func.py'
#   The command func can be used for commands or functionalities that exist on the
#   tinySA series of devices but arent included in the library yet. There is NO
#   built in error checking for this process.
#
#   Last update: August 17, 2025
##-------------------------------------------------------------------------------\


# import tinySA_python (tsapython) package
from tsapython import tinySA


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
    start = 150e6   # 150 MHz
    stop = 200e6    # 200 MHz
    pts = 450       # for tinySA Ultra
    outmask = 1     # get measured data (y axis)

    # scan
    # NOTE: raw command strings go to the device unchanged. The firmware reads
    # '150M' or '150000000', but NOT '150e6' (that is read as 150 Hz).
    data_bytes = tsa.command("scan 150M 200M 5 2")

    print(data_bytes)

    tsa.resume() #resume

    tsa.disconnect()

