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

History : (06/05/2013) First version.
        : (23/07/2015) python3 comparison.
"""

import os


from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from SRP.SRPCatalogue.GetSDSS import GetSDSS


class SDSS:
    # SDSS entries
    class CatEntries:
        def __init__ (self,id,ra,dec,u,eu,g,eg,r,er,i,ei,z,ez):
            self.Id = id
            self.RA = float(ra)
            self.DEC = float(dec)
            inpmag = AstroMagInput (u,eu)
            self.u = inpmag.Mag
            self.eu =inpmag.eMag
            inpmag = AstroMagInput (g,eg)
            self.g = inpmag.Mag
            self.eg =inpmag.eMag
            inpmag = AstroMagInput (r,er)
            self.r = inpmag.Mag
            self.er =inpmag.eMag
            inpmag = AstroMagInput (i,ei)
            self.i = inpmag.Mag
            self.ei =inpmag.eMag
            inpmag = AstroMagInput (z,ez)
            self.z = inpmag.Mag
            self.ez =inpmag.eMag

        
        def __str__ (self):
            msg = "%30s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%9.3f\t" % (self.u, self.eu)
            msg = msg + "%10.3f\t%9.3f\t" % (self.g, self.eg)
            msg = msg + "%10.3f\t%9.3f" % (self.r, self.er)
            msg = msg + "%10.3f\t%9.3f" % (self.i, self.ei)
            msg = msg + "%10.3f\t%9.3f" % (self.z, self.ez)
            return msg
            
 
        def __lt__ (self, other):
            return self.r < other.r
 
 
 
    
    def __init__ (self, ra, dec, radius=1.0, epoch=2000.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=epoch)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Epoch = 2000.0
        self.Radius = radius
        self.ListEntries = []
        
        
    def GetData(self):
        sdss = GetSDSS (self.RA,self.DEC,self.Radius)
        if len(sdss) == 0:
            return None
        for il in sdss:
            id = il['SDSS12']
            ra = il['RA_ICRS']
            dec = il['DE_ICRS']
            coord = AstroCoordInput(ra,dec)
            u = il['umag']
            eu = il['e_umag']
            g = il['gmag']
            eg = il['e_gmag']
            r = il['rmag']
            er = il['e_rmag']
            i = il['imag']
            ei = il['e_imag']
            z = il['zmag']
            ez = il['e_zmag']
            newinp = self.CatEntries(id,coord.RA,coord.DEC,u,eu,g,eg,r,er,i,ei,z,ez)
            # No duplicate entries
            for ii in self.ListEntries:
                if newinp.Id == ii.Id:
                    break
            else:
                self.ListEntries.append(newinp)
        return len(self.ListEntries)

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
        msg = msg + "Id\tRA\tDEC\tu\teu\tg\teg\tr\ter\ti\tei\tz\tez\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()


