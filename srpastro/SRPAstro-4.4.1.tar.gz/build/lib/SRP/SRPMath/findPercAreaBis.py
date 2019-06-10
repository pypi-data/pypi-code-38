""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 28/01/2016
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (28/01/2016) First version.

"""


import numpy



def findPercAreaBis (x,y,r,xp,yp):
    intersezioni = []
    xA = xp - 1
    sqr = r**2-(xA-x)**2
    if sqr >= 0:
        yA1 = y + math.sqrt(sqr)
        yA2 = y - math.sqrt(sqr)
        if yp-1 <= yA1 <= yp:
            intersezioni.append((xA,yA1,True,1))
        if yp-1 <= yA2 <= yp:
            intersezioni.append((xA,yA2,False,1))
    xB = xp
    sqr = r**2-(xB-x)**2
    if sqr >= 0:
        yB1 = y + math.sqrt(sqr)
        yB2 = y - math.sqrt(sqr)
        if yp-1 <= yB1 <= yp:
            intersezioni.append((xB,yB1,True,2))
        if yp-1 <= yB2 <= yp:
            intersezioni.append((xB,yB2,False,2))
    yC = yp - 1
    sqr = r**2-(yC-y)**2
    if sqr >= 0.0:
        xC1 = x + math.sqrt(sqr)
        xC2 = x - math.sqrt(sqr)
        if xp-1 <= xC1 <= xp:
            intersezioni.append((xC1,yC,True,3))
        if xp-1 <= xC2 <= xp:
            intersezioni.append((xC2,yC,False,3))
    yD = yp
    sqr = r**2-(yD-y)**2
    if sqr >= 0.0:
        xD1 = x + math.sqrt(sqr)
        xD2 = x - math.sqrt(sqr)
        if xp-1 <= xD1 <= xp:
            intersezioni.append((xD1,yD,True,4))
        if xp-1 <= xD2 <= xp:
            intersezioni.append((xD2,yD,False,4))
    if len(intersezioni) == 2:
        if yp-1 >= y or yp <= y:
            if intersezioni[0][0] <= intersezioni[1][0]:
                area1 = (intersezioni[0][0]-(xp-1))*(intersezioni[0][1]-(yp-1))
                area3 = (xp-intersezioni[1][0])*(intersezioni[1][1]-(yp-1))
                if yp-1 >= y:
                    area2 = integFuct(intersezioni[0][0],intersezioni[1][0],x,y,r,yp)
                elif yp <= y:
                    area2 = integFuct(intersezioni[0][0],intersezioni[1][0],x,y,r,yp,False)
            else:
                area1 = (intersezioni[1][0]-(xp-1))*(intersezioni[1][1]-(yp-1))
                area3 = (xp-intersezioni[0][0])*(intersezioni[0][1]-(yp-1))
                if yp-1 >= y:
                    area2 = integFuct(intersezioni[1][0],intersezioni[0][0],x,y,r,yp)
                elif yp <= y:
                    area2 = integFuct(intersezioni[1][0],intersezioni[0][0],x,y,r,yp,False)
            area = area1 + area2 + area3
        else:
            if xp-1 >= x:
                if intersezioni[0][1] <= intersezioni[1][1]:
                    area = integFuct(intersezioni[0][1],intersezioni[1][1],y,x,r,xp)
                else:
                    area = integFuct(intersezioni[1][1],intersezioni[0][1],y,x,r,xp)
            else:
                if intersezioni[0][1] <= intersezioni[1][1]:
                    area = integFuct(intersezioni[0][1],intersezioni[1][1],y,x,r,xp,False)
                else:
                    area = integFuct(intersezioni[1][1],intersezioni[0][1],y,x,r,xp,False)
        if yp-1 >= y:
            return area
        elif yp <= y:
            return 1.0-area
        else:
            if xp-1 >= x:
                return area
            elif xp <= x:
                return 1-area
    else:
        dist = math.sqrt((x-xp)**2+(y-yp)**2)
        if dist < r:
            return 1.0
        else:
            return 0.0


