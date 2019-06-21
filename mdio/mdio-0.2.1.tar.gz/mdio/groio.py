import numpy as np
import mdio.base 
from mdio.utilities import la2v, v2la, selection_to_indices
import six

def gro_atom_parse(line):
    """
    Extract data from a grofile line.
    """
    line = line.ljust(80)
    result = {}
    result['serial'] = int(line[15:20])
    result['name'] = line[10:15]
    result['resName'] = line[5:10]
    result['resSeq'] = int(line[0:5])
    result['x'] = float(line[20:28])
    result['y'] = float(line[28:36])
    result['z'] = float(line[36:44])

    result['chainID'] = '  '
    result['altLoc'] = ' '
    result['iCode'] = ' '
    result['occupancy'] = 1.0
    result['tempFactor'] = 0.0
    result['element'] = result['name'].lstrip(' 0123456789')[0]
    result['charge'] = '  '
    return result
    
class GroFileReader(object):
    def __init__(self, filename, top=None, selection=None):
        self.filename = filename
        #self.atom_indices = selection_to_indices(selection, top)
        self.selection = selection
        self.top = None
        self.unitcell_vectors = None
        self.index = -1
        self.f = open(self.filename)
        self.buffer = self.f.readline()
        if self.buffer == "":
            self.buffer = 'EOF   '
            
    def read_frame(self):
        time = self.read_title()
        if self.buffer[:6] == 'EOF   ':
            return None
        index = -1
        try:
            natoms = int(self.buffer)
        except:
            raise IOError('Error extracting topology from {}'.format(self.filename))
        result = []
        for i in range(natoms):
            index += 1
            self.buffer = self.f.readline()
            if self.buffer == "":
                return None
            data = gro_atom_parse(self.buffer)
            data['index'] = index
            data['chainid'] = ' '
            result.append(data)
        self.buffer = self.f.readline()
        if self.buffer == "":
            self.buffer = 'EOF   '
        if self.top is None:
            self.top = mdio.base.Topology(result)
            self.atom_indices = selection_to_indices(self.selection, self.top)
            if self.atom_indices is not None:
                self.top = self.top.subset(self.atom_indices)
        crds = np.array([[data['x'], data['y'], data['z']] for data in result])
        if self.atom_indices is not None:
            crds = crds[self.atom_indices]
        tmpwords = []
        for w in self.buffer.split():
            w = ''.join([i for i in w if not i in '-.'])
            tmpwords.append(w)
        if six.PY2:
            tmpwords = [unicode(w) for w in tmpwords]
        if all([w.isnumeric() for w in tmpwords]):
            words = self.buffer.split()
            unitcell_vectors = None
            if len(words) >= 3:
                unitcell_vectors = np.zeros((3,3))
                unitcell_vectors[0,0] = float(words[0])
                unitcell_vectors[1,1] = float(words[1])
                unitcell_vectors[2,2] = float(words[2])
            if len(words) >= 9:
                unitcell_vectors[0,1] = float(words[3])
                unitcell_vectors[0,2] = float(words[4])
                unitcell_vectors[1,0] = float(words[5])
                unitcell_vectors[1,2] = float(words[6])
                unitcell_vectors[2,0] = float(words[7])
                unitcell_vectors[2,1] = float(words[8])
            self.unitcell_vectors = unitcell_vectors
            self.buffer = self.f.readline()
            if self.buffer == "":
                self.buffer = 'EOF   '
        else:
            self.unitcell_vectors = None
        frame = mdio.base.Frame(crds, 
                      box=self.unitcell_vectors, 
                      time=time)
        return frame
    
    def read_title(self):
        if self.buffer[:6] == 'EOF   ':
            return None
        words = self.buffer.split()
        self.index += 1
        if 't=' in words:
            time = float(words[words.index('t=') + 1])
        else:
            time = float(self.index)
        self.buffer = self.f.readline()
        if self.buffer == "":
            self.buffer = 'EOF   '
        return time

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
        
class GroFileWriter(object):
    def __init__(self, filename, top=None):
        self.filename = filename
        self.index = -1
        self.f = open(filename, 'w')
        if top is None:
            raise RuntimeError('Error - cannot write Gro format without a topology.')
        self.top = mdio.base.Topology(top)

    def write_frame(self, frame):
        self.index += 1
        titleformat = 'Created by mdio t= {}\n {}\n'
        self.f.write(titleformat.format(frame.time, frame.n_atoms))
        atomformat = '{:5d}{:5s}{:5s}{:5d}{:8.3f}{:8.3f}{:8.3f}\n'
        for i, atom in enumerate(self.top.atoms):
            self.f.write(atomformat.format(atom.residue.resSeq,
                                           atom.residue.name, 
                                           atom.name,
                                           atom.serial,
                                           frame.xyz[i,0],
                                           frame.xyz[i,1],
                                           frame.xyz[i,2]))
        if frame.unitcell_vectors is not None:
            unitcell_vectors = []
            unitcell_vectors.append(frame.unitcell_vectors[0,0])
            unitcell_vectors.append(frame.unitcell_vectors[1,1])
            unitcell_vectors.append(frame.unitcell_vectors[2,2])
            unitcell_vectors.append(frame.unitcell_vectors[0,1])
            unitcell_vectors.append(frame.unitcell_vectors[0,2])
            unitcell_vectors.append(frame.unitcell_vectors[1,0])
            unitcell_vectors.append(frame.unitcell_vectors[1,2])
            unitcell_vectors.append(frame.unitcell_vectors[2,0])
            unitcell_vectors.append(frame.unitcell_vectors[2,1])
            if sum(unitcell_vectors[3:]) > 0:
                crystformat = '{:8.3f}' * 9 + '\n'
                self.f.write(crystformat.format(*unitcell_vectors))
            else:
                crystformat = '{:8.3f}' * 3 + '\n'
                self.f.write(crystformat.format(*unitcell_vectors[:3]))
        
    def write(self, trajectory):
        for i in range(len(trajectory)):
            self.write_frame(trajectory.frame(i))

    def close(self):
        self.f.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

def gro_open(filename, mode='r', top=None, selection=None):
    """
    Open a Gro file.
    """
    if not mode in ["r", "w"]:
        raise ValueError('Error: mode must be "r" or "w".')
    if mode == 'r':
        return GroFileReader(filename, top=None, selection=selection)
    else:
        return GroFileWriter(filename, top=top)
