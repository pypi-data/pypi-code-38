import mdio
import numpy as np
import pytest
try:
    import mdtraj as mdt
    has_mdt = True
except:
    has_mdt = False

try:
    from simtk.openmm.app import PDBFile
    has_openmm = True
except:
    has_openmm = False

ncfile = 'examples/test.nc'
dcdfile = 'examples/test.dcd'
xtcfile = 'examples/test.xtc'
pdbfile = 'examples/test.pdb'
pdb10file = 'examples/test10.pdb'
grofile = 'examples/test.gro'
testcrds = np.array([2.837, 4.348, 2.527])
testbox = np.array([[5.9414,  0.,     0.   ],
     [ 0.,    5.9414,  0.,   ],
     [ 0.,     0.,    5.9414]], dtype=np.float32)
testi = 10

def test_loader():
    t = mdio.load(ncfile)
    assert np.allclose(t.xyz[0,0], testcrds) is True
    assert np.allclose(t[0].unitcell_vectors, testbox) is True
    assert len(t) == testi

def test_opener():
    fin = mdio.open(ncfile)
    fout = mdio.open('tmp.dcd', 'w')
    frame = fin.read_frame()
    while frame is not None:
        fout.write_frame(frame)
        frame = fin.read_frame()
    fin.close()
    fout.close()

def test_mdt_load():
    if not has_mdt:
        pytest.skip("mdtraj not installed.")
    mdtrajectory = mdt.load(ncfile, top=pdbfile)
    t = mdio.load(mdtrajectory)
    assert t.n_frames == mdtrajectory.n_frames

def test_openmm_load():
    if not has_openmm:
        pytest.skip("openmm not installed.")
    openmm_molecule  = PDBFile(pdb10file)
    t = mdio.load(openmm_molecule)
    assert t.n_frames == openmm_molecule.getNumFrames()

def test_consistency():
    finA = mdio.open(ncfile, 'r')
    finB = mdio.open('tmp.dcd', 'r')
    frameA = finA.read_frame()
    frameB = finB.read_frame()
    while frameA is not None:
        assert np.allclose(frameA.xyz, frameB.xyz) is True
        frameA = finA.read_frame()
        frameB = finB.read_frame()
    finA.close()
    finB.close()

def test_multiopen():
    t = mdio.load([ncfile, dcdfile])
    assert len(t) == 20

def test_with_top():
    t = mdio.load(ncfile, top=pdbfile)
    assert t.topology is not None

def test_with_top_and_indices():
    t = mdio.load(ncfile, top=pdbfile, selection=range(10))
    assert t.n_atoms == 10
    sel = t.topology.select('name CA')
    assert len(sel) == 1

def test_with_selection_1():
    t = mdio.load(ncfile, top=pdbfile, selection='name CA')
    assert t.n_atoms == 58

def test_with_selection_2():
    t = mdio.load(ncfile, top=pdbfile, selection='not residue 1 to 3')
    assert t.n_atoms == 840

def test_with_selection_3():
    t = mdio.load(xtcfile, top=grofile, selection='name CA')
    assert t.n_atoms == 58

def test_with_selection_4():
    t = mdio.load(dcdfile, top=grofile, selection='not residue 1 to 3')
    assert t.n_atoms == 840

def test_with_selection_5():
    t = mdio.load(dcdfile, top=grofile, selection='element N')
    assert t.n_atoms == 84

def test_with_selection_6():
    t = mdio.load(dcdfile, top=grofile, selection='mass > 2.0')
    assert t.n_atoms == 454

def test_with_slice_2():
    t = mdio.load(dcdfile + '[3:10:3]', top=grofile, selection='mass > 2.0')
    assert t.n_frames == 3

def test_with_slice_1():
    t = mdio.load(dcdfile + '[:5]', top=grofile, selection='mass > 2.0')
    assert t.n_frames == 5

def test_make_whole():
    t = mdio.load(pdbfile)
    t2 = t.packed_around(selection='index 1')
    assert t2.rmsd_from(t)[0] > 1.0
    t3 = t2.make_whole()
    assert t3.rmsd_from(t)[0] < 0.01
