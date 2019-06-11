"""Python utilities for Fullwave3D VTR model files

 * Licensed under terms of 3-Clause BSD license (see LICENSE)
 * Copyright (c) 2017 S-Cube, tlin@s-cube.com

"""
from __future__ import print_function
import os.path

__version__ = '0.4.1'


class VTRModel(object):
    """Represents a Fullwav3D VTR model in 1,2, or 3 dimensions
    """
    import numpy

    def __init__(self, file_name=None, read_model=True, use_memmap=False):
        """Initializes a VTR model with an existing vtr file

        To set-up an empty VTR model (to manually fill metadata), call init
        without any arguments.

        :param file_name: file name of VTR file to read
        :type file_name: str
        :param read_model: whether to read the actual model properties,
            defaults to True
        :type read_model: bool, optional
        """
        super(VTRModel, self).__init__()
        # instance variables
        self.file = file_name
        self.use_memmap = use_memmap
        self.num_dimensions = None
        self.num_properties = None
        self.shape = ()
        self.shape_fortran = ()
        self.nx1 = None
        self.nx2 = None
        self.nx3 = None
        self.arrays = []  # list of ND-arrays

        if file_name is not None:
            self._read_from_file()

    def _read_from_file(self, read_model=True):
        if self._file_exists():
            self._parse_metadata()
            if read_model:
                self._parse_model()
        else:
            raise IOError("Given file_name does not point to a valid file")

    def _file_exists(self):
        """Checks if the VTR file_name points to a valid file that exists

        :returns: True if self.file_name is a valid file path and file exists
        :rtype: {bool}
        """
        return os.path.isfile(self.file)

    def _parse_metadata(self):
        """Fills in instance variables based on parsed vtr file,
        except for the actual model values stored in self.arrays
        """

        header = numpy.fromfile(self.file, dtype=numpy.int32, count=10)

        # Get number of attributes
        self.num_properties = header[1]
        if (self.num_properties == 0):  # this could happen if using write_vtr
            self.num_properties = 1

        # Get dimension information
        self.num_dimensions = header[2]  # check for 1D/2D/3D models

        self.nx3 = header[6]  # vtr files always has nx3 (fastest, nz) dimension
        if (self.num_dimensions == 3):
            self.nx2 = header[7]  # ny
            self.nx1 = header[8]  # nx
            self.shape = (self.nx1, self.nx2, self.nx3)
            self.shape_fortran = (self.nx3, self.nx2, self.nx1)
        elif (self.num_dimensions == 2):
            self.nx2 = 1
            self.nx1 = header[7]
            self.shape = (self.nx1, self.nx3)
            self.shape_fortran = (self.nx3, self.nx1)
        elif (self.num_dimensions == 1):
            self.nx2 = 1
            self.nx1 = 1
            self.shape = (self.nx3,)
            self.shape_fortran = (self.nx3,)
        else:
            # TODO: raise this error in all cases of parsing
            raise IOError("Error reading dimension information from VTR file")

    def _parse_model(self):
        """Reads the actual model properties from the VTR file, initializes and
        populates the self.arrays
        """

        # make sure we have valid metadata first
        if not self.num_dimensions:
            raise RuntimeError("Attempted to read model without parsing metadata first")

        # initialize array list
        self.arrays = [None] * self.num_properties

        # simply read the whole thing as floats and shave off parts we don't need
        if self.use_memmap:
            model = numpy.memmap(self.file, dtype='float32', mode='r')
        else:
            model = numpy.fromfile(self.file, dtype=numpy.float32, count=-1)

        values_in_fastDim = self.num_properties * self.nx3

        if (self.num_dimensions == 3):
            model = model[10:]  # would be 8 for 1D models, 10 for 3D models
            model = model.reshape((self.nx1, self.nx2, values_in_fastDim + 2))
            model = model[:, :, 1:(values_in_fastDim + 1)]
            model = model.reshape((self.nx1, self.nx2, self.nx3, self.num_properties))
            for prop_index in range(0, self.num_properties):
                self.arrays[prop_index] = numpy.squeeze(model[:, :, :, prop_index])
        elif (self.num_dimensions == 2):
            model = model[9:]  # would be 8 for 1D models, 10 for 3D models
            model = model.reshape((self.nx1, values_in_fastDim + 2))
            model = model[:, 1:(values_in_fastDim + 1)]
            model = model.reshape((self.nx1, self.nx3, self.num_properties))
            for prop_index in range(0, self.num_properties):
                self.arrays[prop_index] = numpy.squeeze(model[:, :, prop_index])
        elif (self.num_dimensions == 1):
            model = model[8:]  # would be 8 for 1D models, 10 for 3D models
            model = model.reshape((values_in_fastDim + 2,))
            model = model[1:(values_in_fastDim + 1)]
            model = model.reshape((self.nx3, self.num_properties))
            for prop_index in range(0, self.num_properties):
                self.arrays[prop_index] = numpy.squeeze(model[:, prop_index])


def vtrfile_to_ndarray(filename, prop_index=0):
    """
    Convenience function to read a VTR file and return an NDarray
    that points to the `prop_index`-th property (0 is first, default)

    :param filename: file name of VTR file to read
    :type filename: str
    :param prop_index: desired property index (zero-based indexing), defaults to 0
    :type prop_index: int, optional
    :returns: a NumPy NDArray instance holding the desired model property
    :rtype: numpy.ndarray
    :raises: IOError
    """
    vtr = VTRModel(filename)
    if not vtr._file_exists():
        raise IOError("specified vtr file does not exist")
    return vtr.arrays[prop_index]


def print_vtr_metadata(vtr_object):
    """Quick diagnostic tool for printing the metadata of VTR objects

    :param vtr_object: input vtr model object
    :type vtr_object: VTRModel
    """
    print("VTR filename: ", vtr_object.file)
    print("Number of properties: ", vtr_object.num_properties)
    print("Number of dimensions: ", vtr_object.num_dimensions)
    print("NX1: ", vtr_object.nx1)
    print("NX2: ", vtr_object.nx2)
    print("NX3(fastest): ", vtr_object.nx3)
