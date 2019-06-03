

import os, sys, glob
thisdir = os.path.abspath(os.path.dirname(__file__))
import numpy as np
from mantid2mcvine.nxs import template as nxs_template, Events2Nxs

def create_nexus(datadir,fileTOsave, template ):
    # template = os.path.join(thisdir, '../mantid/{}.nxs'.format(template_name))

    det = "{directoryName}/*/detector*.npy".format(directoryName=datadir)

    detector = glob.glob(det)


    # det2 = "{directoryName}/*/detector2.npy".format(directoryName=datadir)
    # detector2 = glob.glob(det2)

    # print (len(detector2))
    events=[]

    for npyf in detector:
        narr = np.load(npyf)
        events.append(narr)

    # e1 = np.load(detector1)
    # e2 = np.load(detector2)
    events = np.hstack(events)



    N = 256*3
    e2n = Events2Nxs.Event2Nxs(template, npixels=2*N*N, nmonitors=0)
    # e2n.run('./debug-bsd/step0/events.npy', 'sim.nxs')
    e2n.write(events, tofbinsize=0.1, nxsfile=fileTOsave)


