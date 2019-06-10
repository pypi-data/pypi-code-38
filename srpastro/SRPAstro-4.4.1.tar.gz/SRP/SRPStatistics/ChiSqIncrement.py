""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.1.0
Author  : Stefano Covino
Date    : 30/04/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : ChiSqIncrement(dof,prob=90,acc=0.001)
            dof is the number of degrees of freedom
            prob is the probability for having a higher chisquare than 100-prob%
            acc is the accuracy of the chisquare increment computation
          The function return the chisquare increment.
        

Remarks : input is a list of (x,sigmax)

History : (30/04/2011) First version.
        : (24/07/2015) scipy porting.
"""

from scipy import stats


def ChiSqIncrement(dof, prob=90.0, acc=0.001):
    if dof <= 0:
        return 0.0
    alf = 100.0 - prob
    maxchi = 0.0
    chii = 0.1
    upi = True
    while not alf-acc/2. <= 100.0*(1.-stats.chi2.cdf(maxchi,dof)) <= alf+acc/2.:
        oldi = upi      # save the old increment direction
        if 100.0*(1.-stats.chi2.cdf(maxchi,dof)) > alf:
            maxchi = maxchi + chii
            upi = True          # up increment
        else:
            maxchi = maxchi - chii
            upi = False         # down increment
            if maxchi < 0:
                maxchi = maxchi + chii  # back to original value
                chii = chii / 2.0       # if increment gets negative better refined serach
        if oldi != upi:
            chii = chii/2.      # if oscillates half inrement
    return maxchi
    
    