from mdio.rstio import rst_open
import numpy as np

rstfile = 'examples/test.rst7'
pdbfile = 'examples/test.pdb'
testxyz = np.array([2.837, 4.348, 2.527])
testunitcell_vectors = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 2

def test_opener():
    f = rst_open(rstfile, 'r')
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
    fin = rst_open(rstfile, 'r')
    fout = rst_open('tmp.rst', 'w')
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

    finA = rst_open(rstfile, 'r')
    finB = rst_open('tmp.rst', 'r')
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    while frameA is not None:
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
    finA.close()
    finB.close()

def test_nobox():
    rstfile = 'examples/test_nobox.rst7'

    f = rst_open(rstfile, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_atom_indices():
    fsel = rst_open(rstfile, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = rst_open(rstfile, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_selection():
    fsel = rst_open(rstfile, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

