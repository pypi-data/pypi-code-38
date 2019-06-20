# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:12:24 2019

@author: Win10 Pro x64
"""
import serial
import crcmod
import struct
import time

import serial.tools.list_ports


class DPS:
    def __init__(self, comport=None):
        if comport == None:
            dpsFound = False
            for comp in serial.tools.list_ports.comports():
                if (comp.description[0:16] == 'USB-SERIAL CH340'):
                    comport = comp.device
                    dpsFound = True
                    
            if dpsFound == False:
                raise RuntimeError("No DPS device found")

        self.comport = comport

        self.crc16_func = crcmod.predefined.mkCrcFun('modbus')

        self.dps = serial.Serial(self.comport, baudrate=9600, timeout=2.0)
        
    def addcrc(self, cmdb):
        return cmdb+self.crc16_func(cmdb).to_bytes(2, byteorder='little')
    
    def close(self):
        self.dps.close()
    
    def readVoltCurr(self):
        ret=self.readReg(2,2)
        volt = ret[3] / 100.0
        curr = ret[4] / 1000.0
        return volt, curr
    
    def readReg(self, regaddr, numBytes):
        cmdbytes = struct.pack('>BBHH', 0x01, 0x03, regaddr, numBytes)
        cmdbytes = self.addcrc(cmdbytes)
        self.dps.write(cmdbytes)
        retval = self.dps.read(size=9)
        vals = struct.unpack('>BBBHHH', retval)        
        return vals
            
    def writeReg(self, regaddr, value):
        cmdbytes = struct.pack('>BBHH', 0x01, 0x06, regaddr, value)
        cmdbytes = self.addcrc(cmdbytes)
        self.dps.write(cmdbytes)
        retval = self.dps.read(size=8)
        vals = struct.unpack('>BBHHH', retval)
        return vals
    
    def setVolt(self, volt):
        self.writeReg(0, int(volt*100.0))
    
    def setOnOff(self, state):
        self.writeReg(9, 1 if state else 0)
