import numpy as np
import mdio.base 
from mdio.utilities import la2v, v2la, selection_to_indices

class MDCRDFileReader(object):
    def __init__(self, filename, top=None, selection=None):
        self.filename = filename
        self.top = top
        if self.top is None:
            raise IOError('Error - cannot load an MDCRD format file without a topology.')
        self.top = mdio.base.Topology(self.top)
        self.atom_indices = selection_to_indices(selection, self.top)
        self.n_atoms = self.top.n_atoms
        if self.atom_indices is not None:
            if self.top is not None:
                self.top = self.top.subset(self.atom_indices)
        self.index = -1
        self.f = open(self.filename)
        title  = self.f.readline()
        self.buffer = self.f.readline()
        if self.buffer == "":
            self.buffer = 'EOF   '
            
    def read_frame(self):
        if self.buffer[:6] == 'EOF   ':
            return None
        crds = self.read_coordinates(self.n_atoms)
        if len(crds) != self.n_atoms:
            return None
        if self.atom_indices is not None:
            crds = crds[self.atom_indices]
        if len(self.buffer.rstrip()) <= 72:
            box = self.read_coordinates(2)
            if len(box) == 0:
                box = None
            else:
                lengths = box[0]
                angles = np.ones((3)) * 90.0
                if len(box) == 2:
                    angles = box[1]
                box = la2v(lengths, angles)
        else:
            box = None

        frame = mdio.base.Frame(crds, 
                      box=box, 
                      time=self.index,
                      units='angstroms')
        return frame

    def read_coordinates(self, n_atoms):
        if self.buffer[:6] == 'EOF   ':
            return np.zeros((0, 3))
        xyz = []
        n_coords = 3 * n_atoms
        blank = ' ' * 8
        end = False
        while not end:
            self.buffer = self.buffer.rstrip().ljust(80)
            j = min(10, n_coords) * 8
            wx = [self.buffer[i:i+8] for i in range(0, j, 8)]
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
        
class MDCRDFileWriter(object):
    def __init__(self, filename, top=None):
        self.filename = filename
        self.index = -1
        self.f = open(filename, 'w')
        titleformat = 'Created by mdio \n'
        self.f.write(titleformat)

    def write_frame(self, frame):
        scalefactor = 10.0
        self.index += 1
        for i, x in enumerate(frame.xyz.flatten()):
            x = x * scalefactor
            self.f.write('{:8.3f}'.format(x))
            if (i + 1) % 10 == 0:
                self.f.write('\n')
        if (len(frame.xyz) * 3) % 10 != 0:
            self.f.write('\n')
        if frame.unitcell_vectors is not None:
            lengths, angles = v2la(frame.unitcell_vectors * scalefactor)
            self.f.write(('{:8.3f}' * 3).format(*lengths))
            self.f.write(('{:8.3f}' * 3).format(*angles))
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

def mdcrd_open(filename, mode='r', top=None, selection=None):
    """
    Open an MDCRD  file.
    """
    if not mode in ["r", "w"]:
        raise ValueError('Error: mode must be "r" or "w".')
    if mode == 'r':
        return MDCRDFileReader(filename, top=top, selection=selection)
    else:
        return MDCRDFileWriter(filename)
