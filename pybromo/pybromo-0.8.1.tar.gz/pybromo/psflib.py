#
# PyBroMo - A single molecule diffusion simulator in confocal geometry.
#
# Copyright (C) 2013-2015 Antonino Ingargiola tritemio@gmail.com
#

"""
This module provides classes to compute PSF functions either starting from
an analytical formula (i.e. Gaussian) or by interpolation of a precomputed PSF.

File part of PyBroMo: a single molecule diffusion simulator.
Copyright (C) 2013-2014 Antonino Ingargiola tritemio@gmail.com
"""

import pkg_resources
import os
from scipy.io import loadmat
import scipy.interpolate as SI
import numexpr as NE
import numpy as np
import hashlib
from numpy import exp


def psf_from_pytables(psf_pytables):
    """Load a PSF object (either numeric or gauss) from a pytables array.
    """
    if 'kind' not in psf_pytables.attrs:
        # old files may not have the `kind` attribute, assume NumericPSF
        psf_type = 'numeric'
    else:
        psf_type = psf_pytables.attrs['kind']
    #print(psf_type, type(psf_type), str(psf_type), flush=True)
    loader = {'numeric': NumericPSF, 'gauss': GaussianPSF}
    if psf_type not in loader:
        msg = f'PSF of type `{psf_type}` not supported.'
        raise ValueError(msg)
    return loader[psf_type](psf_pytables=psf_pytables)


class GaussianPSF:
    """This class implements a Gaussian-shaped PSF function."""

    def __init__(self, xc=0, yc=0, zc=0, sx=0.2e-6, sy=0.2e-6, sz=0.8e-6, psf_pytables=None):
        """Create a Gaussian PSF object with given center and sigmas.
        `xc`, `yc`, `zc`: position of the center of the gaussian (m)
        `sx`, `sy`, `sz`: sigmas of the gaussian function (m).
        `psf_pytables`, if not None, it is a pytables array from which
        to load the PSF data. `psf_pytables` overrides the other
        arguments.
        """
        self.kind = 'gauss'
        self.fname = 'gaussian_psf'
        if psf_pytables is not None:
            assert psf_pytables.attrs['kind'] == 'gauss'
            self.rc, self.s = psf_pytables.read().astype(np.float64)
            self.xc, self.yc, self.zc = self.rc
            self.sx, self.sy, self.sz = self.s
        else:
            self.xc, self.yc, self.zc = xc, yc, zc
            self.rc = np.array([xc, yc, zc], dtype=np.float64)
            self.sx, self.sy, self.sz = sx, sy, sz
            self.s = np.array([sx, sy, sz], dtype=np.float64)

    def __repr__(self):
        return f'GaussianPSF( {dict(mean=self.rc, sigma=self.s)} )'

    def eval(self, x, y, z):
        """Evaluate the function in (x, y, z)."""
        xc, yc, zc = self.rc
        sx, sy, sz = self.s

        ## Method1: direct evaluation
        #return exp(-(((x-xc)**2)/(2*sx**2) + ((y-yc)**2)/(2*sy**2) +\
        #        ((z-zc)**2)/(2*sz**2)))

        ## Method2: evaluation using numexpr
        def arg(s):
            return "((%s-%sc)**2)/(2*s%s**2)" % (s, s, s)
        return NE.evaluate("exp(-(%s + %s + %s))" %
                           (arg("x"), arg("y"), arg("z")))

        ## Method3: evaluation with partial function
        #g_arg = lambda t, mu, sig: -((t-mu)**2)/(2*sig**2)
        #return exp(g_arg(x, xc, sx) + g_arg(y, yc, sy) + g_arg(z, zc, sz))

    def eval_xz(self, x, z):
        """Evaluate the function in (x, z) (micro-meters).
        The function is rotationally symmetric around z.
        """
        xc, yc, zc = self.rc
        sx, sy, sz = self.s
        return exp(-(((x-xc)**2)/(2*sx**2) + ((z-zc)**2)/(2*sz**2)))

    def hash(self):
        """Return an hash string computed on the PSF data."""
        return hashlib.md5(repr(self).encode()).hexdigest()

    def to_hdf5(self, file_handle, parent_node='/'):
        """Store the PSF data in `file_handle` (pytables) in `parent_node`.

        The PSF data is stored in an array named `gauss_psf_params` with
        shape 2 x 3. Columns are x, y, z coordinates, rows are mean and
        standard deviation.
        """
        data = np.vstack([self.rc, self.s]).astype(np.float64)
        tarray = file_handle.create_array(
            parent_node, name='gauss_psf_params', obj=data,
            title='Gaussian PSF mean and std. dev.')
        file_handle.set_node_attr(tarray, 'kind', self.kind)
        return tarray


class NumericPSF:
    def __init__(self, fname='xz_realistic_z50_150_160_580nm_n1335_HR2',
                 dir_=None, x_step=0.5 / 8, z_step=0.5 / 8,
                 psf_pytables=None):
        """Create a PSF object for interpolation from numeric data.

        `dir_+fname`: should be a valid path

        If `dir_` is None use the "system" folder where the PSF shipped with
        pybromo are placed.
        """
        self.kind = 'numeric'
        if psf_pytables is not None:
            if 'kind' in psf_pytables.attrs:
                assert psf_pytables.attrs['kind'] == self.kind
            self.psflab_psf_raw = psf_pytables[:]
            for name in ['fname', 'dir_', 'x_step', 'z_step']:
                setattr(self, name, psf_pytables.get_attr(name))
        else:
            self.fname = fname
            if dir_ is None:
                dir_ = pkg_resources.resource_filename('pybromo', 'psf_data')
            self.dir_ = dir_
            self.x_step, self.z_step = x_step, z_step
            self.psflab_psf_raw = load_PSFLab_file('/'.join([dir_, fname]))

        xi, zi, hdata, zm = convert_PSFLab_xz(self.psflab_psf_raw,
                                              x_step=x_step, z_step=z_step,
                                              normalize=True)
        # Interpolating function (inputs in micron)
        self._fun_um = SI.RectBivariateSpline(xi, zi, hdata.T, kx=1, ky=1)

        self.xi, self.zi, self.hdata, self.zm = xi, zi, hdata, zm
        self.x_step, self.z_step = xi[1] - xi[0], zi[1] - zi[0]

    def eval_xz(self, x, z):
        """Evaluate the function in (x, z) (micro-meters).
        The function is rotationally symmetric around z.
        The argument `x` must be >= 0.
        """
        return self._fun_um.ev(x * 1e6, z * 1e6)

    def eval(self, x, y, z):
        """Evaluate the function in (x, y, z).
        The function is rotationally symmetric around z.
        """
        ro = np.sqrt(x**2 + y**2)
        zs, xs = ro.shape
        v = self.eval_xz(ro.ravel(), z.ravel())
        return v.reshape(zs, xs)

    def to_hdf5(self, file_handle, parent_node='/'):
        """Store the PSF data in `file_handle` (pytables) in `parent_node`.

        The raw PSF array name is stored with same name as the original fname.
        Also, the following attributes are set: fname, dir_, x_step, z_step.
        """
        tarray = file_handle.create_array(parent_node, name=self.fname,
                                          obj=self.psflab_psf_raw,
                                          title='PSF x-z slice (PSFLab array)')
        for name in ['fname', 'dir_', 'x_step', 'z_step', 'kind']:
            file_handle.set_node_attr(tarray, name, getattr(self, name))
        return tarray

    def hash(self):
        """Return an hash string computed on the PSF data."""
        hash_list = []
        for key, value in sorted(self.__dict__.items()):
            if not callable(value):
                if isinstance(value, np.ndarray):
                    hash_list.append(value.tostring())
                else:
                    hash_list.append(str(value))
        return hashlib.md5(repr(hash_list).encode()).hexdigest()


def load_PSFLab_file(fname):
    """Load the array `data` in the .mat file `fname`."""
    if os.path.exists(fname) or os.path.exists(fname + '.mat'):
        return loadmat(fname)['data']
    else:
        raise IOError("Can't find PSF file '%s'" % fname)

def convert_PSFLab_xz(data, x_step=0.5, z_step=0.5, normalize=False):
    """Process a 2D array (from PSFLab .mat file) containing a x-z PSF slice.

    The input data is the raw array saved by PSFLab. The returned array has
    the x axis cut in half (only positive x) to take advantage of the
    rotational symmetry around z. Pysical dimensions (`x_step` and `z_step)
    are also assigned.

    If `nomalize` is True the peak is normalized to 1.

    Returns:
    x, z: (1D array) the X and Z axis in pysical units
    hdata: (2D array) the PSF intesity
    izm: (float) the index of PSF max along z (axis 0) for x=0 (axis 1)
    """
    z_len, x_len = data.shape
    hdata = data[:, (x_len - 1) // 2:]
    x = np.arange(hdata.shape[1]) * x_step
    z = np.arange(-(z_len - 1) / 2, (z_len - 1) / 2 + 1) * z_step
    if normalize:
        hdata /= hdata.max()  # normalize to 1 at peak
    return x, z, hdata, hdata[:, 0].argmax()
