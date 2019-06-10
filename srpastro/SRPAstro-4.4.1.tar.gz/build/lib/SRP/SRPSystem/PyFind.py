""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 19/01/2018
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Usage   : PyFind (path, selp='*')
            

History : (02/04/2016) First version.
        : (19/01/2018) Multiple patter managed.
"""


import os, fnmatch



def mpatt (name, mpat):
    if isinstance(mpat,list):
        mm = mpat
    else:
        mm = [mpat]
    #
    for p in mm:
        if fnmatch.fnmatch(name, p):
            return True
    return False



def PyFind (path, selp='*', exclp=[]):
    fileList = []
    #
    for dName, sdName, fList in os.walk(path):
        for fileName in fList:
            if fnmatch.fnmatch(fileName, selp) and not mpatt(fileName, exclp):
                fileList.append(os.path.join(dName, fileName))
    #
    return fileList
