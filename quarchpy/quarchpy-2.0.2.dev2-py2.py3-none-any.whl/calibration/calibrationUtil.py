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
# Calibration control
from quarchpy.calibration import *
# Quarch device control
from quarchpy.device import *
# Global resources
import quarchpy.calibration.calibrationConfig
from time import sleep,time
import datetime
import logging,os
import sys

# Performs a standard calibration of the PPM
def runCalibration (instrAddress=None, calPath=None, ppmAddress=None, logLevel="warning", calAction=None):

    try:

        # Process parameters
        if (calPath is None):
            calPath = os.getcwd()
        if (os.path.isdir(calPath) == False):
            raise ValueError ("Supplied calibration path is invalid: " + calPath)
        # Use current directory if none is specified
        if (calPath is None):
            calPath = os.getcwd()
            print ("No output folder specified, using: " + calPath)

        #check log file is present or writeable
        numeric_level = getattr(logging, logLevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)              
    
        # Display the app title to the user
        displayCalInstruction ("open_hd")

        # If no address specified, the user must select the module to calibrate
        if (ppmAddress == None):        
            # Request user to select the (QTL1999) PPM to calibrate
            print ("")
            print ("Please select a Quarch Power Module:")
            print ("")
            ppmAddress = userSelectDevice (scanFilterStr = ["QTL1999","QTL1995","QTL1944"])
            if (ppmAddress == 'quit'):
                sys.exit ("Exiting, on user instruction")     
        # verify ip address here?
        else:
            ppmAddress = "REST:" + ppmAddress

        myPpmDevice = quarchDevice(ppmAddress)
            

        # main execution loop
        # calAction is always cleared at the end of this loop, once the action has been completed
        while(True):

            # If no calibration action is selected, request one
            if (calAction == None):
                calAction = displayCalInstruction ("select_action")
            if (calAction == 'quit'):
                sys.exit ("Exiting, on user instruction")

            # If no address specified, the user must select the module to calibrate
            if ('select' in calAction) or (ppmAddress == None):        
                # Request user to select the (QTL1999) PPM to calibrate
                print ("")
                print ("Please select a Quarch Power Module:")
                print ("")
                ppmAddress = userSelectDevice (scanFilterStr = ["QTL1999","QTL1995","QTL1944"])
                if (ppmAddress == 'quit'):
                    sys.exit ("Exiting, on user instruction")
                else:
                    myPpmDevice = quarchDevice(ppmAddress)

            # If a read is requested
            if ('read' in calAction):

                # create Power Module Object
                ppm = HDPowerModule(myPpmDevice)
                
                savedCalibration = ppm.readCalibration()

            elif ('write' in calAction):

                # create Power Module Object
                ppm = HDPowerModule(myPpmDevice)

                ppm.writeCalibration(savedCalibration)

            elif ('calibrate' in calAction) or ('verify' in calAction):

                # If no calibration instrument is provided, request it
                while(True):
                    if (instrAddress == None):
                        print("")
                        instrAddress = userSelectCalInstrument (scanFilterStr = "keithley")
                        if (instrAddress == 'quit'):
                            sys.exit ("Exiting, on user instruction")
                    try:
                        # Connect to the calibration instrument
                        myCalInstrument = keithley2460 (instrAddress)
                        # Open the connection
                        myCalInstrument.openConnection ()
                        break
                    # In fail, allow the user to try again with a new selection
                    except:
                        print ("Unable to communicate with selected instrument!")
                        print("")         
                        instrAddress = None

                # Creates the calibration header information object and populates it with all basic information
                calHeader = CalibrationHeaderInformation()
                populateCalHeader_Keithley(calHeader, myCalInstrument)
                populateCalHeader_HdPpm(calHeader, myPpmDevice, calAction)
                populateCalHeader_System(calHeader)

                # Verify the Quarch module is an HD
                if ('QTL1944' not in calHeader.quarchInternalSerial):
                    sys.exit("ERROR - The attached quarch module is not a valid HD power module")

                # open report for writing
                fileName = calPath + "\\" + calHeader.quarchInternalSerial + " " + datetime.datetime.now().strftime("%d-%m-%y %H-%M" + ".txt")
                print("\nReport file: " + fileName)
                reportFile = open(fileName,"a+")
    
                # If a calibration is requested
                if ('calibrate' in calAction):                
                    # create Power Module Object
                    ppm = HDPowerModule(myPpmDevice)

                    report = ppm.calibrate(myCalInstrument,reportFile)

                # If a verify is required
                if ('verify' in calAction):           
                    # create Power Module Object
                    ppm = HDPowerModule(myPpmDevice)

                    report= ppm.verify(myCalInstrument,reportFile)

                # Close all instruments
                myCalInstrument.closeConnection()
                myPpmDevice.closeConnection()        

                # Create structure to hold module results
                #moduleResults = ModuleResultsInformation ()
                #moduleResults.calibrationHeader = calHeader
                # Loop through the calibration channels and get their results
                #for channel in ppm.calibrations:
                #    moduleResults.channelResults.append (channel.report())
                # TODO: Now export the final reports to file
                #ModuleResultsInformation.saveTextReport (calPath)        

                reportFile.close()

            # End of Loop - clear action so we are prompted to chose another
            calAction = None
    
    except Exception as thisException:
        try:
            myCalInstrument.setLoadCurrent(0)
        # Handle case where exception may have been thrown before instrument was set up
        except:
            pass
        logging.error(thisException)
        raise thisException
        #pass

# CalUtil --ppm USB:1999 --instr 192.168.1.21 --calpath c:\CalData --action calibrate
#
#
if __name__ == "__main__":
    import argparse
    # Handle expected command line arguments here using a flexible parsing system
    parser = argparse.ArgumentParser(description='Calibration utility parameters')
    parser.add_argument('-a', '--action', help='Calibration action to perform', choices=['calibrate', 'verify'], type=str.lower)
    parser.add_argument('-m', '--module', help='IP Address or netBIOS name of power module to calibrate', type=str.lower)
    parser.add_argument('-i', '--instr', help='IP Address or netBIOS name of calibration instrument', type=str.lower)
    parser.add_argument('-p', '--path', help='Path to store calibration logs', type=str.lower)    
    parser.add_argument('-l', '--logging', help='Level of logging to report', choices=['warning', 'error', 'debug'], type=str.lower,default='warning') 
    args = parser.parse_args()
    
    # Call the main calibration function, passing the provided arguments
    runCalibration(instrAddress = args.instr, calPath = args.path, ppmAddress = args.module, logLevel = args.logging, calAction = args.action)
