import mcvine, mcvine.components
from mcni.AbstractComponent import AbstractComponent
import numpy as np
import os
thisdir = os.path.dirname(__file__)

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

def instrument( sample='', angleMon1=45, angleMon2=135, beam=None, sourceTosample_x=0.0,
                sourceTosample_y=0.0,sourceTosample_z=0.0, detector_size=0.5):
    if beam is None:
        beam = os.path.join(thisdir, '../beam/Neutrons_mcvine.dat')
    instrument = mcvine.instrument()
    # a_source=mcvine.components.sources.Source_simple(Lambda0=1.4827, radius=0., width=0.001, height=0.001, dist=0.3, xw=0.001, yh=0.001)
    a_source = mcvine.components.sources.NeutronFromStorage('source', beam)
    instrument.append(a_source, position=(0, 0, 0))

    samplename = sample
    samplexml = os.path.join(thisdir, '../sample/sampleassembly_%s.xml' % samplename)
    sample = mcvine.components.samples.SampleAssemblyFromXml('sample', samplexml)
    instrument.append(sample, position=(sourceTosample_x,sourceTosample_y , sourceTosample_z),  relativeTo=a_source)
    
    save = mcvine.components.monitors.NeutronToStorage('save', 'scattered-neutrons.mcvine')
    instrument.append(save, position=(0,0,0), relativeTo=sample)
    
    angle1 = np.deg2rad(angleMon1)
    d = 0.5
    instrument.append(
        EventMonitor_4D('monitor1', detector_size, detector_size),
        position=(d * np.sin(angle1), 0, d * np.cos(angle1)),
        orientation=(0, np.rad2deg(angle1), 0),
        relativeTo=sample)

    angle2 = np.deg2rad(angleMon2)
    d = 0.5
    instrument.append(
        EventMonitor_4D('monitor2', detector_size, detector_size),
        position=(d * np.sin(angle2), 0, d * np.cos(angle2)),
        orientation=(0, np.rad2deg(angle2), 0),
        relativeTo=sample)
    return instrument

# if __name__ == '__main__': main()
