from mdio.pdbio import pdb_open
import mdio.pdbio
import numpy as np

pdbfile = 'examples/test.pdb'
testxyz = np.array([4.7139, 1.2523, -0.3213])
testunitcell_vectors = np.array([[5.9108,  0.,     0.   ],
     [ 0.,    5.9108,  0.,   ],
     [ 0.,     0.,    5.9108]], dtype=np.float32)
testi = 2

def test_opener1():
    f = pdb_open(pdbfile, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    assert np.allclose(frame.unitcell_vectors, testunitcell_vectors) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_consistency():
    fin = pdb_open(pdbfile, 'r')
    fout = pdb_open('tmp.pdb', 'w', top=pdbfile)
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

    finA = pdb_open(pdbfile, 'r')
    finB = pdb_open('tmp.pdb', 'r')
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    while frameA is not None:
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
    finA.close()
    finB.close()

def test_nobox():
    pdbfile = 'examples/test_nobox.pdb'

    f = pdb_open(pdbfile, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_atom_indices():
    fsel = pdb_open(pdbfile, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = pdb_open(pdbfile, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_topology_indices():
    f = pdb_open(pdbfile, 'r', top=pdbfile, selection=range(10))
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 1

def test_selection():
    fsel = pdb_open(pdbfile, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

