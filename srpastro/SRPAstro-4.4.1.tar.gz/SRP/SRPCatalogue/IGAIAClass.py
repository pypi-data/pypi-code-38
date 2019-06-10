""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 14/05/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (16/02/2016) First version.
        : (14/05/2019) Minor upgrade.
"""

import os
from SRP.SRPMath.AstroMagInput import AstroMagInput
from SRP.SRPMath.AstroCoordInput import AstroCoordInput
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from astropy import units as u
from astroquery.vizier import Vizier
from astroquery.vizier import Conf
import warnings


class IGAIA:
    Conf.row_limit = -1
    #  
    class CatEntries:
        def __init__ (self,objid,ra,dec,mb,emb,mr,emr,mg,emg):
            self.Id = objid
            self.RA = float(ra)
            self.DEC = float(dec)
            inpmag = AstroMagInput (mb,emb)
            self.B = inpmag.Mag
            self.eB = inpmag.eMag
            inpmag = AstroMagInput (mr,emr)
            self.R = inpmag.Mag
            self.eR = inpmag.eMag
            inpmag = AstroMagInput (mg,emg)
            self.G = inpmag.Mag
            self.eG = inpmag.eMag
        
        def __str__ (self):
            msg = "%20s\t%15.6f\t%15.6f\t" % (self.Id, self.RA, self.DEC)
            msg = msg + "%7.2f\t%7.2f\t" % (self.B, self.eB)
            msg = msg + "%7.2f\t%7.2f\t" % (self.R, self.eR)
            msg = msg + "%7.2f\t%7.2f" % (self.G, self.eG)
            return msg
            

        def __lt__ (self, other):
            return self.R < other.R

    
    
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
            restab = Vizier.query_region(crd, radius=self.Radius*u.arcmin, catalog=["I/324/igsl3"])
        except:
            restab = []
        warnings.resetwarnings()
        #
        if len(restab) > 0:
            data = restab[0]
            for i in data:
                objid = 'IGAIA'
                ra = i['RAJ2000']
                dec = i['DEJ2000']
                coord = AstroCoordInput(ra,dec)
                mb = i['magBJ']
                emb = i['e_magBJ']
                mr = i['magRF']
                emr = i['e_magRF']
                mg = i['magG']
                emg = i['e_magG']
                newinp = self.CatEntries(objid,coord.RA,coord.DEC,mb,emb,mr,emr,mg,emg)
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
        msg = msg + "Id\tRA\tDEC\tB\teB\tR\teR\tG\teG\n"
        msg = msg + "---------\n"
        msg = msg + str(self)
        msg = msg + "EOD\n"
        return msg

        
        
    def sort(self):
        self.ListEntries.sort()
        
        
