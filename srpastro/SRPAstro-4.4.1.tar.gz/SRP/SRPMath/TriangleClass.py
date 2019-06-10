""" Utility functions and classes for SRP

Context : SRP
Module  : Math.py
Version : 1.0.1
Author  : Stefano Covino
Date    : 21/03/2012
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks :

History : (02/09/2010) First version.
        : (21/03/2012) Better management of math errors.

"""

import math

from .PointClass import Point
from .AstroAngleInput import AstroAngleInput
from .CartesianCoordAmpRotoTranslation import CartesianCoordAmpRotoTranslation
from .InverseCartesianCoordAmpRotoTranslation import InverseCartesianCoordAmpRotoTranslation

class Triangle:
    def __init__ (self, v0, v1, v2, atol=1.0):
        self.Vertici = [Point(v0), Point(v1), Point(v2)]
        self.Sizes = [self.Vertici[1].PointDist(self.Vertici[2]),
            self.Vertici[0].PointDist(self.Vertici[2]),
                self.Vertici[1].PointDist(self.Vertici[0])]
        try:
            self.Angles = [math.degrees(math.acos((self.Sizes[2]**2 + self.Sizes[1]**2 - self.Sizes[0]**2)/(2*self.Sizes[2]*self.Sizes[1]))),
                        math.degrees(math.acos((self.Sizes[0]**2 + self.Sizes[2]**2 - self.Sizes[1]**2)/(2*self.Sizes[0]*self.Sizes[2]))),
                            math.degrees(math.acos((self.Sizes[1]**2 + self.Sizes[0]**2 - self.Sizes[2]**2)/(2*self.Sizes[1]*self.Sizes[0])))]
        except ValueError:
            self.Angles = [0,0,0]
        except ZeroDivisionError:
            self.Angles = [0,0,0]
        self.AngTol = AstroAngleInput(atol).Angle
        self.ConnVert = []


    def IsSymmTriangle (self):
        neqangl = 0
        if math.fabs(self.Angles[0] - self.Angles[1]) <= self.AngTol:
            neqangl = neqangl + 1
        if math.fabs(self.Angles[1] - self.Angles[2]) <= self.AngTol:
            neqangl = neqangl + 1
        if math.fabs(self.Angles[2] - self.Angles[0]) <= self.AngTol:
            neqangl = neqangl + 1
        if neqangl >= 1:
            return True
        else:
            return False

    
    def Commensurabili(self,other):
        eqang = []
        assangl = [False for i in range(3)]
        for i in range(3):
            for l in range(3):
                if (assangl[l] == False) and math.fabs(self.Angles[i] - other.Angles[l]) <= self.AngTol:
#                    print self.Angles[i],other.Angles[l]
                    eqang.append((i,l))
                    assangl[l] = True
                    break
        self.ConnVert = eqang 
        if len(eqang) < 3:
            return False
        else:            
            return True
            
    
    def Rotable (self, other):
        if len(self.ConnVert) !=3:
            self.Rot = 0.0
            return False
        unoa = self.Vertici[self.ConnVert[0][0]].AngOrig(self.Vertici[self.ConnVert[1][0]].Coord)
        duea = other.Vertici[self.ConnVert[0][1]].AngOrig(other.Vertici[self.ConnVert[1][1]].Coord)
        rota = duea-unoa
#        print duea,unoa,rota
        unob = self.Vertici[self.ConnVert[0][0]].AngOrig(self.Vertici[self.ConnVert[2][0]].Coord)
        dueb = other.Vertici[self.ConnVert[0][1]].AngOrig(other.Vertici[self.ConnVert[2][1]].Coord)
        rotb = dueb-unob
#        print dueb,unob,rotb
        unoc = self.Vertici[self.ConnVert[1][0]].AngOrig(self.Vertici[self.ConnVert[2][0]].Coord)
        duec = other.Vertici[self.ConnVert[1][1]].AngOrig(other.Vertici[self.ConnVert[2][1]].Coord)
        rotc = duec-unoc
#        print duec,unoc,rotc
        if math.fabs(rota-rotb) > self.AngTol or math.fabs(rota-rotc) > self.AngTol or math.fabs(rotb-rotc) > self.AngTol:
            return False
        else:
            return True
            
                
    def SizeFactor (self,other):
        sisfact = 0.0
        if len(self.ConnVert) != 3:
            self.SiFa = 1.0
            return self.SiFa
        else:
            for p in self.ConnVert:
                sisfact = sisfact + self.Sizes[p[0]]/other.Sizes[p[1]]
#                print self.Sizes[p[0]],other.Sizes[p[1]]
            self.SiFa = sisfact/3.0
            return self.SiFa
        
    def RotationFactor (self,other):
        if len(self.ConnVert) !=3:
            self.Rot = 0.0
            return self.Rot
        unoa = self.Vertici[self.ConnVert[0][0]].AngOrig(self.Vertici[self.ConnVert[1][0]].Coord)
        duea = other.Vertici[self.ConnVert[0][1]].AngOrig(other.Vertici[self.ConnVert[1][1]].Coord)
        rota = duea-unoa
#        print duea,unoa,rota
        unob = self.Vertici[self.ConnVert[0][0]].AngOrig(self.Vertici[self.ConnVert[2][0]].Coord)
        dueb = other.Vertici[self.ConnVert[0][1]].AngOrig(other.Vertici[self.ConnVert[2][1]].Coord)
        rotb = dueb-unob
#        print dueb,unob,rotb
        unoc = self.Vertici[self.ConnVert[1][0]].AngOrig(self.Vertici[self.ConnVert[2][0]].Coord)
        duec = other.Vertici[self.ConnVert[1][1]].AngOrig(other.Vertici[self.ConnVert[2][1]].Coord)
        rotc = duec-unoc
#        print duec,unoc,rotc
        self.Rot = (rota+rotb+rotc)/3.0
#        print "rot",rota,rotb,rotc
        return self.Rot

    
    def ShiftFactor (self,other):
        if self.SiFa == None:
            self.SiFa = 1.0
        if self.Rot == None:
            self.Rot = 0.0
        newc = CartesianCoordAmpRotoTranslation(self.Vertici[self.ConnVert[0][0]].Coord,(0,0),self.Rot,1./self.SiFa)
        sha = (other.Vertici[self.ConnVert[0][1]].Coord[0]-newc[0]),(other.Vertici[self.ConnVert[0][1]].Coord[1]-newc[1])
        newc = CartesianCoordAmpRotoTranslation(self.Vertici[self.ConnVert[1][0]].Coord,(0,0),self.Rot,1./self.SiFa)
        shb = (other.Vertici[self.ConnVert[1][1]].Coord[0]-newc[0]),(other.Vertici[self.ConnVert[1][1]].Coord[1]-newc[1])
        newc = CartesianCoordAmpRotoTranslation(self.Vertici[self.ConnVert[2][0]].Coord,(0,0),self.Rot,1./self.SiFa)
        shc = (other.Vertici[self.ConnVert[2][1]].Coord[0]-newc[0]),(other.Vertici[self.ConnVert[2][1]].Coord[1]-newc[1])  
#        print "shift",sha,shb,shc
        ShFa = (sha[0]+shb[0]+shc[0])/(3.0*(-1./self.SiFa)),(sha[1]+shb[1]+shc[1])/(3.0*(-1./self.SiFa)) 
#        print "shift",ShFa
        TrueSh = InverseCartesianCoordAmpRotoTranslation(ShFa,(0,0),self.Rot,1.)
#        print "tshift", TrueSh
        self.ShFa = TrueSh      
        return self.ShFa
        