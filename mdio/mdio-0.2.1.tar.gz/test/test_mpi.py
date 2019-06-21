import mdio
import numpy as np
try:
    from mpi4py import MPI
    comm = MPI.COMM_WORLD
except ImportError:
    comm = None

ncfile = 'examples/test.nc'
dcdfile = 'examples/test.dcd'
xtcfile = 'examples/test.xtc'
pdbfile = 'examples/test.pdb'
testcrds = np.array([2.837, 4.348, 2.527])
testbox = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 10

def test_loader_1():
    t = mdio.mpi_load(ncfile, comm=comm)
    assert np.allclose(t.xyz[0,0], testcrds) is True
    assert np.allclose(t[0].unitcell_vectors, testbox) is True
    assert len(t) == testi

def test_loader_2():
    t = mdio.mpi_load([ncfile, dcdfile], comm=comm)
    assert np.allclose(t.xyz[0,0], testcrds) is True
    assert np.allclose(t[0].unitcell_vectors, testbox) is True
    assert len(t) == testi * 2
