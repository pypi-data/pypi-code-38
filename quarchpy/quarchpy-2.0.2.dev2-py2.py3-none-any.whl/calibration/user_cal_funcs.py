'''
General functions to help the user perform a calibration
'''

import quarchpy
from quarchpy.calibration.deviceHelpers import locateMdnsInstr

'''
Function to print useful sections of standard calibration text to the user
'''
def displayCalInstruction (instructionName):

    # Print the header for HD module calobration
    if (instructionName.lower() == "open_hd"):
        print ("")
        print ("********************************************************")
        print ("Quarch Technology Calibration System")
        print ("(C) 2019, All rights reserved")
        print ("")
        print ("V" + quarchpy.calibration.calCodeVersion)
        print ("")
        print ("********************************************************")
        print ("")
        print ("Calibration process for QTL1999 HD Power Modules")
        print ("")
        print ("********************************************************")
        print ("")
        print ("")

    # Print and return the selection for calibration action
    elif (instructionName.lower() == "select_action"):        
        print ("")
        print ("Please select the action(s) to perform")
        print ("")
        print ("1 - Read calibration data from the power module to disk")
        print ("2 - Write calibration data from disk to the power module")
        print ("3 - Calibrate the power module")
        print ("4 - Verify existing calibration on the power module")
        print ("5 - Select a different power module")
        print ("")
        print ("q - Quit")
        print ("")
        while(True):
            selection = input ("Enter Selection: ")
            if (selection == "1"):
                return "read"
            if (selection == "2"):
                return "write"
            elif (selection == "3"):
                return "calibrate|verify"
            elif (selection == "4"):
                return "verify"
            elif (selection == "5"):
                return "select"
            elif (selection == "q"):
                return "quit"
            else:
                print ("INVALID SELECTION!")

    # Print and return the calibration instrument selection
    elif (instructionName.lower() == "select_instrument"):
        while(True):
            foundDevices = locateMdnsInstr ("keithley")
            print ("")

            print ("Calibration instruments available:")
            print ("")
            
            # if we found devices, list them
            if (len(foundDevices) > 0):
                count = 1
                for k, v in foundDevices.items():
                    print (str(count) + " - " + k + "\t" + v)
                    count += 1
            # else print nothing found
            else:
                print ("No Calibration Instruments found")
            print ("")
            print ("r - Rescan for instruments")
            print ("m - Manually enter IP address")
            print ("q - Quit")
            print ("")

            while(True):
                userValue = input ("Enter Selection: ")
            
                # Validate as an int
                try:
                    userNumber = int(userValue)
                    if (userNumber > len(foundDevices) or userNumber < 1):
                        raise ValueError ()
                    else:
                        break
                except:
                    if (userValue == 'q' or userValue == 'r' or userValue == 'm'):
                        break
                    else:
                        print ("INVALID SELECTION!")
        
            if (userValue == 'q'):
                return "quit"
            elif (userValue == 'r'):
                pass
            elif (userValue == 'm'):
                return input ("Enter IP address: ")
            else:
                # Return the address string of the selected instrument
                return list(foundDevices)[userNumber - 1]            
    else:
        raise ValueError ("Unknown instruction for display: " + instructionName)