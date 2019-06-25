'''
Implements basic control over lspci utilities, so that we can identify and check the
status of PCIe devices on the host

########### VERSION HISTORY ###########

25/04/2018 - Andy Norrie	- First version
13/06/2019 - Andy Norrie	- Updated to contain base layer lspci API only
                              Other functions are now at a higher level

####################################
'''

import subprocess
import platform
import time
import os
import re
import sys
import ctypes


'''
Get basic information on all PCIe devices on the system.  Returned as a dictionary of dictionaries
{nn:nn.n: {ELEMENT:DATA}}
This is a fast way to scan the bus and see what is there before possible interrogating devices in more detail (device status and similar)
'''
def getPcieDeviceList():
    pcieDevices = {}    
    lspciPath = os.path.join (os.getcwd(), "pciutils", "lspci.exe")

    # call lspci to get a list of all devices and basic details in parable form
    proc = subprocess.Popen([lspciPath, '-Mmmvvnn'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Execute the process
    out, err = proc.communicate()
    # Handle error output
    if (err):
        raise ValueError ("lspci error: " + err.decode('utf-8'))
    out = out.decode('utf-8')

    # Split the output into blocks of each device (paragraph)
    blocks = out.split ('\r\n\r\n')
    for desc in blocks:
        # Split block into each line
        newDevice = {}
        for line in iter (desc.splitlines()):
            pos = line.find(':')
            if (pos != -1):
                # Stop if we hit the end of the slot listings
                if ("Summary of buses" in line):
                    break

                # Add the dictionary item
                newDevice[line[:pos].lower()] = line[pos+1:].strip()   

        # Add the device descriptor as a sub dictionary of the main one
        if ("slot" in newDevice):
            pcieDevices[newDevice["slot"]] = newDevice
    
    # Return the list
    return pcieDevices
    
    
'''
Gets more detailed device information on one or more PCIe bus devices.  Each device info requires a seperate lcpci call
Optionally pass in the info dictionary from getPcieDeviceInfo() in order to fill in the additional details
devicesToScan is a CSV list of PCIe slot addresses.
'''
def getPcieDeviceDetailedInfo (deviceInfo = None, devicesToScan = "all"):

    # Setup the info structure, filling it if an 'all' selection is given but it is currently empty
    if (deviceInfo == None and devicesToScan == "all"):
        deviceInfo = getPcieDeviceInfo()
    elif (deviceInfo == None):
        deviceInfo = {}

    # Run the lspci command
    lspciPath = os.path.join (os.getcwd(), "pciutils", "lspci.exe")

    # call lspci to get detailed information on devices
    proc = subprocess.Popen([lspciPath, '-Mvvv'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Execute the process
    out, err = proc.communicate()
    # Handle error output
    if (err):
        raise ValueError ("lspci error: " + err.decode('utf-8'))
    out = out.decode('utf-8')

    # Split the output into blocks of each device (paragraph)
    blocks = out.split ('\r\n\r\n')
    for desc in blocks:
        lnkStatSpeed = None
        lnkStatWidth = None
        lnkCapsSpeed = None
        lnkCapsWidth = None

        # Get the slot path of the current device
        pos = desc.find (' ')
        currDevice = desc[:pos]

        # Parse each potential section, handle missing sections and continue
        try:            
            # Parse out link status
            strPos = desc.find ('LnkSta:')    
            statusText = desc[strPos:]
            matchObj = re.search ('Speed (.*?),', statusText)
            lnkStatSpeed = matchObj.group(0)
        except:
            pass
        try:
            matchObj = re.search ('Width (.*?),', statusText)
            lnkStatWidth = matchObj.group(0)
        except:
            pass
        try:
            # Parse out link capacity            
            strPos = desc.find ('LnkCap:')    
            statusText = desc[strPos:]
            matchObj = re.search ('Speed (.*?),', statusText)
            lnkCapsSpeed = matchObj.group(0)
        except:
            pass
        try:
            matchObj = re.search ('Width (.*?),', statusText)
            lnkCapsWidth = matchObj.group(0)
        except:
            pass

        # Limit the devices to return, as requested
        if (devicesToScan == "all" or currDevice in devicesToScan):
            # If the device information does not already exists, create the extra stub
            if (currDevice not in deviceInfo):                                  
                deviceInfo[currDevice] = {}

            # Fill in the additional details
            deviceInfo[currDevice]["link_status:speed"] = lnkStatSpeed
            deviceInfo[currDevice]["link_status:width"] = lnkStatWidth
            deviceInfo[currDevice]["link_capability:speed"] = lnkCapsSpeed
            deviceInfo[currDevice]["link_capability:width"] = lnkCapsWidth
            deviceInfo[currDevice]["present"] = "true"

    # Check for any requested devices, which we did not find.  These must be marked as not present (rather than skipped)
    if (devicesToScan != "all"):
        blocks = devicesToScan.split ('|')
        for currDevice in blocks:
            if currDevice not in deviceInfo:
                deviceInfo[currDevice]["present"] = "false"

    # return the updated info structure
    return deviceInfo