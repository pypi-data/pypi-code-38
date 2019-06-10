""" 

Context : SRP
Module  : Tables
Version : 1.0.0
Author  : Stefano Covino
Date    : 27/10/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (27/10/2015) First version.

"""



def ReadCleanedTextFile(fname):
    with open(fname) as f:
        fdata = f.readlines()
    #
    listadata = []
    for i in fdata:
        if len(i.strip()) > 0:
            listadata.append(i.strip())
    #
    return listadata