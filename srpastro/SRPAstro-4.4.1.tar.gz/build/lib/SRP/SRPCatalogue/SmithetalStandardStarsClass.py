""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 29/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (29/07/2015) First version.
"""

import os, os.path


import SRP
from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from SRP.SRPMath.AngularDistance import AngularDistance
from SRP.SRPSystem.SRPPath import SRPPath



class SmithetalStandardStars:
    basepath = SRPPath()
    filename = 'smithetalugrizcat.dat'
    catpath = os.path.join(basepath,'SRPData','Catalogues','SmithetalStandardStars',filename)
    # Catalogue entries
    class CatEntries:
        def __init__ (self, xxx_todo_changeme):
            # Id
            (id,ra,dec,u,eu,g,eg,r,er,i,ei,z,ez) = xxx_todo_changeme
            self.Id = id
            # Coord
            coord = AstroCoordInput(ra,dec)
            self.RA = coord.RA
            self.DEC = coord.DEC
            # u mag
            inpmag = AstroMagInput (u,eu)
            self.u = inpmag.Mag
            self.eu =inpmag.eMag
            # g mag
            inpmag = AstroMagInput (g,eg)
            self.g = inpmag.Mag
            self.eg =inpmag.eMag
            # r mag
            inpmag = AstroMagInput (r,er)
            self.r = inpmag.Mag
            self.er =inpmag.eMag
            # i mag
            inpmag = AstroMagInput (i,ei)
            self.i = inpmag.Mag
            self.ei =inpmag.eMag
            # z mag
            inpmag = AstroMagInput (z,ez)
            self.z = inpmag.Mag
            self.ez =inpmag.eMag

            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%9.3f\t" % (self.u, self.eu)
            msg = msg + "%10.3f\t%9.3f\t" % (self.g, self.eg)
            msg = msg + "%10.3f\t%9.3f\t" % (self.r, self.er)
            msg = msg + "%10.3f\t%9.3f\t" % (self.i, self.ei)
            msg = msg + "%10.3f\t%9.3f" % (self.z, self.ez)
            return msg


        def __lt__ (self, other):
            return self.r < other.r
    
    
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
        msg = msg + "Id\tRA\tDEC\tu\teu\tg\teg\tt\tet\ti\tei\tz\tez\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg
        
        
    def sort(self):
        self.ListEntries.sort()

