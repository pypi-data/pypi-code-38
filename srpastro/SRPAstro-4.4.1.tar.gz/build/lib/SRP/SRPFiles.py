""" Collections of constans, functions and classes for file managements.

Context : SRP
Module  : SRPFiles.py
Version : 1.9.1
Status  : approved
Author  : Stefano Covino, Nico Cucchiara
Date    : 16/06/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/~covino
Purpose : Collection of constants and functions for file managements.

Usage   : to be imported

Remarks :

History : (20/05/2003) First version.
        : (21/05/2003) Read session name function.
        : (08/09/2003) Flux-magnitude file
        : (09/09/2003) Wavelength to frequency conversion.
        : (20/09/2003) Check if a file is readable.
        : (01/10/2003) Reading absorpion data file.
        : (14/10/2003) Tool for pipe management.
        : (24/10/2003) Reading total file.
        : (12/10/2008) Minor correction.
        : (07/09/2009) python 2.6 upgrade.
        : (06/10/2009) Minor correction.
        : (17/06/2010) Better data file path management.
        : (21/03/2011) Better coding for extinction routines.
        : (16/08/2011) Absolute pathes correctly managed.
        : (05/02/2012) Better path management.
        : (21/05/2012) pipe function commented.
        : (24/07/2015) python3 porting.
        : (28/07/2015) Bug correction.
        : (16/06/2016) Modern python porting.
"""



import os, os.path, pickle
import sys
from . import SRPConstants
import SRP
from SRP.SRPSystem.SRPPath import SRPPath



# Constants

ReadMode   = "r"
WriteMode  = "w"
AppendMode = "a"




# Classes

# Generic SRP file

class SRPFile:
    """SRP file.

    Parameters are dirname, filename and mode."""
    def __init__ (self, dirname, filename, mode):
        self.dirname = dirname          # Directory
        self.filename = filename        # File name
        self.mode = mode                # Mode
        self.f = None                   # File pointer

    def SRPOpenFile (self):
        """Open a SRP file.

        Create the directory if it does not exist, return None
        if file does not exist."""
        if len(self.filename) > 0 and self.filename[0] == os.sep:
            fullpath = self.filename
        else:
            fullpath = self.dirname+os.sep+self.filename
        if self.mode == ReadMode and os.path.isfile(fullpath):
            self.f = open(fullpath,self.mode)
        elif self.mode == WriteMode or self.mode == AppendMode:
            if os.path.isfile(self.dirname):
                os.remove(self.dirname)
            if not os.path.isdir(self.dirname):
                os.mkdir(self.dirname)
            self.f = open(fullpath,self.mode)
        else:
            self.f = None


    def SRPCloseFile (self):
        """Close a SRP file."""
        self.f.close()

    def SRPReadTotFile(self):
        """ Read all data from a SRP file."""
        return self.f.readlines()

    def SRPReadFile(self):
        """Read data from a SRP file."""
        return self.f.readline()

    def SRPReadFilePickle(self):
        """Read pickled data from a SRP file."""
        return pickle.load(self.f)

    def SRPWriteFile(self, data=os.linesep):
        self.f.write(str(data))

    def SRPWriteFilePickle(self, data=os.linesep):
        pickle.dump(data,self.f)



def getSRPSessionName():
    f = SRPFile(SRPConstants.SRPLocalDir,SRPConstants.SRPSessionName,ReadMode)
    f.SRPOpenFile()
    if f.f == None:
        return SRPConstants.SRPStandardSessionName
    else:
        return f.SRPReadFile()



def getSRPFITSList(filename):
    list = []
    f = SRPFile(SRPConstants.SRPLocalDir,filename,ReadMode)
    f.SRPOpenFile()
    if f.f == None:
        return list
    else:
        while True:
            ffile = f.SRPReadFile()
            if ffile != '':
                list.append(ffile.strip())
            else:
                break
        f.SRPCloseFile()
        return list



def getSRPKeyList(filename):
    list = []
    f = SRPFile(SRPConstants.SRPLocalDir,filename,ReadMode)
    f.SRPOpenFile()
    if f.f == None:
        return list
    else:
        while True:
            fkey = f.SRPReadFile()
            if fkey != '':
                list.append(fkey.strip())
            else:
                break
        f.SRPCloseFile()
        return list



def getSRPDataPath():
    return SRPPath()



def SRPLeggiMagCalFile (nomefile):
    # Leggi il file
    try:
        f = open(nomefile, "r")
    except:
        return [], [], [], []
    data = f.readlines()
    f.close()
    # Elimina le righe che cominciano con #
    dataclean = []
    for i in range(len(data)):
        if data[i][0] != '#':
            dataclean.append(data[i])
    # Leggi i valori
    banda = []
    l0 = []
    f0 = []
    n0 = []
    for i in range(len(dataclean)):
        valori = dataclean[i].split()
        banda.append(valori[0])
        try:
            l0.append(float(valori[1]))
            f0.append(float(valori[2]))
            n0.append(SRPConstants.Cspeed/l0[i])
        except:
            l0.append(SRPConstans.SRPMagErr)
            f0.append(SRPConstants.SRPMagErr)
            n0.append(SRPConstants.SRPMagErr)
    return banda, l0, f0, n0



def IsReadable (filename):
    return os.access(filename,os.R_OK)


