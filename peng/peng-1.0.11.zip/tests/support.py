# support.py
# Copyright (c) 2013-2019 Pablo Acosta-Serafini
# See LICENSE for details
# pylint: disable=C0103,C0111,C0113,C0122,E1127,R0201,R1710,W0212

# Standard library imports
from __future__ import print_function
import warnings

# PyPI imports
import numpy as np

with warnings.catch_warnings():
    from _pytest.warning_types import PytestWarning

    warnings.filterwarnings("ignore", category=PytestWarning)
    import pytest
# Intra-package imports
import peng
from peng.constants import FP_ATOL, FP_RTOL


###
# Functions
###
def cmp_vectors(vector_a, vector_b, rtol=None, atol=None):
    """Compare two floating point vectors to a given precision."""
    # pylint: disable=R0914
    def _vtype(vector, name):
        num_types = ["int", "float", "complex"]
        for num_type in num_types:
            if vector.dtype.name.startswith(num_type):
                return num_type
        pytest.fail("Vector {0} is not numeric".format(name))

    def _snum(item, vtype):
        if vtype == "complex":
            snum = "{0}{1}j".format(
                peng.to_scientific_string(item.real, 10, 3, True),
                peng.to_scientific_string(item.imag, 10, 3, True),
            )
        else:
            snum = peng.to_scientific_string(item, 10, 3, True)
        return snum

    rtol = rtol or FP_RTOL
    atol = atol or FP_ATOL
    if vector_a.shape != vector_b.shape:
        print("Vector A shape: {0}".format(vector_a.shape))
        print("Vector B shape: {0}".format(vector_b.shape))
        pytest.fail("Vectors have different shape")
    if len(vector_a.shape) != 1:
        pytest.fail("Vectors are matrices")
    if vector_a.size != vector_b.size:
        print("Vector A length: {0}".format(vector_a.size))
        print("Vector B length: {0}".format(vector_b.size))
        pytest.fail("Vectors have different length")
    atype = _vtype(vector_a, "A")
    btype = _vtype(vector_b, "B")
    flag = np.all(np.isclose(vector_a, vector_b, rtol, atol))
    if not flag:
        il = len(str(vector_a.size))
        template = "{0:>" + str(il) + "}: "
        header = "#".center(il + 1) + " "
        header += "Vector A".center(37 if atype == "complex" else 18) + " "
        header += "Vector B".center(37 if btype == "complex" else 18) + " "
        header += "abs(A-B)".center(18) + " "
        header += "Limit".center(18)
        print("\n" + header + "\n" + ("-" * len(header)))
        for num, (item_a, item_b) in enumerate(zip(vector_a, vector_b)):
            ab_items = abs(item_a - item_b)
            lim = atol + rtol * abs(item_b)
            if ab_items > lim:
                sidx = template.format(num)
                anum = _snum(item_a, atype)
                bnum = _snum(item_b, btype)
                ab_num = peng.to_scientific_string(ab_items, 10, 3, True)
                slim = peng.to_scientific_string(lim, 10, 3, True)
                print(sidx + anum + " " + bnum + " " + ab_num + " " + slim)
        pytest.fail("Vectors do not match")


def std_wobj(
    dep_name,
    indep_vector=None,
    dep_vector=None,
    interp="STAIRCASE",
    dep_units="Volts",
    indep_scale="LOG",
):
    """Return a waveform with fixed parameters and given name."""
    # pylint: disable=R0913
    indep_vector = np.array([1, 2, 3]) if indep_vector is None else indep_vector
    dep_vector = np.array([6, 5, 4]) if dep_vector is None else dep_vector
    return peng.Waveform(
        indep_vector=indep_vector,
        dep_vector=dep_vector,
        dep_name=dep_name,
        indep_scale=indep_scale,
        dep_scale="LINEAR",
        indep_units="Sec",
        dep_units=dep_units,
        interp=interp,
    )
