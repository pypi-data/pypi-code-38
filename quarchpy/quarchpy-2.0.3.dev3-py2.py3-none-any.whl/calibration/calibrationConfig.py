#!/usr/bin/env python
'''
This file contains global setup variables and similar


########### VERSION HISTORY ###########

11/04/2019 - Andy Norrie		- First Version

########### INSTRUCTIONS ###########

N/A

####################################
'''

'''
Holds the test resources that are created during setup operations to allow use of the resource during the calibration.
This is a dictionary in the form {nameString:Object} where the nameString is unique and the Object can be
a string, quarchDevice or any similar object used as a resource during testing
'''
calibrationResources = {}

'''
Setting to specify the level of debug logging and display
'''
logDebugMessagesOnTerminal=True