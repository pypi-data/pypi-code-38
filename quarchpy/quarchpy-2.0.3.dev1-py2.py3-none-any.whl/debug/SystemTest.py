from quarchpy import *
from quarchpy.device import *
import pkg_resources
from pkg_resources import parse_version, get_distribution
import os
import platform
import time
import sys

def main ():

    print("Quarchpy Version : " + pkg_resources.get_distribution("quarchpy").version)
    print("Python Version : " + sys.version)
    print("OS Name : " + os.name)
    print("Platform System : " + platform.system())
    print("Platform Release :  " + platform.release())
	
	# Scan for quarch devices on the system
    deviceList = scanDevices('all', favouriteOnly=True)
    moduleStr = userSelectDevice(deviceList)
    print("Selected module is: "+moduleStr)
    # Create a device using the module connection string
    myDevice = quarchDevice(moduleStr)
    QuarchSimpleIdentify(myDevice)

    # Close the module before exiting the script
    myDevice.closeConnection()


'''
This function demonstrates a very simple module identify, that will work with any Quarch device
'''
def QuarchSimpleIdentify(device1):
    # Print the module name
    print("Running the simple identify example.\n")
    print("Module Name:"),
    print(device1.sendCommand("hello?"))

    # Print the module identify and version information
    print("\nModule Identity Information:\n")
    print(device1.sendCommand("*idn?"))




if __name__ == "__main__":
    main()