import numpy as np
import mdio.base 
from mdio.utilities import la2v, v2la, selection_to_indices

class RstFileReader(object):
    def __init__(self, filename, top=None, selection=None):
        self.filename = filename
        if top is not None:
            self.top = mdio.base.Topology(top)
        else:
            self.top = None
        self.atom_indices = selection_to_indices(selection, self.top)
        if self.atom_indices is not None:
            if self.top is not None:
                self.top = self.top.subset(self.atom_indices)
        self.index = -1
        self.f = open(self.filename)
        self.buffer = self.f.readline()
        if self.buffer == "":
            self.buffer = 'EOF   '
            
    def read_frame(self):
        if self.buffer[:6] == 'EOF   ':
            return None
        title = self.buffer
        self.buffer = self.f.readline()
        self.index += 1
        if self.buffer == '':
            return None
        n_atoms = int(self.buffer[:5])
        try:
            time = float(self.buffer[5:20])
        except:
            time = float(self.index)
        self.buffer = self.f.readline()
        if self.buffer == '':
            return None
        crds = self.read_coordinates(n_atoms)
        if len(crds) != n_atoms:
            return None
        if self.atom_indices is not None:
            crds = crds[self.atom_indices]
        vel = self.read_coordinates(n_atoms)
        if len(vel) == 0:
            box = None
        else:
            if len(vel) != n_atoms:
                print('LEN VEL = ', len(vel))
                if len(vel) <= 2:
                    lengths = vel[0]
                    if len(vel) == 2:
                        angles = vel[1]
                    else:
                        angles = np.array([90.0] * 3)
                    box = la2v(lengths, angles)
                else:
                    return None
        if box is None:
            box = self.read_coordinates(2)
            if len(box) > 0:
                lengths = box[0]
                if len(box) == 2:
                    angles = box[1]
                else:
                    angles = np.array([90.0] * 3)
                box = la2v(lengths, angles)
            else:
                box = None

        frame = mdio.base.Frame(crds, 
                      box=box, 
                      time=time,
                      units='angstroms')
        return frame

    def read_coordinates(self, n_atoms):
        if self.buffer[:6] == 'EOF   ':
            return np.zeros((0, 3))
        xyz = []
        n_coords = 3 * n_atoms
        blank = ' ' * 12
        end = False
        while not end:
            self.buffer = self.buffer.ljust(72)
            j = min(6, n_coords) * 12
            wx = [self.buffer[i:i+12] for i in range(0, j, 12)]
            for w in wx:
                if w != blank and not end:
                    try:
                        xyz.append(float(w))
                    except:
                        print('W = ', w)
                        print(self.buffer)
                        print(self.buffer[:6] == 'EOF   ')
                        raise
                    n_coords -= 1
                    end = n_coords == 0
                else:
                    end = True
            self.buffer = self.f.readline()
            if self.buffer == "":
                self.buffer = 'EOF   '
                end = True
            n_found = (3 * n_atoms - n_coords) // 3
        return np.array(xyz).reshape((n_found, 3))
    
    def read(self):
        frames = []
        frame = self.read_frame()
        while frame is not None:
            frames.append(frame)
            frame = self.read_frame()
        return mdio.base.Trajectory(frames, top=self.top)

    def close(self):
        self.f.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
        
class RstFileWriter(object):
    def __init__(self, filename, top=None):
        self.filename = filename
        self.index = -1
        self.f = open(filename, 'w')

    def write_frame(self, frame):
        scalefactor = 10.0
        self.index += 1
        titleformat = 'Created by mdio \n{:5d}{:15.7f}\n'
        self.f.write(titleformat.format(frame.n_atoms, frame.time))
        for i, x in enumerate(frame.xyz.flatten()):
            x = x * scalefactor
            self.f.write('{:12.7f}'.format(x))
            if (i + 1) % 6 == 0:
                self.f.write('\n')
        if len(frame.xyz) % 2 == 1:
            self.f.write('\n')
        if frame.unitcell_vectors is not None:
            lengths, angles = v2la(frame.unitcell_vectors * scalefactor)
            self.f.write(('{:12.7f}' * 3).format(*lengths))
            self.f.write(('{:12.7f}' * 3).format(*angles))
            self.f.write('\n')
        
    def write(self, trajectory):
        for i in range(len(trajectory)):
            self.write_frame(trajectory.frame(i))

    def close(self):
        self.f.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

def rst_open(filename, mode='r', top=None, selection=None):
    """
    Open a Rst file.
    """
    if not mode in ["r", "w"]:
        raise ValueError('Error: mode must be "r" or "w".')
    if mode == 'r':
        return RstFileReader(filename, top=top, selection=selection)
    else:
        return RstFileWriter(filename)
