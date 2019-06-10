""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 20/03/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (20/03/2011) First version.

"""

# Available extinction curves
MW = "MW"
LMC = "LMC"
SMC = "SMC"
SB = "SB"


ExtCurDict = {MW:"Milky Way", LMC:"Large Magellanic Cloud", SMC:"Small Magellanic Cloud", SB:"Star Burst"}
ExtRDict   = {MW : 3.08, LMC : 3.16, SMC : 2.93, SB : 4.05}



#I 24 parametri liberi sono ai, li, bi, ni secondo la tabella di Pei Y., 1992, ApJ 395,130

ai = ({'MW':165.0, 'LMC':175.0, 'SMC':185.0}, {'MW':14.0, 'LMC':19.0, 'SMC':27.0},
        {'MW':0.045, 'LMC':0.023, 'SMC':0.005}, {'MW':0.002, 'LMC':0.005, 'SMC':0.01},
            {'MW':0.002, 'LMC':0.006, 'SMC':0.012}, {'MW':0.012, 'LMC':0.02, 'SMC':0.030})
            
li = ({'MW':0.047, 'LMC':0.046, 'SMC':0.042}, {'MW':0.08, 'LMC':0.08, 'SMC':0.08},
        {'MW':0.22, 'LMC':0.22, 'SMC':0.22}, {'MW':9.7, 'LMC':9.7, 'SMC':9.7},
           {'MW':18.0, 'LMC':18.0, 'SMC':18.0}, {'MW':25.0, 'LMC':25.0, 'SMC':25.0})
           

bi = ({'MW':90.0, 'LMC':90.0, 'SMC':90.0}, {'MW':4.0, 'LMC':5.5, 'SMC':5.50},
        {'MW':-1.95, 'LMC':-1.95, 'SMC':-1.95}, {'MW':-1.95, 'LMC':-1.95, 'SMC':-1.95},
          {'MW':-1.80, 'LMC':-1.80, 'SMC':-1.80}, {'MW':0.00, 'LMC':0.00, 'SMC':0.00})
          
        
ni = ({'MW':2.0, 'LMC':2.0, 'SMC':2.0}, {'MW':6.5, 'LMC':4.5, 'SMC':4.0},
        {'MW':2.0, 'LMC':2.0, 'SMC':2.0}, {'MW':2.0, 'LMC':2.0, 'SMC':2.0},
            {'MW':2.0, 'LMC':2.0, 'SMC':2.0}, {'MW':2.0, 'LMC':2.0, 'SMC':2.0})




