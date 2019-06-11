from __future__ import print_function
from .vtrmodel import VTRModel
import segyio
from segyio import TraceField


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


def print_vtr_metadata(vtr_object, use_json=False):
    """
    Quick diagnostic tool for printing the metadata of VTR objects

    :param vtr_object: input vtr model object
    :type vtr_object: VTRModel
    """
    if use_json:
        print(vtr_object.meta_info(return_json=True))
    else:
        print("VTR filename: ", vtr_object.file)
        print("Number of properties: ", vtr_object.num_properties)
        print("Number of dimensions: ", vtr_object.num_dimensions)
        print("NX1: ", vtr_object.nx1)
        print("NX2: ", vtr_object.nx2)
        print("NX3(fastest): ", vtr_object.nx3)


def ndarrays_to_vtrfile(filename, *arrays):
    """
    Write one or more of properties represented by numpy ndarrays to a VTR file

    :param filename: file name of VTR file to write to
    :type filename: str
    :param arrays: one or more NumPy nudarrays, must all be the same shape with <= 3 dimensions
    :type arrays: numpy.ndarray
    """
    if len(arrays) < 1:
        raise ValueError("must have more than one array input")

    vtr = VTRModel.from_ndarrays(arrays[0], *arrays[1:])
    vtr.save_vtr_file(filename)


def segymodel_to_vtrmodel(filename):
    """
    Constructs a VTRModel from a SEGY file containing a single model parameter

    :param filename: file name of SEGY file describing the model
    :type filename: str
    """

    f = segyio.open(filename, mode="r", strict=False, ignore_geometry=True)

    # early exit if 1D, no need to get geometry information
    trace_count = f.tracecount
    if trace_count <= 1:
        trace = segyio.tools.collect(f.trace)
        return VTRModel.from_ndarrays(trace)

    # determine what headers to use for inline/crosslines
    # there are two main candidates: SourceX/SourceY and Inline3D/Crossline3D
    # additionally we use reciever/group and cdp X/Y headers as fallbacks

    last_sourceX = f.header[-1].get(TraceField.SourceX)
    last_sourceY = f.header[-1].get(TraceField.SourceY)

    last_inline3d = f.header[-1].get(TraceField.INLINE_3D)
    last_xline3d = f.header[-1].get(TraceField.CROSSLINE_3D)

    last_recieverX = f.header[-1].get(TraceField.GroupX)
    last_recieverY = f.header[-1].get(TraceField.GroupY)

    last_cdpX = f.header[-1].get(TraceField.CDP_X)
    last_cdpY = f.header[-1].get(TraceField.CDP_Y)

    # check to see whether any of the above headers are valid, and gives consistent trace count

    got_correct_headers = False
    info = {}

    if (last_sourceX > 0 or last_sourceY > 0):
        # read segy file using these headers for inline/xline sorting and see if trace count is consistent
        f = segyio.open(filename, mode="r", strict=False, iline=TraceField.SourceX, xline=TraceField.SourceY)
        if len(f.ilines) * len(f.xlines) == trace_count:
            got_correct_headers = True
            info["used_headers"] = "source"

    if not got_correct_headers and (last_inline3d > 0 or last_xline3d > 0):
        f = segyio.open(filename, mode="r", strict=False, iline=TraceField.INLINE_3D, xline=TraceField.CROSSLINE_3D)
        if len(f.ilines) * len(f.xlines) == trace_count:
            got_correct_headers = True
            info["used_headers"] = "inline3d"

    if not got_correct_headers and (last_recieverX > 0 or last_recieverY > 0):
        f = segyio.open(filename, mode="r", strict=False, iline=TraceField.GroupX, xline=TraceField.GroupY)
        if len(f.ilines) * len(f.xlines) == trace_count:
            got_correct_headers = True
            info["used_headers"] = "group"

    if not got_correct_headers and (last_cdpX > 0 or last_cdpY > 0):
        f = segyio.open(filename, mode="r", strict=False, iline=TraceField.CDP_X, xline=TraceField.CDP_Y)
        if len(f.ilines) * len(f.xlines) == trace_count:
            got_correct_headers = True
            info["used_headers"] = "cdp"

    if not got_correct_headers:
        raise ValueError('cannot determine a good inline/crossline header pair for the SEGY file')

    model_ndarray = segyio.tools.cube(f)
    if len(model_ndarray.shape) > 3:
        raise ValueError('SEGY model somehow got intrepreted as pre-stack data instead of a 3D post-stack')

    # SEGY files have inline/crossline transposed from VTR
    model_ndarray = model_ndarray.swapaxes(0, 1)  # this returns a new view instead of actually doing transposes

    return VTRModel.from_ndarrays(model_ndarray)


def segymodel_to_vtrfile(segy_filename, vtr_filename):
    """
    Makes a VTR model file from a SEGY file containing a single model parameter

    :param segy_filename: name of the SEGY model file to read
    :type segy_filename: str
    :param vtr_filename: name of the VTR model file to write
    :type vtr_filename: str
    """

    vtr = segymodel_to_vtrmodel(segy_filename)
    vtr.save_vtr_file(vtr_filename)
