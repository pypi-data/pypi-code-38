from mdio.mdtio import mdt_open
import numpy as np
import pytest

try:
    import mdtraj as mdt
except:
    pytest.skip("Skipping MDTraj tests as not installed.", 
                allow_module_level=True)

ncfile = 'examples/test.nc'
pdbfile = 'examples/test.pdb'
testxyz = np.array([2.837, 4.348, 2.527])
testunitcell_vectors = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 11
mdtrajectory = mdt.load(ncfile, top=pdbfile)

def test_opener1():
    f = mdt_open(mdtrajectory, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    assert np.allclose(frame.unitcell_vectors, testunitcell_vectors) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_atom_indices():
    fsel = mdt_open(mdtrajectory, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = mdt_open(mdtrajectory, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_topology_indices():
    f = mdt_open(mdtrajectory, 'r', top=pdbfile, selection=range(10))
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 1

def test_selection():
    fsel = mdt_open(mdtrajectory, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

