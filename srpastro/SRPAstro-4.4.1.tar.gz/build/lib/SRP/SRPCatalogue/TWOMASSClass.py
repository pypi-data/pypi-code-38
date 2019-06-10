""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.2.0
Author  : Stefano Covino
Date    : 23/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (06/08/2010) First version.
        : (04/09/2010) Different import rules.
        : (27/09/2010) Minor correction.
        : (29/09/2010) Skycat output.
        : (13/10/2010) No more maximum number of objects in output.
        : (16/10/2010) Output better suited for skycat.
        : (24/10/2010) Better check for removing duplicate entries.
        : (23/07/2015) python3 comparison.
"""

import os


from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from .GetVizierCat import GetVizierCat
from .ParseVizierCat import ParseVizierCat


class TWOMASS:
    # twomass@cadc
    twomasscadcaddress = "vizier.hia.nrc.ca"
    twomasscdsaddress = "vizier.u-strasbg.fr"
    # pars ra,dec,inner radius,outer radius, maxentries
    twomasscadcquery = "/viz-bin/asu-acl?-source=2mass&-c.ra=%s&-c.dec=%s&-c.rm=%s/%s"
    twomasscdsquery = "/viz-bin/asu-acl?-source=II/246&-c.ra=%s&-c.dec=%s&-c.rm=%s/%s"
    # 2mass entries
    class CatEntries:
        def __init__ (self,id,ra,dec,j,ej,h,eh,k,ek):
            self.Id = id
            self.RA = float(ra)
            self.DEC = float(dec)
            inpmag = AstroMagInput (j,ej)
            self.J = inpmag.Mag
            self.eJ =inpmag.eMag
            inpmag = AstroMagInput (h,eh)
            self.H = inpmag.Mag
            self.eH =inpmag.eMag
            inpmag = AstroMagInput (k,ek)
            self.K = inpmag.Mag
            self.eK =inpmag.eMag
            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%9.3f\t" % (self.J, self.eJ)
            msg = msg + "%10.3f\t%9.3f\t" % (self.H, self.eH)
            msg = msg + "%10.3f\t%9.3f" % (self.K, self.eK)
            return msg
            


        def __lt__ (self, other):
            return self.H < other.H



    def __init__ (self, ra, dec, radius=1.0, epoch=2000.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=epoch)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Epoch = 2000.0
        self.Radius = radius
        self.ListEntries = []
        
        
    def GetData(self):
        QueryStr = self.twomasscdsquery % (self.RA,self.DEC,0.0,self.Radius)
        data = GetVizierCat(self.twomasscdsaddress,QueryStr)
        if data == None:
            QueryStr = self.twomasscadcquery % (self.RA,self.DEC,0.0,self.Radius)
            data = GetVizierCat(self.twomasscadcaddress,QueryStr)
        if data != None:
            parseddata = ParseVizierCat(data)
            for i in range(2,len(parseddata)):
                id = parseddata[i][0]
                ra = parseddata[i][1]
                dec = parseddata[i][2]
                coord = AstroCoordInput(ra,dec)
                j = parseddata[i][3]
                ej = parseddata[i][4]
                h = parseddata[i][5]
                eh = parseddata[i][6]
                k = parseddata[i][7]
                ek = parseddata[i][8]
                newinp = self.CatEntries(id,coord.RA,coord.DEC,j,ej,h,eh,k,ek)
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
        msg = msg + "Id\tRA\tDEC\tJ\teJ\tH\teH\tK\teK\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
