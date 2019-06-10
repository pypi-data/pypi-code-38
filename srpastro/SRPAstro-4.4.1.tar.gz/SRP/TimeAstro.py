"""Adapted from Practical Astronomy with your Calculator.
   By Peter Duffett-Smith"""
# Bugs in version 1.6
# Modified by stefano Covino (covino@mi.astro.it), 10 Aug 2003

from .TimeAstro_algs import *

Error='astro.Error'

class Time:
    """ Class to handle time requirements.

    Initialize with 3 arguments: longitude, latitude and daylight
    savings time if applicable. Longitude can range from 0-360 or -180
    to 180. Latitude -90 to 90.
    Example:
    >>> now=Time(-72,38,0)

    Class Time defines the following methods:
    >>> now.set_now()
        Sets the time to the current time
    >>> now.local()
        With a tuple of six as argument sets the local time. With no
        argument it returns the local time:
    >>> now.local((1997,11,13,23,12,5))
        The tuple has the form (year,month,date,hour,minute,second)
    Similarly for Greenwitch Sidereal Time (gst), Local Sidereal Time
    >>> (lst) and Universal Coordinated Time (utc).
    >>> now.gst()
    >>> now.utc()
    >>> now.lst()


    >>> now.julian()   returns the julian day corresponding to 0hours
                       of the given date.
      >>> now.day()    returns the day

    The class defines the following (useful) attributes:
    x.lon       longitude
    x.lat       latitude
    x.savings   daylight savings time

    x.utchour   utc hour in decimal notation
    x.gsthour   gst hour in decimal notation
    x.lsthour   lst hour in decimal notation
    x.localhour local hour in decimal notation

    x.localtime    a list of the local time (year,month,day,hour,min,sec)
    x.utctime      a list of the utc time (year,month,day,hour,min,sec)
    x.gsttime      a list of the gst time (year,month,day,hour,min,sec)
    x.lsttime      a list of the lst time (year,month,day,hour,min,sec)
    """

    def __init__(self,lon=0,lat=0,savings=0):
        if lon>180:
            self.lon=lon-360
        else:
            self.lon=lon
        self.lat=lat
        self.savings=savings
        self.localtime=[0,0,0,0.0,0.0,0.0]

    def local(self,time=None):
        if time==None:
            return tuple(self.localtime)
        elif len(time)!=6:
            raise Error("Requires a tuple of 6")
        self.localtime[0:len(time)]=list(time[:])
        self.localhour=to_decimal(time[-3:])

    def set_now(self):
        import time
        now=time.localtime(time.time())[0:6]
        self.local(now)

    def gst(self,time=None):
        if time==None:
            T=self.utc()
            self.gsthour=to_gst(to_julian(T[0:3]+(0.0,0.0,0.0)),
                                self.utchour)
            return to_hms(self.gsthour)
        elif len(time)!=6:
            raise Error("Requires a tuple of 6")
        self.date=list(time[0:3])
        self.gsthour=to_decimal(time[-3:])
        self.julianday=to_julian(time[0:3]+(0.0,0.0,0.0))
        self.utchour=gst_to_utc(self.julianday,self.gsthour)
        self.localday,self.localhour=utc_to_local(self.utchour,
                                     self.lon,self.savings)
        self.localtime=self.date+list(to_hms(self.localhour))
        self.localtime[2]=self.localtime[2]+self.localday

    def utc(self,time=None):
        if time==None:
            if 'localhour' not in self.__dict__:
                self.set_now()
            utcday,self.utchour=to_utc(self.localhour,self.lon,self.savings)
            hour=to_hms(self.utchour)
            self.utctime=self.localtime[:]
            self.utctime[-3:]=list(hour)
            self.utctime[2]=self.utctime[2]+utcday
            return tuple(self.utctime)
        elif len(time)!=6:
            raise Error("Requires a tuple of 6")
        self.date=list(time[0:3])
        self.utchour=to_decimal(time[-3:])
        self.julianday=to_julian(time[0:3]+(0.0,0.0,0.0))
        self.localday,self.localhour=utc_to_local(self.utchour,
                                     self.lon,self.savings)
        self.localtime=self.date+list(to_hms(self.localhour))
        self.localtime[2]=self.localtime[2]+self.localday

    def lst(self,time=None):
        if time==None:
            self.gst()
            self.lsthour=divmod(self.gsthour+self.lon/float(15),24)[1]
            return to_hms(self.lsthour)
        elif len(time)!=6:
            raise Error("Requires a tuple of 6")
        self.date=list(time[0:3])
        self.lsthour=to_decimal(time[-3:])
        self.gsthour=lst_to_gst(self.lsthour,self.lon)
        self.gst(time[0:3]+to_hms(self.gsthour))

    def julian(self):
        if 'localhour' not in self.__dict__:
            self.set_now()
        return to_julian(tuple(self.localtime[0:3])+(0.0,0.0,0.0))

    def day(self):
        return day_of_week(self.julian())

class Coordinates:
    """ Fixes the coordinates of a heavenly body. provides methods to
    convert from one coordinate system to the other. Requires a Time
    object as an argument upon initialization."""
    def __init__(self,Time):
        import copy
        self.Time=copy.deepcopy(Time)

    def ecliptic(self,ecl_lon=None,beta=None):
        if ecl_lon==None and beta==None:
            if not ('Declination' in self.__dict__ and \
                    'right_ascension' in self.__dict__):
                raise Error("No location has been specified")

            ecl_lon,beta=eq_to_ecl(self.right_ascension,self.Declination,
                                   self.Time.julian())
            self.ecliptic_longitude,self.beta=ecl_lon,beta
            return to_hms(self.ecliptic_longitude),to_hms(self.beta)

        elif ecl_lon==None or beta==None:
            raise Error("Requires 0 or 2 arguments")
        [ecl_lon,beta]=list(map(to_decimal,[ecl_lon,beta]))
        self.ecliptic_longitude=ecl_lon
        self.beta=beta
        ascens,self.Declination=ecl_to_eq(ecl_lon,beta,self.Time.julian())
        self.ascension(to_hms(ascens))

    def horizon(self,azi=None,alt=None):
        if azi==None and alt==None:
            if not ('Declination' in self.__dict__ and \
                    'right_ascension' in self.__dict__):
                raise Error("No location has been specified")

            azi,alt=eq_to_hor(self.hour_angle,
                              self.Declination,self.Time.lat)
            self.azimuth,self.altitude=azi,alt
            return to_hms(self.azimuth),to_hms(self.altitude)
        elif azi==None or alt==None:
            raise Error("Requires 0 or 2 arguments")
        [azi,alt]=list(map(to_decimal,[azi,alt]))
        self.azimuth=azi
        self.altitude=alt
        h_angle,self.Declination=hor_to_eq(azi,alt,self.Time.lat)
        self.hourangle(to_hms(h_angle))

    def hourangle(self,h_angle=None):
        if h_angle==None:
            try:
                return to_hms(self.hour_angle)
            except AttributeError:
                raise Error("No location has been specified")
        h_angle=to_decimal(h_angle)
        self.hour_angle=h_angle
        ascens=to_decimal(self.Time.lst())-h_angle
        if ascens<0:ascens=ascens+24
        self.right_ascension=ascens

    def ascension(self,ascens=None):
        if ascens==None:
            try:
                return to_hms(self.right_ascension)
            except AttributeError:
                raise Error("No location has been specified")
        ascens=to_decimal(ascens)
        self.right_ascension=ascens
        h_angle=to_decimal(self.Time.lst())-ascens
        if h_angle<0:h_angle=h_angle+24
        self.hour_angle=h_angle

    def declination(self,decl=None):
        if decl==None:
            try:
                return to_hms(self.Declination)
            except AttributeError:
                raise Error("No location has been specified")
        self.Declination=to_decimal(decl)


    def equatorial(self,ascens=None,decl=None):
        if ascens==None and decl==None:
            if not ('Declination' in self.__dict__ and \
                    'right_ascension' in self.__dict__):
                raise Error("No location has been specified")
            return to_hms(self.hour_angle),to_hms(self.Declination)
        elif ascens==None or decl==None:
            raise Error("Requires 0 or 2 arguments")
        self.ascension(ascens)
        self.declination(decl)

    def __sub__(self,other):
        [a1,a2,d1,d2]=list(map(deg_to_rad,[self.right_ascension*15,
                                      other.right_ascension*15,
                                      self.Declination,other.Declination]))
        d=acos(sin(d1)*sin(d2)+cos(d1)*cos(d2)*cos(a1-a2))
        return to_hms(rad_to_deg(d))

    def rising(self):
        cosAr=sin(deg_to_rad(self.Declination))/cos(deg_to_rad(self.Time.lat))
        if cosAr<-1:
            raise Error("Body is never rising")
        elif cosAr>1:
            raise Error("Body is circumpolar")

        Ar=rad_to_deg(acos(cosAr))
        As=360-Ar
        h=acos(-tan(deg_to_rad(self.Declination))*
               tan(deg_to_rad(self.Time.lat)))
        LSTr=(24+self.right_ascension-rad_to_deg(h)/15.0)%24
        LSTs=(self.right_ascension+rad_to_deg(h)/15.0)%24
        Trising=Time(self.Time.lon,self.Time.lat,self.Time.savings)
        Tsetting=Time(self.Time.lon,self.Time.lat,self.Time.savings)
        Trising.lst(tuple(self.Time.localtime[0:3])+to_hms(LSTr))
        Tsetting.lst(tuple(self.Time.localtime[0:3])+to_hms(LSTs))
        Brising=Coordinates(Trising)
        Bsetting=Coordinates(Tsetting)
        Brising.horizon(to_hms(Ar),(0,0,0))
        Bsetting.horizon(to_hms(As),(0,0,0))
        return Brising,Bsetting


def test():
    time=Time(40,-80,0)
    print("LST",time.lst())
    print("Julian",time.julian())
    print("UTC",time.utc())
    print("GST",time.gst())
    print("Local",time.local())
    print("Day",time.day())
    t=(1997,1,1,5,0,0)
    time.lst(t)
    print(time.local())
    time.gst(t)
    print(time.local())
    time.local(t)
    print(time.gst())
    time.utc(t)
    print(time.day())

    star=Coordinates(time)
    try:
        star.ecliptic()
    except Error:
        print("need to specify location")
    try:
        star.ascension()
    except Error:
        print("need to specify location")

    a=(120,40,0)
    b=(-5,40,10)
    star.ecliptic(a,b)
    print("Horizon",star.horizon())
    star.horizon(a,b)
    print("Equatorial",star.equatorial())
    print("Hour Angle",star.hourangle())
    print("Right Ascension",star.ascension())
    star.ascension(b)
    star.declination(a)
    print("Right Ascension",star.ascension())
    print("Ecliptic",star.ecliptic())
    print("-----------------------------------")
    print("-----------------------------------")
    print("Test for Class Time")
    t=Time(-70,40,0)
    t.set_now()
    print("Local ",t.local())
    print("UTC   ",t.utc())
    print("GST   ",t.gst())
    print("LST   ",t.lst())
    print("Set LST to ",t.lst())
    t.lst(t.local()[0:3]+t.lst())
    print("Local ",t.local())
    print("UTC   ",t.utc())
    print("GST   ",t.gst())
    print("LST   ",t.lst())
    print("Set UTC to ",t.utc())
    t.utc(t.utc())
    print("Local ",t.local())
    print("UTC   ",t.utc())
    print("GST   ",t.gst())
    print("LST   ",t.lst())
