#!/usr/bin/env python
'''
This example demonstrates the use of Quarch Drive Test Suite functions to create a set of tests

- Tests can be run directly, or parsed from a CSV file
- Test callbacks can be overridden by the user and modified to add additional functionality

########### VERSION HISTORY ###########

20/09/2018 - Andy Norrie		- First Version

########### INSTRUCTIONS ###########

1- Run the script and follow the instructions on screen

####################################
'''


# Import standard test functions
import driveTestCore
# Import configuration and globals
import driveTestConfig
from driveTestConfig import testCallbacks
# Import hot-plug tests (needed for function based example)
import hotPlugTest
from quarchpy.device import scanDevices

'''
Main function, containing the example code
'''
def main():

    '''
    Setup the callback functions used by the tests, for logging and checking drive function
    This currently uses the standard provided functions, can cab be altered by the user
    '''
    driveTestConfig.testCallbacks = {"TEST_LOG": driveTestCore.notifyTestLogEventXml,
                     "TEST_GETDISKSTATUS": driveTestCore.DiskStatusCheck,
                     "UTILS_VISUALSLEEP": driveTestCore.visualSleep,
                     "TEST_GETRESOURCE": driveTestCore.getTestResource,
                     "TEST_SETRESOURCE": driveTestCore.setTestResource}

    # Display title text
    print("\n################################################################################")
    print("\n                           QUARCH TECHNOLOGY                        \n\n  ")
    print("Automated Drive/Host test suite.   ")
    print("\n################################################################################\n")  
           
    '''
    Example: Run a set of specific test points from the script
    Commented out by default, comment in if desired
    '''
    #ExampleTests()

    #def ActivateRemoteServer(portNumber=9742, connectLocal = False):
    driveTestCore.ActivateRemoteServer()
    #driveTestCore.ActivateRemoteServer(localHost = False)


    '''
    Example: Run all test points in the given CSV file
    '''
    #driveTestCore.executeCsvTestFile(testCallbacks, ".\CSV_test_1.csv")


def ExampleTests():
    print(scanDevices("all",scanInArray=True))

    # Specify the module and drive to work with
    driveTestCore.specifyQuarchModule ("USB:QTL1743-03-392", "quarchModule1")
    #driveTestCore.specifyDriveById ("PCI:0:01.2", "testDrive1")
    quarchDevice = driveTestConfig.testCallbacks["TEST_GETRESOURCE"] ("quarchModule1")    

    # Run a sweep of hot-plug times in 5 steps
    #unhIolHotPlugSimpleSweep (testCallbacks, quarchModules["quarchModule1"], drivesList["testDrive1"], "10mS", "1S", 5, 10)

    hotPlugTest.executeAndCheckCommand (quarchDevice, "sig:all:sour 1")
    hotPlugTest.executeAndCheckCommand (quarchDevice, "sig:all:sour 2")
    hotPlugTest.executeAndCheckCommand (quarchDevice, "sig:all:sour 3")
    hotPlugTest.executeAndCheckCommand (quarchDevice, "conf:def state")
    hotPlugTest.executeAndCheckCommand (quarchDevice, "sig:all:sour 4")
    
if __name__ == "__main__":
    main()
