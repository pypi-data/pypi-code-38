""" Utility functions and classes for SRP

Context : SRP
Module  : SRPUtil.py
Version : 1.23.3
Status  : approved
Author  : Stefano Covino, Nino Cucchiara
Date    : 14/03/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino
Purpose : Collection of utility functions and classes for SRP.

Usage   : to be imported

Remarks :

History : (29/05/2003) First version.
        : (15/06/2003) Better good range.
        : (09/09/2003) Magnitude to/from flux.
        : (02/10/2003) Reddening.
        : (07/10/2003) Angular distance.
        : (14/10/2003) Better SRPPhotometry output.
        : (23/12/2003) Zero-point in star data.
        : (01/09/2003) Rad to deg and viceversa functions.
        : (26/10/2004) DAOPHOT data classes.
        : (25/12/2004) Sigma clipping function.
        : (03/07/2005) Calzetti's Extinction Law
        : (13/04/2006) Bug corrected in which.
        : (25/02/2007) Absorption at the X-rays.
        : (15/11/2007) Corrections to absorption curves.
        : (21/11/2007) Star Data class for GAIA photom output.
        : (14/12/2007) Better management of redshifted data for X-ray absorption.
        : (12/10/2008) Peak data.
        : (18/10/2008) angleRange.
        : (22/10/2008) Rototraslations.
        : (16/11/2008) Better mangament of sigma-clipping algorithms.
        : (18/04/2009) Jansky to erg/scm2A conversion.
        : (21/05/2010) Better FITS header mamagement.
        : (17/06/2010) Better data file path management
        : (22/06/2010) Minor improvement.
        : (30/09/2010) Stardata improvement.
        : (14/10/2010) Minor correction in Stardata.
        : (21/03/2011) Better coding for extinction routines.
        : (20/08/2011) Exptime in StarData.
        : (23/10/2011) No more Jy 2 ergs/s cm2 A and viceversa conversion.
        : (30/10/2011) Ellipticity added to StarData class.
        : (18/12/2012) Airmass in Daophot and GAIA output.
        : (11/02/2013) Classification added to StarData class.
        : (11/03/2014) Bug in daophot allstar output.
        : (28/07/2015) python3 porting.
        : (04/01/2017) Minor bug in porting.
        : (08/02/2017) Comparison python3-like
        : (14/03/2017) angleRange function ported to SRP.SRPMath.
"""


from . import SRPFiles, SRPConstants
import os, string, math, copy
from . import TimeAstro_algs






class StarData:
    def __init__ (self, dlista, exptime, zpl=(25.0, 0.0), mjd=-99.0, arm=1.0, flt='Unknown'):
        self.Id = dlista[0]
        self.X = float(dlista[1])
        self.Y = float(dlista[2])
        self.RA = float(dlista[3])
        self.DEC = float(dlista[4])
        self.magap = float(dlista[5])
        self.emagap = float(dlista[6])
        self.mag = float(dlista[7])
        self.emag = float(dlista[8])
        self.sky = float(dlista[9])
        self.fmax = float(dlista[10])
        self.FWHM = float(dlista[11])
        self.Ellipticity = float(dlista[12])
        self.Classification = float(dlista[13])
        self.mag = self.mag + 2.5*math.log10(exptime)
        self.magap = self.magap + 2.5*math.log10(exptime)
        self.magap = self.magap + zpl[0] - 25.0
        self.mag = self.mag + zpl[0] - 25.0
        self.emagap = math.sqrt(math.pow(self.emagap,2)+math.pow(zpl[1],2))
        self.emag = math.sqrt(math.pow(self.emag,2)+math.pow(zpl[1],2))
        self.MJD = mjd
        self.Airmass = float(arm)
        self.Filter = flt
        self.Exptime = exptime

    def __str__ (self):
        ostr = "%10s\t%7.2f\t%7.2f\t%10.6f\t%10.6f\t" % (self.Id, self.X, self.Y, self.RA, self.DEC)
        ostr = ostr + "%7.3f\t%6.3f\t%9.3f\t%15.3f\t" % (self.magap, self.emagap, self.sky, self.fmax)
        ostr = ostr + "%7.3f\t%6.3f\t%5.2f\t%15s\t" % (self.mag, self.emag, self.FWHM, self.MJD)
        ostr = ostr + "%7.3f\t%15s\t%7.2f\t%7.2f\t" % (self.Airmass, self.Filter, self.Exptime, self.Ellipticity)
        ostr = ostr + "%5.2f" % (self.Classification)
        return ostr+os.linesep



def getStarData (dlista, exptime, zpl=(25.0,0.0), mjd=-99.0, arm=1.0, flt='Unknown'):
    slista = []
    for i in range(len(dlista)):
        if dlista[i] != '':
            l = dlista[i].split()
            if len(l) > 0 and l[0] != '>' and len(l) == 14:
                s = StarData(l,exptime,zpl,mjd,arm,flt)
                slista.append(s)
    return slista



def getGoodRange (range,fact):
    zone = []
    xmin = int(1 + (range[1]-range[0]) * fact/100.0)
    xmax = int(range[1] -  (range[1]-range[0]) * fact/100.0)
    if len(range) == 4:
        ymin = int(1 + (range[3]-range[2]) * fact/100.0)
        ymax = int(range[3] - (range[3]-range[2]) * fact/100.0)
        zone = [xmin,xmax,ymin,ymax]
    else:
        zone = [xmin,xmax]
    return zone



def getRange (header):
    values = []
    naxis = header['NAXIS']
    xmin = 1
    xmax = header["NAXIS1"]
    if xmax == '':
        xmax = 1
    if naxis >= 2:
        ymin = 1
        ymax = header["NAXIS2"]
        if ymax == '':
            ymax = 1
        values = [xmin,xmax,ymin,ymax]
    else:
        values = [xmin,xmax]
    return values


# Fluxes and magnitudes
def getMagnitude (fl,efl,ban):
    sp = SRPFiles.getSRPDataPath()
    if sp == None:
        nofi = SRPConstants.SRPMagFluxFile
    else:
        nofi = os.path.join(sp,SRPConstants.SRPMagFluxFile)
    band, l0, f0, n0 = SRPFiles.SRPLeggiMagCalFile (nofi)
    #Cerchiamo la banda
    mag, emag, le = SRPConstants.SRPMagErr, SRPConstants.SRPMagErr, SRPConstants.SRPMagErr
    for i in range(len(band)):
        if band[i].strip().upper() == ban.strip().upper():
            mag = -2.5*(math.log10(fl/f0[i]))
            emag = (2.5/math.log(10.0))*efl/fl
            le = l0[i]
    return mag, emag, le


def getFlux (mag,emag,ban):
    sp = SRPFiles.getSRPDataPath()
    if sp == None:
        nofi = SRPConstants.SRPMagFluxFile
    else:
        nofi = os.path.join(sp,SRPConstants.SRPMagFluxFile)
    band, l0, f0, n0 = SRPFiles.SRPLeggiMagCalFile (nofi)
    #Cerchiamo la banda
    fl, efl, ne = SRPConstants.SRPMagErr, SRPConstants.SRPMagErr, SRPConstants.SRPMagErr
    for i in range(len(band)):
        if band[i].strip().upper() == ban.strip().upper():
            fl = f0[i]*math.pow(10,(-mag/2.5))
            efl = emag*fl/(2.5/math.log(10.0))
            ne = n0[i]
    return fl, efl, ne


def getBand ():
    sp = SRPFiles.getSRPDataPath()
    if sp == None:
        nofi = SRPConstants.SRPMagFluxFile
    else:
        nofi = os.path.join(sp,SRPConstants.SRPMagFluxFile)
    band, l0, f0, n0 = SRPFiles.SRPLeggiMagCalFile (nofi)
    return band




# Angular distance
def AngDistance(pos1, pos2):
    p1a = TimeAstro_algs.deg_to_rad(pos1[0])
    p1b = TimeAstro_algs.deg_to_rad(pos1[1])
    p2a = TimeAstro_algs.deg_to_rad(pos2[0])
    p2b = TimeAstro_algs.deg_to_rad(pos2[1])
    A = math.sin(p1b) * math.sin(p2b)
    B = math.cos(p1b) * math.cos(p2b)
    C = math.cos(p1a-p2a)
    D = TimeAstro_algs.rad_to_deg(math.acos(A+B*C))
    return D







# Deg to rad and viceversa
def deg2rad(ang):
    return ang*math.pi/180.0


def rad2deg(ang):
    return ang*180.0/math.pi



# DAOPHOT data

class DAOStarApData:
    def __init__ (self, exptime, n, x, y, maglist, emaglist, sky, esky, skew, zp, am):
        self.Id = int(n)
        self.X = float(x)
        self.Y = float(y)
        self.MagList = []
        self.eMagList = []
        for i in range(len(maglist)):
            self.MagList.append(float(maglist[i])+2.5*math.log10(exptime)+zp[0])
            er = math.sqrt(math.pow(float(emaglist[i]),2)+math.pow(zp[1],2))
            self.eMagList.append(er)
        self.Sky = float(sky)
        self.eSky = float(esky)
        self.SSkew = float(skew)
        self.Airmass = float(am)

    def __str__ (self):
        msg = ''
        msg = msg + "%6d\t%10.3f\t%10.3f" % (self.Id, self.X, self.Y)
        msg = msg + "\t%10.2f\t%10.2f\t%10.2f" % (self.Sky, self.eSky, self.SSkew)
        for i in range(len(self.MagList)):
            msg = msg + "\t%8.3f\t%8.3f" % (self.MagList[i], self.eMagList[i])
        msg = msg + "\t%8.3f" % (self.Airmass)
        return msg



class DAOStarPsfData:
    def __init__ (self, exptime, n, x, y, sky, it, chi, sharp, mag, emag, zp, am):
        self.Id = int(n)
        self.X = float(x)
        self.Y = float(y)
        self.Mag = float(mag)+2.5*math.log10(exptime)+zp[0]
        self.eMag = math.sqrt(math.pow(float(emag),2)+math.pow(zp[1],2))
        self.Sky = float(sky)
        self.nIt = int(float(it))
        self.Chi = float(chi)
        self.Sharp = float(sharp)
        self.Airmass = float(am)

    def __str__ (self):
        msg = ''
        msg = msg + "%6d\t%10.3f\t%10.3f" % (self.Id, self.X, self.Y)
        msg = msg + "\t%10.2f\t%4d\t%5.1f" % (self.Sky, self.nIt, self.Chi)
        msg = msg + "\t%5.1f\t%8.3f\t%8.3f" % (self.Sharp, self.Mag, self.eMag)
        msg = msg + "\t%8.3f" % (self.Airmass)
        return msg





# X-ray absorption
def XAbsorption (energy, nh=1e20, z=0):
    ren = energy * (1 + z)
    if ren < 0.03:
        return 0.0
    elif ren > 10.0:
        return 1.0
    if nh < 0:
        return 0.0
    if 0.03 <= ren < 0.1:
        C1 = 17.3
        C2 = 608.1
        C3 = -2150.0
    elif 0.1 <= ren < 0.284:
        C1 = 34.6
        C2 = 267.9
        C3 = -476.1
    elif 0.284 <= ren < 0.400:
        C1 = 78.1
        C2 = 18.8
        C3 = 4.3
    elif 0.4 <= ren < 0.532:
        C1 = 71.4
        C2 = 66.8
        C3 = -51.4
    elif 0.532 <= ren < 0.707:
        C1 = 95.5
        C2 = 145.8
        C3 = -61.1
    elif 0.707 <= ren < 0.867:
        C1 = 308.9
        C2 = -380.6
        C3 = 294.0
    elif 0.867 <= ren < 1.303:
        C1 = 120.6
        C2 = 169.3
        C3 = -47.7
    elif 1.303 <= ren < 1.840:
        C1 = 141.3
        C2 = 146.8
        C3 = -31.5
    elif 1.840 <= ren < 2.471:
        C1 = 202.7
        C2 = 104.7
        C3 = -17.0
    elif 2.471 <= ren < 3.210:
        C1 = 342.7
        C2 = 18.7
        C3 = 0.0
    elif 3.210 <= ren < 4.038:
        C1 = 352.2
        C2 = 18.7
        C3 = 0.0
    elif 4.038 <= ren < 7.111:
        C1 = 433.9
        C2 = -2.4
        C3 = 0.75
    elif 7.111 <= ren < 8.331:
        C1 = 629.0
        C2 = 30.9
        C3 = 0.0
    elif ren >= 8.331:
        C1 = 701.2
        C2 = 25.2
        C3 = 0.0
    xcs = 1e-24*(C1 + C2*ren + C3*ren**2) / ren**3
    return math.e**-(xcs*nh)




# GAIA data

class GAIAStarData:
    def __init__ (self, exptime, n, x, y, mag, emag, sky, totsignal, radius, zp, am):
        self.Id = int(n)
        self.X = float(x)
        self.Y = float(y)
        self.Mag = float(mag)+2.5*math.log10(exptime)+zp[0]
        self.eMag = math.sqrt(math.pow(float(emag),2)+math.pow(zp[1],2))
        self.Sky = float(sky)
        self.TotSignal = float(totsignal)
        self.Radius = [float(radius[0]), float(radius[1])*float(radius[0]), float(radius[2])*float(radius[0])]
        self.Airmass = am

    def __str__ (self):
        msg = ''
        msg = msg + "%6d\t%10.3f\t%10.3f" % (self.Id, self.X, self.Y)
        msg = msg + "\t%8.3f\t%8.3f" % (self.Mag, self.eMag)
        msg = msg + "\t%10.2f\t%10g" % (self.Sky, self.TotSignal)
        msg = msg + "\t%6.2f\t%6.2f\t%6.2f" % (self.Radius[0],self.Radius[1],self.Radius[2])
        msg = msg + "\t%8.3f" % (self.Airmass)
        return msg


# Peak data
class PeakData:
    def __init__ (self, dlista):
        self.Id = dlista[0]
        self.X = float(dlista[1])
        self.Y = float(dlista[2])
        self.pix = float(dlista[3])
        self.mean = float(dlista[4])
        self.dev = float(dlista[5])
        self.med = float(dlista[6])
        self.min = float(dlista[7])
        self.max = float(dlista[8])
        self.fx = float(dlista[9])
        self.fy = float(dlista[10])
        self.FWHM = float(dlista[11])
        self.flux = float(dlista[12])
        self.NX = self.X
        self.NY = self.Y

    def __str__ (self):
        ostr = "%5s\t%7.2f\t%7.2f\t%5d\t%8.2f\t" % (self.Id, self.X, self.Y, self.pix, self.mean)
        ostr = ostr + "%8.2f\t%8.2f\t%8.2f\t%8.2f\t" % (self.dev, self.med, self.min, self.max)
        ostr = ostr + "%7.2f\t%7.2f\t%7.2f\t%10.3f\t" % (self.fx, self.fy, self.FWHM, self.flux)
        ostr = ostr + "%7.2f\t%7.2f" % (self.NX, self.NY)
        return ostr+os.linesep


    def __lt__ (self, other):
        return self.flux < other.flux


def rotoTrasla (coords, x0=0.0, y0=0.0, alpha=0.0, halfx=0.0, halfy=0.0):
    x = coords[0]-halfx
    y = coords[1]-halfy
    xn = x0 + x*math.cos(math.radians(alpha))-y*math.sin(math.radians(alpha))
    yn = y0 + x*math.sin(math.radians(alpha))+y*math.cos(math.radians(alpha))
    NX = xn+halfx
    NY = yn+halfy
    return NX,NY

def antiRotoTrasla (coords, x0=0.0, y0=0.0, alpha=0.0, halfx=0.0, halfy=0.0):
    x = coords[0]-halfx-x0
    y = coords[1]-halfy-y0
    xn = x*math.cos(math.radians(alpha))+y*math.sin(math.radians(alpha))
    yn = -x*math.sin(math.radians(alpha))+y*math.cos(math.radians(alpha))
    NX = xn+halfx
    NY = yn+halfy
    return NX,NY


#def angleRange (ang):
#    while not 0.0 <= ang <= 360.0:
#        if ang < 0.0:
#            ang = ang + 360.0
#        elif ang > 360.0:
#            ang = ang - 360.0
#    return ang


