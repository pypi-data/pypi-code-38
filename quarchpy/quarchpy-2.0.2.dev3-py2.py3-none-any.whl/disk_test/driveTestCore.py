#!/usr/bin/env python
'''
This file contains the core functions for the drive test suite.
Functions are placed here for the core setup functions called during the init stage of a test (or CSV parsed test set)


########### VERSION HISTORY ###########

03/01/2019 - Andy Norrie        - First Version

########### INSTRUCTIONS ###########

N/A

####################################
'''

from __future__ import print_function
import sys
import os
import threading
import time
import xml.etree.ElementTree as cElementTree
import socket
import multiprocessing
import importlib
import traceback
from datetime import datetime

from quarchpy.device import quarchDevice, quarchArray
from quarchpy.disk_test.testLine import testLine
from quarchpy.device import scanDevices

import quarchpy.disk_test.lspci as lspci
import quarchpy.disk_test.hotPlugTest as hotPlugTest
import quarchpy.disk_test.driveTestConfig as driveTestConfig

#import driveTestConfig
#from quarchpy.disk_test import hotPlugTest
#from quarchpy.disk_test.driveTestConfig import testCallbacks, testResources
#from quarchpy.disk_test.lspci import isPcieDevicePresent, verifyDriveStats
#from driveTestConfig import testCallbacks, testResources





# Import zero conf only if available
try:
    import zeroconf
    from zeroconf import ServiceInfo, Zeroconf
    zeroConfAvail = True
except:
    zeroConfAvail = False

#string to save reply from java (for module selection e.t.c)
choiceResponse = None
GUI_TCP_IP = "127.0.0.1"

'''
Stores a given string in the test resources dictionary
'''
def storeResourceString (resourceName, resourceValue):
    driveTestConfig.testResources[resourceName] = resourceValue


'''
Adds a newly defined quarch module to use during the test and stores it as a resource to use later
connection="USB:QTL1743" or "REST:192.168.1.12<7>"
moduleName="myModule1" (unique string to identify the resource later)
'''
def specifyQuarchModule(connection, moduleName):

    # If this is an array controller sub module
    strPos = connection.find ('<')
    if (strPos != -1):
        print(connection + " : " + moduleName)
        # Get the array part
        arrayConnection = connection[0:strPos]
        # Get the sub module nubmber
        arrayPosition = connection[strPos+1:]
        arrayPosition = arrayPosition.strip(' >')

        # Create the array controller connection
        myQuarchDevice = quarchDevice(arrayConnection)        
        # Promote connection to array type
        myArray = quarchArray(myQuarchDevice) 
        # Get access to the sub-device
        mySubDevice = myArray.getSubDevice (arrayPosition)
        moduleResponse = mySubDevice.sendCommand("*TST?")

        # Test the connection
        if (moduleResponse != "OK"):
            notifyTestLogEvent(time.time(), "error", "Quarch module not ready", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"textDetails":"Module responded: " + moduleResponse})
        else:
            # Add the item to the test resources dictionary
            driveTestConfig.testResources[moduleName] = mySubDevice
    else: 
        # Create the device connection
        print(connection)
        myQuarchDevice = quarchDevice(connection)

        # Test the connection
        moduleResponse = myQuarchDevice.sendCommand("*TST?")
        if (moduleResponse is None or moduleResponse == ""):
            notifyTestLogEvent(time.time(), "error", "Quarch module did not respond", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)
            return
        elif (moduleResponse != "OK"):
            notifyTestLogEvent(time.time(), "warning", "Quarch module did not pass self test", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"textDetails":"Module responded: " + moduleResponse})

        # Add the item to the test resources dictionary
        driveTestConfig.testResources[moduleName] = myQuarchDevice
            


'''
Parses and executes all the tests specified within the given CSV file
testCallbacks=Dictionary of callback function for the tests
filePath=Full path to CSV file containing the tests
'''
def executeCsvTestFile(testCallbacks, filePath, delimitor="\t"):
    # Open the test file for parsing
    with open(filePath, 'r') as scriptFile:
        # Iterate through each line in the file
        for fileLine in scriptFile:
            # Comment lines
            if (fileLine.find("#") == 0):
                # Ignore file comment lines
                continue
            # Config line - for setting up modules and test elements
            elif (fileLine.find("Config") == 0):
                # Split the line into sections
                lineSections = fileLine.split(delimitor)
                # Get the module that the setup function is in
                moduleName = lineSections[1]
                # Get the name of the setup function
                testName = lineSections[2]

                # Build up the paramenter string for the python function call
                funcParams = ""
                for x in range(3, len(lineSections)):
                    # Skip any params that have no data (CSV file can generate empty params here)
                    if (len(lineSections[x].strip()) > 0):
                        funcParams = funcParams + lineSections[x].strip() + ","
                # Strip the last comma off the end
                funcParams = funcParams.strip(',')

                # Parse the string into a dictionary of parameters
                parsedArgs = dict(e.split('=') for e in funcParams.split(','))               
                modulePointer = sys.modules[moduleName]
                # Call the function, using module.function(parameters)
                getattr(modulePointer, testName)(**parsedArgs)
            # Standard test line - for running a defined test
            elif (fileLine.find("Test") == 0):
                # Split the line into sections
                lineSections = fileLine.split(delimitor)
                # Get the module that the setup function is in
                moduleName = lineSections[1]
                # Get the name of the setup function
                testName = lineSections[2]

                # Build up the paramenter string for the python function call
                funcParams = ""
                for x in range(3, len(lineSections)):
                    # Skip any params that have no data (CSV file can generate empty params here)
                    if (len(lineSections[x].strip()) > 0):
                        funcParams = funcParams + lineSections[x].strip() + ","
                # Strip the last comma off the end
                funcParams = funcParams.strip(',')

                # Parse the string into a dictionary of parameters
                parsedArgs = dict(e.split('=') for e in funcParams.split(','))
                
                # Get the module pointer for the required test module
                modulePointer = sys.modules[moduleName]
                # Call the function, using module.function(parameters)
                getattr(modulePointer, testName)(**parsedArgs)
            # Skip line - used to mark test for temporary bypass
            elif (fileLine.find("Skip") == 0):
                continue
            # Ignore blank lines
            elif (len(fileLine.strip()) == 0):
                continue
            # Undefined line type
            else:
                # Split the line into sections
                lineSections = fileLine.split(delimitor)
                # Log the error of the unknown line type
                driveTestConfig.testCallbacks["TEST_LOG"](time.time(), "error", "Unknown test line type: " + lineSections[0], os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name)



'''
Adds a newly defined disk drive to use during the test
driveId="PCI:0:00.0"
driveName="myDrive1"
'''
def specifyDriveById(driveId, driveName):    
    # Add the item to the test resources dictionary
    driveTestConfig.testResources[driveName] = driveId


'''
Callback function allowing tests to request a specific 'test resource' item
This could be a quarch module connection, setup string or any other object.
These resources are created during the 'Config' phase

resourceName=Name of the resource to return
'''
def getTestResource (resourceName):
    if (resourceName in driveTestConfig.testResources):
        return driveTestConfig.testResources[resourceName]
    else:
        notifyTestLogEvent(time.time(), "error", "Unknown resource item requested:" + resourceName, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"textDetails":"The given resource name was not found"})
        return None
'''
Callback function allowing tests to store a specific 'test resource' item
This could be a quarch module connection, setup string or any other object.
These resources are created during the 'Config' phase

resourceName = Unique name of resource
resourceValue = Value for resource
'''
def setTestResource (resourceName, resourceValue):
    driveTestConfig.testResources[resourceName] = resourceValue


def resetTestResources () :
    #python booleanness logic - if true there's something here
    if driveTestConfig.testResources:
        driveTestConfig.testResources.clear()

'''
Callback: Run when a test invokes UTILS_VISUALSLEEP.  This allows user feedback when a delay function is required. Specified
delay time is in seconds
'''
def visualSleep(delayTime):
    # Print header for delay
    print("Delay:" + str(delayTime) + "S:", end="")
    # Tick through each second
    for x in range(0, delayTime):        
        time.sleep(1)
        print(".", end="")
    # Force a new line
    print("")



'''
Callback: Run whenever a TEST_LOG event ocurrs, allowing the script to direct the various forms
of output from tests to one or more locations (terminal, results database and similar)
'''
logFilePath = os.path.join(os.getcwd(), "LogFile" + str(datetime.now()).replace(':','_') + ".txt")
def notifyTestLogEvent(timeStamp, logType, logText, logSource, logDetails=None):
    # Build up log string
    logString = datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S') + "\t" + logType + "\t" + logText + "\t" + logSource
    # Append details
    if (logDetails != None):
        for k,v in logDetails.items():
            logString = logString + "\t" + k + "=" + str(v)
    # Print to terminal, skipping debug if not required
    if (not (driveTestConfig.logDebugMessagesOnTerminal == False and logType == 'debug')):
        print(logString)
    # Write to log file, skipping debug if not required
    if (not (driveTestConfig.logDebugMessagesInFile == False and logType == 'debug')):
        with open(logFilePath, 'a') as logFile:
            logFile.write(logString + "\n") 
            
'''
Callback: Run whenever a TEST_LOG event ocurrs, allowing the script to direct the various forms
of output from tests to one or more locations (terminal, results database and similar)

This version logs to a remote TCP server
'''
def notifyTestLogEventXml(uniqueId, timeStamp, logType, logText, logSource, logDetails=None):

    print("Unique id : " + str(uniqueId))

    if uniqueId is "" or uniqueId is None:
        #quick check in place just to ensure the unique id of an object is not sent incorrectly
        uniqueId = " "

    # Build main XML structure
    xmlObject = cElementTree.Element("object")
    cElementTree.SubElement(xmlObject, "uniqueID").text = uniqueId
    cElementTree.SubElement(xmlObject, "timestamp").text = datetime.utcfromtimestamp(timeStamp).strftime('%Y-%m-%d %H:%M:%S')
    cElementTree.SubElement(xmlObject, "logType").text = logType
    cElementTree.SubElement(xmlObject, "text").text = logText
    cElementTree.SubElement(xmlObject, "messageSource").text = logSource
    # Add details dictionary if present
    if (logDetails != None):
        xmlDetails = cElementTree.SubElement(xmlObject, "logDetails")
        for k,v in logDetails.items():
            xmlEntry = cElementTree.SubElement(xmlDetails, "entry")
            cElementTree.SubElement(xmlEntry, "key").text = str(k)
            cElementTree.SubElement(xmlEntry, "value").text = str(v)

    print("creating xml tree object str")
    xmlstr = str(cElementTree.tostring(xmlObject),"UTF-8").replace("\n", "")
    # Send to GUI server
    sendMsgToGUI(xmlstr)
    
    # TODO: Remove me - temp output to old log as well
    # notifyTestLogEvent(timeStamp, logType, logText, logSource, logDetails)


def notifyChoiceOption(count,option):
    sendString = "QuarchDTS::" + str(count) + "=" + str(option)
    # Send to GUI server
    sendMsgToGUI(sendString)

"""
Function for any item being sent to GUI 
Default is to wait 3 seconds, but can be set for longer / infinite
"""
def sendMsgToGUI(toSend, timeToWait = 5):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((driveTestConfig.guiAddress, driveTestConfig.guiPort))
    print ("IP trying to connect on is : " + str(GUI_TCP_IP))
    s.connect((GUI_TCP_IP, 9921))
    # TODO: Remove the print command
    print ("Item Sent across : " + toSend )
    toSend = str.encode(toSend)

    s.sendall(toSend + b"\n")
    # function for response + timeout

    #basically infinite wait
    if timeToWait is None:
        timeToWait = 999999

    processTimeoutAndResult(s, timeToWait)
    print("Received a confirmation response, closing port and continueing")
    s.close()


"""
Starts a subprocess to attempt to receive a return packet from java
if timeout of 3 seconds is exceeded, break
"""
def processTimeoutAndResult(socket, timeToWait):
    processObject = threading.Thread(target=getReturnPacket(socket))
    processObject.start()
    # timeout of 3 seconds
    start = time.time()
    while time.time() - start <= timeToWait:
        if processObject.is_alive():
            # print("Sleeping, timeout Left = " + str(TIMEOUT - (time.time() - start)))
            time.sleep(.1)  # Just to avoid hogging the CPU
        else:
            # All the processes are done, break now.
            break
    else:
        # We only enter this if we didn't 'break' above.
        # print("Response Timeout Reached")
        processObject.terminate()
        processObject.join()

"""
reads data from socket passed
"""
def getReturnPacket(socket):
    BUFFER_SIZE = 4096
    data = ""
    while(True):
        data = socket.recv(BUFFER_SIZE)
        if "OK" in bytes.decode(data):
            break
        if "choiceResponse" in bytes.decode(data):
            global choiceResponse
            choiceResponse = data
            print ("I recieved user's choice now")
            break
        if "STOP" in bytes.decode(data):
            print (data)
            break
    return 

'''
Simple debug function for collating terminal print requests for debug purposes.
Use this rather than a direct print for all debug messages
'''
def debugTerminalPrint (message):
    if (driveTestConfig.logTerminalDebug == True):
        print (message)
    return

'''
Callback: Run when a test invokes TEST_GETDISKSTATUS (Check the status of the drive).  This can use lspci or
be expanded to use any form of internal test tool
'''
def DiskStatusCheck(uniqueID, driveId, expectedState):
    # PCIE drive type
    if (driveId.index('PCIE:') == 0):        
        # Get pcieMappingMode resource if set
        # Check to see if the pcieMappingMode resource string is set
        mappingMode = getTestResource ("pcieMappingMode")
        if (mappingMode == None):
            mappingMode = False

        # Get the PCIe address
        pcieAddress = driveId[5:]
        driveState = lspci.isPcieDevicePresent (pcieAddress, mappingMode)

        # If drive should be plugged, verify the speed and link width
        if (expectedState):
            if (lspci.verifyDriveStats (uniqueID, pcieAddress, mappingMode) and driveState):
                return True
            else:
                return False
        else:        
            if(driveState == False):
                return True
            else:
                return False

        return driveState
    # Unknown device type
    else:        
        notifyTestLogEvent(time.time(), "error", "Unknown drive type: " + driveId, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"textDetails":"Unable to check status of the drive"})
        return False





CurrentTest = "starting"
def alivePulse():
    counter = 0
    quarchidentifier = "QuarchDTS"
    separator = "::"
    current_time = time.time()

    while True:
        # QuarchDTS::currentTest::1
        quarchstringtosend = quarchidentifier + separator + CurrentTest + separator + str(counter)

        #print("time is " + str(time.time() - current_time))

        if (time.time() - current_time) > 1:
            #send item to gui and reset function variables

            try :
                sendMsgToGUI(quarchstringtosend)
                counter += 1
            except Exception as e:
                print("server not up")
                print (e)
                pass
            current_time = time.time()


        #as to not clutter cpu
        time.sleep(.1)

'''
Tries to get the local/network IP address of the server
'''
def getLocalIpAddress ():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = None
    finally:
        s.close()
    return IP


'''
Activates a remote server at the given port number.  This function will not return until the server connection is closed

This is intended for use with a remote client (generally running a compliance test script).  This server takes in XML format command requests and executes local
test functions based on this.
'''
def ActivateRemoteServer(portNumber=9742, localHost = True):

    driveTestConfig.testCallbacks = {"TEST_LOG": notifyTestLogEventXml,
                                     "TEST_GETDISKSTATUS": DiskStatusCheck,
                                     "UTILS_VISUALSLEEP": visualSleep,
                                     "TEST_GETRESOURCE": getTestResource,
                                     "TEST_SETRESOURCE": setTestResource }

    TCP_IP = '127.0.0.1'

    if not localHost:
        TCP_IP = socket.gethostbyname(socket.gethostname())
        print("Using ip: " + str(socket.gethostbyname(socket.gethostname())))
    else:
        print("Using local - 127.0.0.1")

    TCP_PORT = portNumber
    portNumber = 1024
    BUFFER_SIZE = 4096
    mDnsInfo = None
    
    # Get the sensible server name
    if (serverName is None):
        try:
            serverName = socket.gethostname()
        except:
            serverName = "no-name-server"

    try:
        # Setup and open the socket for connection
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind((TCP_IP, TCP_PORT))
        sock.listen(1)
        print ("----Remote Server Activated----")
        print("\tServer IP: " + str(TCP_IP))
        
        # Activates mDNS registration for the server, so it can be located remotely
        if (zeroConfAvail):                   
            try:
                # Register the service
                mDnsIp = TCP_IP
                mDnsDesc = {'version': '1.0','server-name': serverName}
                mDnsInfo = ServiceInfo("_http._tcp.local.", "quarchCS._http._tcp.local.", socket.inet_aton(mDnsIp), TCP_PORT, 0, 0, mDnsDesc)
                zeroConf = Zeroconf()
                zeroConf.register_service(mDnsInfo)           

                # Print registration results
                print ("----mDNS Registered----")
                print ("\tServer Name: " + serverName)
            except:
                print ("mDNS error, Service not registered")
        else:
            zeroConf = None
            

        # Wait for a connection
        #sock.setblocking(0)
        conn, addr = sock.accept()
        print ("----Remote Server connection opened from: " + str(addr))

        global GUI_TCP_IP
        #layout = :<'x.x.x.x',xx>
        item = str(addr).split('\'')
        GUI_TCP_IP = item[1]

        continueScript = True

        #processObject = multiprocessing.Process(target=alivePulse())
        # doesn't matter if the process terminates mid - completion
        #processObject.daemon = True
        #processObject.start()

        try:
            # Loop while the server is to be active
            while continueScript:
                # Get data from the connection
                data = conn.recv(BUFFER_SIZE)
                if not data: pass

                data = data.replace(str.encode("\r\n"),b"")
                #print("Data Recieved = " + bytes.decode(data))

                if "Alive?" in bytes.decode(data):
                    #polling to seeif alive

                    toSend = str.encode("ok >")

                    conn.sendall(toSend + b"\n")
                    #conn.sendall(str.encode(finishedString))
                    continue

                try:
                    myobj = testLine()
                    # Parse the data (should be in XML form)
                    
                    xmlRoot = cElementTree.fromstring(bytes.decode(data))
                    myobj.initFromXml(xmlRoot)
                    # Get the module pointer for the required test module
                    if (myobj.moduleName == "driveTestCore"):
                        modulePointer = sys.modules[__name__]
                    else:
                        modulePointer = importlib.import_module(myobj.moduleName)#sys.modules[myobj.moduleName]

                    print(str(modulePointer))
                    #print(bytes.decode(data))

                    # Call the requested function, using module.function(parameters)
                    getattr(modulePointer, myobj.testName)(**myobj.paramList)

                    print("Sending Data : ok >")
                    finishedString = "ok >"
                    conn.sendall(str.encode(finishedString) + b"\n")

                    pass

                except ValueError:
                    print ("ERROR - Bad remote command format")

                except AttributeError:
                    print ("Error loading module")

                except:
                    print ("ERROR - Unexpected failure in command parser")
                    raise
        except KeyboardInterrupt:
            print ("---Remote server shutdown request, user CTRL-C received")
    except Exception as ex:
        print ("----Remote server process exited with an exception")
        print (ex)
        traceback.print_tb(ex.__traceback__)
    finally:
        #processObject.terminate()
        #processObject.join()

        conn.close()
        #sock.shutdown()
        sock.close()
        print ("----Remote server shutdown complete")


if __name__ == "__main__":

    print("\n################################################################################")
    print("\n                           QUARCH TECHNOLOGY                        \n\n  ")
    print("Automated Drive/Host test suite.   ")
    print("\n################################################################################\n")  

    ActivateRemoteServer()



