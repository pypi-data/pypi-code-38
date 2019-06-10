'''
Implements a cross platform system for scanning and querying system resources.

########### VERSION HISTORY ###########

06/05/2019 - Andy Norrie	- First version

####################################
'''

import subprocess
import platform
import time
import os
import re
import sys
import ctypes
import driveTestConfig
import driveTestCore
from lspci import getPcieDeviceInfo, getPcieDeviceDetailedInfo

# to make input function back compatible with Python 2.x
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


'''
Base class to describe the hardware information interface
'''
class baseHostInformation:
    @staticmethod
    def hostInformationFactory():
        if platform.system() == 'Windows':
            return windowsHostInformation()
        else:
            raise NotImplementedError ("Only windows is supported right now")

    def _init_(self):
        pass

    def listPhysicalDrives (driveType, searchParams):
        pass

    def listLogicalDrives (drivePath, searchParams):
        pass

    def getDeviceStatus (physicalDriveId):
        pass

    def isAdminMode ():
        pass

class windowsHostInformation(baseHostInformation):
    def _init_(self):        
        pass

    '''
    Lists physical drives on the system, returning them in the form "{drive-type:identifier=drive description}"
    '''
    def listPhysicalDrives(self, driveType, searchParams = None):
        filterDrives = True

        # Get any additional parameters for the search
        if (searchParams is not None):           
            if ("filter_drives" in searchParams):
                filterDrives = searchParams["filter_drives"]

        # PCIE devices are returned with an identifier number as the PCIe slot ID
        if (driveType.lower() == "pcie"):
            userDevices = {}

            pcieScanData = getPcieDeviceInfo ()
            # Loop through PCIe results, pick only those matching the class code of a storage controller ([01xx]
            for pcieName, pcieDevice in pcieScanData.items():
                if ("[01" in pcieDevice["class"]):
                    # Add the device address and description to the dictionary
                    userDevices["pcie:" + pcieDevice["slot"]] = pcieDevice["vendor"] + ", " + pcieDevice["device"]

            return userDevices
           
        elif (driveType.lower() == "sas"):
            raise NotImplementedError ("sas drives are not supported yet")
    
    '''
    Returns a dictionary of status elements for the given device.
    '''    
    def getDeviceStatus(self, deviceId):
        
        # If a PCIe device
        if (deviceID.find ("pcie") == 0):
            # Get the status of the PCIe device and return it
            return getPcieDeviceDetailedInfo (devicesToScan = deviceId)
        else:
            raise NotImplementedError ("Only PCIE devices are currently supported")
    
    '''
    Check if we are running with admin permissions
    '''
    def isAdminMode(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
