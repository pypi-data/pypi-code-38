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

History : (14/12/2010) First version.
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



class NIRStandardStars:
    basepath = SRPPath()
    filename = 'NIRSTD.txt'
    catpath = os.path.join(basepath,'SRPData','Catalogues','NIRCatalogueCollection','JohnsonSystem',filename)
    # Catalogue entries
    class CatEntries:
        def __init__ (self, xxx_todo_changeme):
            # Id
            (id,ra,dec,sp,j,h,k,ks,l,m,lp,mp) = xxx_todo_changeme
            self.Id = id
            # Coord
            coord = AstroCoordInput(ra,dec)
            self.RA = coord.RA
            self.DEC = coord.DEC
            # Spectral type
            self.SpType = sp
            # J mag
            inpmag = AstroMagInput (j,0)
            self.J = inpmag.Mag
            # H mag
            inpmag = AstroMagInput (h,0)
            self.H = inpmag.Mag
            # K mag
            inpmag = AstroMagInput (k,0)
            self.K = inpmag.Mag
            # Ks mag
            inpmag = AstroMagInput (ks,0)
            self.Ks = inpmag.Mag
            # L mag
            inpmag = AstroMagInput (l,0)
            self.L = inpmag.Mag
            # M mag
            inpmag = AstroMagInput (m,0)
            self.M = inpmag.Mag
            # Lp mag
            inpmag = AstroMagInput (lp,0)
            self.Lp = inpmag.Mag
            # Mp mag
            inpmag = AstroMagInput (mp,0)
            self.Mp = inpmag.Mag

            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10s\t" % (self.SpType)
            msg = msg + "%10.3f\t%10.3f\t" % (self.J, self.H)
            msg = msg + "%10.3f\t%10.3f\t" % (self.K, self.Ks)
            msg = msg + "%10.3f\t%10.3f\t" % (self.L, self.M)
            msg = msg + "%10.3f\t%10.3f" % (self.Lp, self.Mp)            
            return msg
            

        def __lt__ (self, other):
            return self.H < other.H


    
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
        setIds = []
        if data != None:
            for entry in data:
                parseddata = entry.split()
                newinp = self.CatEntries(parseddata)
                if AngularDistance((self.RA,self.DEC),(newinp.RA,newinp.DEC)) <= self.Radius and (newinp.Id not in setIds):
                    self.ListEntries.append(newinp)
                    setIds.append(newinp.Id)
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
        msg = msg + "Id\tRA\tDEC\tSpType\tJ\tH\tK\tKs\tL\tM\tLp\tMp\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg
        
        
    def sort(self):
        self.ListEntries.sort()