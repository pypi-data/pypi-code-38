import sys
import socket
import time
import datetime
import subprocess
import os
import random
import time


class QpsInterface:
    def __init__(self, host='127.0.0.1', port=9822):
        self.host = host
        self.port = port
        
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        time.sleep(1)
        self.recv()
        time.sleep(1)


    def recv(self):
        if sys.hexversion >= 0x03000000:
            response = self.client.recv(4096)
            i = 0
            for b in response:                                          # end buffer on first \0 character/value
                if b > 0:
                    i += 1
                else:
                    break;
            
            return response[:i].decode('utf-8', "ignore")
        else:            
            return self.client.recv(4096)


    def send(self, data):
        if sys.hexversion >= 0x03000000:
            self.client.send( data.encode() )
        else:
            self.client.send( data )
        

    def sendCmdVerbose(self, cmd):
        cmd = cmd + "\r\n"
        self.send(cmd)
        
        response = self.recv().strip()
        pos = response.rfind('\r\n>')
        return response[:pos]

    def connect(self, targetDevice):
        self.sendCmdVerbose("$connect " + targetDevice)
        time.sleep(0.3)


    def disconnect(self, targetDevice):
        self.sendCmdVerbose("$disconnect")


    def getDeviceList(self):
        deviceList = []
        response = self.sendCmdVerbose( "$list" )

        time.sleep(2)

        response2 = self.sendCmdVerbose( "$list" )

        while (response != response2):
            response = response2
            response2 = self.sendCmdVerbose( "$list" )
            time.sleep(1)

        #check if a response was received and the first char was a digit
        if( len(response) > 0 and response[0].isdigit ):
            sa = response.split()
            for s in sa:
                #checks for invalid chars
                if( ")" not in s and ">" not in s ):
                    #append to list if conditions met
                    deviceList.append( s )

        #return list of devices
        return deviceList

    
