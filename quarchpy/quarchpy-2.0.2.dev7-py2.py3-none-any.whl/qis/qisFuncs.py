import os, sys 
#import inspect 
import time, platform 
from quarchpy.connection_specific.connection_QIS import QisInterface 
import subprocess 

def isQisRunning(): 
 
    qisRunning = False
    myQis = None
    
    #attempt to connect to Qis
    try:
        myQis = QisInterface()
        if (myQis is not None):
            #if we can connect to qis, it's running
            qisRunning = True 
    except:
        #if there's no connection to qis, an exception will be caught
        pass    
     
    if (qisRunning is False): 
        return False 
    else:
        return True
 
def startLocalQis(): 
 
    QisPath =os.path.dirname(os.path.abspath(__file__))
    QisPath,junk = os.path.split (QisPath)
    QisPath = os.path.join(QisPath, "connection_specific", "QIS", "qis.jar") 

    #find file path and change directory to Qis Location    
    current_direc = os.getcwd() 
    os.chdir(os.path.dirname(QisPath))     
    command = "-jar \"" + QisPath + "\"" 

    #different start for different OS 
    currentOs = platform.system()  
    if (currentOs == "Windows"): 
        command = "start /high /b javaw " + command 
        os.system(command) 
    elif (currentOs == "Linux"):
        if sys.version_info[0] < 3:
            os.popen2("java " + command)
        else:
            os.popen("java " + command)
    else: 
        command = "start /high /b javaw " + command 
        os.system(command)

    #Qis needs a small time for startup
    time.sleep(2)

    #see if new instance of qis has started
    while not isQisRunning():
        time.sleep(0.1)
        pass
    
    #change directory back to start directory 
    os.chdir(current_direc) 
    
    try: 
        startLocalQis.func_code = (lambda:None).func_code 
    except: 
        startLocalQis.__code__ = (lambda:None).__code__  


def closeQis(host='127.0.0.1', port=9722):
    myQis = QisInterface(host, port)
    myQis.sendAndReceiveCmd(cmd = "$shutdown")
    
def GetQisModuleSelection (QisConnection):
    
    # Request a list of all USB and LAN accessible power modules
    devList = QisConnection.getDeviceList()
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
 
 
