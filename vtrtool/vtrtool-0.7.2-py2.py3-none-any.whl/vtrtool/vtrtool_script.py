#!/usr/bin/env python
"""
Utility to parse and manipulate Fullwave3D VTR files

vtrtool info         prints metadata concerning the VTR file
                     (you can additionally specify just the property to print,
                     e.g., `vtrtool info nx1 file.vtr` will just print out the
                     1st dimension of file.vtr)

vtrtool from_binary  converts a binary float32 file to a VTR file
                     (<num_props> optionally specifies the number of
                     properties encoded in the fast axis of the input file,
                     defaults to 1)

vtrtool to_binary    converts a VTR file to a single-property float32 binary file
vtrtool to_stdout    reads a VTR file and pipes the float32 binary model property to stdout
                     (--property=<index> specifies the <index-th> property in
                     the VTR file to convert, starting with 1)

Usage:
    vtrtool info [(ndims|nprops|nx1|nx2|nx3|json)] <vtr_filename>
    vtrtool from_binary <nx1> <nx2> <nx3> <bin_filename> <vtr_filename>
    vtrtool to_binary [--property=<index>] <vtr_filename> <bin_filename>
    vtrtool to_stdout [--property=<index>] <vtr_filename>

Options:
    -h --help       Show this help

"""
from __future__ import print_function
import sys
import vtrtool
import docopt
import numpy
import os


def _handle_filetype(filename, read_model=True):
    # Returns a VTRModel object from a file
    _, file_ext = os.path.splitext(filename)
    if file_ext == ".vtr":
        return vtrtool.VTRModel(filename, read_model=read_model)
    elif file_ext == ".sgy" or file_ext == ".segy":
        return vtrtool.segymodel_to_vtrmodel(filename)
    else:
        raise ValueError('unrecognized file extension')


def main():

    arguments = docopt.docopt(__doc__, version=vtrtool.__version__)

    if arguments["info"]:
        # prints metadata concerning the VTR file
        vtr = _handle_filetype(arguments["<vtr_filename>"], read_model=False)
        if arguments["ndims"]:
            print(vtr.num_dimensions)
        elif arguments["nprops"]:
            print(vtr.num_properties)
        elif arguments["nx1"]:
            print(vtr.nx1)
        elif arguments["nx2"]:
            print(vtr.nx2)
        elif arguments["nx3"]:
            print(vtr.nx3)
        elif arguments["json"]:
            vtrtool.print_vtr_metadata(vtr, use_json=True)
        else:
            vtrtool.print_vtr_metadata(vtr)

    elif arguments["to_binary"] or arguments["to_stdout"]:
        # converts a VTR file to a single-property float32 binary file, or
        # pipe the float32 binary model property to stdout
        vtr = _handle_filetype(arguments["<vtr_filename>"])
        if arguments["--property"]:
            prop_index = int(arguments["--property"]) - 1  # CLI uses Fortran index
        else:
            prop_index = 0  # first property
        model = vtr.arrays[prop_index]
        if arguments["to_binary"]:
            vtrtool.print_vtr_metadata(vtr)
            print("Dumping property", prop_index + 1)
            model.tofile(arguments["<bin_filename>"], sep="")
        elif arguments["to_stdout"]:
            model.tofile(sys.stdout, sep="")

    elif arguments["from_binary"]:
        # converts a float32 binary file to a VTR file

        num_props = 1  # assume model is single-property
        nx1 = int(arguments["nx1"])
        nx2 = int(arguments["nx2"])
        nx3 = int(arguments["nx3"])

        model = numpy.fromfile(arguments["bin_filename"], dtype=numpy.float32, count=-1)
        model = model.reshape((nx1, nx2, nx3, num_props))
        model_props = []
        for prop_num in range(num_props):
            model_props.append(model[:, :, :, prop_num])

        vtr = vtrtool.VTRModel.from_ndarrays(*model_props)
        vtr.save_vtr_file(arguments["vtr_filename"])

    else:
        pass


if __name__ == '__main__':
    main()
