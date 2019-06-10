""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 05/09/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (05/09/2011) First version.

"""


A = (-1.2150,-1.3509,-1.2150,-1.3509)
B = (1.2359,0.3786,-1.2359,-0.3786)
C = (-0.3085,0.5906,-0.3085,0.5906)
D = (0.0210,-1.1858,-0.0210,1.1858) 


def VoigtFunctApprox (a,v):
    fnz = 0.0
    for i in range(4):
        num = C[i]*(a-A[i]) + D[i]*(v-B[i])
        den = (a-A[i])**2 + (v-B[i])**2
        fnz = fnz + num/den
    return fnz

