import struct
import numpy as np
import  mdio.base
import six
from mdio.utilities import selection_to_indices

def read_record(f, expectedbytes=None, id='data'):
    nbytes = struct.unpack('i', f.read(4))[0]
    buf = f.read(nbytes)
    check = struct.unpack('i', f.read(4))[0]
    if check != nbytes:
        raise ValueError('Error - malformed record in DCD file.')
    if expectedbytes is not None:
        if nbytes != expectedbytes:
            raise IOError('Error reading {} from DCD file.'.format(id))
    return buf

def write_record(f, buf):
    if six.PY2:
        buf = str(buf)
    nbytes = len(buf)
    f.write(struct.pack('i', nbytes))
    f.write(struct.pack('{}s'.format(nbytes), buf))
    f.write(struct.pack('i', nbytes))

class DCDHeader(object):
    """
    The header block for a DCD file.
    """
    def __init__(self, istart=1, nsavec=0, deltat=1.0, version=24, extra=0):
        self.istart = istart
        self.nsavec = nsavec
        self.deltat = deltat
        self.version = version
        self.nsets = 0
        self.extra = extra


def read_dcd_header(f):
    f.seek(0)
    buf = read_record(f, 84, 'header')
    magic = struct.unpack('4s', buf[:4])[0]
    if magic.decode('utf-8') != 'CORD':
        raise IOError('Error - this does not seem to be a DCD format file ({}).'.format(magic))
    header = DCDHeader()
    header.version = struct.unpack('i', buf[80:])[0]
    header.extra = struct.unpack('i', buf[44:48])[0]
    header.nsets, header.istart, header.nsavec = struct.unpack('3i', buf[8:20])
    header.deltat = struct.unpack('f', buf[40:44])[0]
    return header

def write_dcd_header(f, header):
    f.seek(0)
    buf = bytearray(84)
    if six.PY3:
        buf[:4] = struct.pack('4s', b'CORD')
    else:
        buf[:4] = struct.pack('4s', 'CORD')
    buf[8:20] = struct.pack('3i', header.nsets, header.istart, header.nsavec)
    buf[40:48] = struct.pack('fi', header.deltat, header.extra)
    buf[80:] = struct.pack('i', header.version)
    write_record(f, buf)
    
def update_dcd_header(f, nsavec, deltat=None):
    here = f.tell()
    f.seek(20)
    f.write(struct.pack('i', nsavec))
    if deltat is not None:
        f.seek(44)
        f.write(struct.pack('f', deltat))
    f.seek(here)

def read_dcd_titles(f):
    buf = read_record(f)
    ntitle = struct.unpack('i', buf[:4])[0]
    if (len(buf) - 4) // 80 != ntitle:
        raise IOError('Error - cannot read title info from DCD file.')
    titles = []
    for i in range(ntitle):
        offset = 4 + (80 * i)
        titles.append(struct.unpack('80s', buf[offset:offset+80])[0])
    return titles

def write_dcd_titles(f, titles):
    ntitles = len(titles)
    buf = bytearray(4 + 80 * ntitles)
    buf[:4] = struct.pack('i', ntitles)
    for i in range(ntitles):
        offset = 4 + (80 * i)
        title = titles[i]
        lt = len(title)
        lt = min(lt, 80)
        if isinstance(title, str):
            if six.PY3:
                title = bytes(title[:lt], 'utf-8')
            else:
                title = title[:lt]
        
        buf[offset:offset+lt] = struct.pack('{}s'.format(lt), title)
    write_record(f, buf)

def read_dcd_natoms(f):
    buf = read_record(f, 4, 'natoms')
    natoms = struct.unpack('i', buf)[0]
    return natoms

def write_dcd_natoms(f, natoms):
    buf = struct.pack('i', natoms)
    write_record(f, buf)
    
def read_dcd_unit_cell(f):
    buf = read_record(f, 48, 'box data')
    unit_cell_info = struct.unpack('6d', buf)
    return unit_cell_info

def write_dcd_unit_cell(f, unit_cell_data):
    if len(unit_cell_data) != 6:
        raise IOError('Error - must be 6 values in unit cell data list.')
    buf = struct.pack('6d', *unit_cell_data)
    write_record(f, buf)

def read_dcd_coordinates(f, natoms):
    buf = read_record(f, natoms * 4, 'x-coordinates')
    x = struct.unpack('{}f'.format(natoms), buf)
    buf = read_record(f, natoms * 4, 'y-coordinates')
    y = struct.unpack('{}f'.format(natoms), buf)
    buf = read_record(f, natoms * 4, 'z-coordinates')
    z = struct.unpack('{}f'.format(natoms), buf)
    return [list(c) for c in zip(x,y,z)]

def write_dcd_coordinates(f, crds):
    x = [c[0] for c in crds]
    natoms = len(x)
    xbuf = struct.pack('{}f'.format(natoms), *x)
    write_record(f, xbuf)
    y = [c[1] for c in crds]
    write_record(f, struct.pack('{}f'.format(natoms), *y))
    z = [c[2] for c in crds]
    write_record(f, struct.pack('{}f'.format(natoms), *z))

class DCDFileReader(object):
    def __init__(self, f, top=None, selection=None):
        self.f  = f
        if top is not None:
            self.top = mdio.base.Topology(top)
        else:
            self.top = top
        self.atom_indices = selection_to_indices(selection, self.top)
        if self.atom_indices is not None:
            if self.top is not None:
                self.top = self.top.subset(self.atom_indices)

        self.header = read_dcd_header(f)
        self.titles = read_dcd_titles(f)
        self.natoms = read_dcd_natoms(f)
        self.hasbox = self.header.extra == 1
        self.framecount = 0
        self.nframes = self.header.nsavec
        
    def __del__(self):
        try:
            self.f.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
    
    def close(self):
        self.f.close()
        
    def read_frame(self):
        if self.hasbox:
            try:
               box = read_dcd_unit_cell(self.f)
            except:
               return None
        else:
            box = None
        try:
            crds = np.array(read_dcd_coordinates(self.f, self.natoms))
        except:
            return None
        if self.atom_indices is not None:
            crds = crds[self.atom_indices]
        self.framecount += 1
        timestep = self.header.istart + self.framecount - 1
        time = timestep * self.header.deltat
        frame = mdio.base.Frame(crds, self.top, box, time=time, timestep=timestep, units='angstroms')
        return frame

    def read(self):
        frames = []
        frame = self.read_frame()
        while frame is not None:
            frames.append(frame)
            frame = self.read_frame()
        return mdio.base.Trajectory(frames, top=self.top)
        
class DCDFileWriter(object):
    def __init__(self, f, titles=['Created by DCDFileWriter'], top=None):
        self.f = f
        self.header = None
        self.titles = titles
        self.natoms = None
        self.hasbox = None
        self.framecount = 0
        self.deltat = None
        
    def __del__(self):
        try:
            self.close()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
        
    def close(self):
        if self.header is not None:
            if self.deltat < 0:
                self.deltat = 1.0
            update_dcd_header(self.f, self.framecount, self.deltat)
        self.f.close()
        
    def write_frame(self, frame):
        scalefactor = 10.0
        if self.natoms is None:
            self.natoms = frame.n_atoms
            self.hasbox = frame.unitcell_vectors is not None
        elif self.natoms != frame.n_atoms:
            raise IOError('Error - expected {} atoms in frame, found {}.'.format(self.natoms, frame.n_atoms))
        
        if self.hasbox and (frame.unitcell_vectors is None):
            raise IOError('Error - frame is missing box data.')
        if not self.hasbox and (frame.unitcell_vectors is not None):
            raise IOError('Error - frame has unexpected box data.')
            
        if self.header is None:
            self.header = DCDHeader()
            if self.hasbox:
                self.header.extra = 1
            else:
                self.header.extra = 0
            write_dcd_header(self.f, self.header)
            write_dcd_titles(self.f, self.titles)
            write_dcd_natoms(self.f, self.natoms)
        if self.deltat is None:
            self.deltat = -frame.time
        elif self.deltat < 0:
            self.deltat += frame.time
        if self.hasbox:
            box = frame.unitcell_vectors * scalefactor
            tbox = [box[0,0]]
            tbox.append(box[1,0])
            tbox.append(box[1,1])
            tbox.append(box[2,0])
            tbox.append(box[2,1])
            tbox.append(box[2,2])
            write_dcd_unit_cell(self.f, tbox)
        crds = frame.xyz * scalefactor
        write_dcd_coordinates(self.f, crds)
        self.framecount += 1

    def write(self, trajectory):
        """
        Write a list of frames to a dcd file.
        """
        if isinstance(trajectory, np.ndarray):
            trajectory = mdio.base.Trajectory(trajectory)
        for i in range(len(trajectory)):
            self.write_frame(trajectory.frame(i))

def dcd_open(filename, mode='r', top=None, selection=None):
    if not mode in ['r', 'w']:
        raise ValueError('Error - mode must be "r" or "w".')
    if mode == 'r':
        f = open(filename, 'rb')
        filehandler = DCDFileReader(f, top=top, selection=selection)
    elif mode == 'w':
        f = open(filename, 'wb')
        filehandler = DCDFileWriter(f)
    return filehandler
