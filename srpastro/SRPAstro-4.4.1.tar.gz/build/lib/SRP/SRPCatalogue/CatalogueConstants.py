""" Utility functions and classes for SRP

Context : SRP
Module  : Catalogue.py
Version : 1.0.11
Author  : Stefano Covino
Date    : 14/05/2019
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (29/09/2010) First version.
        : (05/10/2010) AstroWise catalogue.
        : (24/10/2010) USNO-A2 catalogue.
        : (14/12/2010) NIR catalogue collection.
        : (28/03/2011) AGN optical standard stars.
        : (11/06/2011) USNOB1 catalogue.
        : (06/05/2013) SDSS catalogue.
        : (26/07/2013) APASS catalogue.
        : (29/07/2015) Smith et al. ugriz catalogue.
        : (14/02/2016) SkyBot query.
        : (17/02/2016) IGAIA.
        : (14/05/2019) SDSS.
"""

# Available catalogues
APS = "APASS Catalogue"
BSC = "Bright Stars Catalogue"
TMC = "2MASS Catalogue"
SSC = "Stetson Optical Standard Stars"
AWC = "AstroWise Standard Stars"
USB = "USNO-B1.0 Catalogue" 
USC = "USNO-A2 Catalogue"
NCC = "NIR Catalogue Collection"
AGNOPT = "AGN Optical Standard Stars"
SDSS = "Sloan Digital Sky Survey"
SMI = "Smith et al. ugriz Standard Stars"
SKB = "SkyBot Minor Planet"
IGAIA = "Initial GAIA catalogue"
SMBD = "Simbad catalogue"

SRPCatalDict = {'APS' : APS, 'BSC' : BSC, 'TMC' : TMC, 'SSC' : SSC, 'AWC' : AWC, 'USB' : USB, 'USC' : USC, 'NCC' : NCC, 'AGNOPT' : AGNOPT, 'SKB' : SKB, 'SDSS' : SDSS, 'SMI' : SMI, 'IGAIA' : IGAIA, 'SMBD' : SMBD}

