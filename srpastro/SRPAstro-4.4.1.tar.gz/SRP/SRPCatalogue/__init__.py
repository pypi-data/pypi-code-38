""" Init file for SRPCatalogue

Context : SRP
Module  : Catalogue
Version : 1.7.0
Author  : Stefano Covino
Date    : 14/05/2019
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.me.oa-brera.inaf.it/utenti/covino


Usage   : to be imported

Remarks :

History : (29/09/2010) First named version.
        : (05/10/2010) AstroWise class.
        : (14/12/2010) NIR collection class.
        : (28/03/2011) AGN optical standard stars.
        : (11/06/2011) USNOB1 class.
        : (15/04/2013) SDSS query script.
        : (06/05/2013) SDSS class.
        : (26/07/2013) APASS class
        : (02/08/2014) SIMBAD name resolver.
        : (29/07/2015) Smith et al. ugriz standard stars.
        : (14/02/2016) SkyBot query.
        : (17/02/2016) IGAIA query.
        : (14/05/2019) SDSS query.
"""



__all__ = ['AGNOptRefStarsClass', 'APASSClass', 'AstroWiseStandardStarsClass', 'BrightStarClass',
           'CatalogueConstants', 'GetSDSS', 'GetVizierCat', 'IGAIAClass', 'NIRStandardStarsClass',
           'ParseVisierCat', 'SDSSClass', 'SimbadNameClass', 'SimbadClass', 'SkyBotClass',
           'SmithetalStandardStarsClass', 'StetsonJohnsonStandardStarsClass', 'TWOMASSClass',
           'USNOB1Class', 'USNOClass']

