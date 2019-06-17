# This file is part of h5py, a Python interface to the HDF5 library.
#
# http://www.h5py.org
#
# Copyright 2008-2013 Andrew Collette and contributors
#
# License:  Standard 3-clause BSD; see "license.txt" for full license terms
#           and contributor agreement.

"""
    High-level interface for creating HDF5 virtual datasets
"""

from copy import deepcopy as copy
from collections import namedtuple

import numpy as np

from h5py import h5
from h5py import h5s, h5r
from h5py import version
from h5py._hl.selections import FancySelection, PointSelection, Selection, \
    _expand_ellipsis, _translate_slice, _translate_int


class h5slice(object):

    def __init__(self, start=None, count=None, stride=None, block=None):
        if any(index < 0 for index in [start, count, stride, block]):
            raise ValueError("Indices must be positive")
        if block > stride:
            raise ValueError("Blocks will overlap if block < stride")

        self.start = start
        self.count = count
        self.stride = stride
        self.block = block

    def indices(self, length):
        start = 0 if self.start is None else self.start
        stride = 1 if self.stride is None else self.stride
        block = 1 if self.block is None else self.block
        count = (length - 1) / block if self.count is None else self.count

        end_index = start + block + (count - 1) * (stride - 1) - 1
        if end_index > length - 1:
            raise ValueError(
                "Slice range ({} - {}) extends beyond maximum index ({})".format(
                    start, end_index, length - 1
                ))

        return start, count, stride, block


def _translate_h5slice(exp, length):
    """ Given an h5slice object, return a 4-tuple
        (start, count, stride, block)
        for use with the hyperslab selection routines
    """
    return exp.indices(length)


def _handle_simple(shape, args):
    """ Process a "simple" selection tuple, containing only slices, integers
        or h5slices.
        Return is a 5-tuple with tuples for start, count, step, block plus a
        flag which tells us if the axis is a "scalar" selection (indexed by an
        integer).

        If "args" is shorter than "shape", the remaining axes are fully
        selected.
    """
    start = []
    count = []
    stride = []
    block = []
    scalar = []

    args = _expand_ellipsis(args, len(shape))

    for arg, length in zip(args, shape):
        _scalar = False
        if isinstance(arg, slice):
            _start, _count, _stride = _translate_slice(arg, length)
            _block = 1
        elif isinstance(arg, h5slice):
            _start, _count, _stride, _block = _translate_h5slice(arg, length)
        else:
            try:
                _start, _count, _stride = _translate_int(int(arg), length)
                _block = 1
                _scalar = True
            except TypeError:
                raise TypeError('Illegal index "%s" (must be a slice or number)' % arg)

        start.append(_start)
        count.append(_count)
        stride.append(_stride)
        block.append(_block)
        scalar.append(_scalar)

    return tuple(start), tuple(count), tuple(stride), tuple(block), \
        tuple(scalar)


class SimpleSelection(Selection):

    """ A single "rectangular" (regular) selection composed of only slices
        and integer arguments.  Can participate in broadcasting.
    """

    @property
    def mshape(self):
        """ Shape of current selection """
        return self._mshape

    def __init__(self, shape, *args, **kwds):
        Selection.__init__(self, shape, *args, **kwds)
        rank = len(self.shape)
        self._sel = ((0,)*rank, self.shape, (1,)*rank, (False,)*rank)
        self._mshape = self.shape

    def __getitem__(self, args):

        if not isinstance(args, tuple):
            args = (args,)

        if self.shape == ():
            if len(args) > 0 and args[0] not in (Ellipsis, ()):
                raise TypeError("Invalid index for scalar dataset (only ..., () allowed)")
            self._id.select_all()
            return self

        start, count, stride, block, scalar = _handle_simple(self.shape, args)

        self._id.select_hyperslab(start, count, stride, block)

        self._sel = (start, count, stride, scalar)

        self._mshape = tuple(x for x, y in zip(count, scalar) if not y)

        return self


    def broadcast(self, target_shape):
        """ Return an iterator over target dataspaces for broadcasting.

        Follows the standard NumPy broadcasting rules against the current
        selection shape (self.mshape).
        """
        if self.shape == ():
            if np.product(target_shape) != 1:
                raise TypeError("Can't broadcast %s to scalar" % target_shape)
            self._id.select_all()
            yield self._id
            return

        start, count, step, scalar = self._sel

        rank = len(count)
        target = list(target_shape)

        tshape = []
        for idx in xrange(1,rank+1):
            if len(target) == 0 or scalar[-idx]:     # Skip scalar axes
                tshape.append(1)
            else:
                t = target.pop()
                if t == 1 or count[-idx] == t:
                    tshape.append(t)
                else:
                    raise TypeError("Can't broadcast %s -> %s" % (target_shape, self.mshape))

        if any([n > 1 for n in target]):
            # All dimensions from target_shape should either have been popped
            # to match the selection shape, or be 1.
            raise TypeError("Can't broadcast %s -> %s" % (target_shape, self.mshape))

        tshape.reverse()
        tshape = tuple(tshape)

        chunks = tuple(x//y for x, y in zip(count, tshape))
        nchunks = int(np.product(chunks))

        if nchunks == 1:
            yield self._id
        else:
            sid = self._id.copy()
            sid.select_hyperslab((0,)*rank, tshape, step)
            for idx in xrange(nchunks):
                offset = tuple(x*y*z + s for x, y, z, s in zip(np.unravel_index(idx, chunks), tshape, step, start))
                sid.offset_simple(offset)
                yield sid


def select(shape, args, dsid):
    """ High-level routine to generate a selection from arbitrary arguments
    to __getitem__.  The arguments should be the following:

    shape
        Shape of the "source" dataspace.

    args
        Either a single argument or a tuple of arguments.  See below for
        supported classes of argument.

    dsid
        A h5py.h5d.DatasetID instance representing the source dataset.

    Argument classes:

    Single Selection instance
        Returns the argument.

    numpy.ndarray
        Must be a boolean mask.  Returns a PointSelection instance.

    RegionReference
        Returns a Selection instance.

    Indices, slices, ellipses, h5slice only
        Returns a SimpleSelection instance

    Indices, slices, ellipses, lists or boolean index arrays
        Returns a FancySelection instance.
    """
    if not isinstance(args, tuple):
        args = (args,)

    # "Special" indexing objects
    if len(args) == 1:

        arg = args[0]
        if isinstance(arg, Selection):
            if arg.shape != shape:
                raise TypeError("Mismatched selection shape")
            return arg

        elif isinstance(arg, np.ndarray):
            sel = PointSelection(shape)
            sel[arg]
            return sel

        elif isinstance(arg, h5r.RegionReference):
            sid = h5r.get_region(arg, dsid)
            if shape != sid.shape:
                raise TypeError("Reference shape does not match dataset shape")

            return Selection(shape, spaceid=sid)

    for a in args:
        if not isinstance(a, slice) and not isinstance(a, h5slice) \
                and a is not Ellipsis:
            try:
                int(a)
                if isinstance(a, np.ndarray) and a.shape == (1,):
                    raise Exception()
            except Exception:
                sel = FancySelection(shape)
                sel[args]
                return sel

    sel = SimpleSelection(shape)
    sel[args]
    return sel


class VDSmap(namedtuple('VDSmap', ('vspace', 'file_name',
                                   'dset_name', 'src_space'))):
    '''Defines a region in a virtual dataset mapping to part of a source dataset
    '''


vds_support = False
hdf5_version = version.hdf5_version_tuple[0:3]

if hdf5_version >= h5.get_config().vds_min_hdf5_version:
    vds_support = True


class VirtualSource(object):
    """Source definition for virtual data sets.

    Instantiate this class to represent an entire source dataset, and then
    slice it to indicate which regions should be used in the virtual dataset.

    path_or_dataset
        The path to a file, or an h5py dataset. If a dataset is given,
        the other parameters are ignored, and the relevant values taken from
        the dataset instead.
    name
        The name of the source dataset within the file.
    shape
        A tuple giving the shape of the dataset.
    dtype
        Numpy dtype or string.
    maxshape
        The source dataset is resizable up to this shape. Use None for
        axes you want to be unlimited.
    """
    def __init__(self, path_or_dataset, name=None,
                 shape=None, dtype=None, maxshape=None):
        from h5py._hl.dataset import Dataset
        if isinstance(path_or_dataset, Dataset):
            failed = {k: v
                      for k, v in
                      {'name': name, 'shape': shape,
                       'dtype': dtype, 'maxshape': maxshape}.items()
                      if v is not None}
            if failed:
                raise TypeError("If a Dataset is passed as the first argument "
                                "then no other arguments may be passed.  You "
                                "passed {failed}".format(failed=failed))
            ds = path_or_dataset
            path = ds.file.filename
            name = ds.name
            shape = ds.shape
            dtype = ds.dtype
            maxshape = ds.maxshape
        else:
            path = path_or_dataset
            if name is None:
                raise TypeError("The name parameter is required when "
                                "specifying a source by path")
            if shape is None:
                raise TypeError("The shape parameter is required when "
                                "specifying a source by path")
        self.path = path
        self.name = name
        self.dtype = dtype

        if maxshape is None:
            self.maxshape = shape
        else:
            self.maxshape = tuple([h5s.UNLIMITED if ix is None else ix
                                   for ix in maxshape])
        self.sel = SimpleSelection(shape)

    @property
    def shape(self):
        return self.sel.mshape

    def __getitem__(self, key):
        tmp = copy(self)
        tmp.sel = select(self.shape, key, dsid=None)
        return tmp

class VirtualLayout(object):
    """Object for building a virtual dataset.

    Instantiate this class to define a virtual dataset, assign to slices of it
    (using VirtualSource objects), and then pass it to
    group.create_virtual_dataset() to add the virtual dataset to a file.

    This class does not allow access to the data; the virtual dataset must
    be created in a file before it can be used.

    shape
        A tuple giving the shape of the dataset.
    dtype
        Numpy dtype or string.
    maxshape
        The source dataset is resizable up to this shape. Use None for
        axes you want to be unlimited.
    """
    def __init__(self, shape, dtype=None, maxshape=None):
        self.shape = shape
        self.dtype = dtype
        self.maxshape = maxshape
        self.sources = []

    def __setitem__(self, key, source):
        sel = select(self.shape, key, dsid=None)
        self.sources.append(VDSmap(sel.id,
                                   source.path,
                                   source.name,
                                   source.sel.id))
