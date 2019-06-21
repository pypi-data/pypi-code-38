from mdio.xtcio import xtc_open
import numpy as np

testunitcell_vectors = np.array(
    [[5.94140005, 0.,         0.        ],
     [0.,         5.94140005, 0.        ],
     [0.,         0.,         5.94140005]]
    )
xtcfile = 'examples/test.xtc'
pdbfile = 'examples/test.pdb'
testxyz = np.array([2.837, 4.348, 2.527]) 
testi = 11

def test_opener():
    f = xtc_open(xtcfile, 'r')
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
    fin = xtc_open(xtcfile, 'r')
    fout = xtc_open('tmp.xtc', 'w')
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

    finA = xtc_open(xtcfile, 'r')
    finB = xtc_open('tmp.xtc', 'r')
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    i = 0
    while frameA is not None:
        #if not np.allclose(frameA.xyz, frameB.xyz):
        #    print(i, frameA.xyz[-1],frameB.xyz[-1])
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
        i += 1
    finA.close()
    finB.close()

def test_nobox():
    xtcfile = 'examples/test_nobox.xtc'
    testi = 11

    f = xtc_open(xtcfile, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi
    f.close()

def test_atom_indices():
    fsel = xtc_open(xtcfile, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = xtc_open(xtcfile, 'r', top=pdbfile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_selection():
    fsel = xtc_open(xtcfile, top=pdbfile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

