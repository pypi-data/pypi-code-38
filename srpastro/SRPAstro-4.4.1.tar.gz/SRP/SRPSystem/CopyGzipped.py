""" Utility functions and classes for SRP

Context : SRP
Module  : System
Version : 1.0.0
Author  : Stefano Covino
Date    : 30/08/2013
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (30/08/2013) First version.

"""


import gzip, os


def CopyGzipped(fin,fout,remove=False):
    try:
        f_in = open(fin, 'rb')
        f_out = gzip.open(fout+'.gz', 'wb')
        f_out.writelines(f_in)
        f_out.close()
        f_in.close()
        if remove:
            os.remove(fin)
        return True
    except IOError:
        return False
        
#