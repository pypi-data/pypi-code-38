'''
Implements basic control over lspci utilities, so that we can identify and check the
status of PCIe devices on the host

########### VERSION HISTORY ###########

25/04/2018 - Andy Norrie	- First version

####################################
'''

import subprocess
import platform
import time
import os
import re
import sys
import ctypes
from quarchpy.disk_test import driveTestConfig
#import quarchpy.disk_test.driveTestCore as driveTestCore
import driveTestCore

# to make input function back compatible with Python 2.x
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


# Internal test results created during teses.  Used to hold temporary data
internalResults = {}



'''
Store the initial state of a drive in the internalResults storage, for later use

driveId=Name of drive
linkSpeed=PCIe link speed string
linkWidth=PCIe link width string
'''
def storeInitialDriveStats (driveId, linkSpeed, linkWidth):
    internalResults[driveId + "_linkSpeed"] = linkSpeed
    internalResults[driveId + "_linkWidth"] = linkWidth

'''
Verifies that the PCIe link stats are the same now as they were at the start of the test

driveId=ID string of the drive to test
'''
def verifyDriveStats (uniqueID, driveId, mappingMode):
    # Get the expected stats
    expectedSpeed = internalResults[driveId + "_linkSpeed"]
    expectedWidth = internalResults[driveId + "_linkWidth"]

    # Get the current stats
    linkSpeed, linkWidth = getPcieLinkStatus (driveId, mappingMode)

    # if the speed and width is the same
    if (linkSpeed == expectedSpeed and linkWidth ==  expectedWidth):
        # Log a test success
        driveTestConfig.testCallbacks["TEST_LOG"] (uniqueID, time.time(), "testResult", "Drive link speed/width was maintained " + driveId, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True})
        return True;
    # Else log a test failure
    else:
        changeDetails = "Was: " + expectedSpeed + "/" + expectedWidth + " Now: " + linkSpeed + "/" + linkWidth
        driveTestConfig.testCallbacks["TEST_LOG"] (uniqueID, time.time(), "testResult", "Drive link speed/width was NOT maintained for: " + driveId, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False, "textDetails":changeDetails})
        return False


'''
Lists all PCIe devices on the bus

mappingMode=True to allow lspci mapping mode to scan beyond switches
filterDrives=True to try and filter out 'non drives' (switches and similar)
'''
def getPcieDevices(mappingMode, filterDrives=False):
    pcieDevices = []
    # lspciPath = os.path.join (os.getcwd(), "pciutils", "lspci.exe")  no longer works for QPY
    lspciPath =  os.path.dirname(os.path.realpath(__file__)) + "\\pciutils\\lspci.exe"

    # Choose mapping mode to use
    if mappingMode == True:
        proc = subprocess.Popen([lspciPath, '-M'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen([lspciPath], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Execute the process
    out, err = proc.communicate()
    # Handle error output
    if (err):
        print ("ERROR: " + err.decode('utf-8'))
    out = out.decode('utf-8')

    # Add valid device lines to the list
    for pciStr in iter(out.splitlines ()):
        matchObj = re.match ('[0-9a-fA-F]+:[0-9a-fA-F]+.[0-9a-fA-F]', pciStr)
        try:
            matchStr = matchObj.group(0)
        except:
            matchStr = ""
        if (len(matchStr) > 0):
            if pciStr.find ('##') == -1:
                if (filterDrives==False):
                    pcieDevices.append (pciStr)
                else:
                    # TODO: check if this looks like a non-storage item and skip
                    pcieDevices.append (pciStr)
    # Return the list
    return pcieDevices

'''
Checks if the specified device exists in the list
'''
def devicePresentInList (deviceList, deviceStr):
    for pciStr in deviceList:
        if deviceStr in pciStr:
            return True
    return False

'''
Returns the link status and speed of the device specified
'''
def getPcieLinkStatus (deviceStr, mappingMode):
    #lspciPath = os.path.join (os.getcwd(), "pciutils", "lspci.exe")    no longer works for qpy
    lspciPath = os.path.dirname(os.path.realpath(__file__)) + "\\pciutils\\lspci.exe"
    print(str(lspciPath))

    if mappingMode == False:
        proc = subprocess.Popen([lspciPath, '-vv', '-s ' + deviceStr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        proc = subprocess.Popen([lspciPath, '-M','-vv', '-s ' + deviceStr], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Execute the process
    out, err = proc.communicate()
    # Handle error output
    if (err):
        print ("ERROR: " + err.decode('utf-8'))
    out = out.decode('utf-8')

    # Locate the link status section    
    strPos = out.find ('LnkSta:')    
    out = out[strPos:]

    
    try:
        # Get the link speed
        matchObj = re.search ('Speed (.*?),', out)
        linkSpeed = matchObj.group(0)
        # Get the link width
        matchObj = re.search ('Width (.*?),', out)
        linkWidth = matchObj.group(0)
    # If the selected device does not have these parameters, fail here
    except:
        linkSpeed = "UNKNOWN"
        linkWidth = "UNKNOWN"
        driveTestConfig.testCallbacks["TEST_LOG"] (None, time.time(), "error", "Device does not report link speed/width", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"textDetails":"deviceName " + deviceStr + " is not suitable for link test"})

    return linkSpeed, linkWidth

'''
Checks if the given device string is visible on the bus
'''
def isPcieDevicePresent (deviceStr, mappingMode):
    # Get current device list
    deviceList = getPcieDevices (mappingMode)
    # Loop through devices and see if our module is there
    for pcieStr in deviceList:
        if deviceStr in pcieStr:
            return True
    return False

'''
Prompts the user to view the list of PCIe devices and select the one to work with
'''
""" -- Console choice
def pickPcieTarget (resourceName):

    # Check to see if the pcieMappingMode resource string is set
    mappingMode = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] ("pcieMappingMode")
    if (mappingMode == None):
        mappingMode = False

    # Get the curent devices
    deviceStr = "NO_DEVICE_STRING"
    deviceList = getPcieDevices (mappingMode)

    while devicePresentInList (deviceList, deviceStr) == False:
        print ("PCI Device was not specified")
        print ("Select from the detected Devices:")
        print ("")

        # Print the list of devices
        count = 0
        for pcieStr in deviceList:
            print (str(count) + ")  " + str(deviceList[count]))
            count = count + 1
        if (count==0):
            print ("ERROR - No PCIe devices found to display")

        # Ask for selection
        selection = input('Enter a numerical selection and press enter: ')
        # exit on 'q'
        if "q" in selection:
            return 0
        # Validate selection
        if re.match ('[0-9]+', selection):            
            if int(selection) < len(deviceList):
                deviceStr = deviceList[int(selection)]
                matchObj = re.match ('[0-9a-fA-F]+:[0-9a-fA-F]+.[0-9a-fA-F]', deviceStr)
                deviceStr = matchObj.group(0)

    # Get and store the initial link status of the selected device
    linkSpeed, linkWidth = getPcieLinkStatus (deviceStr, mappingMode)
    storeInitialDriveStats (deviceStr, linkSpeed, linkWidth)

    print("we've not sent a response before the end of the method")

    # Log the selection
    driveTestConfig.testCallbacks["TEST_LOG"] (time.time(), "comment", "Device Selected: " + "PCIE:" + deviceStr + " - Speed:" + linkSpeed + ", Width:" + linkWidth, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)

    # Store the device selection in the test resources
    driveTestConfig.testCallbacks["TEST_SETRESOURCE"] (resourceName, "PCIE:" + deviceStr)
"""

'''
Prompts the user to view the list of PCIe devices and select the one to work with
'''
def pickPcieTarget (resourceName):
    # Check to see if the pcieMappingMode resource string is set
    mappingMode = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] ("pcieMappingMode")
    if (mappingMode == None):
        mappingMode = False

    # Get the curent devices
    deviceStr = "NO_DEVICE_STRING"
    deviceList = getPcieDevices (mappingMode)
    deviceDict = {}

    while devicePresentInList (deviceList, deviceStr) == False:
        # Print the list of devices
        #count = 0
        for pcieStr in deviceList:
            #split at first space
            moduleSections = pcieStr.split(" ", 1)                      #splitting into ID and Desc
            deviceDict[moduleSections[0]] = moduleSections[1]            #Adding as key / value in dictionary
            print ("Module ID : " + str(moduleSections[0]))
            print ("Module Desc : " + str(moduleSections[1]))

            #is send across in format QuarchDTS::Key=Value
            driveTestCore.notifyChoiceOption( moduleSections[0] , moduleSections[1])
        if not deviceList:
            #python logic!
            print("ERROR - No PCIe devices found to display")

        # Ask for selection -- Send as individual as to allow infinite wait for response
        driveTestCore.sendMsgToGUI("QuarchDTS::end-of-data",None) #wait for response from java
        while driveTestCore.choiceResponse is None:
            time.sleep(0.25)

        #choice response back should be.. choiceResponse::KEY

        choice = bytes.decode(driveTestCore.choiceResponse)
        print("choice from user was : " + choice)

        selection = choice.split("::")
        #order should be choiceResponse::xyz
        selection = selection[1]

        # exit on 'q'
        if "choice-abort" in selection:
            return 0


        """
        For Andy:
        
        The items we send across are: 
        QuarchDTS::key=deviceDesc
        
        The response you will receive back currently is :
        choiceResponse::DeviceDescription
        
        Once you have a dictionary / list of key:value pairs, 
        we can change the below code to compare key with all values in 'keystore'
        """

        # Validate selection
        found = False
        # need to change to string compare

        for key,value in deviceDict.items():
            if selection.strip() == key:
                #deviceStr = deviceList[int(selection)]                                     #Finds current item in list
                #matchObj = re.match('[0-9a-fA-F]+:[0-9a-fA-F]+.[0-9a-fA-F]', deviceStr)    #Regex Match first section (KEY)
                # deviceStr = matchObj.group(0)                                             #returns deviceStr as the regex-match (KEY)
                #if any(key in s for s in deviceList):

                deviceStr = key
                print("I found your device!")
                found = True
                break

        if not found:
            print("couldn't find your device")
            return 0

        #if re.match ('[0-9]+', selection):
        #    if int(selection) < len(deviceList):


    # Get and store the initial link status of the selected device
    linkSpeed, linkWidth = getPcieLinkStatus (deviceStr, mappingMode)
    storeInitialDriveStats (deviceStr, linkSpeed, linkWidth)
    print("Storing stuff, attempting to send a comment across.")
    # Log the selection
    driveTestConfig.testCallbacks["TEST_LOG"](None, time.time(), "testDescription", "Device Selected: " + "PCIE:" + deviceStr + " - Speed:" + linkSpeed + ", Width:" + linkWidth, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)
    #driveTestConfig.testCallbacks["TEST_LOG"](uId, logTime, messageType, messageText, messageSource, messageData)
    #print("here")
    # Store the device selection in the test resources
    driveTestConfig.testCallbacks["TEST_SETRESOURCE"] (resourceName, "PCIE:" + deviceStr)


'''
Checks if the script is runnin under admin permissions
'''
def checkAdmin():
    if platform.system() == 'Windows':
        if is_winAdmin () == False:
            print ("ERROR - Script required admin permissions to run!")
            quit ()
    else:
        if is_linuxAdmin () == False:
            print ("ERROR - Script required root permissions to run!")
            quit ()

'''
Checks for a windows admin user
'''
def is_winAdmin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

'''
Checks for a linux admin user
'''
def is_linuxAdmin():
    if os.getuid() == 0:
        return True
    else:
        return False
