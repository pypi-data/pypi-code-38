# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 19:12:24 2019

@author: Win10 Pro x64
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Feb  3 01:36:04 2019

@author: harald
"""

import serial
import struct
import time

import serial.tools.list_ports

"""
 s: Status [Interval ms]
 m: Single send message, bit pattern channel
 d: periodic send on ch 0 and 1, [Interval ms]
 i: mcp Init bit patter channel
 e: Init state
 v: Version string
 n: System Reset
 """

class M2D2:
    def __init__(self, comport=None):
        self.serial = None
        if comport == None:
            m2d2Found = False
            for comp in serial.tools.list_ports.comports():
                try:
                    dev = serial.Serial(comp.device, baudrate=115200, timeout=1.0)
                except:
                    continue
                dev.read_all()
                dev.write(b"\r")
                time.sleep(0.1)
                rcv_complete = b''
                while True:
                    rcv = dev.read_all()
                    rcv_complete += rcv
                    if len(rcv) == 0 or len(rcv_complete) > 1000:
                        break
                dev.close()
                if rcv_complete.find(b"s: Status [Interval ms]") != -1:
                    m2d2Found = True
                    comport = comp.device
                    break
                    
            if m2d2Found == False:
                raise RuntimeError("No M2D2 device found")

        self.comport = comport

        
        self.serial = serial.Serial(self.comport, baudrate=115200, timeout=1.0)
        self.serial.close()
        
    def _getCmd(self, cmd):
        self.serial.open()
        self.serial.write(b"%s\r"%cmd)
        time.sleep(0.5)
        rv = self.serial.read_all()
        self.serial.close()
        return rv
    
    def _setCmd(self, cmd, *args):
        cmd = b"%s"%cmd
        for arg in args:
            cmd = cmd + b" " + str(arg).encode()
        cmd = cmd + b"\r"
        self.serial.open()
        self.serial.write(cmd)
        self.serial.close()
    
    def periodicSend(self, interval):
        self._setCmd(b"d", interval)
            
    def getVersion(self):
        return self._getCmd(b"v")

    def sendDevice(self, num):
        self._setCmd(b"m", num)
        
    def getRXTXCounts(self):
        rv = self._getCmd(b"s")
        lst = rv.decode().split("\n")[1].split(" ")
        lst = list(filter(lambda a: a != '', lst))[1:]
        txCnts = lst[::2]
        txCnts = [ int(x) for x in txCnts]
        rxCnts = lst[1::2]
        rxCnts = [ int(x) for x in rxCnts]
        return txCnts, rxCnts

    def reset(self):
        self._getCmd(b"n")
    
#%%
if __name__ == "__main__":
    m2d2 = M2D2()
    tx, rx = m2d2.getRXTXCounts()
    #'A4:34:F1:81:D0:02'