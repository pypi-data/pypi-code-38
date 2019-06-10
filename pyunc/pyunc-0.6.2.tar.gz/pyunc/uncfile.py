from __future__ import print_function
import copy
import os
import struct
import sys
import numpy as np
from .header import UNCHeader

MAXMIN = 0
HISTO = 1
TITLE = 2
PIXEL_FORMAT = 3
DIMC = 4
DIMV = 5
PIXELS = 6
INFO = 7
VERSION = 8

SIZES = {
    'title': 81,
    'validmaxmin': 4,
    'maxmin': 8,
    'validhistogram': 4,
    'histogram': 4096,
    'pixelformat': 4,
    'dimc': 4,
    'dimv': 40,
}

PIXEL_FMTS = {
    0o0010: 'GREY',
    0o0020: 'COLOR',
    0o0040: 'COLORPACKED',
    0o0200: 'USERPACKED',
    0o0001: 'BYTE',
    0o0002: 'SHORT',
    0o0003: 'LONG',
    0o0004: 'REAL',
    0o0005: 'COMPLEX'
}


class UNCFile(object):
    """Represents a UNC format image.

    Args:
        f (file): an UNC file opened in read mode
    """

    @classmethod
    def from_file(cls, f):
        uf = cls()
        uf._read_addresses(f)
        uf._read_title(f)
        uf._read_maxmin(f)
        uf._read_histogram(f)
        uf._read_pixel_format(f)
        uf._read_dimc(f)
        uf._read_dimv(f)
        uf._calculate_pixel_count()
        uf._read_info(f)
        uf._read_pixels(f)
        return uf

    @classmethod
    def from_path(cls, path):
        """Open an UNC file at the given path.

        Args:
            path (str): The filename to open
        """
        with open(path, 'rb') as f:
            instance = cls.from_file(f)
        return instance

    def _read_addresses(self, f):
        f.seek(0, os.SEEK_SET)
        self.addresses = struct.unpack('>9i', f.read(36))

    def _read_title(self, f):
        f.seek(self.addresses[TITLE], os.SEEK_SET)
        title_field = struct.unpack('>81s', f.read(SIZES['title']))[0].decode('ascii')
        self.title = title_field.split('\0', 1)[0]

    def _read_maxmin(self, f):
        f.seek(self.addresses[MAXMIN], os.SEEK_SET)
        self.valid_maxmin = struct.unpack('>i', f.read(SIZES['validmaxmin']))[0] == 1
        maxmin = struct.unpack('>2i', f.read(SIZES['maxmin']))
        self.min, self.max = maxmin

    def _read_histogram(self, f):
        f.seek(self.addresses[HISTO], os.SEEK_SET)
        self.valid_histogram = struct.unpack('>i', f.read(SIZES['validhistogram']))[0] == 1
        self.histogram = struct.unpack('>1024i', f.read(SIZES['histogram']))

    def _read_pixel_format(self, f):
        f.seek(self.addresses[PIXEL_FORMAT], os.SEEK_SET)
        self.pixel_format = struct.unpack('>i', f.read(SIZES['pixelformat']))[0]

    def _read_dimc(self, f):
        f.seek(self.addresses[DIMC], os.SEEK_SET)
        self.dimc = struct.unpack('>i', f.read(SIZES['dimc']))[0]

    def _read_dimv(self, f):
        f.seek(self.addresses[DIMV], os.SEEK_SET)
        self.dimv = struct.unpack('>10i', f.read(SIZES['dimv']))

    def _calculate_pixel_count(self):
        pixel_count = 1
        for i in range(self.dimc):
            pixel_count *= self.dimv[i]
        self.pixel_count = pixel_count

    def _read_info(self, f):
        f.seek(0, os.SEEK_END)
        cnt = f.tell()
        info_len = cnt - self.addresses[INFO]
        f.seek(self.addresses[INFO], os.SEEK_SET)
        info_field = f.read(info_len).decode('ascii')
        self.info = [i for i in info_field.split('\0') if i != '']
        self.header = UNCHeader(self.info[0], self.info[1:self.dimv[0] + 1])

    def _read_pixels(self, f):
        dtypes = {
            0o0001: np.dtype('>B'),
            0o0002: np.dtype('>i2'),
            0o0003: np.dtype('>i4'),
            0o0010: np.dtype('>i2')
        }
        if self.pixel_format not in dtypes:
            print(
                'Unable to read pixels, can only handle uint8, int16 and int32 formats.',
                file=sys.stderr
            )
            self.pixels = None
            return
        f.seek(self.addresses[PIXELS], os.SEEK_SET)
        dtype = dtypes[self.pixel_format]
        lin_pixels = np.fromfile(f, dtype=np.dtype(dtype), count=self.pixel_count)
        self.pixels = np.reshape(lin_pixels, self.dimv[0:self.dimc])

    @property
    def num_echoes(self):
        return len(set([s.dicom.get('Echo Number', 0) for s in self.header.slices]))

    @property
    def echo_times(self):
        all_times = set([s.echo_time for s in self.header.slices])
        return sorted(list(all_times))

    def split_echoes(self):
        slices_per_echo = int(self.pixels.shape[0] / self.num_echoes)
        split_pixels = np.ndarray((
            self.num_echoes,
            slices_per_echo,
            self.pixels.shape[1],
            self.pixels.shape[2]
        ))
        for i in range(self.num_echoes):
            start_slice = slices_per_echo * i
            end_slice = (slices_per_echo * i) + slices_per_echo
            split_pixels[i, :, :, :] = self.pixels[start_slice:end_slice, :, :]
        split_uncs = []
        for n in range(self.num_echoes):
            uf = UNCFile()
            uf.header = copy.copy(self.header)
            uf.dimc = self.dimc
            uf.dimv = self.dimv
            uf.header.slices = [
                copy.deepcopy(s) for s in self.header.slices if s.echo_time == self.echo_times[n]
            ]
            uf.pixels = split_pixels[n, :, :, :]
            split_uncs.append(uf)
        return split_uncs

    def split_volumes(self, n_vols):
        slices_per_vol = int(self.pixels.shape[0] / n_vols)
        split_pixels = np.ndarray((
            n_vols,
            slices_per_vol,
            self.pixels.shape[1],
            self.pixels.shape[2]
        ))
        for i in range(n_vols):
            start_slice = slices_per_vol * i
            end_slice = (slices_per_vol * i) + slices_per_vol
            split_pixels[i, :, :, :] = self.pixels[start_slice:end_slice, :, :]
        split_uncs = []
        for n in range(n_vols):
            uf = UNCFile()
            uf.header = copy.copy(self.header)
            uf.dimc = self.dimc
            uf.dimv = self.dimv
            uf.header.slices = [copy.deepcopy(s) for s in self.header.slices[n::n_vols]]
            uf.pixels = split_pixels[n, :, :, :]
            split_uncs.append(uf)
        return split_uncs
