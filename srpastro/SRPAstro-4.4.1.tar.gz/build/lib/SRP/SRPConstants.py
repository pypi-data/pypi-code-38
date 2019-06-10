""" Constants, functions and classes for SRP

Context : SRP
Module  : SRPConstants.py
Version : 1.15.2
Status  : approved
Author  : Stefano Covino, Daniele Malesani
Date    : 17/01/2019
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.merate.mi.astro.it/~covino
Purpose : Collection of constants, functions and classes for SRP.

Usage   : to be imported

Remarks :

History : (20/05/2003) First version.
        : (21/05/2003) New constant.
        : (23/05/2003) New constants.
        : (24/05/2003) Shifted file constant and xcorrd2d
        : (26/05/2003) New constants for alignment.
        : (29/05/2003) Sectractor added.
        : (30/05/2003) Lower detect_minarea
        : (09/06/2003) Setup.
        : (12/06/2003) New setup file name and format.
        : (13/06/2003) New setup output.
        : (15/06/2003) Pre-selected keyword files.
        : (08/09/2003) Error for magnitudes or fluxes
        : (09/09/2003) Speed of light.
        : (20/09/2003) SExtractor parameter set dictionary.
        : (02/10/2003) Extinction curve environment dictionaries.
        : (07/10/2003) Available Catalogues.
        : (10/10/2003) Aperture magnitudes in output.
        : (14/10/2003) New file categoris.
        : (17/10/2003) Minor improvements to SRP Sextrator files.
        : (27/10/2003) Percentage of common objects.
        : (20/12/2003) Site coordinate dictionaries.
        : (03/01/2004) Improvement to classification keywords.
        : (11/10/2004) TNGDOLORESIMA parameters.
        : (25/10/2004) DAOPHOT file extentions and constants.
        : (25/12/2004) Asiago AFOSC and VLT ISAAC imaging keywords.
        : (18/02/2005) VLT FORS spectroscopy keywords and new constants.
        : (16/04/2005) New keyword in the TNGDOLORESIMA set.
        : (03/07/2005) Star burst galaxy data.
        : (14/07/2005) REM/ROSS photometric parameters.
        : (23/07/2005) NTTEMMIIMA parameters.
        : (18/09/2005) Improvements to VLT FORS spectroscopy data.
        : (26/09/2005) TNGNICSIMA parameter set.
        : (01/12/2005) Minor corrections.
        : (13/04/2006) Better porting to cygwin.
        : (01/05/2006) New parameters for ISAAC/SOFI.
        : (09/06/2006) Different output file for skycat format.
        : (29/12/2006) NOTAFOSCIMA parameters.
        : (05/01/2007) Minor correction.
        : (13/04/2007) 2.2m CAFOS imaging parameters.
        : (18/06/2007) Minor corrections.
        : (03/07/2007) DFOSC Danish parameters.
        : (13/07/2007) NACO imaging parameters.
        : (15/07/2007) TNG NICS and REM ROSS imaging parameters.
        : (29/10/2007) Minor improvements. NTT SOFI imaging parameters.
        : (21/11/2007) New file names.
        : (30/11/2007) New observing site.
        : (19/12/2007) GEMINI-N observing site. Corrections to coordinates.
        : (05/09/2008) VLTFOTSIPOL added.
        : (09/10/2008) Photometric parameter set for REMIR.
        : (15/10/2008) Map file parameters.
        : (22/10/2008) MyPhotom parameters.
        : (13/11/2008) Warp parameters.
        : (09/04/2009) Addition to keyword file.
        : (15/02/2010) New NACO parameters.
        : (28/02/2010) X-shooter added.
        : (12/04/2010) X-shooter parameters updated.
        : (11/08/2010) 2MASS catalogue.
        : (16/08/2010) TNG Dolores spectroscopy data.
        : (20/08/2010) Exposure map parameters.
        : (24/09/2010) Version variable.
        : (01/10/2010) SExtractor command names removed.
        : (28/10/2010) No more standard sessione name.
        : (26/12/2010) File extensions for WCS to/from pixel conversion.
        : (21/03/2011) Extinction data better coded.
        : (18/04/2011) Catcube, stcube and average constants.
        : (02/08/2011) Image filter extension.
        : (18/08/2011) Gemini GMOS parameters.
        : (22/09/2011) Ascii spectra extension.
        : (28/02/2012) TNG Dolores spec and pol entries.
        : (31/07/2012) Updated TNG pol entries.
        : (27/08/2012) Updated constants for average sigma-clipping.
        : (13/12/2012) Improvements to FORS imaging polarimetry keywords.
        : (29/07/2015) python3 porting.
        : (22/08/2017) Better keywords for imaging polarimetry.
        : (17/01/2019) More keywords for imaging polarimetry.
"""

import os

# Constants

SRPLocalDir	 = os.curdir
SRPPosAnsw	= 'Y'
SRPEnd	     = 'S'
SRPTab	     = '\t'
SRPMagErr      = 99.9
SRPExitSuccess	   = 0
SRPExitFailure	   = 1
Cspeed	     = 3e8*1e6	# micron/sec


## Version
#__version__ = '3.6.0beta'


# Keyword names
SRPCategory	 = "SRPCategory"
SRPBIAS	         = "BIAS"
SRPEXTR	         = "EXTRACTED FILE"
SRPFLATIMA	 = "IMAGING FLAT"
SRPSCIENCE	 = "SCIENCE"
SRPCatComm	 = "Kind of SRP file"
SRPNFiles        = "SRPNrofFiles"
SRPNFilesComm	 = "Nr. of files"
SRPMethod        = "SRPMethod"
SRPAVERAGE	 = "average"
SRPAVERAGESC     = "average sigma clipping %.1f %.1f"  
SRPAVERAGEREJ	 = "average with rejection"
SRPBIASFLAT	 = "bias and flat applied"
SRPEXTRACTION	 = "extracted"
SRPMethodComm	 = "Method to generate file"
SRPNPHeader	 = """#
# SRP path
#
"""
SRPNPEnd      = "# End configuration file."
SRPNewPath	= "set path=($path "


# File names
SRPAbsFile	       = "SRPAbs.dat"
SRPApPhotDAO	       = "_DAO_ap.dat"
SRPApPhotDAOSky        = "_DAO_ap.skycat"
SRPPsfPhotDAO	       = "_DAO_psf.dat"
SRPPsfPhotDAOSky       = "_DAO_psf.skycat"
SRPBS	               = "BrightStars.pck"
SRPClassFile	       = "Classify.txt"
SRPCutFile	       = "cut"
SRPHomeDir	       = os.path.expanduser("~")
SRPKeyFile	       = "Keywords.txt"
SRPGAIAPhot            = "_GAIA.dat"
SRPGAIAPhotSky         = "_GAIA.skycat"
SRPImaFltFile       = "_flt"
SRPImaFltFITS       = "_flt.fits"
SRPMagFluxFile	       = "SRPCalFlux.data"
SRPNoKeyValue	       = "NoKeyword"
SRPPhotomFile	       = "_photom.dat"
SRPPhotomFileSky       = "_photom.skycat"
SRPMyPhotomFile	       = "_myphotom.dat"
SRPMyPhotomFileSky     = "_myphotom.skycat"
SRPMyPhotOutput        = ".photometry"
SRPPyScrDir	       = 'PyScripts'
SRPScienceFile	       = "_biasflat"
SRPScienceFITS	       = "_biasflat.fits"
SRPSessionName	       = "SRPSessionName.txt"
SRPSetupFile	       = ".SRP-rc"
SRPShiftedFile	       = "shift"
#SRPStandardSessionName = "Swift"
SRPStandardSessionName = ""
SRPTempFile         = "_temp.fits"
SRPWCSFilePix       = "_pix"
SRPWCSFileCoo       = "_radec"
SRPMapFile          = "_map"
SRPWarpFile         = "_warp"
SRPExpMap           = "_expmap"
SRPASCIISpec        = ".ascii"




# External commands

SRPdfits       = "dfits"
SRPdfits_cyg   = "dfits.exe"
SRPxcorr2d     = "xcorr2d"
SRPwarping     = "warping"
#SRPsex	       = "sex"
#SRPsex_cyg     = "sex.exe"
SRPcollapse    = "collapse"
SRPpeak        = "peak"
SRPcatcube     = "catcube"
SRPstcube      = "stcube"
SRPaverage     = "average"



# Pre-selected keyword entries
SRPVLTFORSIMA = "VLTFORSIMA"
VLTFORSIMA  = """NAXIS1
NAXIS2
DATE-OBS
EXPTIME
INSTRUME
HIERARCH ESO OBS TARG NAME
HIERARCH ESO DPR CATG
HIERARCH ESO DPR TYPE
HIERARCH ESO DPR TECH
HIERARCH ESO INS COLL NAME
HIERARCH ESO INS FILT1 NAME
HIERARCH ESO DET READ CLOCK
HIERARCH ESO TEL AIRM START
HIERARCH ESO TEL AIRM END
HIERARCH ESO INS PIXSCALE
EXTNAME
"""
SRPLASCIMA  = "SRPLASCIMA"
LASCIMA	  = """NAXIS1
NAXIS2
DATE-OBS
TIME-OBS
EXPOSURE
FILTER
"""
SRPTNGDOLORESIMA = "TNGDOLORESIMA"
TNGDOLORESIMA  = """NAXIS1
NAXIS2
INSTRUME
RA-DEG
DEC-DEG
AIRMASS
DATE-OBS
EXPSTART
EXPTIME
OBJCAT
OBS-TYPE
FLT_ID
"""
SRPTNGDOLORESSPEC = "TNGDOLORESSPEC"
TNGDOLORESSPEC  = """NAXIS1
NAXIS2
INSTRUME
RA-DEG
DEC-DEG
AIRMASS
DATE-OBS
EXPSTART
EXPTIME
OBJCAT
OBS-TYPE
FLT_ID
GRM_ID
SLT_ID
LMP_ID
"""
SRPTNGDOLORESPOL = "TNGDOLORESPOL"
TNGDOLORESPOL  = """NAXIS1
NAXIS2
INSTRUME
RA-DEG
DEC-DEG
AIRMASS
DATE-OBS
EXPSTART
EXPTIME
OBJCAT
OBS-TYPE
FLT_ID
GRM_ID
SLT_ID
LMP_ID
PSLR_ID
RTY1_ID
RTY2_ID
POSANG
PARANG
"""
SRPTNGNICSIMA = "TNGNICSIMA"
TNGNICSIMA   = """NAXIS
NAXIS1
NAXIS2
TELESCOP
INSTRUME
DATE-OBS
EXPSTART
OBJECT
RA
DEC
AIRMASS
OBSMODE
FILTER
OBJECTIV
PIXSCALE
DIT
NDIT
MOSAIC
IDENT
OBS-TYPE
"""
SRPASIAGOAFOSCIMA = "ASIAGOAFOSCIMA"
ASIAGOAFOSCIMA	 = """NAXIS1
NAXIS2
DATE
EXPSTART
EXPTIME
AIRMASS
IMAGETYP
OBJECT
FILTER
"""
SRPVLTISAACIMA = "VLTISAACIMA"
VLTISAACIMA    = """NAXIS1
NAXIS2
EXPTIME
DATE-OBS
INSTRUME
OBJECT
RA
DEC
HIERARCH ESO DPR CATG
HIERARCH ESO DPR TYPE
HIERARCH ESO DPR TECH
HIERARCH ESO TEL AIRM START
HIERARCH ESO TEL AIRM END
HIERARCH ESO INS PIXSCALE
HIERARCH ESO INS FILT1 NAME
HIERARCH ESO DET DIT
HIERARCH ESO DET NDIT
HIERARCH ESO OBS TARG NAME
"""
SRPVLTFORSSPEC = "VLTFORSSPEC"
VLTFORSSPEC  = """NAXIS
NAXIS1
NAXIS2
DATE-OBS
EXPTIME
INSTRUME
OBJECT
EXTNAME
RA
DEC
AIRMASS
IMAGETYP
FILTER1
GRISM
HIERARCH ESO OBS TARG NAME
HIERARCH ESO DPR CATG
HIERARCH ESO DPR TECH
HIERARCH ESO INS MODE
HIERARCH ESO DET OUT1 CONAD
HIERARCH ESO DET OUT1 RON
HIERARCH ESO INS PIXSCALE
HIERARCH ESO DET READ CLOCK
HIERARCH ESO INS GRIS1 NAME
HIERARCH ESO INS FILT1 NAME
HIERARCH ESO INS COLL NAME
"""
SRPNTTEMMIIMA = "NTTEMMIIMA"
NTTEMMIIMA = """HIERARCH ESO DET WIN1 NX
HIERARCH ESO DET WIN1 NY
TELESCOP
INSTRUME
HIERARCH ESO DPR CATG
HIERARCH ESO DPR TECH
HIERARCH ESO DPR TYPE
OBJECT
RA
DEC
DATE-OBS
EXPTIME
HIERARCH ESO INS FILT2 NAME
HIERARCH ESO TEL AIRM END
HIERARCH ESO TEL AIRM START
HIERARCH ESO TEL AMBI FWHM END
HIERARCH ESO TEL AMBI FWHM START
"""
SRPNOTALFOSCIMA = "NOTALFOSCIMA"
NOTALFOSCIMA = """DATE-OBS
TM_START
TM_END
EXPTIME
INSTRUME
OBJECT
IMAGETYP
ALFLTNM
AIRMASS
"""
SRPDOSDOSCALTOCAFOSIMA = "DOSDOSCALTOCAFOSIMA"
DOSDOSCALTOCAFOSIMA = """NAXIS
NAXIS1
NAXIS2
INSTRUME
OBJECT
EXPTIME
RA
DEC
AIRMASS
DATE-OBS
IMAGETYP
CAMID
CCDNAME
CCDSENS
CCDRON
INSFLNAM
"""
SRPDANISHDFOSCIMA = "DANISHDFOSCIMA"
DANISHDFOSCIMA = """NAXIS1
NAXIS2
RA     
DEC  
OBJECT
DATE-OBS
TM_START
TM_END 
EXPTIME
TELESCOP
INSTRUME
FILTER_B
"""
SRPVLTNACOIMA = "VLTNACOIMA"
VLTNACOIMA = """NAXIS   
NAXIS1  
NAXIS2  
INSTRUME
OBJECT  
RA      
DEC     
EXPTIME 
AIRMASS 
DATE-OBS
HIERARCH ESO DET NCORRS NAME 
HIERARCH ESO DET NDIT        
HIERARCH ESO DPR CATG        
HIERARCH ESO DPR TECH        
HIERARCH ESO DPR TYPE        
HIERARCH ESO INS OPTI6 ID    
HIERARCH ESO ADA POSANG
HIERARCH ESO SEQ CUMOFFSETX 
HIERARCH ESO SEQ CUMOFFSETY
HIERARCH ESO INS PIXSCALE
HIERARCH ESO TEL AMBI FWHM START
"""
SRPREMROSSIMA = "REMROSSIMA"
REMROSSIMA = """
NAXIS   
NAXIS1  
NAXIS2  
DATE-OBS
EXPTIME 
TELESCOP
INSTRUME
GAIN    
RONOISE 
OBJECT  
RA      
DEC     
AIRMASS 
FILTER  
OBSTYPE 
"""
SRPNTTSOFIIMA = "NTTSOFIIMA"
NTTSOFIIMA = """
NAXIS   
NAXIS1  
NAXIS2  
EXPTIME 
DATE-OBS
OBJECT  
RA      
DEC     
HIERARCH ESO DPR CATG        
HIERARCH ESO DPR TECH        
HIERARCH ESO TEL AIRM START    
HIERARCH ESO INS FILT1 ID    
HIERARCH ESO DET NDIT        
HIERARCH ESO INS PIXSCALE
"""
SRPVLTFORSIPOL = "VLTFORSIPOL"
VLTFORSIPOL = """
NAXIS
NAXIS1
NAXIS2
DATE-OBS
EXPTIME
RA
DEC
INSTRUME
HIERARCH ESO TEL AIRM START
HIERARCH ESO DPR TYPE
HIERARCH ESO INS FILT1 NAME
HIERARCH ESO TEL PARANGS START
HIERARCH ESO ADA POSANG
HIERARCH ESO DPR CATG
HIERARCH ESO DPR TECH
HIERARCH ESO INS PIXSCALE
HIERARCH ESO INS MODE
HIERARCH ESO INS COLL NAME
HIERARCH ESO INS RETA2 POSANG
HIERARCH ESO INS RETA4 POSANG
HIERARCH ESO OBS TARG NAME
EXTNAME
"""
SRPVLTXSHOOTER = "VLTXSHOOTER"
VLTXSHOOTER = """
NAXIS   
NAXIS1  
NAXIS2  
ORIGIN  
TELESCOP
INSTRUME
OBJECT  
RA      
DEC     
EXPTIME 
HIERARCH ESO DET DIT 
HIERARCH ESO DET NDIT
MJD-OBS 
DATE-OBS
HIERARCH ESO DET EXP TYPE    
HIERARCH ESO DET OUT1 CONAD  
HIERARCH ESO DET OUT1 RON    
HIERARCH ESO DET READ CLOCK 
HIERARCH ESO DET WIN1 BINX
HIERARCH ESO DET WIN1 BINY
HIERARCH ESO DET READ MODE   
HIERARCH ESO DPR TECH        
HIERARCH ESO INS FILT1 NAME  
HIERARCH ESO TEL AIRM START
HIERARCH ESO SEQ ARM
HIERARCH ESO INS OPTI2 ID
HIERARCH ESO INS OPTI3 NAME
HIERARCH ESO INS OPTI4 NAME
HIERARCH ESO INS OPTI5 NAME
HIERARCH ESO PRO CATG
INS LAMP2 ST
INS LAMP6 ST
"""
SRPTNGDOLORESSPEC = "TNGDOLORESSPEC"
TNGDOLORESSPEC  = """NAXIS1  
NAXIS2  
EXPTIME 
INSTRUME
RA-DEG  
DEC-DEG 
AIRMASS 
PARANG
OBJCAT  
EXPSTART
DATE-OBS
OBS-TYPE
FLT_ID  
GRM_ID  
SLT_ID  
LMP_ID  
"""
SRPGEMINIGMOSIMA = "GEMINIGMOSIMA"
GEMINIGMOSIMA  = """NAXIS1  
NAXIS   
INSTRUME
OBJECT  
OBSTYPE 
OBSCLASS
RA      
DEC     
UT      
DATE    
DETECTOR
OBSEPOCH
EXPTIME 
FILTER1 
FILTER2 
GRATING 
AIRMASS 
RDNOISE
GAIN
MJD-OBS
"""


SRPPREKEYDICT = {SRPVLTFORSIMA:VLTFORSIMA, SRPLASCIMA:LASCIMA, SRPTNGDOLORESIMA:TNGDOLORESIMA, 
 SRPTNGDOLORESSPEC:TNGDOLORESSPEC, SRPTNGDOLORESPOL:TNGDOLORESPOL, SRPASIAGOAFOSCIMA:ASIAGOAFOSCIMA, 
 SRPVLTISAACIMA:VLTISAACIMA, SRPVLTFORSSPEC:VLTFORSSPEC, SRPNTTEMMIIMA:NTTEMMIIMA, SRPNOTALFOSCIMA:NOTALFOSCIMA,
 SRPDOSDOSCALTOCAFOSIMA:DOSDOSCALTOCAFOSIMA, SRPDANISHDFOSCIMA:DANISHDFOSCIMA, SRPVLTNACOIMA:VLTNACOIMA, 
 SRPTNGNICSIMA:TNGNICSIMA, SRPREMROSSIMA:REMROSSIMA, SRPNTTSOFIIMA:NTTSOFIIMA, SRPVLTFORSIPOL:VLTFORSIPOL, 
 SRPVLTXSHOOTER:VLTXSHOOTER, SRPTNGDOLORESSPEC:TNGDOLORESSPEC, SRPGEMINIGMOSIMA:GEMINIGMOSIMA}




# Site coordinates
# ESO La Silla
class SiteCoord:
 def __init__ (self, latc, longc):
  self.Lat = str(latc)
  self.Long = str(longc)
SiteDict = {'LaSilla' : SiteCoord(-29.2567,-70.7292), 'Paranal' : SiteCoord('-24:51:00', '-70:27:00'),
 'Merate' : SiteCoord('45:41:54','9:25:45'), 'TNG' : SiteCoord('28:46:00','-17:53:00'),
 'CalarAlto' : SiteCoord('37:13:25', '2:32:46'), 'NOT' : SiteCoord('28:45:26','-17:53:00'),
 'LBT' : SiteCoord('32:42:04.71','-109:53:20.60'), 'GEMINI-N': SiteCoord(19.8238,-155.4690)}


# DAOPHOT file extentions
DAOApPhot  =  '.ap'
DAOPsfPhot  =  '.als'


