from netCDF4 import Dataset
import numpy as np
import mdio.base 
from mdio.utilities import la2v, v2la, selection_to_indices

class NCFileReader(object):
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

        self.root = Dataset(filename, 'r')
        if self.root.Conventions != "AMBER":
            raise TypeError("Error - this does not appear" 
                             " to be an Amber netcdf file.")
        self.coordinates = self.root['/coordinates']
        self.time = self.root['/time']
        self.index = -1
        self.nframes = len(self.coordinates)
        self.periodic = 'cell_spatial' in self.root.dimensions
        if self.periodic:
            self.cell_lengths = self.root['/cell_lengths']
            self.cell_angles = self.root['/cell_angles']
            
    def read_frame(self):
        self.index += 1
        if self.index >= self.nframes:
            return None
        if self.periodic:
            box = la2v(self.cell_lengths[self.index], 
                       self.cell_angles[self.index])
        else:
            box = None
        crds = self.coordinates[self.index]
        if self.atom_indices is not None:
            crds = crds[self.atom_indices]
        frame = mdio.base.Frame(crds, 
                      box=box, 
                      time=self.time[self.index],
                      units='angstroms')
        return frame
    
    def read(self):
        frames = []
        frame = self.read_frame()
        while frame is not None:
            frames.append(frame)
            frame = self.read_frame()
        return mdio.base.Trajectory(frames, top=self.top)

    def close(self):
        self.root.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
        
class NCFileWriter(object):
    def __init__(self, filename, top=None):
        self.filename = filename
        self.index = -1
        self.root = Dataset(filename, 'w', format="NETCDF3_64BIT_OFFSET")
        self.root.set_fill_off()
        
        self.root.Conventions = "AMBER"
        self.root.ConventionVersion = "1.0"
        self.root.program = "mdio"
        self.root.programVersion = "0.0.2"
        self.root.title = "CREATED by mdio.ncio"
        
        self.root.createDimension("frame", None)
        self.root.createDimension("spatial", 3)
        
        self.spatial = self.root.createVariable("spatial", "S1", ("spatial",))
        self.spatial[0] = "x"
        self.spatial[1] = "y"
        self.spatial[2] = "z"

        self.time = self.root.createVariable("time", "f4", ("frame",))
        self.time.units = "picoseconds"
        
        self.periodic = False

    def set_coordinates(self, natoms):
        self.root.createDimension("atom", natoms)
        self.coordinates = self.root.createVariable("coordinates", "f4", 
                                                    ("frame", "atom", "spatial"))
        self.coordinates.units = "angstrom"
        
    def set_periodic(self):
        if 'cell_spatial' in self.root.dimensions:
            return
        self.root.createDimension("cell_spatial", 3)
        self.root.createDimension("cell_angular", 3)
        self.root.createDimension("label", 5)
        
        self.cell_angular = self.root.createVariable("cell_angular", "S1", 
                                                     ("cell_spatial", "label"))
        self.cell_spatial = self.root.createVariable("cell_spatial", "S1", 
                                                     ("cell_spatial",))
                
        self.cell_angular[0] = "alpha"
        self.cell_angular[1] = "beta"
        self.cell_angular[2] = "gamma"

        self.cell_spatial[0] = "a"
        self.cell_spatial[1] = "b"
        self.cell_spatial[2] = "c"

        self.cell_lengths = self.root.createVariable("cell_lengths", "f4", 
                                                     ("frame", "cell_spatial"))
        self.cell_lengths.units = "angstrom"

        self.cell_angles = self.root.createVariable("cell_angles", "f4", 
                                                    ("frame", "cell_angular"))
        self.cell_angles.units = "degree"
        
        self.periodic = True
        
    def write_frame(self, frame):
        scalefactor = 10.0
        self.index += 1
        self.time[self.index] = frame.time
        if self.index == 0:
            self.set_coordinates(frame.n_atoms)
            if frame.unitcell_vectors is not None:
                self.set_periodic()

        self.coordinates[self.index] = frame.xyz * scalefactor
        if frame.unitcell_vectors is None and self.periodic:
            raise ValueError('Error: frame contains no box data.')
        if frame.unitcell_vectors is not None and not self.periodic:
            raise ValueError('Error: frame contains unexpected box data.')
        if self.periodic:
            l, a = v2la(frame.unitcell_vectors * scalefactor)
            self.cell_lengths[self.index] = l
            self.cell_angles[self.index] = a
        
    def write(self, trajectory):
        if isinstance(trajectory, np.ndarray):
            trajectory = mdio.base.Trajectory(trajectory)
        for i in range(len(trajectory)):
            self.write_frame(trajectory.frame(i))

    def close(self):
        self.root.close()
        
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

def nc_open(filename, mode='r', top=None, selection=None):
    """
    Open an Amber netcdf trajectory file.
    """
    if not mode in ["r", "w"]:
        raise ValueError('Error: mode must be "r" or "w".')
    if mode == 'r':
        return NCFileReader(filename, top=top, selection=selection)
    else:
        return NCFileWriter(filename)
