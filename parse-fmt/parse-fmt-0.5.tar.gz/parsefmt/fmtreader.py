# Python 2-to-3 compatibility code
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import os
import numpy as np


class FMTError(Exception):
    pass


class FMTReader(object):

    def __init__(self, filename):
        """
        Parse a given _fmt file and store its contents in this reader.

        | Args:
        |   filename (str): name of the file to parse

        """

        self._contents = open(filename).readlines()

        self.type = os.path.splitext(filename)[1][1:].replace('_fmt', '')

        # Find begin and end header
        try:
            h0 = [i for i, l in enumerate(self._contents)
                  if 'BEGIN header' in l][0]
        except IndexError:
            raise FMTError('FMT file has no header')

        try:
            h1 = [j for j, l in enumerate(self._contents[h0:])
                  if 'END header' in l][0]+h0
        except IndexError:
            raise FMTError('FMT file header end not found before EOF')

        # Read header
        self._header = self._contents[h0:h1+1]

        self.real_lattice = None
        self.lattice_pars = None

        self.nspins = None
        self.grid = None

        spinre = re.compile('([0-9]+)\s+!\s+nspins')
        gridre = re.compile('([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+'
                            '!\s+fine FFT grid along <a,b,c>')

        for i, l in enumerate(self._header):
            if 'Real Lattice(A)' in l:
                self.real_lattice = []
                self.lattice_pars = []
                for j, ll in enumerate(self._header[i+1:i+4]):
                    x, y, z, _, _, par, _, _, ang = ll.strip().split()
                    self.real_lattice.append([float(f) for f in (x, y, z)])
                    self.lattice_pars.append([float(f) for f in (par, ang)])
                continue
            sm = spinre.search(l)
            if sm is not None:
                self.nspins = int(sm.groups()[0])
                continue
            gm = gridre.search(l)
            if gm is not None:
                self.grid = tuple(int(n) for n in gm.groups())

        try:
            self.legend = self._header[-1].split(':', 2)[1].strip()
        except IndexError:
            self.legend = ''

        # Expunge body
        datare = re.compile('([0-9]+)\s+([0-9]+)\s+([0-9]+)\s+([0-9.-]+)')
        self._raw = np.array([l.strip().split()
                              for l in self._contents[h1+1:]
                              if datare.search(l.strip()) is not None])

        # Check on shape
        if len(self._raw.shape) != 2:
            raise FMTError('Badly formatted data in FMT file')

        # Number of columns?
        self.ncols = self._raw.shape[1]-3
        if self.ncols < 1:
            raise FMTError('Invalid columns in FMT file')

        self._inds = self._raw[:, :3].astype(int)

        # What's the grid shape?
        data_grid = tuple(np.amax(self._inds, axis=0))
        if self.grid is not None and data_grid != self.grid:
            raise FMTError('Invalid grid in FMT file')
        self.grid = data_grid

        if len(self._raw) != (self.grid[0]*self.grid[1]*self.grid[2]):
            raise FMTError('Invalid data block found in FMT file')

        # Now to actually parsing the data
        self.data = np.ones(np.concatenate((self.grid, [self.ncols])))
        self.data[:, :, :, :] = np.nan

        for i, r in enumerate(self._raw):
            try:
                x, y, z = [int(n)-1 for n in r[:3]]
                cols = np.array(r[3:]).astype(float)
            except ValueError:
                raise FMTError('Invalid data entry found in FMT file')
            self.data[x, y, z, :] = cols

        if np.isnan(self.data).any():
            raise FMTError('Incomplete data found in FMT file')

        # Create a fractional and real space grid
        axrng = [np.linspace(0.0, 1.0, g+1)[:-1] for g in self.grid]
        self.fxyz = np.array(np.meshgrid(*axrng, indexing='ij'))
        if self.real_lattice is not None:
            self.xyz = np.tensordot(self.real_lattice, self.fxyz, axes=(0, 0))
        else:
            self.xyz = None


if __name__ == '__main__':

    fr = FMTReader('test/Si2.den_fmt')
    print(fr.type)
    print(fr.real_lattice)
    print(fr.lattice_pars)
    print(fr.nspins)
    print(fr.grid)
    print(fr.legend)
    print(fr.data.shape)
    print(fr.fxyz[:, :3, 0, 0].T)
    print(fr.xyz[:, :3, 0, 0].T)
