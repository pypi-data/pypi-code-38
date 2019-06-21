from mdio.dcdio import dcd_open
import numpy as np

dcdfile = 'examples/test.dcd'
pdbfile = 'examples/test.pdb'
testxyz = np.array([2.837, 4.348, 2.527])
testunitcell_vectors = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 11

def test_opener():
    f = dcd_open(dcdfile, 'r')
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
    fin = dcd_open(dcdfile, 'r')
    fout = dcd_open('tmp.dcd', 'w')
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

    finA = dcd_open(dcdfile, 'r')
    finB = dcd_open('tmp.dcd', 'r')
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    while frameA is not None:
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
    finA.close()
    finB.close()

def test_nobox():
    dcdfile = 'examples/test_nobox.dcd'

    f = dcd_open(dcdfile, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_selection1():
    fsel = dcd_open(dcdfile, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = dcd_open(dcdfile, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_selection2():
    fsel = dcd_open(dcdfile, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

