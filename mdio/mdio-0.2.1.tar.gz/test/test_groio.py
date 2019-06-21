from mdio.groio import gro_open
import mdio.groio
import numpy as np

grofile = 'examples/test.gro'
testxyz = np.array([4.714, 1.252, -0.321])
testunitcell_vectors = np.array([[5.9108,  0.,     0.   ],
     [ 0.,     5.9108,  0.,   ],
     [ 0.,     0.,     5.9108]], dtype=np.float32)
testi = 2

def test_frame_read():
    f = mdio.groio.GroFileReader(grofile)
    frame = f.read_frame()
    assert frame.n_atoms == 892
    print(frame.unitcell_vectors)
    #assert frame.unitcell_vectors is not None

def test_opener1():
    f = gro_open(grofile, 'r')
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
    fin = gro_open(grofile, 'r')
    fout = gro_open('tmp.gro', 'w', top=grofile)
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

    finA = gro_open(grofile, 'r')
    finB = gro_open('tmp.gro', 'r')
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    while frameA is not None:
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
    finA.close()
    finB.close()

def test_nobox():
    grofile = 'examples/test_nobox.gro'

    f = gro_open(grofile, 'r')
    frame = f.read_frame()
    assert np.allclose(frame.xyz[0], testxyz) is True
    i = 1
    while frame is not None:
        frame = f.read_frame()
        i += 1
    assert i == testi

    f.close()

def test_selection1():
    fsel = gro_open(grofile, selection=range(12))
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 12
    fsel.close()

def test_topology():
    f = gro_open(grofile, 'r', top=grofile)
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 58

def test_topology_selection():
    f = gro_open(grofile, 'r', top=grofile, selection=range(10))
    t = f.read()
    sel = t.topology.select('name CA')
    assert len(sel) == 1

def test_selection2():
    fsel = gro_open(grofile, top=grofile, selection='name CA')
    framesel = fsel.read_frame()
    assert len(framesel.xyz) == 58
    fsel.close()

