'''
Created on Jan 29, 2019

@author: reynolds
'''

import sys, os, struct
from wrtdk.parser.parser import parser
from wrtdk.parser.msg.wrtmsg import udp_wrapper

class hcsr04(parser):
    ''' A class for parsing the HCSR04 messages'''

    def __init__(self):
        ''' Constructor '''
        super().__init__()# inherit superclass
        
        # initialize properties
        self.reset()
        
        # define constants
        self.LSB_2_M = 100 * 1e-6
        self.LSB_2_NS = 10
        
    def reset(self):
        ''' resets the parser properties '''
        self._ns = []
        self._alt = []
        
    def parse(self,msg):
        ''' parses the wrt hcsr04 acoustic sensor message '''
        try:
            self._alt,self._ns = struct.unpack('>iI',msg)
            self._alt *= self.LSB_2_M
            self._ns *= self.LSB_2_NS
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
    
    def getData(self):
        ''' returns the data
        altitude in m
        time in nanoseconds'''
        return [self._alt,self._ns]
            
if __name__ == '__main__':
    alt = hcsr04()
    
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20190129_sonar_lord_test\randall_sonar_lord_test.dat'
    
    with open(filename,'rb') as f:
        pos = 0
        idlen = 6
        msg = f.read(idlen)
        pos = 6
        
        while msg != b'$SONAR' or pos < 10:
            msg = msg[1::] + f.read(1)
            pos = pos + 1
            
        wrapper = udp_wrapper()
            
        msg = msg + f.read(36-6)
        pos = pos + 36 - 6
        wrapper.parse(msg)
        
        payload = f.read(wrapper.getLength())
        pos = pos + 1
        
        alt.parse(payload)
        
        print(alt.getData())
        