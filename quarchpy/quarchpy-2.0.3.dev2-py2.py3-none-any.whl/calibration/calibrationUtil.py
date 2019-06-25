#!/usr/bin/env python
'''
This example runs the calibration process for a HD PPM
It products a calibrated PPM and a calibration file for later use

########### VERSION HISTORY ###########

05/04/2019 - Andy Norrie     - First Version

########### INSTRUCTIONS ###########

1- Connect the PPM on LAN and power up
2- Connect the Keithley 2460 until on LAN, power up and check its IP address
3- Connect the calibration switch unit to the output ports of the PPM and Keithley

####################################
'''

# Global resources
#import quarchpy.calibration.calibrationConfig
from time import sleep,time
import datetime
import logging,os
import sys

# Quarch device control
from quarchpy.device import *

# Calibration control
#from quarchpy.calibration import *
from quarchpy.calibration.keithley_2460_control import *
from quarchpy.calibration.calibration_classes import *
from quarchpy.calibration.HDPowerModule import *
from quarchpy.calibration.calibrationConfig import *

# UI functions
from quarchpy.user_interface import *

# Performs a standard calibration of the PPM
def runCalibration (instrAddress=None, calPath=None, ppmAddress=None, logLevel="warning", calAction=None, userMode="testcenter"):

    try:

        # Process parameters
        if (calPath is None):
            calPath = os.getcwd()
        if (os.path.isdir(calPath) == False):
            raise ValueError ("Supplied calibration path is invalid: " + calPath)
        # Use current directory if none is specified
        if (calPath is None):
            calPath = os.getcwd()
            printText ("No output folder specified, using: " + calPath)

        #check log file is present or writeable
        numeric_level = getattr(logging, logLevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)              

        # Display the app title to the user
        printText("********************************************************")
        printText("Quarch Technology Calibration System")
        printText("(C) 2019, All rights reserved")
        printText("V" + quarchpy.calibration.calCodeVersion)
        printText("********************************************************")
        printText("")
        printText("Calibration process for QTL1999 HD Power Modules")
        printText("")
        printText("********************************************************")
        printText("")

        # main execution loop
        while(True):

            # If no address specified, the user must select the module to calibrate
            if (calAction != None and 'select' in calAction) or (ppmAddress == None):  
                
                # Request user to select the (QTL1999) PPM to calibrate
                ppmAddress = userSelectDevice (scanFilterStr = ["QTL1999","QTL1995","QTL1944"])

                if (ppmAddress == 'quit'):
                    sys.exit(0)
                else:
                    myPpmDevice = quarchDevice(ppmAddress)

                    serialNumber = myPpmDevice.sendCommand("*SERIAL?")
                    
                    # Identify and create a power module object
                    if ('1944' in serialNumber):
                        # create HD Power Module Object
                        ppm = HDPowerModule(myPpmDevice)
                    else:
                        raise ValueError("ERROR - Serial number not recogised as a valid power module")

                    # Creates the calibration header information object and populates it with all basic information
                    calHeader = CalibrationHeaderInformation()
                    # Store the current cal header as a resource that can be accessed later
                    calibrationResources["CalHeader"] = calHeader

                    # populate device information
                    populateCalHeader_HdPpm(calHeader, ppm.dut, calAction)
                    #populate system information
                    populateCalHeader_System(calHeader)

                    # create calibration File Name
                    # if its a x6, append the port number
                    if 'QTL1995' in calHeader.quarchEnclosureSerial.upper():
                        calFilename = calHeader.quarchEnclosureSerial + "_port:" + calHeader.quarchEnclosurePosition
                    else:
                        calFilename = calHeader.quarchEnclosureSerial

                    # keep track of overall pass/fail status, this is set false if we fail a test. it should only be set back to true
                    # here, or if the user initiates another test.
                    calHeader.result = True

                    storeDeviceInfo(serial=calHeader.quarchEnclosureSerial,idn=calHeader.idnStr)

            # If no calibration action is selected, request one
            if (calAction == None):

                actionList = []               
                actionList.append("read=Read calibration data from the power module to disk")
                actionList.append("write=Write calibration data from disk to the power module")
                actionList.append("calibrate=Calibrate the power module")
                actionList.append("verify=Verify existing calibration on the power module")
                actionList.append("select=Select a different power module")
                actionList.append("quit=Quit")
                actionList = ','.join(actionList)

                calAction = listSelection("Select an action","Please select an action to perform",actionList)

                calHeader.result = True

            if (calAction == 'quit'):
                if userMode == "testcenter":
                    return #TODO: calHeader
                else:
                    sys.exit(0)

            # If a read is requested
            if ('read' in calAction):
                
                savedCalibration = ppm.readCalibration()

            elif ('write' in calAction):

                ppm.writeCalibration(savedCalibration)

            elif ('calibrate' in calAction) or ('verify' in calAction):

                # If no calibration instrument is provided, request it
                while(True):
                    if (instrAddress == None):
                        instrAddress = userSelectCalInstrument (scanFilterStr = "Keithley 2460")
                    try:
                        # Connect to the calibration instrument
                        myCalInstrument = keithley2460 (instrAddress)
                        # Open the connection
                        myCalInstrument.openConnection ()
                        populateCalHeader_Keithley(calHeader, myCalInstrument)
                        break
                    # In fail, allow the user to try again with a new selection
                    except:
                        printText ("Unable to communicate with selected instrument!")
                        printText("")         
                        instrAddress = None

                # check self test
                # TODO : check status here

                # open report for writing
                fileName = calPath + "\\" + calFilename + "_" + datetime.datetime.now().strftime("%d-%m-%y_%H-%M" + ".txt")
                printText("")
                printText("Report file: " + fileName)
                reportFile = open(fileName,"a+")
                reportFile.write(calHeader.toReportText())
    
                # If a calibration is requested
                if ('calibrate' in calAction):                

                    report = ppm.calibrate(myCalInstrument,reportFile)

                    if report:
                        printText("Calibration Passed")
                        reportFile.write("Calibration Passed")
                    else:
                        printText("Calibration Failed")
                        reportFile.write("Calibration Failed")
                        calHeader.result = False

                # If a verify is required
                if ('verify' in calAction):           

                    report= ppm.verify(myCalInstrument,reportFile)

                    if report:
                        printText("Verification Passed")
                        reportFile.write("Verification Passed")
                    else:
                        printText("Verification Failed")
                        reportFile.write("Verification Failed")
                        calHeader.result = False

                # Close all instruments
                myCalInstrument.closeConnection()      

                reportFile.close()

            # End of Loop
            # if we've done a calibrate, always verify next
            if 'calibrate' in calAction:
                calAction = 'verify'
            # else, unless we're selecting a new ppm, clear calAction
            elif 'select' in calAction:
                pass
            # if we're in testcenter, always exit before selecting a new module
            elif userMode == "testcenter":
                calAction = "quit"
            else:
                calAction = None
    
    except Exception as thisException:
        try:
            myCalInstrument.setLoadCurrent(0)
            myCalInstrument.closeConnection()
        # Handle case where exception may have been thrown before instrument was set up
        except:
            pass
        logging.error(thisException)

        raise thisException

# Returns a resource from the previous calibration.  This is the mechanism for getting results and similar back to
# a higher level automated script.
def getCalibrationResource (resourceName):
    try:
        return calibrationConfig.calibrationResources[resourceName]
    except:
        return None

def main(argstring):
    import argparse
    # Handle expected command line arguments here using a flexible parsing system
    parser = argparse.ArgumentParser(description='Calibration utility parameters')
    parser.add_argument('-a', '--action', help='Calibration action to perform', choices=['calibrate', 'verify'], type=str.lower)
    parser.add_argument('-m', '--module', help='IP Address or netBIOS name of power module to calibrate', type=str.lower)
    parser.add_argument('-i', '--instr', help='IP Address or netBIOS name of calibration instrument', type=str.lower)
    parser.add_argument('-p', '--path', help='Path to store calibration logs', type=str.lower)    
    parser.add_argument('-l', '--logging', help='Level of logging to report', choices=['warning', 'error', 'debug'], type=str.lower,default='warning')
    parser.add_argument('-u', '--userMode', help='User mode',choices=['console','testcenter'], type=str.lower,default='console')
    args = parser.parse_args(argstring)
    
    # Create a user interface object
    thisInterface = user_interface(args.userMode)

    # Call the main calibration function, passing the provided arguments
    runCalibration(instrAddress = args.instr, calPath = args.path, ppmAddress = args.module, logLevel = args.logging, calAction = args.action, userMode = args.userMode)
	
# CalUtil --ppm USB:1999 --instr 192.168.1.21 --calpath c:\CalData --action calibrate
#
#
if __name__ == "__main__":
    main (sys.argv[1:])
    #main (sys.argv)