
# EXAMPLE:
# change the conf file for detector angles
# ./scripts/reduce_mantid.py mantid/sim.nxs mantid/SNAP_virtual_Definition.xml clampcellSi 0.5,0.01,4
import unittest
from mantid.simpleapi import *
from matplotlib import pyplot as plt
import os, sys, numpy as np


thisdir = os.path.abspath(os.path.dirname(__file__))
libpath = os.path.join(thisdir, '../c3dp')
if not libpath in sys.path:
    sys.path.insert(0, libpath)
if not thisdir in sys.path:
    sys.path.insert(0, thisdir)


import reduce_nexasdata_using_mantid as reduce

sample='collimator_plastic_temperature_masked.nxs'


path=os.path.join(thisdir, '../mantid/{}' .format(sample)) #path where the nexus file to be reduced
sample='collimator_plastic_temperature' #name of the saved file
binning='0.5,0.01,4'

def test_reduce():
    d_sim, I_sim, E_sim=reduce.mantid_reduction(path, binning)

    plt.errorbar(d_sim, I_sim, E_sim)
    plt.savefig(os.path.join(thisdir, '../figures/I_d_{sample}.png'.format(sample=sample)))

    np.save(os.path.join(thisdir, '../results/I_d_{sample}.npy'.format(sample=sample)), [d_sim, I_sim, E_sim])

if __name__ == '__main__':
    test_reduce()


