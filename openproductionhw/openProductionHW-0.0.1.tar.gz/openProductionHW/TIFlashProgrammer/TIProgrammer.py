# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 11:01:40 2017

@author: Markus
"""
from subprocess import check_output
from subprocess import CalledProcessError
from subprocess import STDOUT

class TIProgrammer:
    def __init__(self, com, devName, exe, verifyCRC = True):
        # verify by CRC (faster)  or by read-back of flash?
        if verifyCRC:
            self.verify = "crc"
        else:
            self.verify = "rb"
        self.com = com
        self.exe = exe
        self.devName = devName

    @staticmethod
    def autoDetect(exe):
        out = check_output([exe, "-ls", "auto"], shell=True, stderr=STDOUT)
        if out.find(b"ID") == -1:
            raise RuntimeError("No programmer connected")
        devName = out[out.find(b"ID")+3:].split(b"\r")[0].decode()
        return devName
    
    def setCom(self, com):
        self.com = com
        
    def setDevName(self, devName):
        self.devName = devName
        
    def getBLEAddr(self):
        addr = b""
        try:
            out = check_output([self.exe, "-t", "soc(%s,%s)"%(self.devName, self.com), "lsidx(0)", "-r", "macprible"], shell=True, stderr=STDOUT)
            addr = out.split(b"\r\n")[-2]
        except CalledProcessError as inst:
            out = inst.output
        if addr != b"":
            addr = b":".join(addr.split(b" ")[-6:])
        return addr.decode(), out.decode()
        
    def program(self, file):
        ok = True
        try:
            out = check_output([self.exe, "-t", "soc(%s,%s)"%(self.devName, self.com), "-e", "all", "-p", "-f", file, "-v", self.verify, "--reset", "pin"], shell=True, stderr=STDOUT)
        except CalledProcessError as inst:
            out = inst.output
            ok = False
        return ok, out.decode()