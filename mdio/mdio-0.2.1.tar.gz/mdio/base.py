import numpy as np
from  mdio import rmsd_utils
from os.path import splitext
from mendeleev import element as ele
from scipy.spatial.distance import pdist, squareform, cdist
import mdio.dcdio 
import mdio.ncio 
import mdio.xtcio 
import mdio.pdbio 
import mdio.groio
import mdio.rstio
import mdio.mdcrdio
import mdio.mdioio
import mdio.mdtio
import mdio.openmmio
from mdio.utilities import la2v, v2la, parse_selection, Imager

class Frame(object):
    """
    A frame of trajectory data.
    
    """
    def __init__(self, xyz, topology=None, box=None, time=0.0, precision=1000, timestep = 1.0, units='nanometers'):
        if units == 'nanometers':
            self.units = 1.0
        elif units == 'angstroms':
            self.units = 0.1

        xyz = np.array(xyz, dtype=np.float32) * self.units
        self.topology = topology
        if len(xyz.shape) != 2:
            raise TypeError('Error - crds must be a [N,3] array.')
        if xyz.shape[1] != 3:
            raise TypeError('Error - crds must be a [N,3] array.')
        self.n_atoms = xyz.shape[0]
        self.xyz = xyz
        if box is not None:
            box = np.array(box, dtype=np.float32) * self.units
            if box.min() == 0.0 and box.max() == 0.0:
                box = None
            elif len(box.shape) == 1 and len(box) == 6:
                tbox = np.zeros((3,3), dtype=np.float32)
                tbox[0, 0] = box[0]
                tbox[1, 0] = box[1]
                tbox[1, 1] = box[2]
                tbox[2, 0] = box[3]
                tbox[2, 1] = box[4]
                tbox[2, 2] = box[5]
                box = tbox
            elif box.shape != (3,3):
                raise ValueError('Error - unrecognised box data {}'.format(box))
        self.unitcell_vectors = box
        if self.unitcell_vectors is not None:
            self.unitcell_lengths, self.unitcell_angles = v2la(self.unitcell_vectors)
        else:
            self.unitcell_lengths = None
            self.unitcell_angles = None
        self.time = float(time)
        self.precision = int(precision)
        self.timestep = timestep

    def __str__(self):
        if self.unitcell_vectors is not None:
            return "mdio.Frame with {} atoms and box info.".format(self.n_atoms)
        else:
            return "mdio.Frame with {} atoms.".format(self.n_atoms)

    def select(self, atom_indices):
        """
        Create a new Frame from selected atoms.
        """
        return Frame(self.xyz[atom_indices], self.topology, self.unitcell_vectors, self.time)

    def rmsd_from(self, frame, weights=None):
        """
        The RMSD of this Frame from a reference Frame.
        """
        if isinstance(frame, Trajectory):
            frame = frame[0]
        elif not isinstance(frame, Frame):
            raise TypeError('Error - argument must be a Frame or Trajectory')

        if frame.xyz.shape != self.xyz.shape:
            raise ValueError("Error - reference structure has {} atoms but frame has {} atoms.".format(frame.xyz.shape[0], self.xyz.shape[0]))
        return rmsd_utils.kabsch_rmsd(self.xyz, frame.xyz, weights)

    def fitted_to(self, frame, weights=None):
        """
        Returns a copy of the frame least-squares fitted to the reference.
        """
        if isinstance(frame, Trajectory):
            frame = frame[0]
        elif not isinstance(frame, Frame):
            raise TypeError('Error - argument must be a Frame or Trajectory')

        if frame.xyz.shape != self.xyz.shape:
            raise ValueError("Error - reference structure has {} atoms but frame has {} atoms.".format(frame.xyz.shape[0], self.xyz.shape[0]))

        xyz = rmsd_utils.kabsch_fit(self.xyz, frame.xyz, weights)
        return Frame(xyz, self.topology, None, self.time)

    def packed_around(self, selection=None):
        """
        Pack the coordinates in a frame into the periodic box.
        """
        if self.unitcell_vectors is None:
            print('DEBUG: No PBC info.')
            return self
        im = Imager(self.unitcell_vectors)
        if isinstance(selection, str):
            if self.topology is not None:
                atom_indices = self.topology.select(selection)
            else:
                raise TypeError('Error - frame has no topology to parse selection.')
        elif isinstance(selection, list):
            atom_indices = selection
        elif selection is None:
            atom_indices = selection
        else:
            raise TypeError('Error - selection must be a string or list.')
        xyz = im.pack(self.xyz, atom_indices)
            
        if atom_indices is not None:
            if self.topology is not None:
                topology = self.topology.subset(atom_indices)
            else:
                topology = None
        else:
            topology = self.topology
        return Frame(xyz, topology, self.unitcell_vectors, self.time)

    def make_whole(self, bondlist):
        """
        Image atoms to make molecules whole.
        """
        if self.unitcell_vectors is None:
            return self

        im = Imager(self.unitcell_vectors)
        xyz = self.xyz.copy()
        for bond in bondlist:
            dx = xyz[bond[1]] - xyz[bond[0]]
            dx = im.image(dx)
            xyz[bond[1]] = dx + xyz[bond[0]]

        return Frame(xyz, self.topology, self.unitcell_vectors, self.time)

    def save(self, filename):
        ext = splitext(filename)[1]
        if ext in [".nc", ".ncdf"]:
            opener = mdio.ncio.nc_open
        elif ext in [".dcd"]:
            opener = mdio.dcdio.dcd_open
        elif ext in [".xtc"]:
            opener = mdio.xtcio.xtc_open
        elif ext in [".pdb"]:
            opener = mdio.pdbio.pdb_open
        elif ext in [".gro"]:
            opener = mdio.groio.gro_open
        elif ext in [".rst", ".rst7"]:
            opener = mdio.rstio.rst_open
        elif ext in [".mdcrd"]:
            opener = mdio.mdcrdio.mdcrd_open
        else:
            raise TypeError('Error - unrecognised file extension ({})'.format(ext))
        with opener(filename, "w") as f:
            f.write_frame(self)


# Trajectory-level objects for mdio

class Trajectory(object):
    """
    A series of Frames.
    """
    def __init__(self, data, top=None):
        if isinstance(data, str):
            frames = mdio.load(data).frames()

        elif isinstance(data, Frame):
            frames = [data]
        elif isinstance(data, list):
            if not isinstance(data[0], Frame):
                raise TypeError('Error - argument must be a frame or list of frames.')
            frames = data
        elif isinstance(data, np.ndarray):
            s = data.shape
            if len(s) < 2 or len(s) > 3:
                raise TypeError('Error - argument must be a [natoms, 3] or [nframes, natoms, 3] array')
            if s[-1] != 3:
                raise TypeError('Error - argument must be a [natoms, 3] or [nframes, natoms, 3] array')
            if len(s) == 2:
                data = [data]
            frames = [Frame(x) for x in data] 
        else:
            raise TypeError('Error - unsupported data type ({}) for initialisation.'.format(type(data)))

        self.xyz = np.array([frames[0].xyz])
        self.unitcell_vectors = np.array([frames[0].unitcell_vectors])
        self.time = np.array([frames[0].time])
        if len(frames) > 1:
            self.append(frames[1:])
        if top is not None:
            if isinstance(top, Topology):
                self.topology = top
            else:
                self.topology = Topology(top)
        else:
            self.topology = None
        self.top = self.topology
        self.comm = None

    def __str__(self):
        if self.unitcell_vectors[0] is None:
            return "mdio.Trajectory with {} frames, and {} atoms.".format(len(self.xyz), self.n_atoms)
        else:
            return "mdio.Trajectory with {} frames, {} atoms and box info.".format(len(self.xyz), self.n_atoms)

    def __len__(self):
        """
        Length of the trajectory.
        """
        return len(self.xyz)

    def __getitem__(self, key):
        """
        Returns a sub-Trajectory.
        """
        xyz = self.xyz[key]
        unitcell_vectors = self.unitcell_vectors[key]
        time = self.time[key]
        if isinstance(key, int):
            return Trajectory(Frame(xyz, self.topology, unitcell_vectors, time), top=self.topology)
        else:
            return Trajectory([Frame(xyz[i], self.topology, unitcell_vectors[i], time[i]) for i in range(len(xyz))], top=self.topology)

    def __add__(self, other):
        if not isinstance(other, Trajectory):
            raise NotImplementedError('Error - can only add a Trajectory to a Trajectory.')
        result = Trajectory(self.frames())
        result.append(other.frames())
        return result

    def __iadd__(self, other):
        if not isinstance(other, Trajectory):
            raise NotImplementedError('Error - can only add a Trajectory to a Trajectory.')
        self.append(other.frames())
        return self

    @property
    def n_frames(self):
        return self.xyz.shape[0]

    @property
    def n_atoms(self):
        return self.xyz.shape[1]

    def append(self, data):
        """
        Append exra data to a Trajectory

        Data may be a single Frame or a list of Frames.
.
        """
        if isinstance(data, Frame):
            frames = [data]
        elif isinstance(data, list):
            if all([isinstance(d, Frame) for d in data]):
                frames = data
            else:
                raise TypeError('Error - argument must be a frame or list of frames')
        else:
            raise TypeError('Error - argument must be a frame or list of frames.')
        xyz = []
        unitcell_vectors = []
        time = []
        for frame in frames:
            if frame.xyz.shape != self.xyz[0].shape:
                raise ValueError('Error - all frames must contain the same number of atoms.')
            if (frame.unitcell_vectors is None and self.unitcell_vectors[0] is not None) or (frame.unitcell_vectors is not None and self.unitcell_vectors[0] is None):
                raise ValueError('Error - mixing frames with and without box info.')
            xyz.append(frame.xyz)
            unitcell_vectors.append(frame.unitcell_vectors)
            time.append(frame.time)

        self.xyz = np.vstack((self.xyz, xyz))
        self.time = np.concatenate((self.time, time))
        if self.unitcell_vectors[0] is None:
            self.unitcell_vectors = np.concatenate((self.unitcell_vectors, unitcell_vectors))
        else:
            self.unitcell_vectors = np.vstack((self.unitcell_vectors, unitcell_vectors))

    def frame(self, index):
        """
        Returns one frame from the trajectory.
        """
        return Frame(self.xyz[index], self.topology, self.unitcell_vectors[index], self.time[index])
 
    def frames(self):
        """
        Returns the trajectory as a list of frames.
        """
        return [self.frame(i) for i in range(len(self))]

    def select(self, selection):
        """
        Create a new Trajectory from selected atoms.
        """
        if isinstance(selection, str):
            atom_indices = self.topology.select(selection)
        else:
            try:
                atom_indices = list(selection)
            except:
                raise TypeError('Error: selection must be a string or list.')
        frames = []
        for i in range(len(self.xyz)):
            frames.append(Frame(self.xyz[i][atom_indices], None, self.unitcell_vectors[i], self.time[i]))
        if self.topology is not None:
            top = self.topology.subset(atom_indices)
        else:
            top = None
        return Trajectory(frames, top=top)

    def rmsd_from(self, frame, weights=None):
        """
        The RMSD of each Frame from a reference Frame.
        """
        if isinstance(frame, Trajectory):
            frame = frame.frame(0)
        elif not isinstance(frame, Frame):
            raise TypeError('Error - argument must be a Frame or Trajectory')

        if frame.xyz.shape != self.xyz[0].shape:
            raise ValueError("Error - reference structure has {} atoms but trajectory has {} atoms.".format(frame.xyz.shape[0], self.xyz.shape[0]))
        return [rmsd_utils.kabsch_rmsd(xyz, frame.xyz, weights) for xyz in self.xyz]

    def fitted_to(self, frame, weights=None):
        """
        Returns a copy of the trajectory least-squares fitted to the reference.
        """
        if isinstance(frame, Trajectory):
            frame = frame.frame(0)
        elif not isinstance(frame, Frame):
            raise TypeError('Error - argument must be a Frame or Trajectory')

        if frame.xyz.shape != self.xyz[0].shape:
            raise ValueError("Error - reference structure has {} atoms but trajectory has {} atoms.".format(frame.xyz.shape[0], self.xyz.shape[0]))

        xyz = [rmsd_utils.kabsch_fit(x, frame.xyz, weights) for x in self.xyz]
        frames = []
        for i in range(len(xyz)):
            frames.append(Frame(xyz[i], None, None, self.time[i]))
        return Trajectory(frames, top=self.topology)

    def superpose(self, reference):
        """
        In-place least-squares fit of trajectory to reference coordinates.
        """
        new = self.fitted_to(reference)
        self.xyz = new.xyz
        return self

    def packed_around(self, selection=None):
        """
        Pack the coordinates in a trajectory into the periodic box.

        The centre of geometry of the selected atoms is the focus
        for the imaging; if none are given the box centre is used.
t
        """
        if self.unitcell_vectors[0] is None:
            return self
        if isinstance(selection, str):
            if self.topology is None:
                raise RuntimeError('Error - selection needs a topology')
            else:
                atom_indices = self.topology.select(selection)
        else:
            try:
                atom_indices = list(selection)
            except:
                raise TypeError('Error - selection must be a string or list.')
            
        frames = []
        ucv = self.unitcell_vectors[0]
        im = Imager(ucv)
        for i in range(len(self.xyz)):
            if not np.allclose(self.unitcell_vectors[i], ucv):
                ucv = self.unitcell_vectors[i]
                im = Imager(ucv)

            for bond in self.topology.bonds:
                dx = self.xyz[i, bond[1]] - self.xyz[i, bond[0]]
                dx = im.image(dx)
                self.xyz[i, bond[1]] = dx + self.xyz[i, bond[0]]

            xyz = im.pack(self.xyz[i], atom_indices)
            frames.append(Frame(xyz, None, self.unitcell_vectors[i], self.time[i]))
        return Trajectory(frames, top=self.topology)

    def make_whole(self):
        """
        Returns a copy of the trajectory corrected for PBC artifacts.
        """
        if self.unitcell_vectors is None:
            return self
        if len(self.topology.bonds) == 0:
            self.topology.set_bonds(self.xyz[0], self.unitcell_vectors[0], rscale=1.1)
        frames = []
        for frame in self.frames():
            frames.append(frame.make_whole(self.topology.bonds))
        return Trajectory(frames, top=self.topology)

    def mean_structure(self):
        """
        Returns a Frame with the mean structure.
        """
        xyz = self.xyz.mean(axis=0)
        time = np.array(self.time).mean()
        if self.unitcell_vectors[0] is not None:
            unitcell_vectors = self.unitcell_vectors.mean(axis=0)
        else:
            unitcell_vectors = None
       
        return Frame(xyz, self.topology, unitcell_vectors, time)


    def save(self, filename, **kwargs):
        """
        Save the trajectory to a file.

        The format is deduced from the filename extension.

        """
        ext = splitext(filename)[1]
        if ext in [".nc", ".ncdf"]:
            opener = mdio.ncio.nc_open
        elif ext in [".dcd"]:
            opener = mdio.dcdio.dcd_open
        elif ext in [".xtc"]:
            opener = mdio.xtcio.xtc_open
        elif ext in [".pdb"]:
            opener = mdio.pdbio.pdb_open
        elif ext in [".rst", "rst7"]:
            opener = mdio.rstio.rst_open
        elif ext in [".mdcrd"]:
            opener = mdio.mdcrdio.mdcrd_open
        elif ext in [".gro"]:
            opener = mdio.groio.gro_open
        else:
            raise TypeError('Error - unrecognised file extension ({})'.format(ext))
        with opener(filename, "w", top=self.topology, **kwargs) as f:
            f.write(self)

    def save_pdb(self, filename, use_variants=False):
        """
        Included explicitly for nglviewer compatibility.
        """
        opener = mdio.pdbio.pdb_open
        with opener(filename, "w", top=self.topology, use_variants=use_variants) as f:
            f.write(self)


class Topology(object):

    """
    A basic PDB based topology object from which selections can be turned into lists of atom indices.
    
    """
    def __init__(self, source):
        if isinstance(source, mdio.base.Topology):
            self.atomlist = source.atomlist
        elif isinstance(source, str):
            ttop = mdio.load(source)
            self.atomlist = ttop.topology.atomlist
            if self.atomlist is None:
                raise IOError('Error getting topology from {}.'.format(source))
        elif isinstance(source, list) and isinstance(source[0], dict):
            self.atomlist = source
        else:
            raise ValueError('Error initialising topology with given data type {}.'.format(type(source)))
             
        self.n_atoms = len(self.atomlist)
        self.n_residues = 0
        self.n_chains = 0
        self.bonds = []
        self.residuelist = []
        self.chainlist = []
        rcname = None
        cname = None
        
        for a in self.atomlist:
            reschain = str(a['resSeq']) + '_' + a['chainID']
            chainid = a['chainID']
            if cname != chainid:
                self.n_chains += 1
                cname = chainid
                c = {}
                c['chainID'] = chainid
                c['index'] = self.n_chains - 1
                self.chainlist.append(c)

            if reschain != rcname:
                self.n_residues += 1
                rcname = reschain
                r = {}
                r['index'] = self.n_residues - 1
                r['chainIndx'] = self.n_chains - 1
                r['resSeq'] = a['resSeq']
                r['chainID'] = a['chainID']
                r['resName'] = a['resName']
                r['iCode'] = a['iCode']
                r['variant'] = None
                self.residuelist.append(r)

            a['resIndx'] = self.n_residues - 1
            a['chainIndx'] = self.n_chains - 1

        for i, a in enumerate(self.atomlist):
            a['mass'] = self.atom(i).element.mass
            a['element'] = self.atom(i).element.symbol
        

    def __str__(self):
        return 'mdio.Topology with {} atoms, {} residues, {} chains and {} bonds.'.format(self.n_atoms, self.n_residues, self.n_chains, len(self.bonds))


    def get_bonds(self, pdist, xyz, rscale=1.0, selection=None):
        """
        Find the bonds in the selected atoms.

        The argument pdist is the function used to calculate inter-atom
        distances. This might be scipy.spatial.distance.pdist, but might
        be mdio.utilities.Imager.pdist which handles PBC.

        """
        if selection is None:
            atom_indices = range(self.n_atoms)
        else:
            if isinstance(selection, str):
                atom_indices = self.select(selection)
            else:
                try:
                    atom_indices = list(selection)
                except:
                    raise TypeError('Error - selection must be a string or list.')
        d = pdist(xyz[atom_indices])
        n_atoms = len(atom_indices)
        ri = np.zeros((n_atoms, 1))
        for i in range(n_atoms):
            ri[i, 0] = self.atom(atom_indices[i]).element.radius
        dmax = cdist(-ri, ri, 'cityblock')
        for i in range(n_atoms):
            dmax[i, i] = 0
        dmax = squareform(dmax) * rscale
        dd = np.where(d - dmax < 0, 1, 0).astype(np.int)
        bonds = np.transpose(np.triu(squareform(dd)).nonzero())
        for i, b in enumerate(bonds):
            bonds[i, 0] = atom_indices[bonds[i, 0]]
            bonds[i, 1] = atom_indices[bonds[i, 1]]
        return list(bonds)

    def set_bonds(self, xyz, unitcell_vectors=None, rscale=1.1):
        """
        Set the bonds attribute of the topology.
 
        For speed, the method assumes that bonds within protein 
        (or nucleic) regions may be inter-residue, but bonds within 
        hetero components must be intra-residue.

        The parameter rscale scales the covalent radii values used
        to define threshold distances for bonds. The values from the
        mendeleev package are tight, scaling by about 1.1 usually finds
        all the true bonds in a decent structure, without artifacts.

        """
        if unitcell_vectors is None:
            distfunc = pdist
        else:
            im = Imager(unitcell_vectors)
            distfunc = im.pdist

        protein = self.select('protein or nucleic')
        atom_list = []
        bonds = []
        iat = 0
        last_was_protein = iat in protein
        last_chain_name = self.atomlist[0]['chainID']
        last_resseq = self.atomlist[0]['resSeq']
        atom_list.append(iat)
        for iat in range(1, self.n_atoms):
            this_is_protein = iat in protein
            this_chain_name = self.atomlist[iat]['chainID']
            this_resseq = self.atomlist[iat]['resSeq']
            if last_was_protein and this_is_protein:
                process_bonds = last_chain_name != this_chain_name
            elif last_was_protein and (not this_is_protein):
                process_bonds = True
            elif (not last_was_protein) and (not this_is_protein):
                process_bonds = last_resseq != this_resseq
            elif (not last_was_protein) and this_is_protein:
                process_bonds = True
            if not process_bonds:
                atom_list.append(iat)    
            else:
                new_bonds = self.get_bonds(distfunc, xyz, rscale=rscale, selection=atom_list)
                bonds += new_bonds
                atom_list = [iat]
            last_was_protein = this_is_protein
            last_chain_name = this_chain_name
            last_resseq = this_resseq
        if len(atom_list) > 0:
            bonds += self.get_bonds(distfunc, xyz,  rscale=rscale, selection=atom_list)
        self.bonds = bonds

    def atom(self, index):
        return Atom(index, self)

    @property
    def atoms(self):
        indx = 0
        while indx < self.n_atoms:
            yield Atom(indx, self)
            indx += 1

    def residue(self, index):
        return Residue(index, self)

    @property
    def residues(self):
        resindx = 0
        while resindx < self.n_residues:
            yield Residue(resindx, self)
            resindx += 1

    def chain(self, index):
        return Chain(index, self)

    @property
    def chains(self):
        chainindx = 0
        while chainindx < self.n_chains:
            yield Chain(chainindx, self)
            chainindx += 1

    def select(self, expression):
        atom_indices = []
        selection_expression = parse_selection(expression)
        for atom in self.atoms:
            if eval(selection_expression):
                atom_indices.append(atom.index)
        return atom_indices

    def subset(self, atom_indices):
        alist = [a for a in self.atomlist if a['index'] in atom_indices]
        return Topology(alist)

    def set_residue_variants(self, variants_list):
        if len(variants_list) != self.n_residues:
            raise ValueError('Error - variants list must have {} elements.'.format(self.n_residues))
        for i, v in enumerate(variants_list):
            self.residue(i).variant = v

    @classmethod
    def from_dataframe(cls, atoms, bonds=None):
        if len(atoms) == 0:
            raise ValueError('Error - no atoms.')
        atomlist = atoms.to_dict(orient='records')
        return mdio.base.Topology(atomlist)
    
class Element(object):
    element_masses = {}
    element_radii = {}

    def __init__(self, symbol='X', mass=1.0, radius=1.0):
        self.symbol = symbol
        self.mass = mass
        self.radius = radius

    @classmethod
    def from_symbol(self, symbol):
        if not symbol in self.element_masses:
            try:
                e = ele(symbol.strip())
            except ValueError:
                e = ele('C')
            self.element_masses[symbol] = e.atomic_weight
            self.element_radii[symbol] = e.covalent_radius * 0.001 # to nm
        return Element(symbol, self.element_masses[symbol], self.element_radii[symbol])
            
class Atom(object):
    def __init__(self, index, topology):
        self.index = index
        self.topology = topology
        resindx = self.topology.atomlist[index]['resIndx']
        self.residue = self.topology.residue(resindx)
        chainindx = self.topology.atomlist[index]['chainIndx']
        self.chain = self.topology.chain(chainindx)
        self.altloc = self.topology.atomlist[index]['altLoc']
        
    @property
    def serial(self):
        return self.topology.atomlist[self.index]['serial']

    @serial.setter
    def serial(self, value):
        self.topology.atomlist[self.index]['serial'] = value

    @property
    def name(self):
        return self.topology.atomlist[self.index]['name']

    @name.setter
    def name(self, value):
        self.topology.atomlist[self.index]['name'] = value

    @property
    def occupancy(self):
        return self.topology.atomlist[self.index]['occupancy']

    @occupancy.setter
    def occupancy(self, value):
        self.topology.atomlist[self.index]['occupancy'] = value

    @property
    def tempfactor(self):
        return self.topology.atomlist[self.index]['tempFactor']

    @tempfactor.setter
    def tempfactor(self, value):
        self.topology.atomlist[self.index]['tempFactor'] = value

    @property
    def element(self):
        return Element.from_symbol(self.topology.atomlist[self.index]['element'])

    @element.setter
    def element(self, value):
        self.topology.atomlist[self.index]['element'] = value.rjust(2)
    
    @property
    def charge(self):
        return self.topology.atomlist[self.index]['charge']

    @charge.setter
    def charge(self, value):
        self.topology.atomlist[self.index]['charge'] = value


            
class Residue(object):
    def __init__(self, resindx, topology):
        self.resindx = resindx
        self.topology = topology
        self.name = self.topology.residuelist[resindx]['resName']
        chainindx = self.topology.residuelist[resindx]['chainIndx']
        self.chain = self.topology.chain(chainindx)
        self.icode = self.topology.residuelist[resindx]['iCode']

    @property
    def variant(self):
        return self.topology.residuelist[self.resindx]['variant']

    @variant.setter
    def variant(self, value):
        self.topology.residuelist[self.resindx]['variant'] = value

    @property
    def resSeq(self):
        return self.topology.residuelist[self.resindx]['resSeq']

    @resSeq.setter
    def resSeq(self, value):
        self.topology.residuelist[self.resindx]['resSeq'] = value
    
    @property
    def name(self):
        return self.topology.residuelist[self.resindx]['resName']

    @name.setter
    def name(self, value):
        self.topology.residuelist[self.resindx]['resName'] = value
    
    @property
    def atoms(self):
        indx = 0
        while indx < self.topology.n_atoms:
            if self.topology.atomlist[indx]['resIndx'] == self.resindx:
                yield Atom(indx, self.topology)
                indx += 1
            else:
                indx += 1

class Chain(object):
    def __init__(self, chainindx, topology):
        self.index = chainindx
        self.topology = topology

    @property
    def chainid(self):
        return self.topology.chainlist[self.index]['chainID']

    @chainid.setter
    def chainid(self, value):
        self.topology.chainlist[self.index]['chainID'] = value

    @property
    def residues(self):
        resindx = 0
        while resindx < self.topology.n_residues:
            if self.topology.residuelist[resindx]['chainID'] == self.chainid:
                yield Residue(resindx, self.topology)
                resindx += 1
            else:
                resindx += 1

def mpi_load(filenames, top=None, selection=None, comm=None):
    """
    MPI-powered file loader
    """
    if comm is None or isinstance(filenames, str):
        traj = load(filenames, top=top, selection=selection)
        traj.comm = comm
        return traj
    else:
        size = comm.Get_size()
        rank = comm.Get_rank()
    if size == 1:
        return load(filenames, top=top, selection=selection)
    nfiles = len(filenames)
    offsets = np.rint(np.linspace(0, nfiles, size, endpoint=False)).astype(np.int)
    offsets = np.append(offsets, [nfiles])

    i = offsets[rank]
    j = offsets[rank + 1]
    if j > i:
        t = mdio.load(filenames[i:j], top, selection=selection)
    else:
        t = mdio.load_frame(filenames[0], 0, top=top, selection=selection)
        t.xyz = t.xyz[0:0]
        t.time = t.time[0:0]
        if t.unitcell_vectors is not None:
            t.unitcell_vectors = t.unitcell_vectors[0:0]

    sendcounts = np.array(comm.gather(t.n_frames, root=0))
    sendcounts = comm.bcast(sendcounts, root=0)

    n_atoms = t.n_atoms
    tcounts = sendcounts
    xcounts = sendcounts * n_atoms * 3
    bcounts = sendcounts * 9
    tot_frames = sendcounts.sum()
    has_box = t.unitcell_vectors is not None

    xyz = np.empty((tot_frames, n_atoms, 3), dtype=t.xyz.dtype)
    time = np.empty(tot_frames, dtype=t.time.dtype)
    if has_box:
        unitcell_vectors = np.empty((tot_frames, 3, 3), dtype=t.unitcell_vectors.dtype)
    else:
        unitcell_vectors = None

    comm.Gatherv(t.xyz, (xyz, xcounts), root=0)
    comm.Gatherv(t.time, (time, tcounts), root=0)
    comm.Bcast(xyz, root=0)
    comm.Bcast(time, root=0)
    
    if has_box:
        comm.Gatherv(t.unitcell_vectors, (unitcell_vectors, bcounts),  root=0)
        comm.Bcast(unitcell_vectors, root=0)

    t_all = mdio.Trajectory(xyz, t.topology) 
    t_all.time = time
    t_all.unitcell_vectors = unitcell_vectors
    t_all.comm = comm
    return t_all

def slice_parse(filename):
    """
    Split a filename into real name and possible [start:stop:step] components
    """
    def int_or_none(c):
        try:
            result = int(c)
        except:
            result = None
        return result

    if not isinstance(filename, str):
        return filename, None

    if '[' in filename:
        if not ']' in filename:
            raise ValueError('Error in filename {}.'.format(filename))
        i = filename.find('[')
        j = filename.find(']')
        indices = filename[i+1:j]
        filename = filename[:i]
        key = slice(*[int_or_none(c) for c in indices.split(':')])
    else:
        key = None
    return filename, key

def get_opener(filename, top=None):
    """
    Returns an opener for filename.
    """
    openers = [mdio.ncio.nc_open, 
               mdio.dcdio.dcd_open, 
               mdio.xtcio.xtc_open, 
               mdio.groio.gro_open, 
               mdio.rstio.rst_open, 
               mdio.mdtio.mdt_open, 
               mdio.mdioio.mdio_open, 
               mdio.openmmio.openmm_open, 
               mdio.pdbio.pdb_open, 
               mdio.mdcrdio.mdcrd_open]
    for opener in openers:
        if opener == mdio.mdcrdio.mdcrd_open:
            tmptop = top
        else:
            tmptop = None
        try:
            with opener(filename, top=tmptop) as f:
                frame = f.read_frame()
            good_opener = opener
            success = True
        except:
            success = False
        if success:
            break
    if not success:
        return None
    else:
        return good_opener

def load(filenames, top=None, selection=None):
    """
    Format-detecting file loader
    """

    tlist = []
    if not isinstance(filenames, list):
        filenames = [filenames,]
    for i, filename in enumerate(filenames):
        filename, key = slice_parse(filename)
        opener = get_opener(filename, top=top)
        if opener is None:
            raise TypeError('Error - {} does not have a recognised file format'.format(filename))
        with opener(filename, top=top, selection=selection) as f:
            if key is None:
                tlist.append(f.read())
            else:
                tlist.append(f.read()[key])
    result = tlist[0]
    for t in tlist[1:]:
        result += t
    return result

def load_frame(filename, index, top=None, selection=None):
    """
    Format-detecting file loader for a single frame.
    """
    opener = get_opener(filename, top=top)
    if opener is None:
        raise TypeError('Error - {} does not have a recognised file format'.format(filename))
    i = 0
    with opener(filename, top=top, selection=selection) as f:
        while i <= index:
            frame = f.read_frame()
            i += 1
    return Trajectory(frame, top=top)

def mdopen(filename, mode="r", top=None, selection=None):
    """
    Format-agnostic open routines.
    """
    if not mode in ["r", "w"]:
        raise ValueError('Error - mode must be "r" or "w"')

    if mode == "r":
        f = open(filename, 'rb')
        f.close()
        if top is not None:
            f = open(top, 'rb')
            f.close()
        opener = get_opener(filename, top=top)
        if opener is None:
            raise TypeError('Error - {} does not have a recognised file format'.format(filename))
        return opener(filename, top=top, selection=selection)

    else:
        ext = splitext(filename)[1]
        if ext in [".nc", ".ncdf"]:
            opener = mdio.ncio.nc_open
        elif ext in [".dcd"]:
            opener = mdio.dcdio.dcd_open
        elif ext in [".xtc"]:
            opener = mdio.xtcio.xtc_open
        elif ext in [".pdb"]:
            opener = mdio.pdbio.pdb_open
        elif ext in [".gro"]:
            opener = mdio.groio.gro_open
        elif ext in [".rst", ".rst7"]:
            opener = mdio.rstio.rst_open
        elif ext in [".mdcrd"]:
            opener = mdio.mdcrdio.mdcrd_open
        else:
            raise TypeError('Error - unrecognised file extension ({})'.format(ext))
        return opener(filename, "w", top=top)

def get_indices(pdbfile, selection):
    top = Topology(pdbfile)
    return top.select(selection)

def rmsd(traj1, traj2):
    return traj1.rmsd_from(traj2)

