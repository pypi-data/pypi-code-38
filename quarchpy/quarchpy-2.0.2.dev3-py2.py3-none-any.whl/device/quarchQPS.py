from .device import quarchDevice
from quarchpy.qps import toQpsTimeStamp
import os, time, datetime, sys

current_milli_time = lambda: int (round (time.time() * 1000))
current_second_time = lambda: int (round (time.time()))

# Using standard Unix time,  milliseconds since the epoch (midnight 1 January 1970 UTC)
# Should avoid issues with time zones and summer time correction but the local and host
# clocks should still be synchronised
def qpsNowStr():
    return current_milli_time()                          # datetime supports microseconds


class quarchQPS(quarchDevice):
    def __init__(self, quarchDevice):

        self.quarchDevice = quarchDevice
        self.ConType = quarchDevice.ConType
        self.ConString = quarchDevice.ConString

        self.connectionObj = quarchDevice.connectionObj
        self.IP_address = quarchDevice.connectionObj.qps.host
        self.port_number = quarchDevice.connectionObj.qps.port

    def getCanStream(self):
        streamableDevices = ["qtl1824", "qtl1847", "qtl1944", "qtl1995", "qtl1999"]

        startPos  = self.ConString.index("q")
        for  item in streamableDevices:
            tmp = str(self.ConString[startPos:startPos+7])
            if (tmp == str(item)):
                return True
        return False

    def startStream(self, directory):
        if not self.getCanStream():
            print ("This device does not support streaming.")
            return
        else:
            return quarchStream(self.quarchDevice, directory)
    

class quarchStream(quarchQPS):
    def __init__(self, quarchQPS, directory):
        self.connectionObj = quarchQPS.connectionObj
        
        self.IP_address = quarchQPS.connectionObj.qps.host
        self.port_number = quarchQPS.connectionObj.qps.port

        self.ConString = quarchQPS.ConString
        self.ConType = quarchQPS.ConType
        
        time.sleep(1)
      
        #check to see if any invalid file entries
        newDirectory = self.failCheck(directory)
        
    def failCheck(self, newDirectory):
        validResponse = False

        while (validResponse == False):
            #send the command to start stream
            response = self.connectionObj.qps.sendCmdVerbose( "$start stream " + str(newDirectory))
            #if the stream fails, loop until user enters valid name
            if "Fail" in response:
                print (response + ", Please enter a new file name:")
                #grab directory bar end file / folder
                path = os.path.dirname(newDirectory)
                #get a new file name
                if sys.version_info.major==3:                    
                    newEnd = input()
                else:
                    newEnd = raw_input()
                #append user input to directory
                newDirectory = path.replace("\\\\","\\") + newEnd
            else:
                validResponse = True;
        return newDirectory

        
    def addAnnotation(self, annotationString, annotaionTime = 0):
        if annotaionTime == 0:
            # Use current time
            annotaionTime = qpsNowStr()
        else:
            # Convert timestamp to QPS format
            annotaionTime = toQpsTimeStamp (annotaionTime)            

        #replacing invalid chars for xml
        if annotationString.startswith("<<"):
            annotationString = annotationString.replace("\n","\\n")

        return self.connectionObj.qps.sendCmdVerbose("$annotate " + str(annotaionTime) + " " + annotationString)

    def addComment(self, commentString, commentTime = 0 ):
        if commentTime == 0:
            commentTime = qpsNowStr()
        else:
            # Convert timestamp to QPS format
            commentTime = toQpsTimeStamp (commentTime)

        #replacing invalid chars for xml
        if commentString.startswith("<<"):
            commentString = commentString.replace("\n","\\n")

        return self.connectionObj.qps.sendCmdVerbose("comment " + str(commentTime) + " " + commentString)


    def createChannel(self, channelName, channelGroup, baseUnits, usePrefix):
        #Conditions to convert false / true inputs to specification input
        if usePrefix == False: 
            usePrefix = "no"
        if usePrefix == True:
            usePrefix = "yes"

        return self.connectionObj.qps.sendCmdVerbose("$create channel " + channelName + " " + channelGroup  + " " + baseUnits + " " + usePrefix)

    def hideChannel(self, channelSpecifier):
        return self.connectionObj.qps.sendCmdVerbose("$hide channel " + channelSpecifier)

    def showChannel(self, channelSpecifier):
        return self.connectionObj.qps.sendCmdVerbose("$show channel " + channelSpecifier)

    def myChannels(self):
        return self.connectionObj.qps.sendCmdVerbose("$channels")

    def channels(self):
        return self.connectionObj.qps.sendCmdVerbose("$channels").splitlines()
             
    def stopStream(self):
        return self.connectionObj.qps.sendCmdVerbose("$stop stream")

    def hideAllDefaultChannels(self):
        self.hideChannel ("3v3:voltage")
        self.hideChannel ("5v:voltage")
        self.hideChannel ("12v:voltage")
        self.hideChannel ("3v3:current")
        self.hideChannel ("5v:current")
        self.hideChannel ("12v:current")
        self.hideChannel ("3v3:power")
        self.hideChannel ("5v:power")
        self.hideChannel ("12v:power")
        self.hideChannel ("tot:power")
            

    #function to add a data point the the stream
    #time value will default to current time if none passed
    def addDataPoint(self, channelName, groupName, dataValue, dataPointTime = 0):
        if dataPointTime == 0:
            dataPointTime = qpsNowStr()
        else:
            dataPointTime = toQpsTimeStamp (dataPointTime)

        #print ("printing command:  $log " + channelName + " " + groupName + " " + str(dataPointTime) + " " + str(dataValue))
        self.connectionObj.qps.sendCmdVerbose("$log " + channelName + " " + groupName + " " + str(dataPointTime) + " " + str(dataValue))