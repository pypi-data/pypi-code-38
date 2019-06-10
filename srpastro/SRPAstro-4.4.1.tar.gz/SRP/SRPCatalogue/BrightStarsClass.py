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
        : (16/10/2010) Output better suited for skycat.
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



class BrightStars:
    basepath = SRPPath()
    filename = 'BrightStars.dat'
    catpath = os.path.join(basepath,'SRPData','Catalogues','BrightStarCatalogue',filename)
    # Catalogue entries
    class CatEntries:
        def __init__ (self, xxx_todo_changeme):
            # Id & name
            (id,name,ra,dec,mag,dflag,cls,spt) = xxx_todo_changeme
            self.Id = id
            self.Name = name
            # Coord
            coord = AstroCoordInput(ra,dec)
            self.RA = coord.RA
            self.DEC = coord.DEC
            # Mag
            inpmag = AstroMagInput (mag,0)
            self.Mag = inpmag.Mag
            # Double flag
            self.DoubleFlag = dflag
            # Class
            self.Cls = cls
            # Spectral type
            self.SpType = spt

            
        def __str__ (self):
            msg = "%6s\t%20s\t%15.6f\t%15.6f\t" % (self.Id, self.Name, self.RA, self.DEC)
            msg = msg + "%10.3f\t" % (self.Mag)
            msg = msg + "%3s\t%6s\t" % (self.DoubleFlag, self.Cls)
            msg = msg + "%7s" % (self.SpType)
            return msg


        def __lt__ (self, other):
            return self.Mag < other.Mag



    
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
            for e in data:
                newinp = self.CatEntries((str(e[0:5]),str(e[6:28]),str(e[29:31])+':'+str(e[32:34])+':'+str(e[35:41]),
                    str(e[41:45])+':'+str(e[46:48])+':'+str(e[49:53]),str(e[55:59]),str(e[60:62]),str(e[68:72]),str(e[73:79])))
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
        msg = msg + "ra_col: 2\n"
        msg = msg + "dec_col: 3\n"
        msg = msg + "Id\tName\tRADEG\tDECDEG\tMag\tDoubleFlag\tClassification\tSpectralType\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg
        
        
    def sort(self):
        self.ListEntries.sort()
