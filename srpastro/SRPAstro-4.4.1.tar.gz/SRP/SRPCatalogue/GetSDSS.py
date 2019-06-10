""" Utility functions and classes for SRP

Context : SRP
Module  : SRPGW
Version : 1.0.0
Author  : Stefano Covino
Date    : 14/05/2019
E-mail  : stefano.covino@inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : 

Remarks :

History : (14/05/2019) First version.
"""

from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.coordinates import search_around_sky
from astropy import units as u
from astroquery.vizier import Vizier
import warnings




def GetSDSS(rad,decd,rds):
    #
    crd = SkyCoord(ra=rad*u.degree, dec=decd*u.degree)
    #
    warnings.filterwarnings('ignore', category=UserWarning, append=True)
    try:
        restab = Vizier.query_region(crd, radius=rds*u.arcmin, catalog=["SDSS12"])
    except:
        restab = []
    warnings.resetwarnings()
    if len(restab) == 0:
        return []
    else:
        return restab[0]
