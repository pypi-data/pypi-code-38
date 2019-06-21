import mdio.base
from tempfile import NamedTemporaryFile

class MDTrajReader(object):
    def __init__(self, trajectory, top=None, selection=None):

        pdbfile = NamedTemporaryFile(suffix='.pdb')
        ncfile = NamedTemporaryFile(suffix='.nc')
        trajectory[0].save(pdbfile.name)
        trajectory.save(ncfile.name)
        self.trajectory = mdio.base.load(ncfile.name, top=pdbfile.name,
                                         selection=selection)
        pdbfile.close()
        ncfile.close()
        self.index = -1
        self.n_frames = self.trajectory.n_frames

    def read_frame(self):
        self.index += 1
        if self.index >= self.n_frames:
            return None

        return self.trajectory.frame(self.index)

    def read(self):
        self.index += 1
        return self.trajectory[self.index:]

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

def mdt_open(trajectory, mode='r', top=None, selection=None):
    """
    Open an MDTraj trajectory
    """
    if mode != 'r':
        raise IOError('Error: MDTraj trajectories can only be read')
    return MDTrajReader(trajectory, top=top,
                        selection=selection)

