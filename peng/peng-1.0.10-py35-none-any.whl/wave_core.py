"""
Define waveform pseudo-type.

[[[cog
import os, sys
if sys.hexversion < 0x03000000:
    import __builtin__
else:
    import builtins as __builtin__
sys.path.append(os.environ['TRACER_DIR'])
import trace_ex_eng_wave_core
exobj_eng = trace_ex_eng_wave_core.trace_module(no_print=True)
cname = (
    'peng.wave_core.Waveform.__div__'
    if sys.hexversion < 0x03000000 else
    'peng.wave_core.Waveform.__truediv__'
)
]]]
[[[end]]]
"""
# wave_core.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0111,C0302,E0611,E1111,R0205,R0912,R0915,R1701,R1706
# pylint: disable=W0105,W0611,W0706

# Standard library imports
import collections
import copy
import sys
import warnings

# PyPI imports
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    import numpy as np
import pexdoc.exh
import pexdoc.pcontracts
from pexdoc.ptypes import non_null_string

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    import scipy.interpolate
# Intra-package imports imports
from .functions import pprint_vector, remove_extra_delims
from .ptypes import (
    increasing_real_numpy_vector,
    number_numpy_vector,
    wave_scale_option,
    wave_interp_option,
    wave_vectors,
)
from .constants import FP_ATOL, FP_RTOL


###
# Global variables
###
Point = collections.namedtuple("Point", ["indep_var", "dep_var"])
"""
Constructor for a waveform data point.

The first item is the independent variable data and the second item is the
dependent variable data
"""


###
# Functions
###
if sys.hexversion < 0x03000000:  # pragma: no cover

    def _get_ex_msg(obj):
        """Get exception message."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            return obj.value.message if hasattr(obj, "value") else obj.message


else:  # pragma: no cover

    def _get_ex_msg(obj):
        """Get exception message."""
        return obj.value.args[0] if hasattr(obj, "value") else obj.args[0]


def _homogenize_waves(wave_a, wave_b):
    """
    Generate combined independent variable vector.

    The combination is from two waveforms and the (possibly interpolated)
    dependent variable vectors of these two waveforms
    """
    indep_vector = _get_indep_vector(wave_a, wave_b)
    dep_vector_a = _interp_dep_vector(wave_a, indep_vector)
    dep_vector_b = _interp_dep_vector(wave_b, indep_vector)
    return (indep_vector, dep_vector_a, dep_vector_b)


def _interp_dep_vector(wave, indep_vector):
    """Create new dependent variable vector."""
    dep_vector_is_int = wave.dep_vector.dtype.name.startswith("int")
    dep_vector_is_complex = wave.dep_vector.dtype.name.startswith("complex")
    if (wave.interp, wave.indep_scale) == ("CONTINUOUS", "LOG"):
        wave_interp_func = scipy.interpolate.interp1d(
            np.log10(wave.indep_vector), wave.dep_vector
        )
        ret = wave_interp_func(np.log10(indep_vector))
    elif (wave.interp, wave.indep_scale) == ("CONTINUOUS", "LINEAR"):
        dep_vector = (
            wave.dep_vector.astype(np.float64)
            if not dep_vector_is_complex
            else wave.dep_vector
        )
        wave_interp_func = scipy.interpolate.interp1d(wave.indep_vector, dep_vector)
        ret = wave_interp_func(indep_vector)
    else:  # wave.interp == 'STAIRCASE'
        wave_interp_func = scipy.interpolate.interp1d(
            wave.indep_vector, wave.dep_vector, kind="zero"
        )
        # Interpolator does not return the right value for the last
        # data point, it gives the previous "stair" value
        ret = wave_interp_func(indep_vector)
        eq_comp = np.all(
            np.isclose(wave.indep_vector[-1], indep_vector[-1], FP_RTOL, FP_ATOL)
        )
        if eq_comp:
            ret[-1] = wave.dep_vector[-1]
    round_ret = np.round(ret, 0)
    return (
        round_ret.astype("int")
        if (dep_vector_is_int and np.all(np.isclose(round_ret, ret, FP_RTOL, FP_ATOL)))
        else ret
    )


def _get_indep_vector(wave_a, wave_b):
    """Create new independent variable vector."""
    exobj = pexdoc.exh.addex(RuntimeError, "Independent variable ranges do not overlap")
    min_bound = max(np.min(wave_a.indep_vector), np.min(wave_b.indep_vector))
    max_bound = min(np.max(wave_a.indep_vector), np.max(wave_b.indep_vector))
    exobj(bool(min_bound > max_bound))
    raw_range = np.unique(np.concatenate((wave_a.indep_vector, wave_b.indep_vector)))
    return raw_range[np.logical_and(min_bound <= raw_range, raw_range <= max_bound)]


def _verify_compatibility(wave_a, wave_b, check_dep_units=True):
    """Verify that two waveforms can be combined with various mathematical functions."""
    exobj = pexdoc.exh.addex(RuntimeError, "Waveforms are not compatible")
    ctuple = (
        bool(wave_a.indep_scale != wave_b.indep_scale),
        bool(wave_a.dep_scale != wave_b.dep_scale),
        bool(wave_a.indep_units != wave_b.indep_units),
        (bool(wave_a.dep_units != wave_b.dep_units) if check_dep_units else False),
        bool(wave_a.interp != wave_b.interp),
    )
    exobj(any(ctuple))


###
# Class
###
class Waveform(object):
    r"""
    Create a waveform.

    A waveform is an object that binds together an independent variable vector
    with a corresponding dependent variable vector and other relevant meta data
    (independent and dependent variable scale, units and type of function to be
    used for interpolating between given independent variable data points).

    All standard mathematical operators (``+``, ``-``, ``*``,
    ``//``, ``%``, ``**``, ``<<``, ``>>``, ``&``,
    ``^``, ``|``) are supported between waveform objects and between
    a number (integer, float or complex) and a waveform object. An integer
    dependent variable vector preserves its type through any operation unless
    an interpolated dependent variable item results in a floating point value.

    Additionally waveform slicing, iteration and data point membership in the
    waveform are supported. The object(s) expected, returned or tested against
    are 2-item tuples that meet the characteristics of the
    :py:data:`peng.Point` named tuple

    :param indep_vector: Independent variable vector
    :type  indep_vector: :ref:`IncreasingRealNumpyVector`

    :param dep_vector: Dependent variable vector
    :type  dep_vector: :ref:`NumberNumpyVector`

    :param  dep_name: Independent variable name
    :type   dep_name: `NonNullString <https://pexdoc.readthedocs.io/en/stable/
                        ptypes.html#nonnullstring>`_

    :param  indep_scale: Independent variable scale
    :type   indep_scale: :ref:`WaveScaleOption`

    :param  dep_scale: Dependent variable scale
    :type   dep_scale: :ref:`WaveScaleOption`

    :param  indep_units: Independent variable units
    :type   indep_units: string

    :param  dep_units: Dependent variable units
    :type   dep_units: string

    :param  interp: Interpolation function used between dependent variable
                    vector elements
    :type   interp: :ref:`WaveInterpOption`

    :rtype: :py:class:`peng.Waveform()`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.__init__

    :raises:
     * RuntimeError (Argument \`dep_name\` is not valid)

     * RuntimeError (Argument \`dep_scale\` is not valid)

     * RuntimeError (Argument \`dep_units\` is not valid)

     * RuntimeError (Argument \`dep_vector\` is not valid)

     * RuntimeError (Argument \`indep_scale\` is not valid)

     * RuntimeError (Argument \`indep_units\` is not valid)

     * RuntimeError (Argument \`indep_vector\` is not valid)

     * RuntimeError (Argument \`interp\` is not valid)

     * ValueError (Independent and dependent vectors must have the same
       number of elements)

    .. [[[end]]]

    .. note:: Waveforms are "homogenized" before they are used in mathematical
              operations, comparisons, or any other manipulation involving two
              waveforms. First a new independent variable vector is created,
              which is the ordered set resulting from the intersection of the
              independent variable vectors of the two waveforms. An exception
              is raised if there is no overlap (null intersection) between the
              two independent variable vectors. Then the dependent variable
              vector of each waveform is regenerated for the new independent
              variable vector, computing values for elements that are not in
              the waveform's independent variable vector using the specified
              waveform's interpolation function.

              The two waveforms must have identical independent variable scale,
              dependent variable scale, independent variable units, dependent
              variable units and interpolation function.
    """

    # pylint: disable=R0902,R0903,R0913,W0613
    def __init__(
        self,
        indep_vector,
        dep_vector,
        dep_name,
        indep_scale="LINEAR",
        dep_scale="LINEAR",
        indep_units="",
        dep_units="",
        interp="CONTINUOUS",
    ):  # noqa
        self._indep_vector = None
        self._dep_vector = None
        self._dep_name = None
        self._indep_scale = None
        self._dep_scale = None
        self._indep_units = None
        self._dep_units = None
        self._interp = None
        self._set_indep_vector(indep_vector, check=False)
        self._set_dep_vector(dep_vector, check=True)
        self._set_dep_name(dep_name)
        self._set_indep_scale(indep_scale)
        self._set_dep_scale(dep_scale)
        self._set_indep_units(indep_units)
        self._set_dep_units(dep_units)
        self._set_interp(interp)

    def __abs__(self):
        """
        Absolute value of waveform's dependent variable vector.

        For example:

            >>> import math, numpy, peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4.0, -5.0, complex(0, 3)])
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj')
            >>> print(abs(obj))
            Waveform: abs(obj)
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 4+0j, 5+0j, 3+0j ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        """
        obj = copy.copy(self)
        obj.dep_name = "abs({0})".format(obj.dep_name)
        obj.dep_vector = np.abs(obj.dep_vector).astype(obj.dep_vector.dtype)
        return obj

    def __add__(self, other):
        """
        Add dependent variable vectors of two waveforms or a waveform and a number.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a+obj_b)
            Waveform: obj_a+obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 12, 7, 10 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__add__

        :raises:
         * RuntimeError (Waveforms are not compatible)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "+")

    def __and__(self, other):
        """
        Bit-wise logic and waveform operation.

        The logic operation is done on the dependent variable vectors of two
        waveforms or the dependent variable vector of a waveform and a number.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a&obj_b)
            Waveform: obj_a&obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 0, 0, 4 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__and__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "&")

    def __bool__(self):  # pragma: no cover
        """
        Test if the waveform dependent variable is zero for all its elements.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4, 5, 6])
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
            >>> dep_vector = np.zeros(3)
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
        """
        return not bool(
            np.all(
                np.isclose(
                    self._dep_vector, np.zeros(len(self._dep_vector)), FP_RTOL, FP_ATOL
                )
            )
        )

    def __contains__(self, item):
        """
        Test if an item is a data point in the waveform.

        An item is in a waveform when it is a tuple with the characteristics of
        the :py:data:`peng.Point` named tuple and its independent and dependent
        values match a waveform's data point with :py:data:`peng.FP_ATOL`
        absolute tolerance and :py:data:`peng.FP_RTOL` relative tolerance

        :param item: Object
        :type  item: any
        """
        if (not isinstance(item, tuple)) or (
            isinstance(item, tuple) and (len(item) != 2)
        ):
            return False
        tchk = any([isinstance(item[0], typ) for typ in [int, float]])
        if not tchk:
            return False
        tchk = any([isinstance(item[1], typ) for typ in [int, float, complex]])
        if not tchk:
            return False
        indices = [np.where(self._indep_vector >= item[0])[0][0]]
        if indices[0]:
            indices.append(indices[0] - 1)
        for index in indices:
            icmp = np.isclose(
                np.array([self._indep_vector[index]]),
                np.array([item[0]]),
                FP_RTOL,
                FP_ATOL,
            )
            dcmp = np.isclose(
                np.array([self._dep_vector[index]]),
                np.array([item[1]]),
                FP_RTOL,
                FP_ATOL,
            )
            if icmp and dcmp:
                return True
        return False

    def __copy__(self):
        """
        Copy object.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4, 5, 6])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> obj_b = copy.copy(obj_a)
            >>> obj_a == obj_b
            True
            >>> obj_a is obj_b
            False
        """
        return Waveform(
            indep_vector=np.copy(self.indep_vector),
            dep_vector=np.copy(self.dep_vector),
            dep_name=copy.copy(self.dep_name),
            indep_scale=self.indep_scale,
            dep_scale=self.dep_scale,
            indep_units=self.indep_units,
            dep_units=self.dep_units,
            interp=self.interp,
        )

    def __delitem__(self, key):
        """
        Delete a waveform slice.

        :param key: Slice key
        :type  key: integer or slice object

        :raises: Same exceptions as an invalid Numpy array slicing operation
        """
        try:
            self._indep_vector = np.delete(self._indep_vector, key)
            self._dep_vector = np.delete(self._dep_vector, key)
        except:
            raise
        if not self._indep_vector.size:
            raise RuntimeError("Empty waveform after deletion")

    def __div__(self, other):  # pragma: no cover
        """
        Divide the dependent variable vector of a waveform.

        The division may be by the dependent variable vector of another
        waveform, the dependent variable vector of a waveform by a number, or a
        number by the dependent variable vector of a waveform. In the latter
        case a :py:class:`peng.Waveform()` object is returned with the result.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8.0, 2.0, 4.0])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a/obj_b)
            Waveform: obj_a/obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 0.5, 2.5, 1.5 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_doc(cname, no_comment=True)) ]]]

        :raises:
         * RuntimeError (Waveforms are not compatible)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "/")

    def __eq__(self, other):
        """
        Test waveform equality.

        Two waveforms are equal if their independent variable vectors are the
        same with :py:data:`peng.FP_ATOL` absolute tolerance and
        :py:data:`peng.FP_RTOL` relative tolerance, their dependent variable
        vectors are the same with :py:data:`peng.FP_ATOL` absolute tolerance
        and :py:data:`peng.FP_RTOL` relative tolerance, their independent
        variable scales are the same, their dependent variable scales are the
        same, their independent variable units are the same, their dependent
        variable units are the same and they have the same interpolation
        function. Thus if two waveforms are constructed such that they are
        identical but for their variable name, they are considered equal.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4, 5, 6])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector, 'obj_b')
            >>> obj_a == obj_b
            True
            >>> obj_a != obj_b
            False
            >>> dep_vector = obj_a.dep_vector+5
            >>> obj_b = peng.Waveform(indep_vector, dep_vector, 'obj_b')
            >>> obj_a == obj_b
            False
            >>> obj_a != obj_b
            True

        A waveform is considered equal to a real number when its dependent
        variable vector is equal to that number for all of its elements. For
        example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = 12.5*np.ones(len(indep_vector))
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> 5 == obj
            False
            >>> obj == 12.5
            True
        """
        if (
            isinstance(other, float)
            or (isinstance(other, int) and (not isinstance(other, bool)))
            or isinstance(other, complex)
        ):
            return np.all(
                np.isclose(
                    self._dep_vector,
                    other * np.ones(len(self._dep_vector)),
                    FP_RTOL,
                    FP_ATOL,
                )
            )
        if not isinstance(other, Waveform):
            return False
        try:
            _, dep_vector_a, dep_vector_b = _homogenize_waves(self, other)
        except RuntimeError as exobj:
            msg = "Independent variable ranges do not overlap"
            if _get_ex_msg(exobj) == msg:
                return False
            raise
        except:
            raise
        ctuple = (
            np.all(np.isclose(dep_vector_a, dep_vector_b, FP_RTOL, FP_ATOL)),
            bool(self.indep_scale == other.indep_scale),
            bool(self.dep_scale == other.dep_scale),
            bool(self.indep_units == other.indep_units),
            bool(self.dep_units == other.dep_units),
            bool(self.interp == other.interp),
        )
        return bool(all(ctuple))

    def __floordiv__(self, other):
        """
        Integer-divide the dependent variable vector of a waveform.

        The integer division may be by the dependent variable vector of another
        waveform, the dependent variable vector of a waveform by a number, or a
        number by the dependent variable vector of a waveform. In the latter
        case a :py:class:`peng.Waveform()` object is returned with the result.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a//obj_b)
            Waveform: obj_a//obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 0, 2, 1 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__floordiv__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "fdiv")

    def __ge__(self, other):
        """
        Test whether waveform is greater or equal than another waveform or real number.

        A waveform is greater than or equal to another waveform or a number if
        all elements of its dependent variable vector are greater than or equal
        to, element-by-element, the elements of the dependent variable vector
        of another waveform or a real number with :py:data:`peng.FP_ATOL`
        absolute tolerance and :py:data:`peng.FP_RTOL` relative tolerance

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__ge__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, ">=")

    def __getitem__(self, key):
        """
        Slice waveform.

        :param key: Slice key
        :type  key: integer or slice object

        :returns: :py:data:`peng.Point` named tuple or list of
                  :py:data:`peng.Point` named tuples

        :raises: Same exceptions as an invalid Numpy array slicing operation
        """
        try:
            ivector = self._indep_vector[key]
            dvector = self._dep_vector[key]
            return (
                [Point(iitem, ditem) for iitem, ditem in zip(ivector, dvector)]
                if isinstance(ivector, np.ndarray)
                else Point(ivector, dvector)
            )
        except:
            raise

    def __gt__(self, other):
        """
        Test whether waveform is greater than another waveform or real number.

        A waveform is greater than another waveform or a number if all elements
        of its dependent variable vector are greater than, element-by-element,
        the elements of the dependent variable vector of another waveform or a
        real number with :py:data:`peng.FP_ATOL` absolute tolerance and
        :py:data:`peng.FP_RTOL` relative tolerance

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__gt__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, ">")

    def __invert__(self):
        """
        Bit-wise inversion of the dependent variable vector of a waveform.

        For example:

            >>> import math, numpy, peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([6, 5, 4])
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj')
            >>> print(~obj)
            Waveform: ~obj
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ -7, -6, -5 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__invert__

        :raises: TypeError (Complex operand not supported)

        .. [[[end]]]
        """
        pexdoc.exh.addex(
            TypeError,
            "Complex operand not supported",
            self._dep_vector.dtype.name.startswith("complex"),
        )
        obj = copy.copy(self)
        obj.dep_name = "~" + obj.dep_name
        obj.dep_vector = np.invert(obj.dep_vector).astype(obj.dep_vector.dtype)
        return obj

    def __iter__(self):
        """
        Return an iterable over the independent and dependent variable vectors.

        Each item returned by an iterator is a :py:data:`peng.Point` named
        tuple

        :rtype: iterable
        """
        for iitem, ditem in zip(self._indep_vector, self._dep_vector):
            yield iitem, ditem

    def __le__(self, other):
        """
        Test whether waveform is less than or equal to another waveform or real number.

        A waveform is less than or equal to another waveform or a number if
        all elements of its dependent variable vector are less than or equal
        to, element-by-element, the elements of the dependent variable vector
        of another waveform or a real number with :py:data:`peng.FP_ATOL`
        absolute tolerance and :py:data:`peng.FP_RTOL` relative tolerance

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__le__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "<=")

    def __len__(self):
        """Return number of elements in independent (or dependent) variable vector."""
        return len(self._indep_vector)

    def __lshift__(self, other):
        """
        Left shift the dependent variable vector of a waveform.

        The shift amount be set by the dependent variable vector of another
        waveform or a number.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a<<obj_b)
            Waveform: obj_a<<obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 1024, 20, 96 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__lshift__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "<<")

    def __lt__(self, other):
        """
        Test whether a waveform is less than another waveform or real number.

        A waveform is less than another waveform or a number if all elements
        of its dependent variable vector are less than, element-by-element,
        the elements of the dependent variable vector of another waveform or a
        real number with :py:data:`peng.FP_ATOL` absolute tolerance and
        :py:data:`peng.FP_RTOL` relative tolerance

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__lt__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "<")

    def __mod__(self, other):
        r"""
        Division reminder.

        The division reminder may be computed between the dependent variable
        vectors of two waveforms, between the dependent variable vector of a
        waveform and a number, or a number by the dependent variable vector of
        a waveform. In the latter case a :py:class:`peng.Waveform()` object is
        returned with the result.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a%obj_b)
            Waveform: obj_a%obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 4, 1, 2 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__mod__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "%")

    def __mul__(self, other):
        """
        Multiply the dependent variable vector of a waveform.

        The multiplication may be computed element-by-element using another the
        dependent variable vector of another waveform or a number.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a*obj_b)
            Waveform: obj_a*obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 32, 10, 24 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__mul__

        :raises:
         * RuntimeError (Waveforms are not compatible)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "*")

    def __ne__(self, other):
        """
        Test waveform inequality.

        Two waveforms are considered unequal if their independent variable
        vectors are different with :py:data:`peng.FP_ATOL` absolute tolerance
        and :py:data:`peng.FP_RTOL` relative tolerance, and/or their dependent
        variable vectors are different with :py:data:`peng.FP_ATOL` absolute
        tolerance and :py:data:`peng.FP_RTOL` relative tolerance, and/or their
        independent variable scales are not the same, and/or their dependent
        variable scales are not the, and/or their independent variable units
        are not the same, and/or their dependent variable units are not the
        same and/or they do not have the same interpolation function.

        A waveform is considered unequal to a real number when its dependent
        variable is not equal to that number at least in one element.
        """
        return not self.__eq__(other)

    def __neg__(self):
        """
        Multiply the dependent variable vector by -1.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4, -5, 6])
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj')
            >>> print(-obj)
            Waveform: -obj
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ -4, 5, -6 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        """
        obj = copy.copy(self)
        obj.dep_name = "-" + obj.dep_name
        obj.dep_vector = -1 * obj.dep_vector
        return obj

    def __nonzero__(self):  # pragma: no cover
        """
        Test if the waveform dependent vector is zero for all its elements.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4, 5, 6])
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: True
            >>> dep_vector = np.zeros(3)
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj_a')
            >>> if obj:
            ...     print('Boolean test returned: True')
            ... else:
            ...     print('Boolean test returned: False')
            Boolean test returned: False
        """
        return not bool(
            np.all(
                np.isclose(
                    self._dep_vector, np.zeros(len(self._dep_vector)), FP_RTOL, FP_ATOL
                )
            )
        )

    def __or__(self, other):
        """
        Bit-wise logic or the dependent variable of a waveform.

        The other operand may be the dependent variable vector of another
        waveform or a number.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a|obj_b)
            Waveform: obj_a|obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 12, 7, 6 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__or__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "|")

    def __pos__(self):
        """
        Multiply the dependent variable vector of a waveform by +1.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector = np.array([4, 5, 6])
            >>> obj = peng.Waveform(indep_vector, dep_vector, 'obj')
            >>> print(+obj)
            Waveform: obj
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 4, 5, 6 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        """
        return copy.copy(self)

    def __pow__(self, other):
        """
        Raise the dependent variable vector of a waveform to a power exponent.

        The exponent specified by the dependent variable vector of another
        waveform, the dependent variable vector of a waveform to the power
        specified by a number, or a number by the power specified by the
        dependent variable vector of a waveform. In the latter case a
        :py:class:`peng.Waveform()` object is returned with the result.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a**obj_b)
            Waveform: obj_a**obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 65536, 25, 1296 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__pow__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Data type not supported)

         * ValueError (Integers to negative integer powers are not allowed)

        .. [[[end]]]
        """
        return self._operation(other, "**")

    def __radd__(self, other):
        """
        Reflected addition.

        See :py:meth:`peng.Waveform.__add__` for more details
        """
        return self._operation(other, "+")

    def __rand__(self, other):  # pragma: no cover
        """
        Reflected bit-wise logic and.

        See :py:meth:`peng.Waveform.__and__` for more details
        """
        return self._operation(other, "&", reflected=True)

    def __rdiv__(self, other):  # pragma: no cover
        """
        Reflected division.

        See :py:meth:`peng.Waveform.__div__` for more details
        """
        return self._operation(other, "/", reflected=True)

    def __repr__(self):
        # pylint: disable=C0301
        r"""
        Return a string with the expression needed to re-create the object.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> obj = peng.Waveform(
            ...     np.array([1, 2, 3]),
            ...     np.array([4, 5, 6]),
            ...     'test'
            ... )
            >>> repr(obj)
            "peng.Waveform(indep_vector=array([1, 2, 3]), dep_vector=array([4, 5, 6]), dep_name='test', indep_scale='LINEAR', dep_scale='LINEAR', indep_units='', dep_units='', interp='CONTINUOUS')"
        """
        template = (
            "peng.Waveform("
            "indep_vector={0}, "
            "dep_vector={1}, "
            "dep_name={2}, "
            "indep_scale={3}, "
            "dep_scale={4}, "
            "indep_units={5}, "
            "dep_units={6}, "
            "interp={7})"
        )
        return template.format(
            repr(self._indep_vector),
            repr(self._dep_vector),
            repr(self._dep_name),
            repr(self._indep_scale),
            repr(self._dep_scale),
            repr(self._indep_units),
            repr(self._dep_units),
            repr(self._interp),
        )

    def __rfloordiv__(self, other):
        """
        Reflected floor (integer) division.

        See :py:meth:`peng.Waveform.__floordiv__` for more details
        """
        return self._operation(other, "fdiv", reflected=True)

    def __rlshift__(self, other):
        """
        Reflected left shift.

        See :py:meth:`peng.Waveform.__lshift__` for more details
        """
        return self._operation(other, "<<", reflected=True)

    def __rmod__(self, other):
        """
        Reflected division.

        See :py:meth:`peng.Waveform.__mod__` for more details
        """
        return self._operation(other, "%", reflected=True)

    def __rmul__(self, other):
        """
        Reflected multiplication.

        See :py:meth:`peng.Waveform.__mul__` for more details
        """
        return self._operation(other, "*")

    def __ror__(self, other):  # pragma: no cover
        """
        Reflected bit-wise logic or.

        See :py:meth:`peng.Waveform.__or__` for more details
        """
        return self._operation(other, "|", reflected=True)

    def __rpow__(self, other):
        """
        Reflected power.

        See :py:meth:`peng.Waveform.__pow__` for more details
        """
        return self._operation(other, "**", reflected=True)

    def __rrshift__(self, other):
        """
        Reflected right shift.

        See :py:meth:`peng.Waveform.__rshift__` for more details
        """
        return self._operation(other, ">>", reflected=True)

    def __rshift__(self, other):
        """
        Right shift the dependent variable vector of a waveform.

        The shift amount be set by the dependent variable vector of another
        waveform or a number.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([1, 2, 1])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a>>obj_b)
            Waveform: obj_a>>obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 2, 1, 3 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__rshift__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, ">>")

    def __rsub__(self, other):
        """
        Reflected subtraction.

        See :py:meth:`peng.Waveform.__sub__` for more details
        """
        return self._operation(other, "-")

    def __rtruediv__(self, other):  # pragma: no cover
        """
        Reflected true (floating) division.

        See :py:meth:`peng.Waveform.__truediv__` for more details
        """
        return self._operation(other, "/", reflected=True)

    def __rxor__(self, other):  # pragma: no cover
        """
        Reflected bit-wise logic exclusive or .

        See :py:meth:`peng.Waveform.__xor__` for more details
        """
        return self._operation(other, "^", reflected=True)

    def __setitem__(self, key, value):
        """
        Assign a waveform slice.

        :param key: Slice key
        :type  key: integer or slice object

        :param value: Slice value
        :type  value: 2-item tuple or list of 2-item tuples

        :raises:
         * Argument `value` is not valid

         * Same exceptions as an invalid Numpy array slicing operation
        """
        value = [value] if isinstance(value, tuple) else value
        if (
            (value is None)
            or (not isinstance(value, list))
            or (isinstance(value, list) and (not value))
        ):
            raise RuntimeError("Slice value is not valid")
        if not all([isinstance(item, tuple) for item in value]):
            raise RuntimeError("Slice value is not valid")
        if not all([len(item) == 2 for item in value]):
            raise RuntimeError("Slice value is not valid")
        ivector, dvector = zip(*value)
        ivector = np.array(ivector)
        itype = ivector.dtype.name
        valid_types = ["int", "float"]
        if not any([itype.startswith(item) for item in valid_types]):
            raise RuntimeError("Slice value is not valid")
        valid_types = ["int", "float", "complex"]
        dvector = np.array(dvector)
        dtype = dvector.dtype.name
        if not any([dtype.startswith(item) for item in valid_types]):
            raise RuntimeError("Slice value is not valid")
        # Promote types otherwise Numpy truncates float assigning
        # slices to an integer vector for example. Not abstracted
        # in a function for speed
        # Independent vector promotion
        valid_types = ["int", "float"]
        stype = self._indep_vector.dtype.name
        vnum = 0
        for vnum, item in enumerate(valid_types):  # pragma: no branch
            if itype.startswith(item):
                break
        snum = 0
        for snum, item in enumerate(valid_types):  # pragma: no branch
            if stype.startswith(item):
                break
        nresult = max(snum, vnum)
        if nresult > snum:
            ntype = [np.int, np.float, np.complex][nresult]
            self._indep_vector = self._indep_vector.astype(ntype)
        # Dependent vector promotion
        valid_types = ["int", "float", "complex"]
        stype = self._dep_vector.dtype.name
        vnum = 0
        for vnum, item in enumerate(valid_types):  # pragma: no branch
            if dtype.startswith(item):
                break
        snum = 0
        for snum, item in enumerate(valid_types):  # pragma: no branch
            if stype.startswith(item):
                break
        nresult = max(snum, vnum)
        if nresult > snum:
            ntype = [np.int, np.float, np.complex][nresult]
            self._dep_vector = self._dep_vector.astype(ntype)
        try:
            self._indep_vector[key] = ivector if len(ivector) > 1 else ivector[0]
            if min(np.diff(self._indep_vector)) <= 0:
                raise RuntimeError("Slice value is not valid")
            self._dep_vector[key] = dvector if len(dvector) > 1 else dvector[0]
        except:
            raise

    def __str__(self):
        """
        Return a string with a detailed description of the object's contents.

        For example:

            >>> from __future__ import print_function
            >>> import numpy as np
            >>> import peng
            >>> obj = peng.Waveform(
            ...     np.array([1, 2, 3]),
            ...     np.array([4, 5, 6]),
            ...     'test'
            ... )
            >>> print(obj)
            Waveform: test
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 4, 5, 6 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS
        """
        ret = ""
        ret += "Waveform: {0}\n".format(self._dep_name)
        ret += (
            "Independent variable: "
            + pprint_vector(
                vector=self._indep_vector, width=80 - 22, limit=True, indent=22
            )
            + "\n"
        )
        ret += (
            "Dependent variable: "
            + pprint_vector(
                vector=self._dep_vector, width=80 - 20, limit=True, indent=20
            )
            + "\n"
        )
        ret += "Independent variable scale: {0}\n".format(self._indep_scale)
        ret += "Dependent variable scale: {0}\n".format(self._dep_scale)
        ret += "Independent variable units: {0}\n".format(
            self._indep_units if self._indep_units else "(None)"
        )
        ret += "Dependent variable units: {0}\n".format(
            self._dep_units if self._dep_units else "(None)"
        )
        ret += "Interpolating function: {0}".format(self._interp)
        return ret

    def __sub__(self, other):
        """
        Subtract two waveforms, waveform by a number or a number by a waveform.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a-obj_b)
            Waveform: obj_a-obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ -4, 3, 2 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__sub__

        :raises:
         * RuntimeError (Waveforms are not compatible)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "-")

    def __truediv__(self, other):  # pragma: no cover
        """
        Divide (true division) the dependent variable vector of a waveform.

        The division may be between the dependent variable vector of a waveform
        by the dependent variable vector of another waveform, the dependent
        variable vector of a waveform by a number, or a number by the dependent
        variable vector of a waveform. In the latter case a
        :py:class:`peng.Waveform()` object is returned with the result.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8.0, 2.0, 4.0])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a/obj_b)
            Waveform: obj_a/obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 0.5, 2.5, 1.5 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_doc(cname, no_comment=True)) ]]]

        :raises:
         * RuntimeError (Waveforms are not compatible)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "/")

    def __xor__(self, other):
        """
        Bit-wise logic exclusive or waveform operation.

        For example:

            >>> import numpy as np
            >>> import peng
            >>> indep_vector = np.array([1, 2, 3])
            >>> dep_vector_a = np.array([4, 5, 6])
            >>> dep_vector_b = np.array([8, 2, 4])
            >>> obj_a = peng.Waveform(indep_vector, dep_vector_a, 'obj_a')
            >>> obj_b = peng.Waveform(indep_vector, dep_vector_b, 'obj_b')
            >>> print(obj_a^obj_b)
            Waveform: obj_a^obj_b
            Independent variable: [ 1, 2, 3 ]
            Dependent variable: [ 12, 7, 2 ]
            Independent variable scale: LINEAR
            Dependent variable scale: LINEAR
            Independent variable units: (None)
            Dependent variable units: (None)
            Interpolating function: CONTINUOUS

        .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc(raised=True)) ]]]
        .. Auto-generated exceptions documentation for
        .. peng.wave_core.Waveform.__xor__

        :raises:
         * RuntimeError (Independent variable ranges do not overlap)

         * RuntimeError (Waveforms are not compatible)

         * TypeError (Complex operands not supported)

         * TypeError (Data type not supported)

        .. [[[end]]]
        """
        return self._operation(other, "^")

    def _operation(self, other, operand, reflected=False):
        # pylint: disable=R0914,W0212
        cop_list = [">", ">=", "<", "<=", "%", "<<", ">>", "&", "^", "|", "fdiv"]
        extype = pexdoc.exh.addex(TypeError, "Data type not supported")
        if operand in cop_list:
            exnosup = pexdoc.exh.addex(TypeError, "Complex operands not supported")
        scalar = (
            isinstance(other, Waveform)
            and other.dep_units in ["", "-"]
            or self._dep_units in ["", "-"]
        )
        scalar_value = None
        ureflected = not reflected if self._dep_units in ["", "-"] else reflected
        if (
            isinstance(other, complex)
            or isinstance(other, float)
            or (isinstance(other, int) and (not isinstance(other, bool)))
        ):
            scalar = True
            scalar_value = other
            dep_vector = other * (np.ones(len(self._dep_vector)).astype("int"))
            other = Waveform(
                indep_vector=self._indep_vector,
                dep_vector=dep_vector,
                dep_name=str(other),
                indep_scale=self._indep_scale,
                dep_scale=self._dep_scale,
                indep_units=self._indep_units,
                dep_units=self._dep_units,
                interp=self._interp,
            )
        extype(not isinstance(other, Waveform))
        if operand in cop_list:
            exnosup(
                self.dep_vector.dtype.name.startswith("complex")
                or other.dep_vector.dtype.name.startswith("complex")
            )
        check_units_list = ["<", "<=", ">", ">=", "+", "-", "<<", ">>", "&", "|", "^"]
        _verify_compatibility(self, other, operand in check_units_list)
        indep_vector, dep_vector_a, dep_vector_b = _homogenize_waves(self, other)
        proc_self_units = self._dep_units.strip() not in ["", "-"]
        proc_other_units = other._dep_units.strip() not in ["", "-"]
        proc_units = (
            (proc_self_units and proc_other_units)
            if operand in check_units_list
            else (proc_self_units or proc_other_units)
        )
        dep_units = self._dep_units if proc_units else ""
        if operand == "<":
            return (dep_vector_a < dep_vector_b).all()
        if operand == "<=":
            ne_test = np.isclose(dep_vector_a, dep_vector_b, FP_RTOL, FP_ATOL)
            comp_test = dep_vector_a < dep_vector_b
            return np.logical_or(ne_test, comp_test).all()
        if operand == ">":
            return (dep_vector_a > dep_vector_b).all()
        if operand == ">=":
            ne_test = np.isclose(dep_vector_a, dep_vector_b, FP_RTOL, FP_ATOL)
            comp_test = dep_vector_a > dep_vector_b
            return np.logical_or(ne_test, comp_test).all()
        if operand == "+":
            dep_vector = dep_vector_a + dep_vector_b
        elif operand == "-":
            dep_vector = dep_vector_a - dep_vector_b
        elif operand == "*":
            dep_vector = np.multiply(dep_vector_a, dep_vector_b)
            if proc_units and (not scalar):
                dep_units = "({0})*({1})".format(
                    self._dep_units if not ureflected else other._dep_units,
                    other._dep_units if not ureflected else self._dep_units,
                )
            elif proc_units:
                dep_units = self._dep_units if self._dep_units else other._dep_units
        elif operand == "fdiv":
            dep_vector = np.floor_divide(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
            operand = "//"
        elif operand == "%":
            dep_vector = np.mod(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        elif operand == "**":
            exint = pexdoc.exh.addex(
                ValueError, "Integers to negative integer powers are not allowed"
            )
            base = dep_vector_a if not reflected else dep_vector_b
            exp = dep_vector_b if not reflected else dep_vector_a
            base_is_int = base.dtype.name.startswith("int")
            exp_is_int = exp.dtype.name.startswith("int")
            exint(base_is_int and exp_is_int and any(exp < 0))
            dep_vector = np.power(base, exp)
            if proc_units and scalar and (not ureflected):
                dep_units = "({0})**({1})".format(
                    self._dep_units, scalar_value if scalar_value else other._dep_name
                )
            elif proc_units and scalar:
                dep_units = "1**({0})".format(
                    self._dep_units if self._dep_units else other._dep_units
                )
            elif proc_units:
                dep_units = "({0})**({1})".format(
                    self._dep_units if not ureflected else other._dep_units,
                    other._dep_units if not ureflected else self._dep_units,
                )
        elif operand == "/":
            dep_vector = np.divide(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        elif operand == "<<":
            dep_vector = np.left_shift(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        elif operand == ">>":
            dep_vector = np.right_shift(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        elif operand == "&":
            dep_vector = np.bitwise_and(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        elif operand == "|":
            dep_vector = np.bitwise_or(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        else:  # elif operand == '^':
            dep_vector = np.bitwise_xor(
                dep_vector_a if not reflected else dep_vector_b,
                dep_vector_b if not reflected else dep_vector_a,
            )
        dep_name = "({wave1}){op}({wave2})".format(
            wave1=self.dep_name, wave2=other.dep_name, op=operand
        )
        if proc_units and (operand in ["/", "//"]):
            alt_operand = "/"
            if scalar and (not ureflected):
                dep_units = self._dep_units
            elif scalar:
                dep_units = "1{0}({1})".format(
                    alt_operand,
                    self._dep_units if self._dep_units else other._dep_units,
                )
            else:
                dep_units = "({0}){1}({2})".format(
                    self._dep_units if not ureflected else other._dep_units,
                    alt_operand,
                    other._dep_units if not ureflected else self._dep_units,
                )
        return Waveform(
            indep_vector=indep_vector,
            dep_vector=dep_vector,
            dep_name=remove_extra_delims(dep_name, "(", ")"),
            indep_scale=self._indep_scale,
            dep_scale=self._dep_scale,
            indep_units=self._indep_units,
            dep_units=remove_extra_delims(dep_units, "(", ")"),
            interp=self._interp,
        )

    def _get_dep_scale(self):
        return self._dep_scale

    def _get_dep_units(self):
        return self._dep_units

    def _get_dep_vector(self):
        return self._dep_vector

    def _get_dep_name(self):
        return self._dep_name

    def _get_indep_scale(self):
        return self._indep_scale

    def _get_indep_units(self):
        return self._indep_units

    def _get_indep_vector(self):
        return self._indep_vector

    def _get_interp(self):
        return self._interp

    def _get_complex(self):
        return self._dep_vector.dtype.name.startswith("complex")

    def _get_real(self):
        dtype = self._dep_vector.dtype.name
        return any([dtype.startswith(item) for item in ["int", "float"]])

    def _get_vectors(self):
        return [
            Point(iitem, ditem)
            for iitem, ditem in zip(self._indep_vector, self._dep_vector)
        ]

    @pexdoc.pcontracts.contract(dep_scale="wave_scale_option")
    def _set_dep_scale(self, dep_scale):
        self._dep_scale = dep_scale.upper()

    @pexdoc.pcontracts.contract(dep_units=str)
    def _set_dep_units(self, dep_units):
        self._dep_units = dep_units.strip()

    @pexdoc.pcontracts.contract(dep_vector="number_numpy_vector")
    def _set_dep_vector(self, dep_vector, check=True):
        self._set_vectors_int(dep_vector=dep_vector, check=check)

    @pexdoc.pcontracts.contract(dep_name="non_null_string")
    def _set_dep_name(self, dep_name):
        self._dep_name = dep_name

    @pexdoc.pcontracts.contract(indep_scale="wave_scale_option")
    def _set_indep_scale(self, indep_scale):
        self._indep_scale = indep_scale.upper()

    @pexdoc.pcontracts.contract(indep_units=str)
    def _set_indep_units(self, indep_units):
        self._indep_units = indep_units.strip()

    @pexdoc.pcontracts.contract(indep_vector="increasing_real_numpy_vector")
    def _set_indep_vector(self, indep_vector, check=True):
        self._set_vectors_int(indep_vector=indep_vector, check=check)

    @pexdoc.pcontracts.contract(interp="wave_interp_option")
    def _set_interp(self, interp):
        self._interp = interp.upper()

    @pexdoc.pcontracts.contract(vectors="wave_vectors")
    def _set_vectors(self, vectors):
        indep_vector, dep_vector = zip(*copy.copy(vectors))
        self._set_vectors_int(indep_vector, dep_vector)

    def _set_vectors_int(self, indep_vector=None, dep_vector=None, check=True):
        pexdoc.exh.addex(
            ValueError,
            (
                "Independent and dependent vectors must "
                "have the same number of elements"
            ),
            check
            and (
                len(indep_vector if indep_vector is not None else self._indep_vector)
                != len(dep_vector if dep_vector is not None else self._dep_vector)
            ),
        )
        if indep_vector is not None:
            self._indep_vector = copy.copy(indep_vector)
        if dep_vector is not None:
            self._dep_vector = copy.copy(dep_vector)

    # Managed attributes
    complex = property(_get_complex, doc="Complex dependent variable flag")
    r"""
    Returns True if dependent variable is complex, False otherwise
    """

    dep_scale = property(_get_dep_scale, _set_dep_scale, doc="Dependent variable scale")
    r"""
    Gets or sets the waveform dependent variable scale

    :type: :ref:`WaveScaleOption`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.dep_scale

    :raises: (when assigned) RuntimeError (Argument \`dep_scale\` is not
     valid)

    .. [[[end]]]
    """

    dep_units = property(_get_dep_units, _set_dep_units, doc="Dependent variable units")
    r"""
    Gets or sets the waveform dependent variable units

    :type: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.dep_units

    :raises: (when assigned) RuntimeError (Argument \`dep_units\` is not
     valid)

    .. [[[end]]]
    """

    dep_vector = property(
        _get_dep_vector, _set_dep_vector, doc="Dependent variable vector"
    )
    r"""
    Gets or sets the waveform dependent variable vector

    :type: :ref:`NumberNumpyVector`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.dep_vector

    :raises: (when assigned)

     * RuntimeError (Argument \`dep_vector\` is not valid)

     * ValueError (Independent and dependent vectors must have the same
       number of elements)

    .. [[[end]]]
    """

    dep_name = property(_get_dep_name, _set_dep_name, doc="Independent variable name")
    r"""
    Gets or sets the waveform independent variable name

    :type: string
    """

    indep_scale = property(
        _get_indep_scale, _set_indep_scale, doc="Independent variable scale"
    )
    r"""
    Gets or sets the waveform independent variable scale

    :type: :ref:`WaveScaleOption`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.indep_scale

    :raises: (when assigned) RuntimeError (Argument \`indep_scale\` is not
     valid)

    .. [[[end]]]
    """

    indep_units = property(
        _get_indep_units, _set_indep_units, doc="Independent variable units"
    )
    r"""
    Gets or sets the waveform independent variable units

    :type: string

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.indep_units

    :raises: (when assigned) RuntimeError (Argument \`indep_units\` is not
     valid)

    .. [[[end]]]
    """

    indep_vector = property(
        _get_indep_vector, _set_indep_vector, doc="Independent variable vector"
    )
    r"""
    Gets the waveform independent variable vector

    :type: :ref:`IncreasingRealNumpyVector`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.indep_vector

    :raises: (when assigned)

     * RuntimeError (Argument \`indep_vector\` is not valid)

     * ValueError (Independent and dependent vectors must have the same
       number of elements)

    .. [[[end]]]
    """

    interp = property(_get_interp, _set_interp, doc="Interpolation function")
    r"""
    Gets or sets the interpolation function used between dependent
    variable vector elements

    :type: :ref:`WaveInterpOption`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.interp

    :raises: (when assigned) RuntimeError (Argument \`interp\` is not
     valid)

    .. [[[end]]]
    """

    real = property(_get_real, doc="Real dependent variable flag")
    r"""
    Returns True if dependent variable is real, False otherwise
    """

    vectors = property(
        _get_vectors, _set_vectors, doc="Independent and dependent variable vectors"
    )
    r"""
    Gets or sets the independent and dependent variable vectors. The first
    tuple item is the independent variable vector and the second tuple item is
    the dependent variable vector

    :type: :ref:`WaveVectors`

    .. [[[cog cog.out(exobj_eng.get_sphinx_autodoc()) ]]]
    .. Auto-generated exceptions documentation for
    .. peng.wave_core.Waveform.vectors

    :raises: (when assigned) RuntimeError (Argument \`vectors\` is not
     valid)

    .. [[[end]]]
    """
