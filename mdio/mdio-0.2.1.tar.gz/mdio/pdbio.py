import numpy as np
import mdio.base 
from mdio.utilities import la2v, v2la, selection_to_indices

def pdb_atom_parse(line):
    """
    Extract data from an ATOM or HETATM line.
    """
    if '\n' in line:
        line = line[:line.index('\n')]
    line = line.ljust(80)
    result = {}
    result['serial'] = int(line[6:11])
    result['name'] = line[12:16]
    result['altLoc'] = line[16]
    result['resName'] = line[17:20]
    result['chainID'] = line[21]
    result['resSeq'] = int(line[22:26])
    result['iCode'] = line[26]
    result['x'] = float(line[30:38]) * 0.1
    result['y'] = float(line[38:46]) * 0.1
    result['z'] = float(line[46:54]) * 0.1
    try:
        result['occupancy'] = float(line[54:60])
    except:
        result['occupancy'] = 1.0
    try:
        result['tempFactor'] = float(line[60:66])
    except:
        result['tempFactor'] = 0.0
    result['element'] = line[76:78].strip()
    if result['element'] == '':
        result['element'] = result['name'].lstrip(' 0123456789')[0]
    result['charge'] = line[78:80]
    return result
    
class PDBFileReader(object):
    def __init__(self, filename, top=None, selection=None, altloc='A'):
        #print('DEBUG: Reading header')
        self.filename = filename
        self.atom_indices = None
        self.selection = selection
        self.top = None
        self.altloc = altloc
        self.unitcell_vectors = None
        self.index = -1
        self.buffer = ' ' * 80
        self.f = open(filename, 'r')
        while not self.buffer[:6] in ['CRYST1', 'MODEL ', 'ATOM  ','HETATM', 'EOF   ']:
            self.buffer = self.f.readline()
            if self.buffer == "":
                  self.buffer = 'EOF   '
            else:
               self.buffer = self.buffer.ljust(80)
        if self.buffer[:6] == 'CRYST1':
            a = float(self.buffer[6:15]) * 0.1
            b = float(self.buffer[15:24]) * 0.1
            c =float(self.buffer[24:33]) * 0.1
            alpha = float(self.buffer[33:40])
            beta = float(self.buffer[40:47])
            gamma = float(self.buffer[47:54])
            self.unitcell_vectors = la2v((a, b, c), (alpha, beta, gamma))
        while not self.buffer[:6] in ['MODEL ', 'ATOM  ','HETATM', 'EOF   ']:
            self.buffer = self.f.readline()
            if self.buffer == "":
                self.buffer = 'EOF   '
            else:
                self.buffer = self.buffer.ljust(80)
        if self.buffer =='EOF   ':
            raise IOError('Error - this does not seem to be a valid PDB file.')
        #print('DEBUG: header read.')
            
    def read_frame(self):
        #print('DEBUG: reading frame.')
        if self.buffer[:6] == 'EOF   ':
            return None
        while not self.buffer[:6] in ['ATOM  ', 'HETATM', 'EOF   ']:
            self.buffer = self.f.readline()
            if self.buffer == "":
                self.buffer = 'EOF   '
            else:
                self.buffer = self.buffer.ljust(80)
        if self.buffer == 'EOF   ':
            return None

        result = []
        index = -1
        if self.buffer[:6] in ['ATOM  ', 'HETATM']:
            while self.buffer[:6] in ['ATOM  ', 'HETATM', 'TER   ']:
                if self.buffer[:6] in ['ATOM  ', 'HETATM']:
                    index += 1
                    data = pdb_atom_parse(self.buffer)
                    data['index'] = index
                    if self.altloc is None:
                        result.append(data)
                    else:
                        if data['altLoc'] in [self.altloc, ' ']:
                            data['altLoc'] = ' '
                            result.append(data)
                self.buffer = self.f.readline()
                if self.buffer == "":
                    self.buffer = 'EOF   '
                else:
                    self.buffer = self.buffer.ljust(80)
        if self.top is None:
            self.top = mdio.base.Topology(result)
            self.atom_indices = selection_to_indices(self.selection, self.top)
            if self.atom_indices is not None:
                self.top = self.top.subset(self.atom_indices)
        self.index += 1
        crds = np.array([[data['x'], data['y'], data['z']] for data in result])
        if self.atom_indices is not None:
            crds = crds[self.atom_indices]
        frame = mdio.base.Frame(crds, 
                      box=self.unitcell_vectors, 
                      time=self.index,
                      units='nanometers')
        #print('DEBUG: frame read.')

        return frame

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
        
class PDBFileWriter(object):
    def __init__(self, filename, top=None, use_variants=False):
        if top is None:
            raise RuntimeError('Error - cannot write PDB format without a topology.')
        if isinstance(top, mdio.base.Topology):
            self.top = top
        else:
            ttop = mdio.load(top)
            self.top = ttop.topology
        self.filename = filename
        self.index = -1
        self.use_variants = use_variants
        self.f = open(filename, 'w')

    def write_frame(self, frame):
        scalefactor = 10.0
        self.index += 1
        if self.index == 0:
            if frame.unitcell_vectors is not None:
                lengths, angles = v2la(frame.unitcell_vectors * scalefactor)
                crystformat = 'CRYST1{:9.3f}{:9.3f}{:9.3f}{:7.2f}{:7.2f}{:7.2f}\n'
                self.f.write((crystformat.format(lengths[0], lengths[1], lengths[2], angles[0], angles[1], angles[2])))
        modelformat = 'MODEL     {:4d}\n'
        self.f.write(modelformat.format(self.index + 1))
        atomformat = 'ATOM  {:5d} {:4s}{:1s}{:3s} {:1s}{:4d}{:1s}   {:8.3f}{:8.3f}{:8.3f}{:6.2f}{:6.2f}          {:2s}{:2s}\n'
        xyz = frame.xyz * scalefactor
        for i, atom in enumerate(self.top.atoms):
            name = atom.name.strip()
            if len(name) == 1:
                name = ' ' + name + '  '
            elif len(name) == 2:
                name = ' ' + name + ' '
            elif len(name) == 3:
                name = ' '  + name
            else:
                name = name[:4]
            if self.use_variants:
                if atom.residue.variant is not None:
                    resName = atom.residue.variant.strip().ljust(3)[:3]
                else:
                    resName = atom.residue.name.strip().ljust(3)[:3]
            else:
                resName = atom.residue.name.strip().ljust(3)[:3]
            chainID = atom.chain.chainid.strip().ljust(1)[0]
            self.f.write(atomformat.format(atom.serial,
                                           name, 
                                           atom.altloc,
                                           resName,
                                           chainID,
                                           atom.residue.resSeq,
                                           atom.residue.icode,
                                           xyz[i,0],
                                           xyz[i,1],
                                           xyz[i,2],
                                           atom.occupancy,
                                           atom.tempfactor,
                                           atom.element.symbol,
                                           atom.charge,
                                           ))
        self.f.write('ENDMDL\n')
        
    def write(self, trajectory):
        if isinstance(trajectory, np.ndarray):
            trajectory = mdio.base.Trajectory(trajectory)
        for i in range(len(trajectory)):
            self.write_frame(trajectory.frame(i))

    def close(self):
        self.f.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

def pdb_open(filename, mode='r', top=None, selection=None, use_variants=False):
    """
    Open a PDB file.
    """
    if not mode in ["r", "w"]:
        raise ValueError('Error: mode must be "r" or "w".')
    if mode == 'r':
        return PDBFileReader(filename, top=None, selection=selection)
    else:
        return PDBFileWriter(filename, top=top, use_variants=use_variants)
