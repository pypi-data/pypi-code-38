import os, sys 
import datetime
import time, platform 
from quarchpy.qis import isQisRunning, startLocalQis
from quarchpy.connection_specific.connection_QIS import QisInterface 
from quarchpy.connection_specific.connection_QPS import QpsInterface 
import subprocess 

def isQpsRunning(host='127.0.0.1', port=9822):    
    answer = "0"
    try:
        myQps = QpsInterface(host, port)
        answer = myQps.sendCmdVerbose(cmd = "$list")
    except:
        pass           
    
    if answer[0] == "1":
        return True
    else:
        return False
 

def startLocalQps(keepQisRunning=True):
    
    if keepQisRunning:
        if not isQisRunning():
            startLocalQis()
    
    QpsPath =os.path.dirname(os.path.abspath(__file__))
    QpsPath,junk = os.path.split (QpsPath)
    QpsPath = os.path.join(QpsPath, "connection_specific", "QPS", "qps.jar")     
    
    current_direc = os.getcwd()
    
    os.chdir(os.path.dirname(QpsPath))
    
    command = "-jar \"" + QpsPath + "\"" 
    
    currentOs = platform.system() 
    
    if (currentOs is "Windows"):
        command = "start /high /b javaw -Djava.awt.headless=true " + command
        os.system(command)
    elif (currentOs in "Linux"):
        if sys.version_info[0] < 3:
            os.popen2("java " + command + " 2>&1")
        else:
            os.popen("java " + command + " 2>&1")
    else:
        command = "start /high /b javaw -Djava.awt.headless=true " + command
        os.system(command)
     
    
    while not isQpsRunning():
        time.sleep(0.1)
        pass
    
    os.chdir(current_direc)
 
def closeQps(host='127.0.0.1', port=9822): 
    myQps = QpsInterface(host, port) 
    myQps.sendCmdVerbose("$shutdown") 
    del myQps 
    
def GetQpsModuleSelection (QpsConnection):
    
    # Request a list of all USB and LAN accessible power modules
    devList = QpsConnection.getDeviceList()
    # Removes rest devices
    devList = [ x for x in devList if "rest" not in x ]

    # Print the devices, so the user can choose one to connect to
    print ("\n ########## STEP 1 - Select a Quarch Module. ########## \n")
    print (' --------------------------------------------')
    print (' |  {:^5}  |  {:^30}|'.format("INDEX", "MODULE"))
    print (' --------------------------------------------')
        
    try:
        for idx in xrange(len(devList)):
            print (' |  {:^5}  |  {:^30}|'.format(str(idx+1), devList[idx]))
            print(' --------------------------------------------')
    except:
        for idx in range(len(devList)):
            print (' |  {:^5}  |  {:^30}|'.format(str(idx+1), devList[idx]))
            print(' --------------------------------------------')

    # Get the user to select the device to control
    try:
        moduleId = int(raw_input ("\n>>> Enter the index of the Quarch module: "))
    except NameError:
        moduleId = int(input ("\n>>> Enter the index of the Quarch module: "))

    # Verify the selection
    if (moduleId > 0 and moduleId <= len(devList)):
        myDeviceID = devList[moduleId-1]
    else:
        myDeviceID = None

    return myDeviceID
    
'''
Legacy function to handle old scripts which call an adjustTime function to get QPS format time.
This is now done in the QPS module level, so this function returns a integer linux millisecond value
as per the old one
'''
def legacyAdjustTime(timestamp):
    return timestamp
 
'''
Simple function to convert a timestamp or Python datetime object into QPS format time
QPS requires time in mS with no decimal point, so this is converted here
'''
def toQpsTimeStamp(timestamp):
    # Python datetime object
    if (type(timestamp) is datetime):
        newTime = time.mktime(timestamp.timetuple())
        return int(newTime * 1000)
    # If numeric, assume standard unix time in milliseconds
    elif (type(timestamp) is float or type(timestamp) is int):        
        return int(timestamp)
    else:
        # Try if its a numeric value string first (assumed to be milliseconds)
        try:
            timestamp = float(timestamp)
            return int(timestamp)
        # Fall back to assuming a standard format time string
        except:
            newTime = time.mktime(datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S:%f").timetuple())
            return int(newTime * 1000)