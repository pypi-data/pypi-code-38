from mdio.openmmio import openmm_open
import numpy as np
import pytest

try:
    from simtk.openmm.app import PDBFile
except:
    pytest.skip("Skipping OpenMM tests as not installed.", 
                allow_module_level=True)

pdbfile = 'examples/test10.pdb'
testxyz = np.array([2.837, 4.348, 2.527])
testunitcell_vectors = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 11
openmmtrajectory = PDBFile(pdbfile)

def test_opener1():
    n = openmmtrajectory.getNumFrames()
    assert n == testi - 1
    f = openmm_open(openmmtrajectory, 'r')
    n = f.n_frames
    assert n == testi - 1
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
    fsel = openmm_open(openmmtrajectory, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = openmm_open(openmmtrajectory, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_topology_indices():
    f = openmm_open(openmmtrajectory, 'r', top=pdbfile, selection=range(10))
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 1

def test_selection():
    fsel = openmm_open(openmmtrajectory, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

