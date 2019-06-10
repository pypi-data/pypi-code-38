""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 17/02/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (17/02/2016) First version.
"""

import os
from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from astropy import units as u
from astroquery.simbad import Simbad
from astroquery.vizier import Conf
import warnings


class SIMBAD:
    Conf.row_limit = -1
    #  
    class CatEntries:
        def __init__ (self,objid,ra,dec):
            self.Id = objid
            self.RA = float(ra)
            self.DEC = float(dec)
        
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f" % (self.Id, self.RA, self.DEC)
            return msg
            

        def __lt__ (self, other):
            return self.RA < other.RA

    
    
    def __init__ (self, ra, dec, radius=5.0):
        inpcoord = AstroCoordInput(ra,dec,inp_equinox=2000)
        self.RA = inpcoord.RA
        self.DEC = inpcoord.DEC
        self.Radius = radius
        self.ListEntries = []
        
        
    def GetData(self):
        crd = SkyCoord(ra=self.RA*u.degree, dec=self.DEC*u.degree)
        warnings.filterwarnings('ignore', category=UserWarning, append=True)
        try:
            restab = Simbad.query_region(crd, radius=self.Radius*u.arcmin)
        except:
            return None
        warnings.resetwarnings()
        #
        data = restab
        for i in data:
            objid = i['MAIN_ID'].decode()
            ra = i['RA']
            dec = i['DEC']
            coord = AstroCoordInput(ra,dec)
            newinp = self.CatEntries(objid,coord.RA,coord.DEC)
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
        msg = msg + "Id\tRA\tDEC\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
        
        