import socket
import re
import time
import sys
import os
import datetime
import select
import threading
import math

#QisInterface provides a way of connecting to a Quarch backend running at the specified ip address and port, defaults to localhost and 9722
class QisInterface:
    def __init__(self, host='127.0.0.1', port=9722):
        self.host = host
        self.port = port
        self.maxRxBytes = 4096
        self.sock = None
        self.StreamRunSentSemaphore = threading.Semaphore()
        self.sockSemaphore = threading.Semaphore()
        self.stopFlagList = []
        self.listSemaphore = threading.Semaphore()
        self.deviceList = []
        self.deviceDict = {}
        self.dictSemaphore = threading.Semaphore()
        self.connect()
        self.stripesEvent = threading.Event()
        
        self.streamSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.streamSock.connect((self.host, self.port))
        self.streamSock.settimeout(5)
        self.pythonVersion = sys.version[0]
        #self.sendText(self.streamSock, '$scan')
        #time.sleep(3)
        if self.pythonVersion == '3':
            temp = '>'
            self.cursor = temp.encode()
        else:
            self.cursor = '>'
        #clear packets
        try:
            welcomeString = self.streamSock.recv(self.maxRxBytes).rstrip()
        except:
            raise

    # Connect() tries to open a socket  on the host and port specified in the objects variables
    # If successful it returns the backends welcome string. If it fails it returns a string saying unable to connect
    # The backend should be running and host and port set before running this function. Normally it should be called at the beggining
    # of talking to the backend and left open until finished talking when the disconnect() function should be ran
    def connect(self):
        try:
            self.deviceDictSetup('QIS')
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.sock.settimeout(5)
            #clear packets
            try:
                welcomeString = self.sock.recv(self.maxRxBytes).rstrip()
                welcomeString = 'Connected@' + str(self.host) + ':' + str(self.port) + ' ' + '\n    ' + str(welcomeString)
                self.deviceDict['QIS'][0:3] = [False, 'Connected', welcomeString]
                return welcomeString
            except:
                print('')
                print('No welcome received. Unable to connect to Quarch backend on specified host and port (' + self.host + ':' + str(self.port) + ')')
                print('Is backend running and host accessible?')
                print('')
                self.deviceDict['QIS'][0:3] = [True, 'Disconnected', 'Unable to connect to QIS']
                raise
        except:
            self.deviceDictSetup('QIS')
            print('')
            print('Unable to connect to Quarch backend on specified host and port (' + self.host + ':' + str(self.port) + ').')
            print('Is backend running and host accessible?')
            print('')
            self.deviceDict['QIS'][0:3] = [True, 'Disconnected', 'Unable to connect to QIS']
            raise
    
    # Tries to close the socket to specified host and port.
    def disconnect(self):
        res = 'Disconnecting from backend'
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
            self.deviceDict['QIS'][0:3] = [False, "Disconnected", 'Successfully disconnected from QIS']
        except:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            message = 'Unable to end connection. ' + self.host + ':' + str(self.port) + ' \r\n' + str(exc_type) + ' ' + str(fname) + ' ' + str(exc_tb.tb_lineno)
            self.deviceDict['QIS'][0:3] = [True, "Connected", message]
            raise
        return res

    def getCanStream(self, module):
        streamableDevices = ["qtl1824", "qtl1847", "qtl1944", "qtl1995", "qtl1999"]
        for  item in streamableDevices:
            if (str(item) in module):
                return True
        return False

    def startStream(self, module, fileName, fileMaxMB, streamName, streamAverage, releaseOnData, separator):
        if not self.getCanStream(module):
            print ("This device does not support streaming.")
            return
            #Clear the event used for signaling the stream loop to end
        self.StreamRunSentSemaphore.acquire()
        self.deviceDictSetup('QIS')
        i = self.deviceMulti(module)
        self.stopFlagList[i] = True
        self.stripesEvent.set()
        
        
        #Create the thread
        t1 = threading.Thread(target=self.startStreamThread, name=module, args=(module, fileName, fileMaxMB, streamName, streamAverage, releaseOnData, separator))                
        #Start the thread
        t1.start()
        
        #count = 0
        while (self.stripesEvent.is_set()):
            #count += 1                         --debugging to show delay
            pass
            #just wait until event is cleared
        


    def stopStream(self, module, blocking = True):
        try:
            i = self.deviceMulti(module)
            self.stopFlagList[i] = False
            # Wait until the stream thread is finished before returning to user.
            # This means this function will block until the QIS buffer is emptied by the second while 
            # loop in startStreanThread. This may take some time, especially at low averaging but 
            # should gurantee the data won't be lost and QIS buffer is emptied.
            if blocking:
                running = True
                while running:
                    threadNameList = []
                    for t1 in threading.enumerate():
                        threadNameList.append(t1.name)
                    if (module in threadNameList):
                        time.sleep(0.5)
                    else:
                        running = False
            time.sleep(0.1)
        except:
            print('!!!!!!!!!!!!!!!!!!  stopStream exception !!!!!!!!!!!!!!!!!!')
            raise
    
    # This is the function that is ran when t1 is created. It is ran in a seperate thread from 
    # the main application so streaming can happen without blocking the main application from 
    # doing other things. Within this function/thread you have to be very careful not to try 
    # and 'communicate'  with anything from other threads. If you do, you MUST use a thread safe 
    # way of communicating. The thread creates it's own socket and should use that NOT the objects socket
    # (which some of the comms with module functions will use by default).
    def startStreamThread(self, module, fileName, fileMaxMB, streamName, streamAverage, releaseOnData, separator):
        #Create a new socket and connect to back end
        '''
        try:
            streamSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            streamSock.connect((self.host, self.port))
            streamSock.settimeout(5)
            #clear packets
            try:
                welcomeString = streamSock.recv(self.maxRxBytes).rstrip()
            except:
                raise
        except:
            raise
        '''
        #Start module streaming and then read stream data
        try:
            stripes = ['Empty Header']
            #Send stream command so module starts streaming data into the backends buffer
            streamRes = self.sendAndReceiveCmd(self.streamSock, 'rec stream', device=module, betweenCommandDelay = 0)
            #print(streamRes)
            if ('rec stream : OK' in streamRes):
                if (releaseOnData == False):
                    self.StreamRunSentSemaphore.release()
                    self.stripesEvent.clear()
                self.deviceDict[module][0:3] = [False, 'Running', 'Stream Running']
            else:
                self.StreamRunSentSemaphore.release()
                self.deviceDict[module][0:3] = [True, 'Stopped', module + " couldn't start because " + streamRes]
                return
            #If recording to file then get header for file
            if(fileName is not None):
                
                averaging = self.streamHeaderAverage(device=module, sock=self.streamSock)
                count=0
                maxTries=10
                while 'Header Not Available' in averaging:
                    averaging = self.streamHeaderAverage(device=module, sock=self.streamSock)
                    time.sleep(0.1)
                    count += 1
                    if count > maxTries:
                        self.deviceDict[module][0:3] = [True, 'Stopped', 'Header not available']
                        exit()
                version =  self.streamHeaderVersion(device=module, sock=self.streamSock)
                sampleRate = 250000 #adc samples / sec
                stripeRate = sampleRate /  float(averaging) #stripes / sec
                with open(fileName, 'w') as f:
                    timeStampHeader = datetime.datetime.now().strftime("%H:%M:%S:%f %d/%m/%y")
                    formatHeader = self.streamHeaderFormat(device=module, sock=self.streamSock)
                    f.write(str(streamName) + ', ' + str(version) + ', ' + str(module) + ', ' + str(timeStampHeader) + ', avg=' + str(averaging) + ' samples per stripe, stripeRate=' + str(stripeRate) + ' stripes per second\n')
                    formatHeader = formatHeader.replace(", ", separator)
                    f.write(formatHeader + '\n')
            numStripesPerRead = 4096
            maxFileExceeded = False
            openAttempts = 0
            leftover = 0
            remainingStripes = []
            streamOverrun = False
            if streamAverage != None:
                #Matt converting streamAveraging into number
                streamAverage = self.convertStreamAverage(streamAverage)
                
                stripesPerAverage = float(streamAverage) / (float(averaging) * 4e-6)
            isRun = True
            while isRun:
                try:
                    with open(fileName, 'ab') as f:
                        # Until the event threadRunEvent is set externally to this thread, 
                        # loop and read from the stream 
                        i = self.deviceMulti(module)
                        while self.stopFlagList[i] and (not streamOverrun):
                            #now = time.time()
                            streamOverrun, removeChar, newStripes = self.streamGetStripesText(self.streamSock, module, numStripesPerRead)
                            newStripes = newStripes.replace(b' ', str.encode(separator))
                            #print (time.time() - now)
                            if streamOverrun:
                                self.deviceDict[module][0:3] = [True, 'Stopped', 'Device buffer overrun']
                            if (removeChar == -6 and len(newStripes) == 6):
                                isEmpty = False
                            else:
                                isEmpty = True
                            if isEmpty:
                                #Writes in file if not too big else stops streaming
                                statInfo = os.stat(fileName)
                                fileMB = statInfo.st_size / 1048576
                                try:
                                    int(fileMaxMB)
                                except:
                                    continue
                                if int(fileMB) < int(fileMaxMB):
                                    if (releaseOnData == True):
                                        self.StreamRunSentSemaphore.release()
                                        self.stripesEvent.clear()
                                        releaseOnData = False
                                    if(streamAverage != None):
                                        leftover, remainingStripes = self.averageStripes(leftover, stripesPerAverage, newStripes[:removeChar], f, remainingStripes)
                                    else:
                                        f.write(newStripes[:removeChar])
                                else:
                                    maxFileExceeded = True
                                    #print('QisInterface file size exceeded  in loop 1- breaking')
                                    maxFileStatus = self.streamBufferStatus(device=module, sock=self.streamSock)
                                    f.write('Warning: Max file size exceeded before end of stream.\n')
                                    f.write('Unrecorded stripes in buffer when file full: ' + maxFileStatus + '.')
                                    self.deviceDict[module][0:3] = [True, 'Stopped', 'User defined max filesize reached']
                                    break
                            else:
                                # there's no stripes in the buffer - it's not filling up fast - 
                                # sleeps so we don't spam qis with requests (seems to make QIS crash)
                                # it might be clever to change the sleep time accoring to the situation 
                                # e.g. wait longer with higher averaging or lots of no stripes in a row
                                time.sleep(0.1)
                                streamStatus = self.streamRunningStatus(device=module, sock=self.streamSock)
                                if streamOverrun:
                                    #print('QisInterface overrun - breaking')
                                    break
                                elif "Stopped" in streamStatus:
                                    self.deviceDict[module][0:3] = [True, 'Stopped', 'User halted stream']
                                    break
                        #print('Left while 1')
                        self.sendAndReceiveCmd(self.streamSock, 'rec stop', device=module, betweenCommandDelay = 0)
                        if (not streamOverrun) and (not maxFileExceeded):
                            self.deviceDict[module][0:3] = [False, 'Stopped', 'Stream stopped - emptying buffer']
                        # print self.streamBufferStatus(device=module, sock=self.streamSock)
                        if (not maxFileExceeded):
                            #If the backend buffer still has data then keep reading it out
                            #print('Streaming stopped. Emptying data left in QIS buffer to file (' + self.streamBufferStatus(device=module, sock=self.streamSock) + ')')
                            streamOverrun, removeChar, newStripes = self.streamGetStripesText(self.streamSock, module, numStripesPerRead)
                            isEmpty = True
                            if removeChar == -6:
                                if len(newStripes) == 6:
                                    isEmpty = False
                            while isEmpty: # if newStripes has length 6 then it only contains 'eof\r\n'
                                statInfo = os.stat(fileName)
                                fileMB = statInfo.st_size / 1048576
                                try:
                                    int(fileMaxMB)
                                except:
                                    continue
                                if int(fileMB) < int(fileMaxMB):
                                    if(streamAverage != None):
                                        leftover, remainingStripes = self.averageStripes(leftover, stripesPerAverage, newStripes[:removeChar], f, remainingStripes)
                                    else:
                                        newStripes = newStripes.replace(b' ', str.encode(separator))
                                        f.write(newStripes[:removeChar])
                                else:
                                    if not maxFileExceeded:
                                        maxFileStatus = self.streamBufferStatus(device=module,  sock=self.streamSock)
                                        maxFileExceeded = True
                                        self.deviceDict[module][0:3] = [True, 'Stopped', 'User defined max filesize reached']
                                    break
                                #time.sleep(0.01) #reduce speed of loop to stop spamming qis
                                streamOverrun, removeChar, newStripes = self.streamGetStripesText(self.streamSock, module, numStripesPerRead)
                                if removeChar == -6:
                                    if len(newStripes) == 6:
                                        isEmpty = False
                            if maxFileExceeded:
                                f.write('Warning: Max file size exceeded before end of stream.\n')
                                f.write('Unrecorded stripes in buffer when file full: ' + maxFileStatus + '.')
                                print('Warning: Max file size exceeded. Some data has not been saved to file: ' + maxFileStatus + '.')
                                
                        #print('Stripes in buffer now: ' + self.streamBufferStatus(device=module, sock=self.streamSock))
                        
                        if streamOverrun:
                            self.deviceDict[module][0:3] = [True, 'Stopped', 'Device buffer overrun - QIS buffer empty']
                        elif not maxFileExceeded:
                            self.deviceDict[module][0:3] = [False, 'Stopped', 'Stream stopped']
                        time.sleep(0.2)
                        isRun = False
                except IOError as err:
                    #print('\n\n!!!!!!!!!!!!!!!!!!!! IO Error in QisInterface !!!!!!!!!!!!!!!!!!!!\n\n')
                    time.sleep(0.5)
                    openAttempts += 1
                    if openAttempts > 4:
                        print('\n\n!!!!!!!!!!!!!!!!!!!! Too many IO Errors in QisInterface !!!!!!!!!!!!!!!!!!!!\n\n')
                        raise
        except:
            raise

        '''
        #Close streams socket
        try:
            streamSock.shutdown(socket.SHUT_RDWR)
            streamSock.close()
        except:         
            raise
        '''
    
    # Send text and get the backends response. - acts as wrapper to the sendAndReceiveText, intended to provide some extra convenience
    # when sending commands to module (as opposed to back end)
    # If read until cursor is set to True (which is default) then keep reading response until a cursor is returned as the last character of result string
    # After command is sent wait for betweenCommandDelay which defaults to 0 but can be specified to add a delay between commands
    # The objects connection needs to be opened (connect()) before this is used
    def sendCmd(self, device='', cmd='$help', sock=None, readUntilCursor=True, betweenCommandDelay=0.1, expectedResponse = True):
        if sock==None:
            sock = self.sock
        if not (device == ''):
            self.deviceDictSetup(device)
        res =  self.sendAndReceiveText(sock, cmd, device, readUntilCursor)
        time.sleep(betweenCommandDelay)
        #If ends with cursor get rid of it
        if res[-1:] == self.cursor:
            res = res[:-3] #remove last three chars - hopefully '\r\n>'
        time.sleep(0.1)
        return res.decode()
     

    def sendAndReceiveCmd(self, sock=None, cmd='$help', device='', readUntilCursor=True, betweenCommandDelay=0.1):
        if sock==None:
            sock = self.sock
        if not (device == ''):
            self.deviceDictSetup(device)
        if self.pythonVersion == '3':
            res =  self.sendAndReceiveText(sock, cmd, device, readUntilCursor).decode()
        else:
            res =  self.sendAndReceiveText(sock, cmd, device, readUntilCursor)
        time.sleep(betweenCommandDelay)
        #If ends with cursor get rid of it
        if res[-1:] == '>':
            res = res[:-3] #remove last three chars - hopefully '\r\n>'
        return cmd + ' : ' + res
    
    # Send text to the back end then read it's response
    # The objects connection needs to be opened (connect()) before this is used
    # If read until cursor is set to True (which is default) then keep reading response until a cursor is returned as the last character of result string
    def sendAndReceiveText(self, sock, sentText='$help', device='', readUntilCursor=True):
        self.sockSemaphore.acquire()
        try:
            self.sendText(sock, sentText, device)
            if self.pythonVersion == '3':
                res = bytearray()
                res.extend(self.rxBytes(sock))
                #Somtimes we just get one cursor back of currently unknown origins
                #If that happens discard it and read again
                if res[0] == self.cursor:
                    #res[0] = self.rxBytes(sock)
                    print('Only Returned Cursor!!!!!')
                #If create socked fail (between backend and tcp/ip module)
                cba = 'Create Socket Fail'
                if cba.encode() == res[0]:
                    print(res[0].decode())
                cba = 'Connection Timeout'
                if cba.encode() == res[0]:
                    print(res[0].decode())
                #If reading until  a cursor comes back then keep reading until a cursor appears or max tries exceeded
                if readUntilCursor:
                    maxReads = 1000
                    count = 1
                    #check for cursor at end of read and if not there read again
                    while res[-1:] != self.cursor:
                        res.extend(self.rxBytes(sock))
                        count += 1
                        if count >= maxReads:
                            res = ' Count = Error: max reads exceeded before cursor returned\r\n'
                            print(res)
                return res
            else:
                res = self.rxBytes(sock)
                #Somtimes we just get one cursor back of currently unknown origins
                #If that happens discard it and read again
                if res == self.cursor:
                    #print(" CURSOR ONLY")
                    res = self.rxBytes(sock)
                #If create socked fail (between backend and tcp/ip module)
                if 'Create Socket Fail' in res:
                    print(res)
                if 'Connection Timeout' in res:
                    print(res)
                #If reading until  a cursor comes back then keep reading until a cursor appears or max tries exceeded
                if readUntilCursor:
                    maxReads = 1000
                    count = 1
                    #check for cursor at end of read and if not there read again
                    while res[-1:] != self.cursor:
                        res += self.rxBytes(sock)
                        count += 1
                        if count >= maxReads:
                            res = ' Count = Error: max reads exceeded before cursor returned\r\n'
                            print(res)
                return res
                
        except:
            raise
        finally:
            self.sockSemaphore.release()

    def rxBytes(self,sock):
        #sock.setblocking(0) #make socket non-blocking
        #print('rxBytes')
        maxExceptions=10
        exceptions=0
        maxReadRepeats=50
        readRepeats=0
        timeout_in_seconds = 10
        #Keep trying to read bytes until we get some, unless number of read repeads or exceptions is exceeded
        while True: 
            try:
                #select.select returns a list of waitable objects which are ready. On windows it has to be sockets.
                #The first arguement is a list of objects to wait for reading, second writing, third 'exceptional condition'
                #We only use the read list and our socket to check if it is readable. if no timeout is specified then it blocks until it becomes readable.
                ready = select.select([sock], [], [], timeout_in_seconds)
                #time.sleep(0.1)
                #ready = [1,2]
                if ready[0]:
                    ret = sock.recv(self.maxRxBytes)
                    time.sleep(0.1)
                    return ret
                else:
                    #print('rxBytes - readRepeats + 1')
                    
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect((self.host, self.port))
                    sock.settimeout(5)

                    try:
                        welcomeString = self.sock.recv(self.maxRxBytes).rstrip()
                        welcomeString = 'Connected@' + self.host + ':' + str(self.port) + ' ' + '\n    ' + welcomeString
                        print('New Welcome:' + welcomeString)
                    except:
                        print('tried and failed to get new welcome')
                        raise
                        
                    readRepeats=readRepeats+1
                    time.sleep(0.5)

            except:
                #print('rxBytes - exceptions + 1')
                raise
                exceptions=exceptions+1
                time.sleep(0.5)
            
            #If read repeats has been exceeded we failed to get any data on this read.
            #   !!! This is likely to break whatever called us !!!
            if readRepeats >= maxReadRepeats:
                print('Max read repeats exceeded - returning.')
                return 'No data received from QIS'
            #If number of exceptions exceeded then give up by exiting
            if exceptions >= maxExceptions:
                print('Max exceptions exceeded - exiting') #exceptions are probably 10035 non-blocking socket could not complete immediatley
                exit()
    
    # Send text to the back end don't read it's response
    # The objects connection needs to be opened (connect()) before this is used
    def sendText(self, sock, message='$help', device=''):
        if device != '':
            specialTimeout =  '%500000'
            message = device + specialTimeout +  ' ' + message
            #print('Sending: "' + message + '" ' + self.host + ':' + str(self.port))
        try:
            if self.pythonVersion == 2:
                sock.sendall(message + '\r\n')
            else:
                convM = message + '\r\n'
                sock.sendall(convM.encode('utf-8'))
            return 'Sent:' + message
        except:
            raise
    
    # Query the backend for a list of connected modules. A $scan command is sent to refresh the list of devices,
    # Then a wait occurs while the backend discovers devices (network ones can take a while) and then a list of device name strings is returned
    # The objects connection needs to be opened (connect()) before this is used
    def getDeviceList(self, sock=None):

        if sock == None:
            sock = self.sock
        scanWait = 2
        #print('Scanning for devices and waiting ' + str(scanWait) + ' seconds.')
        if self.pythonVersion == '3':
            #devString = self.sendAndReceiveText(sock, '$scan').decode
            #time.sleep(scanWait)
            devString = self.sendAndReceiveText(sock, '$list').decode()
        else:
            #devString = self.sendAndReceiveText(sock, '$scan')
            #time.sleep(scanWait)
            devString = self.sendAndReceiveText(sock, '$list')
   
        devString = devString.replace('>', '')            
        devString = devString.replace(r'\d+\) ', '')   

        #print('"' + devString + '"')
        devString = devString.split('\r\n')
        devString = filter(None, devString) #remove empty elements
        return devString

    #
    def GetQisModuleSelection(self):
        deviceList = []
        response = ""

        if self.pythonVersion == '3':
            #devString = self.sendAndReceiveText(sock, '$scan').decode
            #time.sleep(scanWait)
            response = self.sendAndReceiveText(self.sock, '$list').decode()
        else:
            #devString = self.sendAndReceiveText(sock, '$scan')
            #time.sleep(scanWait)
            response = self.sendAndReceiveText(self.sock, '$list')

        response = response.replace('>', '')
        response = response.replace(r'\d+\) ', '')
        # print('"' + devString + '"')
        response = response.split('\r\n')
        #response = self.getDeviceList()
        print("\nList of devices attached to QIS:\n")
        for device in response:
            print(device)

        # Get the user to select the device to control
        try:
            moduleId = int(raw_input("\n>>> Enter the index of the Quarch module: "))
        except NameError:
            moduleId = int(input("\n>>> Enter the index of the Quarch module: "))
        temp = []
        for s in response:
            temp = temp + s.split()
        response = temp
        # check if a response was received and the first char was a digit
        if (len(response) > 0 and response[0].isdigit):

            for  s in response:
                # checks for invalid chars
                if (")" not in s and ">" not in s):
                    # append to list if conditions met
                    deviceList.append(s)

        if (moduleId > 0 and moduleId <= len(deviceList)):
            myDeviceID = deviceList[moduleId - 1]
        else:
            myDeviceID = None

        return myDeviceID




    # Query stream status for a device attached to backend
    # The objects connection needs to be opened (connect()) before this is used
    def streamRunningStatus(self, device, sock=None):
        try:
            if sock == None:
                sock = self.sock        
            index = 0 # index of relevant line in split string
            if self.pythonVersion == '3':
                streamStatus = self.sendAndReceiveText(sock, 'stream?', device).decode()
            else:
                streamStatus = self.sendAndReceiveText(sock, 'stream?', device)
            streamStatus = streamStatus.split('\r\n')
            streamStatus[index] = re.sub(r':', '', streamStatus[index]) #remove :
            return streamStatus[index]
        except:
            raise
    
    # Query stream buffer status for a device attached to backend
    # The objects connection needs to be opened (connect()) before this is used
    def streamBufferStatus(self, device, sock=None):
        try:
            if sock == None:
                sock = self.sock
            index = 1 # index of relevant line in split string
            if self.pythonVersion == '3':
                streamStatus = self.sendAndReceiveText(sock, 'stream?', device).decode()
            else:
                streamStatus = self.sendAndReceiveText(sock, 'stream?', device)
            streamStatus = streamStatus.split('\r\n')
            streamStatus[index] = re.sub(r'^Stripes Buffered: ', '', streamStatus[index])
            return streamStatus[index]
        except:
            raise
    
    # Get the averaging used on the last/current stream
    # The objects connection needs to be opened (connect()) before this is used
    def streamHeaderAverage(self, device, sock=None):
        try:
            if sock == None:
                sock = self.sock
            index = 2 # index of relevant line in split string
            if self.pythonVersion == '3':
                streamStatus = self.sendAndReceiveText(sock, sentText='stream text header', device=device).decode()
            else:
                streamStatus = self.sendAndReceiveText(sock, sentText='stream text header', device=device)
            streamStatus = streamStatus.split('\r\n')
            if('Header Not Available' in streamStatus[0]):
                dummy = streamStatus[0] + '. Check stream has been ran on device.'
                #print(str)
                return dummy
            streamStatus[index] = re.sub(r'^Average: ', '', streamStatus[index])
            avg = streamStatus[index]
            avg = 2 ** int(avg)
            return '{}'.format(avg)
        except:
            print(device + ' Unable to get stream average.' + self.host + ':' + str(self.port))
            raise   
    
    # Get the version of the stream and convert to string for the specified device
    # The objects connection needs to be opened (connect()) before this is used
    def streamHeaderVersion(self, device, sock=None):
        try:
            if sock == None:
                sock = self.sock
            index = 0 # index of relevant line in split string
            if self.pythonVersion == '3':
                streamStatus = self.sendAndReceiveText(sock,'stream text header', device).decode()
            else:
                streamStatus = self.sendAndReceiveText(sock,'stream text header', device)
            streamStatus = streamStatus.split('\r\n')
            if  'Header Not Available' in streamStatus[0]:
                str = streamStatus[0] + '. Check stream has been ran on device.'
                print(str)
                return str
            version = re.sub(r'^Version: ', '', streamStatus[index])
            if version == '3':
                version = 'Original PPM'
            elif version == '4':
                version = 'XLC PPM'
            elif version == '5':
                version = 'HD PPM'
            else:
                version = 'Unknown stream version'
            return version
        except:
            print(device + ' Unable to get stream version.' + self.host + ':' + str(self.port))
            raise
    
    # Get a header string giving which measurements are returned in the string for the specified device
    # The objects connection needs to be opened (connect()) before this is used
    def streamHeaderFormat(self, device, sock=None):
        try:
            if sock == None:
                sock = self.sock
            index = 1 # index of relevant line in split string
            if self.pythonVersion == '3':
                streamStatus = self.sendAndReceiveText(sock,'stream text header', device).decode()
            else:
                streamStatus = self.sendAndReceiveText(sock,'stream text header', device)
            streamStatus = streamStatus.split('\r\n')
            if  'Header Not Available' in streamStatus[0]:
                str = streamStatus[0] + '. Check stream has been ran on device.'
                print(str)
                return str
            if self.pythonVersion == '3':
                outputMode = self.sendAndReceiveText(sock,'Config Output Mode?', device).decode()
                powerMode = self.sendAndReceiveText(sock,'stream mode power?', device).decode()
            else:
                outputMode = self.sendAndReceiveText(sock,'Config Output Mode?', device)
                powerMode = self.sendAndReceiveText(sock,'stream mode power?', device)
            format = int(re.sub(r'^Format: ', '', streamStatus[index]))
            b0 = 1              #12V_I
            b1 = 1 << 1         #12V_V
            b2 = 1 << 2         #5V_I
            b3 = 1 << 3         #5V_V
            formatHeader = 'StripeNum, Trig, '
            if format & b3:
                if ('3V3' in outputMode):
                    formatHeader = formatHeader +  '3V3_V,'
                else:
                    formatHeader = formatHeader +  '5V_V,'
            if format & b2:
                if ('3V3' in outputMode):
                    formatHeader = formatHeader +  ' 3V3_I,'
                else:
                    formatHeader = formatHeader +  ' 5V_I,'
            
            if format & b1:
                formatHeader = formatHeader + ' 12V_V,'
            if format & b0:
                formatHeader = formatHeader + ' 12V_I'
            if 'Enabled' in powerMode:
                if ('3V3' in outputMode):
                    formatHeader = formatHeader + ' 3V3_P'
                else:
                    formatHeader = formatHeader + ' 5V_P'
                if ((format & b1) or (format & b0)):
                    formatHeader = formatHeader + ' 12V_P'
            return formatHeader
        except:
            print(device + ' Unable to get stream  format.' + self.host + ':' + '{}'.format(self.port))
            raise
    
    # Get stripes out of the backends stream buffer for the specified device using text commands
    # The objects connection needs to be opened (connect()) before this is used
    def streamGetStripesText(self, sock, device, numStripes=4096):
        try:
            bufferStatus = False
            if self.pythonVersion == '3':
                streamStatus = self.sendAndReceiveText(sock, 'stream?', device).decode()
            else:
                streamStatus = self.sendAndReceiveText(sock, 'stream?', device)
            if ('Overrun' in streamStatus) or ('8388608 of 8388608' in streamStatus):
                bufferStatus = True
            stripes = self.sendAndReceiveText(sock, 'stream text all', device, readUntilCursor=True)
            time.sleep(0.001)
            if stripes[-1:] != self.cursor:
                return "Error no cursor returned."
            else:
                if self.pythonVersion == '3':
                    endOfFile = 'eof\r\n>'
                    genEndOfFile = endOfFile.encode()
                else:
                    genEndOfFile = 'eof\r\n>'
                if stripes[-6:] == genEndOfFile:
                    removeChar = -6
                else:
                    removeChar = -1
            
            # stripes = stripes.split('\r\n')
            # stripes = filter(None, stripes) #remove empty sting elements
            #print(stripes)
            return bufferStatus, removeChar, stripes
        except:
            raise
    
    def avgStringFromPwr(self, avgPwrTwo):
        if(avgPwrTwo==0):
            return '0'
        elif(avgPwrTwo==1):
            return '2'
        elif(avgPwrTwo > 1 and avgPwrTwo < 10 ):
            avg = 2 ** int(avgPwrTwo)
            return '{}'.format(avg)
        elif(avgPwrTwo==10):
            return '1k'
        elif(avgPwrTwo==11):
            return '2k'
        elif(avgPwrTwo==12):
            return '4k'
        elif(avgPwrTwo==13):
            return '8k'
        elif(avgPwrTwo==14):
            return '16k'
        elif(avgPwrTwo==15):
            return '32k'
        else:
            return 'Invalid Average Value'
    
    # Works out average values of timescales longer than max device averaging
    def averageStripes(self, leftover, streamAverage, newStripes, f, remainingStripes = []):
        newString = str(newStripes)
        newList = []
        if remainingStripes == []:
            newList = newString.split('\r\n')
        else:
            newList = remainingStripes
            newList.extend(newString.split('\r\n'))
        numElements = newList[0].count(' ') + 1
        streamTotalAverage = leftover + streamAverage
        splitList = [] * numElements
        if len(newList) < streamTotalAverage:
            remainingStripes = newList[:-1]
            return leftover, remainingStripes
        runningAverage = [0] * (len(newList[0].split(' ')) - 2)
        j = 0
        z = 1
        for i in newList[:-1]:
            splitList = i.split(' ')
            splitNumbers = [int(x) for x in splitList[2:]]
            runningAverage = [sum(x) for x in zip(runningAverage, splitNumbers)]
            if z == math.floor(streamTotalAverage):
                finalAverage = splitList[0:2] + [str(round(x / streamAverage)) for x in runningAverage]
                for counter in xrange(len(finalAverage)-1):
                    finalAverage[counter] = finalAverage[counter] + ' '
                if self.pythonVersion == '3':
                    finalAverage = finalAverage.encode
                for x in finalAverage:
                    f.write(x)
                f.write('\r\n')
                streamTotalAverage += streamAverage
                j += 1
            z += 1
        remainingStripes = newList[int(math.floor(j * streamAverage + leftover)):-1]
        leftover = (streamTotalAverage - streamAverage) % 1
        return leftover, remainingStripes

    def deviceMulti(self, device):
        if (device in self.deviceList):
            return self.deviceList.index(device)
        else:
            self.listSemaphore.acquire()
            self.deviceList.append(device)
            self.stopFlagList.append(True)
            self.listSemaphore.release()
            return self.deviceList.index(device)
    
    def deviceDictSetup(self, module):
        if module in self.deviceDict.keys():
            return
        elif module == 'QIS':
            self.dictSemaphore.acquire()
            self.deviceDict[module] = [False, 'Disconnected', "No attempt to connect to QIS yet"]
            self.dictSemaphore.release()
        else:
            self.dictSemaphore.acquire()
            self.deviceDict[module] = [False, 'Stopped', "User hasn't started stream"]
            self.dictSemaphore.release()
    
    def streamInterrupt(self):
        for key in self.deviceDict.keys():
            if self.deviceDict[key][0]:
                return True
        return False
    
    def interruptList(self):
        streamIssueList = []
        for key in self.deviceDict.keys():
            if self.deviceDict[key][0]:
                streamIssue = [key] 
                streamIssue.append(self.deviceDict[key][1])
                streamIssue.append(self.deviceDict[key][2])
                streamIssueList.append(streamIssue)
        return streamIssueList
    
    def waitStop(self):
        running = 1
        while running != 0:
            threadNameList = []
            for t1 in threading.enumerate():
                threadNameList.append(t1.name)
            running = 0
            for module in self.deviceList:
                if (module in threadNameList):
                    running += 1
                    time.sleep(0.5)
            time.sleep(1)

    def convertStreamAverage (self, streamAveraging):
        returnValue = 32000;
        if ("k" in streamAveraging):
            returnValue = streamAveraging.replace("k", "000")
        else:
            returnValue = streamAveraging

        return returnValue

