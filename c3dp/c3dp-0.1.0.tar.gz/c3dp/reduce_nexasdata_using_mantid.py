from mantid.simpleapi import *
from matplotlib import pyplot as plt
import numpy as np
import sys

thisdir = os.path.abspath(os.path.dirname(__file__))
if thisdir not in sys.path:
    sys.path.insert(0, thisdir)

def mantid_reduction(nexus_file, binning):
    sim=Load(nexus_file)
    I_d=ConvertUnits(sim, Target='dSpacing', AlignBins=True)

    sum_I_d=SumSpectra(I_d)
    hist=Rebin(sum_I_d, Params=binning)


    x_sim = hist.readX(0)
    d_sim = (x_sim[1:] + x_sim[:-1]) / 2
    I_sim = hist.readY(0)
    error=hist.readE(0)
    return(d_sim, I_sim, error)




