""" Utility functions and classes for SRP

Context : SRP
Module  : System.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 31/07/2015
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (27/09/2010) First version.
        : (31/07/2015) python3 porting.
"""


import os, os.path, sys


# SRP pipe
if (sys.version_info[0] == 2 and sys.version_info[1] >= 6) or sys.version_info[0] >= 3:
    import subprocess
    
    def Pipe (file):
        f = subprocess.Popen(file,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,shell=True,close_fds=True)
        ky = f.stdout.read()
        estatus = f.wait()
        del f
        if os.WEXITSTATUS (estatus):
            return None
        else:
            return ky
else:
    import popen2
    
    def Pipe (file):
        f = popen2.Popen4(file)
        ky = f.fromchild.read()
        estatus = f.wait()
        del f
        if os.WEXITSTATUS (estatus):
            return None
        else:
            return ky
