import mcvine, mcvine.components
from mcni.AbstractComponent import AbstractComponent
import numpy as np
import os, sys
thisdir = os.path.abspath(os.path.dirname(__file__))
if thisdir not in sys.path:
    sys.path.insert(0, thisdir)

def instrument(beam=None, sample='', angleMon1=45, angleMon2=135,  detector_size=0.5,
               sourceTosample_x=0., sourceTosample_y=0., sourceTosample_z=0.):
    if beam is None:
        beam = os.path.join(thisdir, '../beam/Neutrons_mcvine.dat')
    instrument = mcvine.instrument()
    # a_source=mcvine.components.sources.Source_simple(Lambda0=1.4827, radius=0., width=0.001, height=0.001, dist=0.3, xw=0.001, yh=0.001)
    a_source = mcvine.components.sources.NeutronFromStorage('source', beam)
    instrument.append(a_source, position=(0, 0, 0))

    samplename = sample
    samplexml = os.path.join(thisdir, '../sample/sampleassembly_%s.xml' % samplename)
    sample = mcvine.components.samples.SampleAssemblyFromXml('sample', samplexml)
    instrument.append(sample, position=(sourceTosample_x, sourceTosample_y, sourceTosample_z), relativeTo=a_source)
    
    save = mcvine.components.monitors.NeutronToStorage('save', 'scattered-neutrons.mcvine')
    instrument.append(save, position=(0,0,0), relativeTo=sample)

    from detector import Detector
    angle1 = np.deg2rad(angleMon1)
    d = 0.5
    size = detector_size; pixel_size = size/256/3 #*1.00000001
    Npixels1D = 256*3; NpixelsPerPanel = Npixels1D**2
    instrument.append(
        Detector('detector1', size, size, pixel_size, pixel_size, 'detector1' ),
        position=(d * np.sin(angle1), 0, d * np.cos(angle1)),
        orientation=(0, np.rad2deg(angle1), 0),
        relativeTo=sample
    )

    angle2 = np.deg2rad(angleMon2)
    instrument.append(
        Detector('detector2', size, size, pixel_size, pixel_size, 'detector2', start_index=NpixelsPerPanel),
        position=(d * np.sin(angle2), 0, d * np.cos(angle2)),
        orientation=(0, np.rad2deg(angle2), 0),
        relativeTo=sample)
    return instrument

# if __name__ == '__main__': main()
