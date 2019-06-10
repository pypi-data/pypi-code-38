""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.1.1
Author  : Stefano Covino
Date    : 29/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (29/09/2010) First version.
        : (16/10/2010) Output suited for skycat.
        : (05/02/2012) Better path management.
        : (23/07/2015) python3 comparison.
        : (29/07/2015) python3 porting.
"""

import os, os.path


import SRP
from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from SRP.SRPMath.AngularDistance import AngularDistance
from SRP.SRPSystem.SRPPath import SRPPath



class StetsonOpticalStandardStars:
    basepath = SRPPath()
    filename = 'StetsonStandardStars.dat'
    catpath = os.path.join(basepath,'SRPData','Catalogues','StetsonStandardStars','JohnsonSystem',filename)
    # Catalogue entries
    class CatEntries:
        def __init__ (self, xxx_todo_changeme):
            # Id
            (id,ra,dec,b,eb,nb,ntb,v,ev,nv,ntv,r,er,nr,ntr,i,ei,ni,nti,var) = xxx_todo_changeme
            self.Id = id
            # Coord
            coord = AstroCoordInput(ra,dec)
            self.RA = coord.RA
            self.DEC = coord.DEC
            # B mag
            inpmag = AstroMagInput (b,eb)
            self.B = inpmag.Mag
            self.eB =inpmag.eMag
            self.NB = int(nb)
            self.NTotB = int(ntb)
            # V mag
            inpmag = AstroMagInput (v,ev)
            self.V = inpmag.Mag
            self.eV =inpmag.eMag
            self.NV = int(nv)
            self.NTotV = int(ntv)
            # R mag
            inpmag = AstroMagInput (r,er)
            self.R = inpmag.Mag
            self.eR =inpmag.eMag
            self.NR = int(nr)
            self.NTotR = int(ntr)
            # I mag
            inpmag = AstroMagInput (i,ei)
            self.I = inpmag.Mag
            self.eI =inpmag.eMag
            self.NI = int(ni)
            self.NTotI = int(nti)
            # Variabilit
            self.Var = var

            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%9.3f\t" % (self.B, self.eB)
            msg = msg + "%10.3f\t%9.3f\t" % (self.V, self.eV)
            msg = msg + "%10.3f\t%9.3f\t" % (self.R, self.eR)
            msg = msg + "%10.3f\t%9.3f" % (self.I, self.eI)            
            return msg


        def __lt__ (self, other):
            return self.V < other.V
    
    
    def __init__ (self, ra, dec, radius=1.0, epoch=2000.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=epoch)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Radius = radius/60.0
        self.ListEntries = []
        
        
    def GetData(self):
        f = open(self.catpath)
        data = f.readlines()
        f.close()
        if data != None:
            for entry in data:
                parseddata = entry.split()
                newinp = self.CatEntries(parseddata)
                if AngularDistance((self.RA,self.DEC),(newinp.RA,newinp.DEC)) <= self.Radius:
                    self.ListEntries.append(newinp)
            return len(self.ListEntries)
        else:
            return None

    def __str__(self):
        msg = ''
        for i in self.ListEntries:
            msg = msg + str(i) + os.linesep
        return msg


    def Skycat(self, outname='SRP.cat'):
        msg = ''
        msg = msg + "long_name: SRP catalog for file %s\n" % (outname)
        msg = msg + "short_name: %s\n" % (outname)
        msg = msg + "url: ./%s\n" % (outname)
        msg = msg + "symbol: {} {circle blue} 4\n"
        msg = msg + "id_col: 0\n"
        msg = msg + "ra_col: 1\n"
        msg = msg + "dec_col: 2\n"
        msg = msg + "Id\tRA\tDEC\tB\teB\tV\teV\tR\teR\tI\teI\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg
        
        
    def sort(self):
        self.ListEntries.sort()