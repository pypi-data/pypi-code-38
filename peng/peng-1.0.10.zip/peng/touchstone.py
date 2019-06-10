"""
Define Touchstone file format reader/writer.

[[[cog
import os, sys
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng_touchstone
exobj = trace_ex_eng_touchstone.trace_module(no_print=True)
]]]
[[[end]]]
"""
# touchstone.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0325,E1101,E1111,R0914,W0611

# Standard library imports
import copy
import math
import os
import re
import warnings

# PyPI imports
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    import numpy as np
import pexdoc.exh
import pexdoc.pcontracts
from pexdoc.ptypes import file_name, file_name_exists

# Intra-package imports imports
from .functions import to_scientific_string
from .ptypes import touchstone_data, touchstone_noise_data, touchstone_options


###
# Functions
###
def _chunk_noise(noise):
    """Chunk input noise data into valid Touchstone file rows."""
    data = zip(
        noise["freq"],
        noise["nf"],
        np.abs(noise["rc"]),
        np.angle(noise["rc"]),
        noise["res"],
    )
    for freq, nf, rcmag, rcangle, res in data:
        yield freq, nf, rcmag, rcangle, res


def _chunk_pars(freq_vector, data_matrix, pformat):
    """Chunk input data into valid Touchstone file rows."""
    pformat = pformat.upper()
    length = 4
    for freq, data in zip(freq_vector, data_matrix):
        data = data.flatten()
        for index in range(0, data.size, length):
            fpoint = [freq] if not index else [None]
            cdata = data[index : index + length]
            if pformat == "MA":
                vector1 = np.abs(cdata)
                vector2 = np.rad2deg(np.angle(cdata))
            elif pformat == "RI":
                vector1 = np.real(cdata)
                vector2 = np.imag(cdata)
            else:  # elif pformat == 'DB':
                vector1 = 20.0 * np.log10(np.abs(cdata))
                vector2 = np.rad2deg(np.angle(cdata))
            sep_data = np.array([])
            for item1, item2 in zip(vector1, vector2):
                sep_data = np.concatenate((sep_data, np.array([item1, item2])))
            ret = np.concatenate((np.array(fpoint), sep_data))
            yield ret


@pexdoc.pcontracts.contract(fname="file_name_exists")
def read_touchstone(fname):
    r"""
    Read a `Touchstone <https://ibis.org/connector/touchstone_spec11.pdf>`_ file.

    According to the specification a data line can have at most values for four
    complex parameters (plus potentially the frequency point), however this
    function is able to process malformed files as long as they have the
    correct number of data points (:code:`points` x :code:`nports` x
    :code:`nports` where :code:`points` represents the number of frequency
    points and :code:`nports` represents the number of ports in the file).  Per
    the Touchstone specification noise data is only supported for two-port
    files

    :param fname: Touchstone file name
    :type  fname: `FileNameExists <https://pexdoc.readthedocs.io/en/stable/
                  ptypes.html#filenameexists>`_

    :rtype: dictionary with the following structure:

     * **nports** (*integer*) -- number of ports

     * **opts** (:ref:`TouchstoneOptions`) -- File options

     * **data** (:ref:`TouchstoneData`) -- Parameter data

     * **noise** (:ref:`TouchstoneNoiseData`) -- Noise data, per the Touchstone
       specification only supported in 2-port files

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.touchstone.read_touchstone

    :raises:
     * OSError (File *[fname]* could not be found)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (File *[fname]* does not have a valid extension)

     * RuntimeError (File *[fname]* has no data)

     * RuntimeError (First non-comment line is not the option line)

     * RuntimeError (Frequency must increase)

     * RuntimeError (Illegal data in line *[lineno]*)

     * RuntimeError (Illegal option line)

     * RuntimeError (Malformed data)

     * RuntimeError (Malformed noise data)

     * RuntimeError (Noise frequency must increase)

    .. [[[end]]]

    .. note:: The returned parameter(s) are complex numbers in real and
       imaginary format regardless of the format used in the Touchstone file.
       Similarly, the returned frequency vector unit is Hertz regardless of
       the unit used in the Touchstone file
    """
    # pylint: disable=R0912,R0915,W0702
    # Exceptions definitions
    exnports = pexdoc.exh.addex(
        RuntimeError, "File *[fname]* does not have a valid extension"
    )
    exnoopt = pexdoc.exh.addex(
        RuntimeError, "First non-comment line is not the option line"
    )
    exopt = pexdoc.exh.addex(RuntimeError, "Illegal option line")
    exline = pexdoc.exh.addex(RuntimeError, "Illegal data in line *[lineno]*")
    exnodata = pexdoc.exh.addex(RuntimeError, "File *[fname]* has no data")
    exdata = pexdoc.exh.addex(RuntimeError, "Malformed data")
    exndata = pexdoc.exh.addex(RuntimeError, "Malformed noise data")
    exfreq = pexdoc.exh.addex(RuntimeError, "Frequency must increase")
    exnfreq = pexdoc.exh.addex(RuntimeError, "Noise frequency must increase")
    # Verify that file has correct extension format
    _, ext = os.path.splitext(fname)
    ext = ext.lower()
    nports_regexp = re.compile(r"\.s(\d+)p")
    match = nports_regexp.match(ext)
    exnports(not match, edata={"field": "fname", "value": fname})
    nports = int(match.groups()[0])
    opt_line = False
    units_dict = {"GHZ": "GHz", "MHZ": "MHz", "KHZ": "KHz", "HZ": "Hz"}
    scale_dict = {"GHZ": 1e9, "MHZ": 1e6, "KHZ": 1e3, "HZ": 1.0}
    units_opts = ["GHZ", "MHZ", "KHZ", "HZ"]
    type_opts = ["S", "Y", "Z", "H", "G"]
    format_opts = ["DB", "MA", "RI"]
    opts = dict(units=None, ptype=None, pformat=None, z0=None)
    data = []
    with open(fname, "r") as fobj:
        for num, line in enumerate(fobj):
            line = line.strip().upper()
            # Comment line
            if line.startswith("!"):
                continue
            # Options line
            if (not opt_line) and (not line.startswith("#")):
                exnoopt(True)
            if not opt_line:
                # Each Touchstone data file must contain an option line
                # (additional option lines after the first one will be ignored)
                opt_line = True
                tokens = line[1:].split()  # Remove initial hash
                if "R" in tokens:
                    idx = tokens.index("R")
                    add = 1
                    if len(tokens) > idx + 1:
                        try:
                            opts["z0"] = float(tokens[idx + 1])
                            add = 2
                        except:
                            pass
                    tokens = tokens[:idx] + tokens[idx + add :]
                matches = 0
                for token in tokens:
                    if (token in format_opts) and (not opts["pformat"]):
                        matches += 1
                        opts["pformat"] = token
                    elif (token in units_opts) and (not opts["units"]):
                        matches += 1
                        opts["units"] = units_dict[token]
                    elif (token in type_opts) and (not opts["ptype"]):
                        matches += 1
                        opts["ptype"] = token
                exopt(matches != len(tokens))
            if opt_line and line.startswith("#"):
                continue
            # Data lines
            try:
                if "!" in line:
                    idx = line.index("!")
                    line = line[:idx]
                tokens = [float(item) for item in line.split()]
                data.append(tokens)
            except:
                exline(True, edata={"field": "lineno", "value": num + 1})
    data = np.concatenate(data)
    exnodata(not data.size, edata={"field": "fname", "value": fname})
    # Set option defaults
    opts["units"] = opts["units"] or "GHz"
    opts["ptype"] = opts["ptype"] or "S"
    opts["pformat"] = opts["pformat"] or "MA"
    opts["z0"] = opts["z0"] or 50
    # Format data
    data_dict = {}
    nums_per_freq = 1 + (2 * (nports ** 2))
    fslice = slice(0, data.size, nums_per_freq)
    freq = data[fslice]
    ndiff = np.diff(freq)
    ndict = {}
    if (nports == 2) and ndiff.size and (min(ndiff) <= 0):
        # Extract noise data
        npoints = np.where(ndiff <= 0)[0][0] + 1
        freq = freq[:npoints]
        ndata = data[9 * npoints :]
        nfpoints = int(ndata.size / 5.0)
        exndata(ndata.size % 5 != 0)
        data = data[: 9 * npoints]
        ndiff = 1
        nfslice = slice(0, ndata.size, 5)
        nfreq = ndata[nfslice]
        ndiff = np.diff(nfreq)
        exnfreq(bool(ndiff.size and (min(ndiff) <= 0)))
        nfig_slice = slice(1, ndata.size, 5)
        rlmag_slice = slice(2, ndata.size, 5)
        rlphase_slice = slice(3, ndata.size, 5)
        res_slice = slice(4, ndata.size, 5)
        ndict["freq"] = scale_dict[opts["units"].upper()] * nfreq
        ndict["nf"] = ndata[nfig_slice]
        ndict["rc"] = ndata[rlmag_slice] * np.exp(1j * ndata[rlphase_slice])
        ndict["res"] = ndata[res_slice]
        ndict["points"] = nfpoints
    exdata(data.size % nums_per_freq != 0)
    npoints = int(data.size / nums_per_freq)
    exfreq(bool(ndiff.size and (min(ndiff) <= 0)))
    data_dict["freq"] = scale_dict[opts["units"].upper()] * freq
    d1slice = slice(0, data.size, 2)
    d2slice = slice(1, data.size, 2)
    data = np.delete(data, fslice)
    # For format that has angle information, the angle is given in degrees
    if opts["pformat"] == "MA":
        data = data[d1slice] * np.exp(1j * np.deg2rad(data[d2slice]))
    elif opts["pformat"] == "RI":
        data = data[d1slice] + (1j * data[d2slice])
    else:  # if opts['pformat'] == 'DB':
        data = (10 ** (data[d1slice] / 20.0)) * np.exp(1j * np.deg2rad(data[d2slice]))
    if nports > 1:
        data_dict["pars"] = np.resize(data, (npoints, nports, nports))
    else:
        data_dict["pars"] = copy.copy(data)
    del data
    data_dict["points"] = npoints
    if nports == 2:
        # The order of data for a two-port file is N11, N21, N12, N22 but for
        # m ports where m > 2, the order is N11, N12, N13, ..., N1m
        data_dict["pars"] = np.transpose(data_dict["pars"], (0, 2, 1))
    return dict(nports=nports, opts=opts, data=data_dict, noise=ndict)


@pexdoc.pcontracts.contract(
    fname="file_name",
    options="touchstone_options",
    data="touchstone_data",
    noise="None|touchstone_noise_data",
    frac_length="int,>=0",
    exp_length="int,>0",
)
def write_touchstone(fname, options, data, noise=None, frac_length=10, exp_length=2):
    r"""
    Write a `Touchstone`_ file.

    Parameter data is first resized to an :code:`points` x :code:`nports` x
    :code:`nports` where :code:`points` represents the number of frequency
    points and :code:`nports` represents the number of ports in the file; then
    parameter data is written to file in scientific notation

    :param fname: Touchstone file name
    :type  fname: `FileNameExists <https://pexdoc.readthedocs.io/en/stable/
                  ptypes.html#filenameexists>`_

    :param options: Touchstone file options
    :type  options: :ref:`TouchstoneOptions`

    :param data: Touchstone file parameter data
    :type  data: :ref:`TouchstoneData`

    :param noise: Touchstone file parameter noise data (only supported in
                  two-port files)
    :type  noise: :ref:`TouchstoneNoiseData`

    :param frac_length: Number of digits to use in fractional part of data
    :type  frac_length: non-negative integer

    :param exp_length: Number of digits to use in exponent
    :type  exp_length: positive integer

    .. [[[cog cog.out(exobj.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.touchstone.write_touchstone

    :raises:
     * RuntimeError (Argument \`data\` is not valid)

     * RuntimeError (Argument \`exp_length\` is not valid)

     * RuntimeError (Argument \`fname\` is not valid)

     * RuntimeError (Argument \`frac_length\` is not valid)

     * RuntimeError (Argument \`noise\` is not valid)

     * RuntimeError (Argument \`options\` is not valid)

     * RuntimeError (File *[fname]* does not have a valid extension)

     * RuntimeError (Malformed data)

     * RuntimeError (Noise data only supported in two-port files)

    .. [[[end]]]
    """
    # pylint: disable=R0913
    # Exceptions definitions
    exnports = pexdoc.exh.addex(
        RuntimeError, "File *[fname]* does not have a valid extension"
    )
    exnoise = pexdoc.exh.addex(
        RuntimeError, "Noise data only supported in two-port files"
    )
    expoints = pexdoc.exh.addex(RuntimeError, "Malformed data")
    # Data validation
    _, ext = os.path.splitext(fname)
    ext = ext.lower()
    nports_regexp = re.compile(r"\.s(\d+)p")
    match = nports_regexp.match(ext)
    exnports(not match, edata={"field": "fname", "value": fname})
    nports = int(match.groups()[0])
    exnoise(bool((nports != 2) and noise))
    nums_per_freq = nports ** 2
    expoints(data["points"] * nums_per_freq != data["pars"].size)
    #
    npoints = data["points"]
    par_data = np.resize(np.copy(data["pars"]), (npoints, nports, nports))
    if nports == 2:
        par_data = np.transpose(par_data, (0, 2, 1))
    units_dict = {"ghz": "GHz", "mhz": "MHz", "khz": "KHz", "hz": "Hz"}
    options["units"] = units_dict[options["units"].lower()]
    fspace = 2 + frac_length + (exp_length + 2)
    # Format data
    with open(fname, "w") as fobj:
        fobj.write(
            "# {units} {ptype} {pformat} R {z0}\n".format(
                units=options["units"],
                ptype=options["ptype"],
                pformat=options["pformat"],
                z0=options["z0"],
            )
        )
        for row in _chunk_pars(data["freq"], par_data, options["pformat"]):
            row_data = [
                to_scientific_string(item, frac_length, exp_length, bool(num != 0))
                if item is not None
                else fspace * " "
                for num, item in enumerate(row)
            ]
            fobj.write(" ".join(row_data) + "\n")
        if (nports == 2) and noise:
            fobj.write("! Noise data\n")
            for row in _chunk_noise(noise):
                row_data = [
                    to_scientific_string(item, frac_length, exp_length, bool(num != 0))
                    for num, item in enumerate(row)
                ]
                fobj.write(" ".join(row_data) + "\n")
