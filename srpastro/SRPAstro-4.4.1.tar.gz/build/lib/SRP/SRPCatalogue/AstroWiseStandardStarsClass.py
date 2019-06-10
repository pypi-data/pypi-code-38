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

History : (05/10/2010) First version.
        : (15/10/2010) Wrong output for SDSS filters.
        : (16/10/2010) Output better suited for skycat.
        : (05/02/2012) Better path management.
        : (07/01/2013) Better formatting for output.
        : (23/07/2015) python3 comparison.

"""

import os, os.path

import atpy, numpy

import SRP
from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from SRP.SRPMath.AngularDistance import AngularDistance
from SRP.SRPSystem.SRPPath import SRPPath



class AstroWiseStandardStars:
    basepath = SRPPath()
    filename = 'cal569E_v11.fits'
    catpath = os.path.join(basepath,'SRPData','Catalogues','AstroWiseStandardStars',filename)
    # Catalogue entries
    class CatEntries:
        def __init__ (self, xxx_todo_changeme):
            # Id
            (id,ra,dec,u,eu,b,eb,v,ev,r,er,i,ei,su,esu,sg,esg,sr,esr,si,esi,sz,esz) = xxx_todo_changeme
            self.Id = id
            # Coord
            coord = AstroCoordInput(ra,dec)
            self.RA = coord.RA
            self.DEC = coord.DEC
            # U mag
            inpmag = AstroMagInput (u,eu)
            self.U = inpmag.Mag
            self.eU =inpmag.eMag
            # B mag
            inpmag = AstroMagInput (b,eb)
            self.B = inpmag.Mag
            self.eB =inpmag.eMag
            # V mag
            inpmag = AstroMagInput (v,ev)
            self.V = inpmag.Mag
            self.eV =inpmag.eMag
            # R mag
            inpmag = AstroMagInput (r,er)
            self.R = inpmag.Mag
            self.eR =inpmag.eMag
            # I mag
            inpmag = AstroMagInput (i,ei)
            self.I = inpmag.Mag
            self.eI =inpmag.eMag
            # u mag
            inpmag = AstroMagInput (su,esu)
            self.u = inpmag.Mag
            self.eu =inpmag.eMag
            # g mag
            inpmag = AstroMagInput (sg,esg)
            self.g = inpmag.Mag
            self.eg =inpmag.eMag
            # r mag
            inpmag = AstroMagInput (sr,esr)
            self.r = inpmag.Mag
            self.er =inpmag.eMag
            # i mag
            inpmag = AstroMagInput (si,esi)
            self.i = inpmag.Mag
            self.ei =inpmag.eMag
            # z mag
            inpmag = AstroMagInput (sz,esz)
            self.z = inpmag.Mag
            self.ez =inpmag.eMag
            # sexcoord
            self.Coord = coord

            
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%10.3f\t%9.3f\t" % (self.U, self.eU)
            msg = msg + "%10.3f\t%9.3f\t" % (self.B, self.eB)
            msg = msg + "%10.3f\t%9.3f\t" % (self.V, self.eV)
            msg = msg + "%10.3f\t%9.3f\t" % (self.R, self.eR)
            msg = msg + "%10.3f\t%9.3f\t" % (self.I, self.eI)            
            msg = msg + "%10.3f\t%9.3f\t" % (self.u, self.eu)
            msg = msg + "%10.3f\t%9.3f\t" % (self.g, self.eg)
            msg = msg + "%10.3f\t%9.3f\t" % (self.r, self.er)
            msg = msg + "%10.3f\t%9.3f\t" % (self.i, self.ei)
            msg = msg + "%10.3f\t%9.3f" % (self.z, self.ez)
            msgo = "".join(i for i in msg if 0 < ord(i) < 128)
            return "\t".join(msgo.split())
            


        def __lt__ (self, other):
            return self.V < other.V


    
    def __init__ (self, ra, dec, radius=1.0, epoch=2000.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=epoch)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Radius = radius/60.0
        self.ListEntries = []
        
        
    def GetData(self):
        tb = atpy.Table(self.catpath,type='fits')
        for i in range(len(tb)):
            if AngularDistance((self.RA,self.DEC),(tb.Ra[i],tb.Dec[i])) <= self.Radius:
                datum = self.CatEntries((tb.Name[i],tb.Ra[i],tb.Dec[i],tb.JohnsonU[i],tb.JohnsonU_err[i],
                        tb.JohnsonB[i],tb.JohnsonB_err[i],tb.JohnsonV[i],tb.JohnsonV_err[i],
                        tb.CousinsR[i],tb.CousinsR_err[i],tb.CousinsI[i],tb.CousinsI_err[i],
                        tb.SloanU[i],tb.SloanU_err[i],tb.SloanG[i],tb.SloanG_err[i],
                        tb.SloanR[i],tb.SloanR_err[i],tb.SloanI[i],tb.SloanI_err[i],
                        tb.SloanZ[i],tb.SloanZ_err[i]))
                self.ListEntries.append(datum)
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
        msg = msg + "Id\tRA\tDEC\tJohnsonU\teJohnsonU\tJohnsonB\teJohnsonB\tJohnsonV\teJohnsonV\tCousinsR\teCousinsR\t"
        msg =  msg + "CousinsI\teCousinsI\tSloanU\teSloanU\tSloanG\teSloanG\tSloanR\teSloanR\tSloanI\teSloanI\tSloanZ\teSloanZ\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg
        
        
    def sort(self):
        self.ListEntries.sort()