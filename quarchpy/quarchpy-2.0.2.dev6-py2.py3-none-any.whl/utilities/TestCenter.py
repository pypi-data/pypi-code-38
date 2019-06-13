#!/usr/bin/python

#import testCenter
from inspect import getframeinfo, stack
import sys

# Runs an interface setup function
def setup (commandName, *commandParams):	
    caller = getframeinfo(stack()[1][0])

    # Write the command and params to STDOUT
    sys.stdout.write ("SETUP," + str(caller.filename) + "," + str(caller.lineno) + "," + commandName + ",")
    for index, item in enumerate(commandParams):
        if (index < len(commandParams)-1):
            sys.stdout.write ("\"" + item + "\"" + ",")
        else:
            sys.stdout.write ("\"" + item)

    sys.stdout.write ("\n")
    sys.stdout.flush()

    # Read the response from STDIN
    return sys.stdin.readline().strip();
	
# Runs an interface setup function
def testPoint (commandName, *commandParams):	
    caller = getframeinfo(stack()[1][0])

    # Write the command and params to STDOUT
    sys.stdout.write ("TEST," + str(caller.filename) + "," + str(caller.lineno) + "," + commandName + ",")
    for x in commandParams:
        sys.stdout.write ("\"" + x + "\"" + ",")

    sys.stdout.write ("\n")
    sys.stdout.flush()

    # Read the response from STDIN
    return sys.stdin.readline().strip();
	
# Ends the test sequence
def endTest():
    caller = getframeinfo(stack()[1][0])

    sys.stdout.write ("ENDTEST," + str(caller.filename) + "," + str(caller.lineno));
    sys.stdout.write ("\n");
    sys.stdout.flush()
	
# Starts a block of tests that will be reported together
def beginTestBlock (messageText):
    caller = getframeinfo(stack()[1][0])

    # Write the command and params to STDOUT
    sys.stdout.write ("BLOCK_START," + str(caller.filename) + "," + str(caller.lineno) + "," + "\"" + messageText + "\"")
    sys.stdout.write ("\n")
    sys.stdout.flush()

    # Read the response from STDIN
    return sys.stdin.readline().strip()
	
# Finishes the current test block
def endTestBlock ():
    caller = getframeinfo(stack()[1][0])

    # Write the command and params to STDOUT
    sys.stdout.write ("BLOCK_END," + str(caller.filename) + "," + str(caller.lineno) + "," + "\"")
    sys.stdout.write ("\n")
    sys.stdout.flush()

    # Read the response from STDIN
    return sys.stdin.readline().strip()
