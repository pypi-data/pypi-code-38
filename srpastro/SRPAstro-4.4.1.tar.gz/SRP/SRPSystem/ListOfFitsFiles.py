""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 18/05/2017
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Usage   : ListOfFitsFiles (file)
            file is either a FITS file or a text file with a list of FITS files. 
            It reports a list of FITS files.

History : (02/10/2011) First version.
        : (18/05/2017) Minor update.
"""


import os, os.path
from SRPFITS.Fits.IsFits import IsFits


def ListOfFitsFiles (file):
    if os.path.isfile(file):
        if IsFits(file):
            # case with single FITS file in input
            return [file,]
        else:
            with open(file, 'r') as f:
                read_files = f.readlines()
            listfiles = []
            # case with list of FITS files
            for ifts in read_files:
                if IsFits(ifts.split()[0]):
                    listfiles.append(ifts.split()[0].strip())
                else:
                    return None
            return listfiles
    else:    
        # case with input not even file
        return None
        
