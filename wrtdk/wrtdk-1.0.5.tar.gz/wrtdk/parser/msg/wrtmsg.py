'''
Created on Aug 20, 2018

@author: reynolds
'''
import os, sys, datetime, struct, math
from wrtdk.parser.parser import parser

class udp_wrapper(parser):
    '''  a class for parsing the wrt udp 
    sensor message wrapper '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()# inherit superclass
        
        # define constants
        self.LENGTH = 36
        self.ID_LENGTH = 6
        self.UTC_TIMESTAMP = datetime.datetime.utcnow().timestamp()
        #print('Current UTC Timestamp',self.UTC_TIMESTAMP)# print timestamp
        
        # intiialzie properties
        self.reset()
        
    def reset(self):
        ''' resets the properties '''
        self._type = -1
        self._status = ''
        self._mcu = -1
        self._length = -1
        self._n = -1
        self._sen = -1
        self._sys = -1
        self._chk = -1
        
    def __str__(self,):
        ''' prints the class as a string '''
        return '%s:[type:%s,sensor:%d,system:%s,status:%s,fiducial:%d,mcu:%f,length:%d,checksum:%d]' % (type(self).__name__,
                                                                                                     self._type,
                                                                                                     self._sen,
                                                                                                     self._sys,
                                                                                                     self._status,
                                                                                                     self._n,
                                                                                                     self._mcu,
                                                                                                     self._length,
                                                                                                     self._chk)
    
    def parse(self,msg):
        ''' parses the message wrapper '''
        self.reset()
        try:
            #m1,m2,m3,m4,m5,m6,_,self._sen,self._sys,self._n,stat1,stat2,mcu1,mcu2,_,self._length,self._chk = struct.unpack('>ssssssHHHHssIIIII',msg)
            #self._type = m1.decode() + m2.decode() + m3.decode() + m4.decode() + m5.decode() + m6.decode()
            #self._status = stat1.decode() + stat2.decode()
            
            self._type,_,self._sen,self._sys,self._n,self._status,mcu1,mcu2,_,self._length,self._chk = struct.unpack('>6s4H2s5I',msg)
            self._type = self._type.decode()
            self._status = self._status.decode()
            
            self._mcu = mcu1 + mcu2/1000.0# s
            if self._mcu < self.UTC_TIMESTAMP-86400:
                self._mcu = self._mcu+86400
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def get(self,mtype='$?????',sen_id=0,sys_id=0,fid=0,status='ND',
            t_s=0,t_ms=0,mlen=0,cksm=0):
        try:
            return struct.pack('>6s4H2s5I',
                               mtype,0,sen_id,sys_id,fid,
                               status,t_s,t_ms,0,mlen,cksm)
        except Exception as e:
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d.'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno))
            return None
    
    def getStatus(self):
        ''' returns the status '''
        return self._status
    
    def getMCU(self):
        ''' returns the mcu time '''
        return self._mcu
    
    def getTimestamp(self):
        ''' returns the timestamp '''
        return str(datetime.datetime.fromtimestamp(self._mcu))
    
    def getLength(self):
        ''' returns the length '''
        return self._length
    
    def getType(self):
        ''' returns the message type '''
        return self._type
    
    def getMsgStart(self,position=0):
        ''' returns the message start '''
        return self.LENGTH + position
    
    def getMsgEnd(self,position=0):
        ''' returns the message end '''
        return self.LENGTH + self._length + position
    
    def getStart(self,position=0):
        ''' returns the start of the message '''
        return position
    
    def getEnd(self,position=0):
        ''' returns the end of the message '''
        return position + self.LENGTH
    
    def getFiducial(self):
        ''' returns the fiducial '''
        return self._n
    
    def getSensorID(self):
        ''' returns the sensor id '''
        return self._sen
    
    def getSystemID(self):
        ''' returns the system id '''
        return self._sys
    
    def getWrapperChecksum(self):
        ''' returns the wrapper checksum '''
        return self._chk

class wrtsys(parser):
    ''' parses for wrt system message '''

    def __init__(self):
        ''' Constructor '''
        super().__init__()# inherit superclass
        
        # initialize properties
        self.reset()
        
    def reset(self):
        ''' resets the message '''
        self._msg = 'Parse Error'''
        
    def parse(self,msg):
        ''' parses the $SYSTM message '''
        self.reset()
        try:
            tmp = msg.decode()
            self._msg = tmp[0:3] + ' ' + tmp[5:7] + '/' + tmp[3:5] + '/' + tmp[7:9] + ' ' + tmp[9:11] + ':' + tmp[11:13] + ':' + tmp[13:18] + ' ' +tmp[18:]
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data '''
        return [self._msg]
    
class rtcom_mag(parser):
    ''' message parser for a real time compensated mag '''
    
    def __init__(self):
        ''' constructor '''
        super().__init__()
        
        # reset the parser
        self.reset()
        
    def reset(self):
        ''' resets the value '''
        self._com = self._nan()
        
    def parse(self,msg):
        ''' parses a real time compensated mag message '''
        self.reset()
        
        try:
            self._com, = struct.unpack('<d',msg)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data 
        0) compensated mag data nT'''
        return [self._com]
        
class rtdet_mag(parser):
    ''' message parser for a real time compensated mag '''
    
    def __init__(self):
        ''' constructor '''
        super().__init__()
        
        # reset the parser
        self.reset()
        
    def reset(self):
        ''' resets the value '''
        self._flag = self._nan()
        self._strength = self._nan()
        
    def parse(self,msg):
        ''' parses a real time compensated mag message '''
        self.reset()
        
        try:
            self._flag,self._strength = struct.unpack('<dd',msg)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data 
        0) detection flag
        1) detection strength '''
        return [self._flag,self._strength]
        
class rtinv_mag(parser):
    ''' message parser for a real time compensated mag '''
    
    def __init__(self):
        ''' constructor '''
        super().__init__()
        
        # reset the parser
        self.reset()
        
    def reset(self):
        ''' resets the value '''
        self._x = self._nan()
        self._y = self._nan()
        self._z = self._nan()
        self._s = self._nan()
        self._h = self._nan()
        self._mx = self._nan()
        self._my = self._nan()
        self._mz = self._nan()
        self._m = self._nan()
        self._fit = self._nan()
        self._navE = self._nan()
        self._navN = self._nan()
        self._navA = self._nan()
        
    def parse(self,msg):
        ''' parses a real time compensated mag message '''
        self.reset()
        
        try:
            self._x,self._y,self._z,self._s,self._h,self._mx,self._my,self._mz,self._fit,self._navE,self._navN,self._navA = struct.unpack('<dddddddddddd',msg)
            self._m = math.sqrt(self._mx ** 2 + 
                                self._my ** 2 +
                                self._my ** 2)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data 
        0) inversion x location m
        1) inversion y location m
        2) inversion z location m
        3) inversion speed in mps
        4) inversion headig in degrees
        5) moment x in A m^2
        6) moment y in A m^2
        7) moment z in A m^2
        8) data model fit
        9) navigation easting m
        10) navigation northing m
        11) navigation altitude m
        12) moment magnitude in A m^2'''
        return [self._x,self._y,self._z,
                self._s,self._h,
                self._mx,self._my,self._mz,
                self._fit,
                self._navE,self._navN,self._navA,
                self._m]
    
class rttrk_mag(parser):
    ''' message parser for a real time compensated mag '''
    
    LENGTH = 5
    
    def __init__(self):
        ''' constructor '''
        super().__init__()
        
        # reset the parser
        self.reset()
        
    def reset(self):
        ''' resets the value '''
        self._x = self._nan()
        self._y = self._nan()
        self._z = self._nan()
        self._m = self._nan()
        self._n = self._nan()
        
    def parse(self,msg):
        ''' parses a real time compensated mag message '''
        self.reset()
        
        try:
            self._x,self._y,self._z,self._m,self._n = struct.unpack('<ddddd',msg)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data '''
        return [self._x,self._y,self._z,self._m,self._n]
    
class sw_mag(rttrk_mag):
    
    def parse(self,msg):
        ''' parses a real time compensated mag message '''
        self.reset()
        
        try:
            self._x,self._y,self._z,self._m,self._n = struct.unpack('>ddddd',msg)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
    
    
def test_systm():
    qmag = wrtsys()
    filename = r'C:\Users\reynolds\Documents\1606_navsea\data\no_i2c.dat'
    msg = get_msg(filename,b'$SYSTM')
    print('msg:%s' % msg)
    qmag.parse(msg)
    print('$SYSTM',qmag.getData())
    
def test_rtcom_mag():
    qmag = rtcom_mag()
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20190220_realtimeinv\RT_MSG.bin'
    msg = get_msg(filename,b'$RTCOM')
    print('msg:%s' % msg)
    qmag.parse(msg)
    print('$RTCOM',qmag.getData())
    
def test_rtdet_mag():
    qmag = rtdet_mag()
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20190220_realtimeinv\RT_MSG.bin'
    msg = get_msg(filename,b'$RTDET')
    print('msg:%s' % msg)
    qmag.parse(msg)
    print('$RTDET',qmag.getData())
    
def test_rtinv_mag():
    qmag = rtinv_mag()
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20190220_realtimeinv\RT_MSG.bin'
    msg = get_msg(filename,b'$RTINV')
    print('msg:%s' % msg)
    qmag.parse(msg)
    print('$RTINV',qmag.getData())
    
def test_rtrtk_mag():
    qmag = rttrk_mag()
    filename = r'C:\Users\reynolds\Documents\1704_madunit\data\20190226_rtmsgs\RT_MSG.bin'
    msg = get_msg(filename,b'$RTTRK')
    qmag.parse(msg)
    print('$RTTRK',qmag.getData())
    
def get_msg(filename,msgid):
    with open(filename,'rb') as f:
        idlen = 6
        msg = f.read(idlen)
        pos = 6
        
        while msg != msgid:
            msg = msg[1::] + f.read(1)
            pos = pos + 1
            
        wrapper = udp_wrapper()
            
        msg = msg + f.read(36-6)
        pos = pos + 36 - 6
        wrapper.parse(msg)
        print(type(wrapper.getSensorID()),type(wrapper.getSystemID()))
        
        payload = f.read(wrapper.getLength())
        pos = pos + 1
        
        return payload
            
if __name__ == '__main__':
    test_systm()
    test_rtcom_mag()
    test_rtdet_mag()
    test_rtinv_mag()
    test_rtrtk_mag()