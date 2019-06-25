from ..imaging.visualize import *
from ..tpf import *

directory = 'examples'
mkdir(directory)

def test_animation(howmanydays=1.0):
    tpf = download_kepler_tpf()
    animate_tpf(tpf, howmanydays=howmanydays)
