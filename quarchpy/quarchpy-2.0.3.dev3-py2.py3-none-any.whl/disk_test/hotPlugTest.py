
#!/usr/bin/env python

import time
import os
import sys
import driveTestConfig



# Function to simplify log message sending
def sendLogMessage (logTime, messageType, messageText, messageSource, messageData = None, uId = ""):
    if ("TEST_LOG" in driveTestConfig.testCallbacks):
         driveTestConfig.testCallbacks["TEST_LOG"](uId, logTime, messageType, messageText, messageSource, messageData)

# Displays a visual wait counter if available, otherwise just sleeps
def visualSleep (delayTime):
    if "UTILS_VISUALSLEEP" in driveTestConfig.testCallbacks:
         driveTestConfig.testCallbacks["UTILS_VISUALSLEEP"](delayTime)
    else:
        time.sleep (delayTime)    

# Sends a simple setting command that is expected to return 'OK' on success
# Logs the command
def executeAndCheckCommand (myDevice, command):
    # Run the command
    result = myDevice.sendCommand (command)

    # Log the command data
    sendLogMessage (time.time(), "debug", "Quarch Command: " + command + " - Response: " + result, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"debugLevel":1,"textDetails":"Executing command on module"}, uId="");

    # Verify that the command executed as expected
    if (result == "OK"):
        return True
    else:
        sendLogMessage (time.time(), "error", "Failed to execute Torridon command", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId="");
        return False

'''
Converts a standard time string into a common defined unit
'''
def stringTimeToInt (timeStr, outputUnit):
    multToNano = 0
    nanoTime = 0
    timeStr = timeStr.upper ()
    if ("MS" in timeStr):
        multToNano = 1000000
        timeStr = timeStr[:-2]
        nanoTime = int(timeStr) * multToNano
    elif ("US" in timeStr):
        multToNano = 1000
        timeStr = timeStr[:-2]
        nanoTime = int(timeStr) * multToNano
    elif ("NS" in timeStr):
        multToNano = 1
        timeStr = timeStr[:-2]
        nanoTime = int(timeStr) * multToNano
    elif ("S" in timeStr):
        multToNano = 1000000000
        timeStr = timeStr[:-1]
        nanoTime = int(timeStr) * multToNano
    else:
        raise ValueError ("Invalid input time unit specified")

    outputUnit = outputUnit.upper ()
    if (outputUnit == "MS"):
        return nanoTime / 1000000
    elif (outputUnit == "US"):
        return nanoTime / 1000
    elif (outputUnit == "NS"):
        return nanoTime
    elif (outputUnit == "S"):
        return nanoTime / 1000000000
    else:
        raise ValueError ("Invalid output time unit specified")

    return nanoTime

'''
Sets up a simple hot-plug timing.  6 times sources are available on most modules.
(The final delay must not exceed the max delay time of the module 1270mS for older firmware)

myDevice=Torridon device to setup
delayTime=The step delay time between each length of pin (defaults to mS, otherwise the delay must be specified 1000uS - Only supported by modules with HighRes timing, NOT IMPLEMENTED YET)
stepCount=Number of sources (number of steps) for the staged delay.  Cannot exceed the number of timed sources available
'''
def setupSimpleHotplug (myDevice, delayTime, stepCount):

    commandSuccess = True
    delayTime=int(delayTime)
    stepCount=int(stepCount)
    
    # Check parameters
    if int(delayTime) < 1:
        raise ValueError('delaytime must be positive')
    if (stepCount < 2 or stepCount > 6):
        raise ValueError('stepCount must be between 1 and 6')

    # Run through all 6 timed sources on the module
    for steps in range (1, 6):
        # Calculate the next source delay. Additional sources are set to the last value used
        if steps <= stepCount:
            nextDelay = (steps - 1 ) * delayTime
        if (executeAndCheckCommand (myDevice, "source:" + str(steps) + ":delay " + str(nextDelay)) == False):
            commandSuccess = False;
            
    return commandSuccess
        
'''
Sets up a pin bounce pattern on a given timed source.  The pattern can be specified by text parameters (future will add file name or raw pattern form)

myDevice=Torridon device to setup
sourceNumber=Number of the timed source to set
bouncePattern=Pattern description on text form.  Currently assumes the module supports High-res timing: Simple|25mS|10mS|500uS|50% (Type|delay|length|period|duty cycle)
'''
def setupSourceBounce (myDevice, sourceNumber, bouncePattern):
    commandSuccess = True
    
    # Split the string into a parameter array
    bounceParams = bouncePattern.split ('|')
    # If this is a simple bounce pattern
    if (bounceParams[0] == "Simple"):
        # Set initial delay on source
        if (executeAndCheckCommand (myDevice, "source:" + str(sourceNumber) + ":delay " + bounceParams[1]) == False):
            commandSuccess = False;
        # Set the bounce length
        if (executeAndCheckCommand (myDevice, "source:" + str(sourceNumber) + ":bounce:length " + bounceParams[2]) == False):
            commandSuccess = False;
        # Set the bounce period
        if (executeAndCheckCommand (myDevice, "source:" + str(sourceNumber) + ":bounce:period " + bounceParams[3]) == False):
            commandSuccess = False;
        # Set the bounce duty cycle (strip the %, which is not needed for the command)
        if (executeAndCheckCommand (myDevice, "source:" + str(sourceNumber) + ":bounce:duty " + bounceParams[4].strip('%')) == False):
            commandSuccess = False;
    else:
        raise ValueError ("Requested bounce type not recognised")
        
    return commandSuccess

'''
Sets a list of signals (and/or signal groups) to the given source

myDevice=Torridon device to setup
signalList=List of signal/group names to move (array/list form)
sourceNumber=Number of the timed source to set
'''
def setupSignalsToSource (myDevice, signalList, sourceNumber):   
    commandSuccess = True

    # Loop through each signal and assign it to the source
    for nextSignal in signalList:
        if (executeAndCheckCommand (myDevice, "signal:" + nextSignal + ":source " + str(sourceNumber)) == False):
            commandSuccess = False;

    return commandSuccess

'''
Removes all bounce settings from the given source, reverting back to a simple delay based connection setting

myDevice=Torridon device to setup
sourceNumber=Number of the timed source to set
'''
def clearSourceBounce (myDevice, sourceNumber):
    commandSuccess = True

    if (executeAndCheckCommand (myDevice, "source:" + str(sourceNumber) + ":bounce:clear") == False):
            commandSuccess = False;

    return commandSuccess

'''
Function to run a sweep of hot-plug tests across a given range, in a series of steps across
the the possible insertion speeds (using a simple staged hotplug, based on pin length)
Currently works in mS resolution ONLY

quarchName=Name of Quarch module (resource item name)
driveName=Name of drive under test (resource item name)
startTime=Fastest hot-plug time step (per pin length) mS
stopTime=Slowest hot-plug time step (per pin length) mS
stepCount=Number of steps to sweep between the start and stop time sweep
repeats=Number of times to repeat each point in the sweep
onTime=Optional time in seconds to wait for drive enumeration
offTime=Optional time in seconds to wait for drive removal
'''
def unhIolHotPlugSimpleSweep (quarchName, driveName, startTime, endTime, stepCount, repeats=1, onTime=10, offTime=5):
    errorCounter = 0
    errorSubCounter = 0

    # Validate required callbacks
    if ("TEST_GETDISKSTATUS" not in driveTestConfig.testCallbacks):
        raise ValueError ("You have not implemented the required TEST_GETDISKSTATUS callback!") 
    if ("TEST_GETRESOURCE" not in driveTestConfig.testCallbacks):
        raise ValueError ("You have not implemented the required TEST_GETRESOURCE callback!") 

    # Log start of test
    sendLogMessage (time.time(), "testDescription", "Starting Hotplug sweep test: " + startTime + "-" + endTime + " on device: " + driveName, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name);    

    # Get the resource for the named Quarch module
    quarchDevice = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] (quarchName)
    # Get the resource for the named disk drive under test
    driveObject = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] (driveName)    

    # Check step sizes
    startMilli = stringTimeToInt (startTime, "mS")
    endMilli = stringTimeToInt (endTime, "mS")
    sweepStep = ((endMilli - startMilli) / int(stepCount))    

    # Validate sweep times
    if (endMilli < startMilli):
        raise ValueError ("Start time must be less than or equal to the end time for the sweep")
    if (endMilli > 1270):
        raise ValueError ("End time is out of range (1270mS limit)")
    if (stepCount <= 0):
        raise ValueError ("Step time must be a positive integer")

    # Calculate sweep params
    testTimes = list ()
    for s in range (0, int(stepCount) - 1):
        testTimes.append (startMilli + ((s) * sweepStep))
    # Force end value to match in case of rounding issues
    testTimes.append (endMilli)

    # Module to default state
    executeAndCheckCommand (quarchDevice, "conf:def:state")
    # Sleep for the drive to enumerate (if not already)
    visualSleep (onTime)

    # Loop through the required steps in the sweep
    for nextTime in testTimes:
        errorSubCounter = 0

        # Log start of sub-test
        sendLogMessage (time.time(), "testDescription", "Starting Hotplug sweep sub-point: " + str(nextTime) + "mS on device: " + driveName, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name);    

        # Setup the hot-plug timing
        setupSimpleHotplug (quarchDevice, nextTime, 6)

        # Verify the device is present
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](driveObject, 1)):            
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive detected as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True});
        else:
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT detected as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False});
            errorSubCounter += 1

        # Loop through the number of repeats we need of this plug speed
        for loop in range (0, repeats):

            # Pull the module
            executeAndCheckCommand (quarchDevice, "run:power down")

            # Sleep for drive to shut down
            visualSleep (offTime)

            # Verify the device is gone
            if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](driveObject, 0)):       
                sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive removed, as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True});                
            else:
                sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT removed", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False});
                errorSubCounter += 1

            # Plug the module
            executeAndCheckCommand (quarchDevice, "run:power up")

            # Sleep for drive to power up
            visualSleep (onTime)

            # Verify the device is present
            if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](driveObject, 1)):            
                sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive detected as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True});
            else:
                sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT detected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False});
                errorSubCounter += 1

        # Track errors from this time step
        errorCounter += errorSubCounter
        if errorSubCounter == 0:
            sendLogMessage (time.time(), "testResult", "Hotplug sweep test passed all repeats at: " + str(nextTime), os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True});
        else:
            sendLogMessage (time.time(), "testResult", "Hotplug sweep test failed: " + str(errorSubCounter) + " repeats at: " + str(nextTime), os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False});

    # Track errors from the entire sweep    
    if errorCounter == 0:
        sendLogMessage (time.time(), "testResult", "Hotplug sweep test passed all tests", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True});
    else:
        sendLogMessage (time.time(), "testResult", "Hotplug sweep test failed: " + str(errorCounter) + " repeats in total", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False});


'''
Function to run a set number of hotplug remove/insert cycles using a simple staged hot-plug


quarchName=Name of Quarch module (resource item name)
driveName=Name of drive under test (resource item name)
insertTime=Hot-plug time step (per pin length) in mS
repeats=Number of times to repeat each point in the sweep
onTime=Optional time in seconds to wait for drive enumeration
offTime=Optional time in seconds to wait for drive removal
'''
def simpleHotPlugTest (uniqueID, quarchName, driveName, insertTime, repeats=1, onTime=10, offTime=5):

    startTestTime = time.time()

    errorSubCounter = 0

    # Validate required callbacks
    if ("TEST_GETDISKSTATUS" not in driveTestConfig.testCallbacks):
        raise ValueError ("You have not implemented the required TEST_GETDISKSTATUS callback!") 
    if ("TEST_GETRESOURCE" not in driveTestConfig.testCallbacks):
        raise ValueError ("You have not implemented the required TEST_GETRESOURCE callback!")     

    # Log start of test
    sendLogMessage (time.time(), "testDescription", "Starting Hotplug test at: " + str(insertTime) + "mS on device: " + driveName + ", over " + str(repeats) + " repeats", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId = uniqueID);

    # Get the resource for the named Quarch module
    quarchDevice = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] (quarchName)
    if (quarchDevice is None):
        raise ValueError ("Selected test resource: [" + quarchName + "] not found")
    
    # Get the resource for the named disk drive under test
    driveObject = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] (driveName)
    if (driveObject is None):
        raise ValueError ("Selected test resource: [" + driveName + "] not found")

    # Module to default state
    executeAndCheckCommand (quarchDevice, "conf:def:state")
    # Setup the hot-plug timing
    setupSimpleHotplug (quarchDevice, insertTime, 6)
    # Sleep for the drive to enumerate (if not already)
    visualSleep (onTime)

    # Loop through the number of repeats we need of this plug speed
    for loop in range (0, int(repeats)):

        # Pull the module
        executeAndCheckCommand (quarchDevice, "run:power down")

        # Sleep for drive to shut down
        visualSleep (offTime)

        # Verify the device is gone
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](uniqueID, driveObject, 0)):
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive removed, as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True}, uId = uniqueID);
        else:
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT removed as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False}, uId = uniqueID);
            errorSubCounter += 1            

        # Plug the module
        executeAndCheckCommand (quarchDevice, "run:power up")

        # Sleep for drive to power up
        visualSleep (onTime)

        # Verify the device is present
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](uniqueID, driveObject, 1)):
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive detected as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True}, uId = uniqueID);
        else:
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT detected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False}, uId = uniqueID);
            errorSubCounter += 1

    # Track errors from this time step   
    if errorSubCounter == 0:
        sendLogMessage (time.time(), "testResult", "Hotplug test passed all repeats", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True}, uId = uniqueID);
    else:
        sendLogMessage (time.time(), "testResult", "Hotplug sweep test failed: " + str(errorSubCounter) + " sub-test points", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False}, uId = uniqueID);

    elapsedTime = time.time() - startTestTime 
    summaryString = "TestTime Elapsed: " + str(int(elapsedTime)) + ", Error count = " + str(errorSubCounter) 

    sendLogMessage (time.time(), "testSummary", summaryString, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId = uniqueID);

        

'''
Function to run a set number of hotplug remove/insert cycles using a simple staged hot-plug and added pin-bounce
A single pin bounce pattern can be specified and applied to any number of signal(s)/group(s).  The bounce pattern is
applied to source 4, as this is not used by default on any existing module.


quarchName=Name of Quarch module (resource item name)
driveName=Name of drive under test (resource item name)
insertTime=Hot-plug time step (per pin length) in mS
bouncePattern=Simple|25mS|10mS|500uS|50% (Type|delay|length|period|duty cycle)
bounceSignals=Name1|Name2|Name3
repeats=Number of times to repeat each point in the sweep
onTime=Optional time in seconds to wait for drive enumeration
offTime=Optional time in seconds to wait for drive removal
bounceOnPlug=Optional flag, should bounce be applied to plug
bounceOnPull=Optional flag, should bounce be applied to pull (defaults to False)
'''
def simpleHotPlugBounceTest (uniqueID, quarchName, driveName, insertTime, bouncePattern, bounceSignals, repeats=1, onTime=10, offTime=5, bounceOnPlug=True, bounceOnPull=False):

    startTestTime = time.time()

    errorSubCounter = 0
    signalList = bounceSignals.split('|')

    # Validate required callbacks
    if ("TEST_GETDISKSTATUS" not in driveTestConfig.testCallbacks):
        raise ValueError ("You have not implemented the required TEST_GETDISKSTATUS callback!") 
    if ("TEST_GETRESOURCE" not in driveTestConfig.testCallbacks):
        raise ValueError ("You have not implemented the required TEST_GETRESOURCE callback!")     

    # Log start of test
    sendLogMessage (time.time(), "testDescription", "Starting (Bounce) Hotplug test at: " + str(insertTime) + "mS on device: " + driveName + ", over " + str(repeats) + " repeats", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId = uniqueID);

    # Get the resource for the named Quarch module
    quarchDevice = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] (quarchName)
    # Get the resource for the named disk drive under test
    driveObject = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] (driveName) 

    # Module to default state
    executeAndCheckCommand (quarchDevice, "conf:def:state")
    # Setup the hot-plug timing
    setupSimpleHotplug (quarchDevice, insertTime, 6)    
    # Move the required signals to source 4 (enabling then for bounce)
    setupSignalsToSource (quarchDevice, signalList, 4)
    # (If bounce is required during pull)
    if (bounceOnPull):
        # Setup the pin bounce, using source 4 for now
        setupSourceBounce (quarchDevice, 4, bouncePattern)
    else:
        clearSourceBounce (quarchDevice, 4)
    # Sleep for the drive to enumerate (if not already)
    visualSleep (onTime)    

    # Loop through the number of repeats we need of this plug speed
    for loop in range (0, int(repeats)):

        # If bounce is required during pull
        if (bounceOnPull):
            # Setup the pin bounce, using source 4 for now
            setupSourceBounce (quarchDevice, 4, bouncePattern)
        else:
            clearSourceBounce (quarchDevice, 4)

        # Pull the module
        executeAndCheckCommand (quarchDevice, "run:power down")

        # Sleep for drive to shut down
        visualSleep (offTime)

        # Verify the device is gone
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](uniqueID, driveObject, 0)):
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive removed, as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True}, uId = uniqueID);
        else:
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT removed as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False}, uId = uniqueID);
            errorSubCounter += 1    
            
        # If bounce is required during plug
        if (bounceOnPlug):
            # Setup the pin bounce, using source 4 for now
            setupSourceBounce (quarchDevice, 4, bouncePattern)
        else:
            clearSourceBounce (quarchDevice, 4)

        # Plug the module
        executeAndCheckCommand (quarchDevice, "run:power up")

        # Sleep for drive to power up
        visualSleep (onTime)

        # Verify the device is present
        if (driveTestConfig.testCallbacks["TEST_GETDISKSTATUS"](uniqueID, driveObject, 1)):
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive detected as expected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True}, uId = uniqueID);
        else:
            sendLogMessage (time.time(), "testResult", "HOT_PLUG: Drive NOT detected", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False}, uId = uniqueID);
            errorSubCounter += 1

    # Track errors from this time step   
    if errorSubCounter == 0:
        sendLogMessage (time.time(), "testResult", "Hotplug test passed all repeats", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":True}, uId = uniqueID);
    else:
        sendLogMessage (time.time(), "testResult", "Hotplug sweep test failed: " + str(errorSubCounter) + " sub-test points", os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, {"testResult":False}, uId = uniqueID);

    elapsedTime = time.time() - startTestTime 
    summaryString = "TestTime Elapsed: " + str(int(elapsedTime)) + ", Error count = " + str(errorSubCounter) 

    sendLogMessage (time.time(), "testSummary", summaryString, os.path.basename(__file__) + " - " + sys._getframe().f_code.co_name, uId = uniqueID);

