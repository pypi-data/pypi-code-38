import mdio
from mdio import Frame, Trajectory, Topology
from mdio.base import  get_indices
import numpy as np

#data = np.random.rand(13,56,3)
data = np.arange(13 * 56 * 3).reshape((13, 56, 3))
pdbfile = 'examples/test.pdb'

def test_frame_init():
    f = Frame(data[0])

def test_frame_select():
    atom_indices = range(5)
    f = Frame(data[0])
    fs = f.select(atom_indices)
    assert fs.xyz.shape[0] == 5

def test_frame_rmsd_from():
    f = Frame(data[0])
    f2 = Frame(data[0])
    f2.xyz[:, 0] = f.xyz[:, 1]
    f2.xyz[:, 1] = f.xyz[:, 2]
    f2.xyz[:, 2] = f.xyz[:, 0]
    assert f.rmsd_from(f2) < 0.01

def test_frame_fitted_to():
    f = Frame(data[0])
    f2 = Frame(data[0])
    f2.xyz[:, 0] = f.xyz[:, 1]
    f2.xyz[:, 1] = f.xyz[:, 2]
    f2.xyz[:, 2] = f.xyz[:, 0]
    f3 = f.fitted_to(f2)
    assert np.allclose(f3.xyz, f2.xyz, atol=1e-05)

def test_frame_packed_around():
    xyz = data[0]
    extent = xyz.max(axis=0) - xyz.min(axis=0)
    extent = extent + 1.0
    unitcell_vectors = np.array([[extent[0], 0, 0], [0, extent[1], 0], [0, 0, extent[2]]])
    xyz[0] = xyz.mean(axis=0)
    f = Frame(xyz, box=unitcell_vectors)
    f2 = f.packed_around([0])
    assert  np.allclose(f2.xyz, f.xyz)
    assert f2.rmsd_from(f) < 0.01
    f.xyz[0] = 0.0
    f2 = f.packed_around([0])
    assert not np.allclose(f2.xyz, f.xyz)

def test_traj_init_from_frame():
    t = Trajectory(Frame(data[0]))

def test_traj_init_from_frames():
    frames = [Frame(x) for x in data]
    t = Trajectory(frames)

def test_traj_init_from_array():
    t1 = Trajectory(data[0])
    t2 = Trajectory(data)

def test_traj_init_from_file():
    t2 = Trajectory(data)
    t3 = Trajectory(pdbfile)

def test_select():
    inds = get_indices('examples/test.pdb', 'name CA and residue 2 to 3')
    assert inds == [36, 42]

def test_bonding():
    top = Topology(pdbfile)
    t = Trajectory(pdbfile, top=top)
    
    assert len(t.topology.bonds) == 0
    t.topology.set_bonds(t.xyz[0], t.unitcell_vectors[0])
    assert len(t.topology.bonds) == 888
