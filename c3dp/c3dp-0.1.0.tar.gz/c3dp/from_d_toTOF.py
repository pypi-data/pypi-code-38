import os, glob, numpy as np
from mcni.utils import conversion


Mn=1.67e-27 #Mass of Neutrons (kg)
h=6.60e-34 #Planck's const (Js)

CF=(h*1e7)/Mn #(3.952) time should be in milisecond and wavelength should be in angstrom

def tof_from_d( d, angle, l1=14.699, l2=0.3, l3=0.5, xA=0.0, yA=0.0,zA=0.0):
    "angle: in degrees"

    L = l1 + l2 + np.sqrt(xA ** 2 + yA ** 2 + (zA + l3) ** 2)
    angle = np.deg2rad(angle*1.)
    m = np.array([
        [np.cos(angle), 0, np.sin(angle)],
        [0, 1, 0],
        [-np.sin(angle), 0, np.cos(angle)]
        ])
    labCoords = np.dot(m, np.array([xA, yA, zA])).T + [l3*np.sin(angle), 0, l3*np.cos(angle)]
    # print labCoords[2]
    cos2theta = labCoords[2]/np.linalg.norm(labCoords, axis=-1)
    sintheta = np.sqrt((1 - cos2theta) / 2)
    # twotheta = np.arccos(cos2theta) * 180./np.pi
    lamda=d*(2 * sintheta)
    tof=lamda* L/CF


    return tof

t=tof_from_d(3.13,-50,)
print (t)
# x=np.array([[1,2,3], [4,5,6],[7,8,9]])
# print x[:,2]


