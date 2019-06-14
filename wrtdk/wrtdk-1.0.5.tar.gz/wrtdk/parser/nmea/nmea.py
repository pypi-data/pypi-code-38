'''
Created on Jan 31, 2019

@author: reynolds
'''

from wrtdk.parser.parser import parser
import sys, os, re, utm
import numpy as np

class gcs(object):
    ''' handles gcs coordinates '''
    
    def dm2dd(self,dm,direction):
        '''  Converts a geographic coordiante given in "degres/minutes" dddmm.mmmm
        format (ie, "12319.943281" = 123 degrees, 19.953281 minutes) to a signed
        decimal (python float) format '''
        # '12319.943281'
        if not dm or dm == '0': return 0.
        d, m = re.match(r'^(\d+)(\d\d\.\d+)$', dm).groups()
        value = float(d) + float(m) / 60
        
        if direction == 'N' or direction == 'E': return value
        elif direction == 'S' or direction == 'W': return -value
        else: return np.NaN

class gpgga(parser):
    ''' $GPGGA sentence parser '''
    
    def __init__(self):
        ''' Constructor '''
        super().__init__()
        self.reset()
        self._gcs = gcs()
    
    def reset(self):
        ''' resets the parser '''
        self._time = self._nan()
        self._timestamp = '00:00:00.00'
        self._lat = self._nan()
        self._lon = self._nan()
        self._fix = self._minus1()
        self._n = self._minus1()
        self._easting = self._nan()
        self._northing = self._nan()
        self._region = self._minus1()
        self._zone = ''
        self._dop = self._nan()
        
    def parse(self,msg):
        ''' parses the message in ascii or binary '''
        try:
            if type(msg) == 'bytes': msg = msg.encode()
            if not msg.startswith('$GPGGA'):
                print('ImproperGPGGAMessageError.')     
            string = msg.split(',')
            self._timestamp = '%s:%s:%s' % (string[1][0:2],
                                            string[1][2:4],
                                            string[1][4:])
            self._time = float(string[1][0:2])*3600 + float(string[1][2:4])*60 + float(string[1][4:])
            self._lat = self._gcs.dm2dd(string[2],string[3])
            self._lon = self._gcs.dm2dd(string[4],string[5])
            [self._easting,self._northing,self._region,self._zone] = utm.from_latlon(self._lat,
                                                                                     self._lon)
            self._fix = int(string[6])
            self._n = int(string[7])
            self._dop = float(string[8])
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
            
    def getData(self):
        ''' returns the data 
        0) time in seconds
        1) timestamp in HH:MM:SS.ss
        2) latitude in decimal degrees
        3) longitude in decimal degrees
        4) number of satellites
        5) GPS fix quality
        6) Dilution of precision
        7) UTM easting in m
        8) UTM northing in m
        9) UTM Region
        10) UTM zone'''
        return [self._time,self._timestamp,
                self._lat,self._lon,
                self._n,self._fix,self._dop,
                self._easting,self._northing,self._region,self._zone]
        
class gprmc(parser):
    ''' parses the gprms nmea messages '''
    
    def __init__(self):
        ''' constructor '''
        super().__init__()
        self.reset()
        self._gcs = gcs()
        
    def reset(self):
        ''' resets the parser '''
        self._time = self._nan()
        self._timestamp = '00:00:00.00'
        self._lat = self._nan()
        self._lon = self._nan()
        self._easting = self._nan()
        self._northing = self._nan()
        self._region = self._minus1()
        self._zone = ''
        self._warn = ''
        self._s = self._nan()
        self._c = self._nan()
        self._date = ''
        self._var = self._nan()
        self._var_dir = ''
        
    def parse(self,msg):
        ''' parses the message '''
        try:
            if type(msg) == 'bytes': msg = msg.encode()
            if not msg.startswith('$GPRMC'):
                print('ImproperGPRMCMessageError.')     
            string = msg.split(',')
            self._timestamp = '%s:%s:%s' % (string[1][0:2],
                                            string[1][2:4],
                                            string[1][4:])
            self._time = float(string[1][0:2])*3600 + float(string[1][2:4])*60 + float(string[1][4:])
            self._warn = string[2]
            self._lat = self._gcs.dm2dd(string[3],string[4])
            self._lon = self._gcs.dm2dd(string[5],string[6])
            self._s = float(string[7])
            self._c = string[8]
            self._date = string[9]
            self._var = string[10]
            self._var_dir = string[11]
            
            [self._easting,self._northing,self._region,self._zone] = utm.from_latlon(self._lat,
                                                                                     self._lon)
        except Exception as e:
            self._error = True
            exc_type, _, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print('%s:%s in %s at %d. MSG:%s'%(exc_type.__name__,str(e), fname, exc_tb.tb_lineno,msg))
        
    def getData(self):
        ''' returns the data 
        0) time in seconds
        1) timestamp
        2) waring A=OK, V=warning
        3) latitude in decimal degrees
        4) longitude in decimal degrees
        5) utm easting in m
        6) utm northing in m
        7) utm region
        8) utm zone
        9) speed in knots
        10) true course
        11) date stamp
        12) variation
        13) east/west '''
        return [self._time,self._timestamp,self._warn,
                self._lat,self._lon,
                self._easting,self._northing,self._region,self._zone,
                self._s,self._c,self._date,self._var,self._var_dir]
            
if __name__ == '__main__':
    string = '$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47'
    gga = gpgga()
    gga.parse(string)
    print(gga.getData())
    
    rmc = gprmc()
    rmc.parse('$GPRMC,081836,A,3751.65,S,14507.36,E,000.0,360.0,130998,011.3,E*62')
    print(rmc.getData())
    