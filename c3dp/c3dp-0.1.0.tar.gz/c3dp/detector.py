import mcvine, mcvine.components
from mcni.AbstractComponent import AbstractComponent
from mcni.utils import conversion
import numpy as np
import os
from mcni import neutron_buffer, neutron

class Detector(AbstractComponent):

    "2D detector center a (0,0,0) and perpendicular to z"

    def __init__(self, name, xwidth, yheight, dx, dy, outfile, tofbinsize=0.1, start_index=0):
        self.name = name
        assert xwidth > 0 and yheight > 0 and dx>0 and dy>0
        self.xwidth = xwidth
        self.yheight = yheight
        self.dx = dx
        self.dy = dy
        self.Nx = int(xwidth/dx)
        self.Ny = int(yheight/dy)
        print (self.Nx, self.Ny)
        self.outfile = outfile
        self.tofbinsize = tofbinsize
        self.start_index = start_index
        return

    def process(self, neutrons):
        if not len(neutrons):
            return
        from mcni.neutron_storage import neutrons_as_npyarr, ndblsperneutron # number of doubles per neutrons thats means each neutron is represented by x, y, z, vx, vy, vz, s1, s2, t, t0, p (10 double variables)

        arr = neutrons_as_npyarr(neutrons) #converting the input neutrons to array
        arr.shape = -1, ndblsperneutron
        x = arr[:, 0]; y = arr[:, 1]; z = arr[:, 2]
        vx = arr[:, 3]; vy = arr[:, 4]; vz = arr[:, 5]
        s1 = arr[:, 6]; s2 = arr[:, 7];
        t = arr[:, 8]; t0 = t.copy()
        p = arr[:, 9]

        # propagate to Z = 0
        self._propagateToZ0(x, y, z, vx, vy, vz, t)

        # Filter
        ftr = (x >= -self.xwidth / 2) * (x < self.xwidth / 2) \
              * (y >= -self.yheight / 2) * (y < self.yheight / 2) \
              * (t > t0)
        #
        xindex = (x+self.xwidth/2)//self.dx; xindex[xindex<0] = 0; xindex[xindex>=self.Nx]=self.Nx-1
        yindex = (y+self.yheight/2)//self.dy; yindex[yindex<0] = 0; yindex[yindex>=self.Ny]=self.Ny-1
        index = yindex + xindex * self.Ny + self.start_index
        N = ftr.sum()
        from mccomponents.detector.event_utils import datatype
        events = np.zeros(N, dtype=datatype)
        events['pixelID'] = index[ftr]
        events['tofChannelNo']=t[ftr]*1e6/self.tofbinsize
        events['p'] = p[ftr]
        self._save(events)
        return
    

    def _save(self, events):
        outdir = self._getOutputDirInProgress()
        np.save(os.path.join(outdir, self.outfile), events)
        return
                                    

    def _propagateToZ0(self, x, y, z, vx, vy, vz, t):
        dt = -z / vz
        x += vx * dt
        y += vy * dt
        z[:] = 0
        t += dt
        return


