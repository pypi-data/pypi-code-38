""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 23/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (11/06/2011) First version.
        : (23/07/2015) python3 comparison.
"""

import os


from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from .GetVizierCat import GetVizierCat
from .ParseVizierCat import ParseVizierCat


class USNOB1:
    # usnob1@cds
    usnocdsaddress = "vizier.u-strasbg.fr"
    # pars ra,dec,inner radius,outer radius, maxentries
    usnocdsquery = "/viz-bin/asu-acl?-source=USNO-B1.0&-c.ra=%s&-c.dec=%s&-c.rm=%s/%s"
    # USNOB1 entries
    class CatEntries:
        def __init__ (self,id,ra,dec,b1,r1,b2,r2,i):
            self.Id = id
            self.RA = float(ra)
            self.DEC = float(dec)
            inpmag = AstroMagInput (b1,0)
            self.B1 = inpmag.Mag
            inpmag = AstroMagInput (r1,0)
            self.R1 = inpmag.Mag
            inpmag = AstroMagInput (b2,0)
            self.B2 = inpmag.Mag
            inpmag = AstroMagInput (r2,0)
            self.R2 = inpmag.Mag
            inpmag = AstroMagInput (i,0)
            self.I = inpmag.Mag
            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%10.3f\t" % (self.B1, self.R1)
            msg = msg + "%10.3f\t%10.3f\t" % (self.B2, self.R2)
            msg = msg + "%10.3f" % (self.I)
            return msg
            

        def __lt__ (self, other):
            return self.R1 < other.R1


    
    
    def __init__ (self, ra, dec, radius=1.0, epoch=2000.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=epoch)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Epoch = 2000.0
        self.Radius = radius
        self.ListEntries = []
        
        
    def GetData(self):
        QueryStr = self.usnocdsquery % (self.RA,self.DEC,0.0,self.Radius)
        data = GetVizierCat(self.usnocdsaddress,QueryStr)
        if data == None:
            QueryStr = self.usnocadcquery % (self.RA,self.DEC,0.0,self.Radius)
            data = GetVizierCat(self.usnocadcaddress,QueryStr)
        if data != None:
            parseddata = ParseVizierCat(data)
            for i in range(2,len(parseddata)):
                id = parseddata[i][0]
                ra = parseddata[i][1]
                dec = parseddata[i][2]
                coord = AstroCoordInput(ra,dec)
                b1 = parseddata[i][3]
                r1 = parseddata[i][10]
                b2 = parseddata[i][11]
                r2 = parseddata[i][12]
                im = parseddata[i][13]
                newinp = self.CatEntries(id,coord.RA,coord.DEC,b1,r1,b2,r2,im)
                # No duplicate entries
                for ii in self.ListEntries:
                    if newinp.Id == ii.Id:
                        break
                else:
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
        msg = msg + "Id\tRA\tDEC\tB1\tR1\tB2\tR2\tI\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
        
        