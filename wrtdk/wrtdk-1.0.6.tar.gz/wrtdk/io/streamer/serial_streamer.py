'''
Created on Apr 17, 2019

@author: reynolds
'''

from PyQt5.QtCore import pyqtSignal

from wrtdk.io.streamer.streamer import LoggingStreamer
from wrtdk.parser.nmea.nmea import gpgga, gprmc

import time,os,sys,struct
import numpy as np

class serial_streamer(LoggingStreamer):
    '''
    a streamer for streaming and logging serial data
    '''
    
    new_msg = pyqtSignal(list,'QString',int,int)
    new_timeout = pyqtSignal()

    def __init__(self,port=None):
        '''
        Constructor
        '''
        super().__init__()
        self.port = port
        self._logging = False
        self.gga = gpgga()
        self.rmc = gprmc()
        self.mcu_s = 0
        self.mcu_ms = 0
        self.gpsid = struct.pack('4sss',b'$GPS',bytes(0),bytes(0))
        self.fid = np.uint16(0)
        self.p1 = np.uint16(1)
        
    def setMCU(self,mcu=0):
        ''' sets the mcu time to write to the file '''
        self.mcu_s = int(mcu)
        self.mcu_ms = int( (mcu - self.mcu_s) * 1000 )
        
    def run(self):
        if self.port is not None: self._running = True
        
        while self._running:
            try:
                msg,addr = self.port.readLine()
            except Exception as e:
                #self.new_msg.emit([time.time(),])
                exc_type, _, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
                self.new_timeout.emit()
                if exc_type.__name__ == 'AttributeError': time.sleep(1)
                #self.new_msg.emit(['$ERROR',time.time(),addr,np.nan],'ND',0,0)# send an error message
                continue
            
            # if an empty mesage is received the skip it
            if msg is None: continue
            if len(msg) < 1: 
                self.new_msg.emit(['$EMPTY',time.time(),addr,np.nan],'ND',0,0)# send an error message
                continue
            
            # write the data to a file
            if self.isLogging():
                string = msg.decode().strip().encode()
                if msg[0] == 36: wrapper = struct.pack('>6s4H2s5I%ds' % len(string),
                                                       self.gpsid,0,0,0,self.fid,b'AG',
                                                       self.mcu_s,self.mcu_ms,0,len(string),0,string)
                else: wrapper = struct.pack('>6s4H2s5I%ds' % len(string),
                                                       b'$COUNT',0,0,0,self.fid,b'AG',
                                                       self.mcu_s,self.mcu_ms,0,len(string),0,string)
                if msg[-1] is not 10: msg = msg + b'\n'# add a new line if necessary
                self.writer.write(wrapper)
            
            # parse the messages
            if msg.startswith(b'$GPGGA'):
                self.gga.parse(msg.decode().strip())
                if not self.gga.hasErrored():
                    self.new_msg.emit(['$GPGGA',time.time(),addr] + self.gga.getData(),
                                      'AG',0,0)
            elif msg.startswith(b'$GPRMC'):
                self.rmc.parse(msg.decode().strip())
                if not self.rmc.hasErrored():
                    self.new_msg.emit(['$GPRMC',time.time(),addr] + self.rmc.getData(),
                                      'AG',0,0)
            elif msg.startswith(b'$GPGSV'): self.new_msg.emit(['$GPGSV',time.time(),addr,msg.decode().strip()]
                                                              ,'AG',0,0)
            elif msg.startswith(b'$GPGSA'): self.new_msg.emit(['$GPGSA',time.time(),addr,msg.decode().strip()],
                                                              'AG',0,0)
            elif msg.startswith(b'$GPVTG'): self.new_msg.emit(['$GPVTG',time.time(),addr,msg.decode().strip()],
                                                              'AG',0,0)
            elif msg.startswith(b'$GPGLL'): self.new_msg.emit(['$GPGLL',time.time(),addr,msg.decode().strip()],
                                                              'AG',0,0)
            else:
                try:
                    self.new_msg.emit(['$COUNT',time.time(),addr] + [float(msg.decode().strip())],
                                      'AG',0,0)
                except Exception as e:
                    exc_type, _, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
                    self.new_msg.emit(['$ERROR',time.time(),addr,np.nan],'ND',0,0)# send an error message
                    
            # increment the counter
            self.fid += self.p1
            
        # close the port
        try:
            self.port.close()
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))