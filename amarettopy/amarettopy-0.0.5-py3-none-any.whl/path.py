#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import sys, os, struct
import serial

class AmarettoQuinticPath:
    def __init__(self, t0, p0, v0, a0, t1, p1, v1, a1):
        """

        指定された始点と終点と期間から5次補間したパス計画を作成する

        Parameters
        ----------
        t0 : float
            開始時刻
        t1 : float
            終端時刻
        p0 : float
            開始位置
        p1 : float
            終端位置
        v0 : float
            開始速度
        v1 : float
            終端速度
        a0 : float
            開始加速度
        a1 : float
            終端加速度
        """

        assert(t1 > t0)

        t0 = float(t0)
        t1 = float(t1)
        self.t0 = t0
        self.t1 = t1

        self.k = [ (t0**3*(20*p1*t1**2+2*a0*t1**4+a1*t1**4+8*t1**3*v0-8*t1**3*v1) +t0**4*((-10*p1*t1)-a0*t1**3-2*a1*t1**3+10*t1**2*v1) +t0**5*(2*p1+a1*t1**2-2*t1*v1)+t0*(10*p0*t1**4+2*t1**5*v0) +t0**2*((-20*p0*t1**3)-a0*t1**5-10*t1**4*v0)-2*p0*t1**5) /(2*t0**5-10*t0**4*t1+20*t0**3*t1**2-20*t0**2*t1**3+10*t0*t1**4-2*t1**5)
                 ,-(t0**2*((-60*p0*t1**2)+60*p1*t1**2+a0*t1**4+3*a1*t1**4-16*t1**3*v0 -24*t1**3*v1) +t0**3*(4*a0*t1**3-4*a1*t1**3+24*t1**2*v0+16*t1**2*v1) +t0**4*((-3*a0*t1**2)-a1*t1**2+10*t1*v1)+t0**5*(2*a1*t1-2*v1) +t0*((-2*a0*t1**5)-10*t1**4*v0)+2*t1**5*v0) /(2*t0**5-10*t0**4*t1+20*t0**3*t1**2-20*t0**2*t1**3+10*t0*t1**4-2*t1**5)
                 ,(t0*((-60*p0*t1**2)+60*p1*t1**2-4*a0*t1**4+3*a1*t1**4-36*t1**3*v0 -24*t1**3*v1) +t0**2*((-60*p0*t1)+60*p1*t1+8*a0*t1**3+12*t1**2*v0-12*t1**2*v1) +t0**3*((-8*a1*t1**2)+24*t1*v0+36*t1*v1)-a0*t1**5+t0**4*(4*a1*t1-3*a0*t1) +a1*t0**5) /(2*t0**5-10*t0**4*t1+20*t0**3*t1**2-20*t0**2*t1**3+10*t0*t1**4-2*t1**5)
                 ,(t0*(80*p0*t1-80*p1*t1-4*a1*t1**3+28*t1**2*v0+32*t1**2*v1) +t0**2*(20*p0-20*p1-8*a0*t1**2+8*a1*t1**2-32*t1*v0-28*t1*v1)+8*t1**3*v1 +t0**3*(4*a0*t1-8*v0-12*v1)+12*t1**3*v0-a1*t1**4+3*a0*t1**4-20*p1*t1**2 +20*p0*t1**2+(a0-3*a1)*t0**4) /(2*t0**5-10*t0**4*t1+20*t0**3*t1**2-20*t0**2*t1**3+10*t0*t1**4-2*t1**5)
                 ,-(t0*(30*p0-30*p1-4*a0*t1**2+a1*t1**2-2*t1*v0+2*t1*v1) +14*t1**2*v1+t0**2*((-a0*t1)+4*a1*t1-14*v0-16*v1)+16*t1**2*v0-2*a1*t1**3 +3*a0*t1**3-30*p1*t1+30*p0*t1+(2*a0-3*a1)*t0**3) / (2*t0**5-10*t0**4*t1+20*t0**3*t1**2-20*t0**2*t1**3+10*t0*t1**4-2*t1**5)
                 ,(6*t1*v1+t0*((-2*a0*t1)+2*a1*t1-6*v0-6*v1)+6*t1*v0-a1*t1**2+a0*t1**2 +(a0-a1)*t0**2-12*p1+12*p0) /(2*t0**5-10*t0**4*t1+20*t0**3*t1**2-20*t0**2*t1**3+10*t0*t1**4-2*t1**5)
                 ]

        #print(self.k)

    def interp(self, t):
        """
        パス計画上の時刻に対する位置を返す

        Parameters
        ----------
        t : float
        """
        if self.t0 > t or t > self.t1 :
            return None

        return self.k[5] * t ** 5 + self.k[4]*t**4 + self.k[3] * t**3 + self.k[2] * t**2 + self.k[1] * t + self.k[0]


class AmarettoLinearPath:
    def __init__(self, t0, p0, t1, p1):
        """

        指定された始点と終点と期間から5次補間したパス計画を作成する

        Parameters
        ----------
        t0 : float
            開始時刻
        t1 : float
            終端時刻
        p0 : float
            開始位置
        p1 : float
            終端位置
        """

        assert(t1 > t0)

        t0 = float(t0)
        t1 = float(t1)
        self.t0 = t0
        self.t1 = t1
        self.k = [ (p1*t0-p0*t1)/(t0-t1)
                 , (p0-p1)/(t0-t1)
                 ]

    def interp(self, t):
        """
        パス計画上の時刻に対する位置を返す

        Parameters
        ----------
        t : float
        """
        #print(self.k5, self.k4, self.k3, self.k2, self.k1, self.k0)
        if self.t0 > t or t > self.t1 :
            return None
        return self.k[1]*t+self.k[0]


class AmarettoPath:
    def __init__(self, t_point_list, r0=0.2, r1=0.2):
        """

        指定された始点と終点と期間からパス計画を作成する
        t_point_list は [(t0,p0), (t1,p1)] というパターンのみ対応

        Parameters
        ----------
        p0 : float
            開始位置
        p1 : float
            終端位置
        t0 : float
            移動開始時刻
        t1 : float
            p1到達時刻
        r0 : float
            t1に対する開始加速期間の割合([0.1, 1])
        r1 : float
            t1に対する終端減速期間の割合([0.1, 1])
        """
        [(t0, p0), (t1, p1)] = t_point_list

        assert(t1 > t0)
        assert(r1 > 0 and r0 > 0 and (r1 + r0) <= 1)

        r = 1-r0/2-r1/2

        v0 = 0.0
        a0 = 0.0
        v1 = 0.0
        a1 = 0.0
        t1 = float(t1)

        t2 = t0*(1-r0)+t1*r0
        p2 = (p1*r0/2 + p0*(r - r0/2))/r
        v2 = (p1-p0)/((t1-t0)*r)
        a2 = 0.0
        t3 = t0*r1 + t1*(1-r1)
        p3 = (p0*r1/2 + p1*(r - r1/2))/r
        v3 = v2
        a3 = 0.0

        self.path = [AmarettoQuinticPath(t0,p0,v0,a0,t2,p2,v2,a2)]
        if t3 > t2:
            self.path.append(AmarettoLinearPath(t2,p2,t3,p3))
        self.path.append(AmarettoQuinticPath(t3,p3,v3,a3,t1,p1,v1,a1))

    def interp(self, t):
        """
        パス計画上の時刻に対する位置を返す

        Parameters
        ----------
        t : float
            時刻
        """
        for i in range(len(self.path)):
            x = self.path[i].interp(t)
            if x is not None:
                return x
        return None




