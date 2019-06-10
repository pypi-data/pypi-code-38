""" 

Context : SRP
Module  : Tables
Version : 1.0.0
Author  : Stefano Covino
Date    : 11/02/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (11/02/2013) First version.

"""



def SkyStr(inpstr):
    msgo = "".join(i for i in inpstr if 0 < ord(i) < 128)
    return "\t".join(msgo.split())

