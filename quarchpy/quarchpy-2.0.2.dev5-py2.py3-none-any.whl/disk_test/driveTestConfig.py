#!/usr/bin/env python
'''
This file contains global setup variables and similar, required for use across multiple modules


########### VERSION HISTORY ###########

03/01/2019 - Andy Norrie		- First Version

########### INSTRUCTIONS ###########

N/A

####################################
'''

'''
Defines a dictionary to hold test callback function.  These allow test points to access 'standard' functions, some of which can be user defined
'''
testCallbacks = {}

'''
Holds the test resources that are created during 'Setup' operations to allow use of the resource during 'Tests'.
This is a dictionary in the form {nameString:Object} where the nameString is unique and the Object can be
a string, quarchDevice or any similar object used as a resource during testing
'''
testResources = {}

'''
Setting to specify the level of debug logging and display
'''
logDebugMessagesInFile=True
logDebugMessagesOnTerminal=True

'''
Settings for current GUI
'''
guiAddress="localhost"
guiPort=9921