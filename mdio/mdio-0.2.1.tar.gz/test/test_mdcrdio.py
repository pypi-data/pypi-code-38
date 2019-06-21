from mdio.mdcrdio import mdcrd_open
import numpy as np

mdcrdfile = 'examples/test.mdcrd'
pdbfile = 'examples/test.pdb'
testxyz = np.array([2.837, 4.348, 2.527])
testunitcell_vectors = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 11

def test_opener():
    f = mdcrd_open(mdcrdfile, 'r', top=pdbfile)
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    assert frame.unitcell_vectors is not None
    assert np.allclose(frame.unitcell_vectors, testunitcell_vectors) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi
    f.close()

def test_consistency():
    fin = mdcrd_open(mdcrdfile, 'r', top=pdbfile)
    fout = mdcrd_open('tmp.mdcrd', 'w')
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

    finA = mdcrd_open(mdcrdfile, 'r', top=pdbfile)
    finB = mdcrd_open('tmp.mdcrd', 'r', top=pdbfile)
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    while frameA is not None:
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
    finA.close()
    finB.close()

def test_nobox():
    mdcrdfile = 'examples/test_nobox.mdcrd'

    f = mdcrd_open(mdcrdfile, 'r', top=pdbfile)
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_atom_indices():
    fsel = mdcrd_open(mdcrdfile, selection=range(12), top=pdbfile)
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = mdcrd_open(mdcrdfile, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_selection():
    fsel = mdcrd_open(mdcrdfile, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

