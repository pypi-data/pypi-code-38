import mdio.base
from tempfile import NamedTemporaryFile

class MDIOReader(object):
    def __init__(self, trajectory, top=None, selection=None):

        if not isinstance(trajectory, mdio.base.Trajectory):
            raise TypeError('Error - not an mdio.Trajectory')
        self.trajectory = trajectory
        if selection is not None:
            self.trajectory = self.trajectory.select(selection)
        self.n_frames = self.trajectory.n_frames
        self.index = -1

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

def mdio_open(trajectory, mode='r', top=None, selection=None):
    """
    Open an MDIO trajectory
    """
    if mode != 'r':
        raise IOError('Error: MDIO trajectories can only be read')
    return MDIOReader(trajectory, top=top,
                        selection=selection)

