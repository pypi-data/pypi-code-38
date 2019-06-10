""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 02/08/2014
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : 

History : (02/08/2014) First version.

"""

import warnings
from astroquery.simbad import Simbad
from SRP.SRPMath.AstroCoordInput import AstroCoordInput



class SimbadName:
    def __init__ (self, name):
        self.Name = name

        
        
    def GetData(self):
        d = Simbad.query_object(self.Name)
        return d
        

    def GetCoords(self):
        warnings.resetwarnings()
        warnings.filterwarnings('ignore', category=UserWarning, append=True)
        d = self.GetData()
        warnings.resetwarnings() 
        warnings.filterwarnings('always', category=UserWarning, append=True)
        #
        try:
            ra = d['RA'].data[0]
            dec = d['DEC'].data[0]
        except KeyError:
            return None
        except IndexError:
            return None
        #
        rap = ra.replace(' ',':')
        decp = dec.replace(' ',':')
        #
        return AstroCoordInput(rap,decp)
        

 