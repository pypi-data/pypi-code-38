'''
Created on Feb 14, 2019

@author: reynolds
'''

import time
import numpy as np

from PyQt5.QtCore import pyqtSignal

from wrtdk.io.streamer.streamer import LoggingStreamer

class fieldfox_streamer(LoggingStreamer):
    '''
    a class for stream data from fieldfox VNA
    '''
    
    new_ascan = pyqtSignal(list,str,int,int)

    def __init__(self,port=None):
        '''  constructor  '''
        super().__init__()
        self.port = port
        self._logging = False
        self._d = np.nan
        
    def run(self):
        ''' the aux sensor thread '''
        if self.port is not None: self._running = True
        
        while self._running:
            try:
                if self.port.measure():
                    self.new_ascan.emit(self.port.getData(),
                                        'AG',0,0)
                    
                    if self._logging: self.port.write(self._file,'data',self._d,time.time())
            except Exception as e:
                print(str(e),'Error in aux streamer.')
                
        try:
            self.port.close()
        except Exception as e:
            print('Error.',str(e))
        
    def startLog(self, filename,ftype='w+'):
        ''' starts the log '''
        try:
            self._file = filename
            self.port.header(fn=self._file,odir='data')
            self._logging = True
        except Exception as e:
            print('Error starting aux log file.',str(e))
            
    def isLogging(self):
        ''' returns whether the device is logging '''
        return self._logging
            
    def stopLog(self):
        ''' stops the aux log '''
        self._logging = False
        
    def setDistance(self,d=np.nan):
        ''' sets the distance '''
        self._d = d
        