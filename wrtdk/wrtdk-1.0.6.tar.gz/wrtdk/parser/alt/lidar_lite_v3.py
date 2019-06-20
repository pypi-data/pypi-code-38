'''
Created on Feb 22, 2019

@author: reynolds
'''

import struct, os, sys

from wrtdk.parser.parser import parser
from wrtdk.parser.msg.wrtmsg import udp_wrapper

class lidar_lite_v3(parser):
    ''' classdocs '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()
        
        self.CM_2_M = 1.0/100.0
        
        self.reset()
        
    def reset(self):
        ''' resets the parser '''
        self._health = -1
        self._regulation = -1
        self._peakdet = -1
        self._ref_overflow = -1
        self._sig_overflow = -1
        self._busy = -1
        self._strength = self._nan()
        self._d = self._nan()
        
    def parse(self,msg):
        ''' parses the message '''
        self.reset()
        
        try:
            b,self._strength,self._d = struct.unpack('>BBH',msg)
            self._d *= self.CM_2_M
            self._health       = (b & 0b00100000) >> 5
            self._regulation   = (b & 0b00010000) >> 4
            self._peakdet      = (b & 0b00001000) >> 3
            self._ref_overflow = (b & 0b00000100) >> 2
            self._sig_overflow = (b & 0b00000010) >> 1
            self._busy         = (b & 0b00000001)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data '''
        return [self._health,self._regulation,self._peakdet,
                self._ref_overflow,self._sig_overflow,self._busy,
                self._strength,self._d]
    
def test():
    q = lidar_lite_v3()
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20190221_rtinv-test\105_back_1.dat'
    msg = get_msg(filename)
    print('msg:%s' % msg)
    q.parse(msg)
    print(q.getData())
    
def get_msg(filename):
    with open(filename,'rb') as f:
        idlen = 6
        msg = f.read(idlen)
        pos = 6
        
        while msg != b'$LIDAR' and pos < 1000:
            msg = msg[1::] + f.read(1)
            pos = pos + 1
            
        wrapper = udp_wrapper()
            
        msg = msg + f.read(36-6)
        pos = pos + 36 - 6
        wrapper.parse(msg)
        
        payload = f.read(wrapper.getLength())
        pos = pos + 1
        return payload
            
if __name__ == '__main__':
    test()