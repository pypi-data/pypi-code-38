import os
from openProduction.common import Signals

class TestParams:
    DEVICE_ID = "deviceID"
    def __init__(self, params, folder):
        self._params = params
        self._paramFolder = folder
        self._files = []
        self.keyChanged = Signals.Signal()
        self.deviceIDSet = Signals.Signal()
        
    def __getitem__(self, key):       
        return self._params[key]
    
    def __setitem__(self, key, value):
        self._params[key] = value
        self.keyChanged.emit(key, value)
        if key == self.DEVICE_ID:
            self.deviceIDSet.emit(value)
        
    def __contains__(self, key):
        return key in self._params
    
    def move(self, key):
        params = {}
        if self.DEVICE_ID in self._params:
            devID = self._params[self.DEVICE_ID]
            self._params.pop(self.DEVICE_ID, None)
        else:
            devID = None
        
        params[key] = self._params
        self._params = params
        if devID != None:
            self._params[self.DEVICE_ID] = devID
            

    def setDeviceID(self, val):
        self._params[self.DEVICE_ID] = val
        self.deviceIDSet.emit(val)
        
    def getDeviceID(self):
        return self._params[self.DEVICE_ID]
    
    def clear(self):
        self._params = {}
        self._files = []
    
    def abspath(self, key):
        if self._paramFolder != None:
            return os.path.join(self._paramFolder, self._params[key])
        else:
            return self._params[key]
    
    def addFile(self, fileName):
        fName = os.path.abspath(fileName)
        if fName in self._files:
            return False
        self._files.update(fName)
        return True
    
    def getParams(self):
        return self._params
    
    def getFiles(self):
        return self._files
    
    def __len__(self):
        return len(self._params)
    
    def __str__(self):
        MAX_LEN = 40
        
        maxName = len("Name")
        maxValue = len("Value")
        
        for key, val in self._params.items():
            if type(val) == type({}):
                for subKey, subVal in val.items():
                    subKey = key+"."+subKey
                    maxName = max(maxName, len(subKey))
                    maxValue = max(maxValue, len(str(subVal)))
            else:
                maxName = max(maxName, len(key))
                maxValue = max(maxValue, len(str(val)))
            
        if maxName > MAX_LEN:
            maxName = MAX_LEN
        if maxValue > MAX_LEN:
            maxValue = MAX_LEN
            
        colName = maxName+2
        colVal = maxValue+2
        
        myStr = ""
        myStr += ("+"+"-"*colName + "+" + "-"*colVal + "+") + "\n"
        myStr += ("| Name " + " "*(colName-6) + "| Value " + " "*(colVal-7) + "|") + "\n"
        myStr += ("+"+"="*colName + "+" + "="*colVal + "+") + "\n"
        
        def toStrKeyVal(key,val):
            myStr = ""
            printKey = key
            if len(printKey)>MAX_LEN:
                printKey = printKey[:MAX_LEN-3]+"..."
            printVal = str(val)
            if len(printVal)>MAX_LEN:
                printVal = printVal[:MAX_LEN-3]+"..."
                
            myStr += ("| " + printKey + " "*(colName-len(printKey)-1) + "| " +
                      str(printVal) +" "*(colVal-len(str(printVal))-1) + "|" ) + "\n"
            myStr += ("+"+"-"*colName + "+" + "-"*colVal + "+") + "\n"
            return myStr
        
        for key, val in self._params.items():
            if type(val) == type({}):
                for subKey, subVal in val.items():
                    subKey = key+"."+subKey
                    myStr += toStrKeyVal(subKey, subVal)
            else:
                myStr += toStrKeyVal(key, val)
        return myStr    