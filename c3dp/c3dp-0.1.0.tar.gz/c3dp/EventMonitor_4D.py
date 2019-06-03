import mcvine, mcvine.components
from mcni.AbstractComponent import AbstractComponent
import numpy as np
import os

class EventMonitor_4D( AbstractComponent ):

    def __init__(self, name, xwidth, yheight):
        self.name = name
        self.xwidth= xwidth; self.yheight = yheight
        return
    
    def process(self, neutrons):
        if not len(neutrons):
            return
        from mcni.neutron_storage import neutrons_as_npyarr, ndblsperneutron
        arr = neutrons_as_npyarr(neutrons)
        arr.shape = -1, ndblsperneutron
        x = arr[:,0]; y = arr[:,1]; z = arr[:,2]
        vx = arr[:,3]; vy = arr[:,4]; vz = arr[:,5]
        s1 = arr[:,6]; s2 = arr[:,7];
        t = arr[:,8];  t0 = t.copy()
        p = arr[:,9]

        # propagate to z = 0
        self._propagateToZ0(x,y,z,vx,vy,vz,t)

        # Apply filter if area is positive
        assert self.xwidth > 0 and self.yheight > 0

        # Filter
        ftr    = (x >= -self.xwidth/2)*(x <= self.xwidth/2)*(y >= -self.yheight/2)*(y <= self.yheight/2)*(t>t0)

        x = x[ftr]; y = y[ftr]; z = z[ftr];
        vx = vx[ftr]; vy = vy[ftr]; vz = vz[ftr];
        s1 = s1[ftr]; s2 = s2[ftr]; t = t[ftr]; p = p[ftr];
        events = x,y,z,t,p
        self.save(events)
        return
    
    def save(self, events):
        outdir = self._getOutputDirInProgress()
        np.save(os.path.join(outdir, "%s-events4D.npy"%self.name), events)
    
    def _propagateToZ0(self, x,y,z, vx,vy,vz, t):
        dt = -z/vz
        x += vx*dt
        y += vy*dt
        z[:] = 0
        t += dt
        return
