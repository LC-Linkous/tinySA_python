# This is a quick example of how to ID serial ports manually if you're running
# into issues with autoconnect or connecting in general.
# This is not a streamlined process, 
# it's meant to demonstrate to new users what this process looks like


# import serial tools to identify the ports
import serial.tools.list_ports


# List all available serial ports
ports = serial.tools.list_ports.comports()

# print all found ports
print("found ports")
print(ports)

# loop through the ports and print out info
for port_info in ports:

    # print out which port we're trying
    port = port_info.device 
    print(f"Trying port: {port}")

    # both the tinySA and nanoVNA have 0x0483/0x5740 as their VID/PID
    # so we're going to search for that. the VID and PID values might be
    # in decimal form instead of hex.
    
    print("VID direct call:")
    vid = port_info.vid
    print(vid) # returns 1155 for tinySA, which is in decimal!
    
    if vid == None:
        pass # cannot convert None to hex
    else:
        print("converted VID direct to hex:")
        vid_hex = hex(port_info.vid)
        print(vid_hex) # if 1155 is returned, this matches the hex value 0x0483!
    
    print("PID direct call:")
    pid = port_info.pid
    print(pid)
    
    print("HWID call:")
    hwid = port_info.hwid
    print(hwid) # this gives a more detailed return: 
                # USB VID:PID=0483:5740 SER=400 LOCATION=1-2
                # or:
                # a completely different string with NO VID or PID.
                # So error checking & parsing needed to pull VID and PID
    
    print("get port name: ")
    name = port_info.name
    print(name) # this will usually be the same as the port_info.device



    # check if it's a tinySA or nanoVNA:
    if (vid==None):
        pass 
    elif (hex(vid) == '0x483') and (hex(pid)=='0x5740'):
        print("#########################################")
        print("tinySA device found!")
        print("COM:" + str(port))
        print("#########################################")
        break
    




