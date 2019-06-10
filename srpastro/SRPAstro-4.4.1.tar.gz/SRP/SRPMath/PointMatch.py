""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 11/02/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (11/02/2012) First version.

"""

import math

from SRP.SRPMath.PointClass import Point




def PointMatch (reflist,objlist,tol=5.0,shx=0.0,shy=0.0,force=False):
#    print objlist
#    print reflist
    reqmtch = int(math.ceil(len(reflist)/2.))
    #
    for i in range(len(reflist)):
        for l in range(len(objlist)):
            #print i,l
            pref = Point(reflist[i])
            pobj = Point(objlist[l])
            distx, disty = pref.ShiftDist(pobj)
            #
            if force:
                distx, disty = shx, shy
            #
            assobj = []
            for ii in range(len(reflist)):
                for ll in range(len(objlist)):
                    if Point(reflist[ii],distx,disty).PointDist(Point(objlist[ll])) <= tol:
                        assobj.append((ii,ll))
                        break
            if len(assobj) >= reqmtch:
                return assobj, (distx, disty)
    #
    return [], (0.0,0.0)