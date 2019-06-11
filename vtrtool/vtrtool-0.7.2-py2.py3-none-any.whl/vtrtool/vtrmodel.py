"""Python utilities for Fullwave3D VTR model files

 * Licensed under terms of 3-Clause BSD license (see LICENSE)
 * Copyright (c) 2017 S-Cube, tlin@s-cube.com

"""
from __future__ import print_function
from builtins import range
import os.path
import struct
import json
import numpy


class VTRModel(object):
    """
    Represents a Fullwav3D VTR model in 1,2, or 3 dimensions
    """

    def __init__(self, file_name=None, read_model=True, use_memmap=False):
        """
        Initializes a VTR model with an existing vtr file

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
        self.arrays = list()  # list of ND-arrays

        if file_name is not None:
            self._read_from_file()

    def __repr__(self):
        p_str = "properties" if self.num_properties > 1 else "property"
        return "VTRModel(%i %s; nx1=%i nx2=%i nx3=%i)" \
               % (self.num_properties, p_str, self.nx1, self.nx2, self.nx3)

    def _read_from_file(self, read_model=True):
        if self._file_exists():
            self._parse_metadata()
            if read_model:
                self._parse_model()
        else:
            raise IOError("Given file_name does not point to a valid file")

    def _file_exists(self):
        """
        Checks if the VTR file_name points to a valid file that exists

        :returns: True if self.file_name is a valid file path and file exists
        :rtype: {bool}
        """
        return os.path.isfile(self.file)

    def _parse_metadata(self):
        """
        Fills in instance variables based on parsed vtr file,
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
        """
        Reads the actual model properties from the VTR file, initializes and
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
        self.model = model

    def save_vtr_file(self, out_filename):
        # saves to a VTR file

        meta_header = (12, self.num_properties, self.num_dimensions, 0, 12)
        meta_header_bytes = struct.pack("<" + ("i" * 5), *meta_header)

        dim_header = [4 * self.num_dimensions]
        dim_header.append(self.nx3)
        if self.num_dimensions == 2:
            dim_header.append(self.nx1)
        elif self.num_dimensions == 3:
            dim_header.append(self.nx2)
            dim_header.append(self.nx1)
        dim_header.append(4 * self.num_dimensions)
        dim_header_bytes = struct.pack(
            "<" + ("i" * (self.num_dimensions + 2)), *dim_header
        )

        num_traces = self.nx2 * self.nx1
        trace_length = self.nx3 * self.num_properties
        trace_rec_byte = struct.pack("<i", 4 * trace_length)
        flat_model = self.model.reshape((num_traces, trace_length))

        with open(out_filename, 'wb') as out_file:
            out_file.write(meta_header_bytes)
            out_file.write(dim_header_bytes)
            for tr in range(num_traces):
                out_file.write(trace_rec_byte)
                out_file.write(flat_model[tr, :].tobytes())
                out_file.write(trace_rec_byte)

    def meta_info(self, return_json=False):
        # returns a dict of meta info, a JSON string if flagged true
        meta = {}
        meta["filename"] = self.file
        meta["num_properties"] = self.num_properties
        meta["num_dimensions"] = self.num_dimensions
        meta["nx1"] = self.nx1
        meta["nx2"] = self.nx2
        meta["nx3"] = self.nx3

        if return_json:
            return json.dumps(meta)
        else:
            return meta

    @classmethod
    def from_ndarrays(cls, first_prop, *remaining_props):
        """
        constructs VTR model from 1 or more numpy ndarrays
        """
        # validate all input ad ndarrays
        if (not isinstance(first_prop, numpy.ndarray)) or \
           (not all(map(lambda x: isinstance(x, numpy.ndarray), remaining_props))):
            raise ValueError("input must be numpy ndarrays")

        # collect metadata from first input property
        first_prop = numpy.squeeze(first_prop)
        if first_prop.dtype is not numpy.dtype('float32'):
            first_prop = first_prop.astype('float32')
        vtr_shape = first_prop.shape
        num_dimensions = len(vtr_shape)

        # collect all properties and make sure they are consistent
        arrays = list()
        arrays.append(first_prop)

        for prop in remaining_props:
            if numpy.squeeze(prop).shape != vtr_shape:
                raise ValueError('all props must have the same dimensions')
            if prop.dtype is not numpy.dtype('float32'):
                prop = first_prop.astype('float32')
            arrays.append(prop)

        # zip all props up along fast dimension
        model = numpy.stack(arrays, axis=-1)

        # create object and populate metadata
        vtr = cls()
        vtr.num_dimensions = num_dimensions
        vtr.num_properties = len(arrays)
        vtr.shape = vtr_shape
        vtr.shape_fortran = vtr_shape[-1::-1]  # reverse
        vtr.arrays = [None] * vtr.num_properties

        if num_dimensions == 3:
            vtr.nx3 = vtr_shape[2]
            vtr.nx2 = vtr_shape[1]
            vtr.nx1 = vtr_shape[0]
            model = model.reshape((vtr.nx1, vtr.nx2, vtr.nx3, vtr.num_properties))
            for prop_index in range(0, vtr.num_properties):
                vtr.arrays[prop_index] = numpy.squeeze(model[:, :, :, prop_index])
        elif num_dimensions == 2:
            vtr.nx3 = vtr_shape[1]
            vtr.nx2 = 1
            vtr.nx1 = vtr_shape[0]
            model = model.reshape((vtr.nx1, vtr.nx3, vtr.num_properties))
            for prop_index in range(0, vtr.num_properties):
                vtr.arrays[prop_index] = numpy.squeeze(model[:, :, prop_index])
        elif num_dimensions == 1:
            vtr.nx3 = vtr_shape[0]
            vtr.nx2 = 1
            vtr.nx1 = 1
            model = model.reshape((vtr.nx3, vtr.num_properties))
            for prop_index in range(0, vtr.num_properties):
                vtr.arrays[prop_index] = numpy.squeeze(model[:, prop_index])

        vtr.model = model
        return vtr
