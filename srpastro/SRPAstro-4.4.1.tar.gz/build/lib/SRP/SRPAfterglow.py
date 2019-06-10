""" Utility functions and classes for SRP

Context : SRP
Module  : SRPAfterglow.py
Version : 1.0.0
Status  : approved
Author  : Stefano Covino
Date    : 27/02/2007
E-mail  : stefano.covino@brera.inaf.it
URL     : http://www.merate.mi.astro.it/covino
Purpose : Collection of utility functions and classes for SRP.

Usage   : to be imported

Remarks : Data from Zhang & Meszaros, IJMPA A19, 2385 (2004) and
        : Hurley, Sari and Djorgovski, in "Compact Stellar X-ray Sources".

History : (27/02/2007) First version.
"""


#import SRPFiles, SRPConstants
#import os, string, math, copy
#import TimeAstro_algs
#import stats




def TypSynchrFreqConst (epse=0.1, epsb=0.01, energy=1e52, time=1, z=1):
 csie=1
 return 6*1e15 * (1+z)**0.5 * (energy/1e52)**0.5 * (epse/csie)**2 * (epsb)**0.5 * (time)**-1.5

def CoolSynchrFreqConst (epsb=0.01, energy=1e52, time=1, z=1, density=1):
 return 9*1e12 * (1+z)**-0.5 * (energy/1e52)**-0.5 * (density)**-1 * (epsb)**-1.5 * (time)**-0.5

def SelfAbsSynchrFreqConst (epse=0.1, epsb=0.01, energy=1e52, density=1, z=1):
 csie=1
 return 2*1e9 * (1+z)**-1 * (energy/1e52)**0.2 * (epse/csie)**-1 * (epsb)**0.2 * density**0.4

def TypSynchrFluxConst (epsb=0.01, energy=1e52, ldist=1e28, density=1, z=1):
 return 20 * (1+z) * (epsb)**0.5 * density**0.5 * (energy/1e52) * (ldist/1e28)**-2

def SynchrSpectrConst (nu, epse=0.1, epsb=0.01, energy=1e52, time=1, z=1, density=1, ldist=1e28, p=2.2):
 ntyp = TypSynchrFreqConst (epse, epsb, energy, time, z)
 nsabs = SelfAbsSynchrFreqConst (epse, epsb, energy, density, z)
 ncool = CoolSynchrFreqConst (epsb, energy, time, z, density)
 normfl = TypSynchrFluxConst (epsb, energy, ldist, density, z)
 if ntyp < ncool:
  if nu < nsabs:
   return normfl * (nsabs/ntyp)**(1.0/3.0) * (nu/nsabs)**2
  elif nsabs <= nu < ntyp:
   return normfl * (nu/ntyp)**(1.0/3.0)
  elif ntyp <= nu < ncool:
   return normfl * (nu/ntyp)**((1-p)/2.0)
  else:
   return normfl * (ncool/ntyp)**((1-p)/2.0) * (nu/ncool)**(-p/2.0)
 else:
  if nu < nsabs:
   return normfl * (nsabs/ncool)**(1.0/3.0) * (nu/nsabs)**2
  elif nsabs <= nu < ncool:
   return normfl * (nu/ncool)**(1.0/3.0)
  elif ncool <= nu < ntyp:
   return normfl * (nu/ncool)**-0.5
  else:
   return normfl * (ntyp/ncool)**-0.5 * (nu/ntyp)**(-p/2.0)




# \rho R^2 = Astar * 5 x 10^11  gr/cm
def TypSynchrFreqWind (epse=0.1, epsb=0.01, energy=1e52, time=1, z=1):
 csie=1
 return 1.7*1e14 * (1+z)**0.5 * (energy/1e52)**0.5 * (epse/csie)**2 * (epsb)**0.5 * (time)**-1.5

def CoolSynchrFreqWind (epsb=0.01, energy=1e52, time=1, z=1, Astar=1):
 return 7*1e11 * (1+z)**-1.5 * (energy/1e52)**0.5 * (Astar)**-2 * (epsb)**-1.5 * (time)**0.5

def SelfAbsSynchrFreqWind (epse=0.1, epsb=0.01, energy=1e52, Astar=1, z=1, time=1):
 csie=1
 return 1.5*1e10 * (1+z)**-0.4 * (energy/1e52)**-0.4 * (epse/csie)**-1 * (epsb)**0.2 * Astar**1.2 * (time)**-0.4

def TypSynchrFluxWind (epsb=0.01, energy=1e52, ldist=1e28, Astar=1, z=1, time=1):
 return 180 * (1+z)**1.5 * (epsb)**0.5 * Astar * (energy/1e52)**0.5 * (ldist/1e28)**-2 * (time)**-0.5

def SynchrSpectrWind (nu, epse=0.1, epsb=0.01, energy=1e52, time=1, z=1, Astar=1, ldist=1e28, p=2.2):
 ntyp = TypSynchrFreqWind (epse, epsb, energy, time, z)
 nsabs = SelfAbsSynchrFreqWind (epse, epsb, energy, Astar, z, time)
 ncool = CoolSynchrFreqWind (epsb, energy, time, z, Astar)
 normfl = TypSynchrFluxWind (epsb, energy, ldist, Astar, z, time)
 if ntyp < ncool:
  if nu < nsabs:
   return normfl * (nsabs/ntyp)**(1.0/3.0) * (nu/nsabs)**2
  elif nsabs <= nu < ntyp:
   return normfl * (nu/ntyp)**(1.0/3.0)
  elif ntyp <= nu < ncool:
   return normfl * (nu/ntyp)**((1-p)/2.0)
  else:
   return normfl * (ncool/ntyp)**((1-p)/2.0) * (nu/ncool)**(-p/2.0)
 else:
  if nu < nsabs:
   return normfl * (nsabs/ncool)**(1.0/3.0) * (nu/nsabs)**2
  elif nsabs <= nu < ncool:
   return normfl * (nu/ncool)**(1.0/3.0)
  elif ncool <= nu < ntyp:
   return normfl * (nu/ncool)**-0.5
  else:
   return normfl * (ntyp/ncool)**-0.5 * (nu/ntyp)**(-p/2.0)



