'''
Created on May 7, 2019

@author: reynolds
'''

import sys, os, struct

from wrtdk.parser.parser import parser
from wrtdk.parser.msg.wrtmsg import udp_wrapper
from wrtdk.io.sim.sim_simulator import sim_simulator

class gprip(parser):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        super().__init__()
        self.reset()
        self.id = b'$GPRIP'
        
    def reset(self):
        self.depth = self._nan()
        self.alt = self._nan()
        self.lat = self._nan()
        self.lon = self._nan()
        self.lat_fix = self._nan()
        self.lon_fix = self._nan()
        self.fix = self._nan()
        self.fix_time = self._nan()
        self.time_ms = self._nan()
        self.state = self._nan()
        self.roll = self._nan()
        self.pitch = self._nan()
        self.yaw = self._nan()
        self.speed = self._nan()
    
    def parse(self,msg):
        self.reset()
        try:
            _,self.time_ms,self.state,self.fix,self.fix_time,self.lat_fix,self.lon_fix,self.lat,self.lon,self.depth,self.alt,self.roll,self.pitch,self.yaw,self.speed = struct.unpack('>6sdBH11d',msg)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def get(self,time=0,state=0,
            fix=0,time_fix=0,lat_fix=0,lon_fix=0,
            lat=0,lon=0,
            depth=0,alt=0,speed_mps=0,
            roll=0,pitch=0,yaw=0):
        try:
            return struct.pack('>6sdBH11d',
                           self.id,
                           time,state,
                           fix,time_fix,lat_fix,lon_fix,
                           lat,lon,
                           depth,alt,
                           roll,pitch,yaw,
                           speed_mps)
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
            return None
    
    def getData(self):
        ''' returns the data form the gprip message in a list
        0) epoch time in ms
        1) state
        2) the navigation fix
        3) the fix epoch time in ms
        4) the fix latitude in dd
        5) the fix longtude in dd
        6) the estimated latitude in dd
        7) the estimated longitude in dd
        8) the depth in m
        9) the altitude above the sea floor in m
        10) the roll in radians
        11) the pitch in radians
        12) the yaw in radians
        13) the vehicle speed in mps
        '''
        return [self.time_ms,self.state,
                self.fix,self.fix_time,self.lat_fix,self.lon_fix,
                self.lat,self.lon,
                self.depth,self.alt,
                self.roll,self.pitch,self.yaw,
                self.speed]

def test_gprip():
    m = gprip()
    f = r'C:\Users\reynolds\Documents\1704_madunit\data\20190507_gprip\GPRIP_SWXXX.dat'
    msg = get_msg(f,20)
    for mm in msg:
        print('len: %d msg:%s' % (len(mm),mm))
        m.parse(mm)
        print(m.getData())
    
def get_msg(filename,n=1):
    reader = sim_simulator()
    reader.read(filename,'$GPRIP')
    payload = []
    wrapper = udp_wrapper()
    while len(payload) < n:
        msg = reader.getNext()
        wrapper.parse(msg[0:wrapper.LENGTH])
        if not wrapper.hasErrored():
            payload.append(msg[wrapper.getMsgStart():wrapper.getMsgEnd()])
    
    return payload

if __name__ == '__main__':
    test_gprip()