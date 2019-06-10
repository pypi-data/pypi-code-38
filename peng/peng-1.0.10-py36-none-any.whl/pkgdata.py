# pkgdata.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111

# Standard library imports
import os


###
# Global variables
###
VERSION_INFO = (1, 0, 10, "final", 0)
SUPPORTED_INTERPS = ["2.7", "3.5", "3.6", "3.7"]
COPYRIGHT_START = 2013
PKG_DESC = "This package provides engineering-related classes and functions"
PKG_LONG_DESC = os.linesep.join(
    [
        "This package provides engineering-related classes and functions, including:",
        "",
        "* A waveform :ref:`class <WaveformClass>` that is a first-class object:",
        "",
        "    .. code-block:: python",
        "",
        "        >>> import copy, numpy, peng",
        "        >>> obj_a=peng.Waveform(",
        "        ...     indep_vector=numpy.array([1, 2, 3]),",
        "        ...     dep_vector=numpy.array([10, 20, 30]),",
        "        ...     dep_name='obj_a'",
        "        ... )",
        "        >>> obj_b = obj_a*2",
        "        >>> print(obj_b)",
        "        Waveform: obj_a*2",
        "        Independent variable: [ 1, 2, 3 ]",
        "        Dependent variable: [ 20, 40, 60 ]",
        "        Independent variable scale: LINEAR",
        "        Dependent variable scale: LINEAR",
        "        Independent variable units: (None)",
        "        Dependent variable units: (None)",
        "        Interpolating function: CONTINUOUS",
        "        >>> obj_c = copy.copy(obj_b)",
        "        >>> obj_a == obj_b",
        "        False",
        "        >>> obj_b == obj_c",
        "        True",
        "",
        "  Numerous :ref:`functions <WaveformFunctions>` are provided (trigonometric,",
        "  calculus, transforms, etc.) and creating new functions that operate on",
        "  waveforms is simple since all of their relevant information can be accessed",
        "  through properties",
        "",
        "* Handling numbers represented in engineering notation, obtaining",
        "  their constituent components and converting to and from regular",
        "  floats. For example:",
        "",
        "    .. code-block:: python",
        "",
        "        >>> import peng",
        "        >>> x = peng.peng(1346, 2, True)",
        "        >>> x",
        "        '   1.35k'",
        "        >>> peng.peng_float(x)",
        "        1350.0",
        "        >>> peng.peng_int(x)",
        "        1",
        "        >>> peng.peng_frac(x)",
        "        35",
        "        >>> str(peng.peng_mant(x))",
        "        '1.35'",
        "        >>> peng.peng_power(x)",
        "        EngPower(suffix='k', exp=1000.0)",
        "        >>> peng.peng_suffix(x)",
        "        'k'",
        "",
        "* Pretty printing Numpy vectors. For example:",
        "",
        "    .. code-block:: python",
        "",
        "        >>> from __future__ import print_function",
        "        >>> import peng",
        "        >>> header = 'Vector: '",
        "        >>> data = [1e-3, 20e-6, 30e+6, 4e-12, 5.25e3, -6e-9, 70, 8, 9]",
        "        >>> print(",
        "        ...     header+peng.pprint_vector(",
        "        ...         data,",
        "        ...         width=30,",
        "        ...         eng=True,",
        "        ...         frac_length=1,",
        "        ...         limit=True,",
        "        ...         indent=len(header)",
        "        ...     )",
        "        ... )",
        "        Vector: [    1.0m,   20.0u,   30.0M,",
        "                             ...",
        "                    70.0 ,    8.0 ,    9.0  ]",
        "",
        "* Formatting numbers represented in scientific notation with a greater",
        "  degree of control and options than standard Python string formatting.",
        "  For example:",
        "",
        "    .. code-block:: python",
        "",
        "        >>> import peng",
        "        >>> peng.to_scientific_string(",
        "        ...     number=99.999,",
        "        ...     frac_length=1,",
        "        ...     exp_length=2,",
        "        ...     sign_always=True",
        "        ... )",
        "        '+1.0E+02'",
        "",
    ]
)
PKG_PIPELINE_ID = 6
PKG_DOC_SUBMODULES = ["functions", "wave_core", "wave_functions", "touchstone"]


###
# Functions
###
def _make_version(major, minor, micro, level, serial):
    """Generate version string from tuple (almost entirely from coveragepy)."""
    level_dict = {"alpha": "a", "beta": "b", "candidate": "rc", "final": ""}
    if level not in level_dict:
        raise RuntimeError("Invalid release level")
    version = "{0:d}.{1:d}".format(major, minor)
    if micro:
        version += ".{0:d}".format(micro)
    if level != "final":
        version += "{0}{1:d}".format(level_dict[level], serial)
    return version


__version__ = _make_version(*VERSION_INFO)
