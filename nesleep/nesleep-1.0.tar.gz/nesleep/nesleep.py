import sys
import subprocess  
import logging

printMessage = False

def disableSleep(sleep = '1', prnt = True):
    global printMessage
    printMessage = prnt

    #Fetching the value of sleep when directly called from terminal
    try:
        sleep = sys.argv[1]
    except:
        pass 

    #Finally, executing command & printing out the appropriate message ;)
    if sleep == '1':
        subprocess.call(['sudo', 'pmset', '-a', 'sleep', '0'])
        subprocess.call(['sudo', 'pmset', '-a', 'disablesleep', '1'])
        printIt("Your computer won't sleep now. Cheers 🍻")
    elif sleep == '0':
        subprocess.call(['sudo', 'pmset', '-a', 'sleep', '1'])
        subprocess.call(['sudo', 'pmset', '-a', 'disablesleep', '0'])
        printIt("Your computer can now have a sleep 😄")
    else:
        printIt("Incorrect input. Please use '0' to enable, and '1' to disable the sleep :)")
        return

def sleep(sleep):
    disableSleep(str(int(not sleep)), False)
    
def printIt(text):
    #Printing the messages only when the lib is not imported
    if printMessage:
        print(text)