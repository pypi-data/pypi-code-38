"""Adapted from Practical Astronomy with your Calculator.
   By Peter Duffett-Smith with some (minor) improvements by Stefano Covino"""

from math import *

def to_julian(time):
    "Converts a time tuple to julian day"
    year,month,day,hour,min,sec=time
    #    d=day+(hour+(min+(sec/60.))/60.)/24.
    d=day+to_decimal(time[-3:])/24.0
    if month<3:
        y=year-1
        m=month+12
    else:
        y=year
        m=month
    if (year>1582 or (year==1582 and month>10) or
        (year==1582 and month==10 and day >=15)):
        A=int(y/100)
        B=2-A+int(A/4.)
    else:
        B=0
    if y<0:
        C=int((365.25*y)-0.75)
    else:
        C=int(365.25*y)
    D=int(30.6001*(m+1))
    return B+C+D+d+1720994.5


def to_calendar(day):
    "Converts a julian day to a time tuple"
    jd=0.5+day
    I=int(jd)
    F=jd-I
    if I>2229160:
        A=int((I-1867216.25)/36524.25)
        B=I+1+A-int(A/4.)
    else:
        B=I
    C=B+1524
    D=int((C-122.1)/365.25)
    E=int(365.25*D)
    G=int((C-E)/30.6001)
    d=C-E+F-int(30.6001*G)
    if G<13.5:
        month=G-1
    else:
        month=G-13
    if month>2.5:
        year=D-4716
    else:
        year=D-4715

    day=int(d)
    h=(d-day)*24
    hour,minute,sec=to_hms(h)
    return year,month,day,hour,minute,sec

def to_decimal(time):
    "Converts (hour,minute,second) format to decimal hours"
    hour,min,sec=time
    if hour<0 or min<0 or sec<0:mult=-1
    else:mult=1
    return mult*(abs(hour)+((sec/60.0)+min)/60.0)

def to_hms(hourd):
    "Converts decimal hours to (hour,minute,second) format"
    hour=int(hourd)
    mind=abs(hourd-hour)*60
    min=int(mind)
    sec=round((mind-min)*60,2)
    return hour,min,sec

def to_utc(time,lon,daylight=0):
    "Converts decimal localtime to utc decimal time"
    hour=time-daylight
    if lon>=0:
        zone=int(lon/15.)
    else:
        zone=int(lon/15.)-1
    hour=hour-zone
    if hour>24:
        day=1
        hour=hour-24
    elif hour<0:
        day=-1
        hour=hour+24
    else:
        day=0
    return day,hour

def to_gst(julian,utc):
    "Converts utc decima time to Greenwitch sidereal time"
    s=julian-2451545.0
    t=s/36525.0
    t0=divmod(6.697374558+(2400.051336*t)+(0.000025862*t*t),24)[1]
    gst=divmod(t0+utc*1.002737909,24)[1]
    return gst

def gst_to_utc(julian,gst):
    "Converts Greenwitch sidereal time to utc"
    t=(julian-2451545.0)/36525.0
    t0=divmod(6.697374558+(2400.051336*t)+(0.000025862*t*t),24)[1]
    ut=divmod(divmod((gst-t0),24)[1]*0.9972695663,24)[1]
    return ut

def utc_to_local(utc,lon,savings=0):
    "Converts utc to localtime"
    hour=utc+savings
    if lon>=0:
        zone=int(lon/15.)
    else:
        zone=int(lon/15.)-1
    hour=hour+zone
    if hour>24:
        day=1
        hour=hour-24
    elif hour<0:
        day=-1
        hour=hour+24
    else:
        day=0
    return day,hour

def lst_to_gst(lst,lon):
    "Converts Local sidereal time to Greenwitch sidereal time"
    return divmod(lst-lon/15.0,24)[1]

def day_of_week(julian):
    "Given Julian day, returns day of the week"
    days={0:"Sunday",1:"Monday",2:"Tuesday",3:"Wednesday",4:"Thursday",
          5:"Friday",6:"Saturday"}
    a=(julian+1.5)/7.0
    day=int(round((a-int(a))*7.0))
    return days[day]

def rad_to_deg(rad):
    "Converts radians to degrees"
    return (rad*180.0)/pi

def deg_to_rad(deg):
    "Converts degrees to radians"
    return (deg/180.0)*pi

def eq_to_hor(h_angle,decl,lat):
    "Converts Equatorial coordinates to Horizon coordinates"
    [h_angle,decl,lat]=list(map(deg_to_rad,[h_angle,decl,lat]))
    h_angle=h_angle*15.0
    alt=asin(sin(decl)*sin(lat)+cos(decl)*cos(lat)*cos(h_angle))
    y=-cos(decl)*cos(lat)*sin(h_angle)
    x=sin(decl)-sin(lat)*sin(alt)
    alt=rad_to_deg(alt)
    azi=atan(y/x)
    if x<0:
        azi=rad_to_deg(azi)+180
    elif x>=0 and y<0:
        azi=rad_to_deg(azi)+360
    else:
        azi=rad_to_deg(azi)
    return azi,alt

def hor_to_eq(azimuth,altitude,lat):
    "Converts Horizon coordinates to Equatorial coordinates"
    azimuth=azimuth/15.0
    h_angle,decl=eq_to_hor(azimuth,altitude,lat)
    h_angle=h_angle/15.0
    return h_angle,decl

def ecl_to_eq(ecl_lon,beta,julian=2451545.0):
    "Converts Ecliptic coordiantes to Equatorial coordiantes"

    ##Find the obliquity of the ecliptic for given Julian day
    t=(julian-2451545.0)/36525.0
    deps=(46.815*t+0.0006*t*t-0.00181*t*t*t)/3600.0
    eps=23.439292-deps

    [ecl_lon,beta,eps]=list(map(deg_to_rad,[ecl_lon,beta,eps]))
    decl=asin(sin(beta)*cos(eps)+cos(beta)*sin(eps)*sin(ecl_lon))
    decl=rad_to_deg(decl)
    y=sin(ecl_lon)*cos(eps)-tan(beta)*sin(eps)
    x=cos(ecl_lon)
    ascens=atan(y/x)
    if x<0:
        ascens=rad_to_deg(ascens)+180
    elif x>=0 and y<0:
        ascens=rad_to_deg(ascens)+360
    else:
        ascens=rad_to_deg(ascens)
    ascens=ascens/15.0
    return ascens,decl

def eq_to_ecl(ascens,decl,julian=2451545.0):
    "Converts Equatorial coordinates to Ecliptic coordinates"
    ##Find the obliquity of the ecliptic for given Julian day
    t=(julian-2451545.0)/36525.0
    deps=(46.815*t+0.0006*t*t-0.00181*t*t*t)/3600.0
    eps=23.439292-deps

    ascens=ascens*15.0
    [ascens,decl,eps]=list(map(deg_to_rad,[ascens,decl,eps]))
    beta=asin(sin(decl)*cos(eps)-cos(decl)*sin(eps)*sin(ascens))
    beta=rad_to_deg(beta)
    y=sin(ascens)*cos(eps)+tan(decl)*sin(eps)
    x=cos(ascens)
    ecl_lon=atan(y/x)
    if x<0:
        ecl_lon=rad_to_deg(ecl_lon)+180
    elif x>=0 and y<0:
        ecl_lon=rad_to_deg(ecl_lon)+360
    else:
        ecl_lon=rad_to_deg(ecl_lon)
    return ecl_lon,beta

def solve_kepler(ecc,mean_anom):
    "Solves Kepler equation iteratively"
    e=mean_anom
    d=e-ecc*sin(e)-mean_anom
    while d>0.00000001:
        de=d/(1-ecc*cos(e))
        e=e-de
        d=e-ecc*sin(e)-mean_anom
    return e

def sun(julian):
    "Calculates Sun's ecliptic longitude"
    T=(julian-2415020)/36525.0
    ##    eg=279.6966778+36000.76892*T+0.0003025*T*T
    eg=279.403303
    wg=281.2208444+1.719175*T+0.000452778*T*T
    e=0.01675104-0.0000418*T-0.000000126*T*T
    days=julian-2447891.5
    n=divmod(360*days/365.242191,360)[1]
#    if n<0:n=n+360
    m=n+eg-wg
    if m<0:m=m+360
    E=solve_kepler(e,deg_to_rad(m))
    niou=rad_to_deg(2*atan(sqrt((1+e)/(1-e))*tan(E/2.0)))
    l=divmod(niou+wg,360)[1]
    if l<0:l=l+360
    return l

def planet(julian,plan_elem,earth_elem):
    "Calculate orbital parameters of a planet"
    (t_p,eps_p,w_p,e_p,a_p,i,omega)=plan_elem
    (t_e,eps_e,w_e,e_e,a_e,tmp1,tmp2)=earth_elem
    # For planet
    d=julian-2447891.5
    n_p=(360/365.242191)*(d/t_p)%360
    m_p=n_p+eps_p-w_p
    l=(n_p+(360/pi)*e_p*sin(deg_to_rad(m_p))+eps_p)%360
    niou_p=l-w_p
    r=a_p*(1-e_p*e_p)/(1+e_p*cos(deg_to_rad(niou_p)))
    ## For earth
    n_e=(360/365.242191)*(d/t_e)%360
    m_e=n_e+eps_e-w_e
    L=(n_e+(360/pi)*e_e*sin(deg_to_rad(m_e))+eps_e)%360
    niou_e=l-w_e
    R=a_e*(1-e_e*e_e)/(1+e_e*cos(deg_to_rad(niou_e)))
    psi=asin(sin(deg_to_rad(l-omega))*sin(deg_to_rad(i)))
    y=sin(deg_to_rad(l-omega))*cos(deg_to_rad(i))
    x=cos(deg_to_rad(l-omega))
    dl=atan(y/x)
    if x<0:
        dl=rad_to_deg(dl)+180
    elif x>=0 and y<0:
        dl=rad_to_deg(dl)+360
    else:
        dl=rad_to_deg(dl)
    l_dash=dl+omega
    r_dash=r*cos(psi)
    if a_p<1.0:
        A=rad_to_deg(atan((r_dash*sin(deg_to_rad(L-l_dash)))
                          /(R-r_dash*cos(deg_to_rad(L-l_dash)))))
        ecl_lon=(180+L+A)%360
    else:
        ecl_lon=(rad_to_deg(atan((R*sin(deg_to_rad(l_dash-L)))
               /(r_dash-R*cos(deg_to_rad(l_dash-L)))))+l_dash)%360
    beta=rad_to_deg(atan((r_dash*tan(psi)*sin(deg_to_rad(ecl_lon-l_dash)))
                             /(R*sin(deg_to_rad(l_dash-L)))))
    return ecl_lon,beta
