"""
Waveform pseudo-type functions.

[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng_wave_functions
exobj_eng = trace_ex_eng_wave_functions.trace_module(no_print=True)
]]]
[[[end]]]
"""
# wave_functions.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0413,E1101,E1111,R0913,W0212

# Standard library imports
import copy
import math
import os
import warnings

# PyPI imports
if os.environ.get("READTHEDOCS", "") != "True":
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        import numpy as np
import pexdoc.exh
import pexdoc.pcontracts

# Intra-package imports imports
from .functions import remove_extra_delims
from .constants import FP_ATOL, FP_RTOL
from .wave_core import _interp_dep_vector, Waveform


###
# Functions
###
def _barange(bmin, bmax, inc):
    vector = np.arange(bmin, bmax + inc, inc)
    vector = vector if np.isclose(bmax, vector[-1], FP_RTOL, FP_ATOL) else vector[:-1]
    return vector


def _bound_waveform(wave, indep_min, indep_max):
    """Add independent variable vector bounds if they are not in vector."""
    indep_min, indep_max = _validate_min_max(wave, indep_min, indep_max)
    indep_vector = copy.copy(wave._indep_vector)
    if (
        isinstance(indep_min, float) or isinstance(indep_max, float)
    ) and indep_vector.dtype.name.startswith("int"):
        indep_vector = indep_vector.astype(float)
    min_pos = np.searchsorted(indep_vector, indep_min)
    if not np.isclose(indep_min, indep_vector[min_pos], FP_RTOL, FP_ATOL):
        indep_vector = np.insert(indep_vector, min_pos, indep_min)
    max_pos = np.searchsorted(indep_vector, indep_max)
    if not np.isclose(indep_max, indep_vector[max_pos], FP_RTOL, FP_ATOL):
        indep_vector = np.insert(indep_vector, max_pos, indep_max)
    dep_vector = _interp_dep_vector(wave, indep_vector)
    wave._indep_vector = indep_vector[min_pos : max_pos + 1]
    wave._dep_vector = dep_vector[min_pos : max_pos + 1]


def _build_units(indep_units, dep_units, op):
    """Build unit math operations."""
    if (not dep_units) and (not indep_units):
        return ""
    if dep_units and (not indep_units):
        return dep_units
    if (not dep_units) and indep_units:
        return (
            remove_extra_delims("1{0}({1})".format(op, indep_units))
            if op == "/"
            else remove_extra_delims("({0})".format(indep_units))
        )
    return remove_extra_delims("({0}){1}({2})".format(dep_units, op, indep_units))


def _operation(wave, desc, units, fpointer):
    """Perform generic operation on a waveform object."""
    ret = copy.copy(wave)
    ret.dep_units = units
    ret.dep_name = "{0}({1})".format(desc, ret.dep_name)
    ret._dep_vector = fpointer(ret._dep_vector)
    return ret


def _running_area(indep_vector, dep_vector):
    """Calculate running area under curve."""
    rect_height = np.minimum(dep_vector[:-1], dep_vector[1:])
    rect_base = np.diff(indep_vector)
    rect_area = np.multiply(rect_height, rect_base)
    triang_height = np.abs(np.diff(dep_vector))
    triang_area = 0.5 * np.multiply(triang_height, rect_base)
    return np.cumsum(np.concatenate((np.array([0.0]), triang_area + rect_area)))


def _validate_min_max(wave, indep_min, indep_max):
    """Validate min and max bounds are within waveform's independent variable vector."""
    imin, imax = False, False
    if indep_min is None:
        indep_min = wave._indep_vector[0]
        imin = True
    if indep_max is None:
        indep_max = wave._indep_vector[-1]
        imax = True
    if imin and imax:
        return indep_min, indep_max
    exminmax = pexdoc.exh.addex(
        RuntimeError, "Incongruent `indep_min` and `indep_max` arguments"
    )
    exmin = pexdoc.exh.addai("indep_min")
    exmax = pexdoc.exh.addai("indep_max")
    exminmax(bool(indep_min >= indep_max))
    exmin(
        bool(
            (indep_min < wave._indep_vector[0])
            and (not np.isclose(indep_min, wave._indep_vector[0], FP_RTOL, FP_ATOL))
        )
    )
    exmax(
        bool(
            (indep_max > wave._indep_vector[-1])
            and (not np.isclose(indep_max, wave._indep_vector[-1], FP_RTOL, FP_ATOL))
        )
    )
    return indep_min, indep_max


@pexdoc.pcontracts.contract(wave=Waveform)
def acos(wave):
    r"""
    Return the arc cosine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.acos

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        ValueError,
        "Math domain error",
        bool((min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)),
    )
    return _operation(wave, "acos", "rad", np.arccos)


@pexdoc.pcontracts.contract(wave=Waveform)
def acosh(wave):
    r"""
    Return the hyperbolic arc cosine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.acosh

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(ValueError, "Math domain error", bool(min(wave._dep_vector) < 1))
    return _operation(wave, "acosh", "", np.arccosh)


@pexdoc.pcontracts.contract(wave=Waveform)
def asin(wave):
    r"""
    Return the arc sine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.asin

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        ValueError,
        "Math domain error",
        bool((min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)),
    )
    return _operation(wave, "asin", "rad", np.arcsin)


@pexdoc.pcontracts.contract(wave=Waveform)
def asinh(wave):
    r"""
    Return the hyperbolic arc sine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.asinh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "asinh", "", np.arcsinh)


@pexdoc.pcontracts.contract(wave=Waveform)
def atan(wave):
    r"""
    Return the arc tangent of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.atan

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "atan", "rad", np.arctan)


@pexdoc.pcontracts.contract(wave=Waveform)
def atanh(wave):
    r"""
    Return the hyperbolic arc tangent of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.atanh

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        ValueError,
        "Math domain error",
        bool((min(wave._dep_vector) < -1) or (max(wave._dep_vector) > 1)),
    )
    return _operation(wave, "atanh", "", np.arctanh)


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def average(wave, indep_min=None, indep_max=None):
    r"""
    Return the running average of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.average

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    area = _running_area(ret._indep_vector, ret._dep_vector)
    area[0] = ret._dep_vector[0]
    deltas = ret._indep_vector - ret._indep_vector[0]
    deltas[0] = 1.0
    ret._dep_vector = np.divide(area, deltas)
    ret.dep_name = "average({0})".format(ret._dep_name)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def ceil(wave):
    r"""
    Return the ceiling of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ceil

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "ceil", wave.dep_units, np.ceil)


@pexdoc.pcontracts.contract(wave=Waveform)
def cos(wave):
    r"""
    Return the cosine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.cos

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "cos", "", np.cos)


@pexdoc.pcontracts.contract(wave=Waveform)
def cosh(wave):
    r"""
    Return the hyperbolic cosine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.cosh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "cosh", "", np.cosh)


@pexdoc.pcontracts.contract(wave=Waveform)
def db(wave):
    r"""
    Return a waveform's dependent variable vector expressed in decibels.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.db

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        ValueError, "Math domain error", bool((np.min(np.abs(wave._dep_vector)) <= 0))
    )
    ret = copy.copy(wave)
    ret.dep_units = "dB"
    ret.dep_name = "db({0})".format(ret.dep_name)
    ret._dep_vector = 20.0 * np.log10(np.abs(ret._dep_vector))
    return ret


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def derivative(wave, indep_min=None, indep_max=None):
    r"""
    Return the numerical derivative of a waveform's dependent variable vector.

    The method used is the `backwards differences
    <https://en.wikipedia.org/wiki/
    Finite_difference#Forward.2C_backward.2C_and_central_differences>`_ method

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.derivative

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    delta_indep = np.diff(ret._indep_vector)
    delta_dep = np.diff(ret._dep_vector)
    delta_indep = np.concatenate((np.array([delta_indep[0]]), delta_indep))
    delta_dep = np.concatenate((np.array([delta_dep[0]]), delta_dep))
    ret._dep_vector = np.divide(delta_dep, delta_indep)
    ret.dep_name = "derivative({0})".format(ret._dep_name)
    ret.dep_units = _build_units(ret.indep_units, ret.dep_units, "/")
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def exp(wave):
    r"""
    Return the natural exponent of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.exp

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "exp", "", np.exp)


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def fft(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.fft

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform sampling)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    npoints = npoints or ret._indep_vector.size
    fs = (npoints - 1) / float(ret._indep_vector[-1])
    spoints = min(ret._indep_vector.size, npoints)
    sdiff = np.diff(ret._indep_vector[:spoints])
    cond = not np.all(
        np.isclose(sdiff, sdiff[0] * np.ones(spoints - 1), FP_RTOL, FP_ATOL)
    )
    pexdoc.addex(RuntimeError, "Non-uniform sampling", cond)
    finc = fs / float(npoints - 1)
    indep_vector = _barange(-fs / 2.0, +fs / 2.0, finc)
    dep_vector = np.fft.fft(ret._dep_vector, npoints)
    return Waveform(
        indep_vector=indep_vector,
        dep_vector=dep_vector,
        dep_name="fft({0})".format(ret.dep_name),
        indep_scale="LINEAR",
        dep_scale="LINEAR",
        indep_units="Hz",
        dep_units="",
    )


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def fftdb(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the Fast Fourier Transform of a waveform.

    The dependent variable vector of the returned waveform is expressed in decibels

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.fftdb

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform sampling)

    .. [[[end]]]
    """
    return db(fft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def ffti(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the imaginary part of the Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ffti

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform sampling)

    .. [[[end]]]
    """
    return imag(fft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def fftm(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the magnitude of the Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.fftm

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform sampling)

    .. [[[end]]]
    """
    return abs(fft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
    unwrap=bool,
    rad=bool,
)
def fftp(wave, npoints=None, indep_min=None, indep_max=None, unwrap=True, rad=True):
    r"""
    Return the phase of the Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :param unwrap: Flag that indicates whether phase should change phase shifts
                   to their :code:`2*pi` complement (True) or not (False)
    :type  unwrap: boolean

    :param rad: Flag that indicates whether phase should be returned in radians
                (True) or degrees (False)
    :type  rad: boolean

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.fftp

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`rad\` is not valid)

     * RuntimeError (Argument \`unwrap\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform sampling)

    .. [[[end]]]
    """
    return phase(fft(wave, npoints, indep_min, indep_max), unwrap=unwrap, rad=rad)


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def fftr(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the real part of the Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.fftr

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform sampling)

    .. [[[end]]]
    """
    return real(fft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    dep_var="number",
    der="None|(int,>=-1,<=+1)",
    inst="int,>0",
    indep_min="None|number",
    indep_max="None|number",
)
def find(wave, dep_var, der=None, inst=1, indep_min=None, indep_max=None):
    r"""
    Return the independent variable point associated with a dependent variable point.

    If the dependent variable point is not in the dependent variable vector the
    independent variable vector point is obtained by linear interpolation

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param dep_var: Dependent vector value to search for
    :type  dep_var: integer, float or complex

    :param der: Dependent vector derivative filter. If +1 only independent
                vector points that have positive derivatives when crossing
                the requested dependent vector point are returned; if -1 only
                independent vector points that have negative derivatives when
                crossing the requested dependent vector point are returned;
                if 0 only independent vector points that have null derivatives
                when crossing the requested dependent vector point are
                returned; otherwise if None all independent vector points are
                returned regardless of the dependent vector derivative. The
                derivative of the first and last point of the waveform is
                assumed to be null
    :type  der: integer, float or complex

    :param inst: Instance number filter. If, for example, **inst** equals 3,
                 then the independent variable vector point at which the
                 dependent variable vector equals the requested value for the
                 third time is returned
    :type  inst: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: integer, float or None if the dependent variable point is not found

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.find

    :raises:
     * RuntimeError (Argument \`dep_var\` is not valid)

     * RuntimeError (Argument \`der\` is not valid)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`inst\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    # pylint: disable=C0325,R0914,W0613
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    close_min = np.isclose(min(ret._dep_vector), dep_var, FP_RTOL, FP_ATOL)
    close_max = np.isclose(max(ret._dep_vector), dep_var, FP_RTOL, FP_ATOL)
    if ((np.amin(ret._dep_vector) > dep_var) and (not close_min)) or (
        (np.amax(ret._dep_vector) < dep_var) and (not close_max)
    ):
        return None
    cross_wave = ret._dep_vector - dep_var
    sign_wave = np.sign(cross_wave)
    exact_idx = np.where(np.isclose(ret._dep_vector, dep_var, FP_RTOL, FP_ATOL))[0]
    # Locations where dep_vector crosses dep_var or it is equal to it
    left_idx = np.where(np.diff(sign_wave))[0]
    # Remove elements to the left of exact matches
    left_idx = np.setdiff1d(left_idx, exact_idx)
    left_idx = np.setdiff1d(left_idx, exact_idx - 1)
    right_idx = left_idx + 1 if left_idx.size else np.array([])
    indep_var = ret._indep_vector[exact_idx] if exact_idx.size else np.array([])
    dvector = np.zeros(exact_idx.size).astype(int) if exact_idx.size else np.array([])
    if left_idx.size and (ret.interp == "STAIRCASE"):
        idvector = (
            2.0 * (ret._dep_vector[right_idx] > ret._dep_vector[left_idx]).astype(int)
            - 1
        )
        if indep_var.size:
            indep_var = np.concatenate((indep_var, ret._indep_vector[right_idx]))
            dvector = np.concatenate((dvector, idvector))
            sidx = np.argsort(indep_var)
            indep_var = indep_var[sidx]
            dvector = dvector[sidx]
        else:
            indep_var = ret._indep_vector[right_idx]
            dvector = idvector
    elif left_idx.size:
        y_left = ret._dep_vector[left_idx]
        y_right = ret._dep_vector[right_idx]
        x_left = ret._indep_vector[left_idx]
        x_right = ret._indep_vector[right_idx]
        slope = ((y_left - y_right) / (x_left - x_right)).astype(float)
        # y = y0+slope*(x-x0) => x0+(y-y0)/slope
        if indep_var.size:
            indep_var = np.concatenate(
                (indep_var, x_left + ((dep_var - y_left) / slope))
            )
            dvector = np.concatenate((dvector, np.where(slope > 0, 1, -1)))
            sidx = np.argsort(indep_var)
            indep_var = indep_var[sidx]
            dvector = dvector[sidx]
        else:
            indep_var = x_left + ((dep_var - y_left) / slope)
            dvector = np.where(slope > 0, +1, -1)
    if der is not None:
        indep_var = np.extract(dvector == der, indep_var)
    return indep_var[inst - 1] if inst <= indep_var.size else None


@pexdoc.pcontracts.contract(wave=Waveform)
def floor(wave):
    r"""
    Return the floor of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.floor

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "floor", wave.dep_units, np.floor)


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def ifft(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the inverse Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ifft

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform frequency spacing)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    npoints = npoints or ret._indep_vector.size
    spoints = min(ret._indep_vector.size, npoints)
    sdiff = np.diff(ret._indep_vector[:spoints])
    finc = sdiff[0]
    cond = not np.all(np.isclose(sdiff, finc * np.ones(spoints - 1), FP_RTOL, FP_ATOL))
    pexdoc.addex(RuntimeError, "Non-uniform frequency spacing", cond)
    fs = (npoints - 1) * finc
    tinc = 1 / float(fs)
    tend = 1 / float(finc)
    indep_vector = _barange(0, tend, tinc)
    dep_vector = np.fft.ifft(ret._dep_vector, npoints)
    return Waveform(
        indep_vector=indep_vector,
        dep_vector=dep_vector,
        dep_name="ifft({0})".format(ret.dep_name),
        indep_scale="LINEAR",
        dep_scale="LINEAR",
        indep_units="sec",
        dep_units="",
    )


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def ifftdb(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the inverse Fast Fourier Transform of a waveform.

    The dependent variable vector of the returned waveform is expressed in decibels

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ifftdb

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform frequency spacing)

    .. [[[end]]]
    """
    return db(ifft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def iffti(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the imaginary part of the inverse Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.iffti

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform frequency spacing)

    .. [[[end]]]
    """
    return imag(ifft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def ifftm(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the magnitude of the inverse Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ifftm

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform frequency spacing)

    .. [[[end]]]
    """
    return abs(ifft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
    unwrap=bool,
    rad=bool,
)
def ifftp(wave, npoints=None, indep_min=None, indep_max=None, unwrap=True, rad=True):
    r"""
    Return the phase of the inverse Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :param unwrap: Flag that indicates whether phase should change phase shifts
                   to their :code:`2*pi` complement (True) or not (False)
    :type  unwrap: boolean

    :param rad: Flag that indicates whether phase should be returned in radians
                (True) or degrees (False)
    :type  rad: boolean

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ifftp

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`rad\` is not valid)

     * RuntimeError (Argument \`unwrap\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform frequency spacing)

    .. [[[end]]]
    """
    return phase(ifft(wave, npoints, indep_min, indep_max), unwrap=unwrap, rad=rad)


@pexdoc.pcontracts.contract(
    wave=Waveform,
    npoints="None|(int,>=1)",
    indep_min="None|number",
    indep_max="None|number",
)
def ifftr(wave, npoints=None, indep_min=None, indep_max=None):
    r"""
    Return the real part of the inverse Fast Fourier Transform of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param npoints: Number of points to use in the transform. If **npoints**
                    is less than the size of the independent variable vector
                    the waveform is truncated; if **npoints** is greater than
                    the size of the independent variable vector, the waveform
                    is zero-padded
    :type  npoints: positive integer

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.ifftr

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`npoints\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

     * RuntimeError (Non-uniform frequency spacing)

    .. [[[end]]]
    """
    return real(ifft(wave, npoints, indep_min, indep_max))


@pexdoc.pcontracts.contract(wave=Waveform)
def imag(wave):
    r"""
    Return the imaginary part of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.imag

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "imag", wave.dep_units, np.imag)


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def integral(wave, indep_min=None, indep_max=None):
    r"""
    Return the running integral of a waveform's dependent variable vector.

    The method used is the `trapezoidal
    <https://en.wikipedia.org/wiki/Trapezoidal_rule>`_ method

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.integral

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    ret._dep_vector = _running_area(ret._indep_vector, ret._dep_vector)
    ret.dep_name = "integral({0})".format(ret._dep_name)
    ret.dep_units = _build_units(ret.indep_units, ret.dep_units, "*")
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def group_delay(wave):
    r"""
    Return the group delay of a waveform.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.group_delay

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    ret = -derivative(phase(wave, unwrap=True) / (2 * math.pi))
    ret.dep_name = "group_delay({0})".format(wave.dep_name)
    ret.dep_units = "sec"
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def log(wave):
    r"""
    Return the natural logarithm of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.log

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        ValueError, "Math domain error", bool((min(wave._dep_vector) <= 0))
    )
    return _operation(wave, "log", "", np.log)


@pexdoc.pcontracts.contract(wave=Waveform)
def log10(wave):
    r"""
    Return the base 10 logarithm of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.log10

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Math domain error)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        ValueError, "Math domain error", bool((min(wave._dep_vector) <= 0))
    )
    return _operation(wave, "log10", "", np.log10)


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def naverage(wave, indep_min=None, indep_max=None):
    r"""
    Return the numerical average of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.naverage

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    delta_x = ret._indep_vector[-1] - ret._indep_vector[0]
    return np.trapz(ret._dep_vector, x=ret._indep_vector) / delta_x


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def nintegral(wave, indep_min=None, indep_max=None):
    r"""
    Return the numerical integral of a waveform's dependent variable vector.

    The method used is the `trapezoidal
    <https://en.wikipedia.org/wiki/Trapezoidal_rule>`_ method

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.nintegral

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    return np.trapz(ret._dep_vector, ret._indep_vector)


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def nmax(wave, indep_min=None, indep_max=None):
    r"""
    Return the maximum of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.nmax

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    return np.max(ret._dep_vector)


@pexdoc.pcontracts.contract(
    wave=Waveform, indep_min="None|number", indep_max="None|number"
)
def nmin(wave, indep_min=None, indep_max=None):
    r"""
    Return the minimum of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :rtype: float

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.nmin

    :raises:
     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    _bound_waveform(ret, indep_min, indep_max)
    return np.min(ret._dep_vector)


@pexdoc.pcontracts.contract(wave=Waveform, unwrap=bool, rad=bool)
def phase(wave, unwrap=True, rad=True):
    r"""
    Return the phase of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param unwrap: Flag that indicates whether phase should change phase shifts
                   to their :code:`2*pi` complement (True) or not (False)
    :type  unwrap: boolean

    :param rad: Flag that indicates whether phase should be returned in radians
                (True) or degrees (False)
    :type  rad: boolean

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.phase

    :raises:
     * RuntimeError (Argument \`rad\` is not valid)

     * RuntimeError (Argument \`unwrap\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    ret.dep_units = "rad" if rad else "deg"
    ret.dep_name = "phase({0})".format(ret.dep_name)
    ret._dep_vector = (
        np.unwrap(np.angle(ret._dep_vector)) if unwrap else np.angle(ret._dep_vector)
    )
    if not rad:
        ret._dep_vector = np.rad2deg(ret._dep_vector)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def real(wave):
    r"""
    Return the real part of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.real

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "real", wave.dep_units, np.real)


@pexdoc.pcontracts.contract(wave=Waveform, decimals="int,>=0")
def round(wave, decimals=0):
    r"""
    Round a waveform's dependent variable vector to a given number of decimal places.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param decimals: Number of decimals to round to
    :type  decimals: integer

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.round

    :raises:
     * RuntimeError (Argument \`decimals\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    # pylint: disable=W0622
    pexdoc.exh.addex(
        TypeError,
        "Cannot convert complex to integer",
        wave._dep_vector.dtype.name.startswith("complex"),
    )
    ret = copy.copy(wave)
    ret.dep_name = "round({0}, {1})".format(ret.dep_name, decimals)
    ret._dep_vector = np.round(wave._dep_vector, decimals)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def sin(wave):
    r"""
    Return the sine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.sin

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "sin", "", np.sin)


@pexdoc.pcontracts.contract(wave=Waveform)
def sinh(wave):
    r"""
    Return the hyperbolic sine of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.sinh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "sinh", "", np.sinh)


@pexdoc.pcontracts.contract(wave=Waveform)
def sqrt(wave):
    r"""
    Return the square root of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.sqrt

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    dep_units = "{0}**0.5".format(wave.dep_units)
    return _operation(wave, "sqrt", dep_units, np.sqrt)


@pexdoc.pcontracts.contract(
    wave=Waveform,
    dep_name="str|None",
    indep_min="None|number",
    indep_max="None|number",
    indep_step="None|number",
)
def subwave(wave, dep_name=None, indep_min=None, indep_max=None, indep_step=None):
    r"""
    Return a waveform that is a sub-set of a waveform, potentially re-sampled.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param  dep_name: Independent variable name
    :type   dep_name: `NonNullString <https://pexdoc.readthedocs.io/en/stable/
                        ptypes.html#nonnullstring>`_

    :param indep_min: Independent vector start point of computation
    :type  indep_min: integer or float

    :param indep_max: Independent vector stop point of computation
    :type  indep_max: integer or float

    :param indep_step: Independent vector step
    :type  indep_step: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.subwave

    :raises:
     * RuntimeError (Argument \`dep_name\` is not valid)

     * RuntimeError (Argument \`indep_max\` is not valid)

     * RuntimeError (Argument \`indep_min\` is not valid)

     * RuntimeError (Argument \`indep_step\` is greater than independent
       vector range)

     * RuntimeError (Argument \`indep_step\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * RuntimeError (Incongruent \`indep_min\` and \`indep_max\`
       arguments)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    if dep_name is not None:
        ret.dep_name = dep_name
    _bound_waveform(ret, indep_min, indep_max)
    pexdoc.addai("indep_step", bool((indep_step is not None) and (indep_step <= 0)))
    exmsg = "Argument `indep_step` is greater than independent vector range"
    cond = bool(
        (indep_step is not None)
        and (indep_step > ret._indep_vector[-1] - ret._indep_vector[0])
    )
    pexdoc.addex(RuntimeError, exmsg, cond)
    if indep_step:
        indep_vector = _barange(indep_min, indep_max, indep_step)
        dep_vector = _interp_dep_vector(ret, indep_vector)
        ret._set_indep_vector(indep_vector, check=False)
        ret._set_dep_vector(dep_vector, check=False)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def tan(wave):
    r"""
    Return the tangent of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for peng.wave_functions.tan

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "tan", "", np.tan)


@pexdoc.pcontracts.contract(wave=Waveform)
def tanh(wave):
    r"""
    Return the hyperbolic tangent of a waveform's dependent variable vector.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.tanh

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    return _operation(wave, "tanh", "", np.tanh)


@pexdoc.pcontracts.contract(wave=Waveform)
def wcomplex(wave):
    r"""
    Convert a waveform's dependent variable vector to complex.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.wcomplex

    :raises: RuntimeError (Argument \`wave\` is not valid)

    .. [[[end]]]
    """
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(np.complex)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def wfloat(wave):
    r"""
    Convert a waveform's dependent variable vector to float.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.wfloat

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * TypeError (Cannot convert complex to float)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        TypeError,
        "Cannot convert complex to float",
        wave._dep_vector.dtype.name.startswith("complex"),
    )
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(np.float)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform)
def wint(wave):
    r"""
    Convert a waveform's dependent variable vector to integer.

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.wint

    :raises:
     * RuntimeError (Argument \`wave\` is not valid)

     * TypeError (Cannot convert complex to integer)

    .. [[[end]]]
    """
    pexdoc.exh.addex(
        TypeError,
        "Cannot convert complex to integer",
        wave._dep_vector.dtype.name.startswith("complex"),
    )
    ret = copy.copy(wave)
    ret._dep_vector = ret._dep_vector.astype(np.int)
    return ret


@pexdoc.pcontracts.contract(wave=Waveform, indep_var="number")
def wvalue(wave, indep_var):
    r"""
    Return the dependent variable value at a given independent variable point.

    If the independent variable point is not in the independent variable vector
    the dependent variable value is obtained by linear interpolation

    :param wave: Waveform
    :type  wave: :py:class:`peng.eng.Waveform`

    :param indep_var: Independent variable point for which the dependent
                      variable is to be obtained
    :type  indep_var: integer or float

    :rtype: :py:class:`peng.eng.Waveform`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_functions.wvalue

    :raises:
     * RuntimeError (Argument \`indep_var\` is not valid)

     * RuntimeError (Argument \`wave\` is not valid)

     * ValueError (Argument \`indep_var\` is not in the independent
       variable vector range)

    .. [[[end]]]
    """
    close_min = np.isclose(indep_var, wave._indep_vector[0], FP_RTOL, FP_ATOL)
    close_max = np.isclose(indep_var, wave._indep_vector[-1], FP_RTOL, FP_ATOL)
    pexdoc.exh.addex(
        ValueError,
        "Argument `indep_var` is not in the independent variable vector range",
        bool(
            ((indep_var < wave._indep_vector[0]) and (not close_min))
            or ((indep_var > wave._indep_vector[-1]) and (not close_max))
        ),
    )
    if close_min:
        return wave._dep_vector[0]
    if close_max:
        return wave._dep_vector[-1]
    idx = np.searchsorted(wave._indep_vector, indep_var)
    xdelta = wave._indep_vector[idx] - wave._indep_vector[idx - 1]
    ydelta = wave._dep_vector[idx] - wave._dep_vector[idx - 1]
    slope = ydelta / float(xdelta)
    return wave._dep_vector[idx - 1] + slope * (indep_var - wave._indep_vector[idx - 1])
