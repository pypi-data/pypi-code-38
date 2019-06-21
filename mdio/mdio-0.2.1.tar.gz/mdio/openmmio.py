import mdio.base
from tempfile import NamedTemporaryFile

class OpenMMReader(object):
    def __init__(self, trajectory, top=None, selection=None):

        n_frames = trajectory.getNumFrames()
        topology = trajectory.getTopology()
        pdbfile = NamedTemporaryFile(mode='w', suffix='.pdb')
        trajectory.writeHeader(topology, pdbfile)
        for frame in range(n_frames):
            positions = trajectory.getPositions(frame=frame)
            pdbfile.write('MODEL  {:6d}\n'.format(frame))
            trajectory.writeModel(topology, positions, pdbfile)
            pdbfile.write('ENDMDL\n')
        trajectory.writeFooter(topology, pdbfile)
        pdbfile.flush()
        self.trajectory = mdio.base.load(pdbfile.name, 
                                         selection=selection)
        pdbfile.close()
        self.index = -1
        self.n_frames = int(self.trajectory.n_frames)
        assert self.n_frames == n_frames

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


def openmm_open(trajectory, mode='r', top=None, selection=None):
    """
    Open an OpenMM "trajectory"
    """
    if mode != 'r':
        raise IOError('Error: OpenMM trajectories can only be read')
    return OpenMMReader(trajectory, top=top,
                        selection=selection)

