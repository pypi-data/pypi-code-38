import os, glob, numpy as np
from mcni.utils import conversion

def process(neutronspath):
    "angle: in degrees"
    from mcni.neutron_storage import readneutrons_asnpyarr as rdn
    narr = rdn(neutronspath)
    x = narr[:, 0]; y = narr[:, 1]; z = narr[:, 2]
    vx = narr[:,3]; vy = narr[:,4]; vz = narr[:,5]
    t = narr[:,8];  p = narr[:,9]
    v = (vx*vx + vy*vy +vz*vz)**.5
    cos2theta = vz/v
    lamda = 2 * np.pi / conversion.V2K / v
    sintheta = np.sqrt((1 - cos2theta) / 2)
    d = lamda / (2 * sintheta)
    return d, p
