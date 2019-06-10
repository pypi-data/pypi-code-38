""" 

Context : SRP
Module  : Tables.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 29/07/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (09/11/2010) First version.
        : (29/07/2013) Returns objects satisfying and not satisfying the given criteria.

"""


from SRP.SRPMath.AngularDistance import AngularDistance
from SRP.SRPMath.CartesianDistance import CartesianDistance


def FindObjects(inplist,cols,coord,tol,angular=True):
    objs = []
    nobjsout = []
    xo = coord[0]
    yo = coord[1]
    for en in inplist:
        enl = en.split()
        try:
            x = float(enl[cols[0]-1])
            y = float(enl[cols[1]-1])
        except ValueError:
            return None
        if angular:
            dist = AngularDistance((x,y),(xo,yo))
        else:
            dist = CartesianDistance ((x,y),(xo,yo))
        if dist <= tol:
            objs.append((en,dist))
        else:
            nobjsout.append(en)
    objs.sort(key=lambda z: z[1])
    objsout = []
    for e in objs:
        objsout.append(e[0])
    return objsout, nobjsout
    
