""" Utility functions and classes for SRP

Context : SRP
Module  : Spectroscopy.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 19/03/2011
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

Remarks : from R.J. Wells, Journal of Quantitative Spectroscopy and 
            Radiative Transfer, 62, 29, (1999)

History : (19/03/2011) First version.

"""

import math
import numpy


def VoigtFunctWells (a,v):
    y = a
    try:
        ndt = len(v)
    except TypeError:
        ndt = 1
    if ndt == 1:
        x = numpy.array([v])
    else:
        x = numpy.array(v)
    k = numpy.zeros(x.size)
    XP = numpy.zeros(5)
    XM = numpy.zeros(5)
    YP = numpy.zeros(5)
    YM = numpy.zeros(5)
    MQ = numpy.zeros(5)
    PQ = numpy.zeros(5)
    MF = numpy.zeros(5)
    PF = numpy.zeros(5)
    RRTPI = 0.56418958
    Y0 = 1.5
    Y0PY0 = Y0+Y0
    Y0Q = Y0*Y0
    C = (1.0117281, -0.75197147, 0.012557727, 0.010022008, -0.00024206814, 0.00000050084806)
    S = (1.393237, 0.23115241, -0.15535147, 0.0062183662, 0.000091908299, -0.00000062752596)
    T = (0.31424038, 0.94778839, 1.5976826, 2.2795071, 3.0206370, 3.8897249)
    YQ  = y*y                                             
    YRRTPI = y*RRTPI                                         

    if y >= 70.55:
        for i in range(0,x.size):
            XQ = x[i]*x[i]
            k[i] = YRRTPI / (XQ + YQ)
        return k

    RG1 = 1                                                   
    RG2 = 1
    RG3 = 1
   
    XLIM0 = math.sqrt(15100.0 + y*(40.0 - y*3.6)) 
    if y >= 8.425:
        XLIM1 = 0.0
    else:
        XLIM1 = math.sqrt (164.0 - y*(4.3 + y*1.8))
    XLIM2 = 6.8 - y
    XLIM3 = 2.4*y
    XLIM4 = 18.1*y + 1.65

    if y <= 0.000001:
        XLIM1 = XLIM0                       
        XLIM2 = XLIM0
        
    for i in range(x.size):
        ABX = math.fabs(x[i])
        XQ  = ABX*ABX                                                 
        if ABX >= XLIM0:
            k[i] = YRRTPI / (XQ + YQ)
        elif ABX >= XLIM1:                                 
            if RG1 != 0:
                RG1 = 0
                A0 = YQ + 0.5                                                 
                D0 = A0*A0
                D2 = YQ + YQ - 1.0
            D = RRTPI / (D0 + XQ*(D2 + XQ))
            k[i] = D*y * (A0 + XQ)
        elif ABX >= XLIM2:                                   
            if RG2 != 0:
                RG2 = 0
                H0 =  0.5625 + YQ*(4.5 + YQ*(10.5 + YQ*(6.0 + YQ)))           
                H2 = -4.5    + YQ*(9.0 + YQ*( 6.0 + YQ* 4.0))
                H4 = 10.5    - YQ*(6.0 - YQ*  6.0)
                H6 = -6.0    + YQ* 4.0
                E0 =  1.875  + YQ*(8.25 + YQ*(5.5 + YQ))
                E2 =  5.25   + YQ*(1.0  + YQ* 3.0)
                E4 =  0.75*H6
            D = RRTPI / (H0 + XQ*(H2 + XQ*(H4 + XQ*(H6 + XQ))))
            k[i] = D*y * (E0 + XQ*(E2 + XQ*(E4 + XQ)))
        elif ABX < XLIM3:
            if RG3 != 0:
                RG3 = 0
                Z0 = 272.1014 + y*(1280.829 + y*(2802.870 + y*(3764.966 + y*(3447.629 + y*(2256.981 + y*(1074.409 + y*(369.1989 + y*(88.26741 + y*(13.39880 + y)))))))))
                Z2 = 211.678 + y*(902.3066 + y*(1758.336 + y*(2037.310 + y*(1549.675 + y*(793.4273 + y*(266.2987 + y*(53.59518 + y*5.0)))))))
                Z4 = 78.86585 + y*(308.1852 + y*(497.3014 + y*(479.2576 + y*(269.2916 + y*(80.39278 + y*10.0)))))
                Z6 = 22.03523 + y*(55.02933 + y*(92.75679 + y*(53.59518 + y*10.0)))
                Z8 = 1.496460 + y*(13.39880 + y*5.0)
                P0 = 153.5168 + y*(549.3954 + y*(919.4955 + y*(946.8970 + y*(662.8097 + y*(328.2151 + y*(115.3772 + y*(27.93941 + y*(4.264678 + y*0.3183291))))))))
                P2 = -34.16955 + y*(-1.322256+ y*(124.5975 + y*(189.7730 + y*(139.4665 + y*(56.81652 + y*(12.79458 + y*1.2733163))))))
                P4 = 2.584042 + y*(10.46332 + y*(24.01655 + y*(29.81482 + y*(12.79568 + y*1.9099744))))
                P6 = -0.07272979  + y*(0.9377051+ y*(4.266322 + y*1.273316))
                P8 = 0.0005480304 + y*0.3183291
            D = 1.7724538 / (Z0 + XQ*(Z2 + XQ*(Z4 + XQ*(Z6 + XQ*(Z8+XQ)))))
            k[i] = D*(P0 + XQ*(P2 + XQ*(P4 + XQ*(P6 + XQ*P8))))
        else:
            YPY0 = y + Y0
            YPY0Q = YPY0*YPY0
            k[i] = 0.0
            for j in range(0,5,1):
                D = x[i] - T[j]
                MQ[j] = D*D
                MF[j] = 1.0 / (MQ[j] + YPY0Q)
                XM[j] = MF[j]*D
                YM[j] = MF[j]*YPY0
                D = x[i] + T[j]
                PQ[j] = D*D
                PF[j] = 1.0 / (PQ[j] + YPY0Q)
                XP[j] = PF[j]*D
                YP[j] = PF[j]*YPY0
            if ABX <= XLIM4:
                for j in range(0,5,1):
                    k[i] = k[i] + C[j]*(YM[j]+YP[j]) - S[j]*(XM[j]-XP[j])
            else: 
                YF = y + Y0PY0
                for j in range(0,5,1):
                    k[i] = k[i] + (C[j]*(MQ[j]*MF[j]-Y0*YM[j]) + S[j]*YF*XM[j]) / (MQ[j]+Y0Q) + (C[j]*(PQ[j]*PF[j]-Y0*YP[j]) - S[j]*YF*XP[j]) / (PQ[j]+Y0Q)
                k[i] = y*k[i] + math.exp(-XQ)

    return k
    
    

