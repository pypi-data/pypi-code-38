'''
Created on Aug 17, 2018

@author: reynolds
'''

import os, sys, struct, math
from wrtdk.parser.parser import parser
from wrtdk.parser.msg.wrtmsg import udp_wrapper

class pni(parser):
    ''' a class for parsing the pni vector
    magnetometer binary message '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()# inherit superclass
        
        # define constants
        self.COUNT_2_NT = 1000/75
        self.MSG_LEN = 12
        
        # initialize properties
        self.reset()
        
    def reset(self):
        ''' resets the properties '''
        self._bx = self._nan()
        self._by = self._nan()
        self._bz = self._nan()
        
    def parse(self,msg):
        ''' parses the pni messages '''
        self.reset()
        
        try:
            self._bx,self._by,self._bz = struct.unpack('>iii',msg[:-4])
            self._bx *= self.COUNT_2_NT
            self._by *= self.COUNT_2_NT
            self._bz *= self.COUNT_2_NT
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def _total(self):
        ''' returns the total field value '''
        return math.sqrt(self._bx ** 2 + self._by ** 2 + self._bz ** 2)
            
    def getData(self):
        ''' returns all the data 
        0) bx in n
        1) by in nT
        2) bz in nT
        3) bTotal in nT '''
        return [self._bx,self._by,self._bz,
                self._total()]
    
def test_pni():
    p = pni()
    filename = r'C:\Users\reynolds\Documents\1711_nuwc\data\20180732_deckcheck\20180731_deckcheckS01.dat'
    msg = get_msg(filename)
    print('msg:%s' % msg)
    p.parse(msg)
    print(p.getData())
    
def get_msg(filename):
    with open(filename,'rb') as f:
        idlen = 6
        msg = f.read(idlen)
        pos = 6
        
        while msg != b'$VCMAG' and pos < 1000:
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
    test_pni()