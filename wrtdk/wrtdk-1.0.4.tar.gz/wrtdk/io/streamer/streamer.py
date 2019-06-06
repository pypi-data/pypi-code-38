'''
Created on Feb 14, 2019

@author: reynolds
'''

import sys, os

from PyQt5.Qt import QThread
from wrtdk.io.writer import FileLogger

class LoggingStreamer(QThread):
    
    def __init__(self,running=False,debug=False):
        ''' constructor '''
        super().__init__()
        self._running = running
        self._debug = debug
        self.writer = FileLogger()
    
    def stop(self):
        '''  stops the thread  '''
        self._running = False
        self._debug = False
    
    def startLog(self,filename,ftype='w+'):
        '''  starts the log  '''
        try:
            self.writer.open(filename,ftype=ftype)
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
            
    def stopLog(self):
        '''  stops logging  '''
        try:
            self.writer.close()
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
        
    def isLogging(self):
        ''' returns whether the file writer is currently logging '''
        return self.writer.isLogging()
        