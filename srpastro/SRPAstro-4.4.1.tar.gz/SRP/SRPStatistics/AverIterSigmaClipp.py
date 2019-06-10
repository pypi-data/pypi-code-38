""" Utility functions and classes for SRP

Context : SRP
Module  : Stats.py
Version : 1.1.1
Author  : Stefano Covino
Date    : 13/10/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : input is a list of (x,sigmax)

History : (21/05/2010) First version.
        : (20/08/2010) Input list with no weights case.
        : (13/10/2010) Single object case.

"""

from . import WeightedMean as WM
import copy


def AverIterSigmaClipp (inplst, siglev=2.0):
    worklist = copy.deepcopy(inplst)
    wlst = []
    for i in worklist:
        wlst.append(True)
    ocard = len(wlst)   
    #
    if len(worklist) > 0:
        try:
            ndt = len(worklist[0])
        except TypeError:
            ndt = 1
        if ndt < 2:
            for i in range(len(worklist)):
                worklist[i] = (worklist[i],1.0)
    #
    while True:
        if len(worklist) < 1:
            return None,None,None,None
        elif len(worklist) == 1:
            return worklist[0][0],worklist[0][1],worklist[0][1],1.0,1
        anlst = []
        for i in range(len(wlst)):
            if wlst[i] == True:
                anlst.append(worklist[i])
                #print worklist[i]
        res = WM.WeightedMean(anlst)
        wa = res[0]
        ws = res[1]
        we = res[2]
        ch = res[3]
        #print res
        wmin, wmax = wa - siglev*ws, wa + siglev*ws
        for i in range(len(wlst)):
            if not wmin <= worklist[i][0] <= wmax:
                wlst[i] = False
            #print wmin,wmax,worklist[i][0],wa,ws
        card = 0
        for i in wlst:
            if i == True:
                card = card + 1
        if card != ocard:
                ocard = card
        else:
            return wa,ws,we,ch,len(anlst)

