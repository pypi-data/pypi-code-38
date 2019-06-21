# Reading and writing Gromacs xtc files
#
# Sections of the code here has been rewritten or adapted from the c code in 
# the Gromacs source file libxdrf.cpp.
#
# Part of the header to that file is reproduced here:
#/*
# * This file is part of the GROMACS molecular simulation package.
# *
# * Copyright (c) 1991-2000, University of Groningen, The Netherlands.
# * Copyright (c) 2001-2004, The GROMACS development team.
# * Copyright (c) 2013,2014,2015,2016,2017,2018, by the GROMACS development team, led by
# * Mark Abraham, David van der Spoel, Berk Hess, and Erik Lindahl,
# * and including many others, as listed in the AUTHORS file in the
# * top-level source directory and at http://www.gromacs.org.
# *
#
import xdrlib
import numpy as np
from mdio.xtcutils import BitByteBuffer, unpack_crds
import mdio.base 
from mdio.utilities import selection_to_indices

def sizeofint(imax):
    """
    Number of bits required to store an integer of max size imax.
    """
    num_of_bits = int(imax).bit_length()
    return num_of_bits

def sizeofints(sizes):
    """
    Number of bits required to pack a list of integers with max values sizes.
    
    """
    p = 1
    for s in sizes:
        p = p * s
    i = int(p).bit_length()
    return i

class MagicStuff(object):
    
    def __init__(self, smallidx=None, mindif=None):
        
        self.magicints = [
        0, 0, 0, 0, 0, 0, 0, 0, 0,
        8, 10, 12, 16, 20, 25, 32, 40, 50, 64,
        80, 101, 128, 161, 203, 256, 322, 406, 512, 645,
        812, 1024, 1290, 1625, 2048, 2580, 3250, 4096, 5060, 6501,
        8192, 10321, 13003, 16384, 20642, 26007, 32768, 41285, 52015, 65536,
        82570, 104031, 131072, 165140, 208063, 262144, 330280, 416127, 524287, 660561,
        832255, 1048576, 1321122, 1664510, 2097152, 2642245, 3329021, 4194304, 5284491, 6658042,
        8388607, 10568983, 13316085, 16777216
        ]

        self.FIRSTIDX = 9
        self.LASTIDX = len(self.magicints)
        
        if smallidx is None and mindif is None:
            raise ValueError('Must provide either smallidx or mindif')
    
        if smallidx is None:
            smallidx = self.FIRSTIDX
            while (smallidx < self.LASTIDX) and (self.magicints[smallidx] < mindif):
                smallidx += 1
    
        self.smallidx = smallidx
        self.maxidx = min(self.LASTIDX, smallidx + 8)
        self.minidx = self.maxidx - 8
        self.larger = self.magicints[self.maxidx] // 2
        self.smaller = self.magicints[max(self.FIRSTIDX, smallidx-1)] // 2
        self.smallnum = self.magicints[smallidx] // 2
        self.sizesmall = np.array([self.magicints[smallidx]] * 3, dtype=np.int)
            
    def update(self, is_smaller):
    
        self.smallidx += is_smaller
        if is_smaller < 0:
            self.smallnum = self.smaller
            if self.smallidx > self.FIRSTIDX:
                self.smaller = self.magicints[self.smallidx - 1] // 2
            else:
                self.smaller = 0
        elif is_smaller > 0:
            self.smaller  = self.smallnum
            self.smallnum = self.magicints[self.smallidx] // 2
        self.sizesmall = np.array([self.magicints[self.smallidx]] * 3, dtype=np.int)

def read_frame(up, atom_indices=None):
    """
    Read a frame of trajectory data out of an xdrlib unpacker buffer.
    
    """
    try:
        magic = up.unpack_int()
    except:
        return None
    if magic != 1995:
        raise ValueError('Error reading frame: magic is {}'.format(magic))
        
    maxatoms = up.unpack_int()
    timestep = up.unpack_int()
    time = up.unpack_float()
    box = np.array(up.unpack_farray(9, up.unpack_float)).reshape((3,3))    
    natoms_check = up.unpack_int()
    
    if natoms_check != maxatoms:
        raise ValueError('Error - frame has {} coordinates instead of {}'.format(natoms_check, natoms))
        
    if atom_indices is None:
        natoms = maxatoms
    else:
        natoms = np.array(atom_indices).max() + 1
    if natoms > maxatoms:
        raise ValueError('Error - frame only contains {} atoms'.format(maxatoms))
    if maxatoms <= 9:
        crds = np.array(up.unpack_farray(maxatoms*3, up.unpack_float)).reshape((maxatoms, 3))
        if atom_indices is not None:
            frame = mdio.base.Frame(crds[atom_indices], box=box, time=time, timestep=timestep)
        else: 
            frame = mdio.base.Frame(crds[:natoms], box=box, time=time, timestep=timestep)
        return frame
                               
    precision = up.unpack_float()
    if precision == 0:
        return None
    inv_precision = 1.0 / precision
    
    minint = np.array(up.unpack_farray(3, up.unpack_int), dtype=np.int)
    maxint = np.array(up.unpack_farray(3, up.unpack_int), dtype=np.int)
    smallidx = up.unpack_int()
    sizes = maxint - minint + 1
    bitsizeint = np.zeros(3, dtype=np.int)
    
    if any(sizes > 0xffffff):
        bitsizeint[0] = sizeofint(sizes[0])
        bitsizeint[1] = sizeofint(sizes[1])
        bitsizeint[2] = sizeofint(sizes[2])
        bitsize = 0
    else:
        bitsize = sizeofints(sizes)
        
    ms = MagicStuff(smallidx=smallidx)
    crds = np.zeros((maxatoms, 3))
    
    cnt = up.unpack_int()

    ba = bytearray(up.unpack_fopaque(cnt))
    bs = BitByteBuffer(ba)
    crds = unpack_crds(bs, ms, maxatoms, natoms, bitsize, bitsizeint, 
                       sizes, minint)
    if atom_indices is None:
        frame = mdio.base.Frame(crds[:natoms] * inv_precision, box=box, time=time, timestep=timestep, precision=precision)
    else:
        frame = mdio.base.Frame(crds[atom_indices] * inv_precision, box=box, time=time, timestep=timestep, precision=precision)
    return frame


def write_frame(p, frame):
    """
    Write a trajectory frame to the xdrlib packer buffer.
    
    """
    INT_MAX = 2147483647
    INT_MIN = -2147483648
    MAXABS = INT_MAX - 2
    MAGIC = 1995
    
    p.pack_int(MAGIC)
    p.pack_int(frame.n_atoms)
    p.pack_int(int(frame.timestep))
    p.pack_float(frame.time)
    if frame.unitcell_vectors is None:
        p.pack_farray(9, np.zeros((9)), p.pack_float)
    else:
        p.pack_farray(9, frame.unitcell_vectors.flatten(), p.pack_float)  
    
    crds = frame.xyz
    size = len(crds)
    p.pack_int(size)
    size3 = size * 3
    if size <= 3:
        p.pack_farray(size3, crds.flatten(), p.pack_float)
        return
    p.pack_float(frame.precision)
    precision = frame.precision
    
    ba = bytearray(size3*8)
    buf = BitByteBuffer(ba)
    prevrun = -1
    
    if abs(crds * precision + 0.5).max() > MAXABS:
        raise ValueError('Error - coordinate values too great for precision={}'.format(precision))
    crdrange = crds.max(axis=0) - crds.min(axis=0)
    if crdrange.max() > MAXABS:
        raise ValueError('Error - coordinate range to great for precision={}'.format(precision))
    
    icrds = np.rint((crds * precision)).astype(np.int)
    minint = icrds.min(axis=0)
    maxint = icrds.max(axis=0)
    sizeint = maxint - minint + 1
    
    for i in range(3):
        p.pack_int(minint[i])

    for i in range(3):
        p.pack_int(maxint[i])

    
    bitsizeint = np.zeros(3, dtype=np.int)
    if any(sizeint > 0xffffff):
        bitsizeint[0] = sizeofint(sizeint[0])
        bitsizeint[1] = sizeofint(sizeint[1])
        bitsizeint[2] = sizeofint(sizeint[2])
        bitsize = 0
    else:
        bitsize = sizeofints(sizeint)


    mindif = np.abs(icrds[1:] - icrds[:-1]).sum(axis=1).min()
    ms = MagicStuff(mindif=mindif)
    p.pack_int(ms.smallidx)
        
    i = 0
    prevcoord = np.zeros(3, dtype=np.int)
    tmpcoord = np.zeros(30, dtype=np.intc)
    tmp = np.zeros(3, dtype=np.int)
    while i < size:
        is_small  = False

        if (ms.smallidx < ms.maxidx) and (i >= 1) and all(np.abs(icrds[i] - prevcoord) < ms.larger):
            is_smaller = 1
        elif ms.smallidx > ms.minidx:
            is_smaller = -1
        else:
            is_smaller = 0
            
        if i + 1 < size:
            if all(np.abs(icrds[i] - icrds[i+1]) < ms.smallnum):
                tmp[:] = icrds[i]
                icrds[i] = icrds[i+1]
                icrds[i+1] = tmp[:]
                is_small = True

        tmpcoord[:3] = icrds[i] - minint
        if bitsize == 0:   
            buf.sendint(bitiszeint[0], tmpcoord[0])
            buf.sendint(bitiszeint[1], tmpcoord[1])
            buf.sendint(bitiszeint[2], tmpcoord[2])
        else:
            buf.sendints(bitsize, sizeint, tmpcoord[:3])
        prevcoord[:] = icrds[i]
        i += 1
        
        run = 0
        if not is_small and is_smaller == -1:
            is_smaller = 0
    
        while is_small and run < 8*3:
            dif = icrds[i] - prevcoord
            if is_smaller == -1 and (dif*dif).sum() >= (ms.smaller * ms.smaller):
                is_smaller = 0

            tmpcoord[run:run+3] = dif + ms.smallnum;
            run += 3
            prevcoord[:] = icrds[i]
            i += 1
            if i >= size:
                is_small = False
            else:
                dif = icrds[i] - prevcoord
                is_small = all(np.abs(dif) < ms.smallnum) 
            
        if run != prevrun or is_smaller != 0:
            prevrun = run           
            buf.sendint(1, 1)
            buf.sendint(5, run+is_smaller+1)
        else:
            buf.sendint(1, 0)
        for k in range(0, run, 3):
            buf.sendints(ms.smallidx, ms.sizesmall, tmpcoord[k:k+3])

        ms.update(is_smaller)
                            
    bout = buf.tobytes()
    p.pack_int(len(bout))
    p.pack_fopaque(len(bout), bout)

def xtc_open(filename, mode='r', top=None, selection=None):
    if not mode in ['r', 'w']:
        raise ValueError('Error: mode must be "r" or "w"')
    if mode == 'r':
        filehandler = XtcfileReader(filename, top=top, selection=selection)
    else:
        filehandler = XtcfileWriter(filename)
    return filehandler

class XtcfileReader(object):
    """
    Reader for xtc format files.

    """
    def __init__(self, filename, top=None, selection=None):
        self.filename = filename
        if top is None:
            self.top = top
        else:
            self.top = mdio.base.Topology(top)

        self.atom_indices = selection_to_indices(selection, self.top)
        if self.atom_indices is not None:
            if self.top is not None:
                self.top = self.top.subset(self.atom_indices)
            
        with open(self.filename, 'rb') as f:
            self.up =  xdrlib.Unpacker(f.read())

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def read_frame(self):
        """
        Returns the next frame from the xtc file.

        """
        return read_frame(self.up, atom_indices=self.atom_indices)

    def read(self):
        """
        Returns all remaining frames from the xtc file as a Trajectory.
        """
        frames = []
        frame = self.read_frame()
        while frame is not None:
            frames.append(frame)
            frame = self.read_frame()
        return mdio.base.Trajectory(frames, top=self.top)

    def close(self):
        """
        Close the file (a no-op in read mode)

        """
        pass


class XtcfileWriter(object):
    """
    Writer for xtc format files.

    """
    def __init__(self, filename, top=None):
        self.filename = filename
        self.f = open(self.filename, 'wb')
        self.p = xdrlib.Packer()
        self.timestep = 0

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
        """
        Close the file 

        """
        self.f.close()

    def write_frame(self, frame):
        """
        Write a frame of data to the file.

        """
        self.p.reset()
        if frame.xyz is None:
            raise ValueError('Error - no coordinates in frame')
        if frame.precision is None:
            frame.precision = 1000
        if frame.unitcell_vectors is None:
            frame.unitcell_vectors = np.zeros((3,3))
        if frame.time is None:
            frame.time = self.time
            self.time += 1.0
        else:
            self.time = frame.time + 1.0
        if frame.timestep is None:
            frame.timestep = self.timestep
            self.timestep += 1
        else:
            self.timestep = frame.timestep + 1
        write_frame(self.p, frame)
        self.f.write(self.p.get_buffer())

    def write(self, trajectory):
        """
        Write a series of frames to an xtc file.
        """
        if isinstance(trajectory, np.ndarray):
            trajectory = mdio.base.Trajectory(trajectory)
        for i in range(len(trajectory)):
            self.write_frame(trajectory.frame(i))

