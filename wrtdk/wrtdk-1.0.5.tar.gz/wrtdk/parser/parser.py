'''
Created on Aug 17, 2018

@author: reynolds
'''

import os
import numpy as np

class parser(object):
    ''' class for parsing ascii and binary messages '''

    def __init__(self):
        ''' Constructor '''
        self._error = False
        self._checksum = []
        self._class  = type(self).__name__
        self._filename = os.path.basename(__file__)
        
    def _calculateChecksum(self,b):
        ''' calculates a message checksum '''
        chk = 0
        for _b in b: chk ^= _b
        return chk
    
    def getChecksum(self):
        ''' returns the checksum '''
        return self._checksum
        
    def hasErrored(self):
        ''' returns whether an error occurred and resets error '''
        _err = self._error
        self._error = False
        return _err
    
    def _return(self,value,default=np.nan):
        ''' returns default value if empty '''
        if value == []: return default
        return value
    
    def _nan(self):
        ''' returns an nan for an initial value '''
        return np.nan
    
    def _minus1(self):
        ''' returns a -1 for an initial value '''
        return -1