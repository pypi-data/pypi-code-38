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

History : (24/10/2010) First version.
        : (23/07/2015) python3 comparison.
"""

import os


from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from .GetVizierCat import GetVizierCat
from .ParseVizierCat import ParseVizierCat


class USNO:
    # usno@eso
    usnocadcaddress = "vizier.hia.nrc.ca"
    usnocdsaddress = "vizier.u-strasbg.fr"
    # pars ra,dec,inner radius,outer radius, maxentries
    usnocadcquery = "/viz-bin/asu-acl?-source=usno-a2&-c.ra=%s&-c.dec=%s&-c.rm=%s/%s"
    usnocdsquery = "/viz-bin/asu-acl?-source=usno-a2&-c.ra=%s&-c.dec=%s&-c.rm=%s/%s"
    # USNO entries
    class CatEntries:
        def __init__ (self,id,ra,dec,r,b):
            self.Id = id
            self.RA = float(ra)
            self.DEC = float(dec)
            inpmag = AstroMagInput (r,0)
            self.R = inpmag.Mag
            inpmag = AstroMagInput (b,0)
            self.B = inpmag.Mag
            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t" % (self.R)
            msg = msg + "%10.3f" % (self.B)
            return msg
            
 
        def __lt__ (self, other):
            return self.R < other.R
 
    
    
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
                r = parseddata[i][3]
                b = parseddata[i][6]
                newinp = self.CatEntries(id,coord.RA,coord.DEC,r,b)
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
        msg = msg + "Id\tRA\tDEC\tR\tB\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
        
        