'''
Created on Aug 17, 2018

@author: reynolds
'''

import os, sys, struct
from wrtdk.parser.parser import parser
from wrtdk.parser.msg.wrtmsg import udp_wrapper

class bno055(parser):
    ''' a parser for the wrt bno055 message '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()# inherit initial class
        
        # define constants
        self.COUNT_2_DEGREES = 1/16
        self.COUNT_2_CELCIUS = 1
        
        #reset
        self.reset()
        
    def reset(self):
        ''' resets the parser '''
        self._y = self._nan()
        self._p = self._nan()
        self._r = self._nan()
        self._t = self._nan()
        self._sys = self._minus1()
        self._acc = self._minus1()
        self._gyr = self._minus1()
        self._mag = self._minus1()
        
    def parse(self,msg):
        ''' parses the messages '''
        self.reset()
        
        try:
            y,r,p = struct.unpack('>hhh',msg[18:24])#msg[54:60])
            t,cal = struct.unpack('>bB',msg[44:46])#msg[80:82])
            self._r = r * self.COUNT_2_DEGREES
            self._p = p * self.COUNT_2_DEGREES
            self._y = y * self.COUNT_2_DEGREES
            self._t = t * self.COUNT_2_CELCIUS
            self._sys = (cal&0b11000000)>>6
            self._acc = (cal&0b00110000)>>4
            self._gyr = (cal&0b00001100)>>2
            self._mag = (cal&0b00000011)
            
            self._checksum = self._calculateChecksum(msg)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data 
        0) roll in degrees
        1) pitch in degrees
        2) yaw in degrees
        3) temperature in celcius
        4) system calibration value
        5) accelerometer calibration value
        6) gyro calibration value
        7) mag calibration value'''
        return [self._r,self._p,self._y,
                self._t,
                self._sys,self._acc,self._gyr,self._mag]
    
def test_bno055():
    imu = bno055()
    filename = r'C:\Users\reynolds\Documents\1711_nuwc\data\20180732_deckcheck\20180731_deckcheckS01.dat'
    msg = get_msg(filename)
    print('msg:%s' % msg)
    imu.parse(msg)
    print(imu.getData())
    
def get_msg(filename):
    with open(filename,'rb') as f:
        idlen = 6
        msg = f.read(idlen)
        pos = 6
        
        while msg != b'$IMUXX' and pos < 1000:
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
    test_bno055()