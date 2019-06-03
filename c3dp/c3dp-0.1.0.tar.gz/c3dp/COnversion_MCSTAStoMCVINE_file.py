import mcni
from mcni import neutron_storage as ns
import os, numpy as np


def mcstas2mcvine(inpath, outpath):
    arr = np.loadtxt(inpath)
    N = len(arr)
    newarr = np.zeros((N, 10), dtype=float)
    newarr[:, list(range(10))] = arr[:, [1,2,3, 4,5,6, 8,9, 7, 0]]
    neutrons = ns.neutrons_from_npyarr(newarr)
    ns.dump(neutrons, outpath)
    return

mcstas2mcvine('/home/fi0/Instrument_optimization/neutrons_before_sample_oldG.dat', 'Neutrons_mcvine.dat')