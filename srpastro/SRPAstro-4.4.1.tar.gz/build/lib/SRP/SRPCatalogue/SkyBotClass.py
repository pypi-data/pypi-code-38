""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 14/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (14/02/2016) First version.
"""

import os
from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from .GetVizierCat import GetVizierCat


class SkyBot:
    skybotaddress = "vo.imcce.fr"
    # pars epoch (JD),ra (deg), dec (deg), radius (arcsec), maxposerror (arcsec)
    skybotquery = "/webservices/skybot/skybotconesearch_query.php?-ep=%s&-ra=%.5f&-dec=%.5f&-rs=%.1f&-mime=text&-outout=object&-filter=%.1f&-from=SRP"
    # SkyBot entries
    
    
    
    class CatEntries:
        def __init__ (self,objid,ra,dec,objclass,vmag,poserr,cdist):
            self.Id = objid
            self.RA = float(ra)
            self.DEC = float(dec)
            self.Class = objclass
            inpmag = AstroMagInput (vmag,0)
            self.V = inpmag.Mag
            self.PosErr = poserr
            self.CDist = cdist
            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%s\t%10.2f\t" % (self.Class, self.V)
            msg = msg + "%10.1f\t%10.1f" % (self.PosErr, self.CDist)
            return msg
            

        def __lt__ (self, other):
            return self.CDist < other.CDist


    
    
    def __init__ (self, ra, dec, radius=5.0, time=2000.0, maxerr=10):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=2000)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Epoch = time
        self.Radius = radius
        self.MaxError = maxerr
        self.ListEntries = []
        
        
    def GetData(self):
        QueryStr = self.skybotquery % (self.Epoch,self.RA,self.DEC,self.Radius,self.MaxError)
        data = GetVizierCat(self.skybotaddress,QueryStr)
        #
        if data != None:
            for i in data:
                il = i.split('|')
                if len(il) < 7:
                    return 0
                objid = il[1]
                ra = float(il[2])*15.0
                dec = float(il[3])
                coord = AstroCoordInput(ra,dec)
                objclass = il[4]
                objvmag = float(il[5])
                poserr = float(il[6])
                cdist = float(il[7])
                newinp = self.CatEntries(objid,coord.RA,coord.DEC,objclass,objvmag,poserr,cdist)
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
        msg = msg + "Id\tRA\tDEC\tClass\tV\tPosErr\tCDist\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
        
        