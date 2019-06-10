""" Utility functions and classes for SRP

Context : SRP
Module  : SRPAstro.py
Version : 1.8.3
Status  : approved
Author  : Stefano Covino
Date    : 19/04/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/~covino
Purpose : Collection of utility functions and classes for SRP.

Usage   : to be imported

Remarks :

History : (19/10/2008) First version.
        : (05/11/2008) Sky in MiPhotdata class.
        : (19/11/2008) Many more minor issues and average sigma-clipping for arrays.
        : (20/11/2008) Better sky estimate and sorting of output file.
        : (27/11/2008) Better center moment estimate.
        : (03/01/2009) Better error estimate.
        : (17/04/2009) Better centering algorithm. MinMax function added.
        : (10/10/2009) Management of negative net fluxes.
        : (12/11/2009) Better (simpler) zero point determination.
        : (25/02/2010) RON in electrons.
        : (21/05/2010) Better sigma clipping algorithm.
        : (17/06/2010) Better managment of objects close to the frame boundaries.
        : (20/06/2010) Better centroid determination.
        : (22/06/2010) Minor improvement.
        : (20/12/2010) Import style corrected.
        : (29/07/2015) numpy porting.
        : (05/11/2015) Minor correction.
        : (10/11/2015) BiGauss, resid and centerGauss improved.
        : (13/11/2015) MinMax improved.
        : (27/11/2015) findPercArea improved.
        : (11/12/2015) Better mangitude computation.
        : (17/12/2015) Returns a limit rather than a detection when the magnitude error is
                        larger than 0.5 mag.
        : (28/01/2016) integFuct improved.
        : (19/04/2017) SRPFITS added.
"""


import math, random, os, copy, sys
from scipy.optimize import fmin
from . import SRPUtil
import numpy
from SRP.SRPStatistics.AverIterSigmaClipp import AverIterSigmaClipp
from SRPFITS.Photometry.getBackground import getBackground
from SRPFITS.Photometry.MinMax import MinMax
from SRPFITS.Photometry.centerMoment import centerMoment
from SRP.SRPMath.findPercArea import findPercArea
from SRP.SRPMath.integFuct import integFuct




class MiPhotData:
    def __init__ (self, Id, x0, y0, max, mag, emag, saturation=55000, exptime=1.0, zp=(25.0,0.0), mjd=-99.0, etm=-99.0, sky=0.0, airm=(1.0,0.0), tmg=0.0, etmg=0.0, calsts=(1.0,0.0), cmt='N'):
        self.Id = Id
        self.XC = float(x0)
        self.YC = float(y0)
        self.MAX = float(max)
        if float(mag) < 90:
            self.Mag = float(mag)+2.5*math.log10(exptime)
        else:
            self.Mag = float(mag)
        self.eMag = float(emag)
        self.MagCal = self.Mag+float(zp[0])
        self.eMagCal = math.sqrt(self.eMag**2+float(zp[1])**2)
        self.Comment = cmt
#                if self.MAX < saturation and self.Mag < 90:
#                        self.Comment = 'Ok'
#                elif self.MAX >= saturation:
#                        self.Comment = 'S'
        self.MJD = float(mjd)
        self.Exptime = float(etm)
        self.Sky = float(sky)
        self.ZP = float(zp[0])
        self.eZP = float(zp[1])
        self.ChiZP = float(calsts[0])
        self.NZP = int(calsts[1])
        self.Airm = float(airm[0])
        self.Coef = float(airm[1])
        self.TMag = float(tmg)
        self.eTMag = float(etmg)
        self.DM = 0.0
        self.eDM = 0.0


    def __str__ (self):
        msg = ''
        msg = msg + "%10s\t%7.2f\t%7.2f\t%10.2f\t" % (self.Id, self.XC, self.YC, self.MAX)
        msg = msg + "%7.3f\t%7.3f\t%7.3f\t%7.3f\t" % (self.Mag, self.eMag, self.MagCal, self.eMagCal)
        msg = msg + "%4s\t%15.6f\t%10.1f\t%10.2f\t" % (self.Comment, self.MJD, self.Exptime, self.Sky)
        msg = msg + "%7.3f\t%7.3f\t%7.3f\t%6d\t%7.2f\t%7.3f\t" % (self.ZP, self.eZP, self.ChiZP, self.NZP, self.Airm, self.Coef)
        msg = msg + "%7.3f\t%7.3f" % (self.DM, self.eDM)
        return msg+os.linesep


    def __cmp__ (self, other):
        if self.MJD > other.MJD:
            return 1
        elif self.MJD == othr.MJD:
            return 0
        else:
            return -1




def findPercAreaBis (x,y,r,xp,yp):
    intersezioni = []
    xA = xp - 1
    sqr = r**2-(xA-x)**2
    if sqr >= 0:
        yA1 = y + math.sqrt(sqr)
        yA2 = y - math.sqrt(sqr)
        if yp-1 <= yA1 <= yp:
            intersezioni.append((xA,yA1,True,1))
        if yp-1 <= yA2 <= yp:
            intersezioni.append((xA,yA2,False,1))
    xB = xp
    sqr = r**2-(xB-x)**2
    if sqr >= 0:
        yB1 = y + math.sqrt(sqr)
        yB2 = y - math.sqrt(sqr)
        if yp-1 <= yB1 <= yp:
            intersezioni.append((xB,yB1,True,2))
        if yp-1 <= yB2 <= yp:
            intersezioni.append((xB,yB2,False,2))
    yC = yp - 1
    sqr = r**2-(yC-y)**2
    if sqr >= 0.0:
        xC1 = x + math.sqrt(sqr)
        xC2 = x - math.sqrt(sqr)
        if xp-1 <= xC1 <= xp:
            intersezioni.append((xC1,yC,True,3))
        if xp-1 <= xC2 <= xp:
            intersezioni.append((xC2,yC,False,3))
    yD = yp
    sqr = r**2-(yD-y)**2
    if sqr >= 0.0:
        xD1 = x + math.sqrt(sqr)
        xD2 = x - math.sqrt(sqr)
        if xp-1 <= xD1 <= xp:
            intersezioni.append((xD1,yD,True,4))
        if xp-1 <= xD2 <= xp:
            intersezioni.append((xD2,yD,False,4))
    if len(intersezioni) == 2:
#                area = (intersezioni[0][1]-(yp-1)+intersezioni[1][1]-(yp-1))/2.0
        if yp-1 >= y or yp <= y:
            if intersezioni[0][0] <= intersezioni[1][0]:
                area1 = (intersezioni[0][0]-(xp-1))*(intersezioni[0][1]-(yp-1))
                area3 = (xp-intersezioni[1][0])*(intersezioni[1][1]-(yp-1))
                if yp-1 >= y:
                    area2 = integFuct(intersezioni[0][0],intersezioni[1][0],x,y,r,yp)
                elif yp <= y:
                    area2 = integFuct(intersezioni[0][0],intersezioni[1][0],x,y,r,yp,False)
            else:
                area1 = (intersezioni[1][0]-(xp-1))*(intersezioni[1][1]-(yp-1))
                area3 = (xp-intersezioni[0][0])*(intersezioni[0][1]-(yp-1))
                if yp-1 >= y:
                    area2 = integFuct(intersezioni[1][0],intersezioni[0][0],x,y,r,yp)
                elif yp <= y:
                    area2 = integFuct(intersezioni[1][0],intersezioni[0][0],x,y,r,yp,False)
            area = area1 + area2 + area3
        else:
            if xp-1 >= x:
                if intersezioni[0][1] <= intersezioni[1][1]:
                    area = integFuct(intersezioni[0][1],intersezioni[1][1],y,x,r,xp)
                else:
                    area = integFuct(intersezioni[1][1],intersezioni[0][1],y,x,r,xp)
            else:
                if intersezioni[0][1] <= intersezioni[1][1]:
                    area = integFuct(intersezioni[0][1],intersezioni[1][1],y,x,r,xp,False)
                else:
                    area = integFuct(intersezioni[1][1],intersezioni[0][1],y,x,r,xp,False)
#                print area
#                print intersezioni
#                print
#                if intersezioni[0][3] in [1,2]:
#                        print Funct(intersezioni[0][0],x,y,r,intersezioni[0][2])
#                else:
#                        print Funct(intersezioni[0][1],y,x,r,intersezioni[0][2])
#                if intersezioni[1][3] in [1,2]:
#                        print Funct(intersezioni[1][0],x,y,r,intersezioni[1][2])
#                else:
#                        print Funct(intersezioni[1][1],y,x,r,intersezioni[1][2])
        if yp-1 >= y:
            return area
        elif yp <= y:
            return 1.0-area
        else:
            if xp-1 >= x:
                return area
            elif xp <= x:
                return 1-area
    else:
        dist = math.sqrt((x-xp)**2+(y-yp)**2)
        if dist < r:
            return 1.0
        else:
            return 0.0


def sumApert (table, x, y, r):
    if math.floor(x-r) < 1:
        xmin = 1
    else:
        xmin = int(math.floor(x-r))
    if math.ceil(x+r) > table.shape[1]:
        xmax = table.shape[1]
    else:
        xmax = int(math.ceil(x+r))
    if math.floor(y-r) < 1:
        ymin = 1
    else:
        ymin = int(math.floor(y-r))
    if math.ceil(y+r) > table.shape[0]:
        ymax = table.shape[0]
    else:
        ymax = int(math.ceil(y+r))
    field = table[(ymin-1):ymax,(xmin-1):xmax]
    tot = 0.0
#        npix = 0
    npixbis = 0
    maxf = 0.0
    for i in range(field.shape[1]):
        for l in range(field.shape[0]):
            dist = math.sqrt((x-(l+xmin-0.5))**2+(y-(i+ymin-0.5))**2)
            if dist <= r-0.5*math.sqrt(2):
                tot = tot + field[l,i]
#                                npix = npix + 1
                npixbis = npixbis + 1
                if field[l,i] > maxf:
                    cy,cx = i,l
                    maxf = field[l,i]
            elif r-0.5*math.sqrt(2) < dist <= r+0.5*math.sqrt(2):
#                                pa = findPercArea (x,y,r,l+xmin,i+ymin)
                pabis = findPercAreaBis (x,y,r,l+xmin,i+ymin)
                tot = tot + pabis*field[l,i]
#                                npix = npix + pa
                npixbis = npixbis + pabis
    #if math.fabs((math.pi*r**2-npixbis)/npixbis) > 1.0:
    #    sys.exit(1)
    return tot, npixbis, maxf






def computeMag (flux,back,ebg,npix,gain=1.0,ron=0.0,upsig=3):
    nflux = flux-npix*back
    enflux = math.sqrt(math.fabs(flux)*gain + npix*(ebg*gain)**2 + npix*ron**2)
#        print nflux,enflux,flux,back,ebg,npix
    if nflux > 0.0 and enflux > 0.0:
        emag = (2.5/math.log(10.0))*enflux/(nflux*gain)
        mag = -2.5*math.log10(nflux)
        if emag > 0.5:
            mag = -2.5*math.log10(upsig*enflux)
            emag = 99.0
    elif nflux <= 0.0 and enflux > 0.0:
        mag = -2.5*math.log10(upsig*enflux)
        emag = 99.0
    else:
        mag = 99
        emag = 99
    return mag,emag





def AverWeight(wlst,wei):
    if len(wlst) == 0:
        return None, None
    elif len(wlst) == 1:
        return wlst[0],wei[0]
    sum = 0.0
    wsum = 0.0
    for i in range(len(wlst)):
        sum = sum + wlst[i]*wei[i]**-2
        wsum = wsum + wei[i]**-2
#                print wlst[i],wei[i]
    err = 0.0
    ave = sum/wsum
    for i in range(len(wlst)):
        err = err + (ave-wlst[i])**2
    errf = math.sqrt(err/(len(wlst)-1))
#        print ave, errf/math.sqrt(len(wlst))
    return ave, errf/math.sqrt(len(wlst))



def averageZeroPoint (inplst, einplst, siglev = 2.0):
    wlst = copy.copy(inplst)
    ewlst = copy.copy(einplst)
    card = len(wlst)
    while True:
#                print wlst
#                print ewlst
        if len(wlst) < 1:
            return None,None
        elif len(wlst) == 1:
            return wlst[0],ewlst[0]
        elif len(wlst) == 2:
            return AverWeight(wlst,ewlst)
        elif 3 <= len(wlst) <= 10:
            wa = numpy.mean(wlst)
            dst = 0.0
            for i,l in zip(wlst,ewlst):
                dstil = math.fabs(wa-i)/l
                if dstil > dst:
                    dst = dstil
                    refi,refl = i,l
            if dst > 3:
                wlst.remove(refi)
                ewlst.remove(refl)
#                                print wa,refi,refl,dst
            else:
                return AverWeight(wlst,ewlst)
        else:
            wa = numpy.mean(wlst)
            ws = numpy.std(wlst,ddof=1)
            wmin, wmax = wa - siglev*ws, wa + siglev*ws
#                        print wa,ws,wmin,wmax
            for i,l in zip(wlst,ewlst):
                if not wmin <= i <= wmax:
                    wlst.remove(i)
                    ewlst.remove(l)
            if card != len(wlst):
                card = len(wlst)
            else:
                return AverWeight(wlst,ewlst)



def simplerAverageZeroPoint (inplst, einplst):
    wlst = copy.copy(inplst)
    ewlst = copy.copy(einplst)
    if len(wlst) < 1:
        return None,None
    elif len(wlst) == 1:
        return wlst[0],ewlst[0]
    else:
        wl = numpy.mean(wlst)
        ws = numpy.std(wlst,ddof=1)
        we = ws/math.sqrt(len(wlst))
        return wl,we



